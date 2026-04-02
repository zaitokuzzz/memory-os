from sqlalchemy.orm import Session

from app.repositories.memory_repository import MemoryRepository


class KnowledgeRetriever:
    def __init__(self) -> None:
        self.repo = MemoryRepository()

    def retrieve(self, db: Session, owner_id, agent_id, query: str, query_embedding: list[float], top_k: int = 5):
        vector_results = self.repo.vector_search_by_type(
            db=db,
            owner_id=owner_id,
            agent_id=agent_id,
            memory_type="knowledge",
            query_embedding=query_embedding,
            limit=top_k,
        )

        lexical_results = self.repo.search_by_type_basic(
            db=db,
            owner_id=owner_id,
            agent_id=agent_id,
            memory_type="knowledge",
            query=query,
            limit=top_k,
        )

        unique = {}
        for item in vector_results + lexical_results:
            unique[str(item.id)] = item

        return list(unique.values())[:top_k]
