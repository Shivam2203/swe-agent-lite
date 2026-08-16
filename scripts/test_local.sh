#!/bin/bash
set -e

echo "🧪 Running local tests..."

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/ -v --cov=src --cov-report=html

echo "✅ Tests complete! Coverage report in htmlcov/index.html"