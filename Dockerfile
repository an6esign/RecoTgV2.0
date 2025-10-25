FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create false
RUN poetry install --no-root --no-interaction --no-ansi

COPY src /app/src
COPY migrations /app/migrations
COPY alembic.ini /app/alembic.ini

CMD ["uvicorn", "src.services.auth.app.main:app", "--host", "0.0.0.0", "--port", "8001"]
