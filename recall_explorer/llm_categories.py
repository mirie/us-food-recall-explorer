"""Manual LLM category-labelling round trip -- no API calls from this module.

Historical note: the original (Phase 3) version of this module supported a
manual round trip through a separate Claude.ai chat, covering only the
~12% `Uncategorized` residual keyword rules couldn't label. Phase 5 replaced
that scope with a full-dataset reclassification under the taxonomy in
CLASSIFICATION_RULES.md (see classify_all.py). This module's functions
(export_for_classification, build_classification_prompt,
parse_classification_result) remain as-is, covering the historical manual
round trip; CATEGORY_ENUM below now reflects the Phase 5 taxonomy instead of
categories.py's keyword rules.
"""

import csv
import io

from recall_explorer.categories import UNCATEGORIZED

# The approved Phase 5 taxonomy -- must match CLASSIFICATION_RULES.md's
# "## 1. Label set" section exactly (see test_llm_categories.py's sync test).
CATEGORY_ENUM = [
    "Dairy",
    "Eggs",
    "Beef/Pork/Poultry/Game Meats",
    "Seafood",
    "Produce",
    "Plant Protein",
    "Grains/Cereal",
    "Bakery",
    "Prepared/Frozen",
    "Snacks/Candy",
    "Nuts/Seeds",
    "Beverages",
    "Spices/Condiments",
    "Oils/Fats",
    "Supplements",
    "Baking Supplies",
    "Food Additives/Ingredients",
    "Non-Food Item",
    "Baby/Toddler Food",
    "Pet Food/Treats",
    "Uncategorized",
]


def export_for_classification(df):
    """Return (recall_number, product_description) for rows still Uncategorized."""
    subset = df[df["category"] == UNCATEGORIZED][["recall_number", "product_description"]]
    return subset.reset_index(drop=True)


def build_classification_prompt():
    """Ready-to-paste instructions for the separate Claude.ai classification chat."""
    categories_list = "\n".join(f"- {c}" for c in CATEGORY_ENUM)
    return f"""You will classify US food recall product descriptions into exactly one
category each, from this fixed list (use these labels verbatim, nothing else):

{categories_list}

Two worked examples of genuinely ambiguous cases, to calibrate:
- "Blue Bell coconut fudge" -> pick the single best-fitting category (it could
  read as Dairy, Snacks/Candy, or Nuts/Seeds -- pick what the product most
  fundamentally IS, not every ingredient it contains).
- "a89471 batter mix x1" (a bare SKU/code with little food-identifying text)
  -> Uncategorized, if nothing in the description reliably indicates a category.

Rules:
- Every row in the attached CSV must appear exactly once in your output.
- Output ONLY a CSV with header `recall_number,category`, one line per input
  row, in any order -- no commentary, no markdown fences, no extra columns.
- `category` must be exactly one of the labels listed above (case-sensitive).
- When genuinely unsure, use Uncategorized rather than guessing.
"""


def _looks_like_header(row):
    return len(row) >= 2 and row[0].strip().lower() == "recall_number"


def parse_classification_result(raw_text, expected_recall_numbers):
    """Parse pasted-back CSV text into a validated recall_number -> category mapping.

    Returns (mapping, problems). Invalid categories are dropped, not coerced.
    `problems` collects every issue found (bad category, missing expected row,
    unexpected extra row) so a partial or bad paste is caught before merging.
    """
    problems = []
    mapping = {}
    seen = set()

    reader = csv.reader(io.StringIO(raw_text))
    rows = [row for row in reader if row and any(cell.strip() for cell in row)]
    if rows and _looks_like_header(rows[0]):
        rows = rows[1:]

    valid_categories = set(CATEGORY_ENUM)
    for row in rows:
        if len(row) < 2:
            continue
        recall_number, category = row[0].strip(), row[1].strip()
        if not recall_number:
            continue
        seen.add(recall_number)
        if category not in valid_categories:
            problems.append(f"{recall_number}: invalid category {category!r}, dropped")
            continue
        if recall_number not in expected_recall_numbers:
            problems.append(f"{recall_number}: not in the expected set, dropped")
            continue
        mapping[recall_number] = category

    missing = expected_recall_numbers - seen
    for recall_number in sorted(missing):
        problems.append(f"{recall_number}: expected but missing from the response")

    return mapping, problems
