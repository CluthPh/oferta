from decimal import Decimal

from app.affiliates.database_provider import DatabaseAffiliateLinkProvider
from app.database.repositories.channels import sync_niche_config
from app.schemas.configuration import load_niches_file
from app.schemas.niche import NicheConfig, TelegramConfig
from app.schemas.product import ProductCandidate
from app.telegram.formatter import fit_caption, format_offer_html


def test_formatter_escapes_html() -> None:
    product = ProductCandidate(
        product_id="MLB123",
        canonical_url="https://produto.mercadolivre.com.br/MLB-123-produto-_JM",
        title="Notebook <barato>",
        current_price=Decimal("100"),
    )
    message = format_offer_html(product, TelegramConfig(chat_ids=["@canal"], header="Oferta"))
    assert "&lt;barato&gt;" in message
    assert "<barato>" not in message


def test_caption_limit_preserves_html() -> None:
    product = ProductCandidate(
        product_id="MLB123",
        canonical_url="https://produto.mercadolivre.com.br/MLB-123-produto-_JM",
        title="Produto " * 300,
        current_price=Decimal("100"),
    )
    config = TelegramConfig(chat_ids=["@canal"], header="Oferta", footer=["x" * 1200])
    caption = fit_caption(format_offer_html(product, config), product, config)
    assert len(caption) <= 1024
    assert caption.count("<b>") == caption.count("</b>")


def test_pending_affiliate_csv_is_deduplicated(tmp_path) -> None:  # type: ignore[no-untyped-def]
    provider = DatabaseAffiliateLinkProvider(tmp_path / "pending.csv")
    product = ProductCandidate(
        product_id="MLB123",
        canonical_url="https://produto.mercadolivre.com.br/MLB-123-produto-_JM",
        title="Produto",
        current_price=Decimal("100"),
    )
    provider.register_pending_link(product, "informatica")
    provider.register_pending_link(product, "informatica")
    assert (tmp_path / "pending.csv").read_text(encoding="utf-8").count("MLB123") == 1


def test_load_niches_config(tmp_path) -> None:  # type: ignore[no-untyped-def]
    config = tmp_path / "niches.yml"
    config.write_text(
        """
niches:
  - name: informatica
    telegram:
      chat_ids:
        - "@canal"
""",
        encoding="utf-8",
    )
    loaded = load_niches_file(config)
    assert loaded.niches[0].name == "informatica"


def test_affiliate_csv_import_export(db_session, tmp_path) -> None:  # type: ignore[no-untyped-def]
    sync_niche_config(
        db_session,
        NicheConfig(name="informatica", telegram=TelegramConfig(chat_ids=["@canal"])),
    )
    source = tmp_path / "affiliate.csv"
    source.write_text(
        "\n".join(
            [
                "product_id,canonical_url,affiliate_url,niche,active",
                "MLB123,https://produto.mercadolivre.com.br/MLB-123-produto-_JM,https://afiliado,informatica,true",
            ]
        ),
        encoding="utf-8",
    )
    provider = DatabaseAffiliateLinkProvider(tmp_path / "pending.csv")
    assert provider.import_csv(db_session, source) == 1
    exported = tmp_path / "exported.csv"
    assert provider.export_csv(db_session, exported) == 1
    assert "informatica" in exported.read_text(encoding="utf-8")
