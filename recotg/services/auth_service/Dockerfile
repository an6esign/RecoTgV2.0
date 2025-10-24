FROM python:3.11-slim
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 1) Ставим зависимости из корня репо
COPY pyproject.toml poetry.lock* ./
RUN pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-root --only main


ENV PYTHONPATH=/app

CMD ["uvicorn","recotg.services.auth_service.main:app","--host","0.0.0.0","--port","8001"]