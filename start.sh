#!/bin/bash
# Run migrations before starting the app
alembic upgrade head

# Start the app
uvicorn main:app --host 0.0.0.0 --port 8000
