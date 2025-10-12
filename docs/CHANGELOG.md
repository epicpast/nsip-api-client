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

## [1.1.0] - 2025-10-11

### Added
- **MCP Server**: New Model Context Protocol server for LLM integration
  - Command: `nsip-mcp-server` CLI for starting the MCP server
  - 9 MCP tools wrapping NSIP API operations:
    - `nsip_get_last_update`: Database last updated timestamp
    - `nsip_list_breeds`: List available breed groups
    - `nsip_get_statuses`: Get status options by breed group
    - `nsip_get_trait_ranges`: Get trait ranges by breed
    - `nsip_search_animals`: Search animals with filters
    - `nsip_get_animal`: Get detailed animal information
    - `nsip_get_lineage`: Get animal lineage/pedigree
    - `nsip_get_progeny`: Get animal progeny list
    - `nsip_search_by_lpn`: Comprehensive animal lookup
  - Multiple transport options:
    - stdio (default, for MCP clients)
    - HTTP SSE (for web applications)
    - WebSocket (for real-time bidirectional communication)
  - Context management system:
    - Automatic response summarization for large datasets (>2000 tokens)
    - 70% token reduction target to prevent LLM context overflow
    - Preserves key information: identity, pedigree, contact, top 3 traits
    - Metadata tracking (`_summarized`, `_original_token_count`, `_reduction_percent`)
  - Smart caching layer:
    - 1-hour TTL for API responses
    - 40%+ cache hit rate target
    - 1000 entry max size with FIFO eviction
    - Cache metrics tracking (hits, misses, hit rate)
  - Performance monitoring:
    - Server health endpoint (`get_server_health` tool)
    - Metrics tracking for all operations
    - Success criteria validation (SC-001 through SC-012)
  - Structured error handling:
    - JSON-RPC 2.0 compliant error responses
    - LLM-friendly error messages with actionable suggestions
    - Parameter validation before API calls (95%+ catch rate target)
  - Documentation:
    - Comprehensive MCP server section in README.md
    - Quickstart guide (`specs/001-create-an-mcp/quickstart.md`)
    - Environment variable configuration
    - Transport setup examples
    - Error handling examples

### Dependencies
- **Added**: `fastmcp>=2.0` - FastMCP framework for MCP server implementation
- **Added**: `tiktoken>=0.5.0` - Token counting for context management (GPT-4 tokenizer)

### Performance Targets
- Tool discovery: <5 seconds from connection
- Summarization: ≥70% token reduction for large responses
- Validation: ≥95% invalid requests caught before API
- Cache hit rate: ≥40% in typical usage
- Concurrent connections: Support 50+ without degradation
- Startup time: <3 seconds to ready state

### Distribution
- Package remains GitHub-only (not published to PyPI per DISTRIBUTION.md policy)
- Install via: `pip install git+https://github.com/epicpast/nsip-api-client@v1.1.0`
- Or use uvx: `uvx --from git+https://github.com/epicpast/nsip-api-client@v1.1.0 nsip-mcp-server`

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
animal = client.get_animal_details("6401492020FLE249")
print(f"{animal.breed} - {animal.gender}")
```

**Important Notes:**
- This client was reverse-engineered from the public NSIP website
- The API is not officially documented and may change without notice
- No authentication is required - it's a public API
- Please use responsibly and respect rate limits

**Reverse Engineering Credits:**
This client was created through network traffic analysis using Chrome DevTools. All endpoints and data structures were discovered by observing the NSIP Search web application at http://nsipsearch.nsip.org
