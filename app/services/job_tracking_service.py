from datetime import datetime, timezone

from app.core.enums import JobStatus
from app.db.session import SessionLocal
from app.models.worker_job import WorkerJob
from app.repositories.worker_repository import WorkerRepository


class JobTrackingService:
    def __init__(self) -> None:
        self.repo = WorkerRepository()

    def create_job(self, job_type: str, payload: dict | None = None) -> str:
        db = SessionLocal()
        try:
            item = WorkerJob(
                job_type=job_type,
                status=JobStatus.QUEUED,
                payload=payload or {},
            )
            created = self.repo.create(db, item)
            return str(created.id)
        finally:
            db.close()

    def mark_running(self, job_id: str) -> None:
        db = SessionLocal()
        try:
            job = self.repo.get(db, job_id)
            if not job:
                return
            job.status = JobStatus.RUNNING
            job.started_at = datetime.now(timezone.utc)
            self.repo.update(db, job)
        finally:
            db.close()

    def mark_success(self, job_id: str) -> None:
        db = SessionLocal()
        try:
            job = self.repo.get(db, job_id)
            if not job:
                return
            job.status = JobStatus.SUCCESS
            job.finished_at = datetime.now(timezone.utc)
            self.repo.update(db, job)
        finally:
            db.close()

    def mark_failed(self, job_id: str, error_message: str) -> None:
        db = SessionLocal()
        try:
            job = self.repo.get(db, job_id)
            if not job:
                return
            job.status = JobStatus.FAILED
            job.error_message = error_message
            job.finished_at = datetime.now(timezone.utc)
            self.repo.update(db, job)
        finally:
            db.close()
