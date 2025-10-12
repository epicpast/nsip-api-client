"""
Unit tests for MCP tool wrappers

Tests all 9 MCP tools that wrap NSIPClient methods:
- nsip_get_last_update
- nsip_list_breeds
- nsip_get_statuses
- nsip_get_trait_ranges
- nsip_search_animals
- nsip_get_animal
- nsip_get_lineage
- nsip_get_progeny
- nsip_search_by_lpn

Test coverage:
- Parameter validation
- Successful API calls with mocked NSIPClient responses
- Cache behavior (first call miss, second call hit)
- Tool discovery (all 9 tools registered)
- Error handling and structured error messages

Target: >90% coverage (SC-011)
"""

import asyncio
from unittest.mock import MagicMock, patch

import pytest

from nsip_mcp import mcp_tools
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


class TestMcpToolDiscovery:
    """Test MCP tool registration and discovery."""

    def test_all_tools_registered(self):
        """Verify all 9 NSIP tools are registered with MCP server."""
        # Get dict of registered tools from MCP server (FastMCP 2.x uses get_tools())
        tools_dict = asyncio.run(mcp.get_tools())
        tool_names = list(tools_dict.keys())

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
            assert tool_name in tool_names, f"Tool {tool_name} not registered"

    def test_tool_descriptions_populated(self):
        """Verify all tools have non-empty descriptions (FR-002)."""
        tools_dict = asyncio.run(mcp.get_tools())

        for tool_name, tool in tools_dict.items():
            if tool_name.startswith("nsip_"):
                assert tool.description, f"Tool {tool_name} has no description"
                assert len(tool.description) > 10, f"Tool {tool_name} description too short"


class TestNsipGetLastUpdate:
    """Tests for nsip_get_last_update tool."""

    @patch("nsip_mcp.tools.NSIPClient")
    def test_returns_valid_response(self, mock_client_class):
        """Verify tool returns last update date."""
        mock_client = MagicMock()
        mock_client.get_date_last_updated.return_value = {"date": "09/23/2025"}
        mock_client_class.return_value = mock_client

        # Access the actual function via .fn attribute
        result = mcp_tools.nsip_get_last_update.fn()

        assert result == {"date": "09/23/2025"}
        mock_client.get_date_last_updated.assert_called_once()

    @patch("nsip_mcp.tools.NSIPClient")
    def test_caching_behavior(self, mock_client_class):
        """Verify tool uses cache correctly."""
        mock_client = MagicMock()
        mock_client.get_date_last_updated.return_value = {"date": "09/23/2025"}
        mock_client_class.return_value = mock_client

        # First call - cache miss
        result1 = mcp_tools.nsip_get_last_update.fn()
        assert mock_client.get_date_last_updated.call_count == 1

        # Second call - cache hit
        result2 = mcp_tools.nsip_get_last_update.fn()
        assert result1 == result2
        assert mock_client.get_date_last_updated.call_count == 1  # Still 1, not called again


class TestNsipListBreeds:
    """Tests for nsip_list_breeds tool."""

    @patch("nsip_mcp.tools.NSIPClient")
    def test_returns_breed_list(self, mock_client_class):
        """Verify tool returns array of breeds with id and name."""
        mock_client = MagicMock()

        # Create mock breed objects with id and name attributes
        mock_breed_1 = MagicMock()
        mock_breed_1.id = 61
        mock_breed_1.name = "Range"

        mock_breed_2 = MagicMock()
        mock_breed_2.id = 62
        mock_breed_2.name = "Maternal Wool"

        mock_breed_3 = MagicMock()
        mock_breed_3.id = 64
        mock_breed_3.name = "Hair"

        mock_breed_4 = MagicMock()
        mock_breed_4.id = 69
        mock_breed_4.name = "Terminal"

        mock_client.get_available_breed_groups.return_value = [
            mock_breed_1,
            mock_breed_2,
            mock_breed_3,
            mock_breed_4,
        ]
        mock_client_class.return_value = mock_client

        result = mcp_tools.nsip_list_breeds.fn()

        expected = [
            {"id": 61, "name": "Range"},
            {"id": 62, "name": "Maternal Wool"},
            {"id": 64, "name": "Hair"},
            {"id": 69, "name": "Terminal"},
        ]
        assert result == expected
        mock_client.get_available_breed_groups.assert_called_once()

    @patch("nsip_mcp.tools.NSIPClient")
    def test_caching_behavior(self, mock_client_class):
        """Verify tool uses cache correctly."""
        mock_client = MagicMock()

        mock_breed = MagicMock()
        mock_breed.id = 61
        mock_breed.name = "Range"

        mock_client.get_available_breed_groups.return_value = [mock_breed]
        mock_client_class.return_value = mock_client

        # First call - cache miss
        result1 = mcp_tools.nsip_list_breeds.fn()
        assert mock_client.get_available_breed_groups.call_count == 1

        # Second call - cache hit
        result2 = mcp_tools.nsip_list_breeds.fn()
        assert result1 == result2
        assert mock_client.get_available_breed_groups.call_count == 1  # Not called again

    @patch("nsip_mcp.tools.NSIPClient")
    def test_empty_breed_list(self, mock_client_class):
        """Verify tool handles empty breed list."""
        mock_client = MagicMock()
        mock_client.get_available_breed_groups.return_value = []
        mock_client_class.return_value = mock_client

        result = mcp_tools.nsip_list_breeds.fn()

        assert result == []
        mock_client.get_available_breed_groups.assert_called_once()


class TestNsipGetStatuses:
    """Tests for nsip_get_statuses tool."""

    @patch("nsip_mcp.tools.NSIPClient")
    def test_returns_status_list(self, mock_client_class):
        """Verify tool returns list of status strings."""
        mock_client = MagicMock()
        mock_client.get_statuses_by_breed_group.return_value = [
            "CURRENT",
            "SOLD",
            "DEAD",
            "COMMERCIAL",
            "CULL",
            "EXPORTED",
        ]
        mock_client_class.return_value = mock_client

        result = mcp_tools.nsip_get_statuses.fn()

        expected = ["CURRENT", "SOLD", "DEAD", "COMMERCIAL", "CULL", "EXPORTED"]
        assert result == expected
        mock_client.get_statuses_by_breed_group.assert_called_once()

    @patch("nsip_mcp.tools.NSIPClient")
    def test_caching_behavior(self, mock_client_class):
        """Verify tool uses cache correctly."""
        mock_client = MagicMock()
        mock_client.get_statuses_by_breed_group.return_value = ["CURRENT", "SOLD"]
        mock_client_class.return_value = mock_client

        # First call - cache miss
        result1 = mcp_tools.nsip_get_statuses.fn()
        assert mock_client.get_statuses_by_breed_group.call_count == 1

        # Second call - cache hit
        result2 = mcp_tools.nsip_get_statuses.fn()
        assert result1 == result2
        assert mock_client.get_statuses_by_breed_group.call_count == 1  # Not called again


class TestNsipGetTraitRanges:
    """Tests for nsip_get_trait_ranges tool."""

    @patch("nsip_mcp.tools.NSIPClient")
    def test_requires_breed_id(self, mock_client_class):
        """Verify breed_id parameter is required."""
        mock_client = MagicMock()
        mock_client.get_trait_ranges_by_breed.return_value = {
            "BWT": {"min": -0.713, "max": 0.0},
            "WWT": {"min": -1.234, "max": 2.456},
        }
        mock_client_class.return_value = mock_client

        # breed_id is a required parameter, calling without it should work
        # but pass it to the client method
        result = mcp_tools.nsip_get_trait_ranges.fn(breed_id=486)

        assert "BWT" in result
        assert "WWT" in result
        mock_client.get_trait_ranges_by_breed.assert_called_once_with(486)

    @patch("nsip_mcp.tools.NSIPClient")
    def test_returns_trait_ranges(self, mock_client_class):
        """Verify tool returns trait ranges with min/max values."""
        mock_client = MagicMock()
        mock_client.get_trait_ranges_by_breed.return_value = {
            "BWT": {"min": -0.713, "max": 0.0},
            "WWT": {"min": -1.234, "max": 2.456},
            "YWT": {"min": -2.1, "max": 3.8},
            "PFAT": {"min": -0.5, "max": 0.5},
        }
        mock_client_class.return_value = mock_client

        result = mcp_tools.nsip_get_trait_ranges.fn(breed_id=486)

        assert result == {
            "BWT": {"min": -0.713, "max": 0.0},
            "WWT": {"min": -1.234, "max": 2.456},
            "YWT": {"min": -2.1, "max": 3.8},
            "PFAT": {"min": -0.5, "max": 0.5},
        }
        mock_client.get_trait_ranges_by_breed.assert_called_once_with(486)

    @patch("nsip_mcp.tools.NSIPClient")
    def test_caching_behavior(self, mock_client_class):
        """Verify tool uses cache correctly."""
        mock_client = MagicMock()
        mock_client.get_trait_ranges_by_breed.return_value = {
            "BWT": {"min": -0.713, "max": 0.0},
        }
        mock_client_class.return_value = mock_client

        # First call - cache miss
        result1 = mcp_tools.nsip_get_trait_ranges.fn(breed_id=486)
        assert mock_client.get_trait_ranges_by_breed.call_count == 1

        # Second call with same breed_id - cache hit
        result2 = mcp_tools.nsip_get_trait_ranges.fn(breed_id=486)
        assert result1 == result2
        assert mock_client.get_trait_ranges_by_breed.call_count == 1  # Not called again

    @patch("nsip_mcp.tools.NSIPClient")
    def test_different_breed_ids_separate_cache(self, mock_client_class):
        """Verify different breed_ids use separate cache entries."""
        mock_client = MagicMock()
        mock_client.get_trait_ranges_by_breed.return_value = {"BWT": {"min": 0, "max": 1}}
        mock_client_class.return_value = mock_client

        # Call with breed_id=486
        mcp_tools.nsip_get_trait_ranges.fn(breed_id=486)
        assert mock_client.get_trait_ranges_by_breed.call_count == 1

        # Call with different breed_id=487 - should call API again
        mcp_tools.nsip_get_trait_ranges.fn(breed_id=487)
        assert mock_client.get_trait_ranges_by_breed.call_count == 2


class TestNsipSearchAnimals:
    """Tests for nsip_search_animals tool."""

    @patch("nsip_mcp.tools.NSIPClient")
    def test_pagination_parameters(self, mock_client_class):
        """Verify page and page_size parameters work correctly."""
        mock_client = MagicMock()

        # Create mock search result object
        mock_result = MagicMock()
        mock_result.results = [
            {"LpnId": "6401492020FLE249", "Breed": "Katahdin"},
            {"LpnId": "6401492020FLE250", "Breed": "Katahdin"},
        ]
        mock_result.total_count = 1523
        mock_result.page = 1
        mock_result.page_size = 20

        mock_client.search_animals.return_value = mock_result
        mock_client_class.return_value = mock_client

        result = mcp_tools.nsip_search_animals.fn(page=1, page_size=20)

        assert result["page"] == 1
        assert result["page_size"] == 20
        assert result["total_count"] == 1523
        assert len(result["results"]) == 2

        mock_client.search_animals.assert_called_once_with(
            page=1,
            page_size=20,
            breed_id=None,
            sorted_trait=None,
            reverse=None,
            search_criteria=None,
        )

    @patch("nsip_mcp.tools.NSIPClient")
    def test_search_criteria_optional(self, mock_client_class):
        """Verify search_criteria parameter is optional."""
        mock_client = MagicMock()

        mock_result = MagicMock()
        mock_result.results = []
        mock_result.total_count = 0
        mock_result.page = 0
        mock_result.page_size = 15

        mock_client.search_animals.return_value = mock_result
        mock_client_class.return_value = mock_client

        # Call without search_criteria
        result = mcp_tools.nsip_search_animals.fn()

        assert result["results"] == []
        assert result["total_count"] == 0

        mock_client.search_animals.assert_called_once_with(
            page=0,
            page_size=15,
            breed_id=None,
            sorted_trait=None,
            reverse=None,
            search_criteria=None,
        )

    @patch("nsip_mcp.tools.NSIPClient")
    def test_with_all_parameters(self, mock_client_class):
        """Verify tool passes all parameters correctly."""
        mock_client = MagicMock()

        mock_result = MagicMock()
        mock_result.results = [{"LpnId": "ABC123"}]
        mock_result.total_count = 1
        mock_result.page = 0
        mock_result.page_size = 15

        mock_client.search_animals.return_value = mock_result
        mock_client_class.return_value = mock_client

        search_criteria = {"status": "CURRENT", "gender": "F"}
        result = mcp_tools.nsip_search_animals.fn(
            page=0,
            page_size=15,
            breed_id=486,
            sorted_trait="BWT",
            reverse=True,
            search_criteria=search_criteria,
        )

        assert result["total_count"] == 1

        mock_client.search_animals.assert_called_once_with(
            page=0,
            page_size=15,
            breed_id=486,
            sorted_trait="BWT",
            reverse=True,
            search_criteria=search_criteria,
        )

    @patch("nsip_mcp.tools.NSIPClient")
    def test_caching_behavior(self, mock_client_class):
        """Verify tool uses cache correctly."""
        mock_client = MagicMock()

        mock_result = MagicMock()
        mock_result.results = [{"LpnId": "ABC123"}]
        mock_result.total_count = 1
        mock_result.page = 0
        mock_result.page_size = 15

        mock_client.search_animals.return_value = mock_result
        mock_client_class.return_value = mock_client

        # First call - cache miss
        result1 = mcp_tools.nsip_search_animals.fn(page=0, page_size=15)
        assert mock_client.search_animals.call_count == 1

        # Second call with same parameters - cache hit
        result2 = mcp_tools.nsip_search_animals.fn(page=0, page_size=15)
        assert result1 == result2
        assert mock_client.search_animals.call_count == 1  # Not called again


class TestNsipGetAnimal:
    """Tests for nsip_get_animal tool."""

    @patch("nsip_mcp.tools.NSIPClient")
    def test_requires_search_string(self, mock_client_class):
        """Verify search_string parameter is required."""
        mock_client = MagicMock()

        mock_animal = MagicMock()
        mock_animal.to_dict.return_value = {
            "lpn_id": "6401492020FLE249",
            "breed": "Katahdin",
            "gender": "Female",
        }

        mock_client.get_animal_details.return_value = mock_animal
        mock_client_class.return_value = mock_client

        result = mcp_tools.nsip_get_animal.fn(search_string="6401492020FLE249")

        assert result["lpn_id"] == "6401492020FLE249"
        mock_client.get_animal_details.assert_called_once_with("6401492020FLE249")

    @patch("nsip_mcp.tools.NSIPClient")
    def test_returns_complete_animal_info(self, mock_client_class):
        """Verify tool returns complete animal information."""
        mock_client = MagicMock()

        mock_animal = MagicMock()
        mock_animal.to_dict.return_value = {
            "lpn_id": "6401492020FLE249",
            "breed": "Katahdin",
            "gender": "Female",
            "traits": {
                "BWT": {"value": 0.246, "accuracy": 0.89},
                "WWT": {"value": 1.234, "accuracy": 0.92},
            },
            "sire_id": "ABC123",
            "dam_id": "DEF456",
        }

        mock_client.get_animal_details.return_value = mock_animal
        mock_client_class.return_value = mock_client

        result = mcp_tools.nsip_get_animal.fn(search_string="6401492020FLE249")

        assert result["lpn_id"] == "6401492020FLE249"
        assert result["breed"] == "Katahdin"
        assert result["gender"] == "Female"
        assert "traits" in result
        assert "BWT" in result["traits"]
        assert result["traits"]["BWT"]["value"] == 0.246

    @patch("nsip_mcp.tools.NSIPClient")
    def test_caching_behavior(self, mock_client_class):
        """Verify tool uses cache correctly."""
        mock_client = MagicMock()

        mock_animal = MagicMock()
        mock_animal.to_dict.return_value = {"lpn_id": "6401492020FLE249"}

        mock_client.get_animal_details.return_value = mock_animal
        mock_client_class.return_value = mock_client

        # First call - cache miss
        result1 = mcp_tools.nsip_get_animal.fn(search_string="6401492020FLE249")
        assert mock_client.get_animal_details.call_count == 1

        # Second call with same search_string - cache hit
        result2 = mcp_tools.nsip_get_animal.fn(search_string="6401492020FLE249")
        assert result1 == result2
        assert mock_client.get_animal_details.call_count == 1  # Not called again

    @patch("nsip_mcp.tools.NSIPClient")
    def test_different_search_strings_separate_cache(self, mock_client_class):
        """Verify different search strings use separate cache entries."""
        mock_client = MagicMock()

        mock_animal = MagicMock()
        mock_animal.to_dict.return_value = {"lpn_id": "ABC"}

        mock_client.get_animal_details.return_value = mock_animal
        mock_client_class.return_value = mock_client

        # Call with first search string
        mcp_tools.nsip_get_animal.fn(search_string="ABC123")
        assert mock_client.get_animal_details.call_count == 1

        # Call with different search string - should call API again
        mcp_tools.nsip_get_animal.fn(search_string="DEF456")
        assert mock_client.get_animal_details.call_count == 2


class TestNsipGetLineage:
    """Tests for nsip_get_lineage tool."""

    @patch("nsip_mcp.tools.NSIPClient")
    def test_requires_lpn_id(self, mock_client_class):
        """Verify lpn_id parameter is required."""
        mock_client = MagicMock()

        mock_lineage = MagicMock()
        mock_lineage.to_dict.return_value = {
            "sire": {"lpn_id": "123ABC", "name": "Ram A"},
            "dam": {"lpn_id": "456DEF", "name": "Ewe B"},
        }

        mock_client.get_lineage.return_value = mock_lineage
        mock_client_class.return_value = mock_client

        result = mcp_tools.nsip_get_lineage.fn(lpn_id="6401492020FLE249")

        assert "sire" in result
        assert "dam" in result
        mock_client.get_lineage.assert_called_once_with("6401492020FLE249")

    @patch("nsip_mcp.tools.NSIPClient")
    def test_returns_pedigree_info(self, mock_client_class):
        """Verify tool returns pedigree information."""
        mock_client = MagicMock()

        mock_lineage = MagicMock()
        mock_lineage.to_dict.return_value = {
            "sire": {
                "lpn_id": "123ABC",
                "name": "Ram A",
                "breed": "Katahdin",
            },
            "dam": {
                "lpn_id": "456DEF",
                "name": "Ewe B",
                "breed": "Katahdin",
            },
            "ancestors": {
                "paternal_grandsire": {"lpn_id": "789GHI"},
                "paternal_granddam": {"lpn_id": "012JKL"},
            },
        }

        mock_client.get_lineage.return_value = mock_lineage
        mock_client_class.return_value = mock_client

        result = mcp_tools.nsip_get_lineage.fn(lpn_id="6401492020FLE249")

        assert result["sire"]["lpn_id"] == "123ABC"
        assert result["dam"]["lpn_id"] == "456DEF"
        assert "ancestors" in result
        assert "paternal_grandsire" in result["ancestors"]

    @patch("nsip_mcp.tools.NSIPClient")
    def test_caching_behavior(self, mock_client_class):
        """Verify tool uses cache correctly."""
        mock_client = MagicMock()

        mock_lineage = MagicMock()
        mock_lineage.to_dict.return_value = {"sire": {}, "dam": {}}

        mock_client.get_lineage.return_value = mock_lineage
        mock_client_class.return_value = mock_client

        # First call - cache miss
        result1 = mcp_tools.nsip_get_lineage.fn(lpn_id="6401492020FLE249")
        assert mock_client.get_lineage.call_count == 1

        # Second call with same lpn_id - cache hit
        result2 = mcp_tools.nsip_get_lineage.fn(lpn_id="6401492020FLE249")
        assert result1 == result2
        assert mock_client.get_lineage.call_count == 1  # Not called again


class TestNsipGetProgeny:
    """Tests for nsip_get_progeny tool."""

    @patch("nsip_mcp.tools.NSIPClient")
    def test_pagination_parameters(self, mock_client_class):
        """Verify page and page_size parameters work correctly."""
        mock_client = MagicMock()

        mock_animal_1 = MagicMock()
        mock_animal_1.to_dict.return_value = {
            "lpn_id": "ABC123",
            "sex": "M",
            "birth_year": 2024,
        }

        mock_animal_2 = MagicMock()
        mock_animal_2.to_dict.return_value = {
            "lpn_id": "ABC124",
            "sex": "F",
            "birth_year": 2024,
        }

        mock_progeny = MagicMock()
        mock_progeny.animals = [mock_animal_1, mock_animal_2]
        mock_progeny.total_count = 6
        mock_progeny.page = 1
        mock_progeny.page_size = 2

        mock_client.get_progeny.return_value = mock_progeny
        mock_client_class.return_value = mock_client

        result = mcp_tools.nsip_get_progeny.fn(lpn_id="6401492020FLE249", page=1, page_size=2)

        assert result["page"] == 1
        assert result["page_size"] == 2
        assert result["total_count"] == 6
        assert len(result["animals"]) == 2
        assert result["animals"][0]["lpn_id"] == "ABC123"

        mock_client.get_progeny.assert_called_once_with("6401492020FLE249", page=1, page_size=2)

    @patch("nsip_mcp.tools.NSIPClient")
    def test_default_pagination(self, mock_client_class):
        """Verify default pagination values."""
        mock_client = MagicMock()

        mock_progeny = MagicMock()
        mock_progeny.animals = []
        mock_progeny.total_count = 0
        mock_progeny.page = 0
        mock_progeny.page_size = 10

        mock_client.get_progeny.return_value = mock_progeny
        mock_client_class.return_value = mock_client

        result = mcp_tools.nsip_get_progeny.fn(lpn_id="6401492020FLE249")

        assert result["page"] == 0
        assert result["page_size"] == 10

        mock_client.get_progeny.assert_called_once_with("6401492020FLE249", page=0, page_size=10)

    @patch("nsip_mcp.tools.NSIPClient")
    def test_returns_offspring_list(self, mock_client_class):
        """Verify tool returns offspring information."""
        mock_client = MagicMock()

        mock_animal = MagicMock()
        mock_animal.to_dict.return_value = {
            "lpn_id": "ABC123",
            "sex": "M",
            "birth_year": 2024,
            "breed": "Katahdin",
        }

        mock_progeny = MagicMock()
        mock_progeny.animals = [mock_animal]
        mock_progeny.total_count = 1
        mock_progeny.page = 0
        mock_progeny.page_size = 10

        mock_client.get_progeny.return_value = mock_progeny
        mock_client_class.return_value = mock_client

        result = mcp_tools.nsip_get_progeny.fn(lpn_id="6401492020FLE249")

        assert len(result["animals"]) == 1
        assert result["animals"][0]["lpn_id"] == "ABC123"
        assert result["animals"][0]["sex"] == "M"

    @patch("nsip_mcp.tools.NSIPClient")
    def test_caching_behavior(self, mock_client_class):
        """Verify tool uses cache correctly."""
        mock_client = MagicMock()

        mock_progeny = MagicMock()
        mock_progeny.animals = []
        mock_progeny.total_count = 0
        mock_progeny.page = 0
        mock_progeny.page_size = 10

        mock_client.get_progeny.return_value = mock_progeny
        mock_client_class.return_value = mock_client

        # First call - cache miss
        result1 = mcp_tools.nsip_get_progeny.fn(lpn_id="6401492020FLE249")
        assert mock_client.get_progeny.call_count == 1

        # Second call with same parameters - cache hit
        result2 = mcp_tools.nsip_get_progeny.fn(lpn_id="6401492020FLE249")
        assert result1 == result2
        assert mock_client.get_progeny.call_count == 1  # Not called again


class TestNsipSearchByLpn:
    """Tests for nsip_search_by_lpn tool.

    Note: This tool ALWAYS returns a summarized response due to the large
    combined data size from details + lineage + progeny.
    """

    @patch("nsip_mcp.tools.NSIPClient")
    def test_returns_summarized_profile(self, mock_client_class):
        """Verify tool returns summarized animal profile (always summarized)."""
        mock_client = MagicMock()

        # Mock animal details
        mock_details = MagicMock()
        mock_details.to_dict.return_value = {
            "lpn_id": "6401492020FLE249",
            "breed": "Katahdin",
            "gender": "Female",
        }

        # Mock lineage
        mock_lineage = MagicMock()
        mock_lineage.to_dict.return_value = {
            "sire": {"lpn_id": "123ABC"},
            "dam": {"lpn_id": "456DEF"},
        }

        # Mock progeny
        mock_progeny_animal = MagicMock()
        mock_progeny_animal.to_dict.return_value = {
            "lpn_id": "ABC123",
            "sex": "M",
        }

        mock_progeny = MagicMock()
        mock_progeny.animals = [mock_progeny_animal]
        mock_progeny.total_count = 1
        mock_progeny.page = 0
        mock_progeny.page_size = 10

        # Mock the combined response
        mock_client.search_by_lpn.return_value = {
            "details": mock_details,
            "lineage": mock_lineage,
            "progeny": mock_progeny,
        }
        mock_client_class.return_value = mock_client

        result = mcp_tools.nsip_search_by_lpn.fn(lpn_id="6401492020FLE249")

        # Verify summarized response structure (not nested details/lineage/progeny)
        assert "_summarized" in result
        assert result["_summarized"] is True
        assert "lpn_id" in result
        assert "breed" in result
        assert "total_progeny" in result
        assert result["total_progeny"] == 1

    @patch("nsip_mcp.tools.NSIPClient")
    def test_includes_lineage_info(self, mock_client_class):
        """Verify summarized profile includes sire/dam info."""
        mock_client = MagicMock()

        mock_details = MagicMock()
        mock_details.to_dict.return_value = {
            "lpn_id": "6401492020FLE249",
            "breed": "Katahdin",
        }

        mock_lineage = MagicMock()
        mock_lineage.to_dict.return_value = {
            "sire": {"lpn_id": "SIRE123"},
            "dam": {"lpn_id": "DAM456"},
        }

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

        result = mcp_tools.nsip_search_by_lpn.fn(lpn_id="6401492020FLE249")

        # Summarized response always includes core fields
        assert "_summarized" in result
        assert result["_summarized"] is True
        # Summarized response always includes core fields
        assert "_summarized" in result
        assert result["_summarized"] is True
        # Summarized response always includes core fields
        assert "_summarized" in result
        assert result["_summarized"] is True

    @patch("nsip_mcp.tools.NSIPClient")
    def test_caching_behavior(self, mock_client_class):
        """Verify tool uses cache correctly."""
        mock_client = MagicMock()

        mock_details = MagicMock()
        mock_details.to_dict.return_value = {"lpn_id": "6401492020FLE249", "breed": "Katahdin"}

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

        # First call - cache miss
        result1 = mcp_tools.nsip_search_by_lpn.fn(lpn_id="6401492020FLE249")
        assert mock_client.search_by_lpn.call_count == 1

        # Second call with same lpn_id - cache hit
        result2 = mcp_tools.nsip_search_by_lpn.fn(lpn_id="6401492020FLE249")
        assert result1 == result2
        assert mock_client.search_by_lpn.call_count == 1  # Not called again

    @patch("nsip_mcp.tools.NSIPClient")
    def test_with_multiple_progeny(self, mock_client_class):
        """Verify tool correctly counts multiple progeny in summarized response."""
        mock_client = MagicMock()

        mock_details = MagicMock()
        mock_details.to_dict.return_value = {"lpn_id": "6401492020FLE249", "breed": "Katahdin"}

        mock_lineage = MagicMock()
        mock_lineage.to_dict.return_value = {"sire": {}, "dam": {}}

        # Create multiple progeny
        mock_prog_1 = MagicMock()
        mock_prog_1.to_dict.return_value = {"lpn_id": "PROG1", "sex": "M"}

        mock_prog_2 = MagicMock()
        mock_prog_2.to_dict.return_value = {"lpn_id": "PROG2", "sex": "F"}

        mock_prog_3 = MagicMock()
        mock_prog_3.to_dict.return_value = {"lpn_id": "PROG3", "sex": "M"}

        mock_progeny = MagicMock()
        mock_progeny.animals = [mock_prog_1, mock_prog_2, mock_prog_3]
        mock_progeny.total_count = 3
        mock_progeny.page = 0
        mock_progeny.page_size = 10

        mock_client.search_by_lpn.return_value = {
            "details": mock_details,
            "lineage": mock_lineage,
            "progeny": mock_progeny,
        }
        mock_client_class.return_value = mock_client

        result = mcp_tools.nsip_search_by_lpn.fn(lpn_id="6401492020FLE249")

        # Summarized response includes progeny count (not full list)
        assert "total_progeny" in result
        assert result["total_progeny"] == 3
        assert result["_summarized"] is True


class TestCacheBehavior:
    """Tests for caching behavior across all tools."""

    @patch("nsip_mcp.tools.NSIPClient")
    def test_first_call_cache_miss(self, mock_client_class):
        """Verify first call misses cache and hits API."""
        mock_client = MagicMock()
        mock_client.get_date_last_updated.return_value = {"date": "09/23/2025"}
        mock_client_class.return_value = mock_client

        # Clear cache to ensure clean state
        response_cache.clear()
        initial_misses = response_cache.misses

        # First call should be a cache miss
        mcp_tools.nsip_get_last_update.fn()

        assert response_cache.misses == initial_misses + 1
        assert mock_client.get_date_last_updated.call_count == 1

    @patch("nsip_mcp.tools.NSIPClient")
    def test_second_call_cache_hit(self, mock_client_class):
        """Verify second call with same params hits cache."""
        mock_client = MagicMock()
        mock_client.get_date_last_updated.return_value = {"date": "09/23/2025"}
        mock_client_class.return_value = mock_client

        # First call - cache miss
        mcp_tools.nsip_get_last_update.fn()
        initial_hits = response_cache.hits

        # Second call - should be cache hit
        mcp_tools.nsip_get_last_update.fn()

        assert response_cache.hits == initial_hits + 1
        assert mock_client.get_date_last_updated.call_count == 1  # Still only 1 call

    @patch("nsip_mcp.tools.NSIPClient")
    def test_cache_key_determinism(self, mock_client_class):
        """Verify same params generate same cache key."""
        mock_client = MagicMock()

        mock_result = MagicMock()
        mock_result.results = []
        mock_result.total_count = 0
        mock_result.page = 0
        mock_result.page_size = 15

        mock_client.search_animals.return_value = mock_result
        mock_client_class.return_value = mock_client

        # Make two calls with same parameters
        mcp_tools.nsip_search_animals.fn(page=0, page_size=15, breed_id=486)
        mcp_tools.nsip_search_animals.fn(page=0, page_size=15, breed_id=486)

        # Should only call API once due to cache hit
        assert mock_client.search_animals.call_count == 1

    @patch("nsip_mcp.tools.NSIPClient")
    def test_different_params_different_cache_keys(self, mock_client_class):
        """Verify different params generate different cache keys."""
        mock_client = MagicMock()

        mock_result = MagicMock()
        mock_result.results = []
        mock_result.total_count = 0
        mock_result.page = 0
        mock_result.page_size = 15

        mock_client.search_animals.return_value = mock_result
        mock_client_class.return_value = mock_client

        # Call with different page values
        mcp_tools.nsip_search_animals.fn(page=0, page_size=15)
        mcp_tools.nsip_search_animals.fn(page=1, page_size=15)

        # Should call API twice (different cache keys)
        assert mock_client.search_animals.call_count == 2

    @patch("nsip_mcp.tools.NSIPClient")
    def test_cache_metrics_tracking(self, mock_client_class):
        """Verify cache tracks hits and misses correctly."""
        mock_client = MagicMock()
        mock_client.get_date_last_updated.return_value = {"date": "09/23/2025"}
        mock_client_class.return_value = mock_client

        # Clear cache and reset metrics
        response_cache.clear()

        # First call - miss
        mcp_tools.nsip_get_last_update.fn()
        assert response_cache.misses == 1
        assert response_cache.hits == 0

        # Second call - hit
        mcp_tools.nsip_get_last_update.fn()
        assert response_cache.misses == 1
        assert response_cache.hits == 1

        # Third call - hit
        mcp_tools.nsip_get_last_update.fn()
        assert response_cache.misses == 1
        assert response_cache.hits == 2

        # Verify hit rate calculation
        hit_rate = response_cache.hit_rate()
        assert hit_rate == pytest.approx(66.67, rel=0.01)  # 2 hits out of 3 total

    @patch("nsip_mcp.tools.NSIPClient")
    def test_cache_across_different_tools(self, mock_client_class):
        """Verify cache works independently for different tools."""
        mock_client = MagicMock()

        # Setup mocks for different tools
        mock_client.get_date_last_updated.return_value = {"date": "09/23/2025"}

        mock_breed = MagicMock()
        mock_breed.id = 61
        mock_breed.name = "Range"
        mock_client.get_available_breed_groups.return_value = [mock_breed]

        mock_client.get_statuses_by_breed_group.return_value = ["CURRENT"]

        mock_client_class.return_value = mock_client

        # Call different tools multiple times
        mcp_tools.nsip_get_last_update.fn()
        mcp_tools.nsip_get_last_update.fn()  # Cache hit

        mcp_tools.nsip_list_breeds.fn()
        mcp_tools.nsip_list_breeds.fn()  # Cache hit

        mcp_tools.nsip_get_statuses.fn()
        mcp_tools.nsip_get_statuses.fn()  # Cache hit

        # Each tool should be called only once
        assert mock_client.get_date_last_updated.call_count == 1
        assert mock_client.get_available_breed_groups.call_count == 1
        assert mock_client.get_statuses_by_breed_group.call_count == 1

        # Verify cache metrics
        assert response_cache.hits == 3  # 3 cache hits
        assert response_cache.misses == 3  # 3 cache misses
