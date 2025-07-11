@echo off
REM UNL Accessibility Remediator - Windows Startup Script
REM This script automatically handles port conflicts on Windows

REM Change to the directory where this script is located
cd /d "%~dp0"

echo 🎯 UNL Accessibility Remediator Setup
echo ===============================================

echo 📋 Checking prerequisites...

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed
    echo Please install Docker Desktop from: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM Check if Docker Compose is available
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is not installed
    echo Please install Docker Desktop which includes Docker Compose
    pause
    exit /b 1
)

echo ✅ Docker and Docker Compose are available

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running
    echo Please start Docker Desktop and try again
    pause
    exit /b 1
)

echo ✅ Docker is running

echo 🔍 Finding available ports...

REM Find available web port (starting from 8001)
set WEB_PORT=8001
:find_web_port
netstat -an | find "LISTENING" | find ":%WEB_PORT%" >nul 2>&1
if %errorlevel% equ 0 (
    set /a WEB_PORT+=1
    if %WEB_PORT% gtr 8020 (
        echo ❌ Could not find available web port in range 8001-8020
        pause
        exit /b 1
    )
    goto find_web_port
)

REM Find available Ollama port (starting from 11434)
set OLLAMA_PORT=11434
:find_ollama_port
netstat -an | find "LISTENING" | find ":%OLLAMA_PORT%" >nul 2>&1
if %errorlevel% equ 0 (
    set /a OLLAMA_PORT+=1
    if %OLLAMA_PORT% gtr 11454 (
        echo ❌ Could not find available Ollama port in range 11434-11454
        pause
        exit /b 1
    )
    goto find_ollama_port
)

echo ✅ Using ports: Web=%WEB_PORT%, Ollama=%OLLAMA_PORT%

echo ⚙️ Configuring services...

REM Create .env file with discovered ports
echo WEB_PORT=%WEB_PORT%> .env
echo OLLAMA_PORT=%OLLAMA_PORT%>> .env

REM Create directories
if not exist "input" mkdir input
if not exist "output" mkdir output
if not exist "reports" mkdir reports

echo ✅ Configuration complete

echo 🚀 Starting services...
echo This may take a few minutes on first run (downloading images)

docker-compose up --build -d
if %errorlevel% neq 0 (
    echo ❌ ERROR: Failed to start the services.
    echo Please review the error messages above.
    echo You can get more details by running: docker-compose logs
    pause
    exit /b 1
)

echo ⏳ Waiting for services to start...
timeout /t 10 /nobreak >nul

REM Wait for health check to pass
echo ⏳ Checking if services are ready...
:check_health
curl -s http://localhost:%WEB_PORT%/health >nul 2>&1
if %errorlevel% neq 0 (
    echo ⏳ Services still starting up, please wait...
    timeout /t 5 /nobreak >nul
    goto check_health
)

echo ✅ Services are ready!
echo 🌐 Opening web interface in your default browser...

echo.
echo 🎉 UNL Accessibility Remediator is running!
echo ==============================================
echo 🌐 Web Interface: http://localhost:%WEB_PORT%
echo 📋 Health Check: http://localhost:%WEB_PORT%/health
echo.
echo 📝 How to use:
echo 1. Your browser should now be open to the tool interface
echo 2. Upload a PowerPoint (.pptx), PDF (.pdf), Word (.docx), or HTML file
echo 3. Review the accessibility analysis and recommendations
echo 4. Download the improved files and reports
echo.
echo ⚙️ To stop the services:
echo    🖱️ Easy way: Double-click 'stop-accessibility-tool.bat'
echo    💻 Command line: docker-compose down
echo.
echo 📂 File locations:
echo    • Input files: .\input\
echo    • Processed files: .\output\
echo    • Reports: .\reports\
echo.
echo Opening web interface...
start http://localhost:%WEB_PORT%

pause