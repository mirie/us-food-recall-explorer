"""Unit tests for the manual LLM category-labelling round trip.

This module never calls an API -- it only shapes the export handed to a
separate Claude.ai chat, and parses/validates whatever comes back. All
inputs here are hand-built; nothing touches data/food_recalls.csv.
"""

import re
from pathlib import Path

import pandas as pd
import pytest

from recall_explorer.llm_categories import (
    CATEGORY_ENUM,
    build_classification_prompt,
    export_for_classification,
    parse_classification_result,
)
from recall_explorer.categories import UNCATEGORIZED

RULES_PATH = Path(__file__).resolve().parent.parent / "CLASSIFICATION_RULES.md"


def _df(rows):
    return pd.DataFrame(rows, columns=["recall_number", "category", "product_description"])


# --- CATEGORY_ENUM -----------------------------------------------------------

def test_category_enum_includes_uncategorized_and_no_duplicates():
    assert UNCATEGORIZED in CATEGORY_ENUM
    assert len(CATEGORY_ENUM) == len(set(CATEGORY_ENUM))


def test_category_enum_matches_classification_rules_doc():
    """CATEGORY_ENUM must exactly match CLASSIFICATION_RULES.md's label set."""
    text = RULES_PATH.read_text()
    match = re.search(r"## 1\. Label set \(21\)\s*```text\n(.*?)\n```", text, re.DOTALL)
    assert match, "Could not find the '## 1. Label set (21)' code block in CLASSIFICATION_RULES.md"
    doc_labels = [line.strip() for line in match.group(1).splitlines() if line.strip()]
    assert CATEGORY_ENUM == doc_labels


# --- export_for_classification ------------------------------------------------

def test_export_filters_to_uncategorized_rows_only():
    df = _df(
        [
            ("F-0001", "Produce", "Fresh lettuce"),
            ("F-0002", UNCATEGORIZED, "Pure trans-resveratrol"),
            ("F-0003", UNCATEGORIZED, "California medley"),
        ]
    )
    out = export_for_classification(df)
    assert list(out["recall_number"]) == ["F-0002", "F-0003"]
    assert list(out.columns) == ["recall_number", "product_description"]


def test_export_returns_empty_frame_when_nothing_uncategorized():
    df = _df([("F-0001", "Produce", "Fresh lettuce")])
    out = export_for_classification(df)
    assert len(out) == 0
    assert list(out.columns) == ["recall_number", "product_description"]


# --- build_classification_prompt ---------------------------------------------

def test_prompt_lists_every_enum_category():
    prompt = build_classification_prompt()
    for category in CATEGORY_ENUM:
        assert category in prompt


def test_prompt_specifies_output_shape():
    prompt = build_classification_prompt()
    assert "recall_number,category" in prompt


# --- parse_classification_result ----------------------------------------------

def test_parses_clean_csv_response():
    raw = "recall_number,category\nF-0002,Supplements\nF-0003,Produce\n"
    mapping, problems = parse_classification_result(raw, expected_recall_numbers={"F-0002", "F-0003"})
    assert mapping == {"F-0002": "Supplements", "F-0003": "Produce"}
    assert problems == []


def test_flags_invalid_category_and_drops_it():
    raw = "recall_number,category\nF-0002,NotARealCategory\nF-0003,Produce\n"
    mapping, problems = parse_classification_result(raw, expected_recall_numbers={"F-0002", "F-0003"})
    assert mapping == {"F-0003": "Produce"}
    assert any("F-0002" in p and "NotARealCategory" in p for p in problems)


def test_flags_missing_expected_recall_number():
    raw = "recall_number,category\nF-0002,Produce\n"
    mapping, problems = parse_classification_result(raw, expected_recall_numbers={"F-0002", "F-0003"})
    assert mapping == {"F-0002": "Produce"}
    assert any("F-0003" in p for p in problems)


def test_flags_unexpected_recall_number():
    raw = "recall_number,category\nF-0002,Produce\nF-9999,Produce\n"
    mapping, problems = parse_classification_result(raw, expected_recall_numbers={"F-0002"})
    assert mapping == {"F-0002": "Produce"}
    assert any("F-9999" in p for p in problems)


def test_ignores_blank_lines():
    raw = "recall_number,category\n\nF-0002,Produce\n\n"
    mapping, problems = parse_classification_result(raw, expected_recall_numbers={"F-0002"})
    assert mapping == {"F-0002": "Produce"}
    assert problems == []


def test_handles_missing_header_gracefully():
    raw = "F-0002,Produce\nF-0003,Bakery\n"
    mapping, problems = parse_classification_result(raw, expected_recall_numbers={"F-0002", "F-0003"})
    assert mapping == {"F-0002": "Produce", "F-0003": "Bakery"}
    assert problems == []


def test_empty_response_flags_all_expected_as_missing():
    mapping, problems = parse_classification_result("", expected_recall_numbers={"F-0002"})
    assert mapping == {}
    assert any("F-0002" in p for p in problems)
