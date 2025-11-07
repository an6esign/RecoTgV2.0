FROM python:3.11-slim

WORKDIR /app

COPY alembic.ini .
COPY migrations ./migrations
COPY src ./src

RUN rm -f /etc/pip.conf $PIP_CONFIG_FILE || true \
    && python -m pip install --no-cache-dir --upgrade pip \
    && PIP_REQUIRE_HASHES= pip install --no-cache-dir \
    "alembic==1.13.3" \
    "SQLAlchemy[asyncio]==2.0.36" \
    "asyncpg==0.29.0"

ENV PYTHONUNBUFFERED=1

CMD ["alembic", "upgrade", "head"]
