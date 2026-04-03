from fastapi import APIRouter, HTTPException

from app.schemas.output import GenerateRequest, GenerateResponse
from app.services.llm_client import LLMClient
from app.services.prompt_manager import PromptManager

router = APIRouter()


@router.post("/generate", response_model=GenerateResponse)
def generate(request: GenerateRequest) -> GenerateResponse:
    prompt = PromptManager.get_prompt(request.prompt_version, request.requirements)
    client = LLMClient()

    try:
        data = client.generate_json(
            prompt=prompt,
            model=request.model,
            temperature=request.temperature,
        )
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return GenerateResponse(**_normalize_output(data))


def _normalize_output(data: dict) -> dict:
    data = _normalize_top_level(data)

    test_cases = data.get("test_cases")
    if not isinstance(test_cases, list):
        return data

    normalized = []
    for index, item in enumerate(test_cases):
        if not isinstance(item, dict):
            continue

        inputs = dict(item.get("inputs") or {})

        for key in [
            "item_category",
            "item_price",
            "payment_method",
            "inserted_amount",
            "inventory_status",
        ]:
            if key in item and key not in inputs:
                inputs[key] = item[key]

        normalized.append(
            {
                "id": str(item.get("id") or item.get("test_case_id") or index + 1),
                "scenario": item.get("scenario") or item.get("description") or "",
                "inputs": inputs,
                "expected": item.get("expected") or item.get("expected_result") or "",
            }
        )

    data["test_cases"] = normalized
    return data


def _normalize_top_level(data: dict) -> dict:
    if not isinstance(data.get("input_variables"), list):
        data["input_variables"] = _dict_keys_to_list(data.get("input_variables"))

    if not isinstance(data.get("equivalence_partitions"), list):
        data["equivalence_partitions"] = _flatten_partitions(
            data.get("equivalence_partitions")
        )

    if not isinstance(data.get("boundary_values"), list):
        data["boundary_values"] = _flatten_boundaries(data.get("boundary_values"))

    return data


def _dict_keys_to_list(value) -> list:
    if isinstance(value, dict):
        return [str(key) for key in value.keys()]
    if isinstance(value, list):
        return value
    return []


def _flatten_partitions(value) -> list:
    if isinstance(value, list):
        return value

    if not isinstance(value, dict):
        return []

    flattened = []
    counter = 1
    for var_name, groups in value.items():
        if isinstance(groups, dict):
            for label, items in groups.items():
                flattened.append(
                    {
                        "id": f"EP{counter}",
                        "description": f"{var_name}: {label} -> {items}",
                        "valid": label.lower() == "valid",
                    }
                )
                counter += 1
        else:
            flattened.append(
                {
                    "id": f"EP{counter}",
                    "description": f"{var_name}: {groups}",
                    "valid": True,
                }
            )
            counter += 1

    return flattened


def _flatten_boundaries(value) -> list:
    if isinstance(value, list):
        return value

    if not isinstance(value, dict):
        return []

    flattened = []
    for var_name, bounds in value.items():
        if isinstance(bounds, dict):
            values = list(bounds.values())
        elif isinstance(bounds, list):
            values = bounds
        else:
            values = [bounds]
        flattened.append({"variable": str(var_name), "values": values})

    return flattened
