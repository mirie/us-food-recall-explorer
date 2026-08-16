"""Manually re-verified known-answer probes, replacing the naive regex-built
labels in pilot_sample.csv. Each entry checked by reading the FULL
product_description against CLASSIFICATION_RULES.md's actual rules, not
guessed from a keyword match.

Dropped from the original 58 (genuinely ambiguous, not fit for a "known
answer" floor test):
  F-1527-2022  a 40-item multi-product recall notice, not one product
  F-2107-2012  "Black Bean Soup" -- cooked-bean-dish rule vs. soup-is-
               Prepared/Frozen rule genuinely conflict; the doc doesn't
               resolve this
  F-1874-2012  "FC BLACK BEAN/CORN SALSA" -- description is truncated in
               the source data; too little to be sure

Corrected (regex matched a keyword that wasn't actually the product):
  F-2292-2012  Supplements, not Dairy (meal-replacement shake; "whole milk"
               only appears in its list of EXCLUDED ingredients)
  F-1753-2012  Bakery, not Dairy (finished cookies; milk is an ingredient)
  F-1622-2013  Plant Protein, not meat ("Ground Beef Style" plant mix)
  F-1274-2019  Plant Protein, not meat (Impossible plant product)
  F-0841-2013  Spices/Condiments, not Seafood (a bouillon-style base)
  F-0684-2013  Prepared/Frozen, not Seafood (a composite "Meal...Stir Fry")
  F-1476-2013  Bakery, not Nuts/Seeds (a danish pastry; almonds are garnish)
  F-0676-2013  Prepared/Frozen, not Bakery (a PB&J sandwich, not loaf bread)
  F-0660-2013  Prepared/Frozen, not Bakery (same, different filling)
  F-0781-2013  Bakery, not Oils/Fats (a cake; olive oil is an ingredient)
  F-1930-2012  Seafood, not Oils/Fats (conch salad; olive oil is in a sauce)
  F-2140-2012  Spices/Condiments, not Oils/Fats (a dressing)
  F-1427-2012  Seafood, not Oils/Fats (oysters packed IN olive oil --
               packing medium never governs, per the doc's own example)
  F-0303-2013  Nuts/Seeds, not Spices/Condiments (peanut butter; honey is
               a flavor modifier, not the product)
  F-0032-2013  Produce, not Spices/Condiments (a melon mix; regex matched
               "honey" inside "Honeydew", not honey itself)
  F-0632-2013  Prepared/Frozen, not Spices/Condiments (a composite meal box)
  F-1514-2013  Bakery, not Baking Supplies (a cookie MIX -- the doc's own
               rule: mixes for a specific baked good are Bakery)
  F-1600-2014  Bakery, not Baking Supplies (finished donuts)
  F-0588-2020  Seafood, not meat (frozen tuna; regex false-matched "round"
               in "Tuna Round Steak" against the meat-cut pattern)
  F-1577-2022  Prepared/Frozen, not meat (a composite "meal...Bowl")

Confirmed correct as originally labeled: everything else (38 rows).
"""

CORRECTED_EXPECTED = {
    "F-0023-2015": "Eggs",
    "F-0147-2017": "Eggs",
    "F-1410-2018": "Eggs",
    "H-0210-2025": "Eggs",
    "F-1626-2012": "Produce",
    "F-1618-2012": "Produce",
    "F-1606-2012": "Produce",
    "F-1614-2012": "Produce",
    "F-2320-2014": "Beverages",
    "F-2319-2014": "Beverages",
    "F-1949-2014": "Beverages",
    "F-2772-2015": "Beverages",
    "F-2292-2012": "Supplements",
    "F-1753-2012": "Bakery",
    "F-2113-2012": "Dairy",
    "F-1717-2014": "Dairy",
    "F-1622-2013": "Plant Protein",
    "F-1274-2019": "Plant Protein",
    "F-2151-2012": "Seafood",
    "F-0841-2013": "Spices/Condiments",
    "F-0684-2013": "Prepared/Frozen",
    "F-1801-2012": "Seafood",
    "F-0398-2013": "Nuts/Seeds",
    "F-0559-2013": "Nuts/Seeds",
    "F-1378-2014": "Nuts/Seeds",
    "F-1476-2013": "Bakery",
    "F-1786-2012": "Snacks/Candy",
    "F-1787-2012": "Snacks/Candy",
    "F-1788-2012": "Snacks/Candy",
    "F-1789-2012": "Snacks/Candy",
    "F-0676-2013": "Prepared/Frozen",
    "F-1403-2012": "Bakery",
    "F-0660-2013": "Prepared/Frozen",
    "F-0781-2013": "Bakery",
    "F-1930-2012": "Seafood",
    "F-2140-2012": "Spices/Condiments",
    "F-1427-2012": "Seafood",
    "F-2073-2012": "Plant Protein",
    "F-2117-2012": "Plant Protein",
    "F-1686-2014": "Grains/Cereal",
    "F-0090-2015": "Grains/Cereal",
    "F-1260-2016": "Grains/Cereal",
    "F-1753-2019": "Pet Food/Treats",
    "F-1754-2019": "Pet Food/Treats",
    "F-1409-2015": "Baby/Toddler Food",
    "F-1558-2019": "Baby/Toddler Food",
    "F-0022-2020": "Baby/Toddler Food",
    "F-0303-2013": "Nuts/Seeds",
    "F-0032-2013": "Produce",
    "F-0632-2013": "Prepared/Frozen",
    "F-1581-2013": "Baking Supplies",
    "F-1514-2013": "Bakery",
    "F-1600-2014": "Bakery",
    "F-0588-2020": "Seafood",
    "F-1577-2022": "Prepared/Frozen",
}
# Dropped as too ambiguous for a known-answer floor test:
#   F-1527-2022, F-2107-2012, F-1874-2012
