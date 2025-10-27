#!/bin/bash
# Quick start script to launch both API and translator

echo "========================================================================"
echo "  Pangasinan ML Translator - Complete System Startup"
echo "========================================================================"
echo ""

cd midterms

# Check if model exists
if [ ! -f "models/best_model.pt" ]; then
    echo "⚠️  No trained model found!"
    echo ""
    echo "Please train the model first:"
    echo "  cd midterms"
    echo "  python train_model.py --epochs 20"
    echo ""
    exit 1
fi

echo "✓ Model found"
echo ""

# Start API in background
echo "🚀 Starting ML API server..."
echo ""

# Kill any existing process on port 8000
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Start API
uvicorn api:app --host 0.0.0.0 --port 8000 &
API_PID=$!

# Wait for API to start
echo "Waiting for API to start..."
sleep 3

# Check if API is running
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✓ API running at http://localhost:8000"
else
    echo "✗ Failed to start API"
    kill $API_PID 2>/dev/null
    exit 1
fi

echo ""
echo "========================================================================"
echo "  System Ready!"
echo "========================================================================"
echo ""
echo "  📡 ML API:          http://localhost:8000"
echo "  📚 API Docs:        http://localhost:8000/docs"
echo "  🌐 Translator:      Open ../translator.html in browser"
echo ""
echo "  Press Ctrl+C to stop the server"
echo ""
echo "========================================================================"
echo ""

# Open translator in default browser
cd ..
if command -v open &> /dev/null; then
    # macOS
    open translator.html
elif command -v xdg-open &> /dev/null; then
    # Linux
    xdg-open translator.html
else
    echo "💡 Manually open: translator.html in your browser"
fi

cd midterms

# Keep API running
wait $API_PID
