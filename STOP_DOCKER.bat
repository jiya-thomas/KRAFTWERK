@echo off
echo.
echo  Stopping Docker container...
cd /d "%~dp0"
docker compose down
echo.
echo  Container stopped successfully.
pause
