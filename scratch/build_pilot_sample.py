"""Throwaway script: build the Step 3 pilot sample.

Not checked in. ~200 proportionally-stratified rows (broad description
variety across the current keyword categories) + ~50 known-answer probes
(unambiguous real rows with a human-assigned expected_category, used as a
sanity floor -- anything less than ~100% on these means the prompt/schema
is broken, not that the taxonomy is hard). Writes scratch/pilot_sample.csv
(columns: recall_number, product_description, expected_category or "").
"""

import re

import pandas as pd

from recall_explorer.pipeline import load_recalls

RNG_SEED = 20260816
STRATIFIED_TARGET = 200

# (regex, expected_category, max rows to take)
PROBE_PATTERNS = [
    (r"\bshell egg", "Eggs", 5),
    (r"\bromaine\b", "Produce", 4),
    (r"\bbottled water\b|\bspring water\b|\bdrinking water\b", "Beverages", 4),
    (r"\bwhole milk\b", "Dairy", 4),
    (r"\bground beef\b", "Beef/Pork/Poultry/Game Meats", 4),
    (r"\bshrimp\b", "Seafood", 4),
    (r"\balmonds\b(?!\s*milk)", "Nuts/Seeds", 4),
    (r"\bpotato chips?\b", "Snacks/Candy", 4),
    (r"\bwhite bread\b", "Bakery", 3),
    (r"\bolive oil\b", "Oils/Fats", 4),
    (r"\bblack beans?\b", "Plant Protein", 4),
    (r"\bwhite rice\b", "Grains/Cereal", 3),
    (r"\bcat food\b|\bdog food\b", "Pet Food/Treats", 4),
    (r"\binfant formula\b", "Baby/Toddler Food", 3),
    (r"\bhoney\b", "Spices/Condiments", 3),
    (r"\bgranulated sugar\b", "Baking Supplies", 3),
    (r"\bround steak\b|\bribeye\b|\bpork chops?\b", "Beef/Pork/Poultry/Game Meats", 3),
]


def build_probes(df):
    used = set()
    rows = []
    for pattern, expected, cap in PROBE_PATTERNS:
        matches = df[df["product_description"].str.contains(pattern, case=False, regex=True, na=False)]
        matches = matches[~matches["recall_number"].isin(used)]
        take = matches.head(cap)
        used.update(take["recall_number"])
        for _, r in take.iterrows():
            rows.append({
                "recall_number": r["recall_number"],
                "product_description": r["product_description"],
                "expected_category": expected,
                "sample_reason": "probe",
            })
    return pd.DataFrame(rows), used


def build_stratified(df, exclude_ids, target_total):
    pool = df[~df["recall_number"].isin(exclude_ids)]
    frac = target_total / len(pool)
    parts = [
        group.sample(frac=frac, random_state=RNG_SEED)
        for _, group in pool.groupby("category")
    ]
    stratified = pd.concat(parts, ignore_index=True)
    out = stratified[["recall_number", "product_description"]].copy()
    out["expected_category"] = ""
    out["sample_reason"] = "stratified"
    return out


def main():
    df = load_recalls()
    probes, used = build_probes(df)
    print(f"Probes: {len(probes)} rows across {len(PROBE_PATTERNS)} patterns")
    print(probes["expected_category"].value_counts())

    stratified = build_stratified(df, used, STRATIFIED_TARGET)
    print(f"\nStratified: {len(stratified)} rows")

    sample = pd.concat([probes, stratified], ignore_index=True)
    sample = sample[["recall_number", "product_description", "expected_category", "sample_reason"]]
    sample.to_csv("scratch/pilot_sample.csv", index=False)
    print(f"\nTotal pilot sample: {len(sample)} rows -> scratch/pilot_sample.csv")


if __name__ == "__main__":
    main()
