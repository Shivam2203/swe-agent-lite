#!/bin/bash
set -e

echo "🚀 Starting SWE Agent Lite..."
echo "📚 Environment: ${ENVIRONMENT:-production}"

# Check if API key is set
if [ -z "$GROQ_API_KEY" ]; then
    echo "❌ ERROR: GROQ_API_KEY not set"
    exit 1
fi

# Run the agent with optional arguments
if [ "$1" == "test" ]; then
    echo "🧪 Running tests..."
    python -m pytest tests/ -v
elif [ "$1" == "dev" ]; then
    echo "🔧 Running in development mode..."
    python main.py --verbose
else
    echo "🚀 Running in production mode..."
    python main.py
fi