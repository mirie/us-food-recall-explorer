"""Phase 5: full-dataset LLM reclassification against CLASSIFICATION_RULES.md.

One-time script, checked in. Classifies every row in data/food_recalls.csv
(29,161 rows -- not just the Uncategorized residual the old Phase 3 manual
round trip covered) via the Claude Message Batches API, at 50% of standard
pricing.

Two commands, run separately so a long-running batch never ties up a
terminal and results stay retrievable for 29 days independent of this
process:

    .venv/bin/python classify_all.py submit
        Builds every chunk request, splits into N_SUBMISSIONS batches,
        creates them, and writes their IDs to data/batch_ids.json. Exits
        immediately -- does not wait for completion.

    .venv/bin/python classify_all.py fetch
        Polls every batch ID in data/batch_ids.json. Batches still running
        are reported and skipped (safe to re-run). Once all have ended,
        retrieves every chunk's results, validates the full set of
        recall_numbers is covered with zero missing and zero unexpected,
        and writes data/recall_categories_llm_full.csv
        (recall_number,category,confidence). Aborts loudly rather than
        writing a partial file.

A *chunk* is CHUNK_SIZE (100) rows classified in a single API request. A
*submission* is one Batch API job holding roughly a third of the chunks --
three submissions so a single submission failure doesn't require resubmitting
everything.

`confidence` is written to the output CSV as a review artifact only; nothing
downstream merges it into the app's runtime data (see the master plan's
Step 4 -- build_classified_dataset.py does not carry it forward).
"""

import argparse
import csv
import json
import sys
import time
from pathlib import Path

from recall_explorer.llm_categories import CATEGORY_ENUM
from recall_explorer.pipeline import load_recalls

MODEL = "claude-opus-5"
# 8000 truncated a 100-row chunk at effort="high" during the Step 3 pilot --
# adaptive thinking at high effort consumed most of the budget before any
# response text, the same failure mode Step 1's design-sample call hit at
# max_tokens=16000 (see BUILD_LOG). Sized generously since chunks (and their
# thinking budgets) are per-request, not cumulative across the run.
MAX_TOKENS = 24000
CHUNK_SIZE = 100
N_SUBMISSIONS = 3

CLASSIFICATION_RULES_PATH = Path(__file__).resolve().parent / "CLASSIFICATION_RULES.md"
BATCH_IDS_PATH = Path(__file__).resolve().parent / "data" / "batch_ids.json"
OUTPUT_CSV_PATH = Path(__file__).resolve().parent / "data" / "recall_categories_llm_full.csv"

TASK_WRAPPER = """\
You are classifying US food recall product descriptions under the taxonomy
above. Apply its governing principle, category rules, boundary rules, and
coverage-hole rules exactly as written.

Two worked examples, to calibrate:
- "Blue Bell Vanilla Ice Cream, coconut fudge swirl" -> `Dairy`. All Blue
  Bell products in this dataset are ice cream; the coconut and fudge are
  flavorings, not the product's identity.
- "a89471 batter mix x1" (a bare SKU/code with little food-identifying
  text) -> `Uncategorized`, if nothing in the description reliably
  indicates a category.

Rules:
- Every row in the attached CSV must appear exactly once in your output,
  in the `classifications` array.
- `category` must be exactly one of the labels in the taxonomy's label set
  (case-sensitive) -- the response schema enforces this by construction.
- Set `confidence`:
  - `high` -- the description contains an unambiguous, direct signal for
    the category (a named product type squarely inside one category's
    rule, no competing boundary rule in play).
  - `medium` -- a boundary or collision rule from the document had to be
    applied to reach the answer (e.g. distinguishing a meat-named
    seasoning from actual meat, or a plant analog from its animal
    counterpart).
  - `low` -- genuinely ambiguous: the description is thin, could
    plausibly fit more than one category even after applying the
    document's rules, or falls into one of the "Known gaps."
- When genuinely unsure, use `Uncategorized` rather than guessing.
"""


def build_system_blocks():
    """System prompt: CLASSIFICATION_RULES.md verbatim + the task wrapper.

    Identical across all 292 chunk requests, so it's marked for prompt
    caching -- well above Opus 5's cacheable minimum.
    """
    rules_text = CLASSIFICATION_RULES_PATH.read_text()
    combined = rules_text + "\n\n---\n\n" + TASK_WRAPPER
    return [{"type": "text", "text": combined, "cache_control": {"type": "ephemeral"}}]


def build_response_schema():
    return {
        "type": "object",
        "properties": {
            "classifications": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "recall_number": {"type": "string"},
                        "category": {"type": "string", "enum": CATEGORY_ENUM},
                        "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
                    },
                    "required": ["recall_number", "category", "confidence"],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["classifications"],
        "additionalProperties": False,
    }


def rows_to_classify(df):
    """(recall_number, product_description) for every row in the dataset."""
    subset = df[["recall_number", "product_description"]]
    return list(subset.itertuples(index=False, name=None))


def chunk_rows(rows, chunk_size=CHUNK_SIZE):
    return [rows[i:i + chunk_size] for i in range(0, len(rows), chunk_size)]


def split_into_submissions(chunks, n_submissions=N_SUBMISSIONS):
    """Split chunks into n_submissions roughly-equal, order-preserving groups."""
    n = len(chunks)
    base, extra = divmod(n, n_submissions)
    submissions = []
    start = 0
    for i in range(n_submissions):
        size = base + (1 if i < extra else 0)
        submissions.append(chunks[start:start + size])
        start += size
    return submissions


def custom_id_for(chunk_index):
    return f"chunk-{chunk_index:04d}"


def build_chunk_user_content(chunk):
    """CSV text (recall_number,product_description) for one chunk's rows."""
    import io

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["recall_number", "product_description"])
    for recall_number, product_description in chunk:
        writer.writerow([recall_number, product_description])
    return buf.getvalue().strip("\r\n")


def build_chunk_request(custom_id, chunk, system_blocks):
    from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
    from anthropic.types.messages.batch_create_params import Request

    return Request(
        custom_id=custom_id,
        params=MessageCreateParamsNonStreaming(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=system_blocks,
            output_config={
                "effort": "high",
                "format": {"type": "json_schema", "schema": build_response_schema()},
            },
            messages=[{"role": "user", "content": build_chunk_user_content(chunk)}],
        ),
    )


def parse_chunk_response_text(text):
    return json.loads(text)["classifications"]


def check_completeness(collected_recall_numbers, expected_recall_numbers):
    missing = sorted(expected_recall_numbers - collected_recall_numbers)
    unexpected = sorted(collected_recall_numbers - expected_recall_numbers)
    return missing, unexpected


def write_results_csv(records, out_path):
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["recall_number", "category", "confidence"])
        writer.writeheader()
        for record in sorted(records, key=lambda r: r["recall_number"]):
            writer.writerow(record)


# --- CLI commands (not unit-tested -- thin wrappers over the Batch API) ----

def cmd_submit(_args):
    import anthropic

    df = load_recalls()
    rows = rows_to_classify(df)
    chunks = chunk_rows(rows)
    system_blocks = build_system_blocks()
    print(f"{len(rows):,} rows -> {len(chunks)} chunks of up to {CHUNK_SIZE}")

    submissions = split_into_submissions(chunks)
    client = anthropic.Anthropic()
    batch_records = []
    chunk_index = 0
    for submission_index, submission_chunks in enumerate(submissions):
        requests = []
        for chunk in submission_chunks:
            requests.append(build_chunk_request(custom_id_for(chunk_index), chunk, system_blocks))
            chunk_index += 1
        batch = client.messages.batches.create(requests=requests)
        print(f"submission {submission_index}: batch {batch.id}, {len(requests)} chunks")
        batch_records.append({
            "batch_id": batch.id,
            "submission_index": submission_index,
            "n_chunks": len(requests),
        })

    BATCH_IDS_PATH.parent.mkdir(parents=True, exist_ok=True)
    BATCH_IDS_PATH.write_text(json.dumps({"batches": batch_records}, indent=2) + "\n")
    print(f"\nWrote {BATCH_IDS_PATH}")


def cmd_fetch(_args):
    import anthropic

    if not BATCH_IDS_PATH.exists():
        raise SystemExit(f"{BATCH_IDS_PATH} not found -- run `submit` first.")
    batch_records = json.loads(BATCH_IDS_PATH.read_text())["batches"]

    client = anthropic.Anthropic()
    all_ended = True
    for record in batch_records:
        batch = client.messages.batches.retrieve(record["batch_id"])
        record["processing_status"] = batch.processing_status
        print(f"batch {record['batch_id']}: {batch.processing_status}")
        if batch.processing_status != "ended":
            all_ended = False

    if not all_ended:
        print("\nNot all batches have ended yet. Re-run `fetch` later.")
        return

    df = load_recalls()
    expected_recall_numbers = set(df["recall_number"])

    collected = {}
    errors = []
    for record in batch_records:
        for result in client.messages.batches.results(record["batch_id"]):
            result_type = result.result.type
            if result_type == "succeeded":
                message = result.result.message
                if message.stop_reason == "refusal":
                    errors.append(f"{result.custom_id}: model refused")
                    continue
                text = next((b.text for b in message.content if b.type == "text"), "")
                for row in parse_chunk_response_text(text):
                    collected[row["recall_number"]] = row
            elif result_type == "errored":
                errors.append(f"{result.custom_id}: errored ({result.result.error.type})")
            elif result_type == "canceled":
                errors.append(f"{result.custom_id}: canceled")
            elif result_type == "expired":
                errors.append(f"{result.custom_id}: expired")

    if errors:
        print(f"\n{len(errors)} chunk-level problems:")
        for e in errors:
            print(f"  {e}")

    missing, unexpected = check_completeness(set(collected), expected_recall_numbers)
    if missing or unexpected:
        raise SystemExit(
            f"Refusing to write a partial file: {len(missing)} missing, "
            f"{len(unexpected)} unexpected recall_numbers."
        )

    write_results_csv(collected.values(), OUTPUT_CSV_PATH)
    print(f"\nWrote {len(collected):,} rows -> {OUTPUT_CSV_PATH}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("submit", help="Build and submit all batches.")
    subparsers.add_parser("fetch", help="Poll and retrieve results; write the output CSV.")
    args = parser.parse_args()

    if args.command == "submit":
        cmd_submit(args)
    elif args.command == "fetch":
        cmd_fetch(args)


if __name__ == "__main__":
    sys.exit(main())
