from sqlalchemy.orm import Session

from app.repositories.memory_repository import MemoryRepository


class BehaviorRetriever:
    def __init__(self) -> None:
        self.repo = MemoryRepository()

    def retrieve(self, db: Session, owner_id, agent_id, query: str, top_k: int = 3):
        results = self.repo.search_by_type_basic(
            db=db,
            owner_id=owner_id,
            agent_id=agent_id,
            memory_type="behavior",
            query=query,
            limit=top_k,
        )
        if results:
            return results

        return self.repo.list_recent_by_type(
            db=db,
            owner_id=owner_id,
            agent_id=agent_id,
            memory_type="behavior",
            limit=top_k,
        )
