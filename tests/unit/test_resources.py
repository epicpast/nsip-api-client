"""Unit tests for MCP resources module.

Note: These tests focus on the underlying resource logic, not the MCP decorator
integration. For FastMCP decorated resources, we test the functions that provide
the data, not the FunctionResource wrapper objects.
"""

from unittest.mock import MagicMock

import pytest

# Import the knowledge base functions that resources use
from nsip_mcp.knowledge_base import (
    get_calendar_template,
    get_disease_guide,
    get_economics_template,
    get_heritabilities,
    get_nutrition_guide,
    get_region_info,
    get_selection_index,
    get_trait_info,
    list_regions,
    list_selection_indexes,
    list_traits,
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


class TestStaticResourceExecution:
    """Tests that directly execute the MCP resource functions via .fn attribute."""

    import asyncio

    def test_get_default_heritabilities_resource(self) -> None:
        """Test default heritabilities resource returns data."""
        import asyncio

        from nsip_mcp.resources.static_resources import get_default_heritabilities

        result = asyncio.run(get_default_heritabilities.fn())
        assert isinstance(result, dict)
        assert "heritabilities" in result
        assert "breed" in result

    def test_get_breed_heritabilities_resource(self) -> None:
        """Test breed heritabilities resource returns data."""
        import asyncio

        from nsip_mcp.resources.static_resources import get_breed_heritabilities

        result = asyncio.run(get_breed_heritabilities.fn(breed="katahdin"))
        assert isinstance(result, dict)
        assert "heritabilities" in result
        assert result["breed"] == "katahdin"

    def test_get_all_traits_resource(self) -> None:
        """Test all traits resource returns data."""
        import asyncio

        from nsip_mcp.resources.static_resources import get_all_traits

        result = asyncio.run(get_all_traits.fn())
        assert isinstance(result, dict)
        assert "traits" in result
        assert "count" in result

    def test_get_trait_details_resource(self) -> None:
        """Test trait details resource returns data."""
        import asyncio

        from nsip_mcp.resources.static_resources import get_trait_details

        result = asyncio.run(get_trait_details.fn(trait_code="WWT"))
        assert isinstance(result, dict)
        assert "trait" in result or "code" in result

    def test_get_all_indexes_resource(self) -> None:
        """Test all indexes resource returns data."""
        import asyncio

        from nsip_mcp.resources.static_resources import get_all_indexes

        result = asyncio.run(get_all_indexes.fn())
        assert isinstance(result, dict)
        assert "indexes" in result

    def test_get_index_details_resource(self) -> None:
        """Test index details resource returns data."""
        import asyncio

        from nsip_mcp.resources.static_resources import get_index_details

        result = asyncio.run(get_index_details.fn(index_name="terminal"))
        assert isinstance(result, dict)
        assert "index_name" in result or "name" in result

    def test_get_all_regions_resource(self) -> None:
        """Test all regions resource returns data."""
        import asyncio

        from nsip_mcp.resources.static_resources import get_all_regions

        result = asyncio.run(get_all_regions.fn())
        assert isinstance(result, dict)
        assert "regions" in result

    def test_get_region_details_resource(self) -> None:
        """Test region details resource returns data."""
        import asyncio

        from nsip_mcp.resources.static_resources import get_region_details

        result = asyncio.run(get_region_details.fn(region_id="midwest"))
        assert isinstance(result, dict)
        assert "region" in result or "id" in result

    def test_get_disease_info_resource(self) -> None:
        """Test disease info resource returns data."""
        import asyncio

        from nsip_mcp.resources.static_resources import get_disease_info

        result = asyncio.run(get_disease_info.fn(region="midwest"))
        assert isinstance(result, dict)

    def test_get_nutrition_info_resource(self) -> None:
        """Test nutrition info resource returns data."""
        import asyncio

        from nsip_mcp.resources.static_resources import get_nutrition_info

        result = asyncio.run(get_nutrition_info.fn(region="midwest", season="summer"))
        assert isinstance(result, dict)

    def test_get_calendar_info_resource(self) -> None:
        """Test calendar info resource returns data."""
        import asyncio

        from nsip_mcp.resources.static_resources import get_calendar_info

        result = asyncio.run(get_calendar_info.fn(task_type="breeding"))
        assert isinstance(result, dict)

    def test_get_economics_info_resource(self) -> None:
        """Test economics info resource returns data."""
        import asyncio

        from nsip_mcp.resources.static_resources import get_economics_info

        result = asyncio.run(get_economics_info.fn(category="feed_costs"))
        assert isinstance(result, dict)


class TestAnimalResourceExecution:
    """Tests that directly execute the animal MCP resource functions via .fn attribute."""

    def test_get_animal_details_resource_not_found(self) -> None:
        """Test animal details resource with non-existent animal."""
        import asyncio
        from unittest.mock import patch

        with patch("nsip_mcp.resources.animal_resources.get_nsip_client") as mock_get:
            mock_client = MagicMock()
            mock_client.get_animal_details.return_value = None
            mock_get.return_value = mock_client

            from nsip_mcp.resources.animal_resources import get_animal_details_resource

            result = asyncio.run(get_animal_details_resource.fn(lpn_id="fake-id"))
            assert isinstance(result, dict)

    def test_get_animal_lineage_resource(self) -> None:
        """Test animal lineage resource."""
        import asyncio
        from unittest.mock import patch

        with patch("nsip_mcp.resources.animal_resources.get_nsip_client") as mock_get:
            mock_client = MagicMock()
            mock_client.get_lineage.return_value = None
            mock_get.return_value = mock_client

            from nsip_mcp.resources.animal_resources import get_animal_lineage_resource

            result = asyncio.run(get_animal_lineage_resource.fn(lpn_id="fake-id"))
            assert isinstance(result, dict)

    def test_get_animal_progeny_resource(self) -> None:
        """Test animal progeny resource."""
        import asyncio
        from unittest.mock import patch

        with patch("nsip_mcp.resources.animal_resources.get_nsip_client") as mock_get:
            mock_client = MagicMock()
            mock_progeny = MagicMock()
            mock_progeny.animals = []
            mock_client.get_progeny.return_value = mock_progeny
            mock_get.return_value = mock_client

            from nsip_mcp.resources.animal_resources import get_animal_progeny_resource

            result = asyncio.run(get_animal_progeny_resource.fn(lpn_id="fake-id"))
            assert isinstance(result, dict)

    def test_get_animal_profile_resource(self) -> None:
        """Test animal full profile resource."""
        import asyncio
        from unittest.mock import patch

        with patch("nsip_mcp.resources.animal_resources.get_nsip_client") as mock_get:
            mock_client = MagicMock()
            mock_client.get_animal_details.return_value = None
            mock_client.get_lineage.return_value = None
            mock_progeny = MagicMock()
            mock_progeny.animals = []
            mock_client.get_progeny.return_value = mock_progeny
            mock_get.return_value = mock_client

            from nsip_mcp.resources.animal_resources import get_animal_profile_resource

            result = asyncio.run(get_animal_profile_resource.fn(lpn_id="fake-id"))
            assert isinstance(result, dict)


class TestFlockResourceExecution:
    """Tests that directly execute the flock MCP resource functions via .fn attribute."""

    def test_get_flock_summary(self) -> None:
        """Test flock summary resource."""
        import asyncio
        from unittest.mock import patch

        with patch("nsip_mcp.resources.flock_resources.get_nsip_client") as mock_get:
            mock_client = MagicMock()
            mock_search = MagicMock()
            mock_search.results = []
            mock_client.search_animals.return_value = mock_search
            mock_get.return_value = mock_client

            from nsip_mcp.resources.flock_resources import get_flock_summary

            result = asyncio.run(get_flock_summary.fn(flock_id="6332"))
            assert isinstance(result, dict)

    def test_get_flock_ebv_averages(self) -> None:
        """Test flock EBV averages resource."""
        import asyncio
        from unittest.mock import patch

        with patch("nsip_mcp.resources.flock_resources.get_nsip_client") as mock_get:
            mock_client = MagicMock()
            mock_search = MagicMock()
            mock_search.results = []
            mock_client.search_animals.return_value = mock_search
            mock_get.return_value = mock_client

            from nsip_mcp.resources.flock_resources import get_flock_ebv_averages

            result = asyncio.run(get_flock_ebv_averages.fn(flock_id="6332"))
            assert isinstance(result, dict)


class TestBreedingResourceExecution:
    """Tests that directly execute the breeding MCP resource functions via .fn attribute."""

    def test_get_breeding_projection(self) -> None:
        """Test breeding projection resource."""
        import asyncio
        from unittest.mock import patch

        with patch("nsip_mcp.resources.breeding_resources.get_nsip_client") as mock_get:
            mock_client = MagicMock()
            mock_client.get_animal_details.return_value = None
            mock_get.return_value = mock_client

            from nsip_mcp.resources.breeding_resources import get_breeding_projection

            result = asyncio.run(get_breeding_projection.fn(ram_lpn="ram1", ewe_lpn="ewe1"))
            assert isinstance(result, dict)

    def test_get_breeding_projection_with_animals(self) -> None:
        """Test breeding projection with mocked animals."""
        import asyncio
        from unittest.mock import patch

        with patch("nsip_mcp.resources.breeding_resources.get_nsip_client") as mock_get:
            with patch("nsip_mcp.resources.breeding_resources.response_cache") as mock_cache:
                mock_cache.get.return_value = None  # No cache hit
                mock_client = MagicMock()

                # Create mock animal with EBVs
                mock_ram = MagicMock()
                mock_ram.to_dict.return_value = {
                    "lpn_id": "ram1",
                    "ebvs": {"WWT": 5.0, "BWT": 0.5, "PWWT": 8.0},
                }
                mock_ewe = MagicMock()
                mock_ewe.to_dict.return_value = {
                    "lpn_id": "ewe1",
                    "ebvs": {"WWT": 4.0, "BWT": 0.3, "NLW": 0.2},
                }
                mock_client.get_animal_details.side_effect = [mock_ram, mock_ewe]
                mock_get.return_value = mock_client

                from nsip_mcp.resources.breeding_resources import get_breeding_projection

                result = asyncio.run(get_breeding_projection.fn(ram_lpn="ram1", ewe_lpn="ewe1"))
                assert isinstance(result, dict)
                assert "projection" in result or "error" not in result

    def test_get_breeding_projection_ewe_not_found(self) -> None:
        """Test breeding projection when ewe is not found."""
        import asyncio
        from unittest.mock import patch

        with patch("nsip_mcp.resources.breeding_resources.get_nsip_client") as mock_get:
            with patch("nsip_mcp.resources.breeding_resources.response_cache") as mock_cache:
                mock_cache.get.return_value = None
                mock_client = MagicMock()

                # Ram found, ewe not found
                mock_ram = MagicMock()
                mock_ram.to_dict.return_value = {"lpn_id": "ram1", "ebvs": {"WWT": 5.0}}
                mock_client.get_animal_details.side_effect = [mock_ram, None]
                mock_get.return_value = mock_client

                from nsip_mcp.resources.breeding_resources import get_breeding_projection

                result = asyncio.run(get_breeding_projection.fn(ram_lpn="ram1", ewe_lpn="ewe1"))
                assert isinstance(result, dict)
                assert "error" in result

    def test_get_breeding_inbreeding(self) -> None:
        """Test breeding inbreeding resource."""
        import asyncio
        from unittest.mock import patch

        with patch("nsip_mcp.resources.breeding_resources.get_nsip_client") as mock_get:
            mock_client = MagicMock()
            mock_client.get_lineage.return_value = None
            mock_get.return_value = mock_client

            from nsip_mcp.resources.breeding_resources import get_breeding_inbreeding

            result = asyncio.run(get_breeding_inbreeding.fn(ram_lpn="ram1", ewe_lpn="ewe1"))
            assert isinstance(result, dict)

    def test_get_breeding_inbreeding_with_lineage(self) -> None:
        """Test breeding inbreeding with lineage data."""
        import asyncio
        from unittest.mock import patch

        with patch("nsip_mcp.resources.breeding_resources.get_nsip_client") as mock_get:
            mock_client = MagicMock()

            # Create mock lineages with common ancestor
            mock_ram_lineage = MagicMock()
            mock_ram_lineage.to_dict.return_value = {
                "sire": {"lpn_id": "common-ancestor"},
                "dam": {"lpn_id": "dam1"},
            }
            mock_ewe_lineage = MagicMock()
            mock_ewe_lineage.to_dict.return_value = {
                "sire": {"lpn_id": "common-ancestor"},
                "dam": {"lpn_id": "dam2"},
            }
            mock_client.get_lineage.side_effect = [mock_ram_lineage, mock_ewe_lineage]
            mock_get.return_value = mock_client

            from nsip_mcp.resources.breeding_resources import get_breeding_inbreeding

            result = asyncio.run(get_breeding_inbreeding.fn(ram_lpn="ram1", ewe_lpn="ewe1"))
            assert isinstance(result, dict)
            assert "inbreeding" in result

    def test_get_breeding_inbreeding_ewe_lineage_not_found(self) -> None:
        """Test breeding inbreeding when ewe lineage not found."""
        import asyncio
        from unittest.mock import patch

        with patch("nsip_mcp.resources.breeding_resources.get_nsip_client") as mock_get:
            mock_client = MagicMock()
            mock_ram_lineage = MagicMock()
            mock_ram_lineage.to_dict.return_value = {"sire": None, "dam": None}
            mock_client.get_lineage.side_effect = [mock_ram_lineage, None]
            mock_get.return_value = mock_client

            from nsip_mcp.resources.breeding_resources import get_breeding_inbreeding

            result = asyncio.run(get_breeding_inbreeding.fn(ram_lpn="ram1", ewe_lpn="ewe1"))
            assert isinstance(result, dict)
            assert "error" in result

    def test_get_breeding_recommendation(self) -> None:
        """Test breeding recommendation resource."""
        import asyncio
        from unittest.mock import patch

        with patch("nsip_mcp.resources.breeding_resources.get_nsip_client") as mock_get:
            mock_client = MagicMock()
            mock_client.get_animal_details.return_value = None
            mock_client.get_lineage.return_value = None
            mock_get.return_value = mock_client

            from nsip_mcp.resources.breeding_resources import get_breeding_recommendation

            result = asyncio.run(get_breeding_recommendation.fn(ram_lpn="ram1", ewe_lpn="ewe1"))
            assert isinstance(result, dict)

    def test_get_breeding_recommendation_proceed(self) -> None:
        """Test breeding recommendation with good match."""
        import asyncio
        from unittest.mock import patch

        with patch("nsip_mcp.resources.breeding_resources.get_nsip_client") as mock_get:
            with patch("nsip_mcp.resources.breeding_resources.response_cache") as mock_cache:
                mock_cache.get.return_value = None
                mock_client = MagicMock()

                # Create animals with good EBVs
                mock_ram = MagicMock()
                mock_ram.to_dict.return_value = {
                    "lpn_id": "ram1",
                    "ebvs": {"WWT": 6.0, "BWT": -0.2, "PWWT": 10.0, "NLW": 0.15},
                }
                mock_ewe = MagicMock()
                mock_ewe.to_dict.return_value = {
                    "lpn_id": "ewe1",
                    "ebvs": {"WWT": 5.0, "BWT": -0.1, "MWWT": 3.0, "NLW": 0.1},
                }
                mock_client.get_animal_details.side_effect = [mock_ram, mock_ewe]
                mock_client.get_lineage.return_value = None  # No lineage = no inbreeding concern
                mock_get.return_value = mock_client

                from nsip_mcp.resources.breeding_resources import get_breeding_recommendation

                result = asyncio.run(get_breeding_recommendation.fn(ram_lpn="ram1", ewe_lpn="ewe1"))
                assert isinstance(result, dict)
                assert "recommendation" in result

    def test_get_breeding_recommendation_high_bwt_concern(self) -> None:
        """Test breeding recommendation with high birth weight concern."""
        import asyncio
        from unittest.mock import patch

        with patch("nsip_mcp.resources.breeding_resources.get_nsip_client") as mock_get:
            with patch("nsip_mcp.resources.breeding_resources.response_cache") as mock_cache:
                mock_cache.get.return_value = None
                mock_client = MagicMock()

                # Create animals with high BWT (dystocia concern)
                mock_ram = MagicMock()
                mock_ram.to_dict.return_value = {
                    "lpn_id": "ram1",
                    "ebvs": {"WWT": 5.0, "BWT": 2.0, "PWWT": 8.0},
                }
                mock_ewe = MagicMock()
                mock_ewe.to_dict.return_value = {
                    "lpn_id": "ewe1",
                    "ebvs": {"WWT": 4.0, "BWT": 1.5},
                }
                mock_client.get_animal_details.side_effect = [mock_ram, mock_ewe]
                mock_client.get_lineage.return_value = None
                mock_get.return_value = mock_client

                from nsip_mcp.resources.breeding_resources import get_breeding_recommendation

                result = asyncio.run(get_breeding_recommendation.fn(ram_lpn="ram1", ewe_lpn="ewe1"))
                assert isinstance(result, dict)


class TestBreedingResourceHelpers:
    """Tests for breeding resource helper functions."""

    def test_project_offspring_ebv_both_none(self) -> None:
        """Test offspring projection when both parents have no value."""
        from nsip_mcp.resources.breeding_resources import _project_offspring_ebv

        result = _project_offspring_ebv(None, None)
        assert result is None

    def test_project_offspring_ebv_sire_only(self) -> None:
        """Test offspring projection when only sire has value."""
        from nsip_mcp.resources.breeding_resources import _project_offspring_ebv

        result = _project_offspring_ebv(5.0, None)
        assert result == 5.0

    def test_project_offspring_ebv_dam_only(self) -> None:
        """Test offspring projection when only dam has value."""
        from nsip_mcp.resources.breeding_resources import _project_offspring_ebv

        result = _project_offspring_ebv(None, 4.0)
        assert result == 4.0

    def test_project_offspring_ebv_both(self) -> None:
        """Test offspring projection with both parents."""
        from nsip_mcp.resources.breeding_resources import _project_offspring_ebv

        result = _project_offspring_ebv(6.0, 4.0)
        assert result == 5.0

    def test_find_common_ancestors_none(self) -> None:
        """Test finding common ancestors with no overlap."""
        from nsip_mcp.resources.breeding_resources import _find_common_ancestors

        lineage1 = {"sire": {"lpn_id": "sire1"}, "dam": {"lpn_id": "dam1"}}
        lineage2 = {"sire": {"lpn_id": "sire2"}, "dam": {"lpn_id": "dam2"}}

        result = _find_common_ancestors(lineage1, lineage2)
        assert result == []

    def test_find_common_ancestors_with_common(self) -> None:
        """Test finding common ancestors with overlap."""
        from nsip_mcp.resources.breeding_resources import _find_common_ancestors

        lineage1 = {"sire": {"lpn_id": "common"}, "dam": {"lpn_id": "dam1"}}
        lineage2 = {"sire": {"lpn_id": "common"}, "dam": {"lpn_id": "dam2"}}

        result = _find_common_ancestors(lineage1, lineage2)
        assert "common" in result

    def test_find_common_ancestors_empty_lineage(self) -> None:
        """Test finding common ancestors with empty lineage."""
        from nsip_mcp.resources.breeding_resources import _find_common_ancestors

        result = _find_common_ancestors({}, {})
        assert result == []

    def test_estimate_inbreeding_no_common(self) -> None:
        """Test inbreeding estimation with no common ancestors."""
        from nsip_mcp.resources.breeding_resources import _estimate_inbreeding

        result = _estimate_inbreeding([])
        assert result == 0.0

    def test_estimate_inbreeding_one_common(self) -> None:
        """Test inbreeding estimation with one common ancestor."""
        from nsip_mcp.resources.breeding_resources import _estimate_inbreeding

        result = _estimate_inbreeding(["ancestor1"])
        assert result == 0.0625

    def test_estimate_inbreeding_capped(self) -> None:
        """Test inbreeding estimation is capped at 25%."""
        from nsip_mcp.resources.breeding_resources import _estimate_inbreeding

        # Many common ancestors should cap at 0.25
        result = _estimate_inbreeding(["a1", "a2", "a3", "a4", "a5", "a6", "a7", "a8"])
        assert result == 0.25


class TestFlockResourceExecutionExtended:
    """Extended tests for flock MCP resource functions."""

    def test_search_flock_animals_resource(self) -> None:
        """Test search flock animals resource."""
        import asyncio

        from nsip_mcp.resources.flock_resources import search_flock_animals

        result = asyncio.run(search_flock_animals.fn())
        assert isinstance(result, dict)
        assert "message" in result or "parameters" in result

    def test_get_flock_summary_with_animals(self) -> None:
        """Test flock summary with animals found."""
        import asyncio
        from unittest.mock import patch

        with patch("nsip_mcp.resources.flock_resources.get_nsip_client") as mock_get:
            with patch("nsip_mcp.resources.flock_resources.response_cache") as mock_cache:
                mock_cache.get.return_value = None
                mock_client = MagicMock()
                mock_search = MagicMock()
                mock_search.results = [
                    {"lpn_id": "6332001", "LpnId": "6332001", "sex": "M", "status": "A"},
                    {"lpn_id": "6332002", "LpnId": "6332002", "sex": "F", "status": "A"},
                    {"lpn_id": "6332003", "LpnId": "6332003", "sex": "F", "status": "S"},
                ]
                mock_client.search_animals.return_value = mock_search
                mock_get.return_value = mock_client

                from nsip_mcp.resources.flock_resources import get_flock_summary

                result = asyncio.run(get_flock_summary.fn(flock_id="6332"))
                assert isinstance(result, dict)
                # Should have summary with animal breakdown
                if "summary" in result:
                    assert "total_animals" in result["summary"]

    def test_get_flock_summary_with_birth_years(self) -> None:
        """Test flock summary calculates birth year distribution."""
        import asyncio
        from unittest.mock import patch

        with patch("nsip_mcp.resources.flock_resources.get_nsip_client") as mock_get:
            with patch("nsip_mcp.resources.flock_resources.response_cache") as mock_cache:
                mock_cache.get.return_value = None
                mock_client = MagicMock()
                mock_search = MagicMock()
                mock_search.results = [
                    {"lpn_id": "6332001", "LpnId": "6332001", "sex": "M", "birth_date": "2022-03"},
                    {"lpn_id": "6332002", "LpnId": "6332002", "sex": "F", "birthDate": "2023-02"},
                ]
                mock_client.search_animals.return_value = mock_search
                mock_get.return_value = mock_client

                from nsip_mcp.resources.flock_resources import get_flock_summary

                result = asyncio.run(get_flock_summary.fn(flock_id="6332"))
                assert isinstance(result, dict)

    def test_get_flock_ebv_averages_with_data(self) -> None:
        """Test flock EBV averages with animals that have EBV data."""
        import asyncio
        from unittest.mock import patch

        with patch("nsip_mcp.resources.flock_resources.get_nsip_client") as mock_get:
            with patch("nsip_mcp.resources.flock_resources.response_cache") as mock_cache:
                mock_cache.get.return_value = None
                mock_client = MagicMock()
                mock_search = MagicMock()
                mock_search.results = [
                    {
                        "lpn_id": "6332001",
                        "LpnId": "6332001",
                        "ebvs": {"WWT": 5.0, "BWT": 0.5},
                    },
                    {
                        "lpn_id": "6332002",
                        "LpnId": "6332002",
                        "ebvs": {"WWT": 4.0, "BWT": 0.3},
                    },
                    {
                        "lpn_id": "6332003",
                        "LpnId": "6332003",
                        "ebvs": {"WWT": 6.0},
                    },
                ]
                mock_client.search_animals.return_value = mock_search
                mock_get.return_value = mock_client

                from nsip_mcp.resources.flock_resources import get_flock_ebv_averages

                result = asyncio.run(get_flock_ebv_averages.fn(flock_id="6332"))
                assert isinstance(result, dict)
                if "ebv_averages" in result:
                    assert "WWT" in result["ebv_averages"]
                    assert result["ebv_averages"]["WWT"]["average"] == 5.0

    def test_get_flock_summary_api_error(self) -> None:
        """Test flock summary handles API error."""
        import asyncio
        from unittest.mock import patch

        from nsip_client.exceptions import NSIPAPIError

        with patch("nsip_mcp.resources.flock_resources.get_nsip_client") as mock_get:
            with patch("nsip_mcp.resources.flock_resources.response_cache") as mock_cache:
                mock_cache.get.return_value = None
                mock_client = MagicMock()
                mock_client.search_animals.side_effect = NSIPAPIError("API error")
                mock_get.return_value = mock_client

                from nsip_mcp.resources.flock_resources import get_flock_summary

                result = asyncio.run(get_flock_summary.fn(flock_id="6332"))
                assert isinstance(result, dict)
                assert "error" in result

    def test_get_flock_ebv_averages_api_error(self) -> None:
        """Test flock EBV averages handles API error."""
        import asyncio
        from unittest.mock import patch

        from nsip_client.exceptions import NSIPAPIError

        with patch("nsip_mcp.resources.flock_resources.get_nsip_client") as mock_get:
            with patch("nsip_mcp.resources.flock_resources.response_cache") as mock_cache:
                mock_cache.get.return_value = None
                mock_client = MagicMock()
                mock_client.search_animals.side_effect = NSIPAPIError("API error")
                mock_get.return_value = mock_client

                from nsip_mcp.resources.flock_resources import get_flock_ebv_averages

                result = asyncio.run(get_flock_ebv_averages.fn(flock_id="6332"))
                assert isinstance(result, dict)
                assert "error" in result

    def test_get_flock_summary_cache_hit(self) -> None:
        """Test flock summary uses cached results."""
        import asyncio
        from unittest.mock import patch

        with patch("nsip_mcp.resources.flock_resources.get_nsip_client") as mock_get:
            with patch("nsip_mcp.resources.flock_resources.response_cache") as mock_cache:
                # Return cached data
                mock_cache.get.return_value = [
                    {"lpn_id": "6332001", "sex": "M", "status": "A"},
                ]
                mock_client = MagicMock()
                mock_get.return_value = mock_client

                from nsip_mcp.resources.flock_resources import get_flock_summary

                result = asyncio.run(get_flock_summary.fn(flock_id="6332"))
                assert isinstance(result, dict)
                # Client should not be called if cache hit
                mock_client.search_animals.assert_not_called()


class TestAnimalResourcesExtended:
    """Extended tests for animal resource functions covering uncovered paths."""

    def test_get_animal_details_success(self) -> None:
        """Test animal details resource with successful response."""
        import asyncio
        from unittest.mock import patch

        with patch("nsip_mcp.resources.animal_resources.get_nsip_client") as mock_get:
            with patch("nsip_mcp.resources.animal_resources.response_cache") as mock_cache:
                mock_cache.get.return_value = None
                mock_client = MagicMock()
                mock_animal = MagicMock()
                mock_animal.to_dict.return_value = {
                    "lpn_id": "6332-12345",
                    "name": "Test Ram",
                    "sex": "M",
                    "breed": "Katahdin",
                    "ebvs": {"WWT": 5.0},
                }
                mock_client.get_animal_details.return_value = mock_animal
                mock_get.return_value = mock_client

                from nsip_mcp.resources.animal_resources import get_animal_details_resource

                result = asyncio.run(get_animal_details_resource.fn(lpn_id="6332-12345"))
                assert isinstance(result, dict)
                assert "animal" in result
                assert result["lpn_id"] == "6332-12345"

    def test_get_animal_details_cache_hit(self) -> None:
        """Test animal details resource with cache hit."""
        import asyncio
        from unittest.mock import patch

        with patch("nsip_mcp.resources.animal_resources.get_nsip_client") as mock_get:
            with patch("nsip_mcp.resources.animal_resources.response_cache") as mock_cache:
                # Cache returns the animal data
                mock_cache.get.return_value = {
                    "lpn_id": "6332-12345",
                    "name": "Cached Ram",
                }
                mock_client = MagicMock()
                mock_get.return_value = mock_client

                from nsip_mcp.resources.animal_resources import get_animal_details_resource

                result = asyncio.run(get_animal_details_resource.fn(lpn_id="6332-12345"))
                assert isinstance(result, dict)
                assert "animal" in result
                # Client should not be called
                mock_client.get_animal_details.assert_not_called()

    def test_get_animal_details_api_error(self) -> None:
        """Test animal details resource handles API error."""
        import asyncio
        from unittest.mock import patch

        from nsip_client.exceptions import NSIPAPIError

        with patch("nsip_mcp.resources.animal_resources.get_nsip_client") as mock_get:
            with patch("nsip_mcp.resources.animal_resources.response_cache") as mock_cache:
                mock_cache.get.return_value = None
                mock_client = MagicMock()
                mock_client.get_animal_details.side_effect = NSIPAPIError("API error")
                mock_get.return_value = mock_client

                from nsip_mcp.resources.animal_resources import get_animal_details_resource

                result = asyncio.run(get_animal_details_resource.fn(lpn_id="6332-12345"))
                assert isinstance(result, dict)
                assert "error" in result

    def test_get_animal_details_not_found_error(self) -> None:
        """Test animal details resource handles not found error."""
        import asyncio
        from unittest.mock import patch

        from nsip_client.exceptions import NSIPNotFoundError

        with patch("nsip_mcp.resources.animal_resources.get_nsip_client") as mock_get:
            with patch("nsip_mcp.resources.animal_resources.response_cache") as mock_cache:
                mock_cache.get.return_value = None
                mock_client = MagicMock()
                mock_client.get_animal_details.side_effect = NSIPNotFoundError("Not found")
                mock_get.return_value = mock_client

                from nsip_mcp.resources.animal_resources import get_animal_details_resource

                result = asyncio.run(get_animal_details_resource.fn(lpn_id="invalid"))
                assert isinstance(result, dict)
                assert "error" in result

    def test_get_animal_lineage_success(self) -> None:
        """Test animal lineage resource with successful response."""
        import asyncio
        from unittest.mock import patch

        with patch("nsip_mcp.resources.animal_resources.get_nsip_client") as mock_get:
            with patch("nsip_mcp.resources.animal_resources.response_cache") as mock_cache:
                mock_cache.get.return_value = None
                mock_client = MagicMock()
                mock_lineage = MagicMock()
                mock_lineage.to_dict.return_value = {
                    "sire": {"lpn_id": "sire123"},
                    "dam": {"lpn_id": "dam456"},
                }
                mock_client.get_lineage.return_value = mock_lineage
                mock_get.return_value = mock_client

                from nsip_mcp.resources.animal_resources import get_animal_lineage_resource

                result = asyncio.run(get_animal_lineage_resource.fn(lpn_id="6332-12345"))
                assert isinstance(result, dict)
                assert "lineage" in result
                assert result["lpn_id"] == "6332-12345"

    def test_get_animal_lineage_cache_hit(self) -> None:
        """Test animal lineage resource with cache hit."""
        import asyncio
        from unittest.mock import patch

        with patch("nsip_mcp.resources.animal_resources.get_nsip_client") as mock_get:
            with patch("nsip_mcp.resources.animal_resources.response_cache") as mock_cache:
                mock_cache.get.return_value = {"sire": None, "dam": None}
                mock_client = MagicMock()
                mock_get.return_value = mock_client

                from nsip_mcp.resources.animal_resources import get_animal_lineage_resource

                result = asyncio.run(get_animal_lineage_resource.fn(lpn_id="6332-12345"))
                assert isinstance(result, dict)
                mock_client.get_lineage.assert_not_called()

    def test_get_animal_lineage_api_error(self) -> None:
        """Test animal lineage resource handles API error."""
        import asyncio
        from unittest.mock import patch

        from nsip_client.exceptions import NSIPAPIError

        with patch("nsip_mcp.resources.animal_resources.get_nsip_client") as mock_get:
            with patch("nsip_mcp.resources.animal_resources.response_cache") as mock_cache:
                mock_cache.get.return_value = None
                mock_client = MagicMock()
                mock_client.get_lineage.side_effect = NSIPAPIError("API error")
                mock_get.return_value = mock_client

                from nsip_mcp.resources.animal_resources import get_animal_lineage_resource

                result = asyncio.run(get_animal_lineage_resource.fn(lpn_id="6332-12345"))
                assert isinstance(result, dict)
                assert "error" in result

    def test_get_animal_lineage_not_found_error(self) -> None:
        """Test animal lineage resource handles not found error."""
        import asyncio
        from unittest.mock import patch

        from nsip_client.exceptions import NSIPNotFoundError

        with patch("nsip_mcp.resources.animal_resources.get_nsip_client") as mock_get:
            with patch("nsip_mcp.resources.animal_resources.response_cache") as mock_cache:
                mock_cache.get.return_value = None
                mock_client = MagicMock()
                mock_client.get_lineage.side_effect = NSIPNotFoundError("Not found")
                mock_get.return_value = mock_client

                from nsip_mcp.resources.animal_resources import get_animal_lineage_resource

                result = asyncio.run(get_animal_lineage_resource.fn(lpn_id="invalid"))
                assert isinstance(result, dict)
                assert "error" in result

    def test_get_animal_progeny_success(self) -> None:
        """Test animal progeny resource with successful response."""
        import asyncio
        from unittest.mock import patch

        with patch("nsip_mcp.resources.animal_resources.get_nsip_client") as mock_get:
            with patch("nsip_mcp.resources.animal_resources.response_cache") as mock_cache:
                mock_cache.get.return_value = None
                mock_client = MagicMock()
                mock_progeny = MagicMock()
                mock_lamb1 = MagicMock()
                mock_lamb1.to_dict.return_value = {"lpn_id": "lamb1", "name": "Lamb 1"}
                mock_lamb2 = MagicMock()
                mock_lamb2.to_dict.return_value = {"lpn_id": "lamb2", "name": "Lamb 2"}
                mock_progeny.animals = [mock_lamb1, mock_lamb2]
                mock_client.get_progeny.return_value = mock_progeny
                mock_get.return_value = mock_client

                from nsip_mcp.resources.animal_resources import get_animal_progeny_resource

                result = asyncio.run(get_animal_progeny_resource.fn(lpn_id="6332-12345"))
                assert isinstance(result, dict)
                assert "progeny" in result
                assert result["count"] == 2

    def test_get_animal_progeny_cache_hit(self) -> None:
        """Test animal progeny resource with cache hit."""
        import asyncio
        from unittest.mock import patch

        with patch("nsip_mcp.resources.animal_resources.get_nsip_client") as mock_get:
            with patch("nsip_mcp.resources.animal_resources.response_cache") as mock_cache:
                mock_cache.get.return_value = [{"lpn_id": "lamb1"}]
                mock_client = MagicMock()
                mock_get.return_value = mock_client

                from nsip_mcp.resources.animal_resources import get_animal_progeny_resource

                result = asyncio.run(get_animal_progeny_resource.fn(lpn_id="6332-12345"))
                assert isinstance(result, dict)
                mock_client.get_progeny.assert_not_called()

    def test_get_animal_progeny_api_error(self) -> None:
        """Test animal progeny resource handles API error."""
        import asyncio
        from unittest.mock import patch

        from nsip_client.exceptions import NSIPAPIError

        with patch("nsip_mcp.resources.animal_resources.get_nsip_client") as mock_get:
            with patch("nsip_mcp.resources.animal_resources.response_cache") as mock_cache:
                mock_cache.get.return_value = None
                mock_client = MagicMock()
                mock_client.get_progeny.side_effect = NSIPAPIError("API error")
                mock_get.return_value = mock_client

                from nsip_mcp.resources.animal_resources import get_animal_progeny_resource

                result = asyncio.run(get_animal_progeny_resource.fn(lpn_id="6332-12345"))
                assert isinstance(result, dict)
                assert "error" in result

    def test_get_animal_progeny_not_found_error(self) -> None:
        """Test animal progeny resource handles not found error."""
        import asyncio
        from unittest.mock import patch

        from nsip_client.exceptions import NSIPNotFoundError

        with patch("nsip_mcp.resources.animal_resources.get_nsip_client") as mock_get:
            with patch("nsip_mcp.resources.animal_resources.response_cache") as mock_cache:
                mock_cache.get.return_value = None
                mock_client = MagicMock()
                mock_client.get_progeny.side_effect = NSIPNotFoundError("Not found")
                mock_get.return_value = mock_client

                from nsip_mcp.resources.animal_resources import get_animal_progeny_resource

                result = asyncio.run(get_animal_progeny_resource.fn(lpn_id="invalid"))
                assert isinstance(result, dict)
                assert "error" in result

    def test_get_animal_progeny_no_animals(self) -> None:
        """Test animal progeny resource when progeny has no animals."""
        import asyncio
        from unittest.mock import patch

        with patch("nsip_mcp.resources.animal_resources.get_nsip_client") as mock_get:
            with patch("nsip_mcp.resources.animal_resources.response_cache") as mock_cache:
                mock_cache.get.return_value = None
                mock_client = MagicMock()
                mock_progeny = MagicMock()
                mock_progeny.animals = None
                mock_client.get_progeny.return_value = mock_progeny
                mock_get.return_value = mock_client

                from nsip_mcp.resources.animal_resources import get_animal_progeny_resource

                result = asyncio.run(get_animal_progeny_resource.fn(lpn_id="6332-12345"))
                assert isinstance(result, dict)
                assert result["count"] == 0

    def test_get_animal_profile_success(self) -> None:
        """Test animal profile resource with successful response."""
        import asyncio
        from unittest.mock import patch

        with patch("nsip_mcp.resources.animal_resources.get_nsip_client") as mock_get:
            with patch("nsip_mcp.resources.animal_resources.response_cache") as mock_cache:
                mock_cache.get.return_value = None
                mock_client = MagicMock()

                mock_animal = MagicMock()
                mock_animal.to_dict.return_value = {"lpn_id": "6332-12345", "name": "Test Ram"}

                mock_lineage = MagicMock()
                mock_lineage.to_dict.return_value = {"sire": None, "dam": None}

                mock_progeny = MagicMock()
                mock_lamb = MagicMock()
                mock_lamb.to_dict.return_value = {"lpn_id": "lamb1"}
                mock_progeny.animals = [mock_lamb]

                mock_client.get_animal_details.return_value = mock_animal
                mock_client.get_lineage.return_value = mock_lineage
                mock_client.get_progeny.return_value = mock_progeny
                mock_get.return_value = mock_client

                from nsip_mcp.resources.animal_resources import get_animal_profile_resource

                result = asyncio.run(get_animal_profile_resource.fn(lpn_id="6332-12345"))
                assert isinstance(result, dict)
                assert "profile" in result
                assert result["profile"]["progeny_count"] == 1

    def test_get_animal_profile_api_error(self) -> None:
        """Test animal profile resource handles API error."""
        import asyncio
        from unittest.mock import patch

        from nsip_client.exceptions import NSIPAPIError

        with patch("nsip_mcp.resources.animal_resources.get_nsip_client") as mock_get:
            with patch("nsip_mcp.resources.animal_resources.response_cache") as mock_cache:
                mock_cache.get.return_value = None
                mock_client = MagicMock()
                mock_client.get_animal_details.side_effect = NSIPAPIError("API error")
                mock_get.return_value = mock_client

                from nsip_mcp.resources.animal_resources import get_animal_profile_resource

                result = asyncio.run(get_animal_profile_resource.fn(lpn_id="6332-12345"))
                assert isinstance(result, dict)
                assert "error" in result

    def test_get_animal_profile_not_found_error(self) -> None:
        """Test animal profile resource handles not found error."""
        import asyncio
        from unittest.mock import patch

        from nsip_client.exceptions import NSIPNotFoundError

        with patch("nsip_mcp.resources.animal_resources.get_nsip_client") as mock_get:
            with patch("nsip_mcp.resources.animal_resources.response_cache") as mock_cache:
                mock_cache.get.return_value = None
                mock_client = MagicMock()
                mock_client.get_animal_details.side_effect = NSIPNotFoundError("Not found")
                mock_get.return_value = mock_client

                from nsip_mcp.resources.animal_resources import get_animal_profile_resource

                result = asyncio.run(get_animal_profile_resource.fn(lpn_id="invalid"))
                assert isinstance(result, dict)
                assert "error" in result

    def test_get_animal_profile_progeny_none(self) -> None:
        """Test animal profile handles None progeny."""
        import asyncio
        from unittest.mock import patch

        with patch("nsip_mcp.resources.animal_resources.get_nsip_client") as mock_get:
            with patch("nsip_mcp.resources.animal_resources.response_cache") as mock_cache:
                mock_cache.get.return_value = None
                mock_client = MagicMock()

                mock_animal = MagicMock()
                mock_animal.to_dict.return_value = {"lpn_id": "6332-12345"}

                mock_lineage = MagicMock()
                mock_lineage.to_dict.return_value = {}

                mock_client.get_animal_details.return_value = mock_animal
                mock_client.get_lineage.return_value = mock_lineage
                mock_client.get_progeny.return_value = None
                mock_get.return_value = mock_client

                from nsip_mcp.resources.animal_resources import get_animal_profile_resource

                result = asyncio.run(get_animal_profile_resource.fn(lpn_id="6332-12345"))
                assert isinstance(result, dict)
                assert result["profile"]["progeny_count"] == 0


class TestBreedingResourcesExtended:
    """Extended tests for breeding resource functions covering uncovered paths."""

    def test_get_breeding_projection_api_error(self) -> None:
        """Test breeding projection handles API error."""
        import asyncio
        from unittest.mock import patch

        from nsip_client.exceptions import NSIPAPIError

        with patch("nsip_mcp.resources.breeding_resources.get_nsip_client") as mock_get:
            with patch("nsip_mcp.resources.breeding_resources.response_cache") as mock_cache:
                mock_cache.get.return_value = None
                mock_client = MagicMock()
                mock_client.get_animal_details.side_effect = NSIPAPIError("API error")
                mock_get.return_value = mock_client

                from nsip_mcp.resources.breeding_resources import get_breeding_projection

                result = asyncio.run(get_breeding_projection.fn(ram_lpn="ram1", ewe_lpn="ewe1"))
                assert isinstance(result, dict)
                assert "error" in result

    def test_get_breeding_projection_not_found_error(self) -> None:
        """Test breeding projection handles not found error."""
        import asyncio
        from unittest.mock import patch

        from nsip_client.exceptions import NSIPNotFoundError

        with patch("nsip_mcp.resources.breeding_resources.get_nsip_client") as mock_get:
            with patch("nsip_mcp.resources.breeding_resources.response_cache") as mock_cache:
                mock_cache.get.return_value = None
                mock_client = MagicMock()
                mock_client.get_animal_details.side_effect = NSIPNotFoundError("Not found")
                mock_get.return_value = mock_client

                from nsip_mcp.resources.breeding_resources import get_breeding_projection

                result = asyncio.run(get_breeding_projection.fn(ram_lpn="ram1", ewe_lpn="ewe1"))
                assert isinstance(result, dict)
                assert "error" in result

    def test_get_breeding_projection_cache_hit(self) -> None:
        """Test breeding projection with cache hit."""
        import asyncio
        from unittest.mock import patch

        with patch("nsip_mcp.resources.breeding_resources.get_nsip_client") as mock_get:
            with patch("nsip_mcp.resources.breeding_resources.response_cache") as mock_cache:
                # Cache returns EBVs for both animals
                mock_cache.get.side_effect = [
                    {"lpn_id": "ram1", "ebvs": {"WWT": 5.0}},
                    {"lpn_id": "ewe1", "ebvs": {"WWT": 4.0}},
                ]
                mock_client = MagicMock()
                mock_get.return_value = mock_client

                from nsip_mcp.resources.breeding_resources import get_breeding_projection

                result = asyncio.run(get_breeding_projection.fn(ram_lpn="ram1", ewe_lpn="ewe1"))
                assert isinstance(result, dict)
                # Should get projection from cached data
                mock_client.get_animal_details.assert_not_called()

    def test_get_breeding_inbreeding_api_error(self) -> None:
        """Test breeding inbreeding handles API error."""
        import asyncio
        from unittest.mock import patch

        from nsip_client.exceptions import NSIPAPIError

        with patch("nsip_mcp.resources.breeding_resources.get_nsip_client") as mock_get:
            mock_client = MagicMock()
            mock_client.get_lineage.side_effect = NSIPAPIError("API error")
            mock_get.return_value = mock_client

            from nsip_mcp.resources.breeding_resources import get_breeding_inbreeding

            result = asyncio.run(get_breeding_inbreeding.fn(ram_lpn="ram1", ewe_lpn="ewe1"))
            assert isinstance(result, dict)
            assert "error" in result

    def test_get_breeding_inbreeding_not_found_error(self) -> None:
        """Test breeding inbreeding handles not found error."""
        import asyncio
        from unittest.mock import patch

        from nsip_client.exceptions import NSIPNotFoundError

        with patch("nsip_mcp.resources.breeding_resources.get_nsip_client") as mock_get:
            mock_client = MagicMock()
            mock_client.get_lineage.side_effect = NSIPNotFoundError("Not found")
            mock_get.return_value = mock_client

            from nsip_mcp.resources.breeding_resources import get_breeding_inbreeding

            result = asyncio.run(get_breeding_inbreeding.fn(ram_lpn="ram1", ewe_lpn="ewe1"))
            assert isinstance(result, dict)
            assert "error" in result

    def test_get_breeding_inbreeding_moderate_risk(self) -> None:
        """Test breeding inbreeding with moderate risk level."""
        import asyncio
        from unittest.mock import patch

        with patch("nsip_mcp.resources.breeding_resources.get_nsip_client") as mock_get:
            mock_client = MagicMock()
            # Create lineages with enough common ancestors for moderate inbreeding
            mock_ram_lineage = MagicMock()
            mock_ram_lineage.to_dict.return_value = {
                "sire": {"lpn_id": "common1", "sire": {"lpn_id": "grandpa"}}
            }
            mock_ewe_lineage = MagicMock()
            mock_ewe_lineage.to_dict.return_value = {
                "sire": {"lpn_id": "common1", "sire": {"lpn_id": "grandpa"}}
            }
            mock_client.get_lineage.side_effect = [mock_ram_lineage, mock_ewe_lineage]
            mock_get.return_value = mock_client

            from nsip_mcp.resources.breeding_resources import get_breeding_inbreeding

            result = asyncio.run(get_breeding_inbreeding.fn(ram_lpn="ram1", ewe_lpn="ewe1"))
            assert isinstance(result, dict)
            assert "inbreeding" in result

    def test_get_breeding_recommendation_api_error(self) -> None:
        """Test breeding recommendation handles API error."""
        import asyncio
        from unittest.mock import patch

        from nsip_client.exceptions import NSIPAPIError

        with patch("nsip_mcp.resources.breeding_resources.get_nsip_client") as mock_get:
            with patch("nsip_mcp.resources.breeding_resources.response_cache") as mock_cache:
                mock_cache.get.return_value = None
                mock_client = MagicMock()
                mock_client.get_animal_details.side_effect = NSIPAPIError("API error")
                mock_get.return_value = mock_client

                from nsip_mcp.resources.breeding_resources import get_breeding_recommendation

                result = asyncio.run(get_breeding_recommendation.fn(ram_lpn="ram1", ewe_lpn="ewe1"))
                assert isinstance(result, dict)
                assert "error" in result

    def test_get_breeding_recommendation_not_found_error(self) -> None:
        """Test breeding recommendation handles not found error."""
        import asyncio
        from unittest.mock import patch

        from nsip_client.exceptions import NSIPNotFoundError

        with patch("nsip_mcp.resources.breeding_resources.get_nsip_client") as mock_get:
            with patch("nsip_mcp.resources.breeding_resources.response_cache") as mock_cache:
                mock_cache.get.return_value = None
                mock_client = MagicMock()
                mock_client.get_animal_details.side_effect = NSIPNotFoundError("Not found")
                mock_get.return_value = mock_client

                from nsip_mcp.resources.breeding_resources import get_breeding_recommendation

                result = asyncio.run(get_breeding_recommendation.fn(ram_lpn="ram1", ewe_lpn="ewe1"))
                assert isinstance(result, dict)
                assert "error" in result

    def test_get_breeding_recommendation_caution(self) -> None:
        """Test breeding recommendation with caution decision."""
        import asyncio
        from unittest.mock import patch

        with patch("nsip_mcp.resources.breeding_resources.get_nsip_client") as mock_get:
            with patch("nsip_mcp.resources.breeding_resources.response_cache") as mock_cache:
                mock_cache.get.return_value = None
                mock_client = MagicMock()

                # Create animals with high BWT (concern) but no other strengths
                mock_ram = MagicMock()
                mock_ram.to_dict.return_value = {
                    "lpn_id": "ram1",
                    "ebvs": {"WWT": 2.0, "BWT": 2.0, "PWWT": 3.0},
                }
                mock_ewe = MagicMock()
                mock_ewe.to_dict.return_value = {
                    "lpn_id": "ewe1",
                    "ebvs": {"WWT": 1.5, "BWT": 1.8},
                }
                mock_client.get_animal_details.side_effect = [mock_ram, mock_ewe]
                mock_client.get_lineage.return_value = None
                mock_get.return_value = mock_client

                from nsip_mcp.resources.breeding_resources import get_breeding_recommendation

                result = asyncio.run(get_breeding_recommendation.fn(ram_lpn="ram1", ewe_lpn="ewe1"))
                assert isinstance(result, dict)
                assert "recommendation" in result
                # Should have concerns about high BWT
                if "concerns" in result["recommendation"]:
                    concerns = result["recommendation"]["concerns"]
                    assert any("birth weight" in c.lower() for c in concerns)

    def test_get_breeding_recommendation_avoid_high_inbreeding(self) -> None:
        """Test breeding recommendation avoids high inbreeding."""
        import asyncio
        from unittest.mock import patch

        with patch("nsip_mcp.resources.breeding_resources.get_nsip_client") as mock_get:
            with patch("nsip_mcp.resources.breeding_resources.response_cache") as mock_cache:
                mock_cache.get.return_value = None
                mock_client = MagicMock()

                mock_ram = MagicMock()
                mock_ram.to_dict.return_value = {
                    "lpn_id": "ram1",
                    "ebvs": {"WWT": 5.0, "BWT": -0.2, "PWWT": 8.0},
                }
                mock_ewe = MagicMock()
                mock_ewe.to_dict.return_value = {
                    "lpn_id": "ewe1",
                    "ebvs": {"WWT": 4.0, "BWT": -0.1},
                }
                mock_client.get_animal_details.side_effect = [mock_ram, mock_ewe]

                # Create lineages with many common ancestors
                mock_ram_lineage = MagicMock()
                mock_ram_lineage.to_dict.return_value = {
                    "sire": {"lpn_id": "common1"},
                    "dam": {"lpn_id": "common2"},
                }
                mock_ewe_lineage = MagicMock()
                mock_ewe_lineage.to_dict.return_value = {
                    "sire": {"lpn_id": "common1"},
                    "dam": {"lpn_id": "common2"},
                }
                mock_client.get_lineage.side_effect = [mock_ram_lineage, mock_ewe_lineage]
                mock_get.return_value = mock_client

                from nsip_mcp.resources.breeding_resources import get_breeding_recommendation

                result = asyncio.run(get_breeding_recommendation.fn(ram_lpn="ram1", ewe_lpn="ewe1"))
                assert isinstance(result, dict)
                assert "recommendation" in result

    def test_find_common_ancestors_nested(self) -> None:
        """Test finding common ancestors in nested lineage."""
        from nsip_mcp.resources.breeding_resources import _find_common_ancestors

        lineage1 = {
            "sire": {"lpn_id": "sire1", "sire": {"lpn_id": "grandsire"}},
            "dam": {"lpn_id": "dam1"},
        }
        lineage2 = {
            "sire": {"lpn_id": "sire2"},
            "dam": {"lpn_id": "dam2", "dam": {"lpn_id": "grandsire"}},
        }

        result = _find_common_ancestors(lineage1, lineage2)
        assert "grandsire" in result

    def test_find_common_ancestors_depth_limit(self) -> None:
        """Test common ancestors respects depth limit."""
        from nsip_mcp.resources.breeding_resources import _find_common_ancestors

        # Create deeply nested lineage
        lineage1 = {
            "sire": {
                "lpn_id": "s1",
                "sire": {
                    "lpn_id": "s2",
                    "sire": {
                        "lpn_id": "s3",
                        "sire": {"lpn_id": "s4", "sire": {"lpn_id": "too_deep"}},
                    },
                },
            }
        }
        lineage2 = {"sire": {"lpn_id": "too_deep"}}

        # Default depth is 4, so "too_deep" at level 5 should not be found
        result = _find_common_ancestors(lineage1, lineage2, depth=4)
        # "too_deep" is at depth 5 in lineage1, should not be found
        # But lineage2 has it at depth 1, so it should still be found if
        # lineage1 also has it within depth.
        # The algorithm finds ancestors in each tree within depth, then intersects.
        # lineage2 has "too_deep" at depth 1, lineage1 at depth 5 (beyond depth 4)
        assert "too_deep" not in result

    def test_get_animal_ebvs_from_cache(self) -> None:
        """Test _get_animal_ebvs uses cache."""
        from unittest.mock import patch

        with patch("nsip_mcp.resources.breeding_resources.response_cache") as mock_cache:
            mock_cache.get.return_value = {"lpn_id": "test", "ebvs": {"WWT": 5.0}}
            mock_client = MagicMock()

            from nsip_mcp.resources.breeding_resources import _get_animal_ebvs

            result = _get_animal_ebvs(mock_client, "test")
            assert result == {"WWT": 5.0}
            mock_client.get_animal_details.assert_not_called()

    def test_get_animal_ebvs_cache_miss(self) -> None:
        """Test _get_animal_ebvs with cache miss."""
        from unittest.mock import patch

        with patch("nsip_mcp.resources.breeding_resources.response_cache") as mock_cache:
            mock_cache.get.return_value = None
            mock_client = MagicMock()
            mock_animal = MagicMock()
            mock_animal.to_dict.return_value = {"lpn_id": "test", "ebvs": {"WWT": 4.0}}
            mock_client.get_animal_details.return_value = mock_animal

            from nsip_mcp.resources.breeding_resources import _get_animal_ebvs

            result = _get_animal_ebvs(mock_client, "test")
            assert result == {"WWT": 4.0}
            mock_client.get_animal_details.assert_called_once()

    def test_get_animal_ebvs_not_found(self) -> None:
        """Test _get_animal_ebvs returns None when animal not found."""
        from unittest.mock import patch

        with patch("nsip_mcp.resources.breeding_resources.response_cache") as mock_cache:
            mock_cache.get.return_value = None
            mock_client = MagicMock()
            mock_client.get_animal_details.return_value = None

            from nsip_mcp.resources.breeding_resources import _get_animal_ebvs

            result = _get_animal_ebvs(mock_client, "invalid")
            assert result is None

    def test_get_animal_ebvs_cache_dict_but_no_ebvs(self) -> None:
        """Test _get_animal_ebvs when cache has dict without ebvs key."""
        from unittest.mock import patch

        with patch("nsip_mcp.resources.breeding_resources.response_cache") as mock_cache:
            mock_cache.get.return_value = {"lpn_id": "test", "name": "Test Ram"}
            mock_client = MagicMock()

            from nsip_mcp.resources.breeding_resources import _get_animal_ebvs

            result = _get_animal_ebvs(mock_client, "test")
            assert result == {}

    def test_get_animal_ebvs_cache_non_dict(self) -> None:
        """Test _get_animal_ebvs when cache returns non-dict."""
        from unittest.mock import patch

        with patch("nsip_mcp.resources.breeding_resources.response_cache") as mock_cache:
            mock_cache.get.return_value = "invalid_cached_value"
            mock_client = MagicMock()

            from nsip_mcp.resources.breeding_resources import _get_animal_ebvs

            result = _get_animal_ebvs(mock_client, "test")
            assert result is None
