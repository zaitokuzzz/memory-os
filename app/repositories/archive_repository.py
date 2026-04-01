from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.memory_archive import MemoryArchive


class ArchiveRepository:
    def create(self, db: Session, item: MemoryArchive) -> MemoryArchive:
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    def get_by_memory_id(self, db: Session, memory_id):
        stmt = select(MemoryArchive).where(MemoryArchive.memory_id == memory_id)
        return db.scalar(stmt)
