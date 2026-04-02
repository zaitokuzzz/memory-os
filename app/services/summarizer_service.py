class SummarizerService:
    def generate_one_line_summary(self, user_input: str, ai_response: str, context_tags: list[str] | None = None) -> str:
        context_part = f" | tags: {', '.join(context_tags)}" if context_tags else ""
        combined = f"User: {user_input} | AI: {ai_response}{context_part}"
        return combined[:280]

    def generate_knowledge_summary(self, content: str) -> str:
        return content[:280]

    def generate_daily_summary(self, memory_summaries: list[str]) -> str:
        joined = " | ".join(memory_summaries)
        return joined[:500]

    def extract_topics(self, texts: list[str]) -> list[str]:
        words = set()
        for text in texts:
            for word in text.lower().split():
                cleaned = word.strip(".,!?()[]{}\"'")
                if len(cleaned) > 4:
                    words.add(cleaned)
        return list(words)[:10]

    def extract_behavior_signal(self, texts: list[str]) -> str:
        return "analitis"
