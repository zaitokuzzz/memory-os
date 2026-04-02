from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.enums import MemoryStatus, MemoryType, VerificationStatus
from app.models.browser_source import BrowserSource
from app.models.memory_item import MemoryItem
from app.repositories.browser_repository import BrowserRepository
from app.repositories.memory_repository import MemoryRepository
from app.schemas.memory_write import (
    BehaviorWriteRequest,
    BrowserWriteRequest,
    InteractionWriteRequest,
    KnowledgeWriteRequest,
    MemoryWriteResponse,
)
from app.services.scoring_service import ScoringService
from app.services.summarizer_service import SummarizerService
from app.utils.validators import validate_owner_agent
from app.workers.tasks.context_tasks import update_context_bundle_task
from app.workers.tasks.distill_tasks import distill_candidate_check_task
from app.workers.tasks.embedding_tasks import generate_embedding_task
from app.workers.tasks.summary_tasks import update_daily_summary_task

router = APIRouter()

memory_repo = MemoryRepository()
browser_repo = BrowserRepository()
summarizer = SummarizerService()
scoring = ScoringService()


@router.post("/write/interaction", response_model=MemoryWriteResponse)
def write_interaction(payload: InteractionWriteRequest, db: Session = Depends(get_db)):
    validate_owner_agent(db, payload.owner_id, payload.agent_id)

    timestamp = payload.timestamp_at or datetime.now(timezone.utc)

    summary = summarizer.generate_one_line_summary(
        user_input=payload.user_input,
        ai_response=payload.ai_response,
        context_tags=payload.context_tags,
    )

    importance_score = scoring.estimate_importance(
        user_input=payload.user_input,
        ai_response=payload.ai_response,
        context_tags=payload.context_tags,
    )

    memory = MemoryItem(
        owner_id=payload.owner_id,
        agent_id=payload.agent_id,
        memory_type=MemoryType.EPISODIC,
        subtype="raw_interaction",
        content=f"User: {payload.user_input}\nAI: {payload.ai_response}",
        summary=summary,
        timestamp_at=timestamp,
        importance_score=importance_score,
        confidence_score=0.9,
        source_weight=0.8,
        status=MemoryStatus.PENDING_EMBEDDING,
        metadata_json={
            "user_input": payload.user_input,
            "ai_response": payload.ai_response,
            "context_tags": payload.context_tags,
            "source": "conversation",
        },
    )

    created = memory_repo.create(db, memory)

    generate_embedding_task.delay(str(created.id))
    update_daily_summary_task.delay(
        str(payload.owner_id),
        str(payload.agent_id) if payload.agent_id else None,
        timestamp.date().isoformat(),
    )
    update_context_bundle_task.delay(str(created.id))
    distill_candidate_check_task.delay(str(created.id))

    return MemoryWriteResponse(
        data={
            "memory_id": str(created.id),
            "summary": created.summary,
            "memory_type": created.memory_type.value,
            "status": created.status.value,
        }
    )


@router.post("/write/knowledge", response_model=MemoryWriteResponse)
def write_knowledge(payload: KnowledgeWriteRequest, db: Session = Depends(get_db)):
    validate_owner_agent(db, payload.owner_id, payload.agent_id)

    timestamp = payload.timestamp_at or datetime.now(timezone.utc)
    summary = payload.summary or summarizer.generate_knowledge_summary(payload.content)

    memory = MemoryItem(
        owner_id=payload.owner_id,
        agent_id=payload.agent_id,
        memory_type=MemoryType.KNOWLEDGE,
        subtype=payload.subtype,
        title=payload.title,
        content=payload.content,
        summary=summary,
        timestamp_at=timestamp,
        importance_score=0.95,
        confidence_score=payload.confidence_score,
        source_weight=1.0,
        status=MemoryStatus.PENDING_EMBEDDING,
        metadata_json={
            "category": payload.category,
            "immutable": payload.immutable,
            "source_type": "curated_knowledge",
        },
    )

    created = memory_repo.create(db, memory)
    generate_embedding_task.delay(str(created.id))

    return MemoryWriteResponse(
        data={
            "memory_id": str(created.id),
            "summary": created.summary,
            "memory_type": created.memory_type.value,
            "status": created.status.value,
        }
    )


@router.post("/write/browser", response_model=MemoryWriteResponse)
def write_browser(payload: BrowserWriteRequest, db: Session = Depends(get_db)):
    validate_owner_agent(db, payload.owner_id, payload.agent_id)

    timestamp = payload.retrieved_at or datetime.now(timezone.utc)
    summary = payload.content[:280]

    memory = MemoryItem(
        owner_id=payload.owner_id,
        agent_id=payload.agent_id,
        memory_type=MemoryType.BROWSER,
        subtype=payload.subtype,
        title=payload.title,
        content=payload.content,
        summary=summary,
        timestamp_at=timestamp,
        importance_score=0.5,
        confidence_score=payload.reliability_score,
        source_weight=0.45 if payload.verification_status == VerificationStatus.UNVERIFIED else 0.7,
        status=MemoryStatus.PENDING_EMBEDDING,
        metadata_json={
            "url": payload.url,
            "domain": payload.domain,
            "verification_status": payload.verification_status.value,
            "source_type": "browser",
        },
    )

    created = memory_repo.create(db, memory)

    browser_source = BrowserSource(
        memory_id=created.id,
        url=payload.url,
        domain=payload.domain,
        retrieved_at=timestamp,
        reliability_score=payload.reliability_score,
        verification_status=payload.verification_status,
        content_hash=None,
    )
    browser_repo.create(db, browser_source)

    generate_embedding_task.delay(str(created.id))

    return MemoryWriteResponse(
        data={
            "memory_id": str(created.id),
            "summary": created.summary,
            "memory_type": created.memory_type.value,
            "status": created.status.value,
        }
    )


@router.post("/write/behavior", response_model=MemoryWriteResponse)
def write_behavior(payload: BehaviorWriteRequest, db: Session = Depends(get_db)):
    validate_owner_agent(db, payload.owner_id, payload.agent_id)

    memory = MemoryItem(
        owner_id=payload.owner_id,
        agent_id=payload.agent_id,
        memory_type=MemoryType.BEHAVIOR,
        subtype=payload.subtype,
        title="Behavior memory",
        content=payload.pattern,
        summary=payload.pattern,
        timestamp_at=datetime.now(timezone.utc),
        importance_score=payload.frequency,
        confidence_score=payload.confidence,
        source_weight=0.75,
        status=MemoryStatus.PENDING_EMBEDDING,
        metadata_json={
            "tone_preference": payload.tone_preference,
            "pattern_type": payload.subtype,
        },
    )

    created = memory_repo.create(db, memory)
    generate_embedding_task.delay(str(created.id))

    return MemoryWriteResponse(
        data={
            "memory_id": str(created.id),
            "summary": created.summary,
            "memory_type": created.memory_type.value,
            "status": created.status.value,
        }
    )
