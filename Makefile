.PHONY: help install install-dev test test-cov lint typecheck security coverage format clean build docker-build publish docs quality

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
	@grep -E '^(lint|typecheck|format|format-check|security):.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ''
	@echo '🧪 Testing:'
	@grep -E '^(test|test-cov|coverage):.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ''
	@echo '🔨 Build & Package:'
	@grep -E '^(build|docker-build|check-package|clean):.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
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

lint:  ## Run linters (ruff check)
	@echo "Running ruff..."
	ruff check src/ tests/ || uv run ruff check src/ tests/

typecheck:  ## Run type checker (mypy)
	@echo "Running mypy type checking..."
	mypy src/ --ignore-missing-imports || uv run mypy src/ --ignore-missing-imports

coverage:  ## Run tests with coverage (80% minimum)
	@echo "Running pytest with coverage..."
	pytest --cov=nsip_client --cov=nsip_mcp --cov-report=term-missing --cov-report=html --cov-fail-under=80 --override-ini="addopts=" -v || \
	uv run pytest --cov=nsip_client --cov=nsip_mcp --cov-report=term-missing --cov-report=html --cov-fail-under=80 --override-ini="addopts=" -v

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

quality:  ## Run all quality checks (format, lint, typecheck, security, coverage)
	@echo "========================================="
	@echo "Running Full Quality Suite"
	@echo "========================================="
	@echo ""
	@echo "Step 1: Formatting (black + isort)..."
	@black src/ tests/ examples/ || uv run black src/ tests/ examples/
	@isort src/ tests/ examples/ || uv run isort src/ tests/ examples/
	@echo "✅ Formatting: PASS\n"
	@echo "Step 2: Linting (ruff)..."
	@ruff check src/ tests/ || uv run ruff check src/ tests/
	@echo "✅ Linting: PASS\n"
	@echo "Step 3: Type checking (mypy)..."
	@mypy src/ --ignore-missing-imports || uv run mypy src/ --ignore-missing-imports
	@echo "✅ Type checking: PASS\n"
	@echo "Step 4: Security (bandit)..."
	@bandit -r src/ -ll -q || uv run bandit -r src/ -ll -q
	@echo "✅ Security: PASS\n"
	@echo "Step 5: Tests with coverage (80% minimum)..."
	@pytest --cov=nsip_client --cov=nsip_mcp --cov-report=term-missing --cov-fail-under=80 --override-ini="addopts=" -q || \
	 uv run pytest --cov=nsip_client --cov=nsip_mcp --cov-report=term-missing --cov-fail-under=80 --override-ini="addopts=" -q
	@echo "\n========================================="
	@echo "✅ ALL QUALITY CHECKS PASSED"
	@echo "========================================="

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

docker-build:  ## Build Docker image
	@echo "Building Docker image..."
	docker build -t nsip-mcp-server:latest .
	@echo "✅ Docker image built: nsip-mcp-server:latest"

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
