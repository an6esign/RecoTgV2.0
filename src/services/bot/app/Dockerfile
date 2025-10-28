FROM python:3.11-slim

WORKDIR /app

# Устанавливаем poetry
ENV POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1
RUN pip install --no-cache-dir poetry==1.8.3

# Копируем только манифесты зависимостей для кеширования слоёв
COPY services/bot/pyproject.toml /app/services/bot/pyproject.toml
COPY services/bot/poetry.lock /app/services/bot/poetry.lock

# Кладём shared и сам бот-код
COPY shared /app/shared
COPY services/bot/app /app/services/bot/app

WORKDIR /app/services/bot
RUN poetry install --only main --no-root

WORKDIR /app/services/bot

ENV PYTHONUNBUFFERED=1

# Запуск aiogram-бота
CMD ["poetry", "run", "bot-run"]
