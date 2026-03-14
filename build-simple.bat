@echo off
echo ========================================
echo Building Best-Option Electron App
echo ========================================
echo.

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    pause
    exit /b 1
)

echo Step 1: Installing Frontend Dependencies...
cd frontend
call npm install

if errorlevel 1 (
    echo ERROR: npm install failed
    cd ..
    pause
    exit /b 1
)

echo.
echo Step 2: Building Frontend...
call npm run build

if errorlevel 1 (
    echo ERROR: Frontend build failed
    cd ..
    pause
    exit /b 1
)

echo.
echo Step 3: Building Electron App...
call npm run electron:build

if errorlevel 1 (
    echo ERROR: Electron build failed
    cd ..
    pause
    exit /b 1
)

cd ..

echo.
echo ========================================
echo Build Complete!
echo ========================================
echo.
echo Installer location: frontend\dist-electron\
echo.
echo NOTE: You need to run the Python backend separately:
echo   python app.py
echo.
pause
