FROM python:3.11-slim

RUN pip install --no-cache-dir poetry==1.8.3

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

COPY src ./src

CMD ["uvicorn", "src.services.auth.app.main:app", "--host", "0.0.0.0", "--port", "8001"]
