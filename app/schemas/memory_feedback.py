from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class MemoryFeedbackRequest(BaseModel):
    query_id: UUID
    memory_id: UUID
    used: bool = True
    helpful_score: float | None = Field(default=None, ge=0.0, le=1.0)
    feedback_note: str | None = None


class MemoryFeedbackResponse(BaseModel):
    status: str = "ok"
    data: dict[str, Any]
    meta: dict[str, Any] = Field(default_factory=dict)
