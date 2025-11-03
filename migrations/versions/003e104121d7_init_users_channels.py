"""init users+channels

Revision ID: 003e104121d7
Revises: 
Create Date: 2025-11-01 12:20:41.059390

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '003e104121d7'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tg_id", sa.BigInteger(), nullable=False),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("username", sa.String(length=255), nullable=True),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", postgresql.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("tg_id", name="uq_users_tg_id"),
        sa.UniqueConstraint("username", name="uq_users_username"),
    )
    op.create_index("ix_users_tg_id", "users", ["tg_id"], unique=False)
    op.create_index("ix_users_phone", "users", ["phone"], unique=False)
    op.create_index("ix_users_username", "users", ["username"], unique=False)

    # channels (PK = username)
    op.create_table(
        "channels",
        sa.Column("username", sa.String(length=255), primary_key=True),
        sa.Column("channel", sa.String(length=512), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("image", sa.String(length=512), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("country", sa.String(length=50), nullable=True),
        sa.Column("subscribers", sa.Integer(), nullable=True),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", postgresql.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("channel", name="uq_channels_channel"),
    )
    op.create_index("ix_channels_category", "channels", ["category"], unique=False)
    op.create_index("ix_channels_country", "channels", ["country"], unique=False)

    # channel_stats (PK = username+date, FK -> channels.username)
    op.create_table(
        "channel_stats",
        sa.Column("username", sa.String(length=255), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("subscribers", sa.Integer(), nullable=True),
        sa.Column("subscribers_day_delta", sa.Integer(), nullable=True),
        sa.Column("subscribers_week_delta", sa.Integer(), nullable=True),
        sa.Column("subscribers_month_delta", sa.Integer(), nullable=True),
        sa.Column("citation_index", sa.Integer(), nullable=True),
        sa.Column("mentioned_channels", sa.Integer(), nullable=True),
        sa.Column("mentions", sa.Integer(), nullable=True),
        sa.Column("reposts", sa.Integer(), nullable=True),
        sa.Column("avg_reach", sa.Integer(), nullable=True),
        sa.Column("avg_reach_ads", sa.Integer(), nullable=True),
        sa.Column("avg_views_12h", sa.Integer(), nullable=True),
        sa.Column("avg_views_24h", sa.Integer(), nullable=True),
        sa.Column("avg_views_48h", sa.Integer(), nullable=True),
        sa.Column("err", sa.Float(), nullable=True),
        sa.Column("err24", sa.Float(), nullable=True),
        sa.Column("engagement_rate", sa.Float(), nullable=True),
        sa.Column("forwards", sa.Integer(), nullable=True),
        sa.Column("comments", sa.Integer(), nullable=True),
        sa.Column("reactions", sa.Integer(), nullable=True),
        sa.Column("posts_total", sa.Integer(), nullable=True),
        sa.Column("posts_day", sa.Integer(), nullable=True),
        sa.Column("posts_week", sa.Integer(), nullable=True),
        sa.Column("posts_month", sa.Integer(), nullable=True),
        sa.Column("collected_at", postgresql.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("username", "date", name="pk_channel_stats"),
        sa.ForeignKeyConstraint(["username"], ["channels.username"], name="fk_channel_stats_username__channels", ondelete="CASCADE"),
        sa.UniqueConstraint("username", "date", name="uq_channel_stats_day"),
    )
    op.create_index("ix_channel_stats_date", "channel_stats", ["date"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_channel_stats_date", table_name="channel_stats")
    op.drop_table("channel_stats")

    op.drop_index("ix_channels_category", table_name="channels")
    op.drop_index("ix_channels_country", table_name="channels")
    op.drop_table("channels")

    op.drop_index("ix_users_tg_id", table_name="users")
    op.drop_index("ix_users_phone", table_name="users")
    op.drop_index("ix_users_username", table_name="users")
    op.drop_table("users")
