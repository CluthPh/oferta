from decimal import Decimal

from app.database.repositories.price_history import add_price_history
from app.database.repositories.products import mark_ignored
from app.schemas.niche import SearchConfig
from app.schemas.product import ProductCandidate, calculate_discount
from app.services.offer_service import OfferService
from app.services.product_service import ProductService


def product(**updates: object) -> ProductCandidate:
    base = {
        "product_id": "MLB123456789",
        "canonical_url": "https://produto.mercadolivre.com.br/MLB-123456789-produto-_JM",
        "title": "SSD NVMe 1TB Novo",
        "current_price": Decimal("400"),
        "original_price": Decimal("500"),
        "discount_percent": 20.0,
        "free_shipping": True,
        "condition": "new",
        "seller_name": "Loja A",
    }
    base.update(updates)
    return ProductCandidate(**base)


def test_discount_calculation() -> None:
    assert calculate_discount(Decimal("500"), Decimal("400")) == 20.0
    assert calculate_discount(None, Decimal("400")) is None
    assert calculate_discount(Decimal("400"), Decimal("500")) is None


def test_offer_approved(db_session) -> None:  # type: ignore[no-untyped-def]
    candidate = product()
    add_price_history(db_session, product(current_price=Decimal("450")))
    add_price_history(db_session, candidate)
    rule = SearchConfig(
        query="ssd",
        min_price=Decimal("100"),
        max_price=Decimal("700"),
        min_discount_percent=10,
        free_shipping_only=True,
        condition="new",
        include_words=["ssd"],
        exclude_words=["defeito"],
    )
    decision = OfferService().evaluate(db_session, candidate, rule)
    assert decision.approved is True
    assert decision.score >= 35


def test_offer_rejects_forbidden_word(db_session) -> None:  # type: ignore[no-untyped-def]
    rule = SearchConfig(query="ssd", exclude_words=["defeito"])
    decision = OfferService().evaluate(db_session, product(title="SSD com defeito"), rule)
    assert decision.approved is False
    assert "proibida" in decision.reason


def test_ignored_product_stays_ignored_after_upsert(db_session) -> None:  # type: ignore[no-untyped-def]
    service = ProductService()
    service.save_candidate(db_session, product())
    mark_ignored(db_session, "MLB123456789")
    saved = service.save_candidate(db_session, product(current_price=Decimal("390")))
    assert saved.ignored is True
