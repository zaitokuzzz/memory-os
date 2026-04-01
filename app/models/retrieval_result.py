import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RetrievalResult(Base):
    __tablename__ = "retrieval_results"
    __table_args__ = (
        UniqueConstraint("query_id", "memory_id", name="uq_retrieval_results_query_memory"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("retrieval_queries.id", ondelete="CASCADE"), nullable=False)
    memory_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("memory_items.id", ondelete="CASCADE"), nullable=False)
    rank_position: Mapped[int] = mapped_column(Integer, nullable=False)
    relevance_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, server_default="0.0")
    final_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, server_default="0.0")
    included_in_context: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    was_expanded: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
