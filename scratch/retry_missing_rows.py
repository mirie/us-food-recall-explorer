"""Throwaway script: fill in rows the full run's batches silently dropped.

Not checked in. 16 of 292 chunks came back from the Batch API with
stop_reason=end_turn (not max_tokens, not refusal) but fewer JSON array
entries than input rows -- the model silently omitted some rows from its
own structured output, a different failure mode than truncation. 419 rows
total. This re-submits just those rows, in smaller (25-row) chunks to
reduce the chance of the same drop pattern, synchronously (small enough
that Batch API overhead isn't worth it), retrying automatically if any
chunk is still short. Merges into data/collected_partial.json and writes
the final data/recall_categories_llm_full.csv once complete.
"""

import json
import time

import anthropic

from classify_all import (
    MAX_TOKENS,
    MODEL,
    build_chunk_user_content,
    build_response_schema,
    build_system_blocks,
    check_completeness,
    parse_chunk_response_text,
    write_results_csv,
)
from recall_explorer.pipeline import load_recalls

RETRY_CHUNK_SIZE = 25
MAX_ROUNDS = 5


def classify_rows(client, system_blocks, rows):
    """Classify a small row list, chunked small, returning {recall_number: record}."""
    collected = {}
    for i in range(0, len(rows), RETRY_CHUNK_SIZE):
        chunk = rows[i:i + RETRY_CHUNK_SIZE]
        user_content = build_chunk_user_content(chunk)
        with client.messages.stream(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=system_blocks,
            output_config={
                "effort": "high",
                "format": {"type": "json_schema", "schema": build_response_schema()},
            },
            messages=[{"role": "user", "content": user_content}],
        ) as stream:
            message = stream.get_final_message()
        text = next((b.text for b in message.content if b.type == "text"), "")
        records = parse_chunk_response_text(text)
        for r in records:
            collected[r["recall_number"]] = r
        got = len(records)
        print(f"  chunk {i // RETRY_CHUNK_SIZE}: {len(chunk)} rows in, {got} out, stop={message.stop_reason}")
        time.sleep(0.3)
    return collected


def main():
    collected = json.load(open("data/collected_partial.json"))
    missing_rows = [tuple(r) for r in json.load(open("data/missing_rows_retry.json"))]
    row_lookup = dict(missing_rows)

    client = anthropic.Anthropic()
    system_blocks = build_system_blocks()

    still_missing_ids = set(row_lookup)
    for round_num in range(1, MAX_ROUNDS + 1):
        if not still_missing_ids:
            break
        rows_to_send = [(rn, row_lookup[rn]) for rn in still_missing_ids]
        print(f"--- retry round {round_num}: {len(rows_to_send)} rows ---")
        results = classify_rows(client, system_blocks, rows_to_send)
        collected.update(results)
        still_missing_ids = still_missing_ids - set(results)
        print(f"  still missing after round {round_num}: {len(still_missing_ids)}")

    if still_missing_ids:
        raise SystemExit(
            f"Refusing to write a partial file: {len(still_missing_ids)} rows still "
            f"missing after {MAX_ROUNDS} retry rounds: {sorted(still_missing_ids)}"
        )

    df = load_recalls()
    expected_ids = set(df["recall_number"])
    missing, unexpected = check_completeness(set(collected), expected_ids)
    if missing or unexpected:
        raise SystemExit(
            f"Refusing to write a partial file: {len(missing)} missing, "
            f"{len(unexpected)} unexpected recall_numbers."
        )

    write_results_csv(collected.values(), "data/recall_categories_llm_full.csv")
    print(f"\nWrote {len(collected):,} rows -> data/recall_categories_llm_full.csv")


if __name__ == "__main__":
    main()
