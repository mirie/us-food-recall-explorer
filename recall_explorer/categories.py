"""Derive a food category from openFDA's free-text product_description.

openFDA has no category field. `product_description` is free prose written by
the recalling firm, so category has to be inferred from keywords -- and the
inference is genuinely lossy. Measured on the full 29,161-row snapshot:
19.8% of descriptions match no category keyword at all, and 35.4% match two
or more (one matches ten).

Almost all of the multi-match noise comes from *ingredient* words being read
as *product type* words. "milk", "butter", "cream", and "nut" appear in
thousands of products that are not dairy or nut products -- a chocolate chip
cookie matches Dairy, Bakery, and Snacks simultaneously.

CATEGORY_RULES is therefore ordered specific-beats-generic, and the order is
the whole design: the first pattern to match wins. Narrow categories whose
keywords name a product outright (Supplements, Seafood, Beef) sit at the top.
Broad categories whose keywords double as ingredients (Dairy, Nuts/Seeds,
Spices/Condiments) sit at the bottom, so they only claim a row when nothing
more specific did.

Known limitation, accepted deliberately: this misfires on products whose
identity *is* the ingredient. "Ice cream sandwich" resolves to Bakery, not
Dairy. Surfaced in the app's "About the data" section rather than hidden.
"""

import re

UNCATEGORIZED = "Uncategorized"

# Order is load-bearing -- first match wins. See module docstring.
CATEGORY_RULES = [
    # Narrow and unambiguous: these words name a product, not an ingredient.
    ("Supplements", r"supplement|vitamin|capsule|softgel|dietary|herbal|"
                    r"kratom|infant formula|probiotic|protein powder"),
    ("Seafood", r"fish|salmon|tuna|shrimp|oyster|clam|crab|lobster|scallop|"
                r"seafood|tilapia|anchov|squid|mussel|cod fillet|sardine"),
    ("Beef", r"\bbeef\b|steak|hamburger|\bveal\b|brisket"),
    ("Pork", r"\bpork\b|bacon|\bham\b|sausage|salami|prosciutto|mortadella|chorizo"),
    ("Poultry/Eggs", r"chicken|turkey|poultry|\begg\b|\beggs\b|\bduck\b"),

    # Product-form categories: these beat ingredient words below them.
    ("Bakery", r"bread|cake|cookie|pastr|muffin|bakery|donut|doughnut|brownie|"
               r"cracker|tortilla|bagel|macaron|\bpie\b|biscuit|croissant"),
    ("Prepared/Frozen", r"frozen|entree|burrito|pizza|soup|sandwich|sushi|"
                        r"noodle|pasta|lasagna|\bwrap\b|casserole"),
    ("Beverages", r"juice|beverage|soda|\btea\b|coffee|smoothie|kombucha|"
                  r"drink|water\b"),
    ("Snacks/Candy", r"candy|chocolate|chip|snack|popcorn|pretzel|granola|"
                     r"fudge|gummy|caramel"),

    # Broad, and their keywords double as ingredients -- last resort only.
    ("Produce", r"lettuce|spinach|salad|romaine|cucumber|tomato|onion|melon|"
                r"cantaloupe|berr|apple|peach|mango|sprout|carrot|celery|"
                r"avocado|papaya|broccoli|cauliflower|potato|squash|kale|"
                r"cilantro|parsley|fruit|vegetable"),
    ("Dairy", r"milk|cheese|yogurt|butter|cream|dairy|queso|brie"),
    ("Nuts/Seeds", r"peanut|almond|cashew|walnut|pecan|pistachio|\bnuts?\b|"
                   r"sesame|chia|flax"),
    ("Spices/Condiments", r"spice|season|sauce|dressing|salsa|hummus|mustard|"
                          r"mayonnais|ketchup|syrup|honey|vinegar"),
]


def assign_category(description):
    """Return the first matching category, or UNCATEGORIZED if none match."""
    text = (description or "").lower()
    for category, pattern in CATEGORY_RULES:
        if re.search(pattern, text):
            return category
    return UNCATEGORIZED
