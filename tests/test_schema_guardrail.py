"""The guardrail: does data/food_recalls.csv still look like what we built against?

This is the one test whose job is to fail loudly if the snapshot is edited,
moved, re-fetched, or drifts in shape. Everything downstream assumes this
file's structure; without this test, a changed CSV produces wrong charts
silently rather than a clear error.

Deliberately asserts shape and bounds, not exact row counts per year -- a
re-fetch legitimately adds recent rows, and that should not be a failure.
"""

import pandas as pd
import pytest

from recall_explorer.schema import (
    EXPECTED_COLUMNS,
    MIN_EXPECTED_ROWS,
    validate_schema,
)
from recall_explorer.pipeline import DATA_PATH


@pytest.fixture(scope="module")
def raw():
    return pd.read_csv(DATA_PATH, dtype=str)


def test_snapshot_file_exists():
    assert DATA_PATH.exists(), (
        f"{DATA_PATH} is missing. Run: python fetch_data.py"
    )


def test_columns_match_exactly_and_in_order(raw):
    assert list(raw.columns) == EXPECTED_COLUMNS


def test_snapshot_has_a_plausible_number_of_rows(raw):
    assert len(raw) >= MIN_EXPECTED_ROWS


def test_key_columns_are_populated(raw):
    # event_id drives the event lens; without it the whole side-by-side
    # comparison silently collapses to the product lens.
    assert raw["event_id"].notna().all()
    assert raw["product_description"].notna().all()
    assert raw["reason_for_recall"].notna().all()


def test_classification_has_only_the_three_known_classes(raw):
    assert set(raw["classification"].dropna()) == {"Class I", "Class II", "Class III"}


def test_validate_schema_accepts_the_real_file(raw):
    validate_schema(raw)  # must not raise


def test_validate_schema_rejects_a_missing_column():
    broken = pd.DataFrame({"recall_number": ["F-1"]})
    with pytest.raises(ValueError, match="missing"):
        validate_schema(broken)
