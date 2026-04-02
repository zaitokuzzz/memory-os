from sqlalchemy.orm import Session

from app.repositories.memory_repository import MemoryRepository


class EpisodicRetriever:
    def __init__(self) -> None:
        self.repo = MemoryRepository()

    def retrieve(self, db: Session, owner_id, agent_id, query: str, query_embedding: list[float], top_k: int = 5):
        text_results = self.repo.search_by_type_basic(
            db=db,
            owner_id=owner_id,
            agent_id=agent_id,
            memory_type="episodic",
            query=query,
            limit=top_k,
        )
        if text_results:
            return text_results

        vector_results = self.repo.vector_search_by_type(
            db=db,
            owner_id=owner_id,
            agent_id=agent_id,
            memory_type="episodic",
            query_embedding=query_embedding,
            limit=top_k,
        )
        if vector_results:
            return vector_results

        return self.repo.list_recent_by_type(
            db=db,
            owner_id=owner_id,
            agent_id=agent_id,
            memory_type="episodic",
            limit=top_k,
        )
