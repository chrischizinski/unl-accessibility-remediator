#!/bin/bash
# UNL Accessibility Tool - Mac Startup
# Double-click this file to start the tool

# Colors for pretty output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Change to the script's directory
cd "$(dirname "$0")"

echo ""
echo "============================================"
echo "   UNL Accessibility Remediator"
echo "   University of Nebraska-Lincoln"  
echo "============================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}ERROR: Docker is not installed${NC}"
    echo ""
    echo "Please install Docker Desktop from:"
    echo "https://docker.com/products/docker-desktop"
    echo ""
    echo "Press Enter to open download page..."
    read
    open "https://docker.com/products/docker-desktop"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo -e "${RED}ERROR: Docker is not running${NC}"
    echo ""
    echo "Please start Docker Desktop and try again."
    echo "Look for the Docker whale icon in your menu bar."
    echo ""
    echo "Press Enter to exit..."
    read
    exit 1
fi

echo -e "${GREEN}✅ Docker is ready${NC}"

# Find available port
echo "🔍 Finding available port..."
PORT=8000
while [[ $PORT -lt 8020 ]]; do
    if ! nc -z localhost $PORT 2>/dev/null; then
        break
    fi
    ((PORT++))
done

if [[ $PORT -ge 8020 ]]; then
    echo -e "${RED}ERROR: No available ports found in range 8000-8020${NC}"
    echo "Please close other web applications and try again."
    echo ""
    echo "Press Enter to exit..."
    read
    exit 1
fi

echo -e "${GREEN}✅ Using port: $PORT${NC}"
echo ""

# Create dynamic docker-compose file
echo "⚙️  Creating configuration..."
cat > docker-compose.dynamic.yml << EOF
version: '3.8'

services:
  accessibility-remediator:
    build: ./accessibility_remediator
    ports:
      - "$PORT:8000"
    volumes:
      - ./input:/app/input
      - ./output:/app/output
      - ./reports:/app/reports
    environment:
      - OLLAMA_HOST=ollama:11434
    depends_on:
      - ollama
    command: ["python", "web/server.py"]

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    environment:
      - OLLAMA_MODELS=/root/.ollama/models

volumes:
  ollama_data:
EOF

# Create directories
mkdir -p input output reports

echo -e "${YELLOW}🚀 Starting services... (this may take a few minutes)${NC}"
echo ""
docker-compose -f docker-compose.dynamic.yml up --build -d

# Wait for services
echo "⏳ Waiting for services to start..."
sleep 15

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}   SUCCESS! Tool is running${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "${BLUE}🌐 Web Interface:${NC} http://localhost:$PORT"
echo ""
echo -e "${YELLOW}📝 Instructions:${NC}"
echo "1. Open the link above in your web browser"
echo "2. Upload a PowerPoint (.pptx) or HTML file"
echo "3. Click 'Analyze Accessibility'"
echo "4. Review the report and download improved files"
echo ""
echo -e "${YELLOW}⚠️  To stop the tool: Close this window or press Ctrl+C${NC}"
echo ""
echo "Press Enter to open the web interface..."
read

# Open web browser
open "http://localhost:$PORT"

echo ""
echo "Tool is running... Press Ctrl+C to stop"
echo "============================================"

# Show logs
docker-compose -f docker-compose.dynamic.yml logs -f