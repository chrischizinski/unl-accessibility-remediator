#!/bin/bash
# UNL Accessibility Remediator - Colleague-Friendly Startup Script
#
# This script automatically handles port conflicts and provides clear instructions
# for colleagues who want to use the tool.

set -e  # Exit on any error

# Change to the directory where this script is located
cd "$(dirname "$0")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🎯 UNL Accessibility Remediator Setup${NC}"
echo "==============================================="

# Function to check if command exists, checking common locations
command_exists() {
    # First try the standard command lookup
    if command -v "$1" >/dev/null 2>&1; then
        return 0
    fi
    
    # For Docker/docker-compose, check common installation paths
    if [ "$1" = "docker" ] || [ "$1" = "docker-compose" ]; then
        for path in /usr/local/bin/$1 /opt/homebrew/bin/$1 /usr/bin/$1; do
            if [ -x "$path" ]; then
                # Add the directory to PATH if not already there
                dir=$(dirname "$path")
                if [[ ":$PATH:" != *":$dir:"* ]]; then
                    export PATH="$dir:$PATH"
                fi
                return 0
            fi
        done
    fi
    
    return 1
}

# Function to find available port with systematic checking
find_available_port() {
    local start_port=$1
    local max_attempts=${2:-20}
    
    # Check if lsof is available
    if ! command_exists lsof; then
        echo -e "${RED}❌ 'lsof' command not found. Please install it to check for available ports.${NC}"
        exit 1
    fi
    
    for ((port=start_port; port<start_port+max_attempts; port++)); do
        # Use lsof for more reliable port checking
        if ! lsof -i :$port >/dev/null 2>&1; then
            echo $port
            return 0
        fi
    done
    return 1
}


# Check prerequisites
echo -e "${YELLOW}📋 Checking prerequisites...${NC}"

if ! command_exists docker; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo "Please install Docker Desktop or OrbStack from:"
    echo "  - Docker Desktop: https://www.docker.com/products/docker-desktop"
    echo "  - OrbStack: https://orbstack.dev"
    exit 1
fi

if ! command_exists docker-compose && ! docker compose version >/dev/null 2>&1; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    echo "Please install Docker Compose or use Docker Desktop/OrbStack which includes it"
    exit 1
fi

echo -e "${GREEN}✅ Docker and Docker Compose are available${NC}"

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running${NC}"
    echo "Please start your Docker service:"
    echo "  - Docker Desktop: Start Docker Desktop application"
    echo "  - OrbStack: Start OrbStack application"
    exit 1
fi

echo -e "${GREEN}✅ Docker is running${NC}"

# Find available ports
echo -e "${YELLOW}🔍 Finding available ports...${NC}"

WEB_PORT=$(find_available_port 8001)
OLLAMA_PORT=$(find_available_port 11434)

if [ -z "$WEB_PORT" ]; then
    echo -e "${RED}❌ Could not find available web port in range 8001-8020${NC}"
    echo "Please stop other web services and try again"
    exit 1
fi

if [ -z "$OLLAMA_PORT" ]; then
    echo -e "${RED}❌ Could not find available port for Ollama in range 11434-11453${NC}"
    echo "Please stop other services using ports in this range"
    exit 1
fi

echo -e "${GREEN}✅ Using ports: Web=$WEB_PORT, Ollama=$OLLAMA_PORT${NC}"

# Create .env file for docker-compose
echo -e "${YELLOW}⚙️  Configuring services...${NC}"
echo "WEB_PORT=${WEB_PORT}" > .env
echo "OLLAMA_PORT=${OLLAMA_PORT}" >> .env

# Create input/output directories
mkdir -p input output reports

echo -e "${GREEN}✅ Configuration complete${NC}"

# Start the services
echo -e "${YELLOW}🚀 Starting services...${NC}"
echo "This may take a few minutes on first run (downloading images)"

# Use modern docker compose command if available, fallback to docker-compose
if docker compose version >/dev/null 2>&1; then
    docker compose up --build -d
else
    docker-compose up --build -d
fi

# Wait for services to be ready
echo -e "${YELLOW}⏳ Waiting for services to start...${NC}"
sleep 10

# Check if services are running
if ! curl -s http://localhost:$WEB_PORT/health >/dev/null 2>&1; then
    echo -e "${YELLOW}⏳ Services still starting up, please wait...${NC}"
    sleep 15
fi

# Wait a bit more and check again
max_attempts=12
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:$WEB_PORT/health >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Services are ready!${NC}"
        break
    fi
    echo -e "${YELLOW}⏳ Still waiting... (attempt $((attempt + 1))/$max_attempts)${NC}"
    sleep 5
    attempt=$((attempt + 1))
done

# Launch browser automatically
echo -e "${BLUE}🌐 Opening web interface in your default browser...${NC}"
if command -v open >/dev/null 2>&1; then
    # macOS
    open "http://localhost:$WEB_PORT"
elif command -v xdg-open >/dev/null 2>&1; then
    # Linux
    xdg-open "http://localhost:$WEB_PORT"
elif command -v start >/dev/null 2>&1; then
    # Windows (if running under WSL or similar)
    start "http://localhost:$WEB_PORT"
else
    echo -e "${YELLOW}⚠️  Could not auto-open browser. Please manually open: http://localhost:$WEB_PORT${NC}"
fi

# Print success message
echo ""
echo -e "${GREEN}🎉 UNL Accessibility Remediator is running!${NC}"
echo "=============================================="
echo -e "${BLUE}🌐 Web Interface:${NC} http://localhost:$WEB_PORT (opened in browser)"
echo -e "${BLUE}📋 Health Check:${NC} http://localhost:$WEB_PORT/health"
echo ""
echo -e "${YELLOW}📝 How to use:${NC}"
echo "1. Your browser should now be open to the tool interface"
echo "2. Upload a PowerPoint (.pptx), PDF (.pdf), Word (.docx), or HTML file"
echo "3. Review the accessibility analysis and recommendations"
echo "4. Download the improved files and reports"
echo ""
echo -e "${YELLOW}⚙️  To stop the services:${NC}"
if docker compose version >/dev/null 2>&1; then
    echo "   docker compose down"
else
    echo "   docker-compose down"
fi
echo ""
echo -e "${YELLOW}📂 File locations:${NC}"
echo "   • Input files: ./input/"
echo "   • Processed files: ./output/"
echo "   • Reports: ./reports/"
echo ""
echo -e "${BLUE}Press Ctrl+C to view logs, or close this terminal when done${NC}"

# Show logs
if docker compose version >/dev/null 2>&1; then
    docker compose logs -f
else
    docker-compose logs -f
fi