@echo off
title KRAFTWERK - Swiss Project Manager
color 0F

echo.
echo  =====================================================
echo   KRAFTWERK // SWISS PROJECT MANAGEMENT SYSTEM
echo  =====================================================
echo.
echo  [1/3] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo  ERROR: Python not found! Please install Python first.
    pause
    exit /b 1
)
echo       Python found. OK
echo.

echo  [2/3] Starting the web server...
echo.
echo  *** DO NOT CLOSE THIS WINDOW ***
echo  *** The app stops if you close it ***
echo.
echo  Your app will open at: http://localhost:8000
echo  =====================================================
echo.

cd /d "C:\Users\jiya Thomas\Desktop\AJCE Project\project_management_system"

:: Open browser after 3 second delay
start "" cmd /c "timeout /nobreak /t 3 >nul && start http://localhost:8000"

echo  [3/3] Server is starting... browser will open in 3 seconds.
echo.

python run.py

echo.
echo  Server has stopped.
pause
