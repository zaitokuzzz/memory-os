from app.db.session import SessionLocal
from app.repositories.memory_repository import MemoryRepository
from app.services.job_tracking_service import JobTrackingService
from app.workers.celery_app import celery_app

memory_repo = MemoryRepository()
job_tracker = JobTrackingService()


@celery_app.task(name="apply_feedback_update")
def apply_feedback_update_task(memory_id: str, helpful_score: float | None, used: bool = True) -> dict:
    job_id = job_tracker.create_job("apply_feedback_update", {"memory_id": memory_id})
    job_tracker.mark_running(job_id)

    db = SessionLocal()
    try:
        memory = memory_repo.get_by_id(db, memory_id)
        if not memory:
            job_tracker.mark_failed(job_id, "memory_not_found")
            return {"status": "not_found", "memory_id": memory_id}

        delta = 0.0
        if used:
            delta += 0.05
        if helpful_score is not None:
            delta += helpful_score * 0.1

        new_score = max(0.0, min(1.0, memory.importance_score + delta))
        memory.importance_score = new_score
        memory_repo.update(db, memory)

        job_tracker.mark_success(job_id)
        return {"status": "ok", "memory_id": memory_id, "importance_score": new_score, "job_id": job_id}
    except Exception as e:
        job_tracker.mark_failed(job_id, str(e))
        raise
    finally:
        db.close()
