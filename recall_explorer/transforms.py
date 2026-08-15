"""Date parsing and the event/product aggregation lenses.

Pure functions over DataFrames -- no file I/O, no Streamlit, no side effects.
"""

import pandas as pd

PRODUCTS = "products"
EVENTS = "events"
LENSES = (EVENTS, PRODUCTS)

# Plausibility window for a recall date. openFDA's enforcement reports begin in
# 2012; anything outside this range is a data-entry artifact, not a real recall.
MIN_PLAUSIBLE_YEAR = 2000
MAX_PLAUSIBLE_YEAR = 2100


def parse_recall_dates(df):
    """Parse recall_initiation_date and derive `recall_date`, `year`, `month`.

    Bad dates become NaT rather than raising -- one bad row must not fail the
    whole load.

    The plausibility window is doing real work here, not defensive padding.
    openFDA contains the value "02121207", which `errors="coerce"` does NOT
    catch: it parses cleanly as 7 December, year 212. Under pandas 2.x that
    fell outside datetime64[ns]'s 1677 floor and coerced to NaT for free; under
    pandas 3.0's datetime64[us] it survives as a real Timestamp and would drag
    a trend chart's x-axis back eighteen centuries. So the range check is
    explicit rather than inherited from the dtype.
    """
    out = df.copy()
    out["recall_date"] = pd.to_datetime(
        out["recall_initiation_date"], format="%Y%m%d", errors="coerce"
    )
    implausible = (
        (out["recall_date"].dt.year < MIN_PLAUSIBLE_YEAR)
        | (out["recall_date"].dt.year > MAX_PLAUSIBLE_YEAR)
    )
    out.loc[implausible, "recall_date"] = pd.NaT
    out["year"] = out["recall_date"].dt.year
    out["month"] = out["recall_date"].dt.month
    return out


def count_by(df, dimension, lens):
    """Count recalls grouped by `dimension`, under one of the two lenses.

    The distinction is the app's central idea, not an implementation detail:

      products -- one row per recalled item. A single recall covering 400 SKUs
                  contributes 400. Answers "how much product was affected?"
      events   -- one count per distinct recall incident, however many products
                  it covered. Answers "how often do recalls happen?"

    On this dataset the lenses differ by ~3.7x overall, and by far more inside
    categories dominated by a few very large recalls -- which is exactly why
    both are always shown rather than one being chosen.

    Returns a DataFrame of [dimension, count], descending by count.
    """
    if lens not in LENSES:
        raise ValueError(f"lens must be one of {LENSES}, got {lens!r}")

    if lens == EVENTS:
        counted = df.groupby(dimension)["event_id"].nunique()
    else:
        counted = df.groupby(dimension).size()

    return (
        counted.rename("count")
        .reset_index()
        .sort_values("count", ascending=False, ignore_index=True)
    )
