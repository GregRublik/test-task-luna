#!/bin/sh
set -e

echo "Running migrations..."
alembic upgrade head

echo "Seeding database..."
python src/db/seed.py

echo "Starting FastAPI..."
uvicorn src.main:app --host 0.0.0.0 --port ${APP_PORT}
