from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.memory_embedding import MemoryEmbedding


class EmbeddingRepository:
    def upsert(
        self,
        db: Session,
        memory_id,
        embedding_model: str,
        embedding: list[float],
    ) -> MemoryEmbedding:
        stmt = select(MemoryEmbedding).where(
            MemoryEmbedding.memory_id == memory_id,
            MemoryEmbedding.embedding_model == embedding_model,
        )
        existing = db.scalar(stmt)

        if existing:
            existing.embedding = embedding
            db.add(existing)
            db.commit()
            db.refresh(existing)
            return existing

        item = MemoryEmbedding(
            memory_id=memory_id,
            embedding_model=embedding_model,
            embedding=embedding,
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item
