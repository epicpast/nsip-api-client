# Contributing to NSIP Client

Thank you for your interest in contributing to the NSIP API Client!

## Development Setup

### Prerequisites
- Python 3.8 or higher
- pip and virtualenv

### Getting Started

1. Clone the repository:
```bash
git clone https://github.com/yourusername/nsip-api-client.git
cd nsip-api-client
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -e ".[dev]"
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=nsip_client --cov-report=html

# Run specific test file
pytest tests/test_client.py

# Run specific test
pytest tests/test_client.py::TestNSIPClient::test_get_animal_details
```

## Code Quality

### Formatting
We use `black` and `isort` for code formatting:

```bash
# Format code
black src/ tests/
isort src/ tests/

# Check formatting
black --check src/ tests/
isort --check src/ tests/
```

### Linting
We use `flake8` and `mypy` for linting:

```bash
# Run flake8
flake8 src/ tests/

# Run mypy
mypy src/
```

### All Quality Checks
Run all quality checks before committing:

```bash
black src/ tests/
isort src/ tests/
flake8 src/ tests/
mypy src/
pytest --cov=nsip_client
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and quality checks
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### PR Requirements
- All tests must pass
- Code coverage should not decrease
- Code must be formatted with black and isort
- Mypy type checking must pass
- Include tests for new features
- Update documentation as needed

## Code Style Guidelines

- Follow PEP 8
- Use type hints for all public functions
- Write docstrings for all public classes and methods
- Keep functions focused and small
- Prefer composition over inheritance

## Testing Guidelines

- Write unit tests for all new code
- Use mocks for API calls
- Test both success and error cases
- Aim for >90% code coverage

## Documentation

- Update README.md for user-facing changes
- Add docstrings to all public APIs
- Include usage examples
- Document breaking changes

## Commit Messages

Use clear, descriptive commit messages:

```
feat: Add support for advanced search filters
fix: Handle timeout errors correctly
docs: Update API examples in README
test: Add tests for progeny pagination
refactor: Simplify error handling logic
```

## Reporting Issues

When reporting issues, please include:
- Python version
- NSIP client version
- Minimal code to reproduce the issue
- Expected vs actual behavior
- Error messages and stack traces

## Questions?

Feel free to open an issue for questions or discussions.
