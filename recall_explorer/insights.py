"""key_insights() -- the four Key Insights stat cards, computed once as a pure function.

Pure function over a DataFrame -- no Streamlit, no file I/O. Returns a flat
NamedTuple so app.py only formats and places values into st.metric() calls;
the percentage math, full-year exclusion, and top-reason ranking all live
here, tested against hand-built fixtures.
"""

from collections import namedtuple

from recall_explorer.filters import OTHER_REASON

KeyInsights = namedtuple(
    "KeyInsights",
    [
        "total_events",
        "first_full_year",
        "first_full_year_events",
        "last_full_year",
        "last_full_year_events",
        "pct_change",
        "peak_year",
        "peak_year_events",
        "top_reason",
        "top_reason_events",
        "top_reason_share",
    ],
)


def _empty_result(total_events=0):
    return KeyInsights(
        total_events=total_events,
        first_full_year=None,
        first_full_year_events=None,
        last_full_year=None,
        last_full_year_events=None,
        pct_change=None,
        peak_year=None,
        peak_year_events=None,
        top_reason=None,
        top_reason_events=None,
        top_reason_share=None,
    )


def key_insights(df, coverage_end):
    """Compute the four Key Insights values for the current (filtered) view.

    `coverage_end` is an explicit (year, month) tuple anchored to the *full*
    dataset's coverage -- same convention as severity_trend()'s partial-year
    flag -- so a filtered view never mistakes its own last row for the
    dataset's true coverage boundary.
    """
    if len(df) == 0:
        return _empty_result(total_events=0)

    total_events = df["event_id"].nunique()

    coverage_end_key = coverage_end[0] * 12 + coverage_end[1]

    events_by_year = (
        df.groupby("year")["event_id"].nunique().sort_index()
    )
    full_years = [
        year for year in events_by_year.index if year * 12 + 12 <= coverage_end_key
    ]

    if len(full_years) >= 2:
        first_full_year = full_years[0]
        last_full_year = full_years[-1]
        first_full_year_events = int(events_by_year[first_full_year])
        last_full_year_events = int(events_by_year[last_full_year])
        pct_change = (
            (last_full_year_events - first_full_year_events) / first_full_year_events * 100
        )
    else:
        first_full_year = None
        first_full_year_events = None
        last_full_year = None
        last_full_year_events = None
        pct_change = None

    if full_years:
        full_year_counts = events_by_year.loc[full_years]
        peak_year_events = int(full_year_counts.max())
        # idxmax on a sorted-by-index Series returns the first (earliest) max.
        peak_year = int(full_year_counts.idxmax())
    else:
        peak_year = None
        peak_year_events = None

    # reason_for_recall is an event-level attribute duplicated across an
    # event's product rows -- a handful of events (~0.5%) have drifting text
    # between their own product rows that tags slightly differently. Taking
    # one canonical row per event (the first) avoids letting that drift
    # inflate a tag's count above what the event actually represents.
    canonical = df.drop_duplicates("event_id", keep="first")
    tagged = canonical.explode("reason_tags")
    tag_counts = (
        tagged[tagged["reason_tags"].notna()]
        .groupby("reason_tags")["event_id"]
        .nunique()
    )

    tagged_event_ids = set(tagged.loc[tagged["reason_tags"].notna(), "event_id"])
    other_events = canonical.loc[
        ~canonical["event_id"].isin(tagged_event_ids), "event_id"
    ].nunique()
    if other_events > 0:
        tag_counts[OTHER_REASON] = other_events

    if len(tag_counts) > 0:
        ranked = tag_counts.sort_values(ascending=False)
        top_count = ranked.iloc[0]
        # Deterministic tie-break: among ties for the top count, label asc.
        tied = sorted(ranked[ranked == top_count].index)
        top_reason = tied[0]
        top_reason_events = int(top_count)
        top_reason_share = top_reason_events / total_events * 100
    else:
        top_reason = None
        top_reason_events = None
        top_reason_share = None

    return KeyInsights(
        total_events=total_events,
        first_full_year=first_full_year,
        first_full_year_events=first_full_year_events,
        last_full_year=last_full_year,
        last_full_year_events=last_full_year_events,
        pct_change=pct_change,
        peak_year=peak_year,
        peak_year_events=peak_year_events,
        top_reason=top_reason,
        top_reason_events=top_reason_events,
        top_reason_share=top_reason_share,
    )
