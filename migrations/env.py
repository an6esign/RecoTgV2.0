from __future__ import annotations
import os, sys, pathlib
from logging.config import fileConfig
from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

# Позволяем импортировать src/*
ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from src.services.auth.app.db_base import Base  # noqa
from src.services.etl.app.db_base import Base  # noqa

# ВАЖНО: импортируем модели всех сервисов, чтобы они были в metadata
import src.services.auth.app.models  # noqa
import src.services.etl.app.models.channel  # noqa

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

DATABASE_URL = os.getenv("DATABASE_URL") or config.get_main_option("sqlalchemy.url")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

target_metadata = Base.metadata

def include_object(obj, name, type_, reflected, compare_to):
    # Если хочешь мигрировать строго ограниченный набор таблиц:
    # return name in {"users", "channels", "channel_stats"} if type_ == "table" else True
    return True

def run_migrations_offline() -> None:
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        compare_server_default=True,
        include_object=include_object,
    )
    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
        include_object=include_object,
    )
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    connectable = create_async_engine(DATABASE_URL, poolclass=pool.NullPool)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    import asyncio
    asyncio.run(run_migrations_online())
