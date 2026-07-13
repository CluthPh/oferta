from decimal import Decimal

import pytest

from app.core.exceptions import SecurityError
from app.marketplaces.mercadolivre.parsers import extract_product_id
from app.utils.money import format_brl, parse_brl
from app.utils.urls import strip_tracking_params, validate_mercadolivre_url


def test_parse_and_format_brl() -> None:
    assert parse_brl("R$ 1.234,56") == Decimal("1234.56")
    assert parse_brl(99.9) == Decimal("99.90")
    assert format_brl(Decimal("1234.56")) == "R$ 1.234,56"


def test_extract_product_id() -> None:
    url = "https://produto.mercadolivre.com.br/MLB-123456789-produto-_JM"
    assert extract_product_id(url) == "MLB123456789"
    assert extract_product_id("MLB123456789") == "MLB123456789"


def test_url_validation_blocks_unknown_hosts() -> None:
    with pytest.raises(SecurityError):
        validate_mercadolivre_url("https://example.com/MLB-123456789")


def test_strip_tracking_params() -> None:
    url = "https://produto.mercadolivre.com.br/MLB-123456789-produto-_JM?utm_source=x&foo=bar"
    assert strip_tracking_params(url).endswith("?foo=bar")
