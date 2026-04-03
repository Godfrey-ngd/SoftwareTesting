from typing import Any, Dict, List

from pydantic import BaseModel, Field


class EquivalencePartition(BaseModel):
    id: str
    description: str
    valid: bool

    class Config:
        extra = "forbid"


class BoundaryValue(BaseModel):
    variable: str
    values: List[Any]

    class Config:
        extra = "forbid"


class TestCase(BaseModel):
    id: str
    scenario: str
    inputs: Dict[str, Any]
    expected: str

    class Config:
        extra = "forbid"


class GenerateRequest(BaseModel):
    requirements: str = Field(min_length=1)
    prompt_version: str = "v1"
    model: str = "gpt-4o-mini"
    temperature: float = 0.2

    class Config:
        extra = "forbid"


class GenerateResponse(BaseModel):
    input_variables: List[str]
    equivalence_partitions: List[EquivalencePartition]
    boundary_values: List[BoundaryValue]
    test_cases: List[TestCase]
    notes: str = ""

    class Config:
        extra = "forbid"
