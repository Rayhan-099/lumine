#!/bin/bash
# Lumine AI Production Startup Script (Linux/Mac)
# Uses Gunicorn with Uvicorn workers for production concurrency

echo "Starting Lumine AI Backend..."

# Run database migrations
alembic upgrade head

# Start Gunicorn server (4 workers)
# Note: On Windows, use uvicorn directly or run start.bat
exec gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
