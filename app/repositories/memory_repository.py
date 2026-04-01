from datetime import date
from uuid import UUID

from pgvector.sqlalchemy import Vector
from sqlalchemy import and_, cast, desc, select
from sqlalchemy.orm import Session

from app.models.daily_summary import DailySummary
from app.models.memory_embedding import MemoryEmbedding
from app.models.memory_item import MemoryItem


class MemoryRepository:
    def create(self, db: Session, memory: MemoryItem) -> MemoryItem:
        db.add(memory)
        db.commit()
        db.refresh(memory)
        return memory

    def update(self, db: Session, memory: MemoryItem) -> MemoryItem:
        db.add(memory)
        db.commit()
        db.refresh(memory)
        return memory

    def get_by_id(self, db: Session, memory_id: UUID | str) -> MemoryItem | None:
        stmt = select(MemoryItem).where(MemoryItem.id == memory_id)
        return db.scalar(stmt)

    def list_recent_by_type(
        self,
        db: Session,
        owner_id: UUID | str,
        agent_id: UUID | str | None,
        memory_type: str,
        limit: int = 10,
    ) -> list[MemoryItem]:
        stmt = (
            select(MemoryItem)
            .where(MemoryItem.owner_id == owner_id)
            .where(MemoryItem.memory_type == memory_type)
            .where(MemoryItem.is_archived.is_(False))
            .order_by(desc(MemoryItem.timestamp_at))
            .limit(limit)
        )

        if agent_id:
            stmt = stmt.where(MemoryItem.agent_id == agent_id)

        return list(db.scalars(stmt).all())

    def search_by_type_basic(
        self,
        db: Session,
        owner_id: UUID | str,
        agent_id: UUID | str | None,
        memory_type: str,
        query: str,
        limit: int = 10,
    ) -> list[MemoryItem]:
        stmt = (
            select(MemoryItem)
            .where(MemoryItem.owner_id == owner_id)
            .where(MemoryItem.memory_type == memory_type)
            .where(MemoryItem.is_archived.is_(False))
            .where(
                (MemoryItem.summary.ilike(f"%{query}%")) |
                (MemoryItem.content.ilike(f"%{query}%")) |
                (MemoryItem.title.ilike(f"%{query}%"))
            )
            .order_by(desc(MemoryItem.timestamp_at))
            .limit(limit)
        )

        if agent_id:
            stmt = stmt.where(MemoryItem.agent_id == agent_id)

        return list(db.scalars(stmt).all())

    def vector_search_by_type(
        self,
        db: Session,
        owner_id: UUID | str,
        agent_id: UUID | str | None,
        memory_type: str,
        query_embedding: list[float],
        limit: int = 5,
    ) -> list[MemoryItem]:
        stmt = (
            select(MemoryItem)
            .join(MemoryEmbedding, MemoryEmbedding.memory_id == MemoryItem.id)
            .where(MemoryItem.owner_id == owner_id)
            .where(MemoryItem.memory_type == memory_type)
            .where(MemoryItem.is_archived.is_(False))
            .order_by(MemoryEmbedding.embedding.cosine_distance(cast(query_embedding, Vector(1536))))
            .limit(limit)
        )

        if agent_id:
            stmt = stmt.where(MemoryItem.agent_id == agent_id)

        return list(db.scalars(stmt).all())

    def list_by_type_global(
        self,
        db: Session,
        memory_type: str,
        limit: int = 1000,
        only_active: bool = True,
    ) -> list[MemoryItem]:
        stmt = select(MemoryItem).where(MemoryItem.memory_type == memory_type)

        if only_active:
            stmt = stmt.where(
                and_(
                    MemoryItem.is_archived.is_(False),
                    MemoryItem.status != "deleted",
                )
            )

        stmt = stmt.order_by(desc(MemoryItem.timestamp_at)).limit(limit)
        return list(db.scalars(stmt).all())

    def list_archive_candidates(
        self,
        db: Session,
        min_final_score: float = 0.25,
        limit: int = 1000,
    ) -> list[MemoryItem]:
        stmt = (
            select(MemoryItem)
            .where(MemoryItem.is_archived.is_(False))
            .where(MemoryItem.final_score < min_final_score)
            .order_by(MemoryItem.timestamp_at.asc())
            .limit(limit)
        )
        return list(db.scalars(stmt).all())

    def get_daily_summary(
        self,
        db: Session,
        owner_id: UUID | str,
        agent_id: UUID | str | None,
        summary_date: date,
    ) -> DailySummary | None:
        stmt = (
            select(DailySummary)
            .where(DailySummary.owner_id == owner_id)
            .where(DailySummary.summary_date == summary_date)
        )

        if agent_id:
            stmt = stmt.where(DailySummary.agent_id == agent_id)

        return db.scalar(stmt)

    def upsert_daily_summary(
        self,
        db: Session,
        owner_id: UUID | str,
        agent_id: UUID | str | None,
        summary_date: date,
        summary: str,
        topics: list[str],
        behavior_signal: str,
        memory_ids: list[str],
    ) -> DailySummary:
        existing = self.get_daily_summary(db, owner_id, agent_id, summary_date)

        if existing:
            existing.summary = summary
            existing.topics = topics
            existing.behavior_signal = behavior_signal
            existing.memory_ids = memory_ids
            db.add(existing)
            db.commit()
            db.refresh(existing)
            return existing

        new_item = DailySummary(
            owner_id=owner_id,
            agent_id=agent_id,
            summary_date=summary_date,
            summary=summary,
            topics=topics,
            behavior_signal=behavior_signal,
            memory_ids=memory_ids,
        )
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return new_item
