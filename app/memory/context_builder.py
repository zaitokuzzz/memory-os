class ContextBuilder:
    def build(self, selected_items: list[dict]) -> str:
        grouped: dict[str, list[dict]] = {
            "knowledge": [],
            "semantic": [],
            "episodic": [],
            "behavior": [],
            "browser": [],
        }

        for item in selected_items:
            grouped[item["memory_type"]].append(item)

        parts: list[str] = []

        if grouped["knowledge"]:
            parts.append("[KNOWLEDGE]")
            parts.extend(f"- {item['content']}" for item in grouped["knowledge"])

        if grouped["semantic"]:
            parts.append("\n[SEMANTIC MEMORY]")
            parts.extend(f"- {item['content']}" for item in grouped["semantic"])

        if grouped["episodic"]:
            parts.append("\n[EPISODIC MEMORY]")
            parts.extend(f"- {item['content']}" for item in grouped["episodic"])

        if grouped["behavior"]:
            parts.append("\n[BEHAVIOR MEMORY]")
            parts.extend(f"- {item['content']}" for item in grouped["behavior"])

        if grouped["browser"]:
            parts.append("\n[BROWSER EVIDENCE]")
            parts.extend(f"- {item['content']}" for item in grouped["browser"])

        return "\n".join(parts)
