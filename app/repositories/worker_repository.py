from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.worker_job import WorkerJob


class WorkerRepository:
    def create(self, db: Session, item: WorkerJob) -> WorkerJob:
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    def get(self, db: Session, job_id):
        stmt = select(WorkerJob).where(WorkerJob.id == job_id)
        return db.scalar(stmt)

    def update(self, db: Session, item: WorkerJob) -> WorkerJob:
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    def list_recent(self, db: Session, limit: int = 20):
        stmt = select(WorkerJob).order_by(desc(WorkerJob.created_at)).limit(limit)
        return list(db.scalars(stmt).all())
