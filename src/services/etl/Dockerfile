# syntax=docker/dockerfile:1.6
FROM python:3.11-slim

ENV POETRY_VERSION=1.8.3 \
    PIP_DEFAULT_TIMEOUT=120 \
    PIP_RETRIES=10 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl ca-certificates && rm -rf /var/lib/apt/lists/*

RUN pip install -U pip && pip install "poetry==$POETRY_VERSION"

WORKDIR /app
COPY pyproject.toml poetry.lock ./

ENV PYTHONPATH=/app

RUN --mount=type=cache,target=/root/.cache/pip \
    bash -euxo pipefail -c '\
    for i in {1..5}; do \
    pip install --only-binary=:all: numpy==2.3.4 pandas==2.3.3 && exit 0; \
    echo "warm-up pip failed, retry $i"; sleep $((i*7)); \
    done; exit 1'

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=cache,target=/root/.cache/pypoetry \
    bash -euxo pipefail -c '\
    poetry config virtualenvs.create false; \
    for i in {1..5}; do \
    poetry install --no-interaction --no-ansi --no-root --only main && exit 0; \
    echo "poetry install failed, retry $i"; sleep $((i*7)); \
    done; exit 1'

COPY . .
