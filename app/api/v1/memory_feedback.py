from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.retrieval_feedback import RetrievalFeedback
from app.repositories.retrieval_repository import RetrievalRepository
from app.schemas.memory_feedback import MemoryFeedbackRequest, MemoryFeedbackResponse
from app.workers.tasks.feedback_tasks import apply_feedback_update_task

router = APIRouter()
retrieval_repo = RetrievalRepository()


@router.post("/feedback", response_model=MemoryFeedbackResponse)
def submit_feedback(payload: MemoryFeedbackRequest, db: Session = Depends(get_db)):
    item = RetrievalFeedback(
        query_id=payload.query_id,
        memory_id=payload.memory_id,
        used=payload.used,
        helpful_score=payload.helpful_score,
        feedback_note=payload.feedback_note,
    )
    created = retrieval_repo.create_feedback(db, item)

    apply_feedback_update_task.delay(
        str(payload.memory_id),
        payload.helpful_score,
        payload.used,
    )

    return MemoryFeedbackResponse(
        data={
            "feedback_id": str(created.id),
            "query_id": str(created.query_id),
            "memory_id": str(created.memory_id),
            "used": created.used,
            "helpful_score": created.helpful_score,
        }
    )
