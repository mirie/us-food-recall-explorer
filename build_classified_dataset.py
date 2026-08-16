"""One-time join of the raw snapshot with the Phase 5 LLM classification.

Run manually, after fetch_data.py and after data/recall_categories_llm_full.csv
is finalized. Writes data/food_recalls_classified.csv: the 19 raw columns from
data/food_recalls.csv, in order, plus llm_category. data/food_recalls.csv
itself is never modified -- it stays the untouched raw snapshot.

confidence is deliberately not merged in. It stays in
data/recall_categories_llm_full.csv as a review artifact; the app never reads it.

    python build_classified_dataset.py
"""

import sys
from pathlib import Path

import pandas as pd

from recall_explorer.schema import EXPECTED_COLUMNS

DATA_DIR = Path(__file__).resolve().parent / "data"
RAW_PATH = DATA_DIR / "food_recalls.csv"
CATEGORIES_PATH = DATA_DIR / "recall_categories_llm_full.csv"
OUT_PATH = DATA_DIR / "food_recalls_classified.csv"


def main():
    raw = pd.read_csv(RAW_PATH, dtype=str)
    categories = pd.read_csv(CATEGORIES_PATH, dtype=str)[["recall_number", "category"]]
    categories = categories.rename(columns={"category": "llm_category"})

    merged = raw.merge(categories, on="recall_number", how="left")
    merged = merged[EXPECTED_COLUMNS + ["llm_category"]]

    missing = merged["llm_category"].isna().sum()
    print(f"{len(merged):,} rows written; {missing:,} without an llm_category.")

    merged.to_csv(OUT_PATH, index=False)
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    sys.exit(main())
