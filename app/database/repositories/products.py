from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.database.models import Product, Seller
from app.schemas.product import ProductCandidate


def upsert_seller(session: Session, product: ProductCandidate) -> Seller | None:
    if not product.seller_id:
        return None
    seller = session.scalar(
        select(Seller).where(
            Seller.marketplace == product.marketplace,
            Seller.seller_id == product.seller_id,
        )
    )
    if seller is None:
        seller = Seller(marketplace=product.marketplace, seller_id=product.seller_id)
        session.add(seller)
    seller.name = product.seller_name
    seller.official_store = product.official_store
    return seller


def upsert_product(session: Session, candidate: ProductCandidate) -> Product:
    product = session.scalar(
        select(Product).where(
            Product.marketplace == candidate.marketplace,
            Product.product_id == candidate.product_id,
        )
    )
    if product is None:
        product = Product(
            marketplace=candidate.marketplace,
            product_id=candidate.product_id,
            discovered_at=candidate.discovered_at,
            canonical_url=candidate.canonical_url,
            title=candidate.title,
        )
        session.add(product)

    product.canonical_url = candidate.canonical_url
    product.title = candidate.title
    product.description = candidate.description
    product.current_price = candidate.current_price
    product.original_price = candidate.original_price
    product.discount_percent = candidate.discount_percent
    product.currency = candidate.currency
    product.image_url = candidate.image_url
    product.seller_id = candidate.seller_id
    product.seller_name = candidate.seller_name
    product.official_store = candidate.official_store
    product.free_shipping = candidate.free_shipping
    product.condition = candidate.condition
    product.available_quantity = candidate.available_quantity
    product.sold_quantity = candidate.sold_quantity
    product.category_id = candidate.category_id
    product.collected_at = candidate.collected_at or datetime.now(UTC)
    upsert_seller(session, candidate)
    return product


def list_products(
    session: Session,
    limit: int = 100,
    query: str = "",
    ignored: bool | None = None,
    free_shipping: bool | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
    min_discount: float | None = None,
) -> list[Product]:
    statement = select(Product)
    if query:
        like = f"%{query}%"
        statement = statement.where(
            or_(Product.title.ilike(like), Product.product_id.ilike(like))
        )
    if ignored is not None:
        statement = statement.where(Product.ignored.is_(ignored))
    if free_shipping is not None:
        statement = statement.where(Product.free_shipping.is_(free_shipping))
    if min_price is not None:
        statement = statement.where(Product.current_price >= min_price)
    if max_price is not None:
        statement = statement.where(Product.current_price <= max_price)
    if min_discount is not None:
        statement = statement.where(Product.discount_percent >= min_discount)
    return list(session.scalars(statement.order_by(Product.collected_at.desc()).limit(limit)).all())


def get_product_by_public_id(session: Session, public_id: str) -> Product | None:
    return session.scalar(select(Product).where(Product.product_id == public_id))


def mark_ignored(session: Session, public_id: str) -> Product | None:
    product = get_product_by_public_id(session, public_id)
    if product is not None:
        product.ignored = True
    return product
