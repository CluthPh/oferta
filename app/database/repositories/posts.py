from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Publication


def latest_publication(session: Session, product_id: str, channel_id: str) -> Publication | None:
    return session.scalar(
        select(Publication)
        .where(
            Publication.product_id == product_id,
            Publication.channel_id == channel_id,
            Publication.status != "dry_run",
        )
        .order_by(Publication.created_at.desc())
        .limit(1)
    )


def should_repost(
    previous: Publication | None,
    current_price: Decimal | None,
    repost_after_hours: int,
    min_price_drop_percent: float,
    price_change_mode: str,
) -> tuple[bool, str]:
    if previous is None:
        return True, "primeira publicacao"
    if previous.status == "failed":
        return True, "postagem anterior falhou"
    if price_change_mode == "ignore":
        return False, "produto ja publicado"
    if current_price is not None and previous.published_price:
        drop = (
            (previous.published_price - current_price) / previous.published_price
        ) * Decimal("100")
        if drop >= Decimal(str(min_price_drop_percent)):
            if price_change_mode == "edit":
                return True, f"queda de preco para edicao: {drop:.2f}%"
            return True, f"queda de preco: {drop:.2f}%"
    published_at = previous.published_at or previous.created_at
    if published_at <= datetime.now(UTC) - timedelta(hours=repost_after_hours):
        return True, "periodo de repostagem atingido"
    return False, "deduplicado por produto e canal"


def record_publication(
    session: Session,
    marketplace: str,
    product_id: str,
    channel_id: str,
    price: Decimal | None,
    link_used: str,
    status: str,
    reason: str,
    telegram_message_id: int | None = None,
    dry_run: bool = False,
) -> Publication:
    row = Publication(
        marketplace=marketplace,
        product_id=product_id,
        channel_id=channel_id,
        telegram_message_id=telegram_message_id,
        published_price=price,
        link_used=link_used,
        status=status,
        reason=reason,
        published_at=None if dry_run else datetime.now(UTC),
        dry_run=dry_run,
    )
    session.add(row)
    return row


def list_publications(session: Session, limit: int = 100) -> list[Publication]:
    return list(
        session.scalars(select(Publication).order_by(Publication.created_at.desc()).limit(limit)).all()
    )
