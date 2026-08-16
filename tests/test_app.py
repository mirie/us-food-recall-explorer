"""AppTest-driven checks for app.py's UI glue.

Runs the real app against the real derived CSV (no mocking -- same
philosophy as test_pipeline.py) using Streamlit's headless AppTest
harness, so widget interactions are exercised without a browser.
"""

from pathlib import Path

from streamlit.testing.v1 import AppTest

APP_PATH = Path(__file__).resolve().parent.parent / "app.py"


def _run():
    return AppTest.from_file(str(APP_PATH)).run(timeout=30)


def test_reset_filters_button_exists():
    at = _run()
    assert at.exception == []
    labels = [b.label for b in at.button]
    assert "Reset filters" in labels


def test_reset_filters_clears_every_filter_back_to_defaults():
    at = _run()
    baseline_total = at.metric[0].value

    at.multiselect(key="category_filter").select("Eggs").run()
    at.multiselect(key="reason_filter").select("Salmonella").run()
    at.multiselect(key="severity_filter").select("Class I").run()
    at.slider(key="year_range").set_range(2015, 2018).run()

    # Sanity check the filters actually took effect before resetting.
    assert at.metric[0].value != baseline_total

    at.button(key="reset_filters_button").click().run()

    assert at.multiselect(key="category_filter").value == []
    assert at.multiselect(key="reason_filter").value == []
    assert at.multiselect(key="severity_filter").value == []
    assert at.slider(key="year_range").value == (2012, 2026)
    assert at.metric[0].value == baseline_total
