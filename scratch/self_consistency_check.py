"""Step 3b check 1: self-consistency.

Re-classify 1,000 rows (fixed random seed) in a second, independent Batch API
run using the exact same request-shaping helpers as classify_all.py, then
compare against data/recall_categories_llm_full.csv. Not checked in --
one-off validation script per HANDOFF_PHASE5_LLM_MERGE.md Step 3b.

Usage:
    .venv/bin/python scratch/self_consistency_check.py submit
    .venv/bin/python scratch/self_consistency_check.py fetch
"""

import csv
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from classify_all import (
    build_system_blocks,
    build_chunk_request,
    custom_id_for,
    chunk_rows,
    check_completeness,
    parse_chunk_response_text,
)
from recall_explorer.pipeline import load_recalls

SAMPLE_SIZE = 1000
SEED = 20260816
SAMPLE_IDS_PATH = Path(__file__).parent / "self_consistency_sample_ids.json"
BATCH_ID_PATH = Path(__file__).parent / "self_consistency_batch_id.json"
RESULT_PATH = Path(__file__).parent / "self_consistency_results.csv"


def cmd_submit():
    import anthropic

    df = load_recalls()
    rows = list(df[["recall_number", "product_description"]].itertuples(index=False, name=None))
    rng = random.Random(SEED)
    sample = rng.sample(rows, SAMPLE_SIZE)
    SAMPLE_IDS_PATH.write_text(json.dumps([r[0] for r in sample], indent=2))

    system_blocks = build_system_blocks()
    chunks = chunk_rows(sample, chunk_size=100)
    requests = [
        build_chunk_request(custom_id_for(i), chunk, system_blocks)
        for i, chunk in enumerate(chunks)
    ]
    client = anthropic.Anthropic()
    batch = client.messages.batches.create(requests=requests)
    BATCH_ID_PATH.write_text(json.dumps({"batch_id": batch.id, "n_chunks": len(requests)}, indent=2))
    print(f"submitted batch {batch.id}, {len(requests)} chunks, {len(sample)} rows")


def cmd_fetch():
    import anthropic

    batch_id = json.loads(BATCH_ID_PATH.read_text())["batch_id"]
    client = anthropic.Anthropic()
    batch = client.messages.batches.retrieve(batch_id)
    print(f"batch {batch_id}: {batch.processing_status}")
    if batch.processing_status != "ended":
        print("not ended yet -- re-run later")
        return

    sample_ids = set(json.loads(SAMPLE_IDS_PATH.read_text()))
    collected = {}
    errors = []
    for result in client.messages.batches.results(batch_id):
        result_type = result.result.type
        if result_type == "succeeded":
            message = result.result.message
            if message.stop_reason == "refusal":
                errors.append(f"{result.custom_id}: refusal")
                continue
            text = next((b.text for b in message.content if b.type == "text"), "")
            for row in parse_chunk_response_text(text):
                collected[row["recall_number"]] = row
        else:
            errors.append(f"{result.custom_id}: {result_type}")

    if errors:
        print(f"{len(errors)} problems:")
        for e in errors:
            print(" ", e)

    missing, unexpected = check_completeness(set(collected), sample_ids)
    print(f"missing: {len(missing)}, unexpected: {len(unexpected)}")

    with RESULT_PATH.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["recall_number", "category", "confidence"])
        writer.writeheader()
        for row in collected.values():
            writer.writerow(row)
    print(f"wrote {len(collected)} rows -> {RESULT_PATH}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "submit":
        cmd_submit()
    elif cmd == "fetch":
        cmd_fetch()
    else:
        raise SystemExit("usage: self_consistency_check.py [submit|fetch]")
