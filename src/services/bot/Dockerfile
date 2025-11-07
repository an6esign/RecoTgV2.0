# syntax=docker/dockerfile:1.6
FROM python:3.11-slim

ENV PIP_DEFAULT_TIMEOUT=120 \
    PIP_RETRIES=10 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.8.3

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip && pip install "poetry==$POETRY_VERSION"

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=cache,target=/root/.cache/pypoetry \
    bash -euxo pipefail -c '\
    poetry config virtualenvs.create false; \
    for i in {1..5}; do \
    poetry install --no-root --only main --no-interaction && exit 0; \
    echo "poetry install failed, retry $i"; sleep $((i*5)); \
    done; exit 1'

COPY . .

CMD ["python", "-m", "src.services.bot.app.main"]
