#!/bin/bash
"""
Port Conflict Resolver for UNL Accessibility Remediator

This script helps resolve Docker port conflicts by cleaning up old containers
and finding available ports.
"""

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔧 Fixing Port Conflicts${NC}"
echo "==============================="

# Function to check if port is in use
port_in_use() {
    local port=$1
    if command -v lsof >/dev/null 2>&1; then
        lsof -i :$port >/dev/null 2>&1
    elif command -v nc >/dev/null 2>&1; then
        nc -z localhost $port 2>/dev/null
    else
        # Fallback: try to bind to port
        python3 -c "import socket; s=socket.socket(); s.bind(('', $port)); s.close()" 2>/dev/null
        return $?
    fi
}

# Function to stop related containers
cleanup_containers() {
    echo -e "${YELLOW}🧹 Cleaning up existing containers...${NC}"
    
    # Stop any running containers with ollama or accessibility in the name
    docker ps -q --filter "name=ollama" | xargs -r docker stop 2>/dev/null || true
    docker ps -q --filter "name=accessibility" | xargs -r docker stop 2>/dev/null || true
    docker ps -q --filter "name=title_ii_compliance" | xargs -r docker stop 2>/dev/null || true
    
    # Remove stopped containers
    docker ps -aq --filter "name=ollama" | xargs -r docker rm 2>/dev/null || true
    docker ps -aq --filter "name=accessibility" | xargs -r docker rm 2>/dev/null || true
    docker ps -aq --filter "name=title_ii_compliance" | xargs -r docker rm 2>/dev/null || true
    
    echo -e "${GREEN}✅ Container cleanup complete${NC}"
}

# Function to find available ports
find_available_ports() {
    local web_port=8001
    local ollama_port=11434
    
    echo -e "${YELLOW}🔍 Finding available ports...${NC}"
    
    # Find available web port
    while port_in_use $web_port; do
        ((web_port++))
        if [ $web_port -gt 8020 ]; then
            echo -e "${RED}❌ No available ports found in range 8001-8020${NC}"
            exit 1
        fi
    done
    
    # Find available Ollama port  
    while port_in_use $ollama_port; do
        ((ollama_port++))
        if [ $ollama_port -gt 11450 ]; then
            echo -e "${RED}❌ No available ports found in range 11434-11450${NC}"
            exit 1
        fi
    done
    
    echo -e "${GREEN}✅ Available ports found: Web=$web_port, Ollama=$ollama_port${NC}"
    echo "$web_port,$ollama_port"
}

# Main execution
echo -e "${YELLOW}Step 1: Stopping existing containers...${NC}"
cleanup_containers

echo -e "${YELLOW}Step 2: Finding available ports...${NC}"
ports=$(find_available_ports)
web_port=$(echo $ports | cut -d',' -f1)
ollama_port=$(echo $ports | cut -d',' -f2)

echo -e "${YELLOW}Step 3: Creating new configuration...${NC}"

# Create dynamic docker-compose file
cat > docker-compose.dynamic.yml << EOF
services:
  ollama:
    image: ollama/ollama:latest
    container_name: unl-accessibility-remediator-$(date +%s)-ollama-1
    ports:
      - "${ollama_port}:11434"
    volumes:
      - ollama_data:/root/.ollama
    environment:
      - OLLAMA_HOST=http://0.0.0.0:11434
      - OLLAMA_ORIGINS=*
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - default

  accessibility-remediator:
    build: ./accessibility_remediator
    container_name: unl-accessibility-remediator-$(date +%s)-app-1
    ports:
      - "${web_port}:8000"
    volumes:
      - ./input:/app/input
      - ./output:/app/output
      - ./reports:/app/reports
    environment:
      - OLLAMA_HOST=http://ollama:11434
      - OLLAMA_MODEL=llama3.1:8b
    depends_on:
      ollama:
        condition: service_healthy
    command: ["python", "web/server.py"]
    networks:
      - default

volumes:
  ollama_data:

networks:
  default:
    driver: bridge
EOF

echo -e "${GREEN}✅ Configuration created successfully${NC}"
echo ""
echo -e "${BLUE}🚀 Ready to start!${NC}"
echo "================================="
echo -e "Web Interface will be: ${GREEN}http://localhost:$web_port${NC}"
echo -e "Ollama API will be: ${GREEN}http://localhost:$ollama_port${NC}"
echo ""
echo "Run this command to start:"
echo -e "${YELLOW}docker-compose -f docker-compose.dynamic.yml up${NC}"