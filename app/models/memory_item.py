import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import MemoryStatus, MemoryType
from app.db.base import Base


class MemoryItem(Base):
    __tablename__ = "memory_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("owners.id", ondelete="CASCADE"), nullable=False)
    agent_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="SET NULL"), nullable=True)

    memory_type: Mapped[MemoryType] = mapped_column(Enum(MemoryType, name="memory_type_enum"), nullable=False)
    subtype: Mapped[str] = mapped_column(Text, nullable=False)

    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    timestamp_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    importance_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.5, server_default="0.5")
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.5, server_default="0.5")
    relevance_hint: Mapped[float | None] = mapped_column(Float, nullable=True)
    decay_score: Mapped[float] = mapped_column(Float, nullable=False, default=1.0, server_default="1.0")
    source_weight: Mapped[float] = mapped_column(Float, nullable=False, default=1.0, server_default="1.0")
    final_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, server_default="0.0")

    status: Mapped[MemoryStatus] = mapped_column(
        Enum(MemoryStatus, name="memory_status_enum"),
        nullable=False,
        default=MemoryStatus.ACTIVE,
        server_default=MemoryStatus.ACTIVE.value,
    )
    is_archived: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")

    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")
    parent_memory_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("memory_items.id", ondelete="SET NULL"),
        nullable=True,
    )

    token_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    access_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    last_accessed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    metadata_json: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict, server_default="{}")

    owner = relationship("Owner", back_populates="memory_items")
    agent = relationship("Agent", back_populates="memory_items")
