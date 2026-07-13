from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from app.core.constants import PRICE_CHANGE_MODES


class TelegramConfig(BaseModel):
    chat_ids: list[str] = Field(default_factory=list)
    header: str = ""
    footer: list[str] = Field(default_factory=list)
    button_text: str = "VER OFERTA"
    hashtags: list[str] = Field(default_factory=list)
    show_seller: bool = True
    show_shipping: bool = True
    show_discount: bool = True
    show_original_price: bool = True
    show_warning: bool = True
    short_caption: bool = False
    topic_id: int | None = None

    @field_validator("chat_ids")
    @classmethod
    def require_chat_id(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("telegram.chat_ids deve conter ao menos um canal")
        return value


class PublicationConfig(BaseModel):
    max_posts_per_cycle: int = 3
    seconds_between_posts: float = 5
    repost_after_hours: int = 168
    min_price_drop_percent: float = 3
    price_change_mode: str = "repost"

    @field_validator("price_change_mode")
    @classmethod
    def valid_mode(cls, value: str) -> str:
        if value not in PRICE_CHANGE_MODES:
            raise ValueError(f"modo invalido: {value}")
        return value


class SearchConfig(BaseModel):
    query: str
    enabled: bool = True
    max_results: int = 20
    min_price: Decimal | None = None
    max_price: Decimal | None = None
    min_discount_percent: float = 0
    free_shipping_only: bool = False
    condition: str | None = None
    include_words: list[str] = Field(default_factory=list)
    exclude_words: list[str] = Field(default_factory=list)
    allowed_sellers: list[str] = Field(default_factory=list)
    blocked_sellers: list[str] = Field(default_factory=list)
    sort: str = "relevance"

    @field_validator("max_results")
    @classmethod
    def sane_max_results(cls, value: int) -> int:
        if value < 1 or value > 100:
            raise ValueError("max_results deve ficar entre 1 e 100")
        return value


class ManualProductConfig(BaseModel):
    url: str
    affiliate_url: str | None = None
    max_price: Decimal | None = None
    min_discount_percent: float = 0
    enabled: bool = True
    channels: list[str] = Field(default_factory=list)


class NicheConfig(BaseModel):
    name: str
    enabled: bool = True
    priority: int = 0
    telegram: TelegramConfig
    publication: PublicationConfig = Field(default_factory=PublicationConfig)
    searches: list[SearchConfig] = Field(default_factory=list)
    manual_products: list[ManualProductConfig] = Field(default_factory=list)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        clean = value.strip().lower()
        if not clean:
            raise ValueError("name nao pode ser vazio")
        return clean


class NichesFile(BaseModel):
    niches: list[NicheConfig]

    @field_validator("niches")
    @classmethod
    def require_niches(cls, value: list[NicheConfig]) -> list[NicheConfig]:
        if not value:
            raise ValueError("arquivo deve conter ao menos um nicho")
        return value

