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
if $PYTHON_CMD flake8 src/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics; then
    echo "✅ flake8 critical: PASS (0 errors)"
else
    echo "❌ flake8 critical: FAIL"
    ((FAILED_CHECKS++))
fi

echo "  Style warnings (max-complexity=10, max-line-length=100)..."
FLAKE8_STYLE=$($PYTHON_CMD flake8 src/ tests/ --count --exit-zero --max-complexity=10 --max-line-length=100 --statistics 2>&1 | tail -1)
echo "ℹ️  flake8 style warnings: $FLAKE8_STYLE (non-blocking)"

echo "  Full flake8 check (matching PR gates)..."
if $PYTHON_CMD flake8 src/ tests/; then
    echo "✅ flake8 full: PASS"
else
    echo "❌ flake8 full: FAIL"
    ((FAILED_CHECKS++))
fi
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

echo "Step 5: Security Check (bandit)"
echo "--------------------------------"
if $PYTHON_CMD bandit -r src/ -ll -q 2>/dev/null; then
    echo "✅ bandit security: PASS"
else
    echo "⚠️  bandit security: Install with 'pip install bandit' (non-blocking)"
fi
echo ""

echo "Step 6: Test Suite & Coverage"
echo "------------------------------"
if $PYTHON_CMD pytest --cov=nsip_client --cov=nsip_mcp --cov-report=term-missing --cov-report=html --cov-report=xml --cov-fail-under=80 -v; then
    echo "✅ pytest & coverage: PASS"
else
    echo "❌ pytest & coverage: FAIL"
    ((FAILED_CHECKS++))
fi
echo ""

echo "Step 7: Coverage Report"
echo "-----------------------"
$PYTHON_CMD coverage report --precision=2
echo ""

echo "Step 8: Package Build Validation"
echo "---------------------------------"
if command -v python &> /dev/null; then
    if python -m build --help &>/dev/null 2>&1; then
        echo "  Building package..."
        if python -m build &>/dev/null; then
            echo "✅ package build: PASS"
            if command -v twine &> /dev/null; then
                echo "  Checking package metadata..."
                if twine check dist/* &>/dev/null; then
                    echo "✅ package metadata: PASS"
                else
                    echo "⚠️  package metadata: Issues found (non-blocking)"
                fi
            else
                echo "ℹ️  twine not installed (optional check)"
            fi
        else
            echo "⚠️  package build: FAIL (non-blocking)"
        fi
    else
        echo "ℹ️  build package not installed (optional check)"
    fi
else
    echo "ℹ️  Package build check skipped (build module not available)"
fi
echo ""

echo "========================================="
echo "Quality Gate Summary"
echo "========================================="
echo ""
echo "Checks run: 6 required quality gates"
echo "Failed checks: $FAILED_CHECKS"
echo ""

if [ $FAILED_CHECKS -eq 0 ]; then
    echo "✅ ALL QUALITY GATES PASSED"
    echo ""
    echo "Quality Gates Passed:"
    echo "  ✅ Black formatting"
    echo "  ✅ isort import sorting"
    echo "  ✅ flake8 linting (critical & full)"
    echo "  ✅ mypy type checking"
    echo "  ✅ pytest & coverage (>80%)"
    echo ""
    echo "Optional Checks:"
    echo "  ℹ️  bandit security scan"
    echo "  ℹ️  package build validation"
    echo ""
    echo "View detailed HTML coverage report at:"
    echo "  file://$(pwd)/htmlcov/index.html"
    echo ""
    echo "✅ Ready for commit and push"
    echo ""
    exit 0
else
    echo "❌ QUALITY GATES FAILED"
    echo ""
    echo "Failed checks: $FAILED_CHECKS"
    echo ""
    echo "Fix the errors above and run again."
    echo "All quality gates must pass before merge."
    echo ""
    exit 1
fi
