from datetime import datetime, timezone

from app.core.enums import MemoryType


class ScoringService:
    def estimate_importance(self, user_input: str, ai_response: str, context_tags: list[str] | None = None) -> float:
        score = 0.5

        if context_tags:
            score += min(0.2, len(context_tags) * 0.03)

        if len(user_input) > 150:
            score += 0.1

        lowered = user_input.lower()
        if "ingat" in lowered or "penting" in lowered:
            score += 0.15

        return min(score, 1.0)

    def compute_decay(self, memory_type: str, timestamp_at: datetime) -> float:
        now = datetime.now(timezone.utc)
        age_days = max(0, (now - timestamp_at).days)

        lambdas = {
            MemoryType.EPISODIC.value: 0.08,
            MemoryType.SEMANTIC.value: 0.01,
            MemoryType.BEHAVIOR.value: 0.02,
            MemoryType.BROWSER.value: 0.05,
            MemoryType.KNOWLEDGE.value: 0.001,
        }
        decay_lambda = lambdas.get(memory_type, 0.05)
        return float(2.718281828 ** (-decay_lambda * age_days))

    def compute_final_score(
        self,
        relevance: float,
        importance: float,
        confidence: float,
        decay: float,
        source_weight: float,
    ) -> float:
        return relevance * importance * confidence * decay * source_weight
