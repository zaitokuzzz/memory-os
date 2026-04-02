from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.core.enums import VerificationStatus


class InteractionWriteRequest(BaseModel):
    owner_id: UUID
    agent_id: UUID | None = None
    user_input: str = Field(..., min_length=1)
    ai_response: str = Field(..., min_length=1)
    timestamp_at: datetime | None = None
    context_tags: list[str] = Field(default_factory=list)


class KnowledgeWriteRequest(BaseModel):
    owner_id: UUID
    agent_id: UUID | None = None
    title: str | None = None
    content: str = Field(..., min_length=1)
    summary: str | None = None
    subtype: str = "fact"
    category: str | None = None
    confidence_score: float = 1.0
    immutable: bool = True
    timestamp_at: datetime | None = None


class BrowserWriteRequest(BaseModel):
    owner_id: UUID
    agent_id: UUID | None = None
    title: str | None = None
    content: str = Field(..., min_length=1)
    subtype: str = "web_article"
    url: str
    domain: str
    reliability_score: float = 0.5
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED
    retrieved_at: datetime | None = None


class BehaviorWriteRequest(BaseModel):
    owner_id: UUID
    agent_id: UUID | None = None
    pattern: str
    tone_preference: str | None = None
    frequency: float = 0.5
    confidence: float = 0.8
    subtype: str = "user_style"


class MemoryWriteResponse(BaseModel):
    status: str = "ok"
    data: dict[str, Any]
    meta: dict[str, Any] = Field(default_factory=dict)
