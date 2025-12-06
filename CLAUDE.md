# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python client, MCP server, and breeding decision support tools for the NSIP (National Sheep Improvement Program) Search API. Provides programmatic access to sheep breeding data including genetic traits (EBVs), pedigree/lineage, and progeny records.

**Key Technologies:** Python 3.10+, FastMCP 2.12.4+, pytest, tiktoken, pandas

## Architecture

```
src/
├── nsip_client/          # Pure API client (no MCP dependencies)
│   ├── client.py         # NSIPClient - HTTP wrapper for nsipsearch.nsip.org/api
│   ├── models.py         # Dataclasses: AnimalDetails, Lineage, Progeny, etc.
│   ├── exceptions.py     # NSIPAPIError, NSIPNotFoundError, NSIPTimeoutError
│   └── cli.py            # nsip-search CLI entrypoint
│
├── nsip_mcp/             # MCP server layer (depends on nsip_client)
│   ├── server.py         # FastMCP server setup, transport configuration
│   ├── mcp_tools.py      # @mcp.tool() decorated functions (main tool definitions)
│   ├── tools.py          # Lower-level tool utilities and helpers
│   ├── context.py        # Token counting (tiktoken), response summarization
│   ├── cache.py          # TtlCache - 1hr TTL, 1000 entry max, FIFO eviction
│   ├── transport.py      # stdio/streamable-http/websocket transport config
│   ├── metrics.py        # Server health metrics (SC-001 through SC-007)
│   ├── errors.py         # JSON-RPC 2.0 error codes and LLM-friendly messages
│   └── cli.py            # nsip-mcp-server CLI entrypoint
│
└── nsip_skills/          # Breeding decision support tools (depends on nsip_client)
    ├── common/           # Shared utilities (data_models, formatters, nsip_wrapper)
    ├── flock_import.py   # Import/enrich flock data from spreadsheets
    ├── ebv_analysis.py   # Compare EBVs across animals
    ├── inbreeding.py     # Calculate inbreeding coefficients
    ├── mating_optimizer.py    # Optimize ram-ewe pairings
    ├── progeny_analysis.py    # Evaluate sires by offspring
    ├── trait_planner.py       # Multi-generation selection planning
    ├── ancestry_builder.py    # Pedigree tree generation
    ├── flock_stats.py         # Aggregate flock statistics
    ├── selection_index.py     # Custom breeding indexes
    └── recommendation_engine.py  # AI-powered recommendations
```

### Package Dependency Hierarchy

```
nsip_skills ──┐
              ├──► nsip_client ──► NSIP API (nsipsearch.nsip.org/api)
nsip_mcp ─────┘
```

- **nsip_client** - Standalone, no MCP or pandas dependencies
- **nsip_mcp** - MCP server layer, uses nsip_client
- **nsip_skills** - Analysis tools, uses nsip_client + pandas

### Data Flow

```
MCP Client → mcp_tools.py → cache.py → client.py → NSIP API
                 ↓
            context.py (token management, optional summarization)
```

### Key Design Decisions

1. **nsip_client is standalone** - No MCP dependencies, can be used as a pure Python API client
2. **Summarization is opt-in** - All MCP tools preserve full data by default; pass `summarize=True` to reduce tokens
3. **Context threshold** - Responses >2000 tokens get metadata tags; summarization targets 70% reduction
4. **Cache key format** - `method_name:sorted_json_params` ensures deterministic keys

## Development Setup

```bash
# Option 1: Using uv (preferred)
uv sync --all-extras
uv run pytest

# Option 2: Traditional venv
make init-dev                        # Creates venv/
source venv/bin/activate             # Linux/Mac
make install-dev                     # pip install -e ".[dev]"
```

## Commands

### Quality Gates (MUST pass before commit)

```bash
# Run complete quality suite (recommended)
./run_tests_and_coverage.sh
# OR
make ci-local

# Individual checks
black src/ tests/ examples/          # Format
isort src/ tests/ examples/          # Sort imports
flake8 src/ tests/                   # Lint (PRIMARY GATE)
mypy src/ --ignore-missing-imports   # Type check
pytest --cov-fail-under=95 -v        # Tests (95% coverage required)
```

### Quick Fixes

```bash
make format     # Auto-fix black + isort
make quality    # Format then run all checks
```

### Running a Single Test

```bash
pytest tests/unit/test_cache.py -v
pytest tests/unit/test_cache.py::TestTtlCache::test_get_returns_cached_value -v
pytest -k "test_cache" -v  # By name pattern

# With uv
uv run pytest tests/unit/test_cache.py -v
```

### MCP Server

```bash
# stdio (default, for Claude Desktop)
nsip-mcp-server

# HTTP (for web apps)
MCP_TRANSPORT=streamable-http MCP_PORT=8000 nsip-mcp-server

# WebSocket
MCP_TRANSPORT=websocket MCP_PORT=9000 nsip-mcp-server
```

### NSIP Skills (Breeding Tools)

```bash
# Run as Python modules
uv run python -m nsip_skills.ebv_analysis LPN_ID1 LPN_ID2
uv run python -m nsip_skills.inbreeding --mating RAM_LPN,EWE_LPN
uv run python -m nsip_skills.flock_stats my_flock.csv --name "My Flock"

# Or via Claude Code slash commands
/nsip:ebv-analyzer LPN_ID1 LPN_ID2
/nsip:inbreeding --mating RAM_LPN,EWE_LPN
/nsip:flock-dashboard my_flock.csv
```

## Code Style

- **Line length:** 100 chars (black + flake8)
- **Imports:** isort with black profile
- **Type hints:** Required for public functions
- **Test coverage:** 95% required

## Release Process

1. Update `version` in `pyproject.toml`
2. Update `docs/CHANGELOG.md` (NOT root level)
3. Run `./run_tests_and_coverage.sh`
4. Commit, tag (`git tag -a vX.Y.Z`), push with tags
5. Create GitHub release referencing `docs/CHANGELOG.md`

## Test Structure

```
tests/
├── unit/           # Fast, isolated tests (mock API calls)
├── integration/    # End-to-end workflow tests
├── benchmarks/     # Performance tests
├── conftest.py     # Shared fixtures
└── test_*.py       # Client/model tests
```

Markers: `@pytest.mark.integration`, `@pytest.mark.slow`

## MCP Tools Reference

| Tool | Description | Caching | Summarization |
|------|-------------|---------|---------------|
| `nsip_get_last_update` | Database timestamp | ✓ | N/A |
| `nsip_list_breeds` | Breed groups (61=Range, 62=Maternal Wool, 64=Hair, 69=Terminal) | ✓ | N/A |
| `nsip_get_statuses` | Animal statuses | ✓ | N/A |
| `nsip_get_trait_ranges` | Min/max trait values by breed | ✓ | N/A |
| `nsip_search_animals` | Paginated animal search | ✓ | Optional |
| `nsip_get_animal` | Single animal details | ✓ | Optional |
| `nsip_get_lineage` | Pedigree tree | ✓ | Optional |
| `nsip_get_progeny` | Offspring list | ✓ | Optional |
| `nsip_search_by_lpn` | Complete profile (details+lineage+progeny) | ✓ | Optional |
| `get_server_health` | Metrics dashboard | No | N/A |

## NSIP Skills Reference (Claude Code Slash Commands)

| Command | Module | Purpose |
|---------|--------|---------|
| `/nsip:flock-import` | flock_import | Import spreadsheet data, enrich with NSIP EBVs |
| `/nsip:ebv-analyzer` | ebv_analysis | Compare EBVs across animals |
| `/nsip:inbreeding` | inbreeding | Calculate pedigree-based inbreeding coefficients |
| `/nsip:mating-plan` | mating_optimizer | Optimize ram-ewe pairings |
| `/nsip:progeny-report` | progeny_analysis | Evaluate sires by offspring performance |
| `/nsip:trait-improvement` | trait_planner | Multi-generation selection planning |
| `/nsip:ancestry` | ancestry_builder | Generate pedigree trees |
| `/nsip:flock-dashboard` | flock_stats | Aggregate flock statistics |
| `/nsip:selection-index` | selection_index | Calculate custom breeding indexes |
| `/nsip:breeding-recs` | recommendation_engine | AI-powered recommendations |

Detailed documentation: `docs/nsip-skills.md`

## Common Pitfalls

1. **Don't skip quality gates** - CI will reject PRs that fail `flake8 src/ tests/`
2. **CHANGELOG location** - `docs/CHANGELOG.md`, not repository root
3. **Cache key order** - Parameters must be JSON-serializable; sorted automatically
4. **Summarization** - Never automatic; explicitly pass `summarize=True` when needed
5. **Coverage threshold** - CI requires 95%, not 80%

## NSIP API Quirks

The upstream NSIP API has inconsistent response formats. Key quirks to handle:

1. **Wrapped vs direct responses** - Some endpoints return `{"success": true, "data": [...]}`, others return the list directly
2. **Field name variations** - Same fields may appear as `breedGroupId/Id/id` or `recordCount/RecordCount`
3. **Content-Type required** - `search_animals` requires `Content-Type: application/json` even with empty body
4. **Trait accuracy formats** - API returns 0-100 percentages; summarization converts to 0-1 decimals

When adding API handling, check `models.py` for `from_api_response()` patterns that handle these variations.
