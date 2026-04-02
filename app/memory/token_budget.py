from app.services.tokenizer_service import TokenizerService


class TokenBudgetManager:
    def __init__(self) -> None:
        self.tokenizer = TokenizerService()

    def pack(self, ranked_candidates: list, max_tokens: int, include_raw_if_needed: bool = True) -> dict:
        selected = []
        total_tokens = 0

        for item in ranked_candidates:
            text = item.summary or item.content
            token_count = self.tokenizer.estimate(text)

            if total_tokens + token_count > max_tokens:
                continue

            selected.append({
                "memory_id": str(item.id),
                "memory_type": item.memory_type.value if hasattr(item.memory_type, "value") else item.memory_type,
                "summary": item.summary,
                "content": text,
                "score": getattr(item, "runtime_score", item.final_score),
            })
            total_tokens += token_count

        return {
            "selected_items": selected,
            "selected_ids": [x["memory_id"] for x in selected],
            "token_estimate": total_tokens,
        }
