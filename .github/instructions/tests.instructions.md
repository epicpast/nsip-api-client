---
applyTo: "**/test_*.py,**/tests/**/*.py"
---

# Testing Guidelines

## Coverage Requirements
- Minimum 95% test coverage required (enforced by CI)
- All new code must include tests
- Use `pytest --cov-fail-under=95` to verify locally

## Test Structure
- Place tests in `tests/unit/` for isolated unit tests
- Place tests in `tests/integration/` for end-to-end tests
- Use markers: `@pytest.mark.integration`, `@pytest.mark.slow`

## Mocking Patterns

### API Client Mocking
```python
from tests.nsip_skills_helpers import MockNSIPClient, MockAnimalDetails

mock_client = MockNSIPClient(
    animals={lpn_id: MockAnimalDetails.create_sample(lpn_id, sire="...", dam="...")}
)
```

### MCP Resource Testing (async functions)
```python
import asyncio
from unittest.mock import MagicMock, patch

def test_resource_function(self) -> None:
    with patch("nsip_mcp.resources.animal_resources.get_nsip_client") as mock_get:
        mock_client = MagicMock()
        mock_client.get_animal_details.return_value = {...}
        mock_get.return_value = mock_client

        from nsip_mcp.resources.animal_resources import get_animal_details_resource
        # Use .fn to call underlying function, not FunctionTool wrapper
        result = asyncio.run(get_animal_details_resource.fn(lpn_id="6332-12345"))
        assert result is not None
```

## Fixtures
- Use shared fixtures from `tests/conftest.py`
- Key fixtures: `sample_lpn_id`, `sample_breed_id`
- Skills fixtures in `tests/unit/nsip_skills/conftest.py`: `mock_animals`, `mock_client`

## Naming Conventions
- Test files: `test_<module>.py`
- Test classes: `Test<ClassName>`
- Test methods: `test_<behavior>_<condition>` (e.g., `test_get_animal_returns_none_when_not_found`)

## Assertions
- Use plain `assert` statements (pytest style)
- Be specific about expected values
- Test both success and error paths
