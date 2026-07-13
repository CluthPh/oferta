from __future__ import annotations

from app.core.constants import TELEGRAM_PHOTO_CAPTION_LIMIT, TELEGRAM_TEXT_LIMIT
from app.schemas.niche import TelegramConfig
from app.schemas.product import ProductCandidate
from app.utils.money import format_brl
from app.utils.text import escape_html, truncate_text


def format_offer_html(product: ProductCandidate, config: TelegramConfig) -> str:
    title_limit = 140 if config.short_caption else 260
    lines = [
        escape_html(config.header),
        "",
        f"<b>{escape_html(truncate_text(product.title, title_limit))}</b>",
        "",
    ]
    if config.show_original_price and product.original_price and product.discount_percent:
        lines.append(f"De: <s>{format_brl(product.original_price)}</s>")
    lines.append(f"Por: <b>{format_brl(product.current_price)}</b>")
    if config.show_discount and product.discount_percent is not None:
        lines.append(f"Desconto: {product.discount_percent:.0f}%")
    if config.show_shipping:
        lines.append("Frete gratis" if product.free_shipping else "Frete conforme anuncio")
    if config.show_seller and product.seller_name:
        lines.append(f"Vendido por: {escape_html(product.seller_name)}")
    if config.footer:
        lines.extend(["", *[escape_html(line) for line in config.footer]])
    if config.hashtags:
        lines.append("")
        lines.append(" ".join(f"#{escape_html(tag.lstrip('#'))}" for tag in config.hashtags))
    if config.show_warning:
        lines.extend(["", "Preco e disponibilidade podem mudar sem aviso."])
    return "\n".join(line for line in lines if line is not None).strip()


def fit_caption(message: str, product: ProductCandidate, config: TelegramConfig) -> str:
    if len(message) <= TELEGRAM_PHOTO_CAPTION_LIMIT:
        return message
    compact_config = config.model_copy(update={"short_caption": True, "show_seller": False})
    for title_limit in (160, 120, 80, 50):
        candidate = format_offer_html(
            product.model_copy(update={"title": truncate_text(product.title, title_limit)}),
            compact_config,
        )
        if len(candidate) <= TELEGRAM_PHOTO_CAPTION_LIMIT:
            return candidate
    final = format_offer_html(
        product.model_copy(update={"title": truncate_text(product.title, 40)}),
        compact_config.model_copy(
            update={
                "footer": [],
                "hashtags": [],
                "show_shipping": False,
                "show_discount": False,
                "show_warning": True,
            }
        ),
    )
    if len(final) <= TELEGRAM_PHOTO_CAPTION_LIMIT:
        return final
    return "Preco e disponibilidade podem mudar sem aviso."


def fit_text(message: str) -> str:
    if len(message) <= TELEGRAM_TEXT_LIMIT:
        return message
    return truncate_text(message, TELEGRAM_TEXT_LIMIT)
