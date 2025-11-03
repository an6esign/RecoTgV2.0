"""update users scheme

Revision ID: dccc27c4f4db
Revises: 003e104121d7
Create Date: 2025-11-03 13:39:44.903344

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'dccc27c4f4db'
down_revision: Union[str, Sequence[str], None] = '003e104121d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # --- 1) Переименования колонок (если уже переименованы — пропустится) ---
    with op.batch_alter_table("users", schema=None) as batch:
        # tg_id -> telegram_user_id
        try:
            batch.alter_column("tg_id", new_column_name="telegram_user_id")
        except Exception:
            pass

        # phone -> phone_number
        try:
            batch.alter_column("phone", new_column_name="phone_number")
        except Exception:
            pass

    # --- 2) Создаём Enum для подписки ---
    # Если тип уже существует — пропустим
    enum_name = "subscriptiontier"
    try:
        postgresql.ENUM("free", "standard", "premium", name=enum_name).create(op.get_bind(), checkfirst=True)
    except Exception:
        pass

    # --- 3) Добавляем новые колонки ---
    with op.batch_alter_table("users", schema=None) as batch:
        # subscription_tier
        batch.add_column(
            sa.Column(
                "subscription_tier",
                sa.Enum("free", "standard", "premium", name=enum_name),
                nullable=False,
                server_default=sa.text("'free'"),
            )
        )
        # is_subscription_active
        batch.add_column(
            sa.Column("is_subscription_active", sa.Boolean(), nullable=False, server_default=sa.text("false"))
        )
        # subscription_expires_at
        batch.add_column(
            sa.Column("subscription_expires_at", postgresql.TIMESTAMP(timezone=True), nullable=True)
        )

        # created_at / updated_at — гарантируем server_default=now()
        try:
            batch.alter_column(
                "created_at",
                existing_type=postgresql.TIMESTAMP(timezone=True),
                server_default=sa.text("now()"),
                existing_nullable=False,
            )
        except Exception:
            pass
        try:
            batch.alter_column(
                "updated_at",
                existing_type=postgresql.TIMESTAMP(timezone=True),
                server_default=sa.text("now()"),
                existing_nullable=False,
            )
        except Exception:
            pass

        # is_active — убедимся, что NOT NULL и default True
        try:
            batch.alter_column(
                "is_active",
                existing_type=sa.Boolean(),
                nullable=False,
                server_default=sa.text("true"),
            )
        except Exception:
            pass

    # --- 4) Индексы/уники под новую схему ---

    # Снимем старые индексы/уники, если были (без падений)
    # tg_id → telegram_user_id
    op.execute("DROP INDEX IF EXISTS ix_users_tg_id")
    op.execute("ALTER TABLE users DROP CONSTRAINT IF EXISTS uq_users_tg_id")

    # phone → phone_number
    op.execute("DROP INDEX IF EXISTS ix_users_phone")
    op.execute("ALTER TABLE users DROP CONSTRAINT IF EXISTS uq_users_phone")
    op.execute("DROP INDEX IF EXISTS ix_users_phone_number")
    op.execute("ALTER TABLE users DROP CONSTRAINT IF EXISTS uq_users_phone_number")

    # username/full_name — если эти колонки больше не используются, можно удалить уники/индексы
    op.execute("ALTER TABLE users DROP CONSTRAINT IF EXISTS uq_users_username")
    op.execute("DROP INDEX IF EXISTS ix_users_username")

    # Создадим уники и индексы для новых колонок
    op.create_unique_constraint("uq_users_telegram_user_id", "users", ["telegram_user_id"])
    op.create_index("ix_users_telegram_user_id", "users", ["telegram_user_id"], unique=False)

    op.create_unique_constraint("uq_users_phone_number", "users", ["phone_number"])
    op.create_index("ix_users_phone_number", "users", ["phone_number"], unique=False)

    # --- 5) (Опционально) Удаляем больше не нужные поля ---
    # Раскомментируй, если точно не нужны:
    # with op.batch_alter_table("users", schema=None) as batch:
    #     for col in ("username", "full_name"):
    #         try:
    #             batch.drop_column(col)
    #         except Exception:
    #             pass


def downgrade():
    # Откат: возвращаем всё как было

    # Индексы/уники новых полей
    op.drop_index("ix_users_phone_number", table_name="users")
    op.drop_constraint("uq_users_phone_number", "users", type_="unique")

    op.drop_index("ix_users_telegram_user_id", table_name="users")
    op.drop_constraint("uq_users_telegram_user_id", "users", type_="unique")

    # Новые колонки
    with op.batch_alter_table("users", schema=None) as batch:
        batch.drop_column("subscription_expires_at")
        batch.drop_column("is_subscription_active")
        batch.drop_column("subscription_tier")

    # Enum тип
    try:
        postgresql.ENUM(name="subscriptiontier").drop(op.get_bind(), checkfirst=True)
    except Exception:
        pass

    # Переименования назад
    with op.batch_alter_table("users", schema=None) as batch:
        try:
            batch.alter_column("telegram_user_id", new_column_name="tg_id")
        except Exception:
            pass
        try:
            batch.alter_column("phone_number", new_column_name="phone")
        except Exception:
            pass

    # Вернём старые индексы/уники (по желанию)
    op.create_unique_constraint("uq_users_tg_id", "users", ["tg_id"])
    op.create_index("ix_users_tg_id", "users", ["tg_id"], unique=False)

    op.create_index("ix_users_phone", "users", ["phone"], unique=False)
    # оставляю без уникальности для phone на даунгрейде — подстрой при необходимости
