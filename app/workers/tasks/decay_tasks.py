from app.db.session import SessionLocal
from app.repositories.memory_repository import MemoryRepository
from app.services.job_tracking_service import JobTrackingService
from app.services.scoring_service import ScoringService
from app.workers.celery_app import celery_app

memory_repo = MemoryRepository()
scoring = ScoringService()
job_tracker = JobTrackingService()


@celery_app.task(name="run_decay")
def run_decay_task() -> dict:
    job_id = job_tracker.create_job("run_decay", {})
    job_tracker.mark_running(job_id)

    db = SessionLocal()
    try:
        updated_count = 0

        for memory_type in ["episodic", "semantic", "knowledge", "behavior", "browser"]:
            memories = memory_repo.list_by_type_global(
                db=db,
                memory_type=memory_type,
                limit=1000,
                only_active=True,
            )
            for memory in memories:
                decay = scoring.compute_decay(memory.memory_type.value, memory.timestamp_at)
                memory.decay_score = decay
                memory.final_score = (
                    memory.importance_score *
                    memory.confidence_score *
                    memory.source_weight *
                    decay
                )
                memory_repo.update(db, memory)
                updated_count += 1

        job_tracker.mark_success(job_id)
        return {"status": "ok", "updated_count": updated_count, "job_id": job_id}
    except Exception as e:
        job_tracker.mark_failed(job_id, str(e))
        raise
    finally:
        db.close()
