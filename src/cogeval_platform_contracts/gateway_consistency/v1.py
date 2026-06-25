from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


GATEWAY_CONSISTENCY_BASELINE_SCHEMA = "cogeval.gateway_consistency.baseline.v1"
GATEWAY_CONSISTENCY_TASK_PACK_SCHEMA = "cogeval.gateway_consistency.task_pack.v1"


class StrictContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class GatewayConsistencyBaseline(StrictContractModel):
    schema_: Literal["cogeval.gateway_consistency.baseline.v1"] = Field(alias="schema")
    source: str = Field(min_length=1)
    raw: dict[str, Any]

    @property
    def schema(self) -> str:
        return self.schema_

    @model_validator(mode="after")
    def validate_raw_reference_results(self) -> "GatewayConsistencyBaseline":
        if "reference_results_by_model" not in self.raw:
            raise ValueError("raw.reference_results_by_model is required")
        return self


class GatewayConsistencyExecutor(StrictContractModel):
    executor_id: str = Field(min_length=1)
    required: bool = True


class GatewayConsistencyDefaults(StrictContractModel):
    repeat_count: int = Field(ge=1)
    timeout_seconds: int = Field(ge=1)
    cost_limit: float = Field(ge=0)


class GatewayConsistencyModel(StrictContractModel):
    model_option_id: str = Field(min_length=1)
    display_name: str = Field(min_length=1)
    model_name: str = Field(min_length=1)


class GatewayConsistencyCase(StrictContractModel):
    task_case_id: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    external_id: str = Field(min_length=1)
    title: str
    baseline: GatewayConsistencyBaseline
    metadata: dict[str, Any] = Field(default_factory=dict)


class GatewayConsistencyTaskPack(StrictContractModel):
    schema_: Literal["cogeval.gateway_consistency.task_pack.v1"] = Field(alias="schema")
    task_pack_id: str = Field(min_length=1)
    display_name: str = Field(min_length=1)
    updated_at: str = Field(min_length=1)
    executor: GatewayConsistencyExecutor
    defaults: GatewayConsistencyDefaults
    models: list[GatewayConsistencyModel]
    cases: list[GatewayConsistencyCase]

    @property
    def schema(self) -> str:
        return self.schema_

    @model_validator(mode="after")
    def validate_non_empty_matrix(self) -> "GatewayConsistencyTaskPack":
        if not self.models:
            raise ValueError("task pack must include at least one model")
        if not self.cases:
            raise ValueError("task pack must include at least one case")
        return self


def validate_gateway_consistency_baseline(payload: Any) -> GatewayConsistencyBaseline:
    return GatewayConsistencyBaseline.model_validate(payload)


def validate_gateway_consistency_task_pack(payload: Any) -> GatewayConsistencyTaskPack:
    return GatewayConsistencyTaskPack.model_validate(payload)
