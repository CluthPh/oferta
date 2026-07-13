from abc import ABC, abstractmethod

from app.schemas.niche import SearchConfig
from app.schemas.product import ProductCandidate


class MarketplaceProvider(ABC):
    @abstractmethod
    async def search_products(self, search: SearchConfig) -> list[ProductCandidate]:
        raise NotImplementedError

    @abstractmethod
    async def get_product(self, product_id_or_url: str) -> ProductCandidate:
        raise NotImplementedError

