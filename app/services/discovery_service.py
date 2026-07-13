from __future__ import annotations

import logging

from app.core.exceptions import AppError
from app.marketplaces.base import MarketplaceProvider
from app.schemas.niche import ManualProductConfig, NicheConfig, SearchConfig
from app.schemas.product import ProductCandidate

logger = logging.getLogger("service.discovery")

DiscoveredProduct = tuple[ProductCandidate, SearchConfig | None, ManualProductConfig | None]


class DiscoveryService:
    def __init__(self, provider: MarketplaceProvider) -> None:
        self.provider = provider

    async def discover_niche(self, niche: NicheConfig) -> list[DiscoveredProduct]:
        collected: list[DiscoveredProduct] = []
        if not niche.enabled:
            return collected
        for search in niche.searches:
            if not search.enabled:
                continue
            try:
                products = await self.provider.search_products(search)
            except AppError as exc:
                logger.error(
                    "search_failed niche=%s query=%s error=%s",
                    niche.name,
                    search.query,
                    exc,
                )
                continue
            collected.extend((product, search, None) for product in products)
        for manual in niche.manual_products:
            if not manual.enabled:
                continue
            try:
                product = await self.provider.get_product(manual.url)
            except AppError as exc:
                logger.error(
                    "manual_product_failed niche=%s url=%s error=%s",
                    niche.name,
                    manual.url,
                    exc,
                )
                continue
            collected.append((product, None, manual))
        return collected
