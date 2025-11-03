import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool

from .db_base import Base

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set")
ASYNC_DATABASE_URL = DATABASE_URL if "+asyncpg" in DATABASE_URL else DATABASE_URL.replace("+psycopg2", "+asyncpg")

engine = create_async_engine(
    ASYNC_DATABASE_URL,
    pool_pre_ping=True,
    poolclass=NullPool,
    echo=False,
    future=True,
)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

async def get_db():
    async with SessionLocal() as session:
        yield session
