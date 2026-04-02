from sqlalchemy.orm import Session

from app.repositories.memory_repository import MemoryRepository


class BrowserRetriever:
    def __init__(self) -> None:
        self.repo = MemoryRepository()

    def retrieve(self, db: Session, owner_id, agent_id, query: str, query_embedding: list[float], top_k: int = 3):
        return self.repo.vector_search_by_type(
            db=db,
            owner_id=owner_id,
            agent_id=agent_id,
            memory_type="browser",
            query_embedding=query_embedding,
            limit=top_k,
        )
