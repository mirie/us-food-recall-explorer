"""Unit tests for apply_filters().

Hand-built DataFrames only -- these never touch data/food_recalls.csv.
"""

import pandas as pd

from recall_explorer.filters import apply_filters, restrict_trend_to_severities

# Five product rows chosen so no two filters select the same subset -- if a
# filter is silently ignored, some other assertion in this file goes red rather
# than everything coincidentally agreeing. Rows 2 and 4 are deliberately
# untagged (reason_tags == []), which is what the "Other" option selects.
FIXTURE = pd.DataFrame({
    "event_id": ["E1", "E2", "E3", "E4", "E5"],
    "year": [2013, 2015, 2015, 2020, 2024],
    "category": ["Produce", "Produce", "Dairy", "Bakery", "Dairy"],
    "classification": ["Class I", "Class II", "Class I", "Class III", "Class II"],
    "reason_tags": [
        ["Salmonella"],
        ["Listeria", "Undeclared allergen"],
        [],
        ["Undeclared allergen"],
        [],
    ],
})


def ids(result):
    return result["event_id"].tolist()


# --- Each dimension in isolation --------------------------------------------


def test_year_range_is_inclusive_at_both_ends():
    result = apply_filters(FIXTURE, year_range=(2015, 2020))
    assert ids(result) == ["E2", "E3", "E4"]


def test_category_filter_keeps_only_selected_categories():
    result = apply_filters(FIXTURE, categories=["Dairy"])
    assert ids(result) == ["E3", "E5"]


def test_severity_filter_keeps_only_selected_classifications():
    result = apply_filters(FIXTURE, severities=["Class I"])
    assert ids(result) == ["E1", "E3"]


# --- The unfiltered default state -------------------------------------------


def test_no_filters_returns_every_row():
    result = apply_filters(FIXTURE)
    assert ids(result) == ["E1", "E2", "E3", "E4", "E5"]


def test_empty_selections_mean_no_filter_not_no_rows():
    # Streamlit's multiselect returns [] when nothing is selected, and the
    # default state is "show all" -- so [] must behave exactly like None.
    result = apply_filters(FIXTURE, categories=[], reasons=[], severities=[])
    assert ids(result) == ["E1", "E2", "E3", "E4", "E5"]


def test_filtering_does_not_mutate_the_input():
    apply_filters(FIXTURE, categories=["Dairy"])
    assert len(FIXTURE) == 5


# --- Two dimensions combined: AND across dimensions -------------------------


def test_year_range_and_category_compose_as_and():
    # Produce alone is E1, E2. Restricting to 2015+ drops E1, leaving only E2 --
    # proves the two filters narrow jointly rather than either alone or a union.
    result = apply_filters(FIXTURE, year_range=(2015, 2024), categories=["Produce"])
    assert ids(result) == ["E2"]


# --- Reason filter: OR across selected tags, "Other" as its own option ------


def test_reason_filter_is_or_across_selected_tags():
    # E1 has only Salmonella, E2 has only Listeria -- selecting both tags must
    # return both rows (OR), not neither (which AND would give here).
    result = apply_filters(FIXTURE, reasons=["Salmonella", "Listeria"])
    assert ids(result) == ["E1", "E2"]


def test_reason_filter_matches_a_multi_tag_row_on_just_one_selected_tag():
    # E2 carries two tags; selecting only one of them ("Listeria") must still
    # surface the row -- OR semantics operate per-tag, not per-row-exact-match.
    result = apply_filters(FIXTURE, reasons=["Listeria"])
    assert ids(result) == ["E2"]


def test_reason_filter_without_other_drops_untagged_rows():
    result = apply_filters(FIXTURE, reasons=["Salmonella"])
    assert "E3" not in ids(result)
    assert "E5" not in ids(result)


def test_reason_filter_with_other_added_brings_untagged_rows_back():
    result = apply_filters(FIXTURE, reasons=["Salmonella", "Other"])
    assert ids(result) == ["E1", "E3", "E5"]


def test_other_alone_selects_only_untagged_rows():
    result = apply_filters(FIXTURE, reasons=["Other"])
    assert ids(result) == ["E3", "E5"]


# --- Zero-result combinations -----------------------------------------------


def test_impossible_combination_returns_empty_frame_without_raising():
    result = apply_filters(FIXTURE, categories=["Produce"], severities=["Class III"])
    assert len(result) == 0
    assert list(result.columns) == list(FIXTURE.columns)


# --- restrict_trend_to_severities: drops de-selected severity lines --------
# severity_trend() always back-fills all three SEVERITY_ORDER classes as real
# zeros (locked in by test_transforms.py's rectangular-grid test) -- correct
# for the unfiltered view, but wrong once the severity filter itself excludes
# a class: a de-selected severity should vanish from the trend chart, not
# render as a flat zero line. This trims the transform's output after the
# fact rather than changing severity_trend()'s always-rectangular contract.

TREND = pd.DataFrame({
    "year": [2020, 2020, 2020, 2021, 2021, 2021],
    "classification": ["Class I", "Class II", "Class III"] * 2,
    "count": [5, 0, 0, 3, 1, 0],
})


def test_no_severity_filter_leaves_trend_untouched():
    result = restrict_trend_to_severities(TREND, severities=None)
    assert len(result) == len(TREND)


def test_empty_severity_filter_leaves_trend_untouched():
    result = restrict_trend_to_severities(TREND, severities=[])
    assert len(result) == len(TREND)


def test_selected_severity_drops_deselected_classification_rows_entirely():
    result = restrict_trend_to_severities(TREND, severities=["Class I"])
    assert set(result["classification"]) == {"Class I"}
    assert len(result) == 2  # one row per year, not zero-filled for II/III
