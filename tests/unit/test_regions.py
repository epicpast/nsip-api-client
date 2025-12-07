"""Unit tests for shepherd regions module.

Tests for region detection and context functions.
"""

from unittest.mock import patch

from nsip_mcp.shepherd.regions import (
    NSIP_REGIONS,
    detect_region,
    get_region_context,
    get_regional_adaptation,
    list_all_regions,
)


class TestNSIPRegionsConstants:
    """Tests for NSIP regions constant dictionary."""

    def test_nsip_regions_exists(self) -> None:
        """Test NSIP_REGIONS dictionary exists and has entries."""
        assert isinstance(NSIP_REGIONS, dict)
        assert len(NSIP_REGIONS) >= 6

    def test_northeast_region(self) -> None:
        """Test northeast region data."""
        northeast = NSIP_REGIONS.get("northeast")
        assert northeast is not None
        assert northeast["id"] == "northeast"
        assert northeast["name"] == "Northeast"
        assert "ME" in northeast["states"]
        assert "NH" in northeast["states"]

    def test_southeast_region(self) -> None:
        """Test southeast region data."""
        southeast = NSIP_REGIONS.get("southeast")
        assert southeast is not None
        assert southeast["id"] == "southeast"
        assert "GA" in southeast["states"]
        assert "FL" in southeast["states"]

    def test_midwest_region(self) -> None:
        """Test midwest region data."""
        midwest = NSIP_REGIONS.get("midwest")
        assert midwest is not None
        assert midwest["id"] == "midwest"
        assert "OH" in midwest["states"]
        assert "IN" in midwest["states"]
        assert midwest["climate"] == "continental"

    def test_southwest_region(self) -> None:
        """Test southwest region data."""
        southwest = NSIP_REGIONS.get("southwest")
        assert southwest is not None
        assert southwest["id"] == "southwest"
        assert "TX" in southwest["states"]
        assert "AZ" in southwest["states"]

    def test_mountain_region(self) -> None:
        """Test mountain region data."""
        mountain = NSIP_REGIONS.get("mountain")
        assert mountain is not None
        assert mountain["id"] == "mountain"
        assert "CO" in mountain["states"]
        assert "MT" in mountain["states"]

    def test_pacific_region(self) -> None:
        """Test pacific region data."""
        pacific = NSIP_REGIONS.get("pacific")
        assert pacific is not None
        assert pacific["id"] == "pacific"
        assert "CA" in pacific["states"]
        assert "WA" in pacific["states"]

    def test_all_regions_have_required_fields(self) -> None:
        """Test all regions have required fields."""
        required_fields = ["id", "name", "states", "climate", "typical_lambing", "parasite_season"]
        for region_id, region in NSIP_REGIONS.items():
            for field in required_fields:
                assert field in region, f"Region {region_id} missing field {field}"


class TestDetectRegion:
    """Tests for detect_region function."""

    def test_detect_region_by_state_ohio(self) -> None:
        """Test region detection by state code - Ohio."""
        result = detect_region(state="OH")
        assert result == "midwest"

    def test_detect_region_by_state_texas(self) -> None:
        """Test region detection by state code - Texas."""
        result = detect_region(state="TX")
        assert result == "southwest"

    def test_detect_region_by_state_california(self) -> None:
        """Test region detection by state code - California."""
        result = detect_region(state="CA")
        assert result == "pacific"

    def test_detect_region_by_state_colorado(self) -> None:
        """Test region detection by state code - Colorado."""
        result = detect_region(state="CO")
        assert result == "mountain"

    def test_detect_region_by_state_georgia(self) -> None:
        """Test region detection by state code - Georgia."""
        result = detect_region(state="GA")
        assert result == "southeast"

    def test_detect_region_by_state_maine(self) -> None:
        """Test region detection by state code - Maine."""
        result = detect_region(state="ME")
        assert result == "northeast"

    def test_detect_region_by_state_lowercase(self) -> None:
        """Test region detection with lowercase state code."""
        result = detect_region(state="oh")
        assert result == "midwest"

    def test_detect_region_by_state_invalid(self) -> None:
        """Test region detection with invalid state code."""
        result = detect_region(state="XX")
        assert result is None

    def test_detect_region_by_zip_northeast(self) -> None:
        """Test region detection by ZIP code - Northeast."""
        result = detect_region(zip_code="01234")
        assert result == "northeast"

    def test_detect_region_by_zip_southeast(self) -> None:
        """Test region detection by ZIP code - Southeast."""
        result = detect_region(zip_code="30301")
        assert result == "southeast"

    def test_detect_region_by_zip_midwest(self) -> None:
        """Test region detection by ZIP code - Midwest."""
        result = detect_region(zip_code="43201")
        assert result == "midwest"

    def test_detect_region_by_zip_southwest(self) -> None:
        """Test region detection by ZIP code - Southwest."""
        result = detect_region(zip_code="75001")
        assert result == "southwest"

    def test_detect_region_by_zip_mountain(self) -> None:
        """Test region detection by ZIP code - Mountain."""
        result = detect_region(zip_code="80202")
        assert result == "mountain"

    def test_detect_region_by_zip_pacific(self) -> None:
        """Test region detection by ZIP code - Pacific."""
        result = detect_region(zip_code="90210")
        assert result == "pacific"

    def test_detect_region_state_takes_priority(self) -> None:
        """Test that state takes priority over ZIP code."""
        # State OH is Midwest, but ZIP 90210 is Pacific
        result = detect_region(state="OH", zip_code="90210")
        assert result == "midwest"

    def test_detect_region_no_inputs(self) -> None:
        """Test region detection with no inputs."""
        result = detect_region()
        assert result is None

    def test_detect_region_flock_prefix_not_implemented(self) -> None:
        """Test region detection by flock prefix returns None (not implemented)."""
        result = detect_region(flock_prefix="6332")
        assert result is None


class TestGetRegionContext:
    """Tests for get_region_context function."""

    def test_get_midwest_context(self) -> None:
        """Test getting context for midwest region."""
        result = get_region_context("midwest")
        assert isinstance(result, dict)
        assert result["id"] == "midwest"
        assert "name" in result
        assert "states" in result
        assert "climate" in result

    def test_get_pacific_context(self) -> None:
        """Test getting context for pacific region."""
        result = get_region_context("pacific")
        assert isinstance(result, dict)
        assert result["id"] == "pacific"
        assert "CA" in result["states"]

    def test_get_unknown_region_context(self) -> None:
        """Test getting context for unknown region falls back to static data."""
        # Unknown region still works using static NSIP_REGIONS fallback
        # when knowledge base raises error
        with patch("nsip_mcp.shepherd.regions.get_region_info") as mock_kb:
            mock_kb.return_value = None  # KB returns None for unknown
            result = get_region_context("unknown_region")
            assert isinstance(result, dict)
            assert result["id"] == "unknown_region"
            # Should still return some structure even for unknown region

    def test_context_has_all_fields(self) -> None:
        """Test that context includes all expected fields."""
        result = get_region_context("midwest")
        expected_fields = [
            "id",
            "name",
            "states",
            "climate",
            "typical_lambing",
            "parasite_season",
            "primary_breeds",
            "challenges",
            "opportunities",
        ]
        for field in expected_fields:
            assert field in result, f"Missing field: {field}"

    def test_context_merges_kb_data(self) -> None:
        """Test that context merges knowledge base data."""
        with patch("nsip_mcp.shepherd.regions.get_region_info") as mock_kb:
            mock_kb.return_value = {
                "name": "Midwest Region",
                "climate": "continental - warm summers, cold winters",
                "primary_breeds": ["Suffolk", "Hampshire"],
                "challenges": ["Winter stress"],
            }
            result = get_region_context("midwest")

            assert result["name"] == "Midwest Region"
            assert "Suffolk" in result["primary_breeds"]
            assert "Winter stress" in result["challenges"]


class TestListAllRegions:
    """Tests for list_all_regions function."""

    def test_list_all_regions_returns_list(self) -> None:
        """Test that list_all_regions returns a list."""
        result = list_all_regions()
        assert isinstance(result, list)
        assert len(result) >= 6

    def test_list_regions_has_required_fields(self) -> None:
        """Test that each region in list has required fields."""
        result = list_all_regions()
        for region in result:
            assert "id" in region
            assert "name" in region
            assert "states" in region

    def test_list_regions_includes_midwest(self) -> None:
        """Test that midwest is in the list."""
        result = list_all_regions()
        region_ids = [r["id"] for r in result]
        assert "midwest" in region_ids

    def test_list_regions_from_kb(self) -> None:
        """Test that list_all_regions uses knowledge base when available."""
        with patch("nsip_mcp.shepherd.regions.list_regions") as mock_kb:
            mock_kb.return_value = ["midwest", "pacific", "southeast"]
            result = list_all_regions()

            assert len(result) == 3
            region_ids = [r["id"] for r in result]
            assert "midwest" in region_ids

    def test_list_regions_fallback_to_static(self) -> None:
        """Test fallback to static data when KB returns empty."""
        with patch("nsip_mcp.shepherd.regions.list_regions") as mock_kb:
            mock_kb.return_value = []  # Empty from KB
            result = list_all_regions()

            # Should fall back to NSIP_REGIONS
            assert len(result) >= 6


class TestGetRegionalAdaptation:
    """Tests for get_regional_adaptation function."""

    def test_breeding_adaptation(self) -> None:
        """Test regional adaptation for breeding topic."""
        result = get_regional_adaptation("midwest", "breeding")
        assert isinstance(result, dict)
        assert "region" in result
        assert "general_notes" in result
        assert "breed_recommendations" in result

    def test_health_adaptation(self) -> None:
        """Test regional adaptation for health topic."""
        result = get_regional_adaptation("midwest", "health")
        assert isinstance(result, dict)
        assert "region" in result
        assert "general_notes" in result
        assert "challenges" in result

    def test_calendar_adaptation(self) -> None:
        """Test regional adaptation for calendar topic."""
        result = get_regional_adaptation("midwest", "calendar")
        assert isinstance(result, dict)
        assert "region" in result
        assert "general_notes" in result
        assert "timing_adjustments" in result

    def test_economics_adaptation(self) -> None:
        """Test regional adaptation for economics topic."""
        result = get_regional_adaptation("midwest", "economics")
        assert isinstance(result, dict)
        assert "region" in result
        assert "general_notes" in result
        assert "market_considerations" in result

    def test_unknown_topic_adaptation(self) -> None:
        """Test regional adaptation for unknown topic."""
        result = get_regional_adaptation("midwest", "unknown_topic")
        assert isinstance(result, dict)
        assert "region" in result
        # Should still return base structure

    def test_breeding_notes_content(self) -> None:
        """Test that breeding notes contain expected content."""
        result = get_regional_adaptation("midwest", "breeding")
        notes = result["general_notes"]
        assert len(notes) >= 1
        # Notes should mention breeds or lambing season
        combined = " ".join(notes)
        assert "breed" in combined.lower() or "lambing" in combined.lower()

    def test_health_notes_content(self) -> None:
        """Test that health notes contain expected content."""
        result = get_regional_adaptation("midwest", "health")
        notes = result["general_notes"]
        assert len(notes) >= 1
        # Notes should mention parasites or climate
        combined = " ".join(notes)
        assert "parasite" in combined.lower() or "climate" in combined.lower()

    def test_calendar_timing_adjustments(self) -> None:
        """Test calendar timing adjustments structure."""
        result = get_regional_adaptation("midwest", "calendar")
        timing = result.get("timing_adjustments", {})
        assert "lambing" in timing or "parasite_management" in timing


class TestStateToRegionMapping:
    """Tests for state to region mapping functionality."""

    def test_all_states_mapped(self) -> None:
        """Test that all states in NSIP_REGIONS are properly mapped."""
        for region_id, region in NSIP_REGIONS.items():
            for state in region["states"]:
                detected = detect_region(state=state)
                assert (
                    detected == region_id
                ), f"State {state} should map to {region_id}, got {detected}"

    def test_midwest_states(self) -> None:
        """Test all midwest states are mapped correctly."""
        midwest_states = ["OH", "IN", "IL", "MI", "WI", "MN", "IA", "MO", "ND", "SD", "NE", "KS"]
        for state in midwest_states:
            assert detect_region(state=state) == "midwest"

    def test_pacific_states(self) -> None:
        """Test all pacific states are mapped correctly."""
        pacific_states = ["WA", "OR", "CA", "AK", "HI"]
        for state in pacific_states:
            assert detect_region(state=state) == "pacific"

    def test_mountain_states(self) -> None:
        """Test all mountain states are mapped correctly."""
        mountain_states = ["MT", "WY", "CO", "UT", "ID", "NV"]
        for state in mountain_states:
            assert detect_region(state=state) == "mountain"
