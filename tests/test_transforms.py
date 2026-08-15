"""Unit tests for date parsing and the event/product aggregation lenses.

Hand-built DataFrames only -- these never touch data/food_recalls.csv.
"""

import pandas as pd

from recall_explorer.transforms import count_by, parse_recall_dates


def test_yyyymmdd_string_becomes_a_real_date():
    df = pd.DataFrame({"recall_initiation_date": ["20150704"]})
    out = parse_recall_dates(df)
    assert out.loc[0, "recall_date"] == pd.Timestamp("2015-07-04")


def test_malformed_date_becomes_null_rather_than_raising():
    # A real value in openFDA's data is "02121207". One bad row must not take
    # down the whole load.
    df = pd.DataFrame({"recall_initiation_date": ["02121207", "20150704"]})
    out = parse_recall_dates(df)
    assert pd.isna(out.loc[0, "recall_date"])
    assert out.loc[1, "recall_date"] == pd.Timestamp("2015-07-04")


def test_derives_year_and_month_for_trend_and_seasonality():
    df = pd.DataFrame({"recall_initiation_date": ["20150704"]})
    out = parse_recall_dates(df)
    assert out.loc[0, "year"] == 2015
    assert out.loc[0, "month"] == 7


# --- The two lenses ---------------------------------------------------------
# Three product rows spanning two events: event E1 has two products, E2 has one.
# Counting the same data both ways is the app's central structural idea, so the
# two lenses must disagree here -- if they ever agree, the fixture is wrong.

LENS_FIXTURE = pd.DataFrame({
    "event_id": ["E1", "E1", "E2"],
    "recall_number": ["F-1", "F-2", "F-3"],
    "category": ["Produce", "Produce", "Dairy"],
})


def test_product_lens_counts_every_row():
    result = count_by(LENS_FIXTURE, "category", lens="products")
    assert result.set_index("category")["count"].to_dict() == {"Produce": 2, "Dairy": 1}


def test_event_lens_counts_distinct_events_not_rows():
    result = count_by(LENS_FIXTURE, "category", lens="events")
    assert result.set_index("category")["count"].to_dict() == {"Produce": 1, "Dairy": 1}


def test_the_two_lenses_disagree_on_multi_product_events():
    products = count_by(LENS_FIXTURE, "category", lens="products")
    events = count_by(LENS_FIXTURE, "category", lens="events")
    assert products["count"].sum() == 3
    assert events["count"].sum() == 2
