from __future__ import annotations

import logging
from urllib.parse import quote_plus, urljoin

import httpx

from app.core.config import Settings, get_settings
from app.core.exceptions import BlockedCollectionError, MarketplaceError
from app.marketplaces.base import MarketplaceProvider
from app.marketplaces.mercadolivre.parsers import parse_json_ld_product
from app.schemas.niche import SearchConfig
from app.schemas.product import ProductCandidate
from app.utils.urls import validate_mercadolivre_url

logger = logging.getLogger("marketplace.mercadolivre.web")


class MercadoLivreWebProvider(MarketplaceProvider):
    def __init__(
        self,
        settings: Settings | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.client = client

    async def __aenter__(self) -> MercadoLivreWebProvider:
        if self.client is None:
            self.client = httpx.AsyncClient(
                timeout=self.settings.http_timeout_seconds,
                headers={"User-Agent": "oferta-telegram/0.1"},
                follow_redirects=False,
            )
        return self

    async def __aexit__(self, *_args: object) -> None:
        if self.client is not None:
            await self.client.aclose()
            self.client = None

    async def search_products(self, search: SearchConfig) -> list[ProductCandidate]:
        url = f"https://lista.mercadolivre.com.br/{quote_plus(search.query)}"
        logger.info("web_search_started query=%s", search.query)
        assert self.client is not None
        response = await self._safe_get(url)
        if response.status_code in {403, 429}:
            raise BlockedCollectionError(f"Coleta web bloqueada: status={response.status_code}")
        if response.is_error:
            raise MarketplaceError(f"Coleta web falhou: status={response.status_code}")
        product_urls = self._extract_product_urls(response.text)[: search.max_results]
        products: list[ProductCandidate] = []
        for product_url in product_urls:
            try:
                products.append(await self.get_product(product_url))
            except MarketplaceError as exc:
                logger.info("web_product_skipped url=%s reason=%s", product_url, exc)
        return products

    async def get_product(self, product_id_or_url: str) -> ProductCandidate:
        validate_mercadolivre_url(product_id_or_url)
        assert self.client is not None
        response = await self._safe_get(product_id_or_url)
        if response.status_code in {403, 429}:
            raise BlockedCollectionError(f"Coleta web bloqueada: status={response.status_code}")
        if response.is_error:
            raise MarketplaceError(f"Coleta web falhou: status={response.status_code}")
        return parse_json_ld_product(response.text, str(response.url))

    def _extract_product_urls(self, html: str) -> list[str]:
        urls: list[str] = []
        marker = "https://produto.mercadolivre.com.br/"
        for part in html.split(marker)[1:]:
            raw = marker + part.split('"', 1)[0].split("'", 1)[0].split("?", 1)[0]
            if raw not in urls:
                urls.append(raw)
        return urls

    async def _safe_get(self, url: str) -> httpx.Response:
        assert self.client is not None
        current_url = url
        for _ in range(3):
            response = await self.client.get(current_url)
            self._raise_if_verification_page(str(response.url))
            if response.status_code not in {301, 302, 303, 307, 308}:
                return response
            location = response.headers.get("location")
            if not location:
                return response
            next_url = urljoin(current_url, location)
            validate_mercadolivre_url(next_url)
            self._raise_if_verification_page(next_url)
            current_url = next_url
        raise MarketplaceError("Muitos redirects na coleta web")

    def _raise_if_verification_page(self, url: str) -> None:
        lowered = url.lower()
        if "account-verification" in lowered or "captcha" in lowered:
            raise BlockedCollectionError("Mercado Livre solicitou verificacao/CAPTCHA")
