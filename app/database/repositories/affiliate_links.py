from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import AffiliateLink


def find_affiliate_link(
    session: Session,
    marketplace: str,
    product_id: str,
    niche_id: int | None = None,
) -> AffiliateLink | None:
    statement = select(AffiliateLink).where(
        AffiliateLink.marketplace == marketplace,
        AffiliateLink.product_id == product_id,
        AffiliateLink.active.is_(True),
    )
    if niche_id is not None:
        niche_specific = session.scalar(
            statement.where(AffiliateLink.niche_id == niche_id).limit(1)
        )
        if niche_specific is not None:
            return niche_specific
    return session.scalar(statement.where(AffiliateLink.niche_id.is_(None)).limit(1))


def upsert_affiliate_link(
    session: Session,
    marketplace: str,
    product_id: str,
    canonical_url: str,
    affiliate_url: str,
    niche_id: int | None = None,
    active: bool = True,
) -> AffiliateLink:
    row = session.scalar(
        select(AffiliateLink).where(
            AffiliateLink.marketplace == marketplace,
            AffiliateLink.product_id == product_id,
            AffiliateLink.niche_id == niche_id,
        )
    )
    if row is None:
        row = AffiliateLink(
            marketplace=marketplace,
            product_id=product_id,
            canonical_url=canonical_url,
            affiliate_url=affiliate_url,
            niche_id=niche_id,
        )
        session.add(row)
    row.canonical_url = canonical_url
    row.affiliate_url = affiliate_url
    row.active = active
    return row


def list_affiliate_links(session: Session) -> list[AffiliateLink]:
    return list(session.scalars(select(AffiliateLink).order_by(AffiliateLink.id.desc())).all())
