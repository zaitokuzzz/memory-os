import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SemanticCluster(Base):
    __tablename__ = "semantic_clusters"
    __table_args__ = (
        UniqueConstraint("owner_id", "agent_id", "cluster_key", name="uq_semantic_clusters_owner_agent_key"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("owners.id", ondelete="CASCADE"), nullable=False)
    agent_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="SET NULL"), nullable=True)
    cluster_key: Mapped[str] = mapped_column(Text, nullable=False)
    memory_ids: Mapped[list] = mapped_column(JSONB, nullable=False, default=list, server_default="[]")
    centroid_memory_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("memory_items.id", ondelete="SET NULL"), nullable=True)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.5, server_default="0.5")
    cluster_size: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    last_distilled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
