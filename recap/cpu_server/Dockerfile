FROM python:3.11-slim

WORKDIR /app

RUN pip install --upgrade pip && \
    pip install poetry

COPY pyproject.toml poetry.lock* /app/

RUN poetry install --no-root 

COPY . /app

ENV WORKERS=8
ENV PORT=8000
ENV DEBUG=False
ENV APP_MODE=web

COPY /app/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]
