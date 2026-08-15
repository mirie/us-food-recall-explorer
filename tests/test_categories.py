"""Unit tests for food-category derivation.

Hand-built inputs only -- these never touch data/food_recalls.csv.
"""

from recall_explorer.categories import assign_category


def test_unambiguous_description_gets_its_category():
    assert assign_category("Fresh romaine lettuce, 12 oz bag") == "Produce"


def test_specific_category_beats_generic_ingredient_mention():
    # "butter" is an ingredient word; shrimp is what the product actually is.
    assert assign_category("Raw shrimp in garlic butter sauce") == "Seafood"


def test_product_form_beats_ingredient_word():
    # Regression guard on rule ORDER: moving Dairy above Bakery breaks this.
    assert assign_category("Chocolate chip cookies made with real butter") == "Bakery"


def test_dairy_still_wins_when_nothing_more_specific_matches():
    # Dairy is demoted, not disabled -- it must still claim genuine dairy.
    assert assign_category("Whole milk, gallon jug") == "Dairy"


def test_description_matching_nothing_is_uncategorized():
    assert assign_category("Item 80847, case pack 12, no UPC") == "Uncategorized"


def test_missing_description_is_uncategorized_not_an_error():
    # openFDA rows are never null today, but the pipeline must not crash if
    # that changes -- an exception here would take down the whole app.
    assert assign_category("") == "Uncategorized"
    assert assign_category(None) == "Uncategorized"


def test_matching_is_case_insensitive():
    assert assign_category("FRESH ROMAINE LETTUCE") == "Produce"


# --- Meat words are ingredient words in this dataset -------------------------
# FDA does not regulate meat, poultry, or processed egg products -- USDA FSIS
# does, in a separate dataset. So essentially every meat keyword in this corpus
# is a flavour or ingredient mention inside an FDA-regulated processed food,
# not a meat recall. Meat categories therefore rank BELOW product-form
# categories, exactly as Dairy does.

def test_bacon_in_a_candy_product_is_not_a_pork_recall():
    assert assign_category("Bacon Brittle, 2 lbs, bulk plastic bags") == "Snacks/Candy"


def test_beef_in_a_prepared_meal_is_not_a_beef_recall():
    assert assign_category("#380 2 lb Hearty Mac & Beef") == "Prepared/Frozen"


def test_egg_in_an_ingredient_list_is_not_an_egg_recall():
    assert assign_category(
        "Pineapple Pies, 24 count, ingredients include egg"
    ) == "Bakery"


def test_plural_product_forms_still_match():
    # Regression: the Bakery rule was `\bpie\b`, which missed "pies" entirely
    # and let the row fall through to a lower tier.
    assert assign_category("Cherry Pies, 24 count") == "Bakery"


def test_produce_keywords_do_not_match_inside_longer_words():
    # Regression: bare `apple` also matched "pineapple".
    assert assign_category("Pineapple upside down cake") == "Bakery"


def test_chicken_flavouring_is_not_a_poultry_recall():
    assert assign_category(
        "Natural Chicken Flavor Seasoning, Net Weight 50 lbs"
    ) == "Spices/Condiments"


# --- Coverage gaps found by inspecting the Uncategorized bucket --------------
# All strings below are real (lightly trimmed) rows that fell through the first
# rule set. Two whole categories were missing; the rest were absent keywords.

def test_breakfast_cereal_gets_the_grains_category():
    assert assign_category(
        "Kellogg's Frosted Mini Wheats, Bite Size, Whole Grain Wheat Cereal"
    ) == "Grains/Cereal"


def test_grits_are_grains():
    assert assign_category("White quick grits packaged in a paper bag") == "Grains/Cereal"


def test_bulk_cooking_oil_gets_the_oils_category():
    assert assign_category("Oasis Foods Soybean Oil, Net Wt. 35 LB") == "Oils/Fats"


def test_oil_as_an_ingredient_does_not_beat_product_form():
    # Oils/Fats sits in tier 3 for the same reason Dairy does.
    assert assign_category("Sardines packed in olive oil, 4 oz tin") == "Seafood"


def test_mushrooms_are_produce():
    assert assign_category("Utopia brand Enoki Mushroom, 200g") == "Produce"


def test_herring_is_seafood():
    assert assign_category("MA Cohen's Kippered Herring, vacuum packed") == "Seafood"


def test_seed_kernels_are_nuts_and_seeds():
    assert assign_category("Southern Grove Roasted & Unsalted Sunflower Kernels") == "Nuts/Seeds"


def test_whole_spices_are_spices():
    assert assign_category("Cardamom Pods Green Whole Organic, 25 lb bulk") == "Spices/Condiments"


def test_tofu_gets_the_plant_protein_category():
    assert assign_category("Gourmet Firm Tofu, retail vacuum pack, net wt 7 oz") == "Plant Protein"
