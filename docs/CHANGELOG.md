# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.2] - 2025-10-12

### Added
- **Claude Code Plugin**: One-command installation for Claude Code users
  - Plugin marketplace configuration (`.claude-plugin/marketplace.json`)
  - Auto-start MCP server configuration (`.claude-plugin/plugin.json`)
  - 9 slash commands for common NSIP workflows:
    - `/nsip/discover` - Show database info, breeds, and statuses
    - `/nsip/lookup` - Get animal details by LPN ID
    - `/nsip/profile` - Complete animal profile (details + lineage + progeny)
    - `/nsip/health` - MCP server performance metrics
    - `/nsip/test-api` - Validate API connectivity
    - `/nsip/search` - Search animals with filters
    - `/nsip/traits` - Get trait ranges by breed
    - `/nsip/lineage` - View pedigree tree
    - `/nsip/progeny` - List offspring
  - Comprehensive plugin README with installation guide
  - Optional custom NSIP_BASE_URL environment variable (defaults to http://nsipsearch.nsip.org/api)
  - No authentication required - NSIP API is public
  - 59 validation tests for plugin configuration
  - Works on both Claude Code CLI and VS Code extension

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

#### MCP Server Implementation
Complete Model Context Protocol (MCP) server for seamless integration with Claude Code and other MCP-compatible AI assistants.

- **10 MCP Tools** exposing complete NSIP API functionality:
  1. `nsip_get_last_update` - Get database last update timestamp
  2. `nsip_list_breeds` - List all available breed groups
  3. `nsip_get_statuses` - Get evaluation statuses by breed group
  4. `nsip_get_trait_ranges` - Get trait ranges for a breed
  5. `nsip_search_animals` - Search animals with criteria and pagination
  6. `nsip_get_animal` - Get complete animal details
  7. `nsip_get_lineage` - Get animal pedigree information
  8. `nsip_get_progeny` - Get animal offspring with pagination
  9. `nsip_search_by_lpn` - Get comprehensive animal profile by LPN ID
  10. `nsip_get_server_metrics` - Get server performance metrics

#### Multi-Transport Support
- **stdio** (default) - Standard input/output for local MCP clients
- **HTTP SSE** - Server-Sent Events for web integration
- **WebSocket** - Full-duplex bidirectional communication
- Environment variable configuration (`MCP_TRANSPORT`, `MCP_PORT`)

#### Smart Context Management
- Automatic response summarization for large datasets (>2000 tokens)
- 70%+ token reduction achieved (measured: >90%)
- Preserves critical information: identity, pedigree, contact, top traits
- Metadata tracking: `_summarized`, `_original_token_count`, `_reduction_percent`
- Pass-through mode for small responses (≤2000 tokens)

#### Response Caching
- Thread-safe TTL cache with 1-hour default expiration
- FIFO eviction policy with 1000 entry max size
- Cache metrics tracking (hits, misses, hit rate)
- 40%+ cache hit rate in typical usage
- Per-operation cache key generation

#### Performance & Monitoring
- Real-time metrics collection for all operations
- Success criteria validation (SC-001 through SC-007)
- Performance benchmarks suite
- Server startup time: <0.1s (target: <3s)
- Tool discovery time: <1s (target: <5s)

#### Error Handling
- JSON-RPC 2.0 compliant error responses
- Actionable error messages for LLMs
- Parameter validation before API calls (95%+ success rate)
- Comprehensive error codes and suggestions
- Detailed error context for debugging

#### Docker Deployment
- Production-ready Dockerfile with multi-stage build
- Docker Compose configuration with health checks
- Security hardening with non-root user
- Volume management for data persistence
- Complete deployment documentation (`docs/docker.md`)

#### Testing & Quality
- **289 comprehensive tests** (100% pass rate)
- **92.54% code coverage** (exceeds 80% requirement)
- Zero skipped tests (complete implementation)
- All CI quality gates passing:
  - Black formatting ✅
  - isort import sorting ✅
  - flake8 linting ✅ (0 critical errors)
  - mypy type checking ✅
  - pytest with coverage ✅
- Local quality gate validation script (`run_tests_and_coverage.sh`)

#### Documentation
- Complete MCP server guide (`docs/mcp-server.md`)
- Docker deployment guide (`docs/docker.md`)
- Full technical specification (`specs/001-create-an-mcp/`)
- API contracts in JSON (`specs/001-create-an-mcp/contracts/mcp-tools.json`)
- Quickstart guide with examples
- Environment configuration reference

### Changed
- Enhanced GitHub Actions workflows for nsip_mcp coverage tracking
- Improved test infrastructure with benchmark and integration suites
- Updated Python version requirements (3.10+ for MCP server)
- Reorganized documentation into `docs/` directory

### Dependencies
- **Added**: `fastmcp>=2.0.0` - FastMCP framework for MCP server
- **Added**: `tiktoken>=0.5.0` - Token counting (cl100k_base encoding)
- Updated Python support: 3.10, 3.11, 3.12, 3.13

### Performance Metrics (Achieved)
- ✅ Tool discovery: <1s (target: <5s)
- ✅ Token reduction: >90% (target: ≥70%)
- ✅ Validation success: 100% (target: ≥95%)
- ✅ Startup time: <0.1s (target: <3s)
- ✅ Code coverage: 92.54% (target: ≥80%)

### Security
- Removed sensitive configuration files from git history
- Added `.gitignore` entries for personal configuration
- Secure Docker deployment with non-root user
- Input validation on all MCP tools
- Type checking with mypy (PEP 561 compliant)

### Distribution
- Package remains GitHub-only (not published to PyPI)
- Install via: `pip install nsip-api-client[mcp]` (from source)
- Docker images available via `docker-compose up`
- CLI command: `nsip-mcp` for server startup

## [1.1.1] - 2025-10-12

### Changed

#### Streamable HTTP Transport Migration
Migrated from legacy HTTP SSE to modern Streamable HTTP transport following MCP specification 2025-03-26.

- **Transport Rename**: `HTTP_SSE` → `STREAMABLE_HTTP` in `TransportType` enum
- **Backward Compatibility**: Legacy `http-sse` environment variable value automatically mapped to `streamable-http`
- **Enhanced Configuration**:
  - Added `MCP_HOST` environment variable (default: `0.0.0.0`)
  - Added `MCP_PATH` environment variable (default: `/mcp`)
  - Updated `TransportConfig` dataclass with `host` and `path` attributes
- **Server Implementation**: Updated `start_server()` to use FastMCP 2.12.4+ native Streamable HTTP support
  - Endpoint: `POST {host}:{port}{path}` (e.g., `POST http://0.0.0.0:8000/mcp`)
  - Session management via MCP protocol
  - Improved error handling and connection lifecycle

#### Updated Transport Options
- **stdio** (unchanged): Default transport for local MCP clients
- **streamable-http** (new): Modern MCP-compliant HTTP transport with session management
- **websocket** (unchanged): Real-time bidirectional communication

#### Documentation Updates
- Updated `docs/mcp-server.md` with Streamable HTTP specification (replaced HTTP SSE section)
- Added migration guide from HTTP SSE to Streamable HTTP
- Updated environment variable documentation
- Added Streamable HTTP endpoint structure and examples
- Updated `cli.py` docstrings to reference `streamable-http` transport

### Migration Guide

**For existing HTTP SSE users:**

Old configuration (still supported):
```bash
MCP_TRANSPORT=http-sse MCP_PORT=8000 nsip-mcp-server
```

New configuration (recommended):
```bash
MCP_TRANSPORT=streamable-http MCP_PORT=8000 nsip-mcp-server
```

**Additional configuration options:**
```bash
MCP_TRANSPORT=streamable-http
MCP_PORT=8000
MCP_HOST=0.0.0.0  # Optional, default: 0.0.0.0
MCP_PATH=/mcp     # Optional, default: /mcp
nsip-mcp-server
```

**Endpoint changes:**
- Old: `POST /messages`, `GET /sse`
- New: `POST /mcp`, `GET /mcp` (unified endpoint with session management)

### Technical Details

- **MCP Specification**: Compliant with MCP Streamable HTTP transport spec (2025-03-26)
- **Session Management**: Automatic session lifecycle management via MCP protocol
- **Connection Handling**: Improved connection pooling and error recovery
- **Performance**: No performance impact, same startup time and throughput as v1.1.0
- **Testing**: All existing tests passing, no breaking changes to stdio or websocket transports

### Compatibility

- ✅ **Backward compatible**: Legacy `http-sse` configuration automatically mapped to `streamable-http`
- ✅ **No breaking changes**: stdio and websocket transports unchanged
- ✅ **Drop-in replacement**: Existing MCP clients work without modification

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
