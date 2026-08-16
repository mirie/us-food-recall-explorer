"""Unit tests for classify_all.py's pure logic.

Per the project's three-tier testing strategy: strict TDD on pure logic here
(chunking, request-shaping, result-parsing, completeness checks -- all
hand-built fixtures, no file I/O beyond the real CLASSIFICATION_RULES.md and
data/food_recalls.csv reads used for the two real-file checks below), plus
one real-file pipeline test. The actual Batch API calls (submit/fetch CLI
commands) are not unit-tested -- per the project's explicit skip list, no
retry/upload/network mocking theater. `parse_classification_result`'s CSV
round trip (the old manual-pass path) is untouched and covered separately in
test_llm_categories.py.
"""

import csv
import json
from pathlib import Path

import pandas as pd
import pytest

from classify_all import (
    CHUNK_SIZE,
    MAX_TOKENS,
    MODEL,
    N_SUBMISSIONS,
    build_chunk_request,
    build_chunk_user_content,
    build_response_schema,
    build_system_blocks,
    check_completeness,
    chunk_rows,
    custom_id_for,
    parse_chunk_response_text,
    rows_to_classify,
    split_into_submissions,
    write_results_csv,
)
from recall_explorer.llm_categories import CATEGORY_ENUM
from recall_explorer.pipeline import load_recalls


# --- chunk_rows ----------------------------------------------------------

def test_chunk_rows_splits_into_groups_of_chunk_size():
    rows = [(f"F-{i}", f"desc {i}") for i in range(250)]
    chunks = chunk_rows(rows, chunk_size=100)
    assert len(chunks) == 3
    assert len(chunks[0]) == 100
    assert len(chunks[1]) == 100
    assert len(chunks[2]) == 50


def test_chunk_rows_default_chunk_size_matches_module_constant():
    rows = [(f"F-{i}", f"desc {i}") for i in range(CHUNK_SIZE + 1)]
    chunks = chunk_rows(rows)
    assert len(chunks) == 2
    assert len(chunks[0]) == CHUNK_SIZE


def test_chunk_rows_empty_input_returns_empty_list():
    assert chunk_rows([]) == []


def test_chunk_rows_preserves_row_order_and_content():
    rows = [("F-0001", "a"), ("F-0002", "b"), ("F-0003", "c")]
    chunks = chunk_rows(rows, chunk_size=2)
    assert chunks == [[("F-0001", "a"), ("F-0002", "b")], [("F-0003", "c")]]


# --- custom_id_for ---------------------------------------------------------

def test_custom_id_for_zero_pads():
    assert custom_id_for(0) == "chunk-0000"
    assert custom_id_for(7) == "chunk-0007"
    assert custom_id_for(291) == "chunk-0291"


def test_custom_id_for_is_unique_across_a_realistic_range():
    ids = {custom_id_for(i) for i in range(292)}
    assert len(ids) == 292


# --- build_chunk_user_content ----------------------------------------------

def test_build_chunk_user_content_has_csv_header():
    content = build_chunk_user_content([("F-0001", "Fresh lettuce")])
    assert content.startswith("recall_number,product_description")


def test_build_chunk_user_content_includes_every_row():
    chunk = [("F-0001", "Fresh lettuce"), ("F-0002", "Whole milk")]
    content = build_chunk_user_content(chunk)
    reader = csv.reader(content.splitlines())
    rows = list(reader)
    assert rows[0] == ["recall_number", "product_description"]
    assert rows[1] == ["F-0001", "Fresh lettuce"]
    assert rows[2] == ["F-0002", "Whole milk"]


def test_build_chunk_user_content_escapes_commas_and_quotes():
    chunk = [("F-0001", 'Product, "Fancy" Edition')]
    content = build_chunk_user_content(chunk)
    reader = csv.reader(content.splitlines())
    rows = list(reader)
    assert rows[1] == ["F-0001", 'Product, "Fancy" Edition']


# --- build_response_schema --------------------------------------------------

def test_response_schema_category_enum_matches_category_enum():
    schema = build_response_schema()
    item_schema = schema["properties"]["classifications"]["items"]
    assert item_schema["properties"]["category"]["enum"] == CATEGORY_ENUM


def test_response_schema_confidence_enum_is_high_medium_low():
    schema = build_response_schema()
    item_schema = schema["properties"]["classifications"]["items"]
    assert item_schema["properties"]["confidence"]["enum"] == ["high", "medium", "low"]


def test_response_schema_forbids_additional_properties():
    schema = build_response_schema()
    assert schema["additionalProperties"] is False
    item_schema = schema["properties"]["classifications"]["items"]
    assert item_schema["additionalProperties"] is False


# --- build_system_blocks (real-file read of CLASSIFICATION_RULES.md) -------

def test_build_system_blocks_embeds_classification_rules_content():
    blocks = build_system_blocks()
    assert len(blocks) == 1
    assert "Beef/Pork/Poultry/Game Meats" in blocks[0]["text"]
    assert "Pet Food/Treats" in blocks[0]["text"]


def test_build_system_blocks_marks_cache_control_ephemeral():
    blocks = build_system_blocks()
    assert blocks[0]["cache_control"] == {"type": "ephemeral"}


# --- build_chunk_request -----------------------------------------------------

def test_build_chunk_request_shape():
    system_blocks = build_system_blocks()
    chunk = [("F-0001", "Fresh lettuce")]
    request = build_chunk_request("chunk-0000", chunk, system_blocks)
    assert request["custom_id"] == "chunk-0000"
    assert request["params"]["model"] == MODEL
    assert request["params"]["max_tokens"] == MAX_TOKENS
    assert request["params"]["system"] == system_blocks
    assert request["params"]["output_config"]["format"]["type"] == "json_schema"


# --- parse_chunk_response_text ----------------------------------------------

def test_parse_chunk_response_text_returns_classification_list():
    text = json.dumps({
        "classifications": [
            {"recall_number": "F-0001", "category": "Produce", "confidence": "high"},
            {"recall_number": "F-0002", "category": "Dairy", "confidence": "medium"},
        ]
    })
    records = parse_chunk_response_text(text)
    assert records == [
        {"recall_number": "F-0001", "category": "Produce", "confidence": "high"},
        {"recall_number": "F-0002", "category": "Dairy", "confidence": "medium"},
    ]


# --- check_completeness -----------------------------------------------------

def test_check_completeness_reports_nothing_when_sets_match():
    missing, unexpected = check_completeness({"F-0001", "F-0002"}, {"F-0001", "F-0002"})
    assert missing == []
    assert unexpected == []


def test_check_completeness_detects_missing():
    missing, unexpected = check_completeness({"F-0001"}, {"F-0001", "F-0002"})
    assert missing == ["F-0002"]
    assert unexpected == []


def test_check_completeness_detects_unexpected():
    missing, unexpected = check_completeness({"F-0001", "F-9999"}, {"F-0001"})
    assert missing == []
    assert unexpected == ["F-9999"]


# --- split_into_submissions --------------------------------------------------

def test_split_into_submissions_preserves_every_chunk():
    chunks = [[("F-%04d" % i, "d")] for i in range(292)]
    submissions = split_into_submissions(chunks, n_submissions=3)
    assert len(submissions) == 3
    flattened = [c for submission in submissions for c in submission]
    assert flattened == chunks


def test_split_into_submissions_default_matches_module_constant():
    chunks = [[("F-0001", "d")]] * 10
    submissions = split_into_submissions(chunks)
    assert len(submissions) == N_SUBMISSIONS


def test_split_into_submissions_roughly_equal_sizes():
    chunks = [[("F-0001", "d")]] * 292
    submissions = split_into_submissions(chunks, n_submissions=3)
    sizes = [len(s) for s in submissions]
    assert max(sizes) - min(sizes) <= 1


# --- write_results_csv --------------------------------------------------------

def test_write_results_csv_writes_header_and_sorted_rows(tmp_path):
    out_path = tmp_path / "results.csv"
    records = [
        {"recall_number": "F-0002", "category": "Dairy", "confidence": "high"},
        {"recall_number": "F-0001", "category": "Produce", "confidence": "medium"},
    ]
    write_results_csv(records, out_path)
    with open(out_path) as f:
        rows = list(csv.reader(f))
    assert rows[0] == ["recall_number", "category", "confidence"]
    assert rows[1] == ["F-0001", "Produce", "medium"]
    assert rows[2] == ["F-0002", "Dairy", "high"]


# --- rows_to_classify --------------------------------------------------------

def test_rows_to_classify_extracts_recall_number_and_description():
    df = pd.DataFrame({
        "recall_number": ["F-0001", "F-0002"],
        "product_description": ["Fresh lettuce", "Whole milk"],
        "category": ["Produce", "Dairy"],
    })
    rows = rows_to_classify(df)
    assert rows == [("F-0001", "Fresh lettuce"), ("F-0002", "Whole milk")]


# --- real-file pipeline test -------------------------------------------------

def test_rows_to_classify_covers_the_full_real_dataset():
    """Every row in the real snapshot must be classifiable -- this pass is a
    full relabel, not a residual-only export like the old Phase 3 path.

    Two rows share a blank recall_number (pre-existing in the raw openFDA
    snapshot, not introduced by this module -- see BUILD_LOG's known-gap
    note), so unique keys are one short of the row count. Both rows are
    still present in `rows` and will still be sent to the classifier; the
    gap only affects recall_number-keyed lookups downstream."""
    df = load_recalls()
    rows = rows_to_classify(df)
    assert len(rows) == len(df)
    assert len({r for r, _ in rows}) == len(df) - 1
