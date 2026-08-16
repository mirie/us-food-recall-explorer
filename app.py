"""US Food Recall Explorer -- Streamlit entry point.

Reads only the local CSV snapshot (via load_recalls()); no network calls at
runtime. UI glue only -- the actual logic lives in recall_explorer/.
"""

import json
from datetime import datetime
from pathlib import Path

import streamlit as st

from recall_explorer.charts import seasonality_heatmap, severity_trend_lines, top_foods_bar
from recall_explorer.filters import OTHER_REASON, apply_filters, restrict_trend_to_severities
from recall_explorer.insights import key_insights
from recall_explorer.pipeline import load_recalls
from recall_explorer.reasons import REASON_LABELS
from recall_explorer.transforms import SEVERITY_ORDER, count_by, seasonality_matrix, severity_trend

METADATA_PATH = Path(__file__).resolve().parent / "data" / "fetch_metadata.json"


@st.cache_data
def get_data():
    return load_recalls()


@st.cache_data
def get_metadata():
    return json.loads(METADATA_PATH.read_text())


st.set_page_config(page_title="US Food Recall Explorer", layout="wide")

# Key Insights cards use full sentences as their st.metric value, which
# Streamlit's default single-line, ellipsis-truncated metric styling was not
# built for -- override it to wrap instead of cutting the sentence off.
st.markdown(
    """
    <style>
    [data-testid="stMetricValue"],
    [data-testid="stMetricValue"] [data-testid="stMarkdownContainer"],
    [data-testid="stMetricValue"] p {
        font-size: 1.35rem;
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: clip !important;
        overflow-wrap: break-word;
        line-height: 1.3;
        height: auto !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

try:
    df = get_data()
except ValueError as e:
    st.error(str(e))
    st.stop()
metadata = get_metadata()

st.title("US Food Recall Explorer")
st.write(
    "Explores US food recalls from **2012–2026** using openFDA's Food "
    "Enforcement dataset — FDA-regulated food only; meat, poultry, and "
    "processed egg products fall under separate USDA jurisdiction and are "
    "not represented here."
)

fetched_at = datetime.fromisoformat(metadata["fetched_at_utc"])
st.caption(f"Data last updated: {fetched_at:%Y-%m-%d} (snapshot pulled once, not live)")

coverage_year, coverage_month = (
    int(x) for x in metadata["openfda_last_updated"].split("-")[:2]
)

# coverage_end and last_recall_date stay anchored to the full dataset, not the
# filtered subset -- they describe when the snapshot itself was observed, not
# what the user currently has selected.
last_recall_date = df["recall_date"].max()
partial_through = f"through {last_recall_date:%B %Y}"

st.divider()
st.subheader("Key Insights")
st.caption("Event-level, current filter selection.")
# Streamlit renders a container where it was created, not where it is last
# written to -- created here so Key Insights appears above Filters even
# though its numbers depend on filtered_df, computed further down.
key_insights_container = st.container()

st.divider()
st.subheader("Filters")

data_min_year, data_max_year = int(df["year"].min()), int(df["year"].max())


def _reset_filters():
    st.session_state.year_range = (data_min_year, data_max_year)
    st.session_state.category_filter = []
    st.session_state.reason_filter = []
    st.session_state.severity_filter = []


col_year, col_category, col_reason, col_severity = st.columns(4)
with col_year:
    year_range = st.slider(
        "Year range", min_value=data_min_year, max_value=data_max_year,
        value=(data_min_year, data_max_year), key="year_range",
    )
with col_category:
    categories = st.multiselect(
        "Category", sorted(df["category"].unique()), key="category_filter"
    )
with col_reason:
    reasons = st.multiselect("Reason", REASON_LABELS + [OTHER_REASON], key="reason_filter")
with col_severity:
    severities = st.multiselect("Severity", SEVERITY_ORDER, key="severity_filter")

st.button("Reset filters", on_click=_reset_filters, key="reset_filters_button")

filtered_df = apply_filters(
    df, year_range=year_range, categories=categories, reasons=reasons, severities=severities
)

if len(filtered_df) == 0:
    with key_insights_container:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total recall events", "No conclusions")
        col2.metric("Change over time", "No conclusions")
        col3.metric("Peak year", "No conclusions")
        col4.metric("Top reason", "No conclusions")

    st.info("No recalls match the current filters. Try widening the year range or clearing a filter.")
else:
    insights = key_insights(filtered_df, coverage_end=(coverage_year, coverage_month))

    with key_insights_container:
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total recall events", f"{insights.total_events:,} events recorded")

        if insights.pct_change is None:
            col2.metric("Change over time", "N/A")
        else:
            direction = "Up" if insights.pct_change >= 0 else "Down"
            col2.metric(
                "Change over time",
                f"{direction} {abs(insights.pct_change):.1f}% from {insights.first_full_year} to {insights.last_full_year}",
                delta=f"{insights.first_full_year_events:,} → {insights.last_full_year_events:,} events",
                delta_color="off",
            )

        if insights.peak_year is None:
            col3.metric("Peak year", "N/A")
        else:
            col3.metric(
                "Peak year",
                f"{insights.peak_year} was the peak year",
                delta=f"{insights.peak_year_events:,} events",
                delta_color="off",
            )

        if insights.top_reason is None:
            col4.metric("Top reason", "N/A")
        else:
            col4.metric(
                "Top reason",
                f"{insights.top_reason}, most common reason",
                delta=f"{insights.top_reason_share:.1f}% of events",
                delta_color="off",
            )

    st.divider()
    st.subheader("Seasonality")
    st.caption(
        "When recalls happen by month, event-level and product-level side by "
        "side. Each panel uses its own colour scale."
    )

    events_matrix = seasonality_matrix(
        filtered_df, lens="events", coverage_end=(coverage_year, coverage_month)
    )
    products_matrix = seasonality_matrix(
        filtered_df, lens="products", coverage_end=(coverage_year, coverage_month)
    )

    col_events, col_products = st.columns(2)
    with col_events:
        st.altair_chart(
            seasonality_heatmap(events_matrix, lens_label="Events"),
            use_container_width=True,
        )
    with col_products:
        st.altair_chart(
            seasonality_heatmap(products_matrix, lens_label="Products"),
            use_container_width=True,
        )

    st.divider()
    st.subheader("Trend over time")
    st.caption(
        "Recall count by year, split by severity class, event-level and "
        "product-level side by side. Three lines rather than one total, since a "
        "single line hides which severity is driving a given year's shape."
    )

    events_trend = restrict_trend_to_severities(
        severity_trend(filtered_df, lens="events", coverage_end=(coverage_year, coverage_month)),
        severities,
    )
    products_trend = restrict_trend_to_severities(
        severity_trend(filtered_df, lens="products", coverage_end=(coverage_year, coverage_month)),
        severities,
    )

    col_events, col_products = st.columns(2)
    with col_events:
        st.altair_chart(
            severity_trend_lines(events_trend, lens_label="Events", partial_through=partial_through),
            use_container_width=True,
        )
    with col_products:
        st.altair_chart(
            severity_trend_lines(products_trend, lens_label="Products", partial_through=partial_through),
            use_container_width=True,
        )

    st.divider()
    st.subheader("Top recalled foods")
    st.caption(
        "Every category in the current view, event-level and product-level "
        "side by side. Each panel ranks by its own counts, so a category's "
        "rank shifting between panels is itself part of the picture -- a "
        "category can rank high on events yet low on products when it lacks "
        "any single large multi-product recall."
    )

    events_counts = count_by(filtered_df, "category", lens="events")
    products_counts = count_by(filtered_df, "category", lens="products")

    col_events, col_products = st.columns(2)
    with col_events:
        st.altair_chart(
            top_foods_bar(events_counts, lens_label="Events"),
            use_container_width=True,
        )
    with col_products:
        st.altair_chart(
            top_foods_bar(products_counts, lens_label="Products"),
            use_container_width=True,
        )

st.divider()
with st.expander("About the data & limitations"):
    st.markdown(
        """
- **openFDA covers FDA-regulated food only.** Meat and poultry are USDA FSIS
  jurisdiction and are absent from this dataset — which is why the meat
  categories are near-empty. Shell eggs, however, are FDA-regulated and appear
  under their own `Eggs` category. Near-empty meat is a property of the data
  source, not evidence that meat is rarely recalled.
- **Category comes from an LLM classification pass** (Claude Opus 5, full
  29,159-row dataset) that replaced an earlier keyword-based approach. Only
  0.72% of rows are `Uncategorized`, down from the keyword pass's 12.2%. A
  self-consistency check (an independent second pass over 1,000 rows) found
  96.1% agreement, with zero disagreements among high-confidence labels — see
  `CLASSIFICATION_RULES.md` and `BUILD_LOG.md` for the full validation.
- **Reason tags are multi-label.** Any reported share is "of recalls
  mentioning X," never "share of all recalls."
- **Recall counts are not a food-safety measure.** Changes over time may
  reflect shifts in detection and reporting practice rather than in the
  safety of the food supply.
- **No country of origin exists in this data.** The `country`/`state` fields
  record the recalling firm's address, not where the food was grown or
  produced.
- **The dataset begins in 2012.** That is a data-availability boundary in
  openFDA's records, not evidence that recalls began then.
- **Every relevant chart shows two lenses side by side: event-level and
  product-level.** A single multi-product recall counts once at the event
  level but can span many rows at the product level (roughly 3.7x on
  average) — both are shown together so neither view is mistaken for the
  whole picture.
- **Charts have no built-in screen-reader-accessible data table
  fallback.** This is a Vega-Lite/Altair (via `st.altair_chart`) platform
  constraint in the current stack, not something addressed in this build.
        """
    )
