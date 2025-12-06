"""
Unit tests for nsip_skills.selection_index

Tests:
- Preset index retrieval
- Custom index creation
- Index score calculation
- Animal ranking by index
- Statistics calculation

Target: >80% coverage
"""

from unittest.mock import patch

import pytest
from nsip_skills_helpers import MockNSIPClient

from nsip_skills.common.data_models import SelectionIndex
from nsip_skills.selection_index import (
    IndexRankings,
    IndexResult,
    calculate_index_score,
    create_custom_index,
    format_index_rankings,
    get_preset_index,
    list_preset_indexes,
    rank_by_index,
)


class TestGetPresetIndex:
    """Tests for get_preset_index function."""

    def test_get_terminal_index(self):
        """Verify terminal index retrieval."""
        index = get_preset_index("terminal")

        assert index.name == "Terminal Index"
        assert index.is_preset is True
        assert "PWWT" in index.trait_weights

    def test_get_maternal_index(self):
        """Verify maternal index retrieval."""
        index = get_preset_index("maternal")

        assert index.name == "Maternal Index"
        assert "NLW" in index.trait_weights

    def test_get_range_index(self):
        """Verify range index retrieval."""
        index = get_preset_index("range")

        assert index.is_preset is True

    def test_get_hair_index(self):
        """Verify hair index retrieval."""
        index = get_preset_index("hair")

        assert index.is_preset is True

    def test_case_insensitive(self):
        """Verify case-insensitive lookup."""
        index1 = get_preset_index("Terminal")
        index2 = get_preset_index("TERMINAL")
        index3 = get_preset_index("terminal")

        assert index1.name == index2.name == index3.name

    def test_with_index_suffix(self):
        """Verify lookup works with 'index' suffix."""
        index = get_preset_index("terminal index")

        assert index.name == "Terminal Index"

    def test_unknown_index_raises(self):
        """Verify unknown index raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            get_preset_index("nonexistent")

        assert "Unknown preset index" in str(exc_info.value)


class TestCreateCustomIndex:
    """Tests for create_custom_index function."""

    def test_basic_creation(self):
        """Verify basic custom index creation."""
        index = create_custom_index(
            name="My Index",
            trait_weights={"BWT": 0.5, "WWT": 1.0},
        )

        assert index.name == "My Index"
        assert index.trait_weights["BWT"] == 0.5
        assert index.is_preset is False

    def test_with_description(self):
        """Verify custom index with description."""
        index = create_custom_index(
            name="Commercial Index",
            trait_weights={"PWWT": 1.5, "YFAT": -0.5},
            description="Focus on growth and leanness",
        )

        assert index.description == "Focus on growth and leanness"

    def test_negative_weights(self):
        """Verify negative weights are allowed."""
        index = create_custom_index(
            name="Low BWT",
            trait_weights={"BWT": -1.0, "WWT": 0.5},
        )

        assert index.trait_weights["BWT"] == -1.0

    def test_single_trait(self):
        """Verify single trait index."""
        index = create_custom_index(
            name="WWT Only",
            trait_weights={"WWT": 1.0},
        )

        assert len(index.trait_weights) == 1


class TestIndexResult:
    """Tests for IndexResult dataclass."""

    def test_basic_creation(self):
        """Verify basic result creation."""
        result = IndexResult(
            lpn_id="TEST123",
            index_name="Terminal",
            total_score=85.5,
        )

        assert result.lpn_id == "TEST123"
        assert result.total_score == 85.5
        assert result.rank == 0

    def test_with_contributions(self):
        """Verify result with trait contributions."""
        result = IndexResult(
            lpn_id="TEST123",
            index_name="Custom",
            total_score=10.0,
            trait_contributions={"BWT": 2.0, "WWT": 8.0},
            rank=1,
            percentile=100.0,
        )

        assert result.trait_contributions["BWT"] == 2.0
        assert result.rank == 1

    def test_to_dict(self):
        """Verify result serialization."""
        result = IndexResult(
            lpn_id="TEST123",
            index_name="Test",
            total_score=50.0,
        )
        d = result.to_dict()

        assert d["lpn_id"] == "TEST123"
        assert d["total_score"] == 50.0


class TestIndexRankings:
    """Tests for IndexRankings dataclass."""

    def test_basic_creation(self):
        """Verify basic rankings creation."""
        index = SelectionIndex(name="Test", trait_weights={"A": 1.0})
        rankings = IndexRankings(index=index)

        assert rankings.index.name == "Test"
        assert rankings.results == []
        assert rankings.mean_score == 0.0

    def test_with_results(self):
        """Verify rankings with result list."""
        index = SelectionIndex(name="Test", trait_weights={"A": 1.0})
        results = [
            IndexResult(lpn_id="A", index_name="Test", total_score=100.0, rank=1),
            IndexResult(lpn_id="B", index_name="Test", total_score=80.0, rank=2),
        ]
        rankings = IndexRankings(
            index=index,
            results=results,
            mean_score=90.0,
            std_score=14.14,
        )

        assert len(rankings.results) == 2
        assert rankings.mean_score == 90.0

    def test_to_dict(self):
        """Verify rankings serialization."""
        index = SelectionIndex(name="Test", trait_weights={"A": 1.0})
        rankings = IndexRankings(index=index, mean_score=50.0)
        d = rankings.to_dict()

        assert d["mean_score"] == 50.0


class TestCalculateIndexScore:
    """Tests for calculate_index_score function."""

    def test_basic_calculation(self, mock_animals):
        """Verify basic score calculation."""
        client = MockNSIPClient(animals=mock_animals)
        index = create_custom_index("Test", {"BWT": 1.0, "WWT": 2.0})

        result = calculate_index_score(
            lpn_id=list(mock_animals.keys())[0],
            index=index,
            client=client,
        )

        assert result.lpn_id == list(mock_animals.keys())[0]
        assert result.total_score > 0
        assert "BWT" in result.trait_contributions
        assert "WWT" in result.trait_contributions

    def test_score_formula(self, mock_animals):
        """Verify score formula: sum of weight * EBV."""
        lpn_id = list(mock_animals.keys())[0]
        animal = mock_animals[lpn_id]
        client = MockNSIPClient(animals=mock_animals)

        # Simple index with known weights
        index = create_custom_index("Simple", {"BWT": 1.0})
        result = calculate_index_score(lpn_id, index, client=client)

        expected = animal.traits["BWT"].value * 1.0
        assert result.total_score == expected

    def test_missing_trait_ignored(self, mock_animals):
        """Verify missing traits don't cause errors."""
        lpn_id = list(mock_animals.keys())[0]
        client = MockNSIPClient(animals=mock_animals)

        # Index with trait not in animal data
        index = create_custom_index("Missing", {"BWT": 1.0, "NONEXISTENT": 10.0})
        result = calculate_index_score(lpn_id, index, client=client)

        # Should only include BWT contribution
        assert "NONEXISTENT" not in result.trait_contributions

    def test_client_closed(self, mock_animals):
        """Verify client is closed when created internally."""
        lpn_id = list(mock_animals.keys())[0]
        index = create_custom_index("Test", {"BWT": 1.0})

        # Patch CachedNSIPClient to track closure
        with patch("nsip_skills.selection_index.CachedNSIPClient") as mock_cls:
            mock_instance = MockNSIPClient(animals=mock_animals)
            mock_cls.return_value = mock_instance

            calculate_index_score(lpn_id, index, client=None)

            assert mock_instance._closed is True


class TestRankByIndex:
    """Tests for rank_by_index function."""

    def test_basic_ranking(self, mock_animals, sample_lpn_ids):
        """Verify basic ranking by index."""
        client = MockNSIPClient(animals=mock_animals)
        index = get_preset_index("terminal")

        rankings = rank_by_index(sample_lpn_ids, index, client=client)

        assert len(rankings.results) > 0
        # Results should be sorted by score (highest first)
        scores = [r.total_score for r in rankings.results]
        assert scores == sorted(scores, reverse=True)

    def test_ranks_assigned(self, mock_animals, sample_lpn_ids):
        """Verify ranks are assigned correctly."""
        client = MockNSIPClient(animals=mock_animals)
        index = create_custom_index("Test", {"WWT": 1.0})

        rankings = rank_by_index(sample_lpn_ids, index, client=client)

        ranks = [r.rank for r in rankings.results]
        assert ranks == list(range(1, len(rankings.results) + 1))

    def test_percentiles_assigned(self, mock_animals, sample_lpn_ids):
        """Verify percentiles are calculated."""
        client = MockNSIPClient(animals=mock_animals)
        index = create_custom_index("Test", {"BWT": 1.0})

        rankings = rank_by_index(sample_lpn_ids, index, client=client)

        # Top animal should have highest percentile
        top_percentile = rankings.results[0].percentile
        assert top_percentile > 0

    def test_statistics_calculated(self, mock_animals, sample_lpn_ids):
        """Verify mean and std are calculated."""
        client = MockNSIPClient(animals=mock_animals)
        index = create_custom_index("Test", {"WWT": 1.0})

        rankings = rank_by_index(sample_lpn_ids, index, client=client)

        assert rankings.mean_score != 0
        assert rankings.std_score >= 0

    def test_string_index_resolved(self, mock_animals, sample_lpn_ids):
        """Verify string index name is resolved."""
        client = MockNSIPClient(animals=mock_animals)

        rankings = rank_by_index(sample_lpn_ids, "terminal", client=client)

        assert rankings.index.name == "Terminal Index"

    def test_selection_thresholds(self, mock_animals, sample_lpn_ids):
        """Verify selection thresholds are calculated."""
        client = MockNSIPClient(animals=mock_animals)
        index = create_custom_index("Test", {"WWT": 1.0})

        rankings = rank_by_index(sample_lpn_ids, index, client=client)

        if len(rankings.results) >= 4:
            assert rankings.selection_threshold_25 > 0
        if len(rankings.results) >= 10:
            assert rankings.selection_threshold_10 > 0

    def test_skips_missing_animals(self, mock_animals, sample_lpn_ids):
        """Verify missing animals are skipped."""
        client = MockNSIPClient(animals=mock_animals)
        index = create_custom_index("Test", {"BWT": 1.0})

        # Add invalid LPN to list
        lpn_ids = sample_lpn_ids + ["INVALID_LPN"]

        rankings = rank_by_index(lpn_ids, index, client=client)

        # Should have results for valid LPNs only
        lpn_results = {r.lpn_id for r in rankings.results}
        assert "INVALID_LPN" not in lpn_results


class TestFormatIndexRankings:
    """Tests for format_index_rankings function."""

    def test_basic_formatting(self):
        """Verify basic rankings formatting."""
        index = SelectionIndex(
            name="Test Index",
            description="A test index",
            trait_weights={"BWT": 1.0, "WWT": 2.0},
        )
        results = [
            IndexResult(
                lpn_id="TOP1",
                index_name="Test Index",
                total_score=100.0,
                rank=1,
                trait_contributions={"BWT": 50.0, "WWT": 50.0},
            ),
            IndexResult(
                lpn_id="TOP2",
                index_name="Test Index",
                total_score=80.0,
                rank=2,
                trait_contributions={"BWT": 30.0, "WWT": 50.0},
            ),
        ]
        rankings = IndexRankings(
            index=index,
            results=results,
            mean_score=90.0,
            std_score=14.14,
        )

        output = format_index_rankings(rankings)

        assert "Test Index" in output
        assert "TOP1" in output
        assert "TOP2" in output
        assert "100" in output

    def test_with_description(self):
        """Verify description is included."""
        index = SelectionIndex(
            name="Test",
            description="Focus on growth traits",
            trait_weights={"WWT": 1.0},
        )
        rankings = IndexRankings(index=index, results=[])

        output = format_index_rankings(rankings)

        assert "Focus on growth traits" in output

    def test_limits_output(self):
        """Verify top_n limits output."""
        index = SelectionIndex(name="Test", trait_weights={"A": 1.0})
        results = [
            IndexResult(lpn_id=f"ANIMAL{i}", index_name="Test", total_score=100 - i)
            for i in range(50)
        ]
        rankings = IndexRankings(index=index, results=results)

        output = format_index_rankings(rankings, top_n=5)

        # Should contain top 5
        assert "ANIMAL0" in output
        assert "ANIMAL4" in output
        # Should not contain beyond top 5
        assert "ANIMAL10" not in output

    def test_shows_statistics(self):
        """Verify statistics are shown."""
        index = SelectionIndex(name="Test", trait_weights={"A": 1.0})
        rankings = IndexRankings(
            index=index,
            results=[],
            mean_score=75.5,
            std_score=10.2,
            selection_threshold_10=95.0,
            selection_threshold_25=85.0,
        )

        output = format_index_rankings(rankings)

        assert "75.5" in output or "75.50" in output
        assert "10.2" in output or "10.20" in output


class TestListPresetIndexes:
    """Tests for list_preset_indexes function."""

    def test_returns_all_presets(self):
        """Verify all preset indexes are listed."""
        presets = list_preset_indexes()

        assert len(presets) >= 4
        keys = [p["key"] for p in presets]
        assert "terminal" in keys
        assert "maternal" in keys
        assert "range" in keys
        assert "hair" in keys

    def test_includes_required_fields(self):
        """Verify each preset has required fields."""
        presets = list_preset_indexes()

        for preset in presets:
            assert "name" in preset
            assert "key" in preset
            assert "description" in preset
            assert "traits" in preset

    def test_traits_is_list(self):
        """Verify traits field is a list."""
        presets = list_preset_indexes()

        for preset in presets:
            assert isinstance(preset["traits"], list)
            assert len(preset["traits"]) > 0


class TestMainCLI:
    """Tests for main() CLI function."""

    def test_main_basic(self, mock_animals, sample_lpn_ids):
        """Verify main CLI with basic arguments."""
        with patch("nsip_skills.selection_index.CachedNSIPClient") as mock_cls:
            mock_instance = MockNSIPClient(animals=mock_animals)
            mock_cls.return_value = mock_instance

            with patch("sys.argv", ["selection_index.py"] + sample_lpn_ids):
                from nsip_skills.selection_index import main

                result = main()

                assert result == 0

    def test_main_json_output(self, mock_animals, sample_lpn_ids):
        """Verify main CLI with JSON output."""
        with patch("nsip_skills.selection_index.CachedNSIPClient") as mock_cls:
            mock_instance = MockNSIPClient(animals=mock_animals)
            mock_cls.return_value = mock_instance

            with patch("sys.argv", ["selection_index.py"] + sample_lpn_ids + ["--json"]):
                from nsip_skills.selection_index import main

                result = main()

                assert result == 0

    def test_main_list_presets(self, mock_animals):
        """Verify main CLI with --list-presets."""
        with patch("sys.argv", ["selection_index.py", "DUMMY", "--list-presets"]):
            from nsip_skills.selection_index import main

            result = main()

            assert result == 0

    def test_main_list_presets_json(self):
        """Verify main CLI with --list-presets --json."""
        with patch("sys.argv", ["selection_index.py", "DUMMY", "--list-presets", "--json"]):
            from nsip_skills.selection_index import main

            result = main()

            assert result == 0

    def test_main_custom_index(self, mock_animals, sample_lpn_ids):
        """Verify main CLI with custom index."""
        with patch("nsip_skills.selection_index.CachedNSIPClient") as mock_cls:
            mock_instance = MockNSIPClient(animals=mock_animals)
            mock_cls.return_value = mock_instance

            custom_json = '{"BWT": 1.0, "WWT": 2.0}'
            with patch(
                "sys.argv",
                ["selection_index.py"] + sample_lpn_ids + ["--index", f"custom:{custom_json}"],
            ):
                from nsip_skills.selection_index import main

                result = main()

                assert result == 0

    def test_main_with_top_limit(self, mock_animals, sample_lpn_ids):
        """Verify main CLI with --top limit."""
        with patch("nsip_skills.selection_index.CachedNSIPClient") as mock_cls:
            mock_instance = MockNSIPClient(animals=mock_animals)
            mock_cls.return_value = mock_instance

            with patch("sys.argv", ["selection_index.py"] + sample_lpn_ids + ["--top", "5"]):
                from nsip_skills.selection_index import main

                result = main()

                assert result == 0

    def test_rank_by_index_creates_client(self, mock_animals, sample_lpn_ids):
        """Verify rank_by_index creates and closes client when not provided."""
        with patch("nsip_skills.selection_index.CachedNSIPClient") as mock_cls:
            mock_instance = MockNSIPClient(animals=mock_animals)
            mock_cls.return_value = mock_instance

            rank_by_index(sample_lpn_ids, "terminal", client=None)

            assert mock_instance._closed is True
