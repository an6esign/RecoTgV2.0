# 1) Базовый образ
FROM python:3.11-slim

# 2) Базовые настройки
ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.3

# 3) Системные зависимости (для pandas, psycopg и т.д.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 4) Poetry
RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}"

WORKDIR /app

# 5) Кэшируем слои с зависимостями
# Сначала копируем только манифесты, чтобы Poetry мог поставить зависимости и закешировать слой
COPY pyproject.toml poetry.lock* ./

# 6) Не создаём виртуалки внутри контейнера — всё ставим в системный site-packages
RUN poetry config virtualenvs.create false

# Если у тебя зависимости разбиты по группам, можешь оставить только runtime:
# RUN poetry install --no-interaction --no-ansi --only main --no-root
# Или установить всё (по умолчанию main + optional groups, без dev)
RUN poetry install --no-interaction --no-ansi --no-root
RUN pip install --no-cache-dir fastapi uvicorn sqlalchemy asyncpg python-multipart

# 7) Копируем исходники проекта
COPY . .

# 8) Если твой проект — пакет (есть src/ и т.п.), установи и сам проект:
# RUN poetry install --no-interaction --no-ansi

# 9) Команда запуска (поправь под свой модуль)
# Важно: теперь uvicorn есть в PATH, т.к. мы не используем отдельную venv
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

