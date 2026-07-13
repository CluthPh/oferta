from __future__ import annotations

import logging
import tempfile
from pathlib import Path

import httpx

from app.core.config import Settings, get_settings
from app.core.exceptions import PublicationError
from app.schemas.niche import TelegramConfig
from app.schemas.product import ProductCandidate
from app.telegram.client import TelegramClient
from app.telegram.formatter import fit_caption, fit_text, format_offer_html

logger = logging.getLogger("telegram.publisher")


class TelegramPublisher:
    def __init__(self, client: TelegramClient, settings: Settings | None = None) -> None:
        self.client = client
        self.settings = settings or get_settings()

    async def aclose(self) -> None:
        await self.client.aclose()

    async def publish_offer(
        self,
        product: ProductCandidate,
        chat_id: str,
        config: TelegramConfig,
        link: str,
        topic_id: int | None = None,
    ) -> int:
        message = format_offer_html(product, config)
        if product.image_url:
            caption = fit_caption(message, product, config)
            try:
                return await self.client.send_photo(
                    chat_id=chat_id,
                    photo_url=product.image_url,
                    caption=caption,
                    button_text=config.button_text,
                    button_url=link,
                    topic_id=topic_id,
                )
            except PublicationError:
                downloaded = await self._download_image(product.image_url)
                if downloaded is not None:
                    try:
                        return await self.client.send_photo_file(
                            chat_id=chat_id,
                            photo_path=downloaded,
                            caption=caption,
                            button_text=config.button_text,
                            button_url=link,
                            topic_id=topic_id,
                        )
                    finally:
                        downloaded.unlink(missing_ok=True)
                logger.info("image_send_failed product=%s fallback=text", product.product_id)
        return await self.client.send_message(
            chat_id=chat_id,
            text=fit_text(message),
            button_text=config.button_text,
            button_url=link,
            topic_id=topic_id,
        )

    async def _download_image(self, url: str) -> Path | None:
        async with httpx.AsyncClient(timeout=self.settings.http_timeout_seconds) as client:
            response = await client.get(url, follow_redirects=False)
        content_type = response.headers.get("content-type", "")
        if response.status_code != 200 or not content_type.startswith("image/"):
            return None
        if len(response.content) > self.settings.max_image_bytes:
            return None
        suffix = ".jpg" if "jpeg" in content_type or "jpg" in content_type else ".img"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as handle:
            handle.write(response.content)
            return Path(handle.name)
