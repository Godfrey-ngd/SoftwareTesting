from app.routes.api import _normalize_output


def test_normalize_output_flattens_test_cases_into_inputs():
    data = {
        "input_variables": ["x"],
        "equivalence_partitions": [],
        "boundary_values": [],
        "test_cases": [
            {
                "test_case_id": "TC1",
                "description": "desc",
                "expected_result": "ok",
                "item_price": 3.0,
                "payment_method": "coin",
            }
        ],
        "notes": "",
    }

    normalized = _normalize_output(data, technique="ep_bva")
    assert normalized["test_cases"][0]["id"] == "TC1"
    assert normalized["test_cases"][0]["scenario"] == "desc"
    assert normalized["test_cases"][0]["expected"] == "ok"
    assert normalized["test_cases"][0]["inputs"]["item_price"] == 3.0
    assert normalized["test_cases"][0]["inputs"]["payment_method"] == "coin"


def test_normalize_output_flattens_partitions_and_boundaries_when_dict():
    data = {
        "input_variables": {"a": 1, "b": 2},
        "equivalence_partitions": {"amount": {"valid": ["=price"], "invalid": ["<0"]}},
        "boundary_values": {"amount": [0, 1, 2]},
        "test_cases": [],
        "notes": "",
    }

    normalized = _normalize_output(data, technique="ep_bva")
    assert normalized["input_variables"] == ["a", "b"]
    assert isinstance(normalized["equivalence_partitions"], list)
    assert isinstance(normalized["boundary_values"], list)
    assert normalized["boundary_values"][0]["variable"] == "amount"


def test_normalize_output_dedupes_conflicting_combinations():
    data = {
        "test_cases": [
            {
                "id": "TC1",
                "description": "a",
                "inputs": {"a": 1, "b": True},
                "expected": "HTTP 201 Created",
            },
            {
                "id": "TC2",
                "description": "b",
                "inputs": {"b": True, "a": 1},
                "expected": "HTTP 400; code=FAIL",
            },
        ],
        "coverage": {"total_pairs": 0, "covered_pairs": 0, "pairwise_coverage_percent": 0, "notes": ""},
    }
    normalized = _normalize_output(data, technique="combinatorial")
    assert len(normalized["test_cases"]) == 1
    assert "conflicting test cases" in normalized["coverage"]["notes"]
