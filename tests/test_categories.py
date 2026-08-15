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
