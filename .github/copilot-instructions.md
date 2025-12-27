# GitHub Copilot Instructions for NSIP API Client

> Also see `CLAUDE.md` in the repository root for comprehensive documentation.

## Project Overview

Python monorepo containing:
- **nsip-client**: Pure API client for NSIP (National Sheep Improvement Program) Search API
- **nsip-mcp-server**: MCP server layer for LLM integrations (FastMCP 2.12.4+)
- **nsip-skills**: Breeding decision support tools (pandas-based analysis)

**Python version**: 3.12+
**Package manager**: uv
**Build backend**: Hatchling
**Linting/Formatting**: ruff
**Type Checking**: pyright (strict mode)
**Testing**: pytest with 95% coverage requirement

## Architecture

```
src/
├── nsip_client/    # Pure API client (no MCP dependencies)
├── nsip_mcp/       # MCP server layer (depends on nsip_client)
└── nsip_skills/    # Analysis tools (depends on nsip_client + pandas)
```

Dependency hierarchy: `nsip_skills` and `nsip_mcp` both depend on `nsip_client`.

## Code Generation Guidelines

### Type Annotations

Always include type annotations for function parameters and return types:

```python
def process_data(items: list[str], limit: int = 10) -> dict[str, int]:
    ...
```

Use `from __future__ import annotations` for forward references.

### Docstrings

Use Google-style docstrings:

```python
def example_function(param1: str, param2: int) -> bool:
    """Short description of the function.

    Longer description if needed, explaining the purpose
    and any important details.

    Args:
        param1: Description of param1.
        param2: Description of param2.

    Returns:
        Description of the return value.

    Raises:
        ValueError: When validation fails.
    """
```

### Imports

Organize imports in this order:
1. Future imports (`from __future__ import annotations`)
2. Standard library
3. Third-party packages
4. Local imports

Use `TYPE_CHECKING` block for type-only imports:

```python
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence
```

### Error Handling

Use descriptive error messages assigned to variables:

```python
# Good
msg = f"Invalid value: {value}"
raise ValueError(msg)

# Avoid
raise ValueError(f"Invalid value: {value}")
```

### Data Classes

Prefer dataclasses for data structures:

```python
from dataclasses import dataclass, field

@dataclass(frozen=True)
class Config:
    """Configuration settings."""

    name: str
    timeout: int = 30
    tags: list[str] = field(default_factory=list)
```

### Async Code

Use async/await for I/O operations:

```python
async def fetch_data(url: str) -> dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()
```

## Development Commands

```bash
# Install dependencies
uv sync --all-extras

# Format and lint
uv run ruff format .
uv run ruff check . --fix

# Type check
uv run pyright

# Run tests with coverage
uv run pytest --cov-fail-under=95 -v
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

### Parametrized Tests

```python
import pytest

@pytest.mark.parametrize("input_val,expected", [
    ("a", 1),
    ("b", 2),
])
def test_parametrized(input_val: str, expected: int):
    assert process(input_val) == expected
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

## File Locations

- Source code: `src/nsip_client/`, `src/nsip_mcp/`, `src/nsip_skills/`
- Unit tests: `tests/unit/`
- Integration tests: `tests/integration/`
- Shared fixtures: `tests/conftest.py`

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
