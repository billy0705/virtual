from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


ROW_ID_COLUMN = "__virtual_row_id"
SUPPORTED_CODECS = ("snappy", "gzip", "brotli", "lz4", "zstd")


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ResidualColumn(StrictModel):
    name: str = Field(min_length=1, max_length=128)
    purpose: str = Field(min_length=1, max_length=500)


class CandidateSpec(StrictModel):
    id: str = Field(
        min_length=1,
        max_length=128,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9_.-]*$",
    )
    summary: str = Field(min_length=1, max_length=1000)
    target_columns: list[str] = Field(min_length=1)
    reference_columns: list[str]
    residual_columns: list[ResidualColumn]
    compression_sql: str = Field(min_length=1)
    reconstruction_sql: str = Field(min_length=1)

    @field_validator("target_columns", "reference_columns")
    @classmethod
    def unique_column_names(cls, value: list[str]) -> list[str]:
        if any(not name or len(name) > 128 for name in value):
            raise ValueError("column names must contain between 1 and 128 characters")
        if len(value) != len(set(value)):
            raise ValueError("column names must be unique")
        return value

    @model_validator(mode="after")
    def validate_column_roles(self) -> "CandidateSpec":
        if set(self.target_columns) & set(self.reference_columns):
            raise ValueError("target and reference columns must not overlap")
        residual_names = [column.name for column in self.residual_columns]
        if len(residual_names) != len(set(residual_names)):
            raise ValueError("residual column names must be unique")
        if ROW_ID_COLUMN in set(self.target_columns + residual_names):
            raise ValueError(f"{ROW_ID_COLUMN} cannot be a target or residual column")
        return self


class CandidateBatch(StrictModel):
    candidates: list[CandidateSpec] = Field(max_length=5)


class CodecSize(StrictModel):
    base_bytes: int = Field(ge=0)
    compressed_bytes: int = Field(ge=0)
    savings_bytes: int
    savings_ratio: float


class Counterexample(StrictModel):
    row_id: int | None = None
    column: str | None = None
    expected: str
    actual: str


class CandidateEvaluation(StrictModel):
    candidate_id: str
    split: str
    valid: bool
    status: Literal[
        "valid",
        "invalid",
        "rejected",
        "timeout",
        "error",
        "skipped",
    ]
    reason: str | None = None
    rows: int = Field(default=0, ge=0)
    mismatch_count: int = Field(default=0, ge=0)
    output_columns: list[str] = Field(default_factory=list)
    auxiliary_columns: int = Field(default=0, ge=0)
    codec_sizes: dict[str, CodecSize] = Field(default_factory=dict)
    reconstruction_latency_ms: float | None = Field(default=None, ge=0)
    counterexamples: list[Counterexample] = Field(default_factory=list)
    elapsed_seconds: float = Field(default=0, ge=0)
    artifact_paths: dict[str, str] = Field(default_factory=dict)

    @property
    def snappy_savings_bytes(self) -> int:
        size = self.codec_sizes.get("snappy")
        return size.savings_bytes if size else 0


class UsageRecord(StrictModel):
    response_id: str | None = None
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    total_tokens: int = Field(default=0, ge=0)
    elapsed_seconds: float = Field(default=0, ge=0)


class StrategyRun(StrictModel):
    strategy: str
    model: str
    candidates: list[CandidateSpec] = Field(default_factory=list)
    usage: list[UsageRecord] = Field(default_factory=list)
    calls: int = Field(default=0, ge=0)
    tool_calls: int = Field(default=0, ge=0)
    elapsed_seconds: float = Field(default=0, ge=0)
    status: Literal["completed", "skipped", "error"] = "completed"
    reason: str | None = None
    lineage: dict[str, Any] = Field(default_factory=dict)
