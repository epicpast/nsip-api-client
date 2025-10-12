#!/bin/bash
# Test execution and coverage verification script
# Matches all GitHub Actions CI quality gates

set -e  # Exit on first error

echo "========================================="
echo "NSIP API Client - Quality Gate Checks"
echo "========================================="
echo ""

# Prefer uv if available, fallback to system Python
if command -v uv &> /dev/null; then
    PYTHON_CMD="uv run"
    echo "Using: uv (modern Python package manager)"
else
    PYTHON_CMD=""
    echo "Using: system Python"
    # Activate virtual environment if it exists
    if [ -d ".venv" ]; then
        echo "Activating virtual environment..."
        source .venv/bin/activate
    fi
fi
echo ""

# Track overall status
FAILED_CHECKS=0

echo "Step 1: Code Formatting (Black)"
echo "--------------------------------"
if $PYTHON_CMD black --check src/ tests/ examples/; then
    echo "✅ Black formatting: PASS"
else
    echo "❌ Black formatting: FAIL"
    ((FAILED_CHECKS++))
fi
echo ""

echo "Step 2: Import Sorting (isort)"
echo "-------------------------------"
if $PYTHON_CMD isort --check-only src/ tests/ examples/; then
    echo "✅ isort import sorting: PASS"
else
    echo "❌ isort import sorting: FAIL"
    ((FAILED_CHECKS++))
fi
echo ""

echo "Step 3: Linting (flake8)"
echo "------------------------"
echo "  Critical errors (E9, F63, F7, F82)..."
FLAKE8_CRITICAL=$($PYTHON_CMD flake8 src/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics)
if [ "$FLAKE8_CRITICAL" = "0" ]; then
    echo "✅ flake8 critical: PASS (0 errors)"
else
    echo "❌ flake8 critical: FAIL ($FLAKE8_CRITICAL errors)"
    $PYTHON_CMD flake8 src/ tests/ --select=E9,F63,F7,F82 --show-source
    ((FAILED_CHECKS++))
fi

echo "  Style warnings (informational, exit-zero)..."
FLAKE8_STYLE=$($PYTHON_CMD flake8 src/ tests/ --count --exit-zero --max-complexity=10 --max-line-length=100 --statistics | tail -1)
echo "ℹ️  flake8 style warnings: $FLAKE8_STYLE (non-blocking)"
echo ""

echo "Step 4: Type Checking (mypy)"
echo "----------------------------"
if $PYTHON_CMD mypy src/ --ignore-missing-imports; then
    echo "✅ mypy type checking: PASS"
else
    echo "❌ mypy type checking: FAIL"
    ((FAILED_CHECKS++))
fi
echo ""

echo "Step 5: Test Suite & Coverage"
echo "------------------------------"
if $PYTHON_CMD pytest --cov=nsip_client --cov=nsip_mcp --cov-report=term-missing --cov-report=html --cov-report=xml --cov-fail-under=80 -v; then
    echo "✅ pytest & coverage: PASS"
else
    echo "❌ pytest & coverage: FAIL"
    ((FAILED_CHECKS++))
fi
echo ""

echo "Step 6: Coverage Report"
echo "-----------------------"
$PYTHON_CMD coverage report --precision=2
echo ""

echo "========================================="
echo "Quality Gate Summary"
echo "========================================="
echo ""
echo "Checks run: 5 quality gates"
echo "Failed checks: $FAILED_CHECKS"
echo ""

if [ $FAILED_CHECKS -eq 0 ]; then
    echo "✅ ALL QUALITY GATES PASSED"
    echo ""
    echo "View detailed HTML coverage report at:"
    echo "  file://$(pwd)/htmlcov/index.html"
    echo ""
    exit 0
else
    echo "❌ QUALITY GATES FAILED"
    echo ""
    echo "Fix the errors above and run again."
    echo ""
    exit 1
fi
