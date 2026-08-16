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
from recall_explorer.schema import EXPECTED_COLUMNS, MIN_EXPECTED_ROWS
from recall_explorer.transforms import count_by

# The raw 2026-08 snapshot holds 29,161 rows / 7,791 events. Two rows carry a
# blank recall_number (an openFDA data gap, not a fetch_data.py bug) and are
# excluded by load_recalls() as incomplete records -- see its comment.
SNAPSHOT_ROWS = 29_159
SNAPSHOT_EVENTS = 7_789


@pytest.fixture(scope="module")
def df():
    return load_recalls()


# --- Shape ------------------------------------------------------------------

def test_pipeline_returns_every_snapshot_row(df):
    assert len(df) == SNAPSHOT_ROWS


def test_pipeline_excludes_rows_with_no_recall_number(df):
    # The two known incomplete rows (event_ids 99068, 99205) must not appear.
    assert df["recall_number"].notna().all()
    assert (df["recall_number"].str.strip() != "").all()
    assert set(df["event_id"]).isdisjoint({"99068", "99205"})


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
    # Post Phase-5 LLM reclassification, measured at 211/29,159 (~0.72%) --
    # see BUILD_LOG.md Entry 22-23 and fetch_metadata.json's
    # llm_classification_pass block. A large move means the classification
    # pass changed materially and the documentation needs updating with it --
    # which is exactly how this bound earned its keep under the old
    # keyword-derived category (it caught an 18.4%-to-11.9% rules change).
    share = (df["category"] == "Uncategorized").mean()
    assert 0.003 <= share <= 0.02


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


# --- Category derivation: direct read of llm_category (Phase 5) ------------
# Post-refactor, pipeline.py no longer runs assign_category() or any keyword
# override at load time -- category comes straight from the derived file's
# llm_category column, blank falling back to Uncategorized. Exercised through
# load_recalls() itself (rather than a standalone pure function, since the
# refactor deliberately inlined this) against a synthetic CSV built to clear
# validate_schema()'s 29,000-row floor, with three planted rows.

def _make_classified_csv(tmp_path, special_rows):
    filler = {col: "x" for col in EXPECTED_COLUMNS}
    filler.update(
        {
            "recall_number": "F-0000-2020",
            "event_id": "1",
            "product_description": "filler product",
            "reason_for_recall": "filler reason",
            "recall_initiation_date": "20200101",
        }
    )
    rows = [dict(filler, llm_category="Produce") for _ in range(MIN_EXPECTED_ROWS)]
    for i, special in enumerate(special_rows):
        rows[i] = dict(filler, recall_number=f"F-SPECIAL-{i}", **special)

    path = tmp_path / "classified.csv"
    pd.DataFrame(rows, columns=EXPECTED_COLUMNS + ["llm_category"]).to_csv(path, index=False)
    return path


def test_llm_category_label_present_is_used(tmp_path):
    path = _make_classified_csv(
        tmp_path, [{"product_description": "Vitamin C tablets", "llm_category": "Supplements"}]
    )
    out = load_recalls(path)
    assert out.loc[out["recall_number"] == "F-SPECIAL-0", "category"].iloc[0] == "Supplements"


def test_llm_category_blank_falls_back_to_uncategorized(tmp_path):
    path = _make_classified_csv(
        tmp_path, [{"product_description": "Assorted items", "llm_category": ""}]
    )
    out = load_recalls(path)
    assert out.loc[out["recall_number"] == "F-SPECIAL-0", "category"].iloc[0] == "Uncategorized"


def test_no_keyword_inference_at_load_time(tmp_path):
    # "milk" would have keyword-matched Dairy under the retired assign_category
    # rules. With llm_category blank, the row must fall back to Uncategorized
    # rather than any keyword ever inferring a category again.
    path = _make_classified_csv(
        tmp_path, [{"product_description": "Whole milk, 1 gallon", "llm_category": ""}]
    )
    out = load_recalls(path)
    assert out.loc[out["recall_number"] == "F-SPECIAL-0", "category"].iloc[0] == "Uncategorized"


def test_classified_csv_has_llm_category_for_essentially_every_row(df):
    missing_share = (df["llm_category"].isna() | (df["llm_category"].str.strip() == "")).mean()
    assert missing_share < 0.001
