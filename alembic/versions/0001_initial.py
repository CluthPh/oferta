"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-07-10
"""
from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "niches",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("header", sa.Text(), nullable=False),
        sa.Column("footer", sa.Text(), nullable=False),
        sa.Column("button_text", sa.String(length=80), nullable=False),
        sa.Column("hashtags", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_niches_name", "niches", ["name"], unique=True)
    op.create_table(
        "channels",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("niche_id", sa.Integer(), sa.ForeignKey("niches.id"), nullable=False),
        sa.Column("chat_id", sa.String(length=180), nullable=False),
        sa.Column("topic_id", sa.Integer(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("niche_id", "chat_id", name="uq_channel_niche_chat"),
    )
    op.create_index("ix_channels_chat_id", "channels", ["chat_id"])
    op.create_index("ix_channels_niche_id", "channels", ["niche_id"])
    op.create_table(
        "search_rules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("niche_id", sa.Integer(), sa.ForeignKey("niches.id"), nullable=False),
        sa.Column("query", sa.String(length=240), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("max_results", sa.Integer(), nullable=False),
        sa.Column("min_price", sa.Numeric(12, 2), nullable=True),
        sa.Column("max_price", sa.Numeric(12, 2), nullable=True),
        sa.Column("min_discount_percent", sa.Float(), nullable=False),
        sa.Column("free_shipping_only", sa.Boolean(), nullable=False),
        sa.Column("condition", sa.String(length=30), nullable=True),
        sa.Column("include_words", sa.Text(), nullable=False),
        sa.Column("exclude_words", sa.Text(), nullable=False),
        sa.Column("allowed_sellers", sa.Text(), nullable=False),
        sa.Column("blocked_sellers", sa.Text(), nullable=False),
        sa.Column("sort", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_search_rules_niche_id", "search_rules", ["niche_id"])
    op.create_table(
        "sellers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("marketplace", sa.String(length=40), nullable=False),
        sa.Column("seller_id", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=220), nullable=False),
        sa.Column("official_store", sa.Boolean(), nullable=False),
        sa.Column("reputation", sa.String(length=80), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("marketplace", "seller_id", name="uq_seller_marketplace_id"),
    )
    op.create_index("ix_sellers_marketplace", "sellers", ["marketplace"])
    op.create_index("ix_sellers_seller_id", "sellers", ["seller_id"])
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("marketplace", sa.String(length=40), nullable=False),
        sa.Column("product_id", sa.String(length=80), nullable=False),
        sa.Column("canonical_url", sa.Text(), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("current_price", sa.Numeric(12, 2), nullable=True),
        sa.Column("original_price", sa.Numeric(12, 2), nullable=True),
        sa.Column("discount_percent", sa.Float(), nullable=True),
        sa.Column("currency", sa.String(length=10), nullable=False),
        sa.Column("image_url", sa.Text(), nullable=False),
        sa.Column("seller_id", sa.String(length=80), nullable=False),
        sa.Column("seller_name", sa.String(length=220), nullable=False),
        sa.Column("official_store", sa.Boolean(), nullable=False),
        sa.Column("free_shipping", sa.Boolean(), nullable=False),
        sa.Column("condition", sa.String(length=30), nullable=False),
        sa.Column("available_quantity", sa.Integer(), nullable=True),
        sa.Column("sold_quantity", sa.Integer(), nullable=True),
        sa.Column("category_id", sa.String(length=80), nullable=False),
        sa.Column("discovered_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("collected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ignored", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("marketplace", "product_id", name="uq_product_marketplace_id"),
    )
    op.create_index("ix_products_collected_at", "products", ["collected_at"])
    op.create_index("ix_products_marketplace", "products", ["marketplace"])
    op.create_index("ix_products_marketplace_product", "products", ["marketplace", "product_id"])
    op.create_index("ix_products_product_id", "products", ["product_id"])
    op.create_table(
        "price_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("marketplace", sa.String(length=40), nullable=False),
        sa.Column("product_id", sa.String(length=80), nullable=False),
        sa.Column("price", sa.Numeric(12, 2), nullable=True),
        sa.Column("original_price", sa.Numeric(12, 2), nullable=True),
        sa.Column("collected_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_price_history_collected_at", "price_history", ["collected_at"])
    op.create_index("ix_price_history_marketplace", "price_history", ["marketplace"])
    op.create_index(
        "ix_price_history_product_collected",
        "price_history",
        ["product_id", "collected_at"],
    )
    op.create_index("ix_price_history_product_id", "price_history", ["product_id"])
    op.create_table(
        "affiliate_links",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("marketplace", sa.String(length=40), nullable=False),
        sa.Column("product_id", sa.String(length=80), nullable=False),
        sa.Column("canonical_url", sa.Text(), nullable=False),
        sa.Column("affiliate_url", sa.Text(), nullable=False),
        sa.Column("niche_id", sa.Integer(), sa.ForeignKey("niches.id"), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "marketplace",
            "product_id",
            "niche_id",
            name="uq_affiliate_product_niche",
        ),
    )
    op.create_index("ix_affiliate_links_marketplace", "affiliate_links", ["marketplace"])
    op.create_index("ix_affiliate_links_niche_id", "affiliate_links", ["niche_id"])
    op.create_index("ix_affiliate_links_product_id", "affiliate_links", ["product_id"])
    op.create_table(
        "publications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("marketplace", sa.String(length=40), nullable=False),
        sa.Column("product_id", sa.String(length=80), nullable=False),
        sa.Column("channel_id", sa.String(length=180), nullable=False),
        sa.Column("telegram_message_id", sa.Integer(), nullable=True),
        sa.Column("published_price", sa.Numeric(12, 2), nullable=True),
        sa.Column("link_used", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("dry_run", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_publications_channel_id", "publications", ["channel_id"])
    op.create_index("ix_publications_product_channel", "publications", ["product_id", "channel_id"])
    op.create_index("ix_publications_product_id", "publications", ["product_id"])
    op.create_index("ix_publications_published_at", "publications", ["published_at"])
    op.create_index("ix_publications_status", "publications", ["status"])
    op.create_table(
        "scan_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("collected_count", sa.Integer(), nullable=False),
        sa.Column("approved_count", sa.Integer(), nullable=False),
        sa.Column("published_count", sa.Integer(), nullable=False),
        sa.Column("ignored_count", sa.Integer(), nullable=False),
        sa.Column("error_count", sa.Integer(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=False),
    )
    op.create_table(
        "application_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("level", sa.String(length=20), nullable=False),
        sa.Column("module", sa.String(length=120), nullable=False),
        sa.Column("action", sa.String(length=120), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_application_events_created_at", "application_events", ["created_at"])
    op.create_index("ix_application_events_level", "application_events", ["level"])


def downgrade() -> None:
    op.drop_table("application_events")
    op.drop_table("scan_runs")
    op.drop_table("publications")
    op.drop_table("affiliate_links")
    op.drop_table("price_history")
    op.drop_table("products")
    op.drop_table("sellers")
    op.drop_table("search_rules")
    op.drop_table("channels")
    op.drop_table("niches")
