#!/bin/bash

echo "🚀 Starting Pangasinan Rule-Based Translation API"
echo "================================================="
echo ""

# Check if we're in the right directory
if [ ! -f "rule_based_api.py" ]; then
    echo "❌ Error: rule_based_api.py not found!"
    echo "   Please run this script from the midterms directory"
    exit 1
fi

# Check if dictionary exists
if [ ! -f "midterm_dictionary.json" ]; then
    echo "❌ Error: midterm_dictionary.json not found!"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    exit 1
fi

# Check if FastAPI is installed
echo "📦 Checking dependencies..."
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "⚠️  FastAPI not found. Installing dependencies..."
    pip install fastapi uvicorn pydantic
fi

echo ""
echo "✓ All checks passed!"
echo ""
echo "🔧 Starting Rule-Based Translation API..."
echo "   URL: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo "   Health Check: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the API
python3 rule_based_api.py
