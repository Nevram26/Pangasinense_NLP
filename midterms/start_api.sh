#!/bin/bash
# Quick start script for Pangasinan Translation API

echo "========================================================================"
echo "  Pangasinan Translation API - Quick Start"
echo "========================================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Error: Failed to install dependencies"
    exit 1
fi

echo ""
echo "✓ Dependencies installed successfully"
echo ""

# Check if model exists
if [ ! -f "models/best_model.pt" ]; then
    echo "🧠 No trained model found. Starting training..."
    echo ""
    
    python3 train_model.py --epochs 20 --batch-size 32
    
    if [ $? -ne 0 ]; then
        echo ""
        echo "❌ Error: Training failed"
        exit 1
    fi
    
    echo ""
    echo "✓ Model trained successfully"
else
    echo "✓ Trained model found"
fi

echo ""
echo "========================================================================"
echo "  Starting API Server"
echo "========================================================================"
echo ""
echo "API will be available at:"
echo "  • http://localhost:8000"
echo "  • http://localhost:8000/docs (Interactive documentation)"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the API server
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
