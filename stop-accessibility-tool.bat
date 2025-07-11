@echo off
REM UNL Accessibility Remediator - Windows Stop Script
REM Simple script to stop the accessibility tool services

REM Change to the directory where this script is located
cd /d "%~dp0"

echo 🛑 UNL Accessibility Remediator - Stop Services
echo ==================================================

REM Check if services are running
docker ps --format "table {{.Names}}" | findstr "accessibility-remediator" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ No accessibility tool services are currently running
    echo Nothing to stop!
    pause
    exit /b 0
)

echo 🔍 Found running services, stopping them...

REM Stop services
docker-compose down

echo ✅ Accessibility tool services have been stopped
echo.
echo 📝 To start again:
echo    Double-click: start-accessibility-tool.bat
echo.
echo 💡 Tip: You can also restart by running the start script again

pause