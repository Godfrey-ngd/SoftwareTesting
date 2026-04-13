from enum import Enum
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class InputType(str, Enum):
    requirements = "requirements"
    codebase = "codebase"


class Technique(str, Enum):
    ep_bva = "ep_bva"
    decision_table = "decision_table"
    state_transition = "state_transition"
    combinatorial = "combinatorial"


class EquivalencePartition(BaseModel):
    id: str
    description: str
    valid: bool
    representative_values: Optional[List[Any]] = None

    class Config:
        extra = "forbid"


class BoundaryValue(BaseModel):
    variable: str
    # Backward compatible (old format):
    values: Optional[List[Any]] = None
    # Industrial-style BVA row format (new):
    boundary_type: Optional[str] = None
    value: Optional[Any] = None
    expected_valid: Optional[bool] = None

    class Config:
        extra = "forbid"


class DecisionTableCondition(BaseModel):
    id: Optional[str] = None
    description: Optional[str] = ""
    values: Optional[List[Any]] = None

    class Config:
        extra = "ignore"


class DecisionTableAction(BaseModel):
    id: Optional[str] = None
    description: Optional[str] = ""

    class Config:
        extra = "ignore"


class DecisionTableRule(BaseModel):
    rule_id: Optional[str] = None
    condition_entries: List[Any]
    action_entries: List[str]
    description: Optional[str] = ""

    class Config:
        extra = "ignore"


class CombinatorialParameter(BaseModel):
    name: str
    values: List[Any]
    type: Optional[str] = None

    class Config:
        extra = "forbid"


class CoverageStrategy(BaseModel):
    method: str
    strength: int

    class Config:
        extra = "forbid"


class CombinatorialConstraint(BaseModel):
    id: str
    description: str
    invalid_combinations: List[Dict[str, Any]] = Field(default_factory=list)

    class Config:
        extra = "forbid"


class EPBVACoverageSummary(BaseModel):
    total_equivalence_partitions: int
    covered_partitions: int
    total_boundary_conditions: int
    covered_boundary_conditions: int
    notes: str = ""

    class Config:
        extra = "forbid"


class TestCase(BaseModel):
    id: str
    covers_rule: Optional[str] = None
    scenario: str
    inputs: Dict[str, Any]
    combination: Optional[Dict[str, Any]] = None
    covers_pairs: Optional[List[List[str]]] = None
    expected: str

    class Config:
        extra = "forbid"


class GenerateRequest(BaseModel):
    requirements: str = Field(default="", description="Requirement text (if input_type=requirements).")
    code_context: str = Field(
        default="",
        description="Testing codebase/module snippet (if input_type=codebase). Paste code or docs.",
    )
    input_type: InputType = InputType.requirements
    technique: Technique = Technique.ep_bva
    prompt_version: str = "v1"
    model: str = "gpt-4o-mini"
    temperature: float = 0.2

    class Config:
        extra = "forbid"


class Meta(BaseModel):
    technique: Technique
    model: str
    temperature: float
    # Optional fields (used by this tool; safe for EP/BVA spec)
    input_type: Optional[InputType] = None
    prompt_version: Optional[str] = None
    strategy: Optional[str] = None

    class Config:
        extra = "forbid"

class EPBVAResponse(BaseModel):
    input_variables: List[str]
    equivalence_partitions: List[EquivalencePartition]
    boundary_values: List[BoundaryValue]
    test_cases: List[TestCase]
    coverage_summary: EPBVACoverageSummary
    notes: str = ""
    meta: Meta

    class Config:
        extra = "forbid"


class DecisionTableResponse(BaseModel):
    input_variables: List[str]
    conditions: List[DecisionTableCondition]
    actions: List[DecisionTableAction]
    rules: List[DecisionTableRule]
    class DecisionTableTestCase(BaseModel):
        id: Optional[str] = None
        covers_rule: Optional[str] = None
        inputs: Optional[Dict[str, Any]] = None
        expected: Optional[str] = ""

        class Config:
            extra = "ignore"

    test_cases: List[DecisionTableTestCase]
    coverage: Dict[str, Any]
    notes: Optional[str] = ""
    meta: Optional[Meta] = None

    class Config:
        extra = "ignore"


class CombinatorialTestCase(BaseModel):
    id: str
    description: str
    inputs: Dict[str, Any]
    expected: str

    class Config:
        extra = "forbid"


class CombinatorialCoverage(BaseModel):
    total_pairs: int
    covered_pairs: int
    pairwise_coverage_percent: float
    notes: str = ""

    class Config:
        extra = "forbid"


class CombinatorialResponse(BaseModel):
    parameters: List[CombinatorialParameter]
    constraints: List[CombinatorialConstraint]
    test_cases: List[CombinatorialTestCase]
    coverage: CombinatorialCoverage
    meta: Meta

    class Config:
        extra = "forbid"


class StateDef(BaseModel):
    id: str
    name: str
    description: str

    class Config:
        extra = "forbid"


class EventDef(BaseModel):
    id: str
    name: str
    description: str

    class Config:
        extra = "forbid"


class TransitionDef(BaseModel):
    id: str
    from_state: str
    to_state: str
    event: str
    guard: Optional[str] = None
    action: Optional[str] = None
    output: str

    class Config:
        extra = "forbid"


class StateTransitionTestCase(BaseModel):
    id: str
    description: str
    initial_state: str
    event: str
    context: Dict[str, Any]
    expected_state: str
    expected_output: str

    class Config:
        extra = "forbid"


class TransitionCoverage(BaseModel):
    total_transitions: int
    covered_transitions: int
    uncovered_transition_ids: List[str]
    notes: str = ""

    class Config:
        extra = "forbid"


class StateTransitionResponse(BaseModel):
    states: List[StateDef]
    events: List[EventDef]
    transitions: List[TransitionDef]
    test_cases: List[StateTransitionTestCase]
    coverage: TransitionCoverage
    meta: Meta

    class Config:
        extra = "forbid"


class StateTransitionErrorResponse(BaseModel):
    error: str
    coverage: TransitionCoverage
    meta: Meta

    class Config:
        extra = "forbid"
