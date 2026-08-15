"""US Food Recall Explorer -- Streamlit entry point.

Reads only the local CSV snapshot (via load_recalls()); no network calls at
runtime. UI glue only -- the actual logic lives in recall_explorer/.
"""

import json
from datetime import datetime
from pathlib import Path

import streamlit as st

from recall_explorer.charts import seasonality_heatmap
from recall_explorer.pipeline import load_recalls
from recall_explorer.transforms import seasonality_matrix

METADATA_PATH = Path(__file__).resolve().parent / "data" / "fetch_metadata.json"


@st.cache_data
def get_data():
    return load_recalls()


@st.cache_data
def get_metadata():
    return json.loads(METADATA_PATH.read_text())


st.set_page_config(page_title="US Food Recall Explorer", layout="wide")

df = get_data()
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

st.divider()
st.subheader("Key Insights")
st.info("Coming in Phase 3: 4 computed stat cards, event-level framed.")

st.divider()
st.subheader("Seasonality")
st.caption(
    "When recalls happen by month, event-level and product-level side by "
    "side. Each panel uses its own colour scale."
)

coverage_year, coverage_month = (
    int(x) for x in metadata["openfda_last_updated"].split("-")[:2]
)

events_matrix = seasonality_matrix(
    df, lens="events", coverage_end=(coverage_year, coverage_month)
)
products_matrix = seasonality_matrix(
    df, lens="products", coverage_end=(coverage_year, coverage_month)
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
st.info("Coming next: line chart of volume/severity by year, both lenses.")

st.divider()
st.subheader("Top recalled foods")
st.info("Coming next: horizontal bar chart by category, both lenses.")

st.divider()
with st.expander("About the data & limitations"):
    st.markdown(
        """
- **openFDA covers FDA-regulated food only.** Meat, poultry, and processed
  egg products are USDA FSIS jurisdiction and are absent from this dataset —
  which is why the meat categories are near-empty. This is a property of the
  data source, not evidence that meat is rarely recalled.
- **Category is keyword-derived and lossy.** About 12% of rows are
  `Uncategorized`, which is a measure of coverage, not correctness — accuracy
  on the labeled ~88% has never been independently measured.
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
        """
    )
