from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from app.core.constants import ALLOWED_MERCADOLIVRE_HOSTS
from app.core.exceptions import SecurityError

SENSITIVE_QUERY_KEYS = {"token", "access_token", "auth", "session", "cookie"}


def validate_mercadolivre_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise SecurityError(f"URL invalida: esquema nao permitido em {url}")
    host = (parsed.netloc or "").lower()
    if host not in ALLOWED_MERCADOLIVRE_HOSTS:
        raise SecurityError(f"URL invalida: host nao permitido em {url}")
    return url


def strip_tracking_params(url: str) -> str:
    parsed = urlparse(url)
    query = [
        (key, value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=False)
        if key.lower() not in SENSITIVE_QUERY_KEYS and not key.lower().startswith("utm_")
    ]
    return urlunparse(parsed._replace(query=urlencode(query), fragment=""))


def safe_log_url(url: str) -> str:
    parsed = urlparse(url)
    return urlunparse(parsed._replace(query="", fragment=""))

