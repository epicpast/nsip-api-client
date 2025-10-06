# Installation Guide

## Quick Install

### From Source (Recommended for Development)

```bash
# Clone the repository
git clone https://github.com/yourusername/nsip-api-client.git
cd nsip-api-client

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

### From PyPI (When Published)

```bash
pip install nsip-client
```

## Requirements

- Python 3.8 or higher
- pip (Python package installer)

## Platform-Specific Instructions

### Linux/macOS

```bash
# Install Python (if not already installed)
# Ubuntu/Debian:
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv

# macOS (using Homebrew):
brew install python3

# Clone and install
git clone https://github.com/yourusername/nsip-api-client.git
cd nsip-api-client
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

### Windows

```powershell
# Install Python from python.org (if not already installed)

# Clone and install
git clone https://github.com/yourusername/nsip-api-client.git
cd nsip-api-client
python -m venv venv
venv\Scripts\activate
pip install -e ".[dev]"
```

## Installation Options

### Minimal Installation (Production)

Install only the required dependencies:

```bash
pip install -e .
```

### Development Installation

Install with all development tools (recommended for contributors):

```bash
pip install -e ".[dev]"
```

This includes:
- pytest (testing framework)
- black, isort (code formatting)
- flake8, mypy (linting and type checking)
- pytest-cov (coverage reporting)
- requests-mock (testing utilities)

### Documentation Build

To build documentation locally:

```bash
pip install -e ".[docs]"
cd docs
make html
```

## Verify Installation

After installation, verify it works:

```bash
# Using Python
python -c "from nsip_client import NSIPClient; print('Installation successful!')"

# Using the CLI
nsip-search breeds

# Run tests
pytest

# Run examples
python examples/basic_usage.py
```

## Using Make Commands

If you have `make` installed, you can use convenient shortcuts:

```bash
# Initialize development environment
make init-dev

# Install development dependencies
make install-dev

# Run tests
make test

# Run tests with coverage
make test-cov

# Format code
make format

# Run linters
make lint

# Run all quality checks
make quality

# See all available commands
make help
```

## Docker Installation (Optional)

If you prefer using Docker:

```bash
# Build image
docker build -t nsip-client .

# Run examples in container
docker run nsip-client python examples/basic_usage.py
```

## Troubleshooting

### ImportError: No module named 'nsip_client'

Make sure you've activated your virtual environment and installed the package:

```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -e .
```

### Permission Errors on Linux/macOS

If you get permission errors, make sure you're using a virtual environment. Never use `sudo pip install`.

### SSL Certificate Errors

If you encounter SSL errors when making API requests:

```bash
pip install --upgrade certifi
```

### Python Version Issues

Check your Python version:

```bash
python --version  # Should be 3.8 or higher
```

If you have multiple Python versions, use `python3` explicitly:

```bash
python3 -m venv venv
```

## Uninstallation

```bash
pip uninstall nsip-client
```

## Next Steps

After installation:

1. Read the [README.md](README.md) for usage examples
2. Check out [examples/](examples/) for code samples
3. Review [CONTRIBUTING.md](CONTRIBUTING.md) if you want to contribute
4. Run `make help` to see available development commands
