from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import OfferApproval
from app.schemas.niche import NicheConfig, SearchConfig
from app.schemas.product import ProductCandidate
from app.schemas.publication import OfferDecision

OPEN_STATUSES = {"pending", "approved"}
VALID_STATUSES = {"pending", "approved", "rejected", "published"}


def upsert_pending_approval(
    session: Session,
    product: ProductCandidate,
    niche: NicheConfig,
    search: SearchConfig | None,
    decision: OfferDecision,
) -> OfferApproval:
    row = session.scalar(
        select(OfferApproval)
        .where(
            OfferApproval.marketplace == product.marketplace,
            OfferApproval.product_id == product.product_id,
            OfferApproval.niche_name == niche.name,
            OfferApproval.status.in_(OPEN_STATUSES),
        )
        .order_by(OfferApproval.created_at.desc())
        .limit(1)
    )
    if row is None:
        row = OfferApproval(
            marketplace=product.marketplace,
            product_id=product.product_id,
            niche_name=niche.name,
        )
        session.add(row)
    row.search_query = search.query if search is not None else "manual"
    row.score = decision.score
    row.reason = decision.reason
    if row.status not in OPEN_STATUSES:
        row.status = "pending"
    return row


def list_approvals(
    session: Session,
    status: str | None = None,
    limit: int = 100,
) -> list[OfferApproval]:
    statement = select(OfferApproval).order_by(OfferApproval.created_at.desc()).limit(limit)
    if status:
        statement = statement.where(OfferApproval.status == status)
    return list(session.scalars(statement).all())


def get_approval(session: Session, approval_id: int) -> OfferApproval | None:
    return session.get(OfferApproval, approval_id)


def set_approval_status(
    session: Session,
    approval_id: int,
    status: str,
    note: str = "",
) -> OfferApproval | None:
    if status not in VALID_STATUSES:
        raise ValueError(f"status invalido: {status}")
    row = session.get(OfferApproval, approval_id)
    if row is None:
        return None
    row.status = status
    row.note = note
    if status in {"approved", "rejected"}:
        row.decided_at = datetime.now(UTC)
    if status == "published":
        row.published_at = datetime.now(UTC)
    return row


def mark_product_published(
    session: Session,
    marketplace: str,
    product_id: str,
    niche_name: str,
) -> None:
    row = session.scalar(
        select(OfferApproval)
        .where(
            OfferApproval.marketplace == marketplace,
            OfferApproval.product_id == product_id,
            OfferApproval.niche_name == niche_name,
            OfferApproval.status.in_(OPEN_STATUSES),
        )
        .order_by(OfferApproval.created_at.desc())
        .limit(1)
    )
    if row is not None:
        row.status = "published"
        row.published_at = datetime.now(UTC)
