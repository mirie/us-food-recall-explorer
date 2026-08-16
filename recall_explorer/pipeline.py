"""Load the static snapshot and apply every derivation the app depends on.

The one place that touches the filesystem. Everything it calls is a pure
function, so the interesting logic stays unit-testable without file I/O.

This module makes no network calls. The snapshot is built once by
fetch_data.py, run manually and outside the app.
"""

from pathlib import Path

import pandas as pd

from recall_explorer.categories import assign_category
from recall_explorer.reasons import tag_reasons
from recall_explorer.schema import validate_schema
from recall_explorer.transforms import parse_recall_dates

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "food_recalls.csv"

# openFDA's enforcement reports begin in 2012. Rows outside the window are
# back-filled stragglers too sparse to chart honestly -- see BUILD_LOG Entry 1.
START_YEAR = 2012


def load_recalls(path=None):
    """Return the analysis-ready DataFrame: load -> validate -> clean -> derive.

    Raises ValueError with an actionable message if the snapshot is missing or
    has drifted from its expected shape, rather than proceeding to render
    charts from data that no longer matches what the app was built against.
    """
    path = Path(path) if path is not None else DATA_PATH
    if not path.exists():
        raise ValueError(
            f"Data snapshot not found at {path}. "
            f"Run `python fetch_data.py` to build it."
        )

    df = pd.read_csv(path, dtype=str)
    validate_schema(df)

    # Two rows in the 2026-08 snapshot carry a blank recall_number (event_ids
    # 99068, 99205) -- an openFDA data gap, not something fetch_data.py can
    # recover. recall_number is the product-level key the whole app keys off
    # of, so these two are incomplete records, excluded rather than kept with
    # a missing identity. See BUILD_LOG.md's Phase 5 Step 2 entry.
    df = df[df["recall_number"].notna() & (df["recall_number"].str.strip() != "")].copy()

    df = parse_recall_dates(df)
    df = df[df["recall_date"].notna() & (df["year"] >= START_YEAR)].copy()

    df["year"] = df["year"].astype(int)
    df["month"] = df["month"].astype(int)
    df["category"] = df["product_description"].map(assign_category)
    df["reason_tags"] = df["reason_for_recall"].map(tag_reasons)

    return df.reset_index(drop=True)
