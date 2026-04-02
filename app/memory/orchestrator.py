from sqlalchemy.orm import Session

from app.memory.context_builder import ContextBuilder
from app.memory.intent_classifier import IntentClassifier
from app.memory.retrieval.behavior import BehaviorRetriever
from app.memory.retrieval.browser import BrowserRetriever
from app.memory.retrieval.episodic import EpisodicRetriever
from app.memory.retrieval.knowledge import KnowledgeRetriever
from app.memory.retrieval.semantic import SemanticRetriever
from app.memory.router import MemoryRouter
from app.memory.token_budget import TokenBudgetManager
from app.models.retrieval_query import RetrievalQuery
from app.models.retrieval_result import RetrievalResult
from app.repositories.retrieval_repository import RetrievalRepository
from app.services.embedding_service import EmbeddingService
from app.services.scoring_service import ScoringService


class MemoryOrchestrator:
    def __init__(self) -> None:
        self.intent_classifier = IntentClassifier()
        self.router = MemoryRouter()
        self.context_builder = ContextBuilder()
        self.token_budget = TokenBudgetManager()
        self.scoring = ScoringService()
        self.embedding_service = EmbeddingService()
        self.retrieval_repo = RetrievalRepository()

        self.episodic = EpisodicRetriever()
        self.semantic = SemanticRetriever()
        self.knowledge = KnowledgeRetriever()
        self.behavior = BehaviorRetriever()
        self.browser = BrowserRetriever()

    def query(self, db: Session, owner_id, agent_id, query: str, max_tokens: int, include_raw_if_needed: bool):
        query_type = self.intent_classifier.classify(query)
        weights = self.router.get_dynamic_weights(query_type)
        query_embedding = self.embedding_service.embed_query(query)

        query_record = RetrievalQuery(
            owner_id=owner_id,
            agent_id=agent_id,
            query_text=query,
            query_type=query_type,
            max_tokens=max_tokens,
            metadata_json={},
        )
        self.retrieval_repo.create_query(db, query_record)

        candidates = []

        if weights["episodic"] > 0:
            candidates.extend(self.episodic.retrieve(db, owner_id, agent_id, query, query_embedding, weights["episodic"]))

        if weights["semantic"] > 0:
            candidates.extend(self.semantic.retrieve(db, owner_id, agent_id, query, query_embedding, weights["semantic"]))

        if weights["knowledge"] > 0:
            candidates.extend(self.knowledge.retrieve(db, owner_id, agent_id, query, query_embedding, weights["knowledge"]))

        if weights["behavior"] > 0:
            candidates.extend(self.behavior.retrieve(db, owner_id, agent_id, query, weights["behavior"]))

        if weights["browser"] > 0:
            candidates.extend(self.browser.retrieve(db, owner_id, agent_id, query, query_embedding, weights["browser"]))

        unique = {}
        for item in candidates:
            unique[str(item.id)] = item

        ranked = []
        lowered_query = query.lower()

        for item in unique.values():
            haystack = f"{item.summary or ''} {item.content or ''}".lower()
            relevance = 0.85 if lowered_query in haystack else 0.65

            decay = self.scoring.compute_decay(
                memory_type=item.memory_type.value if hasattr(item.memory_type, "value") else item.memory_type,
                timestamp_at=item.timestamp_at,
            )

            item.runtime_score = self.scoring.compute_final_score(
                relevance=relevance,
                importance=item.importance_score,
                confidence=item.confidence_score,
                decay=decay,
                source_weight=item.source_weight,
            )
            ranked.append(item)

        ranked.sort(key=lambda x: x.runtime_score, reverse=True)

        packed = self.token_budget.pack(
            ranked_candidates=ranked,
            max_tokens=max_tokens,
            include_raw_if_needed=include_raw_if_needed,
        )

        selected_ids = set(packed["selected_ids"])

        for idx, item in enumerate(ranked, start=1):
            relevance_score = 0.85 if lowered_query in f"{item.summary or ''} {item.content or ''}".lower() else 0.65
            row = RetrievalResult(
                query_id=query_record.id,
                memory_id=item.id,
                rank_position=idx,
                relevance_score=relevance_score,
                final_score=item.runtime_score,
                included_in_context=str(item.id) in selected_ids,
                was_expanded=False,
            )
            self.retrieval_repo.create_result(db, row)

        context_pack = self.context_builder.build(packed["selected_items"])

        return {
            "query_id": str(query_record.id),
            "query_type": query_type.value,
            "results": packed["selected_items"],
            "context_pack": context_pack,
            "token_estimate": packed["token_estimate"],
        }
