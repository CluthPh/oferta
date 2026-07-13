import html
import re
import unicodedata


def normalize_words(value: str) -> str:
    lowered = value.casefold()
    normalized = unicodedata.normalize("NFKD", lowered)
    return "".join(char for char in normalized if not unicodedata.combining(char))


def contains_all_words(text: str, words: list[str]) -> bool:
    normalized = normalize_words(text)
    return all(normalize_words(word) in normalized for word in words)


def contains_any_word(text: str, words: list[str]) -> bool:
    normalized = normalize_words(text)
    return any(normalize_words(word) in normalized for word in words)


def escape_html(value: str) -> str:
    return html.escape(value, quote=False)


def truncate_text(value: str, max_length: int) -> str:
    if len(value) <= max_length:
        return value
    if max_length <= 1:
        return value[:max_length]
    truncated = value[: max_length - 1].rsplit(" ", 1)[0].strip()
    return f"{truncated or value[: max_length - 1]}..."


def collapse_spaces(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()

