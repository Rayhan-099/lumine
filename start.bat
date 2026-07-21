@echo off
REM Lumine AI Startup Script (Windows)

echo Starting Lumine AI Backend...

REM Run database migrations
alembic upgrade head

REM Start Uvicorn directly (Gunicorn is Unix-only)
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
