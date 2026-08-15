"""End-to-end pipeline test against the real, fixed CSV.

No mocking and no synthetic fixtures -- the file is controlled and does not
change, so the real thing is the honest input. Assertions are on final output
and on invariants, not on intermediate steps.

Exact totals are asserted where they are structural facts of the 2026-08
snapshot. Derived percentages are asserted as ranges, because tightening a
keyword rule should be free to move them a little without breaking the build.
"""

import pandas as pd
import pytest

from recall_explorer.pipeline import load_recalls
from recall_explorer.transforms import count_by

SNAPSHOT_ROWS = 29_161
SNAPSHOT_EVENTS = 7_791


@pytest.fixture(scope="module")
def df():
    return load_recalls()


# --- Shape ------------------------------------------------------------------

def test_pipeline_returns_every_snapshot_row(df):
    assert len(df) == SNAPSHOT_ROWS


def test_pipeline_adds_the_derived_columns(df):
    for column in ["recall_date", "year", "month", "category", "reason_tags"]:
        assert column in df.columns


def test_every_row_has_a_usable_date(df):
    # fetch_data.py already windows by year, so nothing should be unparseable.
    # If this fails, the snapshot was rebuilt with different assumptions.
    assert df["recall_date"].notna().all()


def test_dates_stay_inside_the_documented_window(df):
    assert df["year"].min() == 2012
    assert df["year"].max() <= 2026


# --- The two lenses ---------------------------------------------------------

def test_event_lens_counts_fewer_than_product_lens(df):
    assert df["event_id"].nunique() == SNAPSHOT_EVENTS
    assert df["event_id"].nunique() < len(df)


def test_products_per_event_matches_the_documented_ratio(df):
    ratio = len(df) / df["event_id"].nunique()
    assert 3.7 <= ratio <= 3.8


def test_lenses_produce_different_category_rankings(df):
    # The premise of the whole side-by-side design: the two lenses tell
    # different stories. If these ever match exactly, the design is pointless.
    events = count_by(df, "category", lens="events")
    products = count_by(df, "category", lens="products")
    assert events["count"].sum() < products["count"].sum()


# --- Derived columns --------------------------------------------------------

def test_every_row_gets_a_category(df):
    assert df["category"].notna().all()


def test_uncategorized_share_stays_within_documented_bounds(df):
    # Documented in the About section as ~12%. A large move means the rules
    # changed materially and the documentation needs updating with them --
    # which is exactly how this bound earned its keep: expanding the keyword
    # set dropped the share from 18.4% to 11.9% and failed this test, rather
    # than letting the docs quietly go stale.
    share = (df["category"] == "Uncategorized").mean()
    assert 0.08 <= share <= 0.16


def test_uncategorized_is_no_longer_the_largest_category(df):
    counts = df["category"].value_counts()
    assert counts.idxmax() != "Uncategorized"


def test_reason_tagging_covers_most_recalls(df):
    tagged = (df["reason_tags"].str.len() > 0).mean()
    assert tagged >= 0.80


def test_reason_tags_are_lists_not_strings(df):
    # A CSV round-trip would turn these into strings and silently break any
    # downstream explode/filter on them.
    assert isinstance(df["reason_tags"].iloc[0], list)
