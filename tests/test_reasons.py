"""Unit tests for contamination-reason tagging.

Reasons are multi-label: one recall can legitimately cite several causes.
Hand-built inputs only -- these never touch data/food_recalls.csv.
"""

from recall_explorer.reasons import tag_reasons


def test_single_pathogen_is_tagged():
    assert tag_reasons("Product may be contaminated with Listeria monocytogenes.") == ["Listeria"]


def test_recall_citing_two_causes_gets_both_tags():
    # The whole point of multi-label: this recall really does have two causes.
    tags = tag_reasons(
        "Product contains undeclared milk and may also contain small pieces of metal."
    )
    assert set(tags) == {"Undeclared allergen", "Foreign material"}


def test_labeling_phrasing_counts_as_undeclared_allergen():
    # Most allergen recalls never use the word "allergen" -- they describe a
    # labeling defect. Missing this phrasing would undercount the largest group.
    assert "Undeclared allergen" in tag_reasons(
        "The contains statement does not declare walnut."
    )


def test_unmatched_reason_returns_empty_list():
    assert tag_reasons("Product is recalled at the request of the firm.") == []


def test_missing_reason_is_empty_not_an_error():
    assert tag_reasons("") == []
    assert tag_reasons(None) == []


def test_matching_is_case_insensitive():
    assert tag_reasons("PRODUCT MAY CONTAIN SALMONELLA") == ["Salmonella"]


def test_tags_are_not_mutually_exclusive_so_counts_can_exceed_recall_count():
    # Documents the contract the Key Insights cards must respect: any share
    # derived from reasons is "of recalls mentioning X", never "share of total".
    tags = tag_reasons(
        "Undeclared milk; product also tested positive for Listeria monocytogenes."
    )
    assert len(tags) > 1
