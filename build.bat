@echo off
echo ============================================================
echo Best-Option Desktop Application - Build Script
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    pause
    exit /b 1
)

echo Step 1: Installing PyInstaller...
pip install pyinstaller
if errorlevel 1 (
    echo ERROR: Failed to install PyInstaller
    pause
    exit /b 1
)

echo.
echo Step 2: Building Backend Executable...
pyinstaller build_backend.spec --clean
if errorlevel 1 (
    echo ERROR: Backend build failed
    pause
    exit /b 1
)

echo.
echo Step 3: Installing Frontend Dependencies...
cd frontend
call npm install
if errorlevel 1 (
    echo ERROR: Failed to install frontend dependencies
    cd ..
    pause
    exit /b 1
)

echo.
echo Step 4: Building Frontend...
call npm run build
if errorlevel 1 (
    echo ERROR: Frontend build failed
    cd ..
    pause
    exit /b 1
)

echo.
echo Step 5: Building Electron App...
call npm run electron:build
if errorlevel 1 (
    echo ERROR: Electron build failed
    cd ..
    pause
    exit /b 1
)

cd ..

echo.
echo ============================================================
echo BUILD COMPLETE!
echo ============================================================
echo.
echo Build artifacts:
echo   - Backend: dist\best-option-backend\
echo   - Frontend: frontend\dist\
echo   - Electron App: frontend\dist-electron\
echo.
echo To run the backend:
echo   cd dist\best-option-backend
echo   best-option-backend.exe
echo.
pause
