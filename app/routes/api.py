import json
from typing import Any, Dict, Tuple

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.schemas.output import (
    CombinatorialResponse,
    DecisionTableResponse,
    EPBVAResponse,
    GenerateRequest,
    StateTransitionErrorResponse,
    StateTransitionResponse,
)
from app.services.llm_client import LLMClient
from app.services.prompt_manager import PromptManager

router = APIRouter()


@router.post("/generate")
def generate(request: GenerateRequest):
    prompt = PromptManager.get_prompt(
        version=request.prompt_version,
        input_type=request.input_type.value,
        technique=request.technique.value,
        requirement_text=request.requirements,
        code_context=request.code_context,
    )
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

    normalized = _normalize_output(data, technique=request.technique.value)
    normalized["meta"] = {
        "technique": request.technique.value,
        "model": request.model,
        "temperature": float(request.temperature),
        "input_type": request.input_type.value,
        "prompt_version": request.prompt_version,
        **({"strategy": "pairwise"} if request.technique.value == "combinatorial" else {}),
    }
    return _validate_by_technique(normalized, request.technique.value)


@router.post("/generate-stream")
def generate_stream(request: GenerateRequest) -> StreamingResponse:
    prompt = PromptManager.get_prompt(
        version=request.prompt_version,
        input_type=request.input_type.value,
        technique=request.technique.value,
        requirement_text=request.requirements,
        code_context=request.code_context,
    )
    client = LLMClient()

    def event_stream():
        chunks = []
        try:
            yield ": init\n\n"
            for chunk in client.stream_text(
                prompt=prompt,
                model=request.model,
                temperature=request.temperature,
            ):
                chunks.append(chunk)
                payload = json.dumps({"text": chunk})
                yield f"event: chunk\ndata: {payload}\n\n"

            full_text = "".join(chunks)
            data = client._parse_json(full_text)
            normalized = _normalize_output(data, technique=request.technique.value)
            normalized["meta"] = {
                "technique": request.technique.value,
                "model": request.model,
                "temperature": float(request.temperature),
                "input_type": request.input_type.value,
                "prompt_version": request.prompt_version,
                **({"strategy": "pairwise"} if request.technique.value == "combinatorial" else {}),
            }
            validated = _validate_by_technique(normalized, request.technique.value)
            payload = json.dumps({"data": validated})
            yield f"event: done\ndata: {payload}\n\n"
        except Exception as exc:
            payload = json.dumps({"error": str(exc)})
            yield f"event: error\ndata: {payload}\n\n"

    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
    }
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers=headers,
    )


def _normalize_output(data: dict, technique: str) -> dict:
    # State-transition has its own strict schema; avoid EP/BVA normalization on it.
    if technique == "state_transition":
        return _normalize_state_transition(data)

    # Combinatorial has its own shape; do minimal conflict cleanup.
    if technique == "combinatorial":
        data = _normalize_combinatorial(data)
        _dedupe_combinatorial_cases_in_place(data)
        return data

    if technique == "decision_table":
        return _normalize_decision_table(data)

    data = _normalize_top_level(data)

    test_cases = data.get("test_cases")
    if not isinstance(test_cases, list):
        return data

    normalized = []
    for index, item in enumerate(test_cases):
        if not isinstance(item, dict):
            continue

        combination = item.get("combination")
        if isinstance(combination, dict):
            inputs = dict(combination)
        else:
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
                "covers_rule": item.get("covers_rule") or item.get("covers") or item.get("rule"),
                "scenario": item.get("scenario") or item.get("description") or "",
                "inputs": inputs,
                "combination": combination if isinstance(combination, dict) else None,
                "covers_pairs": item.get("covers_pairs"),
                "expected": item.get("expected") or item.get("expected_result") or "",
            }
        )

    data["test_cases"] = normalized
    _dedupe_test_cases_in_place(data)
    return data


def _normalize_decision_table(data: dict) -> dict:
    if not isinstance(data, dict):
        return {}

    # Ensure required top-level keys exist (let schema enforce correctness later).
    data.setdefault("input_variables", [])
    data.setdefault("conditions", [])
    data.setdefault("actions", [])
    data.setdefault("rules", [])
    data.setdefault("test_cases", [])
    data.setdefault("coverage", {"total_rules": 0, "covered_rules": 0, "notes": ""})
    data.setdefault("notes", "")

    # Normalize conditions: allow "values" missing.
    if isinstance(data.get("conditions"), list):
        for c in data["conditions"]:
            if isinstance(c, dict) and "values" not in c:
                c["values"] = None

    # Normalize rules: accept old keys (id/conditions/actions) and convert dict->entry lists when possible.
    normalized_rules = []
    if isinstance(data.get("rules"), list):
        for r in data["rules"]:
            if not isinstance(r, dict):
                continue
            if "rule_id" not in r and "id" in r:
                r["rule_id"] = r["id"]
            if "condition_entries" not in r and isinstance(r.get("conditions"), dict):
                # Best-effort: map dict entries to list aligned with current conditions order.
                cond_order = [c.get("id") for c in data.get("conditions") or [] if isinstance(c, dict)]
                if cond_order:
                    r["condition_entries"] = [r["conditions"].get(cid, "-") for cid in cond_order]
            if "action_entries" not in r and isinstance(r.get("actions"), dict):
                act_order = [a.get("id") for a in data.get("actions") or [] if isinstance(a, dict)]
                if act_order:
                    r["action_entries"] = [r["actions"].get(aid, "") for aid in act_order]
            r.pop("id", None)
            r.pop("conditions", None)
            r.pop("actions", None)
            if "description" not in r:
                r["description"] = ""
            normalized_rules.append(r)
    data["rules"] = normalized_rules

    # Normalize test cases: allow "covers"/"rule" aliases.
    normalized_cases = []
    if isinstance(data.get("test_cases"), list):
        for i, tc in enumerate(data["test_cases"]):
            if not isinstance(tc, dict):
                continue
            tc.setdefault("id", f"TC{i+1}")
            if "covers_rule" not in tc:
                tc["covers_rule"] = tc.get("covers") or tc.get("rule")
            if "inputs" not in tc and isinstance(tc.get("context"), dict):
                tc["inputs"] = tc["context"]
            tc.pop("scenario", None)
            tc.pop("description", None)
            tc.pop("context", None)
            normalized_cases.append(tc)
    data["test_cases"] = normalized_cases

    if isinstance(data.get("notes"), dict):
        data["notes"] = json.dumps(data["notes"], ensure_ascii=False, sort_keys=True)

    return data


def _normalize_combinatorial(data: dict) -> dict:
    if not isinstance(data, dict):
        return {}

    # Accept old format: factors/coverage_strategy/coverage_summary -> parameters/coverage/meta.strategy.
    if "parameters" not in data and isinstance(data.get("factors"), list):
        data["parameters"] = [
            {"name": f.get("name"), "values": f.get("values"), "type": None}
            for f in data["factors"]
            if isinstance(f, dict)
        ]

    if "constraints" in data and isinstance(data["constraints"], list) and data["constraints"] and isinstance(data["constraints"][0], str):
        # Convert string constraints to structured constraints.
        data["constraints"] = [
            {"id": f"C{i+1}", "description": str(desc), "invalid_combinations": []}
            for i, desc in enumerate(data["constraints"])
        ]

    if "coverage" not in data and isinstance(data.get("coverage_summary"), dict):
        # Best-effort mapping.
        data["coverage"] = {
            "total_pairs": 0,
            "covered_pairs": 0,
            "pairwise_coverage_percent": 100,
            "notes": str(data["coverage_summary"].get("notes") or ""),
        }

    meta = data.get("meta") if isinstance(data.get("meta"), dict) else {}
    if isinstance(meta, dict):
        meta.setdefault("strategy", "pairwise")
        data["meta"] = meta

    return data


def _normalize_state_transition(data: dict) -> dict:
    # Keep strict by default; only do safe, non-lossy normalizations.
    if not isinstance(data, dict):
        return {}

    # If already error shape, keep.
    if "error" in data:
        cov = data.get("coverage") if isinstance(data.get("coverage"), dict) else {}
        cov.setdefault("total_transitions", 0)
        cov.setdefault("covered_transitions", 0)
        cov.setdefault("uncovered_transition_ids", [])
        cov.setdefault("notes", "")
        data["coverage"] = cov
        return data

    # states/events may come as list[str]; convert to objects with ids.
    if isinstance(data.get("states"), list) and data["states"] and isinstance(data["states"][0], str):
        data["states"] = [
            {"id": f"S{i+1}", "name": s, "description": ""}
            for i, s in enumerate(data["states"])
        ]
    if isinstance(data.get("events"), list) and data["events"] and isinstance(data["events"][0], str):
        data["events"] = [
            {"id": f"E{i+1}", "name": e, "description": ""}
            for i, e in enumerate(data["events"])
        ]

    # transitions: accept "action" only and map to output if output missing.
    if isinstance(data.get("transitions"), list):
        for t in data["transitions"]:
            if not isinstance(t, dict):
                continue
            if "output" not in t and "action" in t and isinstance(t["action"], str):
                t["output"] = t["action"]

    # coverage defaults
    cov = data.get("coverage") if isinstance(data.get("coverage"), dict) else {}
    cov.setdefault("total_transitions", len(data.get("transitions") or []) if isinstance(data.get("transitions"), list) else 0)
    cov.setdefault("covered_transitions", 0)
    cov.setdefault("uncovered_transition_ids", [])
    cov.setdefault("notes", "")
    data["coverage"] = cov

    return data


def _dedupe_combinatorial_cases_in_place(data: Dict[str, Any]) -> None:
    test_cases = data.get("test_cases")
    if not isinstance(test_cases, list):
        return

    kept: list[dict] = []
    seen: Dict[Tuple[Tuple[str, str], ...], str] = {}
    dropped_conflicts = 0
    dropped_duplicates = 0

    for item in test_cases:
        if not isinstance(item, dict):
            continue
        inputs = item.get("inputs")
        if not isinstance(inputs, dict):
            continue
        key = tuple(sorted((str(k), json.dumps(v, sort_keys=True)) for k, v in inputs.items()))
        expected = str(item.get("expected") or "")
        if key in seen:
            if seen[key] != expected:
                dropped_conflicts += 1
                continue
            dropped_duplicates += 1
            continue
        seen[key] = expected
        kept.append(item)

    if dropped_conflicts or dropped_duplicates:
        cov = data.get("coverage") if isinstance(data.get("coverage"), dict) else {}
        notes = str(cov.get("notes") or "")
        extra = (
            f"Dedupe applied: removed {dropped_duplicates} duplicate test cases and "
            f"{dropped_conflicts} conflicting test cases with identical inputs."
        )
        cov["notes"] = (notes + "\n" + extra).strip()
        data["coverage"] = cov
        data["test_cases"] = kept


def _validate_by_technique(payload: dict, technique: str) -> dict:
    try:
        if technique == "ep_bva":
            return EPBVAResponse(**payload).model_dump()
        if technique == "decision_table":
            return DecisionTableResponse(**payload).model_dump()
        if technique == "combinatorial":
            return CombinatorialResponse(**payload).model_dump()
        if technique == "state_transition":
            if "error" in payload:
                return StateTransitionErrorResponse(**payload).model_dump()
            return StateTransitionResponse(**payload).model_dump()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Output schema validation failed: {exc}") from exc

    raise HTTPException(status_code=400, detail=f"Unknown technique: {technique}")


def _dedupe_test_cases_in_place(data: Dict[str, Any]) -> None:
    test_cases = data.get("test_cases")
    if not isinstance(test_cases, list):
        return

    kept: list[dict] = []
    seen: Dict[Tuple[Tuple[str, str], ...], str] = {}
    dropped_conflicts = 0
    dropped_duplicates = 0

    for item in test_cases:
        if not isinstance(item, dict):
            continue
        combo = item.get("combination")
        if not isinstance(combo, dict):
            continue

        key = tuple(sorted((str(k), json.dumps(v, sort_keys=True)) for k, v in combo.items()))
        expected = str(item.get("expected") or "")
        if key in seen:
            if seen[key] != expected:
                dropped_conflicts += 1
                continue
            dropped_duplicates += 1
            continue
        seen[key] = expected
        kept.append(item)

    if dropped_conflicts or dropped_duplicates:
        notes = str(data.get("notes") or "")
        extra = (
            f"Dedupe applied: removed {dropped_duplicates} duplicate test cases and "
            f"{dropped_conflicts} conflicting test cases with identical combinations."
        )
        data["notes"] = (notes + "\n" + extra).strip()
        data["test_cases"] = kept


def _normalize_top_level(data: dict) -> dict:
    if not isinstance(data.get("input_variables"), list):
        data["input_variables"] = _dict_keys_to_list(data.get("input_variables"))

    if not isinstance(data.get("equivalence_partitions"), list):
        data["equivalence_partitions"] = _flatten_partitions(
            data.get("equivalence_partitions")
        )
    else:
        # EP representative_values must be a list when present.
        for ep in data["equivalence_partitions"]:
            if not isinstance(ep, dict):
                continue
            rv = ep.get("representative_values")
            if rv is None:
                continue
            if isinstance(rv, list):
                continue
            ep["representative_values"] = [rv]

    if not isinstance(data.get("boundary_values"), list):
        data["boundary_values"] = _flatten_boundaries(data.get("boundary_values"))

    # notes should be a string (some models return an object).
    if isinstance(data.get("notes"), dict):
        data["notes"] = json.dumps(data["notes"], ensure_ascii=False, sort_keys=True)

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
