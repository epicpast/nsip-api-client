.PHONY: help install install-dev test test-cov lint format clean build publish docs

.DEFAULT_GOAL := help

help:  ## Show this help message with categorized targets
	@echo '================================'
	@echo 'NSIP API Client - Make Targets'
	@echo '================================'
	@echo ''
	@echo 'Usage: make [target]'
	@echo ''
	@echo '📦 Installation & Setup:'
	@grep -E '^(install|install-dev|init-dev):.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ''
	@echo '✅ Quality Gates (run before commit):'
	@grep -E '^(ci-local|quality-gates|quality):.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ''
	@echo '🔍 Code Quality Tools:'
	@grep -E '^(lint|format|format-check|security):.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ''
	@echo '🧪 Testing:'
	@grep -E '^(test|test-cov):.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ''
	@echo '🔨 Build & Package:'
	@grep -E '^(build|check-package|clean):.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ''
	@echo '📚 Documentation & Examples:'
	@grep -E '^(docs|run-example|run-advanced):.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ''
	@echo '💡 Quick Start:'
	@echo '  1. make install-dev     # Install with dev dependencies'
	@echo '  2. make ci-local        # Run all quality gates'
	@echo '  3. make test-cov        # Run tests with coverage'
	@echo ''
	@echo '📖 For detailed development workflow, see CLAUDE.md'
	@echo ''

install:  ## Install package
	pip install -e .

install-dev:  ## Install package with development dependencies
	pip install -e ".[dev]"

test:  ## Run tests
	pytest

test-cov:  ## Run tests with coverage report
	pytest --cov=nsip_client --cov-report=html --cov-report=term-missing

lint:  ## Run linters (flake8 critical + full, mypy)
	@echo "Critical errors (E9, F63, F7, F82)..."
	flake8 src/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics
	@echo "\nStyle warnings (max-complexity=10, max-line-length=100)..."
	flake8 src/ tests/ --count --exit-zero --max-complexity=10 --max-line-length=100 --statistics
	@echo "\nFull flake8 check..."
	flake8 src/ tests/
	@echo "\nType checking..."
	mypy src/ --ignore-missing-imports

format:  ## Format code with black and isort
	black src/ tests/ examples/
	isort src/ tests/ examples/

format-check:  ## Check code formatting
	black --check src/ tests/ examples/
	isort --check src/ tests/ examples/

security:  ## Run security checks with bandit
	@echo "Running bandit security scan (high/low severity only)..."
	@bandit -r src/ -ll || uv run bandit -r src/ -ll

quality-gates:  ## Run ALL quality gates (matches CI/CD)
	@echo "========================================="
	@echo "Quality Gate Checks (matches GitHub Actions)"
	@echo "========================================="
	@echo ""
	@echo "Step 1: Black formatting..."
	@black --check src/ tests/ examples/
	@echo "✅ Black: PASS\n"
	@echo "Step 2: isort import sorting..."
	@isort --check-only src/ tests/ examples/
	@echo "✅ isort: PASS\n"
	@echo "Step 3: flake8 linting (critical)..."
	@flake8 src/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics
	@echo "✅ flake8 critical: PASS\n"
	@echo "Step 4: flake8 full check..."
	@flake8 src/ tests/
	@echo "✅ flake8 full: PASS\n"
	@echo "Step 5: mypy type checking..."
	@mypy src/ --ignore-missing-imports
	@echo "✅ mypy: PASS\n"
	@echo "Step 6: pytest with coverage..."
	@pytest --cov=nsip_client --cov=nsip_mcp --cov-report=term-missing --cov-fail-under=80 -v
	@echo "\n✅ ALL QUALITY GATES PASSED"

quality:  ## Run all quality checks (auto-fix formatting, then check)
	@echo "Running black (auto-fix)..."
	@black src/ tests/ examples/
	@echo "\nRunning isort (auto-fix)..."
	@isort src/ tests/ examples/
	@echo "\nRunning flake8..."
	@flake8 src/ tests/
	@echo "\nRunning mypy..."
	@mypy src/ --ignore-missing-imports
	@echo "\nRunning tests..."
	@pytest --cov=nsip_client --cov=nsip_mcp --cov-report=term-missing

ci-local:  ## Run exact CI/CD checks locally (no auto-fix)
	./run_tests_and_coverage.sh

clean:  ## Clean build artifacts and cache files
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build:  ## Build distribution packages
	python -m build

check-package:  ## Validate package without publishing
	python -m build
	twine check dist/*
	@echo "✅ Package is valid and ready for GitHub release"
	@echo "⚠️  This project does NOT publish to PyPI"
	@echo "📦 Users install from GitHub releases"

docs:  ## Build documentation
	cd docs && make html

run-example:  ## Run basic usage example
	python examples/basic_usage.py

run-advanced:  ## Run advanced search example
	python examples/advanced_search.py

init-dev:  ## Initialize development environment
	python -m venv venv
	@echo "Virtual environment created. Activate with:"
	@echo "  source venv/bin/activate  (Linux/Mac)"
	@echo "  venv\\Scripts\\activate     (Windows)"
	@echo "Then run: make install-dev"
