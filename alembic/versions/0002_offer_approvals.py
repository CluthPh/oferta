"""offer approvals

Revision ID: 0002_offer_approvals
Revises: 0001_initial
Create Date: 2026-07-11
"""
from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "0002_offer_approvals"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "offer_approvals",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("marketplace", sa.String(length=40), nullable=False),
        sa.Column("product_id", sa.String(length=80), nullable=False),
        sa.Column("niche_name", sa.String(length=120), nullable=False),
        sa.Column("search_query", sa.String(length=240), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("note", sa.Text(), nullable=False),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_offer_approvals_marketplace", "offer_approvals", ["marketplace"])
    op.create_index("ix_offer_approvals_product_id", "offer_approvals", ["product_id"])
    op.create_index(
        "ix_offer_approvals_product",
        "offer_approvals",
        ["marketplace", "product_id"],
    )
    op.create_index("ix_offer_approvals_niche", "offer_approvals", ["niche_name"])
    op.create_index("ix_offer_approvals_niche_name", "offer_approvals", ["niche_name"])
    op.create_index("ix_offer_approvals_status", "offer_approvals", ["status"])


def downgrade() -> None:
    op.drop_table("offer_approvals")
