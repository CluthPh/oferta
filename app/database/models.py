from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )


class Niche(Base, TimestampMixin):
    __tablename__ = "niches"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    priority: Mapped[int] = mapped_column(default=0)
    header: Mapped[str] = mapped_column(Text, default="")
    footer: Mapped[str] = mapped_column(Text, default="")
    button_text: Mapped[str] = mapped_column(String(80), default="VER OFERTA")
    hashtags: Mapped[str] = mapped_column(Text, default="")

    channels: Mapped[list[Channel]] = relationship(
        back_populates="niche",
        cascade="all, delete-orphan",
    )
    searches: Mapped[list[SearchRule]] = relationship(
        back_populates="niche",
        cascade="all, delete-orphan",
    )


class Channel(Base, TimestampMixin):
    __tablename__ = "channels"
    __table_args__ = (UniqueConstraint("niche_id", "chat_id", name="uq_channel_niche_chat"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    niche_id: Mapped[int] = mapped_column(ForeignKey("niches.id"), index=True)
    chat_id: Mapped[str] = mapped_column(String(180), index=True)
    topic_id: Mapped[int | None] = mapped_column(nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    niche: Mapped[Niche] = relationship(back_populates="channels")


class SearchRule(Base, TimestampMixin):
    __tablename__ = "search_rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    niche_id: Mapped[int] = mapped_column(ForeignKey("niches.id"), index=True)
    query: Mapped[str] = mapped_column(String(240))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    max_results: Mapped[int] = mapped_column(default=20)
    min_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    max_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    min_discount_percent: Mapped[float] = mapped_column(default=0.0)
    free_shipping_only: Mapped[bool] = mapped_column(Boolean, default=False)
    condition: Mapped[str | None] = mapped_column(String(30), nullable=True)
    include_words: Mapped[str] = mapped_column(Text, default="")
    exclude_words: Mapped[str] = mapped_column(Text, default="")
    allowed_sellers: Mapped[str] = mapped_column(Text, default="")
    blocked_sellers: Mapped[str] = mapped_column(Text, default="")
    sort: Mapped[str] = mapped_column(String(40), default="relevance")

    niche: Mapped[Niche] = relationship(back_populates="searches")


class Seller(Base, TimestampMixin):
    __tablename__ = "sellers"

    id: Mapped[int] = mapped_column(primary_key=True)
    marketplace: Mapped[str] = mapped_column(String(40), index=True)
    seller_id: Mapped[str] = mapped_column(String(80), index=True)
    name: Mapped[str] = mapped_column(String(220), default="")
    official_store: Mapped[bool] = mapped_column(Boolean, default=False)
    reputation: Mapped[str] = mapped_column(String(80), default="")

    __table_args__ = (
        UniqueConstraint("marketplace", "seller_id", name="uq_seller_marketplace_id"),
    )


class Product(Base, TimestampMixin):
    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("marketplace", "product_id", name="uq_product_marketplace_id"),
        Index("ix_products_marketplace_product", "marketplace", "product_id"),
        Index("ix_products_collected_at", "collected_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    marketplace: Mapped[str] = mapped_column(String(40), index=True)
    product_id: Mapped[str] = mapped_column(String(80), index=True)
    canonical_url: Mapped[str] = mapped_column(Text)
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str] = mapped_column(Text, default="")
    current_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    original_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    discount_percent: Mapped[float | None] = mapped_column(nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="BRL")
    image_url: Mapped[str] = mapped_column(Text, default="")
    seller_id: Mapped[str] = mapped_column(String(80), default="")
    seller_name: Mapped[str] = mapped_column(String(220), default="")
    official_store: Mapped[bool] = mapped_column(Boolean, default=False)
    free_shipping: Mapped[bool] = mapped_column(Boolean, default=False)
    condition: Mapped[str] = mapped_column(String(30), default="")
    available_quantity: Mapped[int | None] = mapped_column(nullable=True)
    sold_quantity: Mapped[int | None] = mapped_column(nullable=True)
    category_id: Mapped[str] = mapped_column(String(80), default="")
    discovered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    ignored: Mapped[bool] = mapped_column(Boolean, default=False)


class PriceHistory(Base):
    __tablename__ = "price_history"
    __table_args__ = (
        Index("ix_price_history_product_collected", "product_id", "collected_at"),
        Index("ix_price_history_collected_at", "collected_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    marketplace: Mapped[str] = mapped_column(String(40), index=True)
    product_id: Mapped[str] = mapped_column(String(80), index=True)
    price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    original_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class AffiliateLink(Base, TimestampMixin):
    __tablename__ = "affiliate_links"
    __table_args__ = (
        UniqueConstraint(
            "marketplace",
            "product_id",
            "niche_id",
            name="uq_affiliate_product_niche",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    marketplace: Mapped[str] = mapped_column(String(40), index=True)
    product_id: Mapped[str] = mapped_column(String(80), index=True)
    canonical_url: Mapped[str] = mapped_column(Text)
    affiliate_url: Mapped[str] = mapped_column(Text)
    niche_id: Mapped[int | None] = mapped_column(ForeignKey("niches.id"), nullable=True, index=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class Publication(Base, TimestampMixin):
    __tablename__ = "publications"
    __table_args__ = (
        Index("ix_publications_product_channel", "product_id", "channel_id"),
        Index("ix_publications_published_at", "published_at"),
        Index("ix_publications_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    marketplace: Mapped[str] = mapped_column(String(40), index=True)
    product_id: Mapped[str] = mapped_column(String(80), index=True)
    channel_id: Mapped[str] = mapped_column(String(180), index=True)
    telegram_message_id: Mapped[int | None] = mapped_column(nullable=True)
    published_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    link_used: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(40))
    reason: Mapped[str] = mapped_column(Text, default="")
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    dry_run: Mapped[bool] = mapped_column(Boolean, default=False)


class OfferApproval(Base, TimestampMixin):
    __tablename__ = "offer_approvals"
    __table_args__ = (
        Index("ix_offer_approvals_status", "status"),
        Index("ix_offer_approvals_product", "marketplace", "product_id"),
        Index("ix_offer_approvals_niche", "niche_name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    marketplace: Mapped[str] = mapped_column(String(40), index=True)
    product_id: Mapped[str] = mapped_column(String(80), index=True)
    niche_name: Mapped[str] = mapped_column(String(120), index=True)
    search_query: Mapped[str] = mapped_column(String(240), default="")
    score: Mapped[int] = mapped_column(default=0)
    reason: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(40), default="pending")
    note: Mapped[str] = mapped_column(Text, default="")
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ScanRun(Base):
    __tablename__ = "scan_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    collected_count: Mapped[int] = mapped_column(default=0)
    approved_count: Mapped[int] = mapped_column(default=0)
    published_count: Mapped[int] = mapped_column(default=0)
    ignored_count: Mapped[int] = mapped_column(default=0)
    error_count: Mapped[int] = mapped_column(default=0)
    error_message: Mapped[str] = mapped_column(Text, default="")


class ApplicationEvent(Base):
    __tablename__ = "application_events"
    __table_args__ = (Index("ix_application_events_created_at", "created_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    level: Mapped[str] = mapped_column(String(20), index=True)
    module: Mapped[str] = mapped_column(String(120))
    action: Mapped[str] = mapped_column(String(120))
    message: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
