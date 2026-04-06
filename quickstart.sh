#!/bin/bash

# Agricultural Statistics Dashboard - Quick Start Guide

echo "========================================"
echo "🌾 Agricultural Statistics Dashboard"
echo "========================================"
echo ""
echo "This script will help you get started with the application."
echo ""

# Check prerequisites
echo "✓ Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "✗ Python 3 not found"
    echo "  Install Python 3: https://www.python.org/downloads/"
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "✗ Node.js not found"
    echo "  Install Node.js: https://nodejs.org/"
    exit 1
fi

# Check PostgreSQL
if ! command -v psql &> /dev/null; then
    echo "⚠ PostgreSQL not found (required for backend)"
    echo "  Install PostgreSQL: https://www.postgresql.org/download/"
    echo "  Skip this if you already have a PostgreSQL instance running"
fi

echo "✓ All prerequisites found!"
echo ""

# Activate virtual environment
echo "📦 Activating Python virtual environment..."
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✓ Virtual environment activated"
else
    echo "✗ Virtual environment not found"
    echo "  Creating one now..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    echo "✓ Virtual environment created and dependencies installed"
fi

echo ""
echo "========================================"
echo "🚀 Starting Services"
echo "========================================"
echo ""
echo "Choose an option:"
echo "1) Start Backend (FastAPI on port 8000)"
echo "2) Start Frontend (React on port 5173)"
echo "3) Start Both (in new terminal windows)"
echo "4) Exit"
echo ""

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo "Starting Backend..."
        echo "Backend will be available at: http://localhost:8000"
        echo "API Docs at: http://localhost:8000/docs"
        cd backend
        uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
        ;;
    2)
        echo "Starting Frontend..."
        echo "Frontend will be available at: http://localhost:5173"
        cd web
        if [ ! -d "node_modules" ]; then
            npm install
        fi
        npm run dev
        ;;
    3)
        echo "Starting both services..."
        echo ""
        echo "Backend: http://localhost:8000"
        echo "Frontend: http://localhost:5173"
        echo "API Docs: http://localhost:8000/docs"
        echo ""
        
        # Start backend in background
        cd backend
        uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
        BACKEND_PID=$!
        echo "✓ Backend started (PID: $BACKEND_PID)"
        
        # Start frontend
        cd ../web
        if [ ! -d "node_modules" ]; then
            npm install
        fi
        npm run dev
        ;;
    4)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid choice!"
        exit 1
        ;;
esac
