from __future__ import annotations

from pathlib import Path

from sqlalchemy.orm import Session

from app.affiliates.base import AffiliateLinkProvider
from app.affiliates.csv_provider import AffiliateCsvStore
from app.database.models import Niche
from app.database.repositories.affiliate_links import (
    find_affiliate_link,
    list_affiliate_links,
    upsert_affiliate_link,
)
from app.database.repositories.channels import get_niche_id
from app.schemas.product import ProductCandidate


class DatabaseAffiliateLinkProvider(AffiliateLinkProvider):
    def __init__(self, pending_path: Path) -> None:
        self.csv_store = AffiliateCsvStore(pending_path)

    def resolve_affiliate_link(
        self,
        session: Session,
        product: ProductCandidate,
        niche_id: int | None,
        manual_affiliate_url: str | None = None,
    ) -> str | None:
        if manual_affiliate_url:
            upsert_affiliate_link(
                session=session,
                marketplace=product.marketplace,
                product_id=product.product_id,
                canonical_url=product.canonical_url,
                affiliate_url=manual_affiliate_url,
                niche_id=niche_id,
            )
            return manual_affiliate_url
        row = find_affiliate_link(session, product.marketplace, product.product_id, niche_id)
        return row.affiliate_url if row is not None else None

    def register_pending_link(self, product: ProductCandidate, niche_name: str) -> None:
        self.csv_store.register_pending(product, niche_name)

    def import_csv(self, session: Session, path: Path) -> int:
        imported = 0
        for row in self.csv_store.read_rows(path):
            active = row.get("active", "true").strip().lower() in {"1", "true", "yes", "sim"}
            niche_name = row.get("niche", "").strip()
            niche_id = get_niche_id(session, niche_name) if niche_name else None
            upsert_affiliate_link(
                session=session,
                marketplace="mercadolivre",
                product_id=row["product_id"],
                canonical_url=row["canonical_url"],
                affiliate_url=row["affiliate_url"],
                niche_id=niche_id,
                active=active,
            )
            imported += 1
        return imported

    def export_csv(self, session: Session, path: Path) -> int:
        rows = []
        for row in list_affiliate_links(session):
            niche = session.get(Niche, row.niche_id) if row.niche_id is not None else None
            rows.append(
                {
                    "product_id": row.product_id,
                    "canonical_url": row.canonical_url,
                    "affiliate_url": row.affiliate_url,
                    "niche": niche.name if niche is not None else "",
                    "active": str(row.active).lower(),
                }
            )
        self.csv_store.write_rows(path, rows)
        return len(rows)
