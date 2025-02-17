#!/bin/bash

# Start PostgreSQL database
docker-compose up -d

# Activate virtual environment and run migrations
source .venv/bin/activate
# alembic upgrade head

echo "Starting FastAPI backend..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
FASTAPI_PID=$!

echo "Starting Streamlit frontend..."
streamlit run frontend/app.py

# When Streamlit is stopped, also stop FastAPI
kill $FASTAPI_PID 2>/dev/null || true
