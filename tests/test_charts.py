"""Smoke test for chart-building functions, against real pipeline output.

Per the testing contract: one "renders without crashing" check per chart,
using real data. No assertions on rendered output -- no SVG, no colours,
no pixel diffs. Trust the chart library; test that it accepts our data.
"""

import pytest

from recall_explorer.charts import seasonality_heatmap, severity_trend_lines, top_foods_bar
from recall_explorer.pipeline import load_recalls
from recall_explorer.transforms import count_by, seasonality_matrix, severity_trend


@pytest.mark.pipeline
def test_seasonality_heatmap_builds_from_real_pipeline_output():
    df = load_recalls()
    matrix = seasonality_matrix(df, lens="events")
    chart = seasonality_heatmap(matrix, lens_label="Events")
    chart.to_dict()


@pytest.mark.pipeline
def test_top_foods_bar_builds_from_real_pipeline_output():
    df = load_recalls()
    counts = count_by(df, "category", lens="events")
    chart = top_foods_bar(counts, lens_label="Events")
    chart.to_dict()


@pytest.mark.pipeline
def test_severity_trend_lines_builds_from_real_pipeline_output():
    df = load_recalls()
    trend = severity_trend(df, lens="events")
    chart = severity_trend_lines(trend, lens_label="Events", partial_through="through July 2026")
    chart.to_dict()
