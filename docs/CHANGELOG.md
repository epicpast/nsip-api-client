# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.4] - 2025-12-07

### Added
- **5 Shepherd MCP Tools**: Exposed the AI Shepherd advisor as MCP tools
  - `shepherd_consult` - General sheep husbandry advice
  - `shepherd_breeding` - EBV interpretation, mating advice, genetics
  - `shepherd_health` - Disease prevention, nutrition, parasites
  - `shepherd_calendar` - Seasonal planning, breeding schedules
  - `shepherd_economics` - Cost analysis, ROI, market timing

- **Enhanced `nsip_list_breeds`**: Now returns individual breeds within each breed group
  - Response includes `breeds` array per group with breed id and name
  - Example: `{"id": 64, "name": "Hair", "breeds": [{"id": 640, "name": "Katahdin"}, ...]}`

### Changed
- MCP tool count increased from 10 to 15 (10 NSIP API + 5 Shepherd tools)
- Transport documentation updated to prefer `streamable-http` over legacy `http-sse`

### Documentation
- Added `docs/getting-started-guide.md` - Non-technical user guide for farmers/breeders
- Added `docs/mcp-configurations.md` - Comprehensive MCP config examples (uvx, Docker, transports)
- Updated `llms.txt` with complete MCP tools, resources, prompts, and Shepherd agent reference
- Updated CLAUDE.md, README.md, and mcp-server.md with correct tool counts
- Fixed Python version requirements in CONTRIBUTING.md (3.10+) and RELEASE.md (3.10-3.13)

## [nsip-skills 1.3.0] - 2025-12-06

### Added

#### NSIP Skills Package - Initial Release
Breeding decision support tools for sheep genetics using NSIP data.

- **10 Analysis Modules**:
  1. `flock_import` - Import and enrich flock data from spreadsheets with NSIP breeding values
  2. `ebv_analysis` - Compare and rank animals by EBV traits
  3. `inbreeding` - Calculate pedigree-based inbreeding coefficients
  4. `mating_optimizer` - Recommend optimal ram-ewe pairings
  5. `progeny_analysis` - Evaluate sires by offspring performance
  6. `trait_planner` - Design multi-generation improvement strategies
  7. `ancestry_builder` - Generate pedigree reports and visualizations
  8. `flock_stats` - Calculate aggregate flock statistics
  9. `selection_index` - Build and apply custom breeding indexes
  10. `recommendation_engine` - AI-powered breeding recommendations

- **9 CLI Entry Points**:
  - `nsip-ebv-analysis` - Compare and analyze EBV traits
  - `nsip-flock-import` - Import flock data from spreadsheets
  - `nsip-flock-stats` - Generate flock statistics
  - `nsip-inbreeding` - Calculate inbreeding coefficients
  - `nsip-mating-optimizer` - Generate mating recommendations
  - `nsip-progeny-analysis` - Analyze progeny performance
  - `nsip-trait-planner` - Plan trait improvement strategies
  - `nsip-ancestry` - Build ancestry/pedigree reports
  - `nsip-selection-index` - Calculate selection indexes

- **Common Utilities**:
  - `CachedNSIPClient` - Wrapper with caching for NSIP API calls
  - Data models: `AnimalAnalysis`, `FlockSummary`, `InbreedingResult`, `MatingPair`, `PedigreeTree`, `TraitProfile`

- **Optional Dependencies**:
  - `gsheets` extra for Google Sheets integration via `gspread`

### Dependencies
- `nsip-client>=1.3.0,<2.0.0` (core API client)
- `pandas>=2.0.0` (data manipulation)
- `numpy>=1.24.0` (numerical operations)
- `openpyxl>=3.1.0` (Excel file support)

### Installation
```bash
# Basic installation
pip install nsip-skills

# With Google Sheets support
pip install nsip-skills[gsheets]
```

## [1.2.0] - 2025-10-13

### Changed
- **BREAKING**: MCP tools no longer automatically summarize responses
  - Summarization is now opt-in via explicit `summarize=True` parameter
  - Default behavior: ALL data preserved (zero data loss)
  - Affected tools: `nsip_search_animals`, `nsip_get_animal`, `nsip_get_lineage`, `nsip_get_progeny`, `nsip_search_by_lpn`

### Added
- Opt-in `summarize` parameter to 5 MCP tools for explicit control over data reduction
- Enhanced data format handling in `summarize_response()`:
  - Support for both string and dict formats for sire/dam fields
  - Trait normalization for dataclass serialization format
  - Automatic accuracy percentage (0-100) to decimal (0-1) conversion
  - Improved contact_info handling with None filtering

### Fixed
- Data loss issue where responses were automatically summarized without user consent
- Format mismatch when handling sire/dam fields in different data structures
- Trait accuracy conversion between percentage and decimal formats
- Empty field issues in summarized responses

### Improved
- User control: Explicit opt-in ensures predictable behavior
- Transparency: `_summarized` metadata always indicates summarization status
- Backward compatibility: Optional parameter doesn't break existing code
- Test coverage: 290 tests passing, 91.94% coverage maintained

## [1.2.1] - 2025-10-14

### Fixed
- **API Response Format Compatibility**: Fixed `get_available_breed_groups()` to handle new NSIP API response format
  - Now supports wrapped response format: `{"success": true, "data": [...]}`
  - Added support for multiple field name variations: `breedGroupId/Id/id` and `breedGroupName/Name/name`
  - Maintains backward compatibility with legacy direct list format
  - Resolves `'str' object has no attribute 'get'` error in `/nsip:discover` MCP command
- **Search Request Headers**: Fixed `search_animals()` to always send `Content-Type: application/json` header
  - API requires JSON content type even with empty request body
  - Changed to always send `json={}` instead of `json=None`
  - Fixes 415 "Unsupported Media Type" errors
  - Fixes 400 "Bad Request" errors when searching without criteria
- **Search Response Parsing**: Enhanced `SearchResults.from_api_response()` to support both field naming conventions
  - Supports camelCase: `recordCount`, `records`, `page`, `pageSize`
  - Supports PascalCase: `TotalCount`, `Results`, `Page`, `PageSize`
  - Resolves 0 results returned when searching (now returns all 145,595+ animals for Katahdin breed)
- **MCP Tool Response Format**: Fixed FastMCP serialization bug in `nsip_list_breeds()` and `nsip_get_statuses()`
  - Wrapped list returns in dict structure due to FastMCP Issue #1969
  - Return format: `{"success": True, "data": [...]}`
  - Prevents MCP client-side deserialization errors

### Changed
- Enhanced API response format flexibility across all endpoints
- Improved error handling for HTTP content negotiation
- Updated all unit and integration tests for new response formats (295 tests passing)

### Technical Details
- **Root Cause**: NSIP API changed response format without versioning
  - Previous: Direct list `[...]` with PascalCase fields
  - Current: Wrapped response `{"success": true, "data": [...]}` with camelCase fields
- **Testing**: Verified against live NSIP API using curl
- **Coverage**: Maintained 92.28% test coverage
- **Quality Gates**: All 6 mandatory gates passing (Black, isort, flake8, mypy, pytest, package build)

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
