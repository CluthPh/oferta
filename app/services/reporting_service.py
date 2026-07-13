from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database.models import OfferApproval, Product, Publication, ScanRun


class ReportingService:
    def build_daily_report(self, session: Session) -> dict[str, object]:
        since = datetime.now(UTC) - timedelta(hours=24)
        top_products = session.scalars(
            select(Product)
            .where(Product.collected_at >= since)
            .order_by(Product.discount_percent.desc().nullslast())
            .limit(10)
        ).all()
        return {
            "period_hours": 24,
            "generated_at": datetime.now(UTC),
            "scans": int(
                session.scalar(select(func.count(ScanRun.id)).where(ScanRun.started_at >= since))
                or 0
            ),
            "products_collected": int(
                session.scalar(
                    select(func.count(Product.id)).where(Product.collected_at >= since)
                )
                or 0
            ),
            "publications": int(
                session.scalar(
                    select(func.count(Publication.id)).where(Publication.created_at >= since)
                )
                or 0
            ),
            "sent_publications": int(
                session.scalar(
                    select(func.count(Publication.id)).where(
                        Publication.created_at >= since,
                        Publication.status == "sent",
                    )
                )
                or 0
            ),
            "dry_runs": int(
                session.scalar(
                    select(func.count(Publication.id)).where(
                        Publication.created_at >= since,
                        Publication.status == "dry_run",
                    )
                )
                or 0
            ),
            "pending_approvals": int(
                session.scalar(
                    select(func.count(OfferApproval.id)).where(OfferApproval.status == "pending")
                )
                or 0
            ),
            "top_discounts": [
                {
                    "product_id": product.product_id,
                    "title": product.title,
                    "current_price": (
                        str(product.current_price) if product.current_price is not None else None
                    ),
                    "discount_percent": product.discount_percent,
                }
                for product in top_products
            ],
        }
