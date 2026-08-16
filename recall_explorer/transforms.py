"""Date parsing and the event/product aggregation lenses.

Pure functions over DataFrames -- no file I/O, no Streamlit, no side effects.
"""

import pandas as pd

PRODUCTS = "products"
EVENTS = "events"
LENSES = (EVENTS, PRODUCTS)

# Fixed display/sort order for the severity trend -- Class I is most severe.
# A value outside this set (data drift, an unexpected classification) is
# still appended rather than dropped, so it surfaces instead of vanishing.
SEVERITY_ORDER = ("Class I", "Class II", "Class III")

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


def _validate_lens(lens):
    if lens not in LENSES:
        raise ValueError(f"lens must be one of {LENSES}, got {lens!r}")


def seasonality_matrix(df, lens, coverage_end=None):
    """Long-form (year, month) grid of recall counts, for the seasonality heatmap.

    Returns every (year, month) cell across the full span of years present in
    `df`, not just the months that happen to have data -- a calendar grid with
    holes would be indistinguishable from a coding error.

    `covered` distinguishes two different kinds of blank cell:

      count=0, covered=True   -- a real zero: this month is within the
                                  snapshot's coverage and simply had no
                                  matching recalls.
      count=NA, covered=False -- not yet observed: this month is beyond
                                  `coverage_end` (e.g. next month, which
                                  hasn't happened).

    `coverage_end` is an explicit (year, month) tuple. It exists because the
    caller's date of last observation is not always the last row in `df` --
    reporting lag can leave a covered month with zero rows so far, and a
    filtered subset of `df` can end earlier than the full dataset's true
    coverage. Defaults to the last (year, month) present in `df`.
    """
    _validate_lens(lens)

    if coverage_end is None:
        coverage_end = (int(df["year"].max()), int(df["month"].max()))
    coverage_end_key = coverage_end[0] * 12 + coverage_end[1]

    if lens == EVENTS:
        counted = df.groupby(["year", "month"])["event_id"].nunique()
    else:
        counted = df.groupby(["year", "month"]).size()
    counted = counted.rename("count")

    years = range(int(df["year"].min()), int(df["year"].max()) + 1)
    grid = pd.DataFrame(
        [(year, month) for year in years for month in range(1, 13)],
        columns=["year", "month"],
    )

    grid = grid.merge(counted.reset_index(), on=["year", "month"], how="left")
    grid["covered"] = (grid["year"] * 12 + grid["month"]) <= coverage_end_key
    grid.loc[grid["covered"], "count"] = grid.loc[grid["covered"], "count"].fillna(0)
    grid.loc[~grid["covered"], "count"] = pd.NA

    return grid.sort_values(["year", "month"], ignore_index=True)


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
    _validate_lens(lens)

    if lens == EVENTS:
        counted = df.groupby(dimension)["event_id"].nunique()
    else:
        counted = df.groupby(dimension).size()

    return (
        counted.rename("count")
        .reset_index()
        .sort_values("count", ascending=False, ignore_index=True)
    )


def severity_trend(df, lens, coverage_end=None):
    """Long-form (year, classification, count, partial) grid for the trend chart.

    Every year present in `df` crossed with every classification -- both the
    three expected values in `SEVERITY_ORDER` and any others actually
    observed, so a data-drift value is appended rather than silently
    dropped. Missing (year, classification) combinations are real zeros, not
    holes -- a gap in a line chart would be indistinguishable from a bug.

    `partial` marks a year whose December falls beyond `coverage_end` --
    same (year, month) key arithmetic as `seasonality_matrix()`'s `covered`
    flag, inverted: a year is partial rather than fully observed. Defaults to
    the last (year, month) present in `df`, same as `seasonality_matrix()`.
    """
    _validate_lens(lens)

    if coverage_end is None:
        coverage_end = (int(df["year"].max()), int(df["month"].max()))
    coverage_end_key = coverage_end[0] * 12 + coverage_end[1]

    if lens == EVENTS:
        counted = df.groupby(["year", "classification"])["event_id"].nunique()
    else:
        counted = df.groupby(["year", "classification"]).size()
    counted = counted.rename("count")

    observed_classes = [c for c in df["classification"].unique() if c not in SEVERITY_ORDER]
    classifications = list(SEVERITY_ORDER) + sorted(observed_classes)

    years = range(int(df["year"].min()), int(df["year"].max()) + 1)
    class_order = {c: i for i, c in enumerate(classifications)}
    grid = pd.DataFrame(
        [(year, c) for year in years for c in classifications],
        columns=["year", "classification"],
    )

    grid = grid.merge(counted.reset_index(), on=["year", "classification"], how="left")
    grid["count"] = grid["count"].fillna(0).astype(int)
    grid["partial"] = (grid["year"] * 12 + 12) > coverage_end_key
    grid["_class_order"] = grid["classification"].map(class_order)

    return (
        grid.sort_values(["year", "_class_order"], ignore_index=True)
        .drop(columns="_class_order")
    )
