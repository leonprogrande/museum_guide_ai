import unicodedata


def normalize_text(text: str) -> str:
    normalized = text.lower().strip()
    normalized = "".join(
        c
        for c in unicodedata.normalize("NFD", normalized)
        if unicodedata.category(c) != "Mn"
    )
    return " ".join(normalized.split())
