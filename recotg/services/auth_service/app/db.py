from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from settings import settings

ASYNC_URL = settings.DATABASE_URL.replace("+psycopg2", "+asyncpg")
engine = create_async_engine(ASYNC_URL, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
Base = declarative_base()