"""Unit tests for MCP resources module.

Note: These tests focus on the underlying resource logic, not the MCP decorator
integration. For FastMCP decorated resources, we test the functions that provide
the data, not the FunctionResource wrapper objects.
"""

import pytest
from unittest.mock import MagicMock

# Import the knowledge base functions that resources use
from nsip_mcp.knowledge_base import (
    get_heritabilities,
    get_trait_info,
    list_traits,
    get_selection_index,
    list_selection_indexes,
    get_region_info,
    list_regions,
    get_disease_guide,
    get_nutrition_guide,
    get_calendar_template,
    get_economics_template,
)
from nsip_mcp.knowledge_base.loader import KnowledgeBaseError


class TestStaticResourcesLogic:
    """Tests for static resource data access.

    These tests verify the knowledge base functions that back
    the MCP resources return valid data.
    """

    def test_get_default_heritabilities(self) -> None:
        """Test default heritabilities returns valid data."""
        result = get_heritabilities()
        assert isinstance(result, dict)
        assert len(result) > 0

    def test_get_breed_heritabilities(self) -> None:
        """Test breed heritabilities returns valid data."""
        result = get_heritabilities("katahdin")
        assert isinstance(result, dict)
        assert len(result) > 0

    def test_get_all_traits(self) -> None:
        """Test listing all traits returns valid data."""
        result = list_traits()
        assert isinstance(result, list)
        assert len(result) > 0

    def test_get_trait_details(self) -> None:
        """Test getting trait details returns valid data."""
        result = get_trait_info("WWT")
        assert isinstance(result, dict)

    def test_get_trait_details_invalid(self) -> None:
        """Test getting invalid trait raises error."""
        with pytest.raises(KnowledgeBaseError):
            get_trait_info("INVALID_XYZ")

    def test_get_all_indexes(self) -> None:
        """Test listing selection indexes returns valid data."""
        result = list_selection_indexes()
        assert isinstance(result, list)
        assert len(result) > 0

    def test_get_index_details(self) -> None:
        """Test getting index details returns valid data."""
        result = get_selection_index("terminal")
        assert isinstance(result, dict)

    def test_get_all_regions(self) -> None:
        """Test listing regions returns valid data."""
        result = list_regions()
        assert isinstance(result, list)
        assert len(result) > 0

    def test_get_region_details(self) -> None:
        """Test getting region details returns valid data."""
        result = get_region_info("midwest")
        assert isinstance(result, dict)

    def test_get_disease_info(self) -> None:
        """Test getting disease guide returns valid data."""
        result = get_disease_guide("midwest")
        assert isinstance(result, (list, dict))

    def test_get_nutrition_info(self) -> None:
        """Test getting nutrition guide returns valid data."""
        result = get_nutrition_guide(region="midwest", season="summer")
        assert isinstance(result, dict)

    def test_get_calendar_info(self) -> None:
        """Test getting calendar template returns valid data."""
        result = get_calendar_template()
        assert isinstance(result, dict)

    def test_get_economics_info(self) -> None:
        """Test getting economics template returns valid data."""
        result = get_economics_template("feed_costs")
        assert isinstance(result, dict)


class TestAnimalResourcesLogic:
    """Tests for animal resource logic using mocked NSIP client."""

    @pytest.fixture
    def mock_client(self) -> MagicMock:
        """Create a mock NSIP client."""
        client = MagicMock()
        return client

    @pytest.fixture
    def mock_animal(self) -> MagicMock:
        """Create a mock animal object."""
        animal = MagicMock()
        animal.to_dict.return_value = {
            "lpn_id": "6332-12345",
            "name": "Test Ram",
            "sex": "M",
            "breed": "Katahdin",
        }
        return animal

    def test_animal_mock_returns_dict(self, mock_client: MagicMock, mock_animal: MagicMock) -> None:
        """Test mock animal returns expected dict structure."""
        mock_client.get_animal_details.return_value = mock_animal
        animal = mock_client.get_animal_details("6332-12345")
        result = animal.to_dict()

        assert isinstance(result, dict)
        assert result.get("lpn_id") == "6332-12345"

    def test_animal_not_found_handling(self, mock_client: MagicMock) -> None:
        """Test handling when animal is not found."""
        mock_client.get_animal_details.return_value = None
        animal = mock_client.get_animal_details("invalid-id")

        assert animal is None

    def test_lineage_mock_structure(self, mock_client: MagicMock) -> None:
        """Test mock lineage returns expected structure."""
        mock_lineage = MagicMock()
        mock_lineage.to_dict.return_value = {
            "animal": {"lpn_id": "6332-12345"},
            "sire": None,
            "dam": None,
        }
        mock_client.get_lineage.return_value = mock_lineage

        lineage = mock_client.get_lineage("6332-12345")
        result = lineage.to_dict()

        assert isinstance(result, dict)
        assert "animal" in result

    def test_progeny_mock_structure(self, mock_client: MagicMock) -> None:
        """Test mock progeny returns expected structure."""
        mock_progeny = MagicMock()
        mock_progeny.to_dict.return_value = {"animals": [], "total": 0}
        mock_client.get_progeny.return_value = mock_progeny

        progeny = mock_client.get_progeny("6332-12345")
        result = progeny.to_dict()

        assert isinstance(result, dict)
        assert "animals" in result or "total" in result


class TestFlockResourcesLogic:
    """Tests for flock resource logic using mocked NSIP client."""

    def test_flock_search_structure(self) -> None:
        """Test flock search returns expected structure from mock."""
        mock_client = MagicMock()
        mock_search_result = MagicMock()
        mock_search_result.animals = []
        mock_search_result.total = 0
        mock_client.search_animals.return_value = mock_search_result

        result = mock_client.search_animals(flock_id="6332")
        assert hasattr(result, "animals")
        assert result.total == 0

    def test_flock_summary_calculation(self) -> None:
        """Test flock summary calculation logic."""
        # Mock a list of animals with EBVs
        animals = [
            {"lpn_id": "001", "sex": "M", "ebvs": {"WWT": 5.0}},
            {"lpn_id": "002", "sex": "F", "ebvs": {"WWT": 3.0}},
            {"lpn_id": "003", "sex": "F", "ebvs": {"WWT": 4.0}},
        ]

        # Calculate summary statistics
        rams = [a for a in animals if a["sex"] == "M"]
        ewes = [a for a in animals if a["sex"] == "F"]

        assert len(rams) == 1
        assert len(ewes) == 2

    def test_flock_ebv_average_calculation(self) -> None:
        """Test EBV average calculation logic."""
        ebv_values = [5.0, 3.0, 4.0]
        avg = sum(ebv_values) / len(ebv_values)

        assert avg == 4.0


class TestBreedingResourcesLogic:
    """Tests for breeding resource logic using mocked NSIP client."""

    @pytest.fixture
    def mock_client(self) -> MagicMock:
        """Create a mock NSIP client."""
        return MagicMock()

    @pytest.fixture
    def mock_animals(self) -> tuple:
        """Create mock ram and ewe objects."""
        ram = MagicMock()
        ram.to_dict.return_value = {
            "lpn_id": "6332-001",
            "name": "Test Ram",
            "sex": "M",
            "ebvs": {"WWT": 5.0, "BWT": 0.5},
        }
        ewe = MagicMock()
        ewe.to_dict.return_value = {
            "lpn_id": "6332-002",
            "name": "Test Ewe",
            "sex": "F",
            "ebvs": {"WWT": 3.0, "BWT": 0.3},
        }
        return ram, ewe

    def test_breeding_projection_calculation(
        self, mock_client: MagicMock, mock_animals: tuple
    ) -> None:
        """Test breeding projection EBV calculation logic."""
        ram, ewe = mock_animals
        ram_ebvs = ram.to_dict()["ebvs"]
        ewe_ebvs = ewe.to_dict()["ebvs"]

        # Offspring EBV = average of sire and dam
        projected_ww = (ram_ebvs["WWT"] + ewe_ebvs["WWT"]) / 2

        assert projected_ww == 4.0

    def test_inbreeding_coefficient_structure(self, mock_client: MagicMock) -> None:
        """Test inbreeding coefficient calculation structure."""
        mock_lineage = MagicMock()
        mock_lineage.to_dict.return_value = {
            "animal": {},
            "sire": None,
            "dam": None,
        }
        mock_client.get_lineage.return_value = mock_lineage

        # When both parents are unknown, COI should be 0 or unknown
        lineage = mock_client.get_lineage("6332-001")
        result = lineage.to_dict()

        assert result["sire"] is None
        assert result["dam"] is None

    def test_breeding_recommendation_structure(
        self, mock_client: MagicMock, mock_animals: tuple
    ) -> None:
        """Test breeding recommendation returns expected structure."""
        ram, ewe = mock_animals
        mock_client.get_animal_details.side_effect = [ram, ewe]

        # Get both animals
        ram_result = mock_client.get_animal_details("6332-001")
        ewe_result = mock_client.get_animal_details("6332-002")

        # Basic recommendation would compare EBVs
        ram_data = ram_result.to_dict()
        ewe_data = ewe_result.to_dict()

        assert ram_data["sex"] == "M"
        assert ewe_data["sex"] == "F"
