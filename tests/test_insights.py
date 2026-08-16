"""Unit tests for key_insights().

Hand-built DataFrames only -- these never touch data/food_recalls.csv.
"""

import pandas as pd
import pytest

from recall_explorer.insights import key_insights

# --- Total events: event lens, not product lens -----------------------------
# E1 has two product rows -- total_events must count it once.

TOTAL_FIXTURE = pd.DataFrame({
    "event_id": ["E1", "E1", "E2"],
    "year": [2020, 2020, 2020],
    "reason_tags": [["Salmonella"], ["Salmonella"], ["Listeria"]],
})


def test_total_events_counts_distinct_events_not_product_rows():
    result = key_insights(TOTAL_FIXTURE, coverage_end=(2020, 12))
    assert result.total_events == 2


# --- % change: first -> last full year, partial year excluded ---------------
# 2012: 2 events, 2013: 1 event, 2014: 3 events -- 2014 is partial
# (coverage_end=(2014, 6), so year*12+12=24180 > coverage key), so the
# comparison must run 2012 -> 2013, not 2012 -> 2014.

PCT_CHANGE_FIXTURE = pd.DataFrame({
    "event_id": ["A1", "A2", "B1", "C1", "C2", "C3"],
    "year": [2012, 2012, 2013, 2014, 2014, 2014],
    "reason_tags": [[], [], [], [], [], []],
})


def test_pct_change_excludes_the_partial_year():
    result = key_insights(PCT_CHANGE_FIXTURE, coverage_end=(2014, 6))
    assert result.first_full_year == 2012
    assert result.first_full_year_events == 2
    assert result.last_full_year == 2013
    assert result.last_full_year_events == 1
    assert result.pct_change == -50.0


def test_pct_change_sign_is_positive_when_events_increase():
    fixture = pd.DataFrame({
        "event_id": ["A1", "B1", "B2"],
        "year": [2012, 2013, 2013],
        "reason_tags": [[], [], []],
    })
    result = key_insights(fixture, coverage_end=(2013, 12))
    assert result.pct_change == 100.0


def test_pct_change_is_none_with_only_one_full_year():
    fixture = pd.DataFrame({
        "event_id": ["A1", "A2"],
        "year": [2014, 2014],
        "reason_tags": [[], []],
    })
    result = key_insights(fixture, coverage_end=(2014, 6))
    assert result.pct_change is None
    assert result.first_full_year is None
    assert result.last_full_year is None


def test_pct_change_is_none_with_zero_full_years():
    # A view filtered down to just the partial year -- nothing to compare.
    fixture = pd.DataFrame({
        "event_id": ["A1"],
        "year": [2026],
        "reason_tags": [[]],
    })
    result = key_insights(fixture, coverage_end=(2026, 6))
    assert result.pct_change is None


# --- Peak year: excludes the partial year even if it has the most events ----

PEAK_FIXTURE = pd.DataFrame({
    "event_id": ["A1", "B1", "B2", "C1", "C2", "C3", "C4"],
    "year": [2012, 2013, 2013, 2014, 2014, 2014, 2014],
    "reason_tags": [[], [], [], [], [], [], []],
})


def test_peak_year_excludes_the_partial_year():
    # 2014 has 4 events, the most of any year, but is partial under this
    # coverage_end -- the peak must fall back to 2013's 2 events.
    result = key_insights(PEAK_FIXTURE, coverage_end=(2014, 6))
    assert result.peak_year == 2013
    assert result.peak_year_events == 2


def test_peak_year_tie_resolves_to_the_earliest_year():
    fixture = pd.DataFrame({
        "event_id": ["A1", "A2", "B1", "B2"],
        "year": [2012, 2012, 2013, 2013],
        "reason_tags": [[], [], [], []],
    })
    result = key_insights(fixture, coverage_end=(2013, 12))
    assert result.peak_year == 2012
    assert result.peak_year_events == 2


# --- Top reason: event-level, multi-label, "Other" is a first-class option --
# reason_for_recall is an event-level attribute duplicated onto every product
# row of that event -- so an event's reason is read from its *first* product
# row. This matters when an event's own rows disagree (real, if rare, in the
# source data -- a handful of events have slightly drifting text between
# their product rows): the first row wins, the rest are ignored, rather than
# unioning tags across every row and inflating a tag's event count.

REASON_FIXTURE = pd.DataFrame({
    "event_id": ["E1", "E1", "E2", "E3", "E4"],
    "year": [2020, 2020, 2020, 2020, 2020],
    "reason_tags": [
        ["Salmonella", "Listeria"],  # E1's first (canonical) row
        ["Salmonella", "Listeria"],  # E1's second row, same tags -- no drift
        ["Listeria"],
        [],
        [],
    ],
})


def test_top_reason_counts_distinct_events_per_tag():
    # Salmonella: E1 only (1 event). Listeria: E1 + E2 (2 events) -- must win.
    result = key_insights(REASON_FIXTURE, coverage_end=(2020, 12))
    assert result.top_reason == "Listeria"
    assert result.top_reason_events == 2


def test_only_the_first_product_row_of_an_event_determines_its_reason():
    # E1's second row has drifted to a different tag than its first row --
    # the first row is canonical, so Listeria must NOT gain a count from it.
    # E2/E3 both canonically tag Salmonella, so if E1's drifted second row
    # were (wrongly) counted, Listeria and Salmonella would tie at 2 instead
    # of Salmonella winning outright at 2 to Listeria's real 0.
    fixture = pd.DataFrame({
        "event_id": ["E1", "E1", "E2", "E3"],
        "year": [2020, 2020, 2020, 2020],
        "reason_tags": [["Salmonella"], ["Listeria"], ["Salmonella"], []],
    })
    result = key_insights(fixture, coverage_end=(2020, 12))
    assert result.top_reason == "Salmonella"
    assert result.top_reason_events == 2


def test_other_is_eligible_and_can_win():
    fixture = pd.DataFrame({
        "event_id": ["E1", "E2", "E3"],
        "year": [2020, 2020, 2020],
        "reason_tags": [["Salmonella"], [], []],
    })
    result = key_insights(fixture, coverage_end=(2020, 12))
    assert result.top_reason == "Other"
    assert result.top_reason_events == 2
    assert result.top_reason_share == pytest.approx(2 / 3 * 100)


def test_event_with_a_tagged_first_row_is_not_other():
    # E1's canonical (first) row carries a tag -- the event must not count
    # toward "Other" regardless of what a later row for the same event says.
    fixture = pd.DataFrame({
        "event_id": ["E1", "E1"],
        "year": [2020, 2020],
        "reason_tags": [["Salmonella"], []],
    })
    result = key_insights(fixture, coverage_end=(2020, 12))
    assert result.top_reason == "Salmonella"
    assert result.top_reason_events == 1
    assert "Other" != result.top_reason


def test_top_reason_share_is_events_over_total_events():
    result = key_insights(REASON_FIXTURE, coverage_end=(2020, 12))
    # total_events = 4 (E1..E4); Listeria = 2 events -> 50%.
    assert result.top_reason_share == pytest.approx(50.0)


# --- Zero state: empty frame degrades gracefully, never raises --------------


def test_empty_frame_returns_zeros_and_nones_without_raising():
    empty = pd.DataFrame({"event_id": [], "year": [], "reason_tags": []})
    result = key_insights(empty, coverage_end=(2020, 12))
    assert result.total_events == 0
    assert result.pct_change is None
    assert result.peak_year is None
    assert result.top_reason is None


# --- Does not mutate the input ----------------------------------------------


def test_does_not_mutate_the_input():
    before = PEAK_FIXTURE.copy()
    key_insights(PEAK_FIXTURE, coverage_end=(2014, 6))
    pd.testing.assert_frame_equal(PEAK_FIXTURE, before)
