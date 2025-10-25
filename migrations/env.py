from logging.config import fileConfig
import os
import sys

from alembic import context
from sqlalchemy import engine_from_config, pool

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# >>> ВАЖНО: насильно добавить /app и /app/src в sys.path <<<
# Это гарантирует, что внутри контейнера питон увидит модуль `src`
project_root = "/app"
src_root = "/app/src"

if project_root not in sys.path:
    sys.path.insert(0, project_root)

if src_root not in sys.path:
    sys.path.insert(0, src_root)
    
from src.services.auth.app.db import Base
from src.services.auth.app.settings import settings

from src.services.auth.app import models 

target_metadata = Base.metadata

def run_migrations_offline():
    """
    Offline режим: генерируем SQL без прямого подключения.
    """
    url = settings.DATABASE_URL  # sync URL для alembic
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    from sqlalchemy import create_engine

    connectable = create_engine(settings.DATABASE_URL)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()