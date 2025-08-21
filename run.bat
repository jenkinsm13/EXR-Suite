@echo off
echo Starting EXR Editing Suite...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://python.org
    pause
    exit /b 1
)

REM Check if dependencies are installed
echo Checking dependencies...
python -c "import fastapi, openexr, numpy, pillow, pydantic, webview" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Check if frontend is built
if not exist "frontend\dist\index.html" (
    echo Building frontend...
    cd frontend
    npm install --legacy-peer-deps
    npm run build
    cd ..
    if errorlevel 1 (
        echo Error: Failed to build frontend
        pause
        exit /b 1
    )
)

echo Starting application...
python main.py

pause
