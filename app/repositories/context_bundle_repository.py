from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.context_bundle import ContextBundle


class ContextBundleRepository:
    def get_by_key(self, db: Session, owner_id, agent_id, bundle_key: str) -> ContextBundle | None:
        stmt = (
            select(ContextBundle)
            .where(ContextBundle.owner_id == owner_id)
            .where(ContextBundle.bundle_key == bundle_key)
        )

        if agent_id:
            stmt = stmt.where(ContextBundle.agent_id == agent_id)

        return db.scalar(stmt)

    def create(self, db: Session, item: ContextBundle) -> ContextBundle:
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    def update(self, db: Session, item: ContextBundle) -> ContextBundle:
        db.add(item)
        db.commit()
        db.refresh(item)
        return item
