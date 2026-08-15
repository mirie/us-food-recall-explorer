"""Altair chart builders.

Pure functions from shaped data (transforms.py output) to alt.Chart objects --
no Streamlit calls, no file I/O.
"""

import altair as alt

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


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
