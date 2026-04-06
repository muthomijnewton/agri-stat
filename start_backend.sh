#!/bin/bash

# Start the FastAPI backend server
cd /home/phil/projects/agric-stat-dash/backend
export PYTHONPATH=/home/phil/projects/agric-stat-dash/backend:$PYTHONPATH
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
