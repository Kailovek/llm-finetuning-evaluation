from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field


class DatasetSummary(BaseModel):
    id: UUID
    name: str
    format: str
    record_count: int
    train_count: int
    validation_count: int
    duplicate_count: int
    rejected_count: int
    statistics: dict[str, float | int]
    created_at: datetime


class TrainingRequest(BaseModel):
    dataset_id: UUID
    mode: Literal["validation_only", "lora"] = "validation_only"
    model_path: str | None = None


class EvaluationRequest(BaseModel):
    dataset_id: UUID
    candidate: Literal["demo-rule"] = "demo-rule"


class JobResponse(BaseModel):
    task_id: UUID
    kind: Literal["training", "evaluation"]
    status: Literal["succeeded", "failed"]
    progress: int = Field(ge=0, le=100)
    result: dict[str, Any]
    created_at: datetime


class InferenceRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=4000)
    model_ref: str = "demo-rule"


class InferenceResponse(BaseModel):
    text: str
    provider: str
    latency_ms: float
    structured: dict[str, Any]
