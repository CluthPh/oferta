from decimal import Decimal

from app.database.repositories.approvals import (
    list_approvals,
    mark_product_published,
    set_approval_status,
    upsert_pending_approval,
)
from app.schemas.niche import NicheConfig, SearchConfig, TelegramConfig
from app.schemas.product import ProductCandidate
from app.schemas.publication import OfferDecision
from app.services.reporting_service import ReportingService


def product() -> ProductCandidate:
    return ProductCandidate(
        product_id="MLB123",
        canonical_url="https://produto.mercadolivre.com.br/MLB-123-produto-_JM",
        title="SSD 1TB",
        current_price=Decimal("300"),
        original_price=Decimal("500"),
        discount_percent=40,
    )


def test_approval_queue_status_flow(db_session) -> None:  # type: ignore[no-untyped-def]
    niche = NicheConfig(name="informatica", telegram=TelegramConfig(chat_ids=["@canal"]))
    search = SearchConfig(query="ssd")
    approval = upsert_pending_approval(
        db_session,
        product(),
        niche,
        search,
        OfferDecision(True, 80, "score=80"),
    )
    assert approval.status == "pending"
    assert list_approvals(db_session, "pending")[0].product_id == "MLB123"
    set_approval_status(db_session, approval.id, "approved")
    assert list_approvals(db_session, "approved")[0].id == approval.id
    mark_product_published(db_session, "mercadolivre", "MLB123", "informatica")
    assert list_approvals(db_session, "published")[0].id == approval.id


def test_daily_report_shape(db_session) -> None:  # type: ignore[no-untyped-def]
    report = ReportingService().build_daily_report(db_session)
    assert report["period_hours"] == 24
    assert "pending_approvals" in report
    assert isinstance(report["top_discounts"], list)
