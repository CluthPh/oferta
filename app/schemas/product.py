from datetime import UTC, datetime
from decimal import Decimal

from pydantic import BaseModel, Field, HttpUrl, field_validator

from app.core.constants import MARKETPLACE_MERCADOLIVRE


def calculate_discount(
    original_price: Decimal | None,
    current_price: Decimal | None,
) -> float | None:
    if original_price is None or current_price is None:
        return None
    if original_price <= 0 or current_price >= original_price:
        return None
    return round(float(((original_price - current_price) / original_price) * Decimal("100")), 2)


class ProductCandidate(BaseModel):
    marketplace: str = MARKETPLACE_MERCADOLIVRE
    product_id: str
    canonical_url: str
    title: str
    description: str = ""
    current_price: Decimal | None = None
    original_price: Decimal | None = None
    discount_percent: float | None = None
    currency: str = "BRL"
    image_url: str = ""
    seller_id: str = ""
    seller_name: str = ""
    official_store: bool = False
    free_shipping: bool = False
    condition: str = ""
    available_quantity: int | None = None
    sold_quantity: int | None = None
    category_id: str = ""
    discovered_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    collected_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("title")
    @classmethod
    def title_is_required(cls, value: str) -> str:
        clean = value.strip()
        if not clean:
            raise ValueError("title nao pode ser vazio")
        return clean

    @field_validator("canonical_url", "image_url")
    @classmethod
    def stringify_urls(cls, value: str | HttpUrl) -> str:
        return str(value)

    def with_calculated_discount(self) -> "ProductCandidate":
        value = self.model_copy()
        value.discount_percent = calculate_discount(value.original_price, value.current_price)
        return value


class ProductListItem(BaseModel):
    id: int
    marketplace: str
    product_id: str
    title: str
    current_price: Decimal | None
    original_price: Decimal | None
    discount_percent: float | None
    canonical_url: str
    image_url: str
    seller_name: str
    free_shipping: bool
    ignored: bool
    collected_at: datetime

    model_config = {"from_attributes": True}
