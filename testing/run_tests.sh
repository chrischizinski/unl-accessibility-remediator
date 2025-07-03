#!/bin/bash
"""
Simple Test Runner for UNL Accessibility Remediator

This script provides an easy way to run tests for the accessibility tool
for both technical and non-technical users.
"""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "=============================================="
echo "   UNL Accessibility Tool - Test Suite"
echo "   University of Nebraska-Lincoln"
echo "=============================================="
echo ""

# Change to project root
cd "$(dirname "$0")/.."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is required but not found${NC}"
    echo "Please install Python 3 and try again"
    exit 1
fi

echo -e "${YELLOW}🧪 Starting comprehensive test suite...${NC}"
echo ""

# Install required Python packages if needed
echo -e "${BLUE}📦 Checking Python dependencies...${NC}"
python3 -c "import requests" 2>/dev/null || {
    echo -e "${YELLOW}Installing required packages...${NC}"
    python3 -m pip install requests --user
}

# Run the comprehensive test suite
echo -e "${BLUE}🚀 Running tests...${NC}"
echo ""

python3 testing/scripts/comprehensive_test.py

TEST_EXIT_CODE=$?

echo ""
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ All tests completed successfully!${NC}"
    echo ""
    echo -e "${BLUE}📄 Test reports available in:${NC}"
    echo "  - testing/reports/test_report.md"
    echo "  - testing/reports/test_report.json"
    echo "  - testing/reports/test_results.log"
else
    echo -e "${RED}❌ Some tests failed${NC}"
    echo ""
    echo -e "${YELLOW}📄 Check test reports for details:${NC}"
    echo "  - testing/reports/test_report.md"
    echo "  - testing/reports/test_results.log"
fi

echo ""
echo -e "${BLUE}🔍 Quick test summary:${NC}"
if [ -f "testing/reports/test_report.md" ]; then
    # Show summary from report
    grep -A 10 "## 📊 Summary" testing/reports/test_report.md | tail -n +2 | head -n 5
fi

echo ""
echo "=============================================="
exit $TEST_EXIT_CODE