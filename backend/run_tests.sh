#!/bin/bash

# Test runner script for the backend

set -e

echo "🧪 Running Backend Tests..."
echo "=============================="

# Activate virtual environment if it exists
if [ -d "../venv" ]; then
    source ../venv/bin/activate
fi

# Run tests with coverage
echo "Running tests with coverage report..."
python -m pytest tests/ \
    -v \
    --tb=short \
    --cov=app \
    --cov-report=term-missing \
    --cov-report=html

echo ""
echo "✅ Test run complete!"
echo "📊 Coverage report generated in htmlcov/index.html"
