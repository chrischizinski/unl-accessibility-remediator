@echo off
REM UNL Accessibility Tool - Windows Startup
REM Double-click this file to start the tool

echo.
echo ============================================
echo   UNL Accessibility Remediator
echo   University of Nebraska-Lincoln
echo ============================================
echo.

REM Check if Docker is installed
where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Docker is not installed
    echo.
    echo Please install Docker Desktop from:
    echo https://docker.com/products/docker-desktop
    echo.
    echo Press any key to open the download page...
    pause >nul
    start https://docker.com/products/docker-desktop
    exit /b 1
)

REM Check if Docker is running
docker info >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Docker is not running
    echo.
    echo Please start Docker Desktop and try again.
    echo Look for the Docker whale icon in your system tray.
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

echo Checking for available ports...

REM Find available port (simple Windows version)
set PORT=8000
:checkport
netstat -an | find ":%PORT%" >nul
if %errorlevel% equ 0 (
    set /a PORT+=1
    if %PORT% lss 8020 goto checkport
)

if %PORT% geq 8020 (
    echo ERROR: No available ports found in range 8000-8020
    echo Please close other web applications and try again.
    echo.
    pause
    exit /b 1
)

echo Using port: %PORT%
echo.

REM Create dynamic docker-compose file
echo Creating configuration...
(
echo version: '3.8'
echo.
echo services:
echo   accessibility-remediator:
echo     build: ./accessibility_remediator
echo     ports:
echo       - "%PORT%:8000"
echo     volumes:
echo       - ./input:/app/input
echo       - ./output:/app/output
echo       - ./reports:/app/reports
echo     environment:
echo       - OLLAMA_HOST=ollama:11434
echo     depends_on:
echo       - ollama
echo     command: ["python", "web/server.py"]
echo.
echo   ollama:
echo     image: ollama/ollama:latest
echo     ports:
echo       - "11434:11434"
echo     volumes:
echo       - ollama_data:/root/.ollama
echo     environment:
echo       - OLLAMA_MODELS=/root/.ollama/models
echo.
echo volumes:
echo   ollama_data:
) > docker-compose.dynamic.yml

REM Create directories
if not exist "input" mkdir input
if not exist "output" mkdir output
if not exist "reports" mkdir reports

echo Starting services... (this may take a few minutes)
echo.
docker-compose -f docker-compose.dynamic.yml up --build -d

REM Wait for services
echo Waiting for services to start...
timeout /t 15 /nobreak >nul

echo.
echo ============================================
echo   SUCCESS! Tool is running
echo ============================================
echo.
echo Web Interface: http://localhost:%PORT%
echo.
echo Instructions:
echo 1. Open the link above in your web browser
echo 2. Upload a PowerPoint (.pptx) or HTML file
echo 3. Click "Analyze Accessibility"
echo 4. Review the report and download improved files
echo.
echo To stop the tool: Close this window or press Ctrl+C
echo.
echo Press any key to open the web interface...
pause >nul

REM Open web browser
start http://localhost:%PORT%

REM Show logs
echo.
echo Tool is running... Press Ctrl+C to stop
docker-compose -f docker-compose.dynamic.yml logs -f