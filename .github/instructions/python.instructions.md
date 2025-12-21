---
applyTo: "**/*.py"
---

# Python Code Guidelines

## Type Hints
- Required for all public functions and methods
- Use `Optional[T]` for nullable parameters
- Use `list[T]` and `dict[K, V]` (Python 3.10+ style, not `List` or `Dict`)
- Return type hints required for all public functions

## Docstrings
- Use Google-style docstrings for public functions
- Include Args, Returns, and Raises sections where applicable

## Error Handling
- Use project-specific exceptions from `nsip_client.exceptions`
- Never catch bare `Exception` without re-raising or logging
- Always provide meaningful error messages

## Imports
- Group imports: stdlib, third-party, local (isort handles this)
- Prefer absolute imports over relative imports
- Import specific items, not entire modules when practical

## Code Style
- Line length: 100 characters maximum
- Use `ruff format` for formatting (black-compatible)
- Use `ruff check` for linting
- No unused imports or variables

## Async Patterns
- MCP resources and tools are async functions
- Use `asyncio.run()` in tests to call async functions
- For FastMCP decorated functions, use `.fn` to access the underlying function

## Data Classes
- Use `@dataclass` for simple data containers
- Include `from_api_response()` class methods for API response parsing
- Handle NSIP API field name variations (see models.py patterns)
