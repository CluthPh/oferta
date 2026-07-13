from __future__ import annotations

from typing import Any, cast

import httpx

from app.core.config import Settings
from app.core.exceptions import PublicationError


class TelegramDiagnosticService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def test(self, chat_id: str | None = None) -> dict[str, object]:
        if not self.settings.telegram_bot_token:
            raise PublicationError("TELEGRAM_BOT_TOKEN nao configurado")
        async with httpx.AsyncClient(
            base_url=f"https://api.telegram.org/bot{self.settings.telegram_bot_token}",
            timeout=self.settings.http_timeout_seconds,
        ) as client:
            me = await self._get(client, "getMe")
            result: dict[str, object] = {"bot": me.get("result", {}), "chat": None}
            if chat_id:
                result["chat"] = (await self._get(client, "getChat", {"chat_id": chat_id})).get(
                    "result",
                    {},
                )
            return result

    async def _get(
        self,
        client: httpx.AsyncClient,
        method: str,
        params: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        response = await client.get(f"/{method}", params=params)
        if response.is_error:
            raise PublicationError(f"Telegram falhou em {method}: status={response.status_code}")
        payload = cast("dict[str, Any]", response.json())
        if not payload.get("ok"):
            raise PublicationError(f"Telegram retornou erro em {method}")
        return payload
