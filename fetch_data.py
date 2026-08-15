"""One-time fetch of the openFDA Food Enforcement dataset to a static CSV.

Run manually. The Streamlit app never imports or calls this module -- it only
reads the CSV this script produces.

    python fetch_data.py --dry-run      # counts only, writes nothing
    python fetch_data.py --limit 1      # smoke test one real row
    python fetch_data.py                # full fetch

Why this paginates by year rather than by offset: openFDA caps `skip` at 25,000
but the dataset holds ~29,000 records. A plain `while skip < total` loop hits
the cap and stops early -- returning a 400 only on the request past it, after
several thousand rows have already been silently dropped. Windowing by year
keeps every window well under the cap.

Only raw API fields are written here. Food-category and contamination-reason
derivation are deliberately left to the app's data-prep layer, so those rules
can be revised without re-hitting the API.
"""

import argparse
import csv
import json
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path

import requests

SCRIPT_VERSION = "1.0"
API_URL = "https://api.fda.gov/food/enforcement.json"

# openFDA's own ceilings, not ours.
PAGE_SIZE = 1000
SKIP_CAP = 25_000

# openFDA enforcement reports begin in 2012. A few dozen records carry an
# earlier recall_initiation_date -- recalls that began before the reporting
# system existed and were back-filled. They are too sparse to chart honestly,
# so the window starts at 2012 and they are left out. See BUILD_LOG Entry 1.
START_YEAR = 2012

# Dropped: address_1, address_2, postal_code, code_info, more_code_info,
# openfda (always {} on this endpoint). None feed a chart or filter.
KEEP_FIELDS = [
    "recall_number",         # unique per product row -- the product-level key
    "event_id",              # shared across a recall's products -- the event-level key
    "product_type",
    "status",
    "classification",        # Class I/II/III -- the severity filter
    "product_description",   # free text; food category is derived from this
    "reason_for_recall",     # free text; contamination reason is derived from this
    "product_quantity",
    "recalling_firm",
    "city",
    "state",
    "country",               # firm's country, NOT country of origin
    "voluntary_mandated",
    "initial_firm_notification",
    "distribution_pattern",
    "recall_initiation_date",  # canonical date for seasonality and trend
    "center_classification_date",
    "report_date",
    "termination_date",
]

REQUEST_PAUSE = 0.25  # openFDA allows 240 req/min unauthenticated; ~40 requests here.
MAX_RETRIES = 4


def _get(params, attempt=1):
    """GET with backoff on transient failures. Returns None for 'no matches'."""
    try:
        resp = requests.get(API_URL, params=params, timeout=30)
    except requests.RequestException as exc:
        if attempt > MAX_RETRIES:
            raise SystemExit(f"Network error after {MAX_RETRIES} retries: {exc}")
        time.sleep(2 ** attempt)
        return _get(params, attempt + 1)

    # openFDA returns 404 with a NOT_FOUND body for an empty result set, which
    # is a legitimate answer to "how many recalls in 2011?", not an error.
    if resp.status_code == 404:
        return None

    if resp.status_code == 429 or resp.status_code >= 500:
        if attempt > MAX_RETRIES:
            raise SystemExit(
                f"openFDA returned {resp.status_code} after {MAX_RETRIES} retries. "
                f"Aborting rather than writing partial data."
            )
        time.sleep(2 ** attempt)
        return _get(params, attempt + 1)

    if resp.status_code != 200:
        raise SystemExit(f"openFDA returned {resp.status_code}: {resp.text[:300]}")

    return resp.json()


def year_query(year):
    return f"recall_initiation_date:[{year}0101 TO {year}1231]"


def count_for_year(year):
    payload = _get({"search": year_query(year), "limit": 1})
    time.sleep(REQUEST_PAUSE)
    if payload is None:
        return 0
    return payload["meta"]["results"]["total"]


def api_last_updated():
    payload = _get({"limit": 1})
    return payload["meta"]["last_updated"] if payload else None


def fetch_year(year, expected, cap=None):
    """Page through one year. Aborts if the API returns fewer rows than promised."""
    rows = []
    skip = 0
    while skip < expected:
        if cap is not None and len(rows) >= cap:
            break
        page_size = PAGE_SIZE if cap is None else min(PAGE_SIZE, cap - len(rows))
        payload = _get({
            "search": year_query(year),
            "limit": page_size,
            "skip": skip,
        })
        time.sleep(REQUEST_PAUSE)
        if payload is None:
            break
        batch = payload["results"]
        if not batch:
            break
        rows.extend(batch)
        skip += len(batch)
        if skip >= SKIP_CAP:
            raise SystemExit(
                f"{year} exceeded openFDA's skip cap of {SKIP_CAP:,}. "
                f"Split this year into smaller windows."
            )

    # The guard that matters: a short year means we lost rows somewhere.
    if cap is None and len(rows) != expected:
        raise SystemExit(
            f"{year}: expected {expected:,} rows, got {len(rows):,}. "
            f"Refusing to write a partial snapshot."
        )
    return rows


def trim(record):
    """Flatten to KEEP_FIELDS, normalising missing values to empty strings."""
    return {field: str(record.get(field, "") or "").strip() for field in KEEP_FIELDS}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true",
                        help="Report per-year counts and write nothing.")
    parser.add_argument("--limit", type=int, default=None,
                        help="Stop after N records (smoke testing).")
    parser.add_argument("--out", default="data/food_recalls.csv",
                        help="Output CSV path (default: data/food_recalls.csv).")
    args = parser.parse_args()

    end_year = date.today().year
    years = list(range(START_YEAR, end_year + 1))

    print(f"openFDA Food Enforcement fetch (v{SCRIPT_VERSION})")
    print(f"Window: {START_YEAR}-{end_year} by recall_initiation_date\n")

    last_updated = api_last_updated()
    print(f"openFDA last_updated: {last_updated}\n")

    counts = {}
    for year in years:
        counts[year] = count_for_year(year)
        print(f"  {year}: {counts[year]:>6,}")

    total = sum(counts.values())
    requests_needed = sum(-(-c // PAGE_SIZE) for c in counts.values())
    print(f"\n  TOTAL: {total:,} records across {len(years)} years")
    print(f"  Requests needed: ~{requests_needed}")

    if args.dry_run:
        print("\nDry run -- nothing written.")
        return

    if args.limit:
        print(f"\nLimiting to {args.limit} record(s).")

    print()
    collected = []
    for year in years:
        if counts[year] == 0:
            continue
        remaining = None if args.limit is None else args.limit - len(collected)
        if remaining is not None and remaining <= 0:
            break
        rows = fetch_year(year, counts[year], cap=remaining)
        collected.extend(rows)
        print(f"  fetched {year}: {len(rows):,} (running total {len(collected):,})")

    if args.limit:
        collected = collected[:args.limit]

    # Product rows are unique by recall_number; a duplicate means we double-paged.
    seen = set()
    deduped = []
    for record in collected:
        key = record.get("recall_number")
        if key in seen:
            continue
        seen.add(key)
        deduped.append(record)
    dupes = len(collected) - len(deduped)
    if dupes:
        print(f"\n  removed {dupes} duplicate recall_number rows")

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=KEEP_FIELDS)
        writer.writeheader()
        for record in deduped:
            writer.writerow(trim(record))

    meta_path = out_path.parent / "fetch_metadata.json"
    meta_path.write_text(json.dumps({
        "script_version": SCRIPT_VERSION,
        "fetched_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "openfda_last_updated": last_updated,
        "source_url": API_URL,
        "date_field": "recall_initiation_date",
        "year_range": [START_YEAR, end_year],
        "total_rows": len(deduped),
        "unique_event_ids": len({r.get("event_id") for r in deduped}),
        "rows_per_year": {str(y): c for y, c in counts.items()},
        "limit_applied": args.limit,
        "columns": KEEP_FIELDS,
    }, indent=2) + "\n", encoding="utf-8")

    print(f"\nWrote {len(deduped):,} rows -> {out_path}")
    print(f"Wrote metadata      -> {meta_path}")


if __name__ == "__main__":
    sys.exit(main())
