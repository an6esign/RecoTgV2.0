
# syntax=docker/dockerfile:1.6
FROM python:3.11-slim

ENV PIP_DEFAULT_TIMEOUT=120 \
    PIP_RETRIES=10 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=1.8.3

# базовые тулзы для сборки колес (на случай отсутствия manylinux)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl ca-certificates gcc && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip && pip install "poetry==$POETRY_VERSION"

WORKDIR /app

# сначала манифесты — чтобы кэшировать слой зависимостей
COPY pyproject.toml poetry.lock ./

# установка зависимостей с ретраями и кэшем
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=cache,target=/root/.cache/pypoetry \
    bash -euxo pipefail -c '\
    poetry config virtualenvs.create false; \
    for i in {1..5}; do \
    poetry install --no-root --only main --no-interaction && exit 0; \
    echo "poetry install failed, retry $i"; sleep $((i*5)); \
    done; exit 1'

# теперь исходники
COPY src /app/src
COPY alembic.ini .
COPY migrations ./migrations

# если у тебя uvicorn в зависимостях:
EXPOSE 8000
CMD ["uvicorn", "src.services.auth.app.main:app", "--host", "0.0.0.0", "--port", "8000"]

