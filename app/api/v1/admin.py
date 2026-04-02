from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.repositories.worker_repository import WorkerRepository

router = APIRouter()
worker_repo = WorkerRepository()


@router.get("/admin/jobs")
def list_worker_jobs(db: Session = Depends(get_db)):
    jobs = worker_repo.list_recent(db, limit=50)
    return {
        "status": "ok",
        "data": {
            "jobs": [
                {
                    "id": str(job.id),
                    "job_type": job.job_type,
                    "status": job.status.value,
                    "created_at": job.created_at,
                    "started_at": job.started_at,
                    "finished_at": job.finished_at,
                    "error_message": job.error_message,
                }
                for job in jobs
            ]
        },
        "meta": {},
    }
