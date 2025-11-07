"""create posts table

Revision ID: 434576d6ccb0
Revises: dccc27c4f4db
Create Date: 2025-11-05 11:45:01.582239

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '434576d6ccb0'
down_revision: Union[str, Sequence[str], None] = 'dccc27c4f4db'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "posts",
        sa.Column("username", sa.String(length=255), nullable=False),
        sa.Column("message_id", sa.BigInteger(), nullable=False),
        sa.Column("posted_at", sa.DateTime(timezone=False), nullable=False),
        sa.Column("text", sa.Text(), nullable=True),

        # MVP: метрики "на момент сбора"
        sa.Column("views_now", sa.Integer(), nullable=True),
        sa.Column("forwards_now", sa.Integer(), nullable=True),
        sa.Column("replies_now", sa.Integer(), nullable=True),
        sa.Column("reactions_now", sa.Integer(), nullable=True),

        sa.Column("collected_at", sa.DateTime(timezone=False), server_default=sa.text("NOW()"), nullable=False),

        sa.PrimaryKeyConstraint("username", "message_id", name="pk_posts"),
        sa.ForeignKeyConstraint(["username"], ["channels.username"], ondelete="CASCADE"),
    )
    op.create_index("ix_posts_user_date", "posts", ["username", "posted_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_posts_user_date", table_name="posts")
    op.drop_table("posts")