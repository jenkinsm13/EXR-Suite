#!/bin/bash

echo "Starting EXR Editing Suite..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

# Check if dependencies are installed
echo "Checking dependencies..."
python3 -c "import fastapi, openexr, numpy, pillow, pydantic, webview" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing dependencies..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install dependencies"
        exit 1
    fi
fi

# Check if frontend is built
if [ ! -f "frontend/dist/index.html" ]; then
    echo "Building frontend..."
    cd frontend
    npm install --legacy-peer-deps
    npm run build
    cd ..
    if [ $? -ne 0 ]; then
        echo "Error: Failed to build frontend"
        exit 1
    fi
fi

echo "Starting application..."
python3 main.py
