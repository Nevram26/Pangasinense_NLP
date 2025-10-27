@echo off
REM Quick start script for Pangasinan Translation API (Windows)

echo ========================================================================
echo   Pangasinan Translation API - Quick Start
echo ========================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo Python found
echo.

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Dependencies installed successfully
echo.

REM Check if model exists
if not exist "models\best_model.pt" (
    echo No trained model found. Starting training...
    echo.
    
    python train_model.py --epochs 20 --batch-size 32
    
    if errorlevel 1 (
        echo.
        echo Error: Training failed
        pause
        exit /b 1
    )
    
    echo.
    echo Model trained successfully
) else (
    echo Trained model found
)

echo.
echo ========================================================================
echo   Starting API Server
echo ========================================================================
echo.
echo API will be available at:
echo   - http://localhost:8000
echo   - http://localhost:8000/docs (Interactive documentation)
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the API server
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
