from datetime import datetime, timezone

from app.core.enums import MemoryStatus, MemoryType
from app.db.session import SessionLocal
from app.models.agent import Agent
from app.models.memory_item import MemoryItem
from app.models.owner import Owner


def main():
    db = SessionLocal()
    try:
        owner = Owner(display_name="Default Owner", external_ref="default-owner")
        db.add(owner)
        db.commit()
        db.refresh(owner)

        agent = Agent(owner_id=owner.id, name="Default Agent", description="Seed agent")
        db.add(agent)
        db.commit()
        db.refresh(agent)

        now = datetime.now(timezone.utc)

        items = [
            MemoryItem(
                owner_id=owner.id,
                agent_id=agent.id,
                memory_type=MemoryType.KNOWLEDGE,
                subtype="fact",
                title="Newton Second Law",
                content="F = m × a",
                summary="Hukum kedua Newton: F = m × a",
                timestamp_at=now,
                importance_score=0.95,
                confidence_score=1.0,
                source_weight=1.0,
                status=MemoryStatus.ACTIVE,
                metadata_json={"category": "physics"},
            ),
            MemoryItem(
                owner_id=owner.id,
                agent_id=agent.id,
                memory_type=MemoryType.EPISODIC,
                subtype="raw_interaction",
                content="User: kita bahas sistem memori AI\nAI: kita susun modular",
                summary="Diskusi sistem memori AI modular",
                timestamp_at=now,
                importance_score=0.8,
                confidence_score=0.9,
                source_weight=0.8,
                status=MemoryStatus.ACTIVE,
                metadata_json={"context_tags": ["ai", "memory"]},
            ),
            MemoryItem(
                owner_id=owner.id,
                agent_id=agent.id,
                memory_type=MemoryType.BEHAVIOR,
                subtype="user_style",
                title="Behavior memory",
                content="User suka eksplorasi sistem kompleks dengan penjelasan formal dan langsung.",
                summary="User suka eksplorasi sistem kompleks, formal dan langsung.",
                timestamp_at=now,
                importance_score=0.7,
                confidence_score=0.85,
                source_weight=0.75,
                status=MemoryStatus.ACTIVE,
                metadata_json={"tone_preference": "formal_direct"},
            ),
        ]

        db.add_all(items)
        db.commit()

        print("Seed data inserted successfully.")
        print(f"owner_id={owner.id}")
        print(f"agent_id={agent.id}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
