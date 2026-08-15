"""Expected shape of the static CSV snapshot.

The app reads one file that never changes during normal operation. That makes
a schema check cheap and worth doing once at load: if the file is edited,
truncated, or re-fetched into a different shape, we want a clear error at
startup rather than empty charts and wrong numbers.
"""

# Order matters -- fetch_data.py writes these in this order, and the guardrail
# test asserts on the order so a silent column reshuffle is caught too.
EXPECTED_COLUMNS = [
    "recall_number",
    "event_id",
    "product_type",
    "status",
    "classification",
    "product_description",
    "reason_for_recall",
    "product_quantity",
    "recalling_firm",
    "city",
    "state",
    "country",
    "voluntary_mandated",
    "initial_firm_notification",
    "distribution_pattern",
    "recall_initiation_date",
    "center_classification_date",
    "report_date",
    "termination_date",
]

# The 2026-08 snapshot holds 29,161 rows. A lower bound rather than an exact
# figure: a legitimate re-fetch adds recent recalls, which must not fail.
# A sharp drop means truncation, and that must fail.
MIN_EXPECTED_ROWS = 29_000

REQUIRED_NON_NULL = ["event_id", "product_description", "reason_for_recall"]


def validate_schema(df):
    """Raise ValueError if the snapshot is not the shape the app expects."""
    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            f"data/food_recalls.csv is missing expected column(s): {missing}. "
            f"Re-run `python fetch_data.py` to rebuild the snapshot."
        )

    if len(df) < MIN_EXPECTED_ROWS:
        raise ValueError(
            f"data/food_recalls.csv has {len(df):,} rows, expected at least "
            f"{MIN_EXPECTED_ROWS:,}. The file looks truncated."
        )

    for column in REQUIRED_NON_NULL:
        if df[column].isna().any():
            n = int(df[column].isna().sum())
            raise ValueError(
                f"data/food_recalls.csv has {n} null value(s) in {column!r}, "
                f"which the aggregation logic depends on."
            )

    return df
