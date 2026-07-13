from typing import Any, TypedDict


class MercadoLivreSearchResult(TypedDict, total=False):
    id: str
    title: str
    price: float
    original_price: float | None
    currency_id: str
    thumbnail: str
    secure_thumbnail: str
    permalink: str
    seller: dict[str, Any]
    official_store_id: int | None
    official_store_name: str | None
    shipping: dict[str, Any]
    condition: str
    available_quantity: int
    sold_quantity: int
    category_id: str

