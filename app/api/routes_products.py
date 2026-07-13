from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import require_admin_key
from app.core.config import get_settings
from app.database.repositories.price_history import get_price_history
from app.database.repositories.products import get_product_by_public_id, list_products, mark_ignored
from app.database.session import session_scope
from app.schemas.product import ProductListItem
from app.services.publish_now_service import PublishNowService

router = APIRouter(prefix="/products", tags=["products"])


@router.get("")
def products(
    limit: int = 100,
    q: str = "",
    ignored: bool | None = None,
    free_shipping: bool | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
    min_discount: float | None = None,
) -> list[ProductListItem]:
    with session_scope() as session:
        return [
            ProductListItem.model_validate(item)
            for item in list_products(
                session,
                limit=limit,
                query=q,
                ignored=ignored,
                free_shipping=free_shipping,
                min_price=min_price,
                max_price=max_price,
                min_discount=min_discount,
            )
        ]


@router.get("/{product_id}")
def product_detail(product_id: str) -> dict[str, object]:
    with session_scope() as session:
        product = get_product_by_public_id(session, product_id)
        if product is None:
            raise HTTPException(status_code=404, detail="produto nao encontrado")
        return {
            "product_id": product.product_id,
            "title": product.title,
            "canonical_url": product.canonical_url,
            "current_price": (
                str(product.current_price) if product.current_price is not None else None
            ),
            "original_price": (
                str(product.original_price) if product.original_price is not None else None
            ),
            "discount_percent": product.discount_percent,
            "image_url": product.image_url,
            "seller_name": product.seller_name,
            "free_shipping": product.free_shipping,
            "ignored": product.ignored,
            "collected_at": product.collected_at,
        }


@router.get("/{product_id}/price-history")
def product_price_history(product_id: str, limit: int = 50) -> list[dict[str, object]]:
    with session_scope() as session:
        product = get_product_by_public_id(session, product_id)
        if product is None:
            raise HTTPException(status_code=404, detail="produto nao encontrado")
        return [
            {
                "price": str(row.price) if row.price is not None else None,
                "original_price": (
                    str(row.original_price) if row.original_price is not None else None
                ),
                "collected_at": row.collected_at,
            }
            for row in get_price_history(session, product.marketplace, product.product_id, limit)
        ]


@router.post("/{product_id}/ignore", dependencies=[Depends(require_admin_key)])
def ignore_product(product_id: str) -> dict[str, str]:
    with session_scope() as session:
        product = mark_ignored(session, product_id)
        if product is None:
            raise HTTPException(status_code=404, detail="produto nao encontrado")
        return {"status": "ignored"}


@router.post("/{product_id}/publish", dependencies=[Depends(require_admin_key)])
async def publish_product(
    product_id: str,
    niche: str | None = None,
    force: bool = True,
) -> dict[str, object]:
    with session_scope() as session:
        product = get_product_by_public_id(session, product_id)
        if product is None:
            raise HTTPException(status_code=404, detail="produto nao encontrado")
        return await PublishNowService(get_settings()).publish(session, product, niche, force)
