#!/bin/bash
# Cardiovascular Disease Prediction System - Quick Start Script (Linux/Mac)

echo "========================================="
echo "CardioPredict - Quick Start"
echo "========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

echo "[1/4] Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error installing dependencies"
    exit 1
fi

echo ""
echo "[2/4] Training machine learning model..."
echo "This may take a minute or two..."
python3 train_model.py
if [ $? -ne 0 ]; then
    echo "Error training model"
    exit 1
fi

echo ""
echo "[3/4] Setup complete!"
echo ""
echo "[4/4] Starting Flask server..."
echo ""
echo "========================================="
echo "Server running at: http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo "========================================="
echo ""

python3 app.py
