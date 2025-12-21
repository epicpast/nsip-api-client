# GitHub Copilot Instructions for NSIP API Client

> Also see `CLAUDE.md` in the repository root for comprehensive documentation.

## Project Overview

Python monorepo containing:
- **nsip-client**: Pure API client for NSIP (National Sheep Improvement Program) Search API
- **nsip-mcp-server**: MCP server layer for LLM integrations (FastMCP 2.12.4+)
- **nsip-skills**: Breeding decision support tools (pandas-based analysis)

**Python version**: 3.10+
**Package manager**: uv (preferred) or pip
**Build backend**: Hatchling

## Architecture

```
src/
├── nsip_client/    # Pure API client (no MCP dependencies)
├── nsip_mcp/       # MCP server layer (depends on nsip_client)
└── nsip_skills/    # Analysis tools (depends on nsip_client + pandas)
```

Dependency hierarchy: `nsip_skills` and `nsip_mcp` both depend on `nsip_client`.

## Code Style Guidelines

- **Line length**: 100 characters
- **Imports**: isort with black profile
- **Type hints**: Required for all public functions
- **Test coverage**: 95% minimum required (CI enforced)
- **Formatter**: `uv run ruff format`
- **Linter**: `uv run ruff check`

## Development Commands

```bash
# Install dependencies
uv sync --all-extras --group dev

# Format and lint
uv run ruff format src tests
uv run ruff check src tests --fix

# Type check
uv run mypy src

# Run tests with coverage
uv run pytest --cov-fail-under=95 -v

# Build packages
uv build
```

## Testing Patterns

### Testing MCP Resources (async functions with FastMCP decorators)

```python
import asyncio
from unittest.mock import MagicMock, patch

def test_resource_api_error(self) -> None:
    with patch("nsip_mcp.resources.animal_resources.get_nsip_client") as mock_get:
        mock_client = MagicMock()
        mock_client.get_animal_details.side_effect = NSIPAPIError("API error")
        mock_get.return_value = mock_client

        from nsip_mcp.resources.animal_resources import get_animal_details_resource
        # Use .fn to call underlying function, not the FunctionTool wrapper
        result = asyncio.run(get_animal_details_resource.fn(lpn_id="6332-12345"))
        assert "error" in result
```

### Skills Mock Classes

```python
from tests.nsip_skills_helpers import MockNSIPClient, MockAnimalDetails

mock_client = MockNSIPClient(
    animals={lpn_id: MockAnimalDetails.create_sample(lpn_id, sire="...", dam="...")}
)
```

## Key Algorithms

**Inbreeding (Wright's Path Coefficient)**:
```
F = sum[(1/2)^(n1+n2+1) * (1 + FA)]
```

**Genetic Gain**:
```
R = h^2 * i * sigma_p
```

## Common Pitfalls

1. **Coverage threshold**: CI requires 95%, not 80%
2. **FastMCP decorated functions**: Use `.fn` to call underlying function
3. **NSIP API inconsistencies**: Check `models.py` for `from_api_response()` patterns
4. **Summarization**: Never automatic; explicitly pass `summarize=True`
5. **CHANGELOG location**: `docs/CHANGELOG.md`, not repository root

## Package Structure

Each package in `packaging/` is independently publishable:
- `packaging/nsip-client/pyproject.toml`
- `packaging/nsip-mcp-server/pyproject.toml`
- `packaging/nsip-skills/pyproject.toml`

Versions are in `src/{package}/__init__.py` and read dynamically by hatch.

## Exception Hierarchy (nsip_client)

```
NSIPError
├── NSIPAPIError (status_code, response)
│   └── NSIPNotFoundError (search_string, always 404)
├── NSIPConnectionError
├── NSIPTimeoutError
└── NSIPValidationError
```

## MCP Tools Reference

**NSIP API Tools (10)**: `nsip_get_last_update`, `nsip_list_breeds`, `nsip_get_statuses`, `nsip_get_trait_ranges`, `nsip_search_animals`, `nsip_get_animal`, `nsip_get_lineage`, `nsip_get_progeny`, `nsip_search_by_lpn`, `get_server_health`

**Shepherd Tools (5)**: `shepherd_consult`, `shepherd_breeding`, `shepherd_health`, `shepherd_calendar`, `shepherd_economics`

## Additional Documentation

- `CLAUDE.md` - Comprehensive project documentation
- `llms.txt` - LLM-optimized reference documentation
- `docs/nsip-skills.md` - Detailed skills guide
- `docs/CHANGELOG.md` - Version history
