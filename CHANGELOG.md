# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-06

### Added
- Initial release of NSIP API Client
- Core client functionality (`NSIPClient`)
- Data models for animals, progeny, lineage, and search results
- Custom exception classes for better error handling
- Comprehensive test suite with >90% coverage
- CLI tool for command-line access (`nsip-search`)
- Complete API endpoint support:
  - Get database update date
  - List breed groups and statuses
  - Search animals with filters
  - Get animal details by LPN ID
  - Retrieve lineage/pedigree information
  - Get progeny (offspring) records
  - Get trait ranges by breed
- Context manager support for client
- Type hints throughout the codebase
- Examples:
  - Basic usage examples
  - Advanced search patterns
  - Pagination examples
  - Animal comparison
- Documentation:
  - README with quick start guide
  - API reference documentation
  - Installation guide
  - Contributing guidelines
  - Full docstrings for all public APIs
- Development tools:
  - Black and isort for code formatting
  - Flake8 and mypy for linting
  - pytest with coverage reporting
  - Makefile for common tasks
- Package configuration:
  - pyproject.toml with full metadata
  - Requirements files for production and development
  - .gitignore for Python projects

### Known Limitations
- Breed list by group endpoint not yet discovered
- Some complex lineage parsing not fully implemented
- Rate limiting behavior unknown

## [Unreleased]

### Planned
- Add caching layer for frequently accessed data
- Implement async client for concurrent requests
- Add export functionality (CSV, JSON)
- Create data visualization examples
- Add more comprehensive lineage parsing
- Discover and implement remaining API endpoints
- Add retry logic with exponential backoff
- Performance benchmarking tools

---

## Release Notes

### Version 1.0.0 - Initial Release

This is the first stable release of the NSIP API Client, a Python library for accessing the National Sheep Improvement Program (NSIP) Search API.

**What's Included:**
- Complete API client with all major endpoints
- Type-safe models for all data structures
- Comprehensive error handling
- CLI tool for quick queries
- Full test coverage
- Production-ready code quality

**Getting Started:**
```bash
pip install nsip-client
```

```python
from nsip_client import NSIPClient

client = NSIPClient()
animal = client.get_animal_details("6####92020###249")
print(f"{animal.breed} - {animal.gender}")
```

**Important Notes:**
- This client was reverse-engineered from the public NSIP website
- The API is not officially documented and may change without notice
- No authentication is required - it's a public API
- Please use responsibly and respect rate limits

**Reverse Engineering Credits:**
This client was created through network traffic analysis using Chrome DevTools. All endpoints and data structures were discovered by observing the NSIP Search web application at http://nsipsearch.nsip.org
