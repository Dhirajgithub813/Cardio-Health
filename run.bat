@echo off
REM Cardiovascular Disease Prediction System - Quick Start Script

echo =========================================
echo CardioPredict - Quick Start
echo =========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo [1/4] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Error installing dependencies
    pause
    exit /b 1
)

echo.
echo [2/4] Training machine learning model...
echo This may take a minute or two...
python train_model.py
if errorlevel 1 (
    echo Error training model
    pause
    exit /b 1
)

echo.
echo [3/4] Setup complete!
echo.
echo [4/4] Starting Flask server...
echo.
echo =========================================
echo Server running at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo =========================================
echo.

python app.py

pause
