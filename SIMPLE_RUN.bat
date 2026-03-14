@echo off
title Best-Option Launcher
color 0A

echo.
echo ========================================
echo   Best-Option Application Launcher
echo ========================================
echo.

REM Check if backend is running
echo Checking backend...
curl -s http://127.0.0.1:8000 >nul 2>&1
if errorlevel 1 (
    echo Backend not running. Starting backend...
    start "Best-Option Backend" cmd /k "python app.py"
    echo Waiting for backend to start...
    timeout /t 5 /nobreak > nul
) else (
    echo Backend is already running!
)

echo.
echo Starting frontend...
cd frontend
start "Best-Option Frontend" cmd /k "npm run dev"

echo.
echo Waiting for frontend to start...
timeout /t 5 /nobreak > nul

echo.
echo Opening application in browser...
start http://localhost:5173

echo.
echo ========================================
echo Application Started Successfully!
echo ========================================
echo.
echo Backend: http://127.0.0.1:8000
echo Frontend: http://localhost:5173
echo.
echo Keep both command windows open.
echo Close them to stop the application.
echo.
pause
