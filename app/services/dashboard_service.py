from __future__ import annotations

from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.database.models import AffiliateLink, OfferApproval, Product, Publication, ScanRun
from app.database.repositories.approvals import list_approvals
from app.database.repositories.events import list_events
from app.database.repositories.scan_runs import latest_scan_run, list_scan_runs


class DashboardService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def build(self, session: Session) -> dict[str, object]:
        latest_scan = latest_scan_run(session)
        return {
            "counts": self._counts(session),
            "settings": self._settings_summary(),
            "latest_scan": self._scan_to_dict(latest_scan) if latest_scan else None,
            "recent_scans": [self._scan_to_dict(row) for row in list_scan_runs(session, 8)],
            "recent_approvals": [
                {
                    "id": row.id,
                    "marketplace": row.marketplace,
                    "product_id": row.product_id,
                    "niche_name": row.niche_name,
                    "search_query": row.search_query,
                    "score": row.score,
                    "reason": row.reason,
                    "status": row.status,
                    "created_at": row.created_at,
                }
                for row in list_approvals(session, limit=20)
            ],
            "recent_events": [
                {
                    "id": row.id,
                    "level": row.level,
                    "module": row.module,
                    "action": row.action,
                    "message": row.message,
                    "created_at": row.created_at,
                }
                for row in list_events(session, 20)
            ],
        }

    def _counts(self, session: Session) -> dict[str, int]:
        return {
            "products": int(session.scalar(select(func.count(Product.id))) or 0),
            "ignored_products": int(
                session.scalar(select(func.count(Product.id)).where(Product.ignored.is_(True)))
                or 0
            ),
            "affiliate_links": int(session.scalar(select(func.count(AffiliateLink.id))) or 0),
            "publications": int(session.scalar(select(func.count(Publication.id))) or 0),
            "sent_publications": int(
                session.scalar(
                    select(func.count(Publication.id)).where(Publication.status == "sent")
                )
                or 0
            ),
            "failed_publications": int(
                session.scalar(
                    select(func.count(Publication.id)).where(Publication.status == "failed")
                )
                or 0
            ),
            "scan_runs": int(session.scalar(select(func.count(ScanRun.id))) or 0),
            "pending_approvals": int(
                session.scalar(
                    select(func.count(OfferApproval.id)).where(OfferApproval.status == "pending")
                )
                or 0
            ),
            "pending_affiliate_links": self._pending_affiliate_count(),
        }

    def _settings_summary(self) -> dict[str, object]:
        return {
            "dry_run": self.settings.dry_run,
            "post_without_affiliate_link": self.settings.post_without_affiliate_link,
            "scan_interval_minutes": self.settings.scan_interval_minutes,
            "run_scan_on_startup": self.settings.run_scan_on_startup,
            "require_approval": self.settings.require_approval,
            "admin_api_key_configured": bool(self.settings.admin_api_key),
            "telegram_token_configured": bool(self.settings.telegram_bot_token),
            "niches_config_path": str(self.settings.niches_config_path),
            "database_url": self.settings.database_url,
            "marketplace_sources": self.settings.marketplace_sources,
        }

    def _pending_affiliate_count(self) -> int:
        path = self.settings.data_dir / "pending_affiliate_links.csv"
        if not path.exists():
            return 0
        with path.open("r", encoding="utf-8", newline="") as handle:
            return max(0, sum(1 for _line in handle) - 1)

    @staticmethod
    def _scan_to_dict(scan: ScanRun) -> dict[str, object]:
        return {
            "id": scan.id,
            "started_at": scan.started_at,
            "finished_at": scan.finished_at,
            "collected_count": scan.collected_count,
            "approved_count": scan.approved_count,
            "published_count": scan.published_count,
            "ignored_count": scan.ignored_count,
            "error_count": scan.error_count,
            "error_message": scan.error_message,
        }


def tail_text_file(path: Path, max_lines: int = 120) -> list[str]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        lines = handle.readlines()
    return [line.rstrip("\n") for line in lines[-max_lines:]]
