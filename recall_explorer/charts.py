"""Altair chart builders.

Pure functions from shaped data (transforms.py output) to alt.Chart objects --
no Streamlit calls, no file I/O.
"""

import altair as alt

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# Validated categorical palette (see dataviz skill, references/palette.md).
# Fixed slot order -- identity, not magnitude, so hue assignment never shifts
# with the data. Single accent for the top-foods bars (category is a single
# unordered dimension, not three things to distinguish by hue).
BAR_ACCENT = "#2a78d6"  # categorical slot 1 (blue)
SEVERITY_COLORS = {
    "Class I": "#2a78d6",    # slot 1, blue
    "Class II": "#eb6834",   # slot 2, orange
    "Class III": "#1baf7a",  # slot 3, aqua
}


def seasonality_heatmap(matrix, lens_label):
    """Month x year heatmap of recall counts, from seasonality_matrix() output.

    Uncovered cells (not yet observed, see transforms.seasonality_matrix) are
    dropped rather than drawn as zero, so they render as page background
    instead of asserting data that doesn't exist yet.

    Each call gets its own colour scale -- events and products run at very
    different magnitudes (~3.7x apart on this dataset), and a shared scale
    would wash the smaller lens out entirely.
    """
    data = matrix[matrix["covered"]].copy()
    data["count"] = data["count"].astype(int)
    data["month_name"] = data["month"].map(lambda m: MONTH_NAMES[m - 1])
    data["year"] = data["year"].astype(str)

    return (
        alt.Chart(data)
        .mark_rect()
        .encode(
            x=alt.X("month_name:O", sort=MONTH_NAMES, title="Month",
                    axis=alt.Axis(labelAngle=0)),
            y=alt.Y("year:O", sort="descending", title="Year"),
            color=alt.Color(
                "count:Q",
                scale=alt.Scale(scheme="blues"),
                legend=alt.Legend(title=f"{lens_label} count"),
            ),
            tooltip=[
                alt.Tooltip("year:N", title="Year"),
                alt.Tooltip("month_name:N", title="Month"),
                alt.Tooltip("count:Q", title="Count"),
            ],
        )
        .properties(title=f"Seasonality — {lens_label}")
    )


def top_foods_bar(counts, lens_label):
    """Horizontal bar chart of recall counts by category, from count_by() output.

    Sorted by this panel's own counts (`sort="-x"`) rather than a shared
    order across lenses -- the rank shift between event and product lenses
    (e.g. Uncategorized moving from #2 to #4) is itself part of what the
    side-by-side comparison is meant to show.

    Every category present in the input renders as-is, no "Other" bucket --
    category assignment is already known-lossy and due for rework once Phase
    3's LLM labelling pass lands, so a display-only collapsing scheme isn't
    worth building now.
    """
    data = counts.copy()
    data["count"] = data["count"].astype(int)

    # 26px per bar so all 17 category labels have room -- at a tighter fixed
    # height Vega-Lite's default overlap avoidance silently drops every other
    # label, leaving unlabeled bars. labelOverlap=False keeps that avoidance
    # from kicking back in even if a future category list runs longer.
    height = max(320, len(data) * 26)

    return (
        alt.Chart(data)
        .mark_bar(color=BAR_ACCENT)
        .encode(
            y=alt.Y(
                "category:N", sort="-x", title=None,
                axis=alt.Axis(labelOverlap=False),
            ),
            x=alt.X("count:Q", title=f"{lens_label} count"),
            tooltip=[
                alt.Tooltip("category:N", title="Category"),
                alt.Tooltip("count:Q", title="Count"),
            ],
        )
        .properties(title=f"Top recalled foods — {lens_label}", height=height)
    )


def severity_trend_lines(trend, lens_label, partial_through=None):
    """Three-line trend chart (Class I/II/III) from severity_trend() output.

    The final partial year renders as a dashed segment (PRD line 62 / handoff
    decision #9), via two layers rather than one `strokeDash` encoding:
    Vega-Lite groups a line per distinct encoding value, so a single-layer
    approach would draw 2012-2025 as one solid group and leave the partial
    year as an isolated one-point group that draws nothing -- the segment
    would vanish instead of dashing. The dashed layer includes the last
    *complete* year too, so the solid-to-dashed segment actually connects
    instead of leaving a gap.

    `partial_through` is a caption string ("through July 2026") shown as a
    subtitle only when the data actually contains a partial year -- no
    subtitle at all once every year is complete.
    """
    data = trend.copy()
    data["count"] = data["count"].astype(int)
    years = sorted(data["year"].unique().tolist())

    color = alt.Color(
        "classification:N",
        sort=list(SEVERITY_COLORS.keys()),
        scale=alt.Scale(
            domain=list(SEVERITY_COLORS.keys()),
            range=list(SEVERITY_COLORS.values()),
        ),
        legend=alt.Legend(title="Severity"),
    )
    x = alt.X("year:O", title="Year", sort=years, axis=alt.Axis(labelAngle=0))
    tooltip = [
        alt.Tooltip("year:O", title="Year"),
        alt.Tooltip("classification:N", title="Severity"),
        alt.Tooltip("count:Q", title="Count"),
    ]

    partial_years = set(data.loc[data["partial"], "year"])
    if partial_years:
        last_complete = max((y for y in years if y not in partial_years), default=None)
        dashed_years = partial_years | ({last_complete} if last_complete is not None else set())
    else:
        dashed_years = set()

    # The last complete year deliberately appears in *both* layers: the solid
    # layer needs it to draw the 2024->2025 segment, and the dashed layer
    # needs it as the dash's starting point for 2025->2026. Excluding it from
    # solid (an earlier version of this) left a real gap in the line.
    solid = data[~data["year"].isin(partial_years)]
    dashed = data[data["year"].isin(dashed_years)] if dashed_years else data.iloc[0:0]

    layers = []
    if len(solid):
        layers.append(
            alt.Chart(solid).mark_line(point=True).encode(x=x, y="count:Q", color=color, tooltip=tooltip)
        )
    if len(dashed):
        layers.append(
            alt.Chart(dashed)
            .mark_line(point=True, strokeDash=[5, 4])
            .encode(x=x, y="count:Q", color=color, tooltip=tooltip)
        )

    title = f"Trend by severity — {lens_label}"
    title_params = (
        alt.TitleParams(
            title,
            subtitle=f"{min(partial_years)} is a partial year — {partial_through}",
            subtitleFontSize=12,
            subtitleColor="#c3c2b7",
            subtitlePadding=4,
        )
        if partial_years and partial_through
        else title
    )

    return alt.layer(*layers).encode(y=alt.Y("count:Q", title=f"{lens_label} count")).properties(title=title_params)
