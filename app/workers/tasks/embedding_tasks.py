from app.core.config import settings
from app.core.enums import MemoryStatus
from app.db.session import SessionLocal
from app.repositories.embedding_repository import EmbeddingRepository
from app.repositories.memory_repository import MemoryRepository
from app.services.embedding_service import EmbeddingService
from app.services.job_tracking_service import JobTrackingService
from app.workers.celery_app import celery_app

embedding_service = EmbeddingService()
memory_repo = MemoryRepository()
embedding_repo = EmbeddingRepository()
job_tracker = JobTrackingService()


def select_embedding_text(memory) -> str:
    if memory.summary:
        return memory.summary
    return memory.content[:2000]


@celery_app.task(name="generate_embedding")
def generate_embedding_task(memory_id: str) -> dict:
    job_id = job_tracker.create_job("generate_embedding", {"memory_id": memory_id})
    job_tracker.mark_running(job_id)

    db = SessionLocal()
    try:
        memory = memory_repo.get_by_id(db, memory_id)
        if not memory:
            job_tracker.mark_failed(job_id, "memory_not_found")
            return {"status": "not_found", "memory_id": memory_id}

        text = select_embedding_text(memory)
        vector = embedding_service.embed(text)

        embedding_repo.upsert(
            db=db,
            memory_id=memory.id,
            embedding_model=settings.embedding_model,
            embedding=vector,
        )

        memory.status = MemoryStatus.ACTIVE
        memory_repo.update(db, memory)

        job_tracker.mark_success(job_id)
        return {"status": "ok", "memory_id": memory_id, "job_id": job_id}
    except Exception as e:
        job_tracker.mark_failed(job_id, str(e))
        raise
    finally:
        db.close()
