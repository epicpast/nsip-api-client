.PHONY: help install install-dev test test-cov lint format clean build publish docs

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install package
	pip install -e .

install-dev:  ## Install package with development dependencies
	pip install -e ".[dev]"

test:  ## Run tests
	pytest

test-cov:  ## Run tests with coverage report
	pytest --cov=nsip_client --cov-report=html --cov-report=term-missing

lint:  ## Run linters (flake8, mypy)
	flake8 src/ tests/
	mypy src/

format:  ## Format code with black and isort
	black src/ tests/ examples/
	isort src/ tests/ examples/

format-check:  ## Check code formatting
	black --check src/ tests/ examples/
	isort --check src/ tests/ examples/

quality:  ## Run all quality checks (format, lint, test)
	@echo "Running black..."
	@black src/ tests/ examples/
	@echo "\nRunning isort..."
	@isort src/ tests/ examples/
	@echo "\nRunning flake8..."
	@flake8 src/ tests/
	@echo "\nRunning mypy..."
	@mypy src/
	@echo "\nRunning tests..."
	@pytest --cov=nsip_client --cov-report=term-missing

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
