FROM python:3.11-slim

WORKDIR /app

RUN pip install --upgrade pip && \
    pip install poetry

COPY pyproject.toml poetry.lock* /app/

RUN poetry install --no-root 

COPY . /app

# Указываем переменные окружения
ENV WORKERS=4

# Команды для запуска сервиса
CMD ["sh", "-c", "poetry run gunicorn -w $WORKERS -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:80"]
