from __future__ import annotations

import hmac
import time
from hashlib import sha256

from fastapi import Cookie, Header, HTTPException, status

from app.core.config import get_settings

SESSION_MAX_AGE_SECONDS = 60 * 60 * 24


def create_admin_session_token() -> str:
    settings = get_settings()
    timestamp = str(int(time.time()))
    signature = hmac.new(
        settings.admin_api_key.encode("utf-8"),
        timestamp.encode("utf-8"),
        sha256,
    ).hexdigest()
    return f"{timestamp}.{signature}"


def verify_admin_session_token(token: str) -> bool:
    settings = get_settings()
    if not settings.admin_api_key or "." not in token:
        return False
    timestamp, signature = token.split(".", 1)
    if not timestamp.isdigit():
        return False
    if int(time.time()) - int(timestamp) > SESSION_MAX_AGE_SECONDS:
        return False
    expected = hmac.new(
        settings.admin_api_key.encode("utf-8"),
        timestamp.encode("utf-8"),
        sha256,
    ).hexdigest()
    return hmac.compare_digest(signature, expected)


def require_admin_key(
    x_admin_key: str = Header(default=""),
    admin_session: str = Cookie(default=""),
) -> None:
    settings = get_settings()
    if not settings.admin_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ADMIN_API_KEY nao configurada",
        )
    if hmac.compare_digest(x_admin_key, settings.admin_api_key):
        return
    if verify_admin_session_token(admin_session):
        return
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="sessao admin invalida")
