# Используем Python 3.11
FROM python:3.11-slim

# Рабочая директория внутри контейнера
WORKDIR /app

# Скопировать файлы зависимостей (poetry/requirements)
COPY pyproject.toml poetry.lock* requirements.txt* /app/

# Установить зависимости
RUN pip install poetry && poetry config virtualenvs.create false && poetry install --no-root

# Скопировать исходники проекта
COPY src /app/src

# Чтобы Python видел модуль src
ENV PYTHONPATH=/app

# Запуск бота
CMD ["python", "-m", "src.services.bot.app.main"]
