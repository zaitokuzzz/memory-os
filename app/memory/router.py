from app.core.enums import QueryType


class MemoryRouter:
    def get_dynamic_weights(self, query_type: QueryType) -> dict:
        if query_type == QueryType.TEMPORAL:
            return {"episodic": 5, "semantic": 2, "knowledge": 0, "behavior": 1, "browser": 0}
        if query_type == QueryType.FACTUAL:
            return {"episodic": 0, "semantic": 2, "knowledge": 5, "behavior": 0, "browser": 1}
        if query_type == QueryType.CONCEPTUAL:
            return {"episodic": 2, "semantic": 5, "knowledge": 3, "behavior": 0, "browser": 0}
        if query_type == QueryType.PERSONAL:
            return {"episodic": 2, "semantic": 1, "knowledge": 0, "behavior": 3, "browser": 0}
        if query_type == QueryType.EXTERNAL_RECENT:
            return {"episodic": 0, "semantic": 1, "knowledge": 1, "behavior": 0, "browser": 5}
        return {"episodic": 3, "semantic": 3, "knowledge": 2, "behavior": 1, "browser": 1}
