FROM python:3.11-slim

WORKDIR /app

# System deps (psycopg)
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock* /app/
RUN pip install --no-cache-dir poetry && poetry config virtualenvs.create false     && poetry install --no-interaction --no-ansi --no-root

COPY . /app

# Pre-create tables at build/run time is not ideal; we'll do it at startup
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
