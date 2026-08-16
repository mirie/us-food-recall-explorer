"""Throwaway script: build the ~5,000-row design sample for Phase 5 Step 1.

Not checked in. Run once, inspect scratch/design_sample.csv, then feed it to
the taxonomy-finalization API call.
"""

import re

import pandas as pd

from recall_explorer.pipeline import load_recalls

RNG_SEED = 20260816

EXHAUSTIVE_CATEGORIES = ["Poultry/Eggs", "Pork", "Beef", "Plant Protein", "Oils/Fats"]

COVERAGE_HOLE_PATTERNS = {
    "alcohol": r"\bbeer\b|\bwine\b|\bspirits?\b|\bcider\b|\bvodka\b|\bwhiskey\b|"
    r"\bwhisky\b|\brum\b|\bgin\b|\btequila\b|\bbrandy\b|\bliqueur\b|\bmead\b|"
    r"\bseltzer\b.*alcohol|hard seltzer|hard cider|malt beverage",
    "coffee_creamer": r"coffee creamer|creamer\b",
    "broth": r"\bbroth\b|\bstock\b|bouillon",
    "baby_food": r"baby food|infant puree|\bpuree\b.*baby|baby.*puree",
    "honey": r"\bhoney\b",
    "agave_stevia_molasses": r"\bagave\b|\bstevia\b|\bmolasses\b",
}

TARGET_TOTAL = 5000


def main():
    df = load_recalls()
    print(f"total rows: {len(df)}")

    exhaustive = df[df["category"].isin(EXHAUSTIVE_CATEGORIES)].copy()
    exhaustive["sample_reason"] = "exhaustive:" + exhaustive["category"]
    print(f"exhaustive slice: {len(exhaustive)} rows")

    pool = df[
        ~df["category"].isin(EXHAUSTIVE_CATEGORIES + ["Uncategorized"])
    ].copy()
    print(f"stratification pool (before coverage-hole pull): {len(pool)} rows")

    remaining_pool = pool.copy()
    coverage_frames = []
    for name, pattern in COVERAGE_HOLE_PATTERNS.items():
        regex = re.compile(pattern, re.IGNORECASE)
        mask = remaining_pool["product_description"].fillna("").str.contains(regex)
        hit = remaining_pool[mask].copy()
        hit["sample_reason"] = f"coverage_hole:{name}"
        coverage_frames.append(hit)
        remaining_pool = remaining_pool[~mask]
        print(f"coverage hole '{name}': {len(hit)} rows pulled")

    coverage_sample = pd.concat(coverage_frames, ignore_index=True)
    print(f"total coverage-hole rows: {len(coverage_sample)}")

    budget_for_stratified = TARGET_TOTAL - len(exhaustive) - len(coverage_sample)
    print(f"remaining budget for plain stratified sample: {budget_for_stratified}")

    frac = budget_for_stratified / len(remaining_pool)
    parts = [
        group.sample(frac=frac, random_state=RNG_SEED)
        for _, group in remaining_pool.groupby("category")
    ]
    stratified = pd.concat(parts, ignore_index=True)
    stratified["sample_reason"] = "stratified:" + stratified["category"]
    print(f"stratified sample: {len(stratified)} rows")

    sample = pd.concat([exhaustive, coverage_sample, stratified], ignore_index=True)
    sample = sample.drop_duplicates(subset="recall_number")
    print(f"final sample size: {len(sample)}")
    print(sample["category"].value_counts())
    print("---sample_reason breakdown (top 20)---")
    print(sample["sample_reason"].value_counts().head(20))

    out_cols = ["recall_number", "product_description", "category", "sample_reason"]
    sample[out_cols].to_csv("scratch/design_sample.csv", index=False)
    print("wrote scratch/design_sample.csv")


if __name__ == "__main__":
    main()
