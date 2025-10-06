#!/bin/bash
# Test execution and coverage verification script

set -e

echo "========================================="
echo "NSIP API Client - Test Coverage Report"
echo "========================================="
echo ""

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Run quality checks
echo "Step 1: Running code quality checks..."
echo "---------------------------------------"

echo "  - black (code formatting)..."
black --check src/ tests/ 2>&1 | head -5 || true

echo "  - isort (import sorting)..."
isort --check-only src/ tests/ 2>&1 | head -5 || true

echo "  - flake8 (linting)..."
flake8 src/ tests/ --max-line-length=100 2>&1 | head -5 || true

echo "  - mypy (type checking)..."
mypy src/ 2>&1 | head -5 || true

echo ""
echo "Step 2: Running test suite with coverage..."
echo "--------------------------------------------"

# Run pytest with coverage
pytest --cov=nsip_client --cov-report=term-missing --cov-report=html -v

echo ""
echo "Step 3: Coverage Summary"
echo "------------------------"

# Generate coverage summary
coverage report --precision=2

echo ""
echo "========================================="
echo "Test Execution Complete!"
echo "========================================="
echo ""
echo "View detailed HTML coverage report at:"
echo "  file://$(pwd)/htmlcov/index.html"
echo ""
