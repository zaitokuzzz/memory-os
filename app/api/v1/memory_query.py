from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.memory.orchestrator import MemoryOrchestrator
from app.repositories.archive_repository import ArchiveRepository
from app.schemas.memory_query import MemoryQueryRequest, MemoryQueryResponse
from app.services.archive_service import ArchiveService
from app.utils.validators import validate_owner_agent

router = APIRouter()
orchestrator = MemoryOrchestrator()
archive_repo = ArchiveRepository()
archive_service = ArchiveService()


@router.post("/query", response_model=MemoryQueryResponse)
def query_memory(payload: MemoryQueryRequest, db: Session = Depends(get_db)):
    validate_owner_agent(db, payload.owner_id, payload.agent_id)

    result = orchestrator.query(
        db=db,
        owner_id=payload.owner_id,
        agent_id=payload.agent_id,
        query=payload.query,
        max_tokens=payload.max_tokens,
        include_raw_if_needed=payload.include_raw_if_needed,
    )
    return MemoryQueryResponse(data=result, meta={})


@router.get("/archive/{memory_id}")
def get_archived_memory(memory_id: str, db: Session = Depends(get_db)):
    archive_item = archive_repo.get_by_memory_id(db, memory_id)
    if not archive_item:
        return {
            "status": "error",
            "error": {
                "code": "ARCHIVE_NOT_FOUND",
                "message": "Archive not found",
            },
        }

    payload = archive_service.load(archive_item.archive_uri)
    return {
        "status": "ok",
        "data": {
            "memory_id": memory_id,
            "archive_uri": archive_item.archive_uri,
            "payload": payload,
        },
        "meta": {},
    }
