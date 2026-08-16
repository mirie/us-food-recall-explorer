"""apply_filters() -- the one function every filter widget in app.py feeds into.

Pure function over a DataFrame -- no Streamlit, no file I/O. Each parameter is
`None` or `[]` to mean "no filter on this dimension"; both spellings collapse
to the same unfiltered behaviour so a widget's empty-selection return value
(Streamlit's multiselect default) reads directly as "show all", per the PRD's
stated default filter state.

Dimensions compose as AND (year range AND category AND ...). Only within the
reason dimension is it OR across selected tags -- see reasons parameter below.
"""

OTHER_REASON = "Other"


def apply_filters(df, year_range=None, categories=None, reasons=None, severities=None):
    """Return the subset of `df` matching every active filter.

    reasons: OR across selected tags -- a row matches if reason_tags contains
    ANY of the selected labels, or if OTHER_REASON is selected and the row's
    reason_tags is empty (untagged). Selecting Salmonella + Listeria matches
    rows tagged with either, not only rows tagged with both (handoff decision,
    matches the PRD's own "Salmonella or Listeria" phrasing).
    """
    out = df

    if year_range:
        start, end = year_range
        out = out[out["year"].between(start, end)]

    if categories:
        out = out[out["category"].isin(categories)]

    if severities:
        out = out[out["classification"].isin(severities)]

    if reasons:
        want_other = OTHER_REASON in reasons
        want_tags = set(reasons) - {OTHER_REASON}

        def matches(tags):
            if want_tags and any(t in want_tags for t in tags):
                return True
            if want_other and not tags:
                return True
            return False

        out = out[out["reason_tags"].map(matches)]

    return out.copy()


def restrict_trend_to_severities(trend, severities):
    """Drop severity_trend() rows for classifications the user filtered out.

    severity_trend() always back-fills all three SEVERITY_ORDER classes as
    real zeros (correct for the unfiltered view -- a class with genuinely no
    recalls in a year is still a real zero, not a hole). But once the
    severity filter itself excludes a class, that class should vanish from
    the trend chart entirely, not render as a flat zero line pinned to the
    x-axis. `severities` falsy (None or []) means no filter -- return as-is.
    """
    if not severities:
        return trend
    return trend[trend["classification"].isin(severities)].copy()
