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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
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

if ! command_exists docker-compose; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    echo "Please install Docker Compose or use Docker Desktop which includes it"
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

docker-compose up --build -d

# Wait for services to be ready
echo -e "${YELLOW}⏳ Waiting for services to start...${NC}"
sleep 10

# Check if services are running
if ! curl -s http://localhost:$WEB_PORT/health >/dev/null 2>&1; then
    echo -e "${YELLOW}⏳ Services still starting up, please wait...${NC}"
    sleep 15
fi

# Print success message
echo ""
echo -e "${GREEN}🎉 UNL Accessibility Remediator is running!${NC}"
echo "=============================================="
echo -e "${BLUE}🌐 Web Interface:${NC} http://localhost:$WEB_PORT"
echo -e "${BLUE}📋 Health Check:${NC} http://localhost:$WEB_PORT/health"
echo ""
echo -e "${YELLOW}📝 How to use:${NC}"
echo "1. Open http://localhost:$WEB_PORT in your browser"
echo "2. Upload a PowerPoint (.pptx) or HTML slide deck"
echo "3. Review the accessibility analysis and recommendations"
echo "4. Download the improved files and reports"
echo ""
echo -e "${YELLOW}⚙️  To stop the services:${NC}"
echo "   docker-compose down"
echo ""
echo -e "${YELLOW}📂 File locations:${NC}"
echo "   • Input files: ./input/"
echo "   • Processed files: ./output/"
echo "   • Reports: ./reports/"
echo ""
echo -e "${BLUE}Press Ctrl+C to view logs, or close this terminal when done${NC}"

# Show logs
docker-compose logs -f