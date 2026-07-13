from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from urllib.parse import urlparse

from app.core.constants import MARKETPLACE_MERCADOLIVRE
from app.core.exceptions import MarketplaceError
from app.schemas.product import ProductCandidate, calculate_discount
from app.utils.money import parse_brl
from app.utils.urls import strip_tracking_params, validate_mercadolivre_url

PRODUCT_ID_RE = re.compile(r"\b(MLB)-?(\d{6,})\b", re.IGNORECASE)
JSON_LD_RE = re.compile(
    r"<script[^>]+type=[\"']application/ld\+json[\"'][^>]*>(.*?)</script>",
    re.IGNORECASE | re.DOTALL,
)


def extract_product_id(value: str) -> str:
    match = PRODUCT_ID_RE.search(value)
    if not match:
        raise MarketplaceError(f"Nao foi possivel extrair product_id de: {value}")
    return f"{match.group(1).upper()}{match.group(2)}"


def canonicalize_url(url: str) -> str:
    validate_mercadolivre_url(url)
    parsed = urlparse(strip_tracking_params(url))
    path = parsed.path
    product_id = extract_product_id(url)
    if "produto.mercadolivre.com.br" in parsed.netloc:
        suffix = path[path.find("-") :] if "-" in path else ""
        return f"https://produto.mercadolivre.com.br/{product_id[:3]}-{product_id[3:]}{suffix}"
    return strip_tracking_params(url)


def normalize_item_json(raw: dict[str, Any], description: str = "") -> ProductCandidate:
    product_id = str(raw.get("id") or "")
    if not product_id:
        raise MarketplaceError("Resposta do Mercado Livre sem id")
    seller = raw.get("seller") or {}
    shipping = raw.get("shipping") or {}
    price = parse_brl(raw.get("price"))
    original = parse_brl(raw.get("original_price"))
    pictures = raw.get("pictures") or []
    image_url = raw.get("secure_thumbnail") or raw.get("thumbnail") or ""
    if pictures and isinstance(pictures[0], dict):
        image_url = str(pictures[0].get("secure_url") or pictures[0].get("url") or image_url)
    seller_id = str(raw.get("seller_id") or seller.get("id") or "")
    seller_name = str(
        seller.get("nickname") or raw.get("seller_name") or raw.get("official_store_name") or ""
    )
    official_store = bool(raw.get("official_store_id") or raw.get("official_store_name"))
    now = datetime.now(UTC)
    return ProductCandidate(
        marketplace=MARKETPLACE_MERCADOLIVRE,
        product_id=product_id,
        canonical_url=strip_tracking_params(str(raw.get("permalink") or "")),
        title=str(raw.get("title") or ""),
        description=description,
        current_price=price,
        original_price=original,
        discount_percent=calculate_discount(original, price),
        currency=str(raw.get("currency_id") or "BRL"),
        image_url=image_url.replace("http://", "https://"),
        seller_id=seller_id,
        seller_name=seller_name,
        official_store=official_store,
        free_shipping=bool(shipping.get("free_shipping")),
        condition=str(raw.get("condition") or ""),
        available_quantity=raw.get("available_quantity"),
        sold_quantity=raw.get("sold_quantity"),
        category_id=str(raw.get("category_id") or ""),
        discovered_at=now,
        collected_at=now,
    )


def parse_json_ld_product(html: str, url: str) -> ProductCandidate:
    for match in JSON_LD_RE.finditer(html):
        payload = match.group(1).strip()
        try:
            parsed = json.loads(payload)
        except json.JSONDecodeError:
            continue
        items = parsed if isinstance(parsed, list) else [parsed]
        for item in items:
            item_type = item.get("@type") if isinstance(item, dict) else None
            is_product = item_type == "Product" or (
                isinstance(item_type, list) and "Product" in item_type
            )
            if not isinstance(item, dict) or not is_product:
                continue
            offers = item.get("offers") or {}
            if isinstance(offers, list):
                offers = offers[0] if offers else {}
            price = parse_brl(offers.get("price") if isinstance(offers, dict) else None)
            image = item.get("image") or ""
            if isinstance(image, list):
                image = image[0] if image else ""
            product_id = extract_product_id(url)
            return ProductCandidate(
                product_id=product_id,
                canonical_url=canonicalize_url(url),
                title=str(item.get("name") or ""),
                description=str(item.get("description") or ""),
                current_price=price,
                original_price=None,
                discount_percent=None,
                image_url=str(image),
                seller_name="",
            )
    raise MarketplaceError("JSON-LD de produto nao encontrado na pagina")


def decimal_to_api(value: Decimal | None) -> str | None:
    if value is None:
        return None
    return str(value.quantize(Decimal("0.01")))
