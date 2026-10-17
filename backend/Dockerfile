FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY alembic.ini ./alembic.ini
COPY alembic ./alembic

RUN mkdir -p /app/uploads /app/vector_data /app/model_cache \
    && chown -R nobody:nogroup /app

EXPOSE 8001

USER nobody

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
