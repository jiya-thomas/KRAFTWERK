@echo off
echo.
echo  =================================================
echo   KRAFTWERK - Swiss Project Management System
echo   DOCKER LAUNCHER
echo  =================================================
echo.

cd /d "%~dp0"

echo  [STEP 1] Checking if Docker Desktop is running...
docker info >nul 2>&1
if errorlevel 1 (
    echo.
    echo  ERROR: Docker Desktop is NOT running!
    echo.
    echo  Please do this:
    echo  1. Look at your Windows taskbar (bottom right corner)
    echo  2. Find the Docker whale icon and double-click it
    echo  3. Wait until Docker says "Docker Desktop is running"
    echo  4. Run this file again
    echo.
    pause
    exit /b 1
)

echo  Docker is running! Good.
echo.
echo  [STEP 2] Building and starting the container...
echo  (This may take 2-3 minutes the first time)
echo.

docker compose up --build -d

if errorlevel 1 (
    echo.
    echo  ERROR: Docker build failed. See error above.
    pause
    exit /b 1
)

echo.
echo  [STEP 3] Opening the app in your browser...
echo.
echo  The app is running at: http://localhost:8000
echo.
timeout /nobreak /t 2 >nul
start "" "http://localhost:8000"

echo  To STOP the app later, run STOP_DOCKER.bat
echo.
pause
