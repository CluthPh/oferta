from decimal import Decimal

from app.database.repositories.posts import record_publication, should_repost


def test_repost_after_price_drop(db_session) -> None:  # type: ignore[no-untyped-def]
    previous = record_publication(
        db_session,
        "mercadolivre",
        "MLB123",
        "@canal",
        Decimal("100"),
        "https://link",
        "sent",
        "teste",
    )
    can_post, reason = should_repost(previous, Decimal("95"), 168, 3, "repost")
    assert can_post is True
    assert "queda" in reason


def test_ignore_duplicate_without_drop(db_session) -> None:  # type: ignore[no-untyped-def]
    previous = record_publication(
        db_session,
        "mercadolivre",
        "MLB123",
        "@canal",
        Decimal("100"),
        "https://link",
        "sent",
        "teste",
    )
    can_post, reason = should_repost(previous, Decimal("99"), 168, 3, "repost")
    assert can_post is False
    assert "deduplicado" in reason

