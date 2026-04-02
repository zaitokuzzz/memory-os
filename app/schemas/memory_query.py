from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class MemoryQueryRequest(BaseModel):
    owner_id: UUID
    agent_id: UUID | None = None
    query: str = Field(..., min_length=1)
    max_tokens: int = 1200
    include_raw_if_needed: bool = True


class MemoryQueryResponse(BaseModel):
    status: str = "ok"
    data: dict[str, Any]
    meta: dict[str, Any] = Field(default_factory=dict)
