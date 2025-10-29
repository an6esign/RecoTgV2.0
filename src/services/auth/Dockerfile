FROM python:3.11-slim

WORKDIR /app

# Скопировать файлы зависимостей
COPY pyproject.toml poetry.lock* requirements.txt* /app/

# Установка зависимостей
RUN pip install poetry && poetry config virtualenvs.create false && poetry install --no-root

# Скопировать исходники проекта
COPY src /app/src
COPY alembic.ini .
COPY migrations ./migrations

# чтобы python видел твой пакет src
ENV PYTHONPATH=/app

# Контейнер будет по умолчанию запускать uvicorn;
# docker-compose потом может переписать CMD через `command:`
CMD ["uvicorn", "src.services.auth.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
