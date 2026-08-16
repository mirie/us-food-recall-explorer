"""Unit tests for date parsing and the event/product aggregation lenses.

Hand-built DataFrames only -- these never touch data/food_recalls.csv.
"""

import pandas as pd
import pytest

from recall_explorer.transforms import (
    count_by,
    parse_recall_dates,
    seasonality_matrix,
    severity_trend,
)


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


# --- The seasonality grid ---------------------------------------------------
# Five product rows across three events and two years, deliberately sparse:
#
#   2020-01  E1 x2   two products, one event -- the lenses must disagree here
#   2020-03  E2 x1
#   2021-05  E3 x1 \  one event spanning a month boundary; it is a real recall
#   2021-06  E3 x1 /  in both months and must count once in each
#
# Every other month of 2020 and 2021 is empty, which is the point: the grid has
# to emit those cells rather than skipping them.

SEASONALITY_FIXTURE = pd.DataFrame({
    "event_id": ["E1", "E1", "E2", "E3", "E3"],
    "year": [2020, 2020, 2020, 2021, 2021],
    "month": [1, 1, 3, 5, 6],
})


def cell(matrix, year, month):
    """The single grid row for one (year, month)."""
    match = matrix[(matrix["year"] == year) & (matrix["month"] == month)]
    assert len(match) == 1, f"expected exactly one cell for {year}-{month}"
    return match.iloc[0]


def test_product_lens_counts_every_row_in_its_cell():
    matrix = seasonality_matrix(SEASONALITY_FIXTURE, lens="products")
    assert cell(matrix, 2020, 1)["count"] == 2


def test_event_lens_counts_distinct_events_in_its_cell():
    matrix = seasonality_matrix(SEASONALITY_FIXTURE, lens="events")
    assert cell(matrix, 2020, 1)["count"] == 1


def test_the_two_lenses_disagree_across_the_grid():
    products = seasonality_matrix(SEASONALITY_FIXTURE, lens="products")
    events = seasonality_matrix(SEASONALITY_FIXTURE, lens="events")
    assert products["count"].sum() == 5
    assert events["count"].sum() == 4


def test_an_event_spanning_two_months_counts_once_in_each():
    # E3 has one product in May and one in June. Under the event lens it is one
    # event, but it genuinely happened in both months -- deduplicating it to a
    # single cell would silently drop a month of activity.
    matrix = seasonality_matrix(SEASONALITY_FIXTURE, lens="events")
    assert cell(matrix, 2021, 5)["count"] == 1
    assert cell(matrix, 2021, 6)["count"] == 1


def test_empty_month_inside_covered_range_is_a_real_zero():
    # February 2020 has no recalls in the fixture but sits well inside the
    # covered span -- it must read as "zero recalls happened", not "unknown".
    matrix = seasonality_matrix(SEASONALITY_FIXTURE, lens="products")
    row = cell(matrix, 2020, 2)
    assert row["count"] == 0
    assert row["covered"] is True or row["covered"] == True  # noqa: E712


def test_month_past_coverage_end_is_uncovered():
    # The fixture's data ends in 2021-06, but if the caller says coverage only
    # extends through May, June must render as "not yet observed" rather than
    # as a zero -- the whole point of the flag is to keep those two apart.
    matrix = seasonality_matrix(
        SEASONALITY_FIXTURE, lens="events", coverage_end=(2021, 5)
    )
    row = cell(matrix, 2021, 6)
    assert row["covered"] is False or row["covered"] == False  # noqa: E712
    assert pd.isna(row["count"])


def test_explicit_coverage_end_beyond_the_data_still_marks_months_covered():
    # This is the August-2026 case: reporting lag can leave a covered month
    # with no rows yet. An explicit coverage_end past the last real row must
    # still mark that month covered (a real zero), not unobserved.
    matrix = seasonality_matrix(
        SEASONALITY_FIXTURE, lens="events", coverage_end=(2021, 12)
    )
    row = cell(matrix, 2021, 12)
    assert row["covered"] is True or row["covered"] == True  # noqa: E712
    assert row["count"] == 0


def test_coverage_end_defaults_to_the_last_month_present_in_df():
    # No coverage_end given -- the fixture's last row is 2021-06, so that
    # month must be covered and nothing past it should appear as covered.
    matrix = seasonality_matrix(SEASONALITY_FIXTURE, lens="events")
    assert cell(matrix, 2021, 6)["covered"] == True  # noqa: E712


def test_rows_are_in_calendar_order():
    matrix = seasonality_matrix(SEASONALITY_FIXTURE, lens="products")
    pairs = list(zip(matrix["year"], matrix["month"]))
    assert pairs == sorted(pairs)


def test_grid_is_rectangular_across_the_full_year_span():
    # Years 2020 and 2021 are both present in the fixture -- the grid must
    # emit all 12 months for each, 24 rows total, not just the months that
    # happen to have data.
    matrix = seasonality_matrix(SEASONALITY_FIXTURE, lens="products")
    assert len(matrix) == 24
    for year in (2020, 2021):
        assert sorted(matrix.loc[matrix["year"] == year, "month"]) == list(range(1, 13))


def test_invalid_lens_raises():
    with pytest.raises(ValueError):
        seasonality_matrix(SEASONALITY_FIXTURE, lens="nonsense")


# --- The severity trend grid ------------------------------------------------
# Four product rows across four events and two years:
#
#   2020  E1 x2, E2 x1   all Class I -- product lens sees 3 rows, event lens
#                        sees 2 distinct events; the lenses must disagree here
#   2021  E3 x1          Class II
#   2021  E4 x1          "Mystery" -- a classification value the app doesn't
#                        expect, which must still surface rather than vanish
#
# 2020 has no Class II/III/Mystery rows and 2021 has no Class I/III rows --
# both must read as real zeros, not missing cells.

TREND_FIXTURE = pd.DataFrame({
    "event_id": ["E1", "E1", "E2", "E3", "E4"],
    "year": [2020, 2020, 2020, 2021, 2021],
    "month": [3, 3, 6, 1, 9],
    "classification": ["Class I", "Class I", "Class I", "Class II", "Mystery"],
})


def trend_cell(trend, year, classification):
    match = trend[(trend["year"] == year) & (trend["classification"] == classification)]
    assert len(match) == 1, f"expected exactly one row for {year}/{classification}"
    return match.iloc[0]


def test_product_lens_counts_every_row_in_its_cell_trend():
    trend = severity_trend(TREND_FIXTURE, lens="products")
    assert trend_cell(trend, 2020, "Class I")["count"] == 3


def test_event_lens_counts_distinct_events_not_rows_trend():
    trend = severity_trend(TREND_FIXTURE, lens="events")
    assert trend_cell(trend, 2020, "Class I")["count"] == 2


def test_the_two_lenses_disagree_on_a_multi_product_event():
    products = severity_trend(TREND_FIXTURE, lens="products")
    events = severity_trend(TREND_FIXTURE, lens="events")
    assert products["count"].sum() == 5
    assert events["count"].sum() == 4


def test_grid_is_rectangular_across_years_and_classifications():
    # 2 years x 4 classifications (Class I/II/III plus the unexpected
    # "Mystery" value) = 8 rows, not just the combinations with data.
    trend = severity_trend(TREND_FIXTURE, lens="events")
    assert len(trend) == 8
    for year in (2020, 2021):
        classes = sorted(trend.loc[trend["year"] == year, "classification"])
        assert classes == ["Class I", "Class II", "Class III", "Mystery"]


def test_class_with_no_rows_in_a_year_is_a_real_zero():
    trend = severity_trend(TREND_FIXTURE, lens="events")
    assert trend_cell(trend, 2020, "Class II")["count"] == 0
    assert trend_cell(trend, 2021, "Class I")["count"] == 0


def test_unexpected_classification_value_is_not_silently_dropped():
    trend = severity_trend(TREND_FIXTURE, lens="events")
    assert trend_cell(trend, 2021, "Mystery")["count"] == 1


def test_year_past_coverage_end_is_marked_partial():
    # Fixture's last row is 2021-09; if coverage only extends through July,
    # 2021 is a partial year -- it hasn't reached December yet.
    trend = severity_trend(TREND_FIXTURE, lens="events", coverage_end=(2021, 7))
    row = trend_cell(trend, 2021, "Class II")
    assert row["partial"] is True or row["partial"] == True  # noqa: E712


def test_year_reaching_december_is_not_partial():
    trend = severity_trend(TREND_FIXTURE, lens="events", coverage_end=(2021, 12))
    row = trend_cell(trend, 2021, "Class II")
    assert row["partial"] is False or row["partial"] == False  # noqa: E712


def test_coverage_end_defaults_to_the_last_month_present_in_df_trend():
    # No coverage_end given -- fixture's last row is 2021-09, so 2021 hasn't
    # reached December and must default to partial.
    trend = severity_trend(TREND_FIXTURE, lens="events")
    row = trend_cell(trend, 2021, "Class II")
    assert row["partial"] is True or row["partial"] == True  # noqa: E712
    row_2020 = trend_cell(trend, 2020, "Class I")
    assert row_2020["partial"] is False or row_2020["partial"] == False  # noqa: E712


def test_rows_ordered_by_year_then_severity_order():
    trend = severity_trend(TREND_FIXTURE, lens="events", coverage_end=(2021, 12))
    year_2020 = list(trend.loc[trend["year"] == 2020, "classification"])
    assert year_2020[:3] == ["Class I", "Class II", "Class III"]


def test_invalid_lens_raises_trend():
    with pytest.raises(ValueError):
        severity_trend(TREND_FIXTURE, lens="nonsense")
