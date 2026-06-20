# Single image used by BOTH the `api` and `worker` services.
# Only the start command differs (set in docker-compose.yml).
FROM python:3.12-slim

# Keep Python lean and predictable inside containers.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first so Docker can cache this layer when only code changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code.
COPY . .

# Folder where tasks write outputs (thumbnails, reports). Mounted as a volume in compose.
RUN mkdir -p /app/storage

EXPOSE 8000

# Default command; docker-compose overrides this per-service.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
