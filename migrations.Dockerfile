FROM python:3.11-slim

WORKDIR /app

COPY alembic.ini .
COPY migrations ./migrations
COPY src ./src

RUN pip install --no-cache-dir alembic sqlalchemy[asyncio] asyncpg

ENV PYTHONUNBUFFERED=1

CMD ["alembic", "upgrade", "head"]
