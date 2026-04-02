def normalize_text(text: str) -> str:
    return " ".join(text.strip().lower().split())


def make_bundle_key(text: str, max_words: int = 6) -> str:
    words = normalize_text(text).split()
    return "_".join(words[:max_words]) if words else "general"
