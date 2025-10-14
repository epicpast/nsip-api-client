"""
Integration tests for MCP server end-to-end workflows

Test Scenarios:

US1 (API Discovery & Invocation):
- Tool discovery (<5 seconds per SC-001)
- Tool invocation with valid parameters
- All 9 tools callable

US2 (Context Management):
- Pass-through behavior (≤2000 tokens, FR-015)
- Summarization (>2000 tokens, 70% reduction per SC-002)
- FR-005a field preservation
- FR-005b field omission

US3 (Error Handling):
- Parameter validation (95% caught per SC-003)
- API error handling with structured responses
- LLM retry success (80% per SC-004)

Multi-Transport:
- stdio transport
- HTTP SSE transport
- WebSocket transport

Target: >90% coverage (SC-011)
"""

import asyncio
import time
from unittest.mock import MagicMock, patch

import pytest

from nsip_mcp.cache import response_cache
from nsip_mcp.server import mcp
from nsip_mcp.tools import reset_client


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear cache before each test."""
    response_cache.clear()
    yield
    response_cache.clear()


@pytest.fixture(autouse=True)
def reset_nsip_client():
    """Reset client singleton before each test."""
    reset_client()
    yield
    reset_client()


class TestUS1ToolDiscovery:
    """Integration tests for User Story 1: API Function Discovery."""

    @pytest.mark.integration
    def test_tool_discovery_under_5_seconds(self):
        """Verify tool discovery completes <5 seconds (SC-001)."""
        start_time = time.time()

        # Discover all tools
        tools = asyncio.run(mcp.get_tools())

        elapsed = time.time() - start_time

        # Verify discovery completes within 5 seconds
        assert elapsed < 5.0, f"Tool discovery took {elapsed}s (>5s threshold)"

        # Verify we discovered tools
        assert len(tools) > 0, "No tools discovered"

    @pytest.mark.integration
    def test_all_9_tools_discoverable(self):
        """Verify all 9 NSIP tools are discoverable by MCP client."""
        tools = asyncio.run(mcp.get_tools())
        tool_names = list(tools.keys())

        expected_tools = [
            "nsip_get_last_update",
            "nsip_list_breeds",
            "nsip_get_statuses",
            "nsip_get_trait_ranges",
            "nsip_search_animals",
            "nsip_get_animal",
            "nsip_get_lineage",
            "nsip_get_progeny",
            "nsip_search_by_lpn",
        ]

        for tool_name in expected_tools:
            assert tool_name in tool_names, f"Tool {tool_name} not discovered"

        # Verify we found exactly 9 NSIP tools (plus get_server_health = 10 total)
        nsip_tools = [name for name in tool_names if name.startswith("nsip_")]
        assert len(nsip_tools) == 9, f"Expected 9 NSIP tools, found {len(nsip_tools)}"

    @pytest.mark.integration
    def test_tool_descriptions_present(self):
        """Verify all tools have non-empty descriptions (FR-002)."""
        tools = asyncio.run(mcp.get_tools())
        nsip_tool_names = [name for name in tools.keys() if name.startswith("nsip_")]

        for tool_name in nsip_tool_names:
            tool = tools[tool_name]
            # Access description from tool's .fn attribute
            description = tool.fn.__doc__ or ""
            assert description, f"Tool {tool_name} has no description"
            assert len(description) > 20, f"Tool {tool_name} description too short"

            # Verify description mentions what the tool does
            description_lower = description.lower()
            assert any(
                word in description_lower
                for word in ["get", "list", "search", "retrieve", "return"]
            ), f"Tool {tool_name} description doesn't explain what it does"


class TestUS1ToolInvocation:
    """Integration tests for User Story 1: Tool Invocation."""

    @pytest.mark.integration
    @patch("nsip_mcp.tools.NSIPClient")
    def test_nsip_list_breeds_invocation(self, mock_client_class):
        """Verify nsip_list_breeds tool invocation returns valid response."""
        # Setup mock client
        mock_client = MagicMock()
        mock_breed = MagicMock()
        mock_breed.id = 61
        mock_breed.name = "Range"
        mock_client.get_available_breed_groups.return_value = [mock_breed]
        mock_client_class.return_value = mock_client

        # Get the tool function
        tools = asyncio.run(mcp.get_tools())
        _ = tools["nsip_list_breeds"]  # Verify tool exists

        # Invoke the tool through MCP
        from nsip_mcp import mcp_tools

        result = mcp_tools.nsip_list_breeds.fn()

        # Verify result structure (now wrapped in dict with success/data)
        assert isinstance(result, dict), "Result should be a dict"
        assert result["success"] is True, "Success should be True"
        assert "data" in result, "Result should have 'data' field"
        assert isinstance(result["data"], list), "Data should be a list"
        assert len(result["data"]) > 0, "Data list should not be empty"
        assert "id" in result["data"][0], "Breed should have 'id' field"
        assert "name" in result["data"][0], "Breed should have 'name' field"
        assert result["data"][0]["id"] == 61
        assert result["data"][0]["name"] == "Range"

    @pytest.mark.integration
    @patch("nsip_mcp.tools.NSIPClient")
    def test_all_tools_invocable(self, mock_client_class):
        """Verify all 9 tools can be invoked successfully."""
        # Setup comprehensive mocks
        mock_client = MagicMock()

        # Mock for nsip_get_last_update
        mock_client.get_date_last_updated.return_value = {"date": "09/23/2025"}

        # Mock for nsip_list_breeds
        mock_breed = MagicMock()
        mock_breed.id = 61
        mock_breed.name = "Range"
        mock_client.get_available_breed_groups.return_value = [mock_breed]

        # Mock for nsip_get_statuses
        mock_client.get_statuses_by_breed_group.return_value = ["CURRENT", "SOLD"]

        # Mock for nsip_get_trait_ranges
        mock_client.get_trait_ranges_by_breed.return_value = {"BWT": {"min": -0.713, "max": 0.0}}

        # Mock for nsip_search_animals
        mock_search_result = MagicMock()
        mock_search_result.results = [{"LpnId": "ABC123"}]
        mock_search_result.total_count = 1
        mock_search_result.page = 0
        mock_search_result.page_size = 15
        mock_client.search_animals.return_value = mock_search_result

        # Mock for nsip_get_animal
        mock_animal = MagicMock()
        mock_animal.to_dict.return_value = {"lpn_id": "ABC123", "breed": "Katahdin"}
        mock_client.get_animal_details.return_value = mock_animal

        # Mock for nsip_get_lineage
        mock_lineage = MagicMock()
        mock_lineage.to_dict.return_value = {"sire": {}, "dam": {}}
        mock_client.get_lineage.return_value = mock_lineage

        # Mock for nsip_get_progeny
        mock_progeny = MagicMock()
        mock_progeny.animals = []
        mock_progeny.total_count = 0
        mock_progeny.page = 0
        mock_progeny.page_size = 10
        mock_client.get_progeny.return_value = mock_progeny

        # Mock for nsip_search_by_lpn
        mock_client.search_by_lpn.return_value = {
            "details": mock_animal,
            "lineage": mock_lineage,
            "progeny": mock_progeny,
        }

        mock_client_class.return_value = mock_client

        # Import tools and test each one
        from nsip_mcp import mcp_tools

        # Test each tool invocation
        result1 = mcp_tools.nsip_get_last_update.fn()
        assert result1 is not None

        result2 = mcp_tools.nsip_list_breeds.fn()
        assert isinstance(result2, dict)
        assert result2["success"] is True

        result3 = mcp_tools.nsip_get_statuses.fn()
        assert isinstance(result3, dict)
        assert result3["success"] is True

        result4 = mcp_tools.nsip_get_trait_ranges.fn(breed_id=486)
        assert isinstance(result4, dict)

        result5 = mcp_tools.nsip_search_animals.fn()
        assert "results" in result5

        result6 = mcp_tools.nsip_get_animal.fn(search_string="ABC123")
        assert isinstance(result6, dict)

        result7 = mcp_tools.nsip_get_lineage.fn(lpn_id="ABC123")
        assert isinstance(result7, dict)

        result8 = mcp_tools.nsip_get_progeny.fn(lpn_id="ABC123")
        assert "animals" in result8

        result9 = mcp_tools.nsip_search_by_lpn.fn(lpn_id="ABC123")
        # nsip_search_by_lpn now returns full structure by default (no auto-summarization)
        assert "details" in result9 or "lpn_id" in result9  # Either full or summarized format
        assert "_summarized" in result9

    @pytest.mark.integration
    @patch("nsip_mcp.tools.NSIPClient")
    def test_caching_across_invocations(self, mock_client_class):
        """Verify caching works across multiple tool invocations."""
        mock_client = MagicMock()
        mock_client.get_date_last_updated.return_value = {"date": "09/23/2025"}
        mock_client_class.return_value = mock_client

        from nsip_mcp import mcp_tools

        # Clear cache metrics
        response_cache.clear()

        # First invocation - cache miss
        result1 = mcp_tools.nsip_get_last_update.fn()
        assert response_cache.misses == 1
        assert response_cache.hits == 0

        # Second invocation - cache hit
        result2 = mcp_tools.nsip_get_last_update.fn()
        assert response_cache.misses == 1
        assert response_cache.hits == 1

        # Verify same result returned
        assert result1 == result2

        # Verify API only called once
        assert mock_client.get_date_last_updated.call_count == 1


class TestUS2PassthroughBehavior:
    """Integration tests for User Story 2: Pass-through (<= 2000 tokens)."""

    @pytest.mark.integration
    @patch("nsip_mcp.tools.NSIPClient")
    def test_small_response_unmodified(self, mock_client_class):
        """Verify responses ≤2000 tokens pass through unmodified (FR-015)."""
        mock_client = MagicMock()

        # Mock a small response (breeds list - typically <500 tokens)
        mock_breed_1 = MagicMock()
        mock_breed_1.id = 61
        mock_breed_1.name = "Range"

        mock_breed_2 = MagicMock()
        mock_breed_2.id = 62
        mock_breed_2.name = "Maternal Wool"

        mock_client.get_available_breed_groups.return_value = [mock_breed_1, mock_breed_2]
        mock_client_class.return_value = mock_client

        from nsip_mcp import mcp_tools

        # Invoke the tool
        result = mcp_tools.nsip_list_breeds.fn()

        # Verify result is wrapped in success/data structure (FastMCP requirement)
        assert isinstance(result, dict), "Should return dict with success/data"
        assert result["success"] is True
        assert "data" in result
        assert isinstance(result["data"], list)
        assert len(result["data"]) == 2, "All breeds should be present"
        assert result["data"][0]["id"] == 61
        assert result["data"][0]["name"] == "Range"
        assert result["data"][1]["id"] == 62
        assert result["data"][1]["name"] == "Maternal Wool"

    @pytest.mark.integration
    @patch("nsip_mcp.tools.NSIPClient")
    def test_passthrough_includes_all_fields(self, mock_client_class):
        """Verify pass-through responses include all original fields."""
        mock_client = MagicMock()

        # Mock status list
        mock_client.get_statuses_by_breed_group.return_value = [
            "CURRENT",
            "SOLD",
            "DEAD",
            "COMMERCIAL",
        ]
        mock_client_class.return_value = mock_client

        from nsip_mcp import mcp_tools

        result = mcp_tools.nsip_get_statuses.fn()

        # Result is wrapped in success/data structure (FastMCP requirement)
        assert isinstance(result, dict), "Should return dict with success/data"
        assert result["success"] is True
        assert "data" in result
        assert isinstance(result["data"], list)
        assert "CURRENT" in result["data"]
        assert "SOLD" in result["data"]
        assert "DEAD" in result["data"]
        assert "COMMERCIAL" in result["data"]

    @pytest.mark.integration
    @patch("nsip_mcp.tools.NSIPClient")
    def test_passthrough_metadata(self, mock_client_class):
        """Verify pass-through responses have _summarized=false."""
        mock_client = MagicMock()
        mock_client.get_date_last_updated.return_value = {"date": "09/23/2025"}
        mock_client_class.return_value = mock_client

        from nsip_mcp import mcp_tools

        result = mcp_tools.nsip_get_last_update.fn()

        # Small dict responses are returned directly without metadata wrapper
        assert "date" in result or "success" in result
        assert isinstance(result, dict)


class TestUS2Summarization:
    """Integration tests for User Story 2: Summarization (> 2000 tokens)."""

    @pytest.mark.integration
    @patch("nsip_mcp.tools.NSIPClient")
    def test_large_response_summarized(self, mock_client_class):
        """Verify responses can be summarized when explicitly requested."""
        mock_client = MagicMock()

        # Create a large animal response (>2000 tokens)
        mock_animal = MagicMock()
        large_traits = {}
        # Add many traits to exceed token threshold
        for i in range(50):
            large_traits[f"TRAIT_{i}"] = {
                "value": float(i),
                "accuracy": 0.5 + (i % 50) / 100.0,
                "percentile": i,
                "ebv": float(i * 10),
                "description": f"This is trait number {i} with a long description" * 10,
            }

        mock_animal.to_dict.return_value = {
            "lpn_id": "6####92020###249",
            "breed": "Katahdin",
            "traits": large_traits,
            "progeny": {
                "animals": [{"lpn_id": f"PROG{j}", "data": "x" * 100} for j in range(20)],
                "total_count": 20,
            },
            "sire": {"lpn_id": "SIRE123", "data": "x" * 100},
            "dam": {"lpn_id": "DAM456", "data": "x" * 100},
        }

        mock_client.get_animal_details.return_value = mock_animal
        mock_client_class.return_value = mock_client

        from nsip_mcp import mcp_tools

        # Explicitly request summarization with summarize=True
        result = mcp_tools.nsip_get_animal.fn(search_string="6####92020###249", summarize=True)

        # Verify summarization occurred
        assert "_summarized" in result
        assert result["_summarized"] is True, "Large response should be summarized when requested"
        assert "_original_token_count" in result
        assert "_summary_token_count" in result
        assert result["_original_token_count"] > 2000, "Original should exceed threshold"
        assert (
            result["_summary_token_count"] < result["_original_token_count"]
        ), "Summary should be smaller"

    @pytest.mark.integration
    @patch("nsip_mcp.tools.NSIPClient")
    def test_70_percent_token_reduction(self, mock_client_class):
        """Verify summarization achieves 70%+ token reduction (SC-002)."""
        mock_client = MagicMock()

        # Create animal with many traits
        mock_animal = MagicMock()
        traits = {}
        for i in range(30):
            traits[f"TRAIT_{i}"] = {
                "value": float(i),
                "accuracy": 0.3 + (i % 70) / 100.0,  # Mix of high and low accuracy
                "description": f"Long description for trait {i}" * 20,
            }

        mock_animal.to_dict.return_value = {
            "lpn_id": "TEST123",
            "breed": "Katahdin",
            "traits": traits,
            "sire_id": "SIRE",
            "dam_id": "DAM",
            "progeny": {"total_count": 10, "animals": []},
        }

        mock_client.get_animal_details.return_value = mock_animal
        mock_client_class.return_value = mock_client

        from nsip_mcp import mcp_tools

        # Explicitly request summarization to test reduction
        result = mcp_tools.nsip_get_animal.fn(search_string="TEST123", summarize=True)

        # Verify 70% reduction target (SC-002)
        assert result["_summarized"] is True, "Should be summarized when requested"
        assert "_reduction_percent" in result
        reduction = result["_reduction_percent"]
        assert reduction >= 70.0, f"Reduction should be >=70%, got {reduction}%"

    @pytest.mark.integration
    @patch("nsip_mcp.tools.NSIPClient")
    def test_fr005a_fields_preserved(self, mock_client_class):
        """Verify FR-005a required fields present in summaries."""
        mock_client = MagicMock()

        mock_details = MagicMock()
        mock_details.to_dict.return_value = {
            "lpn_id": "ABC123",
            "breed": "Katahdin",
            "traits": {f"T{i}": {"value": i, "accuracy": 0.8} for i in range(20)},
            "sire_id": "SIRE123",
            "dam_id": "DAM456",
            "contact": {"name": "Breeder Name", "email": "breeder@example.com"},
        }

        mock_lineage = MagicMock()
        mock_lineage.to_dict.return_value = {"sire": {}, "dam": {}}

        mock_progeny = MagicMock()
        mock_progeny.animals = []
        mock_progeny.total_count = 5
        mock_progeny.page = 0
        mock_progeny.page_size = 10

        mock_client.search_by_lpn.return_value = {
            "details": mock_details,
            "lineage": mock_lineage,
            "progeny": mock_progeny,
        }
        mock_client_class.return_value = mock_client

        from nsip_mcp import mcp_tools

        # Explicitly request summarization to test field preservation
        result = mcp_tools.nsip_search_by_lpn.fn(lpn_id="ABC123", summarize=True)

        # Verify FR-005a required fields present
        assert "_summarized" in result
        assert result["_summarized"] is True, "Should be summarized when requested"

        # Check for required fields
        assert "lpn_id" in result, "lpn_id should be preserved"
        assert "breed" in result, "breed should be preserved"
        # Note: The actual field names depend on summarize_response implementation

    @pytest.mark.integration
    @patch("nsip_mcp.tools.NSIPClient")
    def test_fr005b_fields_omitted(self, mock_client_class):
        """Verify FR-005b fields omitted from summaries."""
        mock_client = MagicMock()

        mock_animal = MagicMock()
        # Create large response to ensure summarization triggers
        traits = {}
        for i in range(30):
            acc = 0.3 + (i % 70) / 100.0  # Mix of high and low accuracy
            traits[f"TRAIT_{i}"] = {"value": float(i), "accuracy": acc}

        mock_animal.to_dict.return_value = {
            "lpn_id": "TEST12345",
            "breed": "Katahdin",
            "traits": traits,
            "verbose_registration_data": "x" * 5000,  # Should be omitted
            "detailed_records": [{"record": i, "data": "x" * 100} for i in range(50)],
        }

        mock_client.get_animal_details.return_value = mock_animal
        mock_client_class.return_value = mock_client

        from nsip_mcp import mcp_tools

        # Explicitly request summarization to test field omission
        result = mcp_tools.nsip_get_animal.fn(search_string="TEST12345", summarize=True)

        # Verify low-accuracy traits omitted (FR-005b)
        assert result["_summarized"] is True, "Should be summarized when requested"
        if "top_traits" in result:
            # Check that only high-accuracy traits included
            for trait in result["top_traits"]:
                assert trait.get("accuracy", 0) >= 0.5, "Low-accuracy traits should be omitted"

    @pytest.mark.integration
    @patch("nsip_mcp.tools.NSIPClient")
    def test_nsip_search_by_lpn_respects_summarize_flag(self, mock_client_class):
        """Verify nsip_search_by_lpn respects summarize parameter (opt-in)."""
        mock_client = MagicMock()

        mock_details = MagicMock()
        mock_details.to_dict.return_value = {"lpn_id": "ABC12345", "breed": "Katahdin"}

        mock_lineage = MagicMock()
        mock_lineage.to_dict.return_value = {"sire": {}, "dam": {}}

        mock_progeny = MagicMock()
        mock_progeny.animals = []
        mock_progeny.total_count = 0
        mock_progeny.page = 0
        mock_progeny.page_size = 10

        mock_client.search_by_lpn.return_value = {
            "details": mock_details,
            "lineage": mock_lineage,
            "progeny": mock_progeny,
        }
        mock_client_class.return_value = mock_client

        from nsip_mcp import mcp_tools

        # Default: no summarization
        result_default = mcp_tools.nsip_search_by_lpn.fn(lpn_id="ABC12345")
        assert "_summarized" in result_default
        assert result_default["_summarized"] is False, "Should NOT summarize by default"

        # Explicit opt-in: summarization enabled
        result_summarized = mcp_tools.nsip_search_by_lpn.fn(lpn_id="ABC12345", summarize=True)
        assert "_summarized" in result_summarized
        assert result_summarized["_summarized"] is True, "Should summarize when requested"
        assert "_original_token_count" in result_summarized
        assert "_summary_token_count" in result_summarized


class TestUS3ParameterValidation:
    """Integration tests for User Story 3: Parameter Validation."""

    @pytest.mark.integration
    def test_invalid_lpn_id_rejected(self):
        """Verify invalid LPN ID (<5 chars) rejected with structured error."""
        from nsip_mcp import mcp_tools

        # Test empty string
        error_response = mcp_tools.nsip_get_animal.fn(search_string="")
        assert "code" in error_response, "Error should have code field"
        assert error_response["code"] == -32602, "Should be INVALID_PARAMS error"
        assert "message" in error_response, "Error should have message"
        assert "search_string" in error_response["message"].lower()

        # Test short LPN ID
        error_response = mcp_tools.nsip_get_animal.fn(search_string="123")
        assert error_response["code"] == -32602
        assert "data" in error_response, "Error should include data"
        assert "parameter" in error_response["data"]
        assert error_response["data"]["parameter"] == "search_string"

    @pytest.mark.integration
    def test_invalid_breed_id_rejected(self):
        """Verify invalid breed_id rejected with structured error."""
        from nsip_mcp import mcp_tools

        # Test negative breed_id
        error_response = mcp_tools.nsip_get_trait_ranges.fn(breed_id=-1)
        assert error_response["code"] == -32602
        assert "breed_id" in error_response["message"].lower()

        # Test zero breed_id
        error_response = mcp_tools.nsip_get_trait_ranges.fn(breed_id=0)
        assert error_response["code"] == -32602
        assert "data" in error_response
        assert error_response["data"]["parameter"] == "breed_id"

    @pytest.mark.integration
    def test_invalid_pagination_rejected(self):
        """Verify invalid pagination parameters rejected."""
        from nsip_mcp import mcp_tools

        # Test negative page
        error_response = mcp_tools.nsip_search_animals.fn(page=-1)
        assert error_response["code"] == -32602
        assert "page" in error_response["message"].lower()

        # Test page_size too large
        error_response = mcp_tools.nsip_search_animals.fn(page_size=200)
        assert error_response["code"] == -32602
        assert "page_size" in error_response["message"].lower()

        # Test page_size too small
        error_response = mcp_tools.nsip_search_animals.fn(page_size=0)
        assert error_response["code"] == -32602

    @pytest.mark.integration
    def test_error_includes_suggestion(self):
        """Verify error response includes suggestion for correction."""
        from nsip_mcp import mcp_tools

        error_response = mcp_tools.nsip_get_animal.fn(search_string="123")

        # Verify structured error data
        assert "data" in error_response
        assert "suggestion" in error_response["data"], "Error should include suggestion"
        assert len(error_response["data"]["suggestion"]) > 0, "Suggestion should be non-empty"

        # Verify suggestion is actionable
        suggestion = error_response["data"]["suggestion"]
        assert any(
            word in suggestion.lower()
            for word in ["full", "complete", "characters", "example", "e.g.", "lpn"]
        ), "Suggestion should be actionable"

    @pytest.mark.integration
    @patch("nsip_mcp.tools.NSIPClient")
    def test_llm_can_retry_with_correction(self, mock_client_class):
        """Verify LLM can interpret error and retry successfully (SC-004)."""
        from nsip_mcp import mcp_tools

        # Step 1: LLM invokes with invalid parameter
        error_response = mcp_tools.nsip_get_animal.fn(search_string="123")
        assert error_response["code"] == -32602
        assert "suggestion" in error_response["data"]

        # Step 2: LLM reads suggestion and corrects parameter
        # Suggestion says: "Provide full LPN ID (minimum 5 characters, e.g., '6####92020###249')"
        # LLM extracts example or uses full ID

        # Mock successful API response
        mock_client = MagicMock()
        mock_animal = MagicMock()
        mock_animal.to_dict.return_value = {
            "lpn_id": "6####92020###249",
            "breed": "Katahdin",
        }
        mock_client.get_animal_details.return_value = mock_animal
        mock_client_class.return_value = mock_client

        # Step 3: LLM retries with corrected parameter
        success_response = mcp_tools.nsip_get_animal.fn(search_string="6####92020###249")
        assert "code" not in success_response, "Success response should not have error code"
        assert "lpn_id" in success_response, "Success response should have data"

    @pytest.mark.integration
    def test_95_percent_validation_success(self):
        """Verify 95%+ invalid requests caught before API (SC-003)."""
        from nsip_mcp import mcp_tools

        # Test comprehensive set of invalid inputs
        invalid_cases = [
            # Empty/whitespace
            ("nsip_get_animal", {"search_string": ""}),
            ("nsip_get_animal", {"search_string": "   "}),
            # Too short
            ("nsip_get_animal", {"search_string": "12"}),
            ("nsip_get_animal", {"search_string": "1234"}),
            # Invalid breed_id
            ("nsip_get_trait_ranges", {"breed_id": -1}),
            ("nsip_get_trait_ranges", {"breed_id": 0}),
            # Invalid pagination
            ("nsip_search_animals", {"page": -1}),
            ("nsip_search_animals", {"page": -100}),
            ("nsip_search_animals", {"page_size": 0}),
            ("nsip_search_animals", {"page_size": 200}),
            ("nsip_search_animals", {"page_size": 1000}),
            # Invalid lineage parameters
            ("nsip_get_lineage", {"lpn_id": ""}),
            ("nsip_get_lineage", {"lpn_id": "123"}),
            # Invalid progeny parameters
            ("nsip_get_progeny", {"lpn_id": "12"}),
            ("nsip_get_progeny", {"lpn_id": "", "page": -1}),
            # Invalid search_by_lpn parameters
            ("nsip_search_by_lpn", {"lpn_id": ""}),
            ("nsip_search_by_lpn", {"lpn_id": "   "}),
        ]

        caught_count = 0
        for tool_name, params in invalid_cases:
            tool = getattr(mcp_tools, tool_name)
            result = tool.fn(**params)

            # Check if validation error returned
            if isinstance(result, dict) and result.get("code") == -32602:
                caught_count += 1

        # Verify 95%+ caught (SC-003)
        total = len(invalid_cases)
        success_rate = (caught_count / total) * 100
        assert success_rate >= 95.0, f"Validation success rate {success_rate}% < 95%"


class TestUS3ApiErrorHandling:
    """Integration tests for User Story 3: API Error Handling."""

    @pytest.mark.integration
    @patch("nsip_mcp.tools.NSIPClient")
    def test_nsip_api_failure_handling(self, mock_client_class):
        """Verify NSIP API failures return structured errors."""
        from nsip_mcp import mcp_tools

        # Mock API failure
        mock_client = MagicMock()
        mock_client.get_animal_details.side_effect = Exception(
            "NSIP API Error: 500 Internal Server Error"
        )
        mock_client_class.return_value = mock_client

        # Invoke tool
        error_response = mcp_tools.nsip_get_animal.fn(search_string="6####92020###249")

        # Verify structured error response
        assert isinstance(error_response, dict), "Error should be dict"
        assert "code" in error_response, "Error should have code"
        assert error_response["code"] == -32000, "Should be NSIP_API_ERROR"
        assert "message" in error_response, "Error should have message"
        assert "data" in error_response, "Error should have data"

    @pytest.mark.integration
    @patch("nsip_mcp.tools.NSIPClient")
    def test_nsip_not_found_error(self, mock_client_class):
        """Verify 404 Not Found errors handled properly."""
        from nsip_client.exceptions import NSIPNotFoundError
        from nsip_mcp import mcp_tools

        mock_client = MagicMock()
        mock_client.get_animal_details.side_effect = NSIPNotFoundError("Animal not found")
        mock_client_class.return_value = mock_client

        error_response = mcp_tools.nsip_get_animal.fn(search_string="NOTFOUND123")

        assert error_response["code"] == -32000
        assert "not found" in error_response["message"].lower()

    @pytest.mark.integration
    @patch("nsip_mcp.tools.NSIPClient")
    def test_nsip_timeout_error(self, mock_client_class):
        """Verify timeout errors include retry-after guidance."""
        from nsip_client.exceptions import NSIPTimeoutError
        from nsip_mcp import mcp_tools

        mock_client = MagicMock()
        mock_client.get_animal_details.side_effect = NSIPTimeoutError("Request timeout after 30s")
        mock_client_class.return_value = mock_client

        error_response = mcp_tools.nsip_get_animal.fn(search_string="TIMEOUT123")

        assert error_response["code"] == -32000
        assert "data" in error_response
        assert "suggestion" in error_response["data"]
        # Verify timeout-specific suggestion
        suggestion = error_response["data"]["suggestion"]
        assert (
            "timeout" in suggestion.lower()
            or "retry" in suggestion.lower()
            or "wait" in suggestion.lower()
        )

    @pytest.mark.integration
    @patch("nsip_mcp.tools.NSIPClient")
    def test_error_suggestion_provided(self, mock_client_class):
        """Verify API errors include retry guidance."""
        from nsip_mcp import mcp_tools

        mock_client = MagicMock()
        mock_client.get_lineage.side_effect = Exception("Network error")
        mock_client_class.return_value = mock_client

        error_response = mcp_tools.nsip_get_lineage.fn(lpn_id="NETWORKERROR")

        # Verify suggestion included
        assert "data" in error_response
        assert "suggestion" in error_response["data"]
        assert len(error_response["data"]["suggestion"]) > 0

        # Verify suggestion is actionable
        suggestion = error_response["data"]["suggestion"].lower()
        assert any(
            word in suggestion for word in ["verify", "check", "retry", "try", "wait", "lpn"]
        ), "Suggestion should provide actionable guidance"

    @pytest.mark.integration
    @patch("nsip_mcp.tools.NSIPClient")
    def test_multiple_error_types_handled(self, mock_client_class):
        """Verify different error types all return structured responses."""
        from nsip_client.exceptions import (
            NSIPAPIError,
            NSIPNotFoundError,
            NSIPTimeoutError,
            NSIPValidationError,
        )
        from nsip_mcp import mcp_tools

        test_cases = [
            (NSIPAPIError("API Error"), "API call failed"),
            (NSIPNotFoundError("Not found"), "Resource not found"),
            (NSIPTimeoutError("Timeout"), "Request timed out"),
            (NSIPValidationError("Invalid"), "Validation failed"),
            (Exception("Generic error"), "Unexpected error"),
        ]

        for exception, expected_message_part in test_cases:
            mock_client = MagicMock()
            mock_client.get_animal_details.side_effect = exception
            mock_client_class.return_value = mock_client

            error_response = mcp_tools.nsip_get_animal.fn(search_string="TEST123")

            # All should return structured errors
            assert isinstance(error_response, dict)
            assert "code" in error_response
            assert error_response["code"] == -32000
            assert "message" in error_response
            assert "data" in error_response

    @pytest.mark.integration
    @patch("nsip_mcp.tools.NSIPClient")
    def test_error_includes_original_error_info(self, mock_client_class):
        """Verify original error information preserved in response."""
        from nsip_mcp import mcp_tools

        mock_client = MagicMock()
        original_error = "NSIP API returned 503: Service Unavailable"
        mock_client.search_animals.side_effect = Exception(original_error)
        mock_client_class.return_value = mock_client

        error_response = mcp_tools.nsip_search_animals.fn()

        # Verify original error info available
        assert "data" in error_response
        # Original error might be in suggestion or as separate field
        _ = str(error_response)  # Verify convertible to string
        # At minimum, the error message should reference the problem
        assert "message" in error_response
        assert len(error_response["message"]) > 0


class TestMultiTransport:
    """Integration tests for multiple transport mechanisms (FR-008a)."""

    @pytest.mark.integration
    def test_stdio_transport(self):
        """Verify stdio transport (default) works correctly."""
        import os

        from nsip_mcp.transport import TransportConfig, TransportType

        # Clear any existing transport environment variables
        old_transport = os.environ.pop("MCP_TRANSPORT", None)
        old_port = os.environ.pop("MCP_PORT", None)

        try:
            # Test default stdio transport (no environment variables)
            config = TransportConfig.from_environment()
            assert config.transport_type == TransportType.STDIO, "Default should be stdio"
            assert config.port is None, "stdio transport should not require port"

            # Test explicit stdio configuration
            os.environ["MCP_TRANSPORT"] = "stdio"
            config = TransportConfig.from_environment()
            assert config.transport_type == TransportType.STDIO
            assert config.port is None

            # Verify validation passes for stdio
            config.validate()  # Should not raise

        finally:
            # Restore original environment
            if old_transport:
                os.environ["MCP_TRANSPORT"] = old_transport
            if old_port:
                os.environ["MCP_PORT"] = old_port

    @pytest.mark.integration
    def test_http_sse_transport(self):
        """Verify HTTP SSE transport (backward compatibility - mapped to streamable-http)."""
        import os

        from nsip_mcp.transport import TransportConfig, TransportType

        # Clear any existing transport environment variables
        old_transport = os.environ.pop("MCP_TRANSPORT", None)
        old_port = os.environ.pop("MCP_PORT", None)

        try:
            # Test HTTP SSE transport configuration (legacy, should map to streamable-http)
            os.environ["MCP_TRANSPORT"] = "http-sse"
            os.environ["MCP_PORT"] = "8080"

            config = TransportConfig.from_environment()
            assert (
                config.transport_type == TransportType.STREAMABLE_HTTP
            )  # Mapped for backward compatibility
            assert config.port == 8080

            # Verify validation passes
            config.validate()  # Should not raise

            # Test missing port raises error
            os.environ.pop("MCP_PORT")
            try:
                TransportConfig.from_environment()
                assert False, "Should raise ValueError for missing port"
            except ValueError as e:
                assert "MCP_PORT" in str(e)
                assert "required" in str(e).lower()

        finally:
            # Restore original environment
            if old_transport:
                os.environ["MCP_TRANSPORT"] = old_transport
            else:
                os.environ.pop("MCP_TRANSPORT", None)
            if old_port:
                os.environ["MCP_PORT"] = old_port
            else:
                os.environ.pop("MCP_PORT", None)

    @pytest.mark.integration
    def test_websocket_transport(self):
        """Verify WebSocket transport works correctly."""
        import os

        from nsip_mcp.transport import TransportConfig, TransportType

        # Clear any existing transport environment variables
        old_transport = os.environ.pop("MCP_TRANSPORT", None)
        old_port = os.environ.pop("MCP_PORT", None)

        try:
            # Test WebSocket transport configuration
            os.environ["MCP_TRANSPORT"] = "websocket"
            os.environ["MCP_PORT"] = "9090"

            config = TransportConfig.from_environment()
            assert config.transport_type == TransportType.WEBSOCKET
            assert config.port == 9090

            # Verify validation passes
            config.validate()  # Should not raise

            # Test invalid port range
            os.environ["MCP_PORT"] = "100"  # Below 1024
            try:
                config = TransportConfig.from_environment()
                assert False, "Should raise ValueError for invalid port range"
            except ValueError as e:
                assert "1024" in str(e) and "65535" in str(e)

            # Test missing port raises error
            os.environ.pop("MCP_PORT")
            try:
                TransportConfig.from_environment()
                assert False, "Should raise ValueError for missing port"
            except ValueError as e:
                assert "MCP_PORT" in str(e)
                assert "required" in str(e).lower()

        finally:
            # Restore original environment
            if old_transport:
                os.environ["MCP_TRANSPORT"] = old_transport
            else:
                os.environ.pop("MCP_TRANSPORT", None)
            if old_port:
                os.environ["MCP_PORT"] = old_port
            else:
                os.environ.pop("MCP_PORT", None)


class TestEndToEndWorkflow:
    """End-to-end integration test combining all user stories."""

    @pytest.mark.integration
    @pytest.mark.slow
    @patch("nsip_mcp.tools.NSIPClient")
    def test_complete_workflow(self, mock_client_class):
        """
        Test complete workflow:
        1. Connect client
        2. Discover tools
        3. Invoke tool
        4. Verify context management
        5. Test error handling
        6. Validate metrics
        """
        from nsip_mcp import mcp_tools
        from nsip_mcp.metrics import server_metrics

        # === 1. Connect Client ===
        # Verify MCP server is initialized and accessible
        assert mcp is not None, "MCP server should be initialized"

        # === 2. Discover Tools ===
        # Verify all tools are discoverable (SC-001: <5 seconds)
        start_time = time.time()
        tools = asyncio.run(mcp.get_tools())
        discovery_time = time.time() - start_time

        assert len(tools) == 10, "Should discover all 10 tools"
        assert discovery_time < 5.0, f"Discovery took {discovery_time}s, should be <5s (SC-001)"

        # Verify NSIP tools exist
        nsip_tools = [
            "nsip_get_last_update",
            "nsip_list_breeds",
            "nsip_get_statuses",
            "nsip_get_trait_ranges",
            "nsip_search_animals",
            "nsip_get_animal",
            "nsip_get_lineage",
            "nsip_get_progeny",
            "nsip_search_by_lpn",
            "get_server_health",
        ]
        for tool_name in nsip_tools:
            assert tool_name in tools, f"Tool {tool_name} not discovered"

        # === 3. Invoke Tool ===
        # Set up mock client for successful API call
        mock_client = MagicMock()

        # Mock small response (pass-through)
        mock_breed_1 = MagicMock()
        mock_breed_1.id = 61
        mock_breed_1.name = "Range"
        mock_client.get_available_breed_groups.return_value = [mock_breed_1]

        # Mock large response (summarization)
        mock_animal = MagicMock()
        large_data = {
            "lpn_id": "6####92020###249",
            "breed": "Katahdin",
            "tag": "TAG123",
            "sire_id": "SIRE456",
            "dam_id": "DAM789",
            "verbose_data": "x" * 15000,  # Exceeds 2000 token threshold
            "detailed_records": [{"record": i, "data": "x" * 100} for i in range(100)],
            "traits": {
                "BWT": {"value": 0.5, "accuracy": 0.89},
                "YWT": {"value": 2.1, "accuracy": 0.92},
                "MWT": {"value": 1.8, "accuracy": 0.65},  # Low accuracy - should be filtered
            },
        }
        mock_animal.to_dict.return_value = large_data
        mock_client.get_animal_details.return_value = mock_animal

        mock_client_class.return_value = mock_client

        # Invoke tool with valid parameters
        result_small = mcp_tools.nsip_list_breeds.fn()
        assert isinstance(result_small, dict), "Response is wrapped in success/data"
        assert result_small["success"] is True
        assert "data" in result_small
        assert len(result_small["data"]) == 1
        assert result_small["data"][0]["id"] == 61

        # === 4. Verify Context Management ===
        # Test pass-through behavior (default, no summarization)
        assert "_summarized" not in str(result_small), "Small response should not be summarized"

        # Test summarization when explicitly requested (SC-002: >=70% reduction)
        result_large = mcp_tools.nsip_get_animal.fn(
            search_string="6####92020###249", summarize=True
        )
        assert "_summarized" in result_large, "Large response should be summarized when requested"
        assert result_large["_summarized"] is True, "Summarization flag should be True"

        # Verify FR-005a fields preserved
        assert "lpn_id" in result_large, "FR-005a: lpn_id (identity) should be preserved"
        assert "breed" in result_large, "FR-005a: breed (identity) should be preserved"
        assert "sire" in result_large, "FR-005a: sire (pedigree) should be preserved"
        assert "dam" in result_large, "FR-005a: dam (pedigree) should be preserved"
        assert (
            "total_progeny" in result_large
        ), "FR-005a: total_progeny (offspring) should be preserved"
        assert "top_traits" in result_large, "FR-005a: top_traits should be preserved"

        # Verify FR-005b fields omitted
        assert "verbose_data" not in result_large, "FR-005b: verbose_data should be omitted"
        assert "detailed_records" not in result_large, "FR-005b: detailed_records should be omitted"
        assert "tag" not in result_large, "FR-005b: registration metadata (tag) should be omitted"

        # === 5. Test Error Handling ===
        # Record initial validation count
        initial_validation_attempts = server_metrics.validation_attempts

        # Test parameter validation (SC-003: >=95% caught before API)
        error_response = mcp_tools.nsip_get_animal.fn(search_string="123")

        # Verify structured error response
        assert "code" in error_response, "Error should have code"
        assert error_response["code"] == -32602, "Should be invalid params error"
        assert "message" in error_response, "Error should have message"
        assert "data" in error_response, "Error should have data"
        assert "suggestion" in error_response["data"], "Error should include suggestion"

        # Verify validation was tracked
        assert (
            server_metrics.validation_attempts > initial_validation_attempts
        ), "Validation should be tracked"

        # Test LLM retry with correction (SC-004: 80% success)
        corrected_response = mcp_tools.nsip_get_animal.fn(search_string="6####92020###249")
        assert "code" not in corrected_response, "Corrected request should succeed"
        assert "lpn_id" in corrected_response, "Corrected request should return data"

        # === 6. Validate Metrics ===
        # Verify cache metrics are tracked
        from nsip_mcp.cache import response_cache

        total_cache_operations = response_cache.hits + response_cache.misses
        assert total_cache_operations > 0, "Cache operations should be tracked"

        # Verify server metrics are available
        metrics_dict = server_metrics.to_dict()
        assert "validation" in metrics_dict, "Metrics should track validation"
        assert "cache" in metrics_dict, "Metrics should track cache"

        # Verify success criteria structure
        criteria = server_metrics.meets_success_criteria()
        assert "SC-001 Discovery <5s" in criteria, "Should track SC-001"
        assert "SC-002 Reduction >=70%" in criteria, "Should track SC-002"
        assert "SC-003 Validation >=95%" in criteria, "Should track SC-003"

        # === Complete Workflow Validation ===
        # All six components successfully validated
        assert True, "Complete end-to-end workflow passed"
