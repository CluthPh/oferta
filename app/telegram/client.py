from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any, cast

import httpx

from app.core.config import Settings, get_settings
from app.core.exceptions import PublicationError
from app.utils.retries import retry_async

logger = logging.getLogger("telegram.client")


class TelegramClient:
    def __init__(
        self,
        settings: Settings | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.client = client

    async def __aenter__(self) -> TelegramClient:
        if not self.settings.telegram_bot_token:
            raise PublicationError("TELEGRAM_BOT_TOKEN nao configurado")
        if self.client is None:
            self.client = httpx.AsyncClient(
                base_url=f"https://api.telegram.org/bot{self.settings.telegram_bot_token}",
                timeout=self.settings.http_timeout_seconds,
            )
        return self

    async def __aexit__(self, *_args: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        if self.client is not None:
            await self.client.aclose()
            self.client = None

    async def send_photo(
        self,
        chat_id: str,
        photo_url: str,
        caption: str,
        button_text: str,
        button_url: str,
        topic_id: int | None = None,
    ) -> int:
        data: dict[str, Any] = {
            "chat_id": chat_id,
            "photo": photo_url,
            "caption": caption,
            "parse_mode": "HTML",
            "reply_markup": self._button(button_text, button_url),
        }
        if topic_id is not None:
            data["message_thread_id"] = topic_id
        payload = await self._post("sendPhoto", data=data)
        return int(payload["result"]["message_id"])

    async def send_photo_file(
        self,
        chat_id: str,
        photo_path: Path,
        caption: str,
        button_text: str,
        button_url: str,
        topic_id: int | None = None,
    ) -> int:
        data: dict[str, Any] = {
            "chat_id": chat_id,
            "caption": caption,
            "parse_mode": "HTML",
            "reply_markup": self._button(button_text, button_url),
        }
        if topic_id is not None:
            data["message_thread_id"] = topic_id
        with photo_path.open("rb") as handle:
            payload = await self._post("sendPhoto", data=data, files={"photo": handle})
        return int(payload["result"]["message_id"])

    async def send_message(
        self,
        chat_id: str,
        text: str,
        button_text: str,
        button_url: str,
        topic_id: int | None = None,
    ) -> int:
        data: dict[str, Any] = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": False,
            "reply_markup": self._button(button_text, button_url),
        }
        if topic_id is not None:
            data["message_thread_id"] = topic_id
        payload = await self._post("sendMessage", data=data)
        return int(payload["result"]["message_id"])

    async def edit_message_caption(
        self,
        chat_id: str,
        message_id: int,
        caption: str,
        button_text: str,
        button_url: str,
    ) -> int:
        data = {
            "chat_id": chat_id,
            "message_id": message_id,
            "caption": caption,
            "parse_mode": "HTML",
            "reply_markup": self._button(button_text, button_url),
        }
        payload = await self._post("editMessageCaption", data=data)
        return int(payload["result"]["message_id"])

    async def _post(
        self,
        method: str,
        data: dict[str, Any],
        files: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        async def do_request() -> httpx.Response:
            assert self.client is not None
            response = await self.client.post(f"/{method}", data=data, files=files)
            if response.status_code == 429:
                retry_after = float(response.json().get("parameters", {}).get("retry_after", 1))
                await asyncio.sleep(retry_after)
                raise PublicationError("Telegram 429")
            return response

        response = await retry_async(do_request, attempts=3)
        if response.is_error:
            raise PublicationError(f"Telegram falhou em {method}: status={response.status_code}")
        payload = cast("dict[str, Any]", response.json())
        if not payload.get("ok"):
            raise PublicationError(f"Telegram retornou erro em {method}")
        return payload

    def _button(self, text: str, url: str) -> str:
        import json

        return json.dumps({"inline_keyboard": [[{"text": text, "url": url}]]}, ensure_ascii=False)
