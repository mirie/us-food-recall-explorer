"""Throwaway script: Step 3 pilot run.

Not checked in. Classifies scratch/pilot_sample.csv (built by
build_pilot_sample.py) synchronously (not via the Batch API -- the pilot is
small enough that iterating on 3 effort levels serially matters more than
the 50% batch discount) at effort levels high, medium, low. Reuses
classify_all.py's request-shaping helpers so the pilot exercises the exact
same system prompt, schema, and chunking shape production will use.

Reports, per effort level: chunk count, token usage (input/output/thinking),
estimated cost, known-answer-probe accuracy, and label agreement against the
`high` baseline. Writes scratch/pilot_results_<effort>.json for inspection.
"""

import json
import time

import anthropic
import pandas as pd

from classify_all import (
    CHUNK_SIZE,
    MAX_TOKENS,
    MODEL,
    build_chunk_user_content,
    build_response_schema,
    build_system_blocks,
    chunk_rows,
    parse_chunk_response_text,
)

# Per-million-token USD prices, Claude Opus 5 (see claude-api skill cache).
INPUT_PRICE_PER_M = 5.00
OUTPUT_PRICE_PER_M = 25.00
CACHE_WRITE_PRICE_PER_M = 6.25   # ~1.25x input
CACHE_READ_PRICE_PER_M = 0.50    # ~0.1x input

EFFORT_LEVELS = ["high", "medium", "low"]

FULL_DATASET_ROWS = 29_159


def load_pilot_rows():
    df = pd.read_csv("scratch/pilot_sample.csv", dtype=str).fillna("")
    rows = list(df[["recall_number", "product_description"]].itertuples(index=False, name=None))
    expected = dict(
        df[df["expected_category"] != ""][["recall_number", "expected_category"]].itertuples(index=False, name=None)
    )
    return rows, expected


def classify_at_effort(client, chunks, system_blocks, effort):
    all_records = {}
    usage_totals = {
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_creation_input_tokens": 0,
        "cache_read_input_tokens": 0,
    }
    for i, chunk in enumerate(chunks):
        user_content = build_chunk_user_content(chunk)

        print(f"  [{effort}] chunk {i + 1}/{len(chunks)} ({len(chunk)} rows)...", end=" ", flush=True)
        with client.messages.stream(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=system_blocks,
            output_config={
                "effort": effort,
                "format": {"type": "json_schema", "schema": build_response_schema()},
            },
            messages=[{"role": "user", "content": user_content}],
        ) as stream:
            message = stream.get_final_message()

        text = next((b.text for b in message.content if b.type == "text"), "")
        try:
            records = parse_chunk_response_text(text)
        except (json.JSONDecodeError, KeyError) as exc:
            print(f"PARSE FAILURE: {exc}")
            records = []

        for r in records:
            all_records[r["recall_number"]] = r

        u = message.usage
        usage_totals["input_tokens"] += u.input_tokens
        usage_totals["output_tokens"] += u.output_tokens
        usage_totals["cache_creation_input_tokens"] += getattr(u, "cache_creation_input_tokens", 0) or 0
        usage_totals["cache_read_input_tokens"] += getattr(u, "cache_read_input_tokens", 0) or 0
        print(f"got {len(records)} rows, stop_reason={message.stop_reason}")
        time.sleep(0.5)

    return all_records, usage_totals


def estimate_cost(usage):
    return (
        usage["input_tokens"] / 1_000_000 * INPUT_PRICE_PER_M
        + usage["output_tokens"] / 1_000_000 * OUTPUT_PRICE_PER_M
        + usage["cache_creation_input_tokens"] / 1_000_000 * CACHE_WRITE_PRICE_PER_M
        + usage["cache_read_input_tokens"] / 1_000_000 * CACHE_READ_PRICE_PER_M
    )


def probe_accuracy(records, expected):
    correct = 0
    total = 0
    misses = []
    for recall_number, expected_category in expected.items():
        total += 1
        got = records.get(recall_number, {}).get("category")
        if got == expected_category:
            correct += 1
        else:
            misses.append((recall_number, expected_category, got))
    return correct, total, misses


def main():
    rows, expected = load_pilot_rows()
    chunks = chunk_rows(rows, chunk_size=CHUNK_SIZE)
    system_blocks = build_system_blocks()
    print(f"Pilot: {len(rows)} rows -> {len(chunks)} chunks, {len(expected)} known-answer probes\n")

    client = anthropic.Anthropic()
    results_by_effort = {}

    for effort in EFFORT_LEVELS:
        print(f"--- effort: {effort} ---")
        records, usage = classify_at_effort(client, chunks, system_blocks, effort)
        cost = estimate_cost(usage)
        correct, total, misses = probe_accuracy(records, expected)
        results_by_effort[effort] = {
            "records": records,
            "usage": usage,
            "cost": cost,
            "probe_correct": correct,
            "probe_total": total,
            "probe_misses": misses,
        }
        print(f"  usage: {usage}")
        print(f"  estimated pilot cost: ${cost:.4f}")
        print(f"  probe accuracy: {correct}/{total}")
        if misses:
            for recall_number, exp, got in misses:
                print(f"    MISS {recall_number}: expected {exp!r}, got {got!r}")
        extrapolated = cost * (FULL_DATASET_ROWS / len(rows))
        print(f"  extrapolated full-run cost (x{FULL_DATASET_ROWS / len(rows):.1f}): ${extrapolated:.2f}\n")

        with open(f"scratch/pilot_results_{effort}.json", "w") as f:
            json.dump({
                "usage": usage,
                "cost": cost,
                "probe_correct": correct,
                "probe_total": total,
                "probe_misses": misses,
                "records": records,
            }, f, indent=2)

    # Label agreement vs. high baseline
    baseline = results_by_effort["high"]["records"]
    print("--- label agreement vs. high ---")
    for effort in ["medium", "low"]:
        other = results_by_effort[effort]["records"]
        common_ids = set(baseline) & set(other)
        agree = sum(1 for rid in common_ids if baseline[rid]["category"] == other[rid]["category"])
        print(f"  {effort}: {agree}/{len(common_ids)} agree with high ({agree / len(common_ids):.1%})")


if __name__ == "__main__":
    main()
