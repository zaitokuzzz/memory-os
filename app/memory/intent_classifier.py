from app.core.enums import QueryType


class IntentClassifier:
    def classify(self, query: str) -> QueryType:
        q = query.lower()

        if any(word in q for word in ["kemarin", "tanggal", "jam", "bulan", "tahun", "waktu itu"]):
            return QueryType.TEMPORAL

        if any(word in q for word in ["apa itu", "definisi", "rumus", "siapa"]):
            return QueryType.FACTUAL

        if any(word in q for word in ["gaya saya", "preferensi saya", "kebiasaan saya"]):
            return QueryType.PERSONAL

        if any(word in q for word in ["browser", "web", "internet", "terbaru", "berita"]):
            return QueryType.EXTERNAL_RECENT

        if any(word in q for word in ["cara", "bagaimana", "pipeline", "arsitektur", "konsep"]):
            return QueryType.CONCEPTUAL

        return QueryType.HYBRID
