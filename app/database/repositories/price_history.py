from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import PriceHistory
from app.schemas.product import ProductCandidate


def add_price_history(
    session: Session,
    product: ProductCandidate,
    min_interval_minutes: int = 30,
) -> PriceHistory | None:
    latest = session.scalar(
        select(PriceHistory)
        .where(
            PriceHistory.marketplace == product.marketplace,
            PriceHistory.product_id == product.product_id,
        )
        .order_by(PriceHistory.collected_at.desc())
        .limit(1)
    )
    now = datetime.now(UTC)
    if (
        latest is not None
        and latest.price == product.current_price
        and latest.original_price == product.original_price
        and latest.collected_at >= now - timedelta(minutes=min_interval_minutes)
    ):
        return None

    row = PriceHistory(
        marketplace=product.marketplace,
        product_id=product.product_id,
        price=product.current_price,
        original_price=product.original_price,
        collected_at=product.collected_at,
    )
    session.add(row)
    return row


def get_previous_price(session: Session, marketplace: str, product_id: str) -> PriceHistory | None:
    return session.scalar(
        select(PriceHistory)
        .where(PriceHistory.marketplace == marketplace, PriceHistory.product_id == product_id)
        .order_by(PriceHistory.collected_at.desc())
        .offset(1)
        .limit(1)
    )


def get_previous_prices(
    session: Session,
    marketplace: str,
    product_id: str,
    limit: int = 10,
) -> list[PriceHistory]:
    return list(
        session.scalars(
            select(PriceHistory)
            .where(PriceHistory.marketplace == marketplace, PriceHistory.product_id == product_id)
            .order_by(PriceHistory.collected_at.desc())
            .offset(1)
            .limit(limit)
        ).all()
    )


def get_price_history(
    session: Session,
    marketplace: str,
    product_id: str,
    limit: int = 50,
) -> list[PriceHistory]:
    rows = list(
        session.scalars(
            select(PriceHistory)
            .where(PriceHistory.marketplace == marketplace, PriceHistory.product_id == product_id)
            .order_by(PriceHistory.collected_at.desc())
            .limit(limit)
        ).all()
    )
    return list(reversed(rows))
