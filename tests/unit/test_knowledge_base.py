"""Unit tests for the knowledge base module."""

import pytest

from nsip_mcp.knowledge_base import (
    get_calendar_template,
    get_disease_guide,
    get_economics_template,
    get_heritabilities,
    get_nutrition_guide,
    get_region_info,
    get_selection_index,
    get_trait_glossary,
    get_trait_info,
    list_regions,
    list_selection_indexes,
    list_traits,
)
from nsip_mcp.knowledge_base.loader import KnowledgeBaseError


class TestHeritabilities:
    """Tests for heritability data access."""

    def test_get_all_heritabilities(self) -> None:
        """Test getting all heritabilities without breed filter."""
        result = get_heritabilities()
        assert isinstance(result, dict)
        assert len(result) > 0
        # Check for expected traits
        assert "WWT" in result or "BWT" in result

    def test_get_heritabilities_by_breed(self) -> None:
        """Test getting heritabilities for a specific breed."""
        result = get_heritabilities("katahdin")
        assert isinstance(result, dict)
        # Should return default values if breed not found
        assert len(result) > 0

    def test_heritability_values_are_floats(self) -> None:
        """Test that heritability values are floats between 0 and 1."""
        result = get_heritabilities()
        for trait, value in result.items():
            assert isinstance(value, (int, float))
            assert 0 <= value <= 1, f"Heritability for {trait} out of range: {value}"


class TestDiseaseGuide:
    """Tests for disease guide data access."""

    def test_get_disease_guide_midwest(self) -> None:
        """Test getting disease guide for midwest region."""
        result = get_disease_guide("midwest")
        assert isinstance(result, (list, dict))

    def test_get_disease_guide_unknown_region(self) -> None:
        """Test getting disease guide for unknown region returns data."""
        result = get_disease_guide("unknown")
        # Should return general diseases or empty
        assert isinstance(result, (list, dict))


class TestNutritionGuide:
    """Tests for nutrition guide data access."""

    def test_get_nutrition_guide_no_params(self) -> None:
        """Test getting nutrition guide without parameters."""
        result = get_nutrition_guide()
        assert isinstance(result, dict)

    def test_get_nutrition_guide_with_region(self) -> None:
        """Test getting nutrition guide with region."""
        result = get_nutrition_guide(region="midwest")
        assert isinstance(result, dict)

    def test_get_nutrition_guide_with_season(self) -> None:
        """Test getting nutrition guide with season."""
        result = get_nutrition_guide(season="winter")
        assert isinstance(result, dict)

    def test_get_nutrition_guide_with_both(self) -> None:
        """Test getting nutrition guide with region and season."""
        result = get_nutrition_guide(region="midwest", season="summer")
        assert isinstance(result, dict)


class TestSelectionIndex:
    """Tests for selection index data access."""

    def test_get_selection_index_terminal(self) -> None:
        """Test getting terminal selection index."""
        result = get_selection_index("terminal")
        assert isinstance(result, dict)
        assert "name" in result or "description" in result or "traits" in result

    def test_get_selection_index_maternal(self) -> None:
        """Test getting maternal selection index."""
        result = get_selection_index("maternal")
        assert isinstance(result, dict)

    def test_get_selection_index_hair(self) -> None:
        """Test getting hair selection index."""
        result = get_selection_index("hair")
        assert isinstance(result, dict)

    def test_get_selection_index_balanced(self) -> None:
        """Test getting balanced selection index."""
        result = get_selection_index("balanced")
        assert isinstance(result, dict)

    def test_list_selection_indexes(self) -> None:
        """Test listing all selection indexes."""
        result = list_selection_indexes()
        assert isinstance(result, list)
        assert len(result) > 0


class TestTraitGlossary:
    """Tests for trait glossary data access."""

    def test_get_trait_glossary(self) -> None:
        """Test getting complete trait glossary."""
        result = get_trait_glossary()
        assert isinstance(result, dict)
        assert len(result) > 0

    def test_get_trait_info_ww(self) -> None:
        """Test getting info for weaning weight trait."""
        result = get_trait_info("WWT")
        assert isinstance(result, dict)
        assert "name" in result or "description" in result

    def test_get_trait_info_case_insensitive(self) -> None:
        """Test trait info lookup is case insensitive."""
        result = get_trait_info("wWT")
        assert isinstance(result, dict)

    def test_get_trait_info_invalid(self) -> None:
        """Test getting info for invalid trait raises error."""
        with pytest.raises(KnowledgeBaseError):
            get_trait_info("INVALID_TRAIT_XYZ")

    def test_list_traits(self) -> None:
        """Test listing all traits."""
        result = list_traits()
        assert isinstance(result, list)
        assert len(result) > 0
        # Should include common traits
        assert any(t in result for t in ["WWT", "BWT", "PWWT"])


class TestRegions:
    """Tests for region data access."""

    def test_get_region_info_midwest(self) -> None:
        """Test getting midwest region info."""
        result = get_region_info("midwest")
        assert isinstance(result, dict)
        assert "name" in result or "states" in result or "climate" in result

    def test_get_region_info_southeast(self) -> None:
        """Test getting southeast region info."""
        result = get_region_info("southeast")
        assert isinstance(result, dict)

    def test_get_region_info_unknown(self) -> None:
        """Test getting info for unknown region raises error."""
        with pytest.raises(KnowledgeBaseError):
            get_region_info("unknown")

    def test_list_regions(self) -> None:
        """Test listing all regions."""
        result = list_regions()
        assert isinstance(result, list)
        assert len(result) > 0


class TestCalendarTemplates:
    """Tests for calendar template data access."""

    def test_get_calendar_template_no_region(self) -> None:
        """Test getting calendar template without region."""
        result = get_calendar_template()
        assert isinstance(result, dict)

    def test_get_calendar_template_with_region(self) -> None:
        """Test getting calendar template with region."""
        result = get_calendar_template("midwest")
        assert isinstance(result, dict)


class TestEconomicsTemplates:
    """Tests for economics template data access."""

    def test_get_economics_template_no_category(self) -> None:
        """Test getting economics template without category."""
        result = get_economics_template()
        assert isinstance(result, dict)

    def test_get_economics_template_feed_costs(self) -> None:
        """Test getting feed costs template."""
        result = get_economics_template("feed_costs")
        assert isinstance(result, dict)

    def test_get_economics_template_cost_templates(self) -> None:
        """Test getting cost templates."""
        result = get_economics_template("cost_templates")
        assert isinstance(result, dict)

    def test_get_economics_template_revenue_templates(self) -> None:
        """Test getting revenue templates."""
        result = get_economics_template("revenue_templates")
        assert isinstance(result, dict)


class TestKnowledgeBaseError:
    """Tests for knowledge base error handling."""

    def test_error_has_message(self) -> None:
        """Test KnowledgeBaseError has a message."""
        error = KnowledgeBaseError("Test error")
        assert str(error) == "Test error"
