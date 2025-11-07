#!/bin/bash

# Integration Tests Runner Script
# Runs comprehensive integration tests for IACT DORA metrics system

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}IACT Integration Tests Suite${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Navigate to project directory
cd "$(dirname "$0")/../api/callcentersite" || exit 1

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}Warning: No virtual environment detected${NC}"
    echo -e "${YELLOW}Consider activating venv: source venv/bin/activate${NC}"
    echo ""
fi

# Check dependencies
echo -e "${GREEN}[1/5] Checking dependencies...${NC}"
python -c "import pytest" 2>/dev/null || {
    echo -e "${RED}Error: pytest not installed${NC}"
    echo "Install with: pip install pytest pytest-django pytest-cov"
    exit 1
}

python -c "import django" 2>/dev/null || {
    echo -e "${RED}Error: Django not installed${NC}"
    exit 1
}

echo -e "${GREEN}✓ Dependencies OK${NC}"
echo ""

# Check database connection
echo -e "${GREEN}[2/5] Checking database connection...${NC}"
python manage.py check --database default || {
    echo -e "${RED}Error: Database connection failed${NC}"
    exit 1
}
echo -e "${GREEN}✓ Database OK${NC}"
echo ""

# Run migrations for test database
echo -e "${GREEN}[3/5] Preparing test database...${NC}"
python manage.py makemigrations --check --dry-run >/dev/null 2>&1 || {
    echo -e "${YELLOW}Warning: Pending migrations detected${NC}"
}
echo -e "${GREEN}✓ Test database ready${NC}"
echo ""

# Run integration tests
echo -e "${GREEN}[4/5] Running integration tests...${NC}"
echo ""

if [ "$1" = "--fast" ]; then
    # Fast mode: no coverage
    pytest tests/integration/ -v --tb=short
elif [ "$1" = "--coverage" ]; then
    # Coverage mode: detailed coverage report
    pytest tests/integration/ \
        --cov=dora_metrics \
        --cov=callcentersite \
        --cov-report=term-missing \
        --cov-report=html:htmlcov/integration \
        --cov-branch \
        -v

    echo ""
    echo -e "${GREEN}Coverage report generated: htmlcov/integration/index.html${NC}"
elif [ "$1" = "--parallel" ]; then
    # Parallel mode: faster execution
    pytest tests/integration/ -n auto -v
else
    # Default mode: standard run with coverage
    pytest tests/integration/ \
        --cov=dora_metrics \
        --cov=callcentersite \
        --cov-report=term \
        -v
fi

TEST_EXIT_CODE=$?

echo ""

# Report results
echo -e "${GREEN}[5/5] Test Results${NC}"
echo ""

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}✓ ALL INTEGRATION TESTS PASSED${NC}"
    echo -e "${GREEN}========================================${NC}"
    exit 0
else
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}✗ SOME INTEGRATION TESTS FAILED${NC}"
    echo -e "${RED}========================================${NC}"
    exit 1
fi
