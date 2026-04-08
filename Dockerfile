FROM python:3.11-slim

WORKDIR /app

# Install build dependencies and application
RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock* ./
RUN pip install --no-cache-dir poetry &&     poetry config virtualenvs.create false &&     poetry install --no-interaction --no-ansi --no-root || true

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "rmer_ai_coffee.connectivity.rest_api:app", "--host", "0.0.0.0", "--port", "8000"]