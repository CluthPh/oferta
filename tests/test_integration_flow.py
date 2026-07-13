from decimal import Decimal

from app.affiliates.database_provider import DatabaseAffiliateLinkProvider
from app.database.repositories.affiliate_links import upsert_affiliate_link
from app.database.repositories.channels import sync_niche_config
from app.database.repositories.posts import list_publications
from app.schemas.niche import NicheConfig, PublicationConfig, SearchConfig, TelegramConfig
from app.schemas.product import ProductCandidate
from app.services.offer_service import OfferService
from app.services.product_service import ProductService
from app.services.publication_service import PublicationService


async def test_collected_approved_linked_and_dry_run_published(  # type: ignore[no-untyped-def]
    db_session,
    tmp_path,
    test_settings,
) -> None:
    niche = NicheConfig(
        name="informatica",
        telegram=TelegramConfig(chat_ids=["@canal"], header="Oferta"),
        searches=[SearchConfig(query="ssd", min_discount_percent=10, include_words=["ssd"])],
    )
    niche_row = sync_niche_config(db_session, niche)
    product = ProductCandidate(
        product_id="MLB123456789",
        canonical_url="https://produto.mercadolivre.com.br/MLB-123456789-produto-_JM",
        title="SSD NVMe 1TB",
        current_price=Decimal("400"),
        original_price=Decimal("500"),
        discount_percent=20,
        free_shipping=True,
    )
    upsert_affiliate_link(
        db_session,
        product.marketplace,
        product.product_id,
        product.canonical_url,
        "https://afiliado.example/oferta",
        niche_row.id,
    )
    ProductService().save_candidate(db_session, product)
    decision = OfferService().evaluate(db_session, product, niche.searches[0])
    published = await PublicationService(
        DatabaseAffiliateLinkProvider(tmp_path / "pending.csv"),
        None,
        test_settings,
    ).publish_product(db_session, niche, product, decision)
    assert published == 1
    rows = list_publications(db_session)
    assert rows[0].status == "dry_run"
    assert rows[0].link_used == "https://afiliado.example/oferta"


async def test_publication_respects_cycle_limit(  # type: ignore[no-untyped-def]
    db_session,
    tmp_path,
    test_settings,
) -> None:
    niche = NicheConfig(
        name="informatica",
        telegram=TelegramConfig(chat_ids=["@canal"], header="Oferta"),
        publication=PublicationConfig(max_posts_per_cycle=1, seconds_between_posts=0),
        searches=[SearchConfig(query="ssd", min_discount_percent=10, include_words=["ssd"])],
    )
    niche_row = sync_niche_config(db_session, niche)
    service = PublicationService(
        DatabaseAffiliateLinkProvider(tmp_path / "pending.csv"),
        None,
        test_settings,
    )
    products = [
        ProductCandidate(
            product_id="MLB123456789",
            canonical_url="https://produto.mercadolivre.com.br/MLB-123456789-produto-_JM",
            title="SSD NVMe 1TB",
            current_price=Decimal("400"),
            original_price=Decimal("500"),
            discount_percent=20,
            free_shipping=True,
        ),
        ProductCandidate(
            product_id="MLB987654321",
            canonical_url="https://produto.mercadolivre.com.br/MLB-987654321-produto-_JM",
            title="SSD SATA 2TB",
            current_price=Decimal("450"),
            original_price=Decimal("600"),
            discount_percent=25,
            free_shipping=True,
        ),
    ]
    for product in products:
        upsert_affiliate_link(
            db_session,
            product.marketplace,
            product.product_id,
            product.canonical_url,
            f"https://afiliado.example/{product.product_id}",
            niche_row.id,
        )
    decision = OfferService().evaluate(db_session, products[0], niche.searches[0])
    assert await service.publish_product(db_session, niche, products[0], decision) == 1
    decision = OfferService().evaluate(db_session, products[1], niche.searches[0])
    assert await service.publish_product(db_session, niche, products[1], decision) == 0
