from __future__ import annotations

from app.database.models import Product
from app.schemas.product import ProductCandidate


def product_to_candidate(product: Product) -> ProductCandidate:
    return ProductCandidate(
        marketplace=product.marketplace,
        product_id=product.product_id,
        canonical_url=product.canonical_url,
        title=product.title,
        description=product.description,
        current_price=product.current_price,
        original_price=product.original_price,
        discount_percent=product.discount_percent,
        currency=product.currency,
        image_url=product.image_url,
        seller_id=product.seller_id,
        seller_name=product.seller_name,
        official_store=product.official_store,
        free_shipping=product.free_shipping,
        condition=product.condition,
        available_quantity=product.available_quantity,
        sold_quantity=product.sold_quantity,
        category_id=product.category_id,
        discovered_at=product.discovered_at,
        collected_at=product.collected_at,
    )
