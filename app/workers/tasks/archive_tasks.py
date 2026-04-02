from datetime import datetime, timezone

from app.core.enums import MemoryStatus
from app.db.session import SessionLocal
from app.models.memory_archive import MemoryArchive
from app.repositories.archive_repository import ArchiveRepository
from app.repositories.memory_repository import MemoryRepository
from app.services.archive_service import ArchiveService
from app.services.job_tracking_service import JobTrackingService
from app.workers.celery_app import celery_app

memory_repo = MemoryRepository()
archive_repo = ArchiveRepository()
archive_service = ArchiveService()
job_tracker = JobTrackingService()


@celery_app.task(name="run_archive")
def run_archive_task() -> dict:
    job_id = job_tracker.create_job("run_archive", {})
    job_tracker.mark_running(job_id)

    db = SessionLocal()
    try:
        archived_count = 0
        now = datetime.now(timezone.utc)

        memories = memory_repo.list_archive_candidates(
            db=db,
            min_final_score=0.25,
            limit=1000,
        )

        for memory in memories:
            age_days = (now - memory.timestamp_at).days
            if age_days < 60 or memory.is_archived:
                continue

            payload = {
                "id": str(memory.id),
                "summary": memory.summary,
                "content": memory.content,
                "metadata": memory.metadata_json,
            }
            archive_uri = archive_service.store(memory.id, payload)

            archive_item = MemoryArchive(
                memory_id=memory.id,
                archive_uri=archive_uri,
                archive_reason="age_and_low_score",
                storage_provider="local",
                checksum=None,
                metadata_json={},
            )
            archive_repo.create(db, archive_item)

            memory.is_archived = True
            memory.status = MemoryStatus.ARCHIVED
            memory_repo.update(db, memory)
            archived_count += 1

        job_tracker.mark_success(job_id)
        return {"status": "ok", "archived_count": archived_count, "job_id": job_id}
    except Exception as e:
        job_tracker.mark_failed(job_id, str(e))
        raise
    finally:
        db.close()
