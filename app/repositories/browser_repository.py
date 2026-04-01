from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.browser_source import BrowserSource


class BrowserRepository:
    def create(self, db: Session, item: BrowserSource) -> BrowserSource:
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    def get_by_memory_id(self, db: Session, memory_id):
        stmt = select(BrowserSource).where(BrowserSource.memory_id == memory_id)
        return db.scalar(stmt)
