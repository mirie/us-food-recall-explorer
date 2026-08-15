"""Smoke test for chart-building functions, against real pipeline output.

Per the testing contract: one "renders without crashing" check per chart,
using real data. No assertions on rendered output -- no SVG, no colours,
no pixel diffs. Trust the chart library; test that it accepts our data.
"""

import pytest

from recall_explorer.charts import seasonality_heatmap
from recall_explorer.pipeline import load_recalls
from recall_explorer.transforms import seasonality_matrix


@pytest.mark.pipeline
def test_seasonality_heatmap_builds_from_real_pipeline_output():
    df = load_recalls()
    matrix = seasonality_matrix(df, lens="events")
    chart = seasonality_heatmap(matrix, lens_label="Events")
    chart.to_dict()
