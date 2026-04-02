import random

from app.core.config import settings


class EmbeddingService:
    def embed(self, text: str) -> list[float]:
        random.seed(hash(text) % 10_000_000)
        return [random.uniform(-1, 1) for _ in range(settings.embedding_dim)]

    def embed_query(self, text: str) -> list[float]:
        return self.embed(text)
