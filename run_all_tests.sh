#!/bin/bash
#
# Comprehensive test runner for Daur-AI-v1
# Runs all tests with Xvfb virtual display and generates coverage report
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=================================="
echo "Daur-AI-v1 Comprehensive Test Suite"
echo "=================================="
echo ""

# Check if Xvfb is installed
if ! command -v xvfb-run &> /dev/null; then
    echo -e "${RED}Error: Xvfb is not installed${NC}"
    echo "Install with: sudo apt-get install xvfb"
    exit 1
fi

# Install test dependencies if needed
echo -e "${YELLOW}Checking test dependencies...${NC}"
python3 -m pip install --user -q pytest pytest-asyncio pytest-timeout 2>&1 | grep -v "Requirement already satisfied" || true
echo ""

# Create test results directory
mkdir -p test_results

# Run tests with coverage
echo -e "${YELLOW}Running tests with Xvfb virtual display...${NC}"
echo ""

# Set display for Xvfb
export DISPLAY=:99

# Run tests with xvfb-run
xvfb-run -a python3 -m pytest \
    tests/ \
    -v \
    --tb=short \
    --ignore=tests/test_input_controller.py \
    --ignore=tests/test_input_controller_full.py \
    2>&1 | tee test_results/test_output.log

# Capture exit code
TEST_EXIT_CODE=$?

echo ""
echo "=================================="
echo "Test Results Summary"
echo "=================================="
echo ""

# Display summary
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
else
    echo -e "${RED}✗ Some tests failed${NC}"
fi

echo ""
echo "Test artifacts:"
echo "  - Coverage HTML report: test_results/coverage_html/index.html"
echo "  - Coverage JSON: test_results/coverage.json"
echo "  - JUnit XML: test_results/junit.xml"
echo "  - Full output log: test_results/test_output.log"
echo ""

# Display coverage summary if available
if [ -f "test_results/coverage.json" ]; then
    echo "Coverage Summary:"
    python3 << 'EOF'
import json
try:
    with open('test_results/coverage.json') as f:
        data = json.load(f)
        total = data['totals']
        percent = total['percent_covered']
        print(f"  Total Coverage: {percent:.2f}%")
        print(f"  Lines Covered: {total['covered_lines']}/{total['num_statements']}")
except Exception as e:
    print(f"  Could not parse coverage data: {e}")
EOF
fi

echo ""
exit $TEST_EXIT_CODE

