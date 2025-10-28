FROM python:3.11-slim

# 1. Установим poetry
RUN pip install --no-cache-dir poetry==1.8.3

WORKDIR /app

# 2. Скопировать pyproject/lock из корня монорепы
COPY pyproject.toml poetry.lock ./

# 3. Установить зависимости (создаст виртуалку внутри образа)
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

# 4. Скопировать исходники (всю src, чтобы импорты работали)
COPY src ./src

# 5. Команда по умолчанию — uvicorn
CMD ["uvicorn", "src.services.auth.app.main:app", "--host", "0.0.0.0", "--port", "8001"]
