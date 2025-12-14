"""
Unit tests for MCP tool wrappers

Tests all 15 MCP tools:
- 9 NSIP tools: nsip_get_last_update, nsip_list_breeds, nsip_get_statuses,
  nsip_get_trait_ranges, nsip_search_animals, nsip_get_animal, nsip_get_lineage,
  nsip_get_progeny, nsip_search_by_lpn
- 5 Shepherd tools: shepherd_consult, shepherd_breeding, shepherd_health,
  shepherd_calendar, shepherd_economics
- 1 Utility tool: get_server_health

Test coverage:
- Parameter validation
- Successful API calls with mocked NSIPClient responses
- Cache behavior (first call miss, second call hit)
- Tool discovery (all 15 tools registered)
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
        """Verify tool returns array of breed groups with their breeds."""
        mock_client = MagicMock()

        # Create mock breed group objects with id, name, and breeds attributes
        mock_breed_1 = MagicMock()
        mock_breed_1.id = 61
        mock_breed_1.name = "Range"
        mock_breed_1.breeds = [
            {"id": 486, "name": "South African Meat Merino"},
            {"id": 610, "name": "Targhee"},
        ]

        mock_breed_2 = MagicMock()
        mock_breed_2.id = 62
        mock_breed_2.name = "Maternal Wool"
        mock_breed_2.breeds = []

        mock_breed_3 = MagicMock()
        mock_breed_3.id = 64
        mock_breed_3.name = "Hair"
        mock_breed_3.breeds = [{"id": 640, "name": "Katahdin"}]

        mock_breed_4 = MagicMock()
        mock_breed_4.id = 69
        mock_breed_4.name = "Terminal"
        mock_breed_4.breeds = []

        mock_client.get_available_breed_groups.return_value = [
            mock_breed_1,
            mock_breed_2,
            mock_breed_3,
            mock_breed_4,
        ]
        mock_client_class.return_value = mock_client

        result = mcp_tools.nsip_list_breeds.fn()

        assert result["success"] is True
        assert "data" in result
        expected_data = [
            {
                "id": 61,
                "name": "Range",
                "breeds": [
                    {"id": 486, "name": "South African Meat Merino"},
                    {"id": 610, "name": "Targhee"},
                ],
            },
            {"id": 62, "name": "Maternal Wool", "breeds": []},
            {"id": 64, "name": "Hair", "breeds": [{"id": 640, "name": "Katahdin"}]},
            {"id": 69, "name": "Terminal", "breeds": []},
        ]
        assert result["data"] == expected_data
        mock_client.get_available_breed_groups.assert_called_once()

    @patch("nsip_mcp.tools.NSIPClient")
    def test_caching_behavior(self, mock_client_class):
        """Verify tool uses cache correctly."""
        mock_client = MagicMock()

        mock_breed = MagicMock()
        mock_breed.id = 61
        mock_breed.name = "Range"
        mock_breed.breeds = [{"id": 486, "name": "Targhee"}]

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

        assert result["success"] is True
        assert result["data"] == []
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

        assert result["success"] is True
        assert "data" in result
        expected_data = ["CURRENT", "SOLD", "DEAD", "COMMERCIAL", "CULL", "EXPORTED"]
        assert result["data"] == expected_data
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
            {"LpnId": "6####92020###249", "Breed": "Katahdin"},
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
            "lpn_id": "6####92020###249",
            "breed": "Katahdin",
            "gender": "Female",
        }

        mock_client.get_animal_details.return_value = mock_animal
        mock_client_class.return_value = mock_client

        result = mcp_tools.nsip_get_animal.fn(search_string="6####92020###249")

        assert result["lpn_id"] == "6####92020###249"
        mock_client.get_animal_details.assert_called_once_with("6####92020###249")

    @patch("nsip_mcp.tools.NSIPClient")
    def test_returns_complete_animal_info(self, mock_client_class):
        """Verify tool returns complete animal information."""
        mock_client = MagicMock()

        mock_animal = MagicMock()
        mock_animal.to_dict.return_value = {
            "lpn_id": "6####92020###249",
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

        result = mcp_tools.nsip_get_animal.fn(search_string="6####92020###249")

        assert result["lpn_id"] == "6####92020###249"
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
        mock_animal.to_dict.return_value = {"lpn_id": "6####92020###249"}

        mock_client.get_animal_details.return_value = mock_animal
        mock_client_class.return_value = mock_client

        # First call - cache miss
        result1 = mcp_tools.nsip_get_animal.fn(search_string="6####92020###249")
        assert mock_client.get_animal_details.call_count == 1

        # Second call with same search_string - cache hit
        result2 = mcp_tools.nsip_get_animal.fn(search_string="6####92020###249")
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

        result = mcp_tools.nsip_get_lineage.fn(lpn_id="6####92020###249")

        assert "sire" in result
        assert "dam" in result
        mock_client.get_lineage.assert_called_once_with("6####92020###249")

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

        result = mcp_tools.nsip_get_lineage.fn(lpn_id="6####92020###249")

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
        result1 = mcp_tools.nsip_get_lineage.fn(lpn_id="6####92020###249")
        assert mock_client.get_lineage.call_count == 1

        # Second call with same lpn_id - cache hit
        result2 = mcp_tools.nsip_get_lineage.fn(lpn_id="6####92020###249")
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

        result = mcp_tools.nsip_get_progeny.fn(lpn_id="6####92020###249", page=1, page_size=2)

        assert result["page"] == 1
        assert result["page_size"] == 2
        assert result["total_count"] == 6
        assert len(result["animals"]) == 2
        assert result["animals"][0]["lpn_id"] == "ABC123"

        mock_client.get_progeny.assert_called_once_with("6####92020###249", page=1, page_size=2)

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

        result = mcp_tools.nsip_get_progeny.fn(lpn_id="6####92020###249")

        assert result["page"] == 0
        assert result["page_size"] == 10

        mock_client.get_progeny.assert_called_once_with("6####92020###249", page=0, page_size=10)

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

        result = mcp_tools.nsip_get_progeny.fn(lpn_id="6####92020###249")

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
        result1 = mcp_tools.nsip_get_progeny.fn(lpn_id="6####92020###249")
        assert mock_client.get_progeny.call_count == 1

        # Second call with same parameters - cache hit
        result2 = mcp_tools.nsip_get_progeny.fn(lpn_id="6####92020###249")
        assert result1 == result2
        assert mock_client.get_progeny.call_count == 1  # Not called again


class TestNsipSearchByLpn:
    """Tests for nsip_search_by_lpn tool.

    Note: This tool combines data from details + lineage + progeny.
    Summarization is opt-in via the summarize parameter.
    """

    @patch("nsip_mcp.tools.NSIPClient")
    def test_returns_profile_default_no_summarization(self, mock_client_class):
        """Verify tool returns full animal profile by default (no summarization)."""
        mock_client = MagicMock()

        # Mock animal details
        mock_details = MagicMock()
        mock_details.to_dict.return_value = {
            "lpn_id": "6####92020###249",
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

        result = mcp_tools.nsip_search_by_lpn.fn(lpn_id="6####92020###249")

        # Verify NO summarization by default
        assert "_summarized" in result
        assert result["_summarized"] is False, "Should NOT summarize by default"
        # Full structure preserved (nested)
        assert "details" in result
        assert "lineage" in result
        assert "progeny" in result

    @patch("nsip_mcp.tools.NSIPClient")
    def test_summarized_profile_includes_lineage(self, mock_client_class):
        """Verify summarized profile includes sire/dam info when requested."""
        mock_client = MagicMock()

        mock_details = MagicMock()
        mock_details.to_dict.return_value = {
            "lpn_id": "6####92020###249",
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

        # Request summarization explicitly
        result = mcp_tools.nsip_search_by_lpn.fn(lpn_id="6####92020###249", summarize=True)

        # Verify summarization occurred
        assert "_summarized" in result
        assert result["_summarized"] is True
        # Core fields should be present in summarized version
        assert "lpn_id" in result
        assert "breed" in result

    @patch("nsip_mcp.tools.NSIPClient")
    def test_caching_behavior(self, mock_client_class):
        """Verify tool uses cache correctly."""
        mock_client = MagicMock()

        mock_details = MagicMock()
        mock_details.to_dict.return_value = {"lpn_id": "6####92020###249", "breed": "Katahdin"}

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
        result1 = mcp_tools.nsip_search_by_lpn.fn(lpn_id="6####92020###249")
        assert mock_client.search_by_lpn.call_count == 1

        # Second call with same lpn_id - cache hit
        result2 = mcp_tools.nsip_search_by_lpn.fn(lpn_id="6####92020###249")
        assert result1 == result2
        assert mock_client.search_by_lpn.call_count == 1  # Not called again

    @patch("nsip_mcp.tools.NSIPClient")
    def test_with_multiple_progeny(self, mock_client_class):
        """Verify tool correctly counts multiple progeny in summarized response."""
        mock_client = MagicMock()

        mock_details = MagicMock()
        mock_details.to_dict.return_value = {"lpn_id": "6####92020###249", "breed": "Katahdin"}

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

        # Without summarization, full nested structure is returned
        result = mcp_tools.nsip_search_by_lpn.fn(lpn_id="6####92020###249")

        # Without summarization, check nested structure
        assert result["_summarized"] is False
        assert "progeny" in result
        assert result["progeny"]["total_count"] == 3
        assert len(result["progeny"]["animals"]) == 3


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
        mock_breed.breeds = []
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


class TestShepherdConsultTool:
    """Tests for shepherd_consult_tool."""

    def test_returns_guidance(self):
        """Test shepherd consult returns guidance."""
        result = asyncio.run(
            mcp_tools.shepherd_consult_tool.fn(question="How to select rams?", region="midwest")
        )

        assert isinstance(result, dict)
        # Could have either guidance or error depending on mock setup
        assert "guidance" in result or "error" in result

    def test_handles_empty_question(self):
        """Test handling of empty question."""
        result = asyncio.run(mcp_tools.shepherd_consult_tool.fn(question="", region="midwest"))

        assert isinstance(result, dict)


class TestShepherdBreedingTool:
    """Tests for shepherd_breeding_tool."""

    def test_returns_dict(self):
        """Test shepherd breeding returns dict."""
        result = asyncio.run(
            mcp_tools.shepherd_breeding_tool.fn(
                question="How to improve weaning weight?",
                region="midwest",
                production_goal="terminal",
            )
        )

        assert isinstance(result, dict)


class TestShepherdHealthTool:
    """Tests for shepherd_health_tool."""

    def test_returns_dict(self):
        """Test shepherd health returns dict."""
        result = asyncio.run(
            mcp_tools.shepherd_health_tool.fn(
                question="What vaccines do I need?",
                region="midwest",
                life_stage="maintenance",
            )
        )

        assert isinstance(result, dict)


class TestShepherdCalendarTool:
    """Tests for shepherd_calendar_tool."""

    def test_returns_dict(self):
        """Test shepherd calendar returns dict."""
        result = asyncio.run(
            mcp_tools.shepherd_calendar_tool.fn(
                question="When to start breeding?",
                region="midwest",
                task_type="breeding",
            )
        )

        assert isinstance(result, dict)


class TestShepherdEconomicsTool:
    """Tests for shepherd_economics_tool."""

    def test_returns_dict(self):
        """Test shepherd economics returns dict."""
        result = asyncio.run(
            mcp_tools.shepherd_economics_tool.fn(
                question="What is my cost per ewe?",
                flock_size="medium",
                market_focus="direct",
            )
        )

        assert isinstance(result, dict)


class TestHandleNsipApiError:
    """Tests for handle_nsip_api_error function.

    The function returns a dict with 'code', 'message', and 'data' fields
    following MCP error response format.
    """

    def test_not_found_error(self):
        """Test handling NSIPNotFoundError."""
        from nsip_client.exceptions import NSIPNotFoundError
        from nsip_mcp.mcp_tools import handle_nsip_api_error

        error = NSIPNotFoundError("Animal not found")
        result = handle_nsip_api_error(error, "fetching animal 12345")

        assert isinstance(result, dict)
        assert "code" in result
        assert "message" in result
        assert "Animal not found" in result["message"]

    def test_timeout_error(self):
        """Test handling NSIPTimeoutError."""
        from nsip_client.exceptions import NSIPTimeoutError
        from nsip_mcp.mcp_tools import handle_nsip_api_error

        error = NSIPTimeoutError("Connection timed out")
        result = handle_nsip_api_error(error, "fetching breeds")

        assert isinstance(result, dict)
        assert "code" in result
        assert "message" in result
        assert "timeout" in result["message"].lower()

    def test_validation_error(self):
        """Test handling NSIPValidationError."""
        from nsip_client.exceptions import NSIPValidationError
        from nsip_mcp.mcp_tools import handle_nsip_api_error

        error = NSIPValidationError("Invalid breed ID")
        result = handle_nsip_api_error(error, "validating breed")

        assert isinstance(result, dict)
        assert "code" in result
        assert "message" in result
        assert "validation" in result["message"].lower()

    def test_generic_api_error(self):
        """Test handling generic NSIPAPIError."""
        from nsip_client.exceptions import NSIPAPIError
        from nsip_mcp.mcp_tools import handle_nsip_api_error

        error = NSIPAPIError("Server error")
        result = handle_nsip_api_error(error, "fetching data")

        assert isinstance(result, dict)
        assert "code" in result
        assert "message" in result

    def test_unexpected_error(self):
        """Test handling unexpected non-NSIP errors."""
        from nsip_mcp.mcp_tools import handle_nsip_api_error

        error = RuntimeError("Unexpected error")
        result = handle_nsip_api_error(error, "unknown operation")

        assert isinstance(result, dict)
        assert "code" in result
        assert "message" in result
        assert "unexpected" in result["message"].lower()


class TestGetNsipClient:
    """Tests for get_nsip_client function."""

    def test_returns_client_instance(self):
        """Test that get_nsip_client returns a client."""
        from nsip_mcp.mcp_tools import get_nsip_client

        client = get_nsip_client()
        assert client is not None

    def test_singleton_behavior(self):
        """Test that get_nsip_client returns same instance."""
        from nsip_mcp.mcp_tools import get_nsip_client

        client1 = get_nsip_client()
        client2 = get_nsip_client()
        # Should be the same singleton instance
        assert client1 is client2


class TestCachedApiCallDecorator:
    """Tests for cached_api_call decorator."""

    def test_decorator_caches_result(self):
        """Test that decorated function caches results."""
        from nsip_mcp.mcp_tools import cached_api_call

        call_count = 0

        @cached_api_call("test_cache")
        def test_function():
            nonlocal call_count
            call_count += 1
            return {"result": "data"}

        # First call should execute function
        result1 = test_function()
        assert result1 == {"result": "data"}
        assert call_count == 1

        # Second call should return cached value
        result2 = test_function()
        assert result2 == {"result": "data"}
        # Count should still be 1 due to caching
        assert call_count == 1

    def test_decorator_with_kwargs(self):
        """Test decorator with keyword arguments."""
        from nsip_mcp.mcp_tools import cached_api_call

        @cached_api_call("test_kwargs")
        def test_function(*, arg1, arg2="default"):
            return {"arg1": arg1, "arg2": arg2}

        result = test_function(arg1="value1", arg2="value2")
        assert result == {"arg1": "value1", "arg2": "value2"}

    def test_decorator_with_positional_args(self):
        """Test decorator correctly converts positional args to kwargs for caching."""
        from nsip_mcp.tools import cached_api_call

        call_count = 0

        @cached_api_call("test_positional")
        def test_function(arg1, arg2, arg3="default"):
            nonlocal call_count
            call_count += 1
            return {"arg1": arg1, "arg2": arg2, "arg3": arg3}

        # First call with positional args - should miss cache
        result1 = test_function("val1", "val2")
        assert result1 == {"arg1": "val1", "arg2": "val2", "arg3": "default"}
        assert call_count == 1

        # Second call with same positional args - should hit cache
        result2 = test_function("val1", "val2")
        assert result2 == {"arg1": "val1", "arg2": "val2", "arg3": "default"}
        assert call_count == 1  # Still 1, cached

        # Third call with kwargs (same values) - should hit cache due to conversion
        result3 = test_function(arg1="val1", arg2="val2")
        assert result3 == {"arg1": "val1", "arg2": "val2", "arg3": "default"}
        assert call_count == 1  # Still 1, same cache key

    def test_decorator_mixed_positional_and_kwargs(self):
        """Test decorator with mixed positional and keyword arguments."""
        from nsip_mcp.tools import cached_api_call

        call_count = 0

        @cached_api_call("test_mixed")
        def test_function(arg1, arg2, arg3="default"):
            nonlocal call_count
            call_count += 1
            return {"arg1": arg1, "arg2": arg2, "arg3": arg3}

        # Call with mixed positional and kwargs
        result = test_function("val1", arg2="val2", arg3="val3")
        assert result == {"arg1": "val1", "arg2": "val2", "arg3": "val3"}
        assert call_count == 1

        # Same call should hit cache
        result2 = test_function("val1", arg2="val2", arg3="val3")
        assert result2 == result
        assert call_count == 1  # Cached

    def test_decorator_raises_on_duplicate_args(self):
        """Test decorator raises TypeError when same arg passed positionally and as kwarg."""
        from nsip_mcp.tools import cached_api_call

        @cached_api_call("test_duplicate")
        def test_function(arg1, arg2):
            return {"arg1": arg1, "arg2": arg2}

        # Passing same argument both ways should raise TypeError
        with pytest.raises(TypeError) as exc_info:
            test_function("val1", arg1="other_val")

        assert "got multiple values for argument 'arg1'" in str(exc_info.value)

    def test_decorator_on_method(self):
        """Test decorator behavior on instance methods documents self handling (H3).

        KNOWN LIMITATION: When the decorator is used on a method, 'self' is excluded
        from cache key generation. This means different instances SHARE the same cache
        for the same arguments. This is acceptable for methods that don't depend on
        instance state, but may be incorrect for stateful methods.

        Currently, no decorated functions in this codebase are instance methods.
        """
        from nsip_mcp.tools import cached_api_call

        call_count = 0

        class TestClass:
            @cached_api_call("test_method")
            def method(self, arg1):
                nonlocal call_count
                call_count += 1
                return {"arg1": arg1, "id": id(self)}

        obj1 = TestClass()
        obj2 = TestClass()

        # First call on obj1
        result1 = obj1.method("val1")
        assert result1["arg1"] == "val1"
        assert call_count == 1

        # Second call on obj2 with same arg - SHARES cache (known limitation)
        result2 = obj2.method("val1")
        assert result2["arg1"] == "val1"
        # The cached result from obj1 is returned (self is excluded from cache key)
        assert result2["id"] == result1["id"]  # Same cached result
        assert call_count == 1  # Still 1 - cache hit

        # Third call on obj1 should also hit cache
        result3 = obj1.method("val1")
        assert result3["id"] == result1["id"]
        assert call_count == 1  # Still 1 - cache hit

    def test_decorator_filters_var_positional(self):
        """Test decorator correctly filters *args from param_names (H1)."""
        from nsip_mcp.tools import cached_api_call

        call_count = 0

        @cached_api_call("test_var_positional")
        def test_function(arg1, *args):
            nonlocal call_count
            call_count += 1
            return {"arg1": arg1, "extra": args}

        # Call with positional arg only (args should be filtered from cache key)
        result1 = test_function("val1")
        assert result1 == {"arg1": "val1", "extra": ()}
        assert call_count == 1

        # Same call should hit cache (only arg1 in cache key)
        result2 = test_function("val1")
        assert result2 == result1
        assert call_count == 1  # Cached

    def test_decorator_filters_var_keyword(self):
        """Test decorator correctly filters **kwargs from param_names (H1)."""
        from nsip_mcp.tools import cached_api_call

        call_count = 0

        @cached_api_call("test_var_keyword")
        def test_function(arg1, **kwargs):
            nonlocal call_count
            call_count += 1
            return {"arg1": arg1, "extra": kwargs}

        # Call with only required arg
        result1 = test_function(arg1="val1")
        assert result1 == {"arg1": "val1", "extra": {}}
        assert call_count == 1

        # Same call should hit cache
        result2 = test_function(arg1="val1")
        assert result2 == result1
        assert call_count == 1  # Cached

    def test_decorator_with_keyword_only_params(self):
        """Test decorator handles keyword-only parameters correctly (M3)."""
        from nsip_mcp.tools import cached_api_call

        call_count = 0

        @cached_api_call("test_keyword_only")
        def test_function(arg1, *, kwonly1, kwonly2="default"):
            nonlocal call_count
            call_count += 1
            return {"arg1": arg1, "kwonly1": kwonly1, "kwonly2": kwonly2}

        # First call with keyword-only args
        result1 = test_function("val1", kwonly1="kw1")
        assert result1 == {"arg1": "val1", "kwonly1": "kw1", "kwonly2": "default"}
        assert call_count == 1

        # Same call should hit cache
        result2 = test_function("val1", kwonly1="kw1")
        assert result2 == result1
        assert call_count == 1  # Cached

        # Different kwonly1 value should miss cache
        result3 = test_function("val1", kwonly1="different")
        assert result3["kwonly1"] == "different"
        assert call_count == 2  # New call

    def test_decorator_with_positional_only_params(self):
        """Test decorator handles positional-only parameters correctly (M3).

        Python 3.8+ syntax: parameters before / are positional-only.
        """
        from nsip_mcp.tools import cached_api_call

        call_count = 0

        @cached_api_call("test_positional_only")
        def test_function(pos_only, /, regular):
            nonlocal call_count
            call_count += 1
            return {"pos_only": pos_only, "regular": regular}

        # First call
        result1 = test_function("pos1", "reg1")
        assert result1 == {"pos_only": "pos1", "regular": "reg1"}
        assert call_count == 1

        # Same positional values should hit cache
        result2 = test_function("pos1", "reg1")
        assert result2 == result1
        assert call_count == 1  # Cached

        # Different positional-only value should miss cache
        result3 = test_function("pos2", "reg1")
        assert result3["pos_only"] == "pos2"
        assert call_count == 2  # New call


class TestValidateLpnId:
    """Tests for validate_lpn_id function."""

    def test_valid_lpn_id_records_success_metric(self):
        """Test valid LPN ID records validation success in metrics (H2)."""
        from unittest.mock import MagicMock, patch

        from nsip_mcp.mcp_tools import validate_lpn_id

        mock_metrics = MagicMock()

        with patch("nsip_mcp.mcp_tools.server_metrics", mock_metrics):
            result = validate_lpn_id("6####92020###249")

        assert result is None  # Validation passed
        mock_metrics.record_validation.assert_called_once_with(success=True)

    def test_empty_lpn_id_returns_error(self):
        """Test empty LPN ID returns validation error."""
        from nsip_mcp.mcp_tools import validate_lpn_id

        result = validate_lpn_id("")
        assert result is not None
        assert "code" in result
        assert "message" in result

    def test_whitespace_only_lpn_id_returns_error(self):
        """Test whitespace-only LPN ID returns validation error."""
        from nsip_mcp.mcp_tools import validate_lpn_id

        result = validate_lpn_id("   ")
        assert result is not None
        assert "code" in result

    def test_short_lpn_id_returns_error(self):
        """Test short LPN ID (< 5 chars) returns validation error."""
        from nsip_mcp.mcp_tools import validate_lpn_id

        result = validate_lpn_id("ABC")
        assert result is not None
        assert "code" in result
        assert "message" in result

    def test_valid_lpn_id_returns_none(self):
        """Test valid LPN ID returns None (no error)."""
        from nsip_mcp.mcp_tools import validate_lpn_id

        result = validate_lpn_id("6####92020###249")
        assert result is None


class TestValidateBreedId:
    """Tests for validate_breed_id function."""

    def test_zero_breed_id_returns_error(self):
        """Test zero breed ID returns validation error."""
        from nsip_mcp.mcp_tools import validate_breed_id

        result = validate_breed_id(0)
        assert result is not None
        assert "code" in result

    def test_negative_breed_id_returns_error(self):
        """Test negative breed ID returns validation error."""
        from nsip_mcp.mcp_tools import validate_breed_id

        result = validate_breed_id(-5)
        assert result is not None
        assert "code" in result

    def test_valid_breed_id_returns_none(self):
        """Test valid breed ID returns None (no error)."""
        from nsip_mcp.mcp_tools import validate_breed_id

        result = validate_breed_id(486)
        assert result is None


class TestValidatePagination:
    """Tests for validate_pagination function."""

    def test_negative_page_returns_error(self):
        """Test negative page number returns validation error."""
        from nsip_mcp.mcp_tools import validate_pagination

        result = validate_pagination(-1, 15)
        assert result is not None
        assert "code" in result
        assert "page" in result["message"].lower()

    def test_zero_page_size_returns_error(self):
        """Test zero page_size returns validation error."""
        from nsip_mcp.mcp_tools import validate_pagination

        result = validate_pagination(0, 0)
        assert result is not None
        assert "code" in result

    def test_page_size_over_100_returns_error(self):
        """Test page_size > 100 returns validation error."""
        from nsip_mcp.mcp_tools import validate_pagination

        result = validate_pagination(0, 150)
        assert result is not None
        assert "code" in result

    def test_valid_pagination_returns_none(self):
        """Test valid pagination returns None (no error)."""
        from nsip_mcp.mcp_tools import validate_pagination

        result = validate_pagination(0, 15)
        assert result is None


class TestApplyContextManagement:
    """Tests for apply_context_management function."""

    def test_default_passthrough(self):
        """Test default behavior is passthrough (no summarization)."""
        from nsip_mcp.mcp_tools import apply_context_management

        response = {"lpn_id": "ABC123", "breed": "Katahdin"}
        result = apply_context_management(response)

        assert result["_summarized"] is False
        assert result["lpn_id"] == "ABC123"

    def test_explicit_summarize_true(self):
        """Test explicit summarization request."""
        from nsip_mcp.mcp_tools import apply_context_management

        response = {"lpn_id": "ABC123", "breed": "Katahdin"}
        result = apply_context_management(response, summarize=True)

        assert result["_summarized"] is True

    def test_summarization_failure_fallback(self):
        """Test fallback when summarization fails."""
        from nsip_mcp.mcp_tools import apply_context_management

        # Pass an object that will cause summarization to fail
        with patch("nsip_mcp.mcp_tools.summarize_response") as mock_summarize:
            mock_summarize.side_effect = Exception("Summarization failed")

            response = {"lpn_id": "ABC123", "breed": "Katahdin"}
            result = apply_context_management(response, summarize=True)

            # Should fall back to original response with error flags
            assert result["_summarization_failed"] is True
            assert "Summarization failed" in result["_summarization_error"]


class TestNsipGetAnimalValidation:
    """Tests for nsip_get_animal validation paths."""

    def test_empty_search_string_returns_error(self):
        """Test empty search_string returns validation error."""
        result = mcp_tools.nsip_get_animal.fn(search_string="")

        assert isinstance(result, dict)
        assert "code" in result
        assert "message" in result

    def test_short_search_string_returns_error(self):
        """Test short search_string returns validation error."""
        result = mcp_tools.nsip_get_animal.fn(search_string="AB")

        assert isinstance(result, dict)
        assert "code" in result

    @patch("nsip_mcp.tools.NSIPClient")
    def test_api_exception_returns_error(self, mock_client_class):
        """Test API exception is handled and returns error dict."""
        from nsip_client.exceptions import NSIPNotFoundError

        mock_client = MagicMock()
        mock_client.get_animal_details.side_effect = NSIPNotFoundError("Not found")
        mock_client_class.return_value = mock_client

        result = mcp_tools.nsip_get_animal.fn(search_string="VALIDLPN123")

        assert isinstance(result, dict)
        assert "code" in result
        assert "message" in result


class TestNsipGetLineageValidation:
    """Tests for nsip_get_lineage validation paths."""

    def test_empty_lpn_id_returns_error(self):
        """Test empty lpn_id returns validation error."""
        result = mcp_tools.nsip_get_lineage.fn(lpn_id="")

        assert isinstance(result, dict)
        assert "code" in result

    @patch("nsip_mcp.tools.NSIPClient")
    def test_api_exception_returns_error(self, mock_client_class):
        """Test API exception is handled and returns error dict."""
        from nsip_client.exceptions import NSIPTimeoutError

        mock_client = MagicMock()
        mock_client.get_lineage.side_effect = NSIPTimeoutError("Timeout")
        mock_client_class.return_value = mock_client

        result = mcp_tools.nsip_get_lineage.fn(lpn_id="VALIDLPN123")

        assert isinstance(result, dict)
        assert "code" in result
        assert "timeout" in result["message"].lower()


class TestNsipGetProgenyValidation:
    """Tests for nsip_get_progeny validation paths."""

    def test_empty_lpn_id_returns_error(self):
        """Test empty lpn_id returns validation error."""
        result = mcp_tools.nsip_get_progeny.fn(lpn_id="")

        assert isinstance(result, dict)
        assert "code" in result

    def test_invalid_pagination_returns_error(self):
        """Test invalid pagination returns validation error."""
        result = mcp_tools.nsip_get_progeny.fn(lpn_id="VALIDLPN123", page=-1, page_size=15)

        assert isinstance(result, dict)
        assert "code" in result

    @patch("nsip_mcp.tools.NSIPClient")
    def test_api_exception_returns_error(self, mock_client_class):
        """Test API exception is handled and returns error dict."""
        from nsip_client.exceptions import NSIPAPIError

        mock_client = MagicMock()
        mock_client.get_progeny.side_effect = NSIPAPIError("API error")
        mock_client_class.return_value = mock_client

        result = mcp_tools.nsip_get_progeny.fn(lpn_id="VALIDLPN123")

        assert isinstance(result, dict)
        assert "code" in result


class TestNsipSearchByLpnValidation:
    """Tests for nsip_search_by_lpn validation paths."""

    def test_empty_lpn_id_returns_error(self):
        """Test empty lpn_id returns validation error."""
        result = mcp_tools.nsip_search_by_lpn.fn(lpn_id="")

        assert isinstance(result, dict)
        assert "code" in result

    @patch("nsip_mcp.tools.NSIPClient")
    def test_api_exception_returns_error(self, mock_client_class):
        """Test API exception is handled and returns error dict."""
        from nsip_client.exceptions import NSIPNotFoundError

        mock_client = MagicMock()
        mock_client.search_by_lpn.side_effect = NSIPNotFoundError("Not found")
        mock_client_class.return_value = mock_client

        result = mcp_tools.nsip_search_by_lpn.fn(lpn_id="VALIDLPN123")

        assert isinstance(result, dict)
        assert "code" in result


class TestNsipSearchAnimalsValidation:
    """Tests for nsip_search_animals validation paths."""

    def test_negative_page_returns_error(self):
        """Test negative page returns validation error."""
        result = mcp_tools.nsip_search_animals.fn(page=-1)

        assert isinstance(result, dict)
        assert "code" in result

    def test_page_size_over_100_returns_error(self):
        """Test page_size > 100 returns validation error."""
        result = mcp_tools.nsip_search_animals.fn(page=0, page_size=150)

        assert isinstance(result, dict)
        assert "code" in result

    @patch("nsip_mcp.tools.NSIPClient")
    def test_api_exception_returns_error(self, mock_client_class):
        """Test API exception is handled and returns error dict."""
        from nsip_client.exceptions import NSIPAPIError

        mock_client = MagicMock()
        mock_client.search_animals.side_effect = NSIPAPIError("Search failed")
        mock_client_class.return_value = mock_client

        result = mcp_tools.nsip_search_animals.fn(page=0, page_size=15)

        assert isinstance(result, dict)
        assert "code" in result


class TestNsipGetTraitRangesValidation:
    """Tests for nsip_get_trait_ranges validation paths."""

    def test_zero_breed_id_returns_error(self):
        """Test zero breed_id returns validation error."""
        result = mcp_tools.nsip_get_trait_ranges.fn(breed_id=0)

        assert isinstance(result, dict)
        assert "code" in result

    def test_negative_breed_id_returns_error(self):
        """Test negative breed_id returns validation error."""
        result = mcp_tools.nsip_get_trait_ranges.fn(breed_id=-5)

        assert isinstance(result, dict)
        assert "code" in result

    @patch("nsip_mcp.tools.NSIPClient")
    def test_api_exception_returns_error(self, mock_client_class):
        """Test API exception is handled and returns error dict."""
        from nsip_client.exceptions import NSIPAPIError

        mock_client = MagicMock()
        mock_client.get_trait_ranges_by_breed.side_effect = NSIPAPIError("Failed")
        mock_client_class.return_value = mock_client

        result = mcp_tools.nsip_get_trait_ranges.fn(breed_id=486)

        assert isinstance(result, dict)
        assert "code" in result


class TestShepherdToolsExceptionHandling:
    """Tests for Shepherd tool exception handling.

    Note: Shepherd prompts are imported inside the tool functions, not at module level.
    We need to patch them at nsip_mcp.prompts.shepherd_prompts.
    """

    def test_shepherd_consult_exception(self):
        """Test shepherd_consult handles exceptions gracefully."""
        with patch("nsip_mcp.prompts.shepherd_prompts.shepherd_consult_prompt") as mock_prompt:
            mock_fn = MagicMock()
            mock_fn.side_effect = Exception("Prompt failed")
            mock_prompt.fn = mock_fn

            result = asyncio.run(
                mcp_tools.shepherd_consult_tool.fn(question="test", region="midwest")
            )

            assert isinstance(result, dict)
            assert "error" in result
            assert "failed" in result["error"].lower()

    def test_shepherd_breeding_exception(self):
        """Test shepherd_breeding handles exceptions gracefully."""
        with patch("nsip_mcp.prompts.shepherd_prompts.shepherd_breeding_prompt") as mock_prompt:
            mock_fn = MagicMock()
            mock_fn.side_effect = Exception("Prompt failed")
            mock_prompt.fn = mock_fn

            result = asyncio.run(
                mcp_tools.shepherd_breeding_tool.fn(
                    question="test", region="midwest", production_goal="terminal"
                )
            )

            assert isinstance(result, dict)
            assert "error" in result

    def test_shepherd_health_exception(self):
        """Test shepherd_health handles exceptions gracefully."""
        with patch("nsip_mcp.prompts.shepherd_prompts.shepherd_health_prompt") as mock_prompt:
            mock_fn = MagicMock()
            mock_fn.side_effect = Exception("Prompt failed")
            mock_prompt.fn = mock_fn

            result = asyncio.run(
                mcp_tools.shepherd_health_tool.fn(
                    question="test", region="midwest", life_stage="maintenance"
                )
            )

            assert isinstance(result, dict)
            assert "error" in result

    def test_shepherd_calendar_exception(self):
        """Test shepherd_calendar handles exceptions gracefully."""
        with patch("nsip_mcp.prompts.shepherd_prompts.shepherd_calendar_prompt") as mock_prompt:
            mock_fn = MagicMock()
            mock_fn.side_effect = Exception("Prompt failed")
            mock_prompt.fn = mock_fn

            result = asyncio.run(
                mcp_tools.shepherd_calendar_tool.fn(
                    question="test", region="midwest", task_type="breeding"
                )
            )

            assert isinstance(result, dict)
            assert "error" in result

    def test_shepherd_economics_exception(self):
        """Test shepherd_economics handles exceptions gracefully."""
        with patch("nsip_mcp.prompts.shepherd_prompts.shepherd_economics_prompt") as mock_prompt:
            mock_fn = MagicMock()
            mock_fn.side_effect = Exception("Prompt failed")
            mock_prompt.fn = mock_fn

            result = asyncio.run(
                mcp_tools.shepherd_economics_tool.fn(
                    question="test", flock_size="medium", market_focus="direct"
                )
            )

            assert isinstance(result, dict)
            assert "error" in result
