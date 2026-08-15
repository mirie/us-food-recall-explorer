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
    # Tier 1 -- narrow, and these words genuinely name a product here.
    ("Supplements", r"supplement|vitamin|capsule|softgel|dietary|herbal|"
                    r"kratom|infant formula|probiotic|protein powder"),
    ("Seafood", r"fish|salmon|tuna|shrimp|oyster|clam|crab|lobster|scallop|"
                r"seafood|tilapia|anchov|squid|mussel|cod fillet|sardine|"
                r"herring|mackerel|caviar|octopus|calamari|pollock"),

    # Tier 2 -- product form. What the item *is*, which beats what it contains.
    ("Bakery", r"bread|cake|cookie|pastr|muffin|bakery|donut|doughnut|brownie|"
               r"cracker|tortilla|bagel|macaron|\bpies?\b|biscuit|croissant"),
    ("Prepared/Frozen", r"frozen|entree|burrito|pizza|soup|sandwich|sushi|"
                        r"noodle|pasta|lasagna|\bwrap\b|casserole|mac &|"
                        r"macaroni|dumpling|ravioli|\btaco\b|meal kit|"
                        r"slider|nugget|\bpatt(y|ies)\b"),
    ("Grains/Cereal", r"cereal|grits|\boats?\b|granola|flour|\brice\b|quinoa|"
                      r"wheat|barley|cornmeal|corn meal|couscous|\bbran\b|"
                      r"\bgrain\b|muesli"),
    ("Beverages", r"juice|beverage|soda|\btea\b|coffee|smoothie|kombucha|"
                  r"drink|water\b|kool-aid|lemonade|cider|nectar|cocoa|"
                  r"latte|espresso"),
    ("Snacks/Candy", r"candy|chocolate|chip|snack|popcorn|pretzel|granola|"
                     r"fudge|gummy|caramel|brittle|ganache|truffle|toffee|"
                     r"marshmallow|wafer|nougat|licorice"),
    ("Plant Protein", r"tofu|tempeh|seitan|plant based|plant-based|"
                      r"meat alternative|veggie burger"),

    # Tier 3 -- keywords that double as ingredients. Last resort only.
    #
    # Meat sits here, not in tier 1, and the reason is jurisdictional: FDA does
    # not regulate meat, poultry, or processed egg products. USDA FSIS does, in
    # a separate dataset. So a meat word in THIS corpus is almost always a
    # flavouring or ingredient inside an FDA-regulated processed food --
    # "Natural Beef Flavor", "Bacon Brittle", "Chicken Flavor Seasoning". These
    # categories are kept so genuine FDA-jurisdiction items still land
    # somewhere, but they must not outrank product form.
    # \bapple matters: without the boundary it also matches "pineapple".
    ("Produce", r"lettuce|spinach|salad|romaine|cucumber|tomato|onion|melon|"
                r"cantaloupe|berr|\bapples?\b|peach|mango|sprout|carrot|"
                r"celery|avocado|papaya|broccoli|cauliflower|potato|squash|"
                r"kale|cilantro|parsley|fruit|vegetable|mushroom|garlic|"
                r"ginger|cabbage|\bbeets?\b|radish|asparagus|\bpeas?\b|"
                r"\blimes?\b|\blemons?\b|banana|\bpears?\b|cherr|grape"),
    ("Dairy", r"milk|cheese|yogurt|butter|cream|dairy|queso|brie|gelato|"
              r"sorbet|custard|kefir|\bwhey\b"),
    ("Nuts/Seeds", r"peanut|almond|cashew|walnut|pecan|pistachio|\bnuts?\b|"
                   r"sesame|chia|flax|kernel|sunflower|hazelnut|macadamia|"
                   r"coconut|tahini|pumpkin seed"),
    ("Spices/Condiments", r"spice|season|sauce|dressing|salsa|hummus|mustard|"
                          r"mayonnais|ketchup|syrup|honey|vinegar|flavor|"
                          r"thyme|cardamom|za'?atar|cumin|turmeric|paprika|"
                          r"oregano|basil|curry|\bherbs?\b|\bdips?\b|spread"),
    # Tier 3 as well: "packed in oil" is an ingredient, not a product form.
    ("Oils/Fats", r"\boils?\b|shortening|margarine|\blard\b|\bghee\b"),
    ("Beef", r"\bbeef\b|steak|hamburger|\bveal\b|brisket"),
    ("Pork", r"\bpork\b|bacon|\bham\b|sausage|salami|prosciutto|mortadella|chorizo"),
    ("Poultry/Eggs", r"chicken|turkey|poultry|\begg\b|\beggs\b|\bduck\b"),
]


def assign_category(description):
    """Return the first matching category, or UNCATEGORIZED if none match."""
    text = (description or "").lower()
    for category, pattern in CATEGORY_RULES:
        if re.search(pattern, text):
            return category
    return UNCATEGORIZED
