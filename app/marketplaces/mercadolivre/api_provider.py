from __future__ import annotations

import logging
from typing import Any

import httpx

from app.core.config import Settings, get_settings
from app.core.exceptions import BlockedCollectionError, MarketplaceError
from app.marketplaces.base import MarketplaceProvider
from app.marketplaces.mercadolivre.parsers import (
    decimal_to_api,
    extract_product_id,
    normalize_item_json,
)
from app.schemas.niche import SearchConfig
from app.schemas.product import ProductCandidate
from app.utils.retries import CircuitBreaker, retry_async

logger = logging.getLogger("marketplace.mercadolivre.api")


class MercadoLivreApiProvider(MarketplaceProvider):
    def __init__(
        self,
        settings: Settings | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.client = client
        self.breaker = CircuitBreaker()

    async def __aenter__(self) -> MercadoLivreApiProvider:
        if self.client is None:
            headers = {"Accept": "application/json", "User-Agent": "oferta-telegram/0.1"}
            if self.settings.mercadolivre_access_token:
                headers["Authorization"] = f"Bearer {self.settings.mercadolivre_access_token}"
            self.client = httpx.AsyncClient(
                base_url="https://api.mercadolibre.com",
                timeout=self.settings.http_timeout_seconds,
                headers=headers,
                follow_redirects=False,
            )
        return self

    async def __aexit__(self, *_args: object) -> None:
        if self.client is not None:
            await self.client.aclose()
            self.client = None

    async def search_products(self, search: SearchConfig) -> list[ProductCandidate]:
        if not self.breaker.allow_request():
            raise MarketplaceError("Circuit breaker aberto para Mercado Livre API")
        params: dict[str, Any] = {"q": search.query, "limit": search.max_results}
        if search.min_price is not None or search.max_price is not None:
            minimum = decimal_to_api(search.min_price) or "*"
            maximum = decimal_to_api(search.max_price) or "*"
            params["price"] = f"{minimum}-{maximum}"
        if search.condition:
            params["ITEM_CONDITION"] = "2230284" if search.condition == "new" else "2230581"
        sort_map = {"price_asc": "price_asc", "relevance": "relevance"}
        if search.sort in sort_map:
            params["sort"] = sort_map[search.sort]

        async def do_request() -> httpx.Response:
            assert self.client is not None
            return await self.client.get(
                f"/sites/{self.settings.mercadolivre_site_id}/search",
                params=params,
            )

        response = await retry_async(do_request)
        self._raise_for_response(response)
        payload = response.json()
        results = payload.get("results", [])
        self.breaker.record_success()
        return [normalize_item_json(result) for result in results if isinstance(result, dict)]

    async def get_product(self, product_id_or_url: str) -> ProductCandidate:
        product_id = (
            extract_product_id(product_id_or_url)
            if product_id_or_url.startswith(("http://", "https://"))
            else product_id_or_url
        )

        async def get_item() -> httpx.Response:
            assert self.client is not None
            return await self.client.get(f"/items/{product_id}")

        response = await retry_async(get_item)
        self._raise_for_response(response)
        description = await self._get_description(product_id)
        self.breaker.record_success()
        return normalize_item_json(response.json(), description=description)

    async def _get_description(self, product_id: str) -> str:
        assert self.client is not None
        try:
            response = await self.client.get(f"/items/{product_id}/description")
            if response.status_code == 200:
                payload = response.json()
                return str(payload.get("plain_text") or "")[:1000]
        except httpx.HTTPError:
            logger.info("description_unavailable product=%s", product_id)
        return ""

    def _raise_for_response(self, response: httpx.Response) -> None:
        if response.status_code in {401, 403, 429}:
            self.breaker.record_failure()
            raise BlockedCollectionError(
                f"Mercado Livre API bloqueou coleta: status={response.status_code}"
            )
        if response.is_error:
            self.breaker.record_failure()
            raise MarketplaceError(f"Mercado Livre API falhou: status={response.status_code}")
