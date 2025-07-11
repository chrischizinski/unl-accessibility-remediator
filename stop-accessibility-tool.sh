#!/bin/bash
# UNL Accessibility Remediator - Stop Script
#
# Simple script to stop the accessibility tool services

# Change to the directory where this script is located
cd "$(dirname "$0")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🛑 UNL Accessibility Remediator - Stop Services${NC}"
echo "=================================================="

# Check if services are running
if ! docker ps --format "table {{.Names}}" | grep -q "accessibility-remediator"; then
    echo -e "${YELLOW}⚠️  No accessibility tool services are currently running${NC}"
    echo "Nothing to stop!"
    exit 0
fi

echo -e "${YELLOW}🔍 Found running services, stopping them...${NC}"

# Stop services
if docker compose version >/dev/null 2>&1; then
    docker compose down
else
    docker-compose down
fi

echo -e "${GREEN}✅ Accessibility tool services have been stopped${NC}"
echo ""
echo -e "${BLUE}📝 To start again:${NC}"
echo "   Double-click: start-accessibility-tool.sh"
echo ""
echo -e "${YELLOW}💡 Tip:${NC} You can also restart by running the start script again"