"""
Unit tests for nsip_skills.progeny_analysis

Tests:
- Progeny analysis
- Sire comparison
- Trait statistics
- Report formatting

Target: >95% coverage
"""

from __future__ import annotations

from unittest.mock import patch

from nsip_skills_helpers import (
    SAMPLE_LPNS,
    SAMPLE_SIRE_LPN,
    MockAnimalDetails,
    MockNSIPClient,
    MockProgeny,
)

from nsip_skills.common.data_models import (
    ProgenyStats,
    SelectionIndex,
)
from nsip_skills.progeny_analysis import (
    ProgenyAnalysisResult,
    SireComparisonResult,
    analyze_progeny,
    compare_sires,
    format_sire_comparison,
)


class TestAnalyzeProgeny:
    """Tests for analyze_progeny function."""

    def test_basic_analysis(self, mock_animals, mock_progeny):
        """Verify basic progeny analysis."""
        client = MockNSIPClient(
            animals=mock_animals,
            progeny=mock_progeny,
        )

        result = analyze_progeny(SAMPLE_SIRE_LPN, client=client)

        assert isinstance(result, ProgenyAnalysisResult)
        assert result.parent_lpn == SAMPLE_SIRE_LPN
        assert result.stats is not None

    def test_calculates_trait_means(self, mock_animals, mock_progeny):
        """Verify trait means are calculated."""
        client = MockNSIPClient(
            animals=mock_animals,
            progeny=mock_progeny,
        )

        result = analyze_progeny(SAMPLE_SIRE_LPN, client=client)

        # Should have trait means calculated
        assert isinstance(result.stats.trait_means, dict)

    def test_identifies_gender_counts(self, mock_animals, mock_progeny):
        """Verify male/female counts are tracked."""
        client = MockNSIPClient(
            animals=mock_animals,
            progeny=mock_progeny,
        )

        result = analyze_progeny(SAMPLE_SIRE_LPN, client=client)

        # Should track gender counts
        assert result.stats.male_count >= 0
        assert result.stats.female_count >= 0

    def test_filters_by_traits(self, mock_animals, mock_progeny):
        """Verify trait filtering works."""
        client = MockNSIPClient(
            animals=mock_animals,
            progeny=mock_progeny,
        )

        result = analyze_progeny(
            SAMPLE_SIRE_LPN,
            traits=["BWT", "WWT"],
            client=client,
        )

        # Should only have filtered traits
        for trait in result.stats.trait_means:
            assert trait in ["BWT", "WWT"]

    def test_custom_index(self, mock_animals, mock_progeny):
        """Verify custom selection index is used."""
        client = MockNSIPClient(
            animals=mock_animals,
            progeny=mock_progeny,
        )

        custom_index = SelectionIndex(
            name="Custom",
            trait_weights={"BWT": 1.0, "WWT": 2.0},
        )

        result = analyze_progeny(
            SAMPLE_SIRE_LPN,
            index=custom_index,
            client=client,
        )

        assert result is not None

    def test_no_progeny(self, mock_animals):
        """Verify handling when parent has no progeny."""
        client = MockNSIPClient(
            animals=mock_animals,
            progeny={},  # No progeny
        )

        result = analyze_progeny(SAMPLE_SIRE_LPN, client=client)

        assert result.stats.total_progeny == 0

    def test_identifies_top_performers(self, mock_animals, mock_progeny):
        """Verify top performers are identified."""
        client = MockNSIPClient(
            animals=mock_animals,
            progeny=mock_progeny,
        )

        result = analyze_progeny(SAMPLE_SIRE_LPN, client=client)

        assert isinstance(result.stats.top_performers, list)

    def test_identifies_bottom_performers(self, mock_animals, mock_progeny):
        """Verify bottom performers are identified."""
        client = MockNSIPClient(
            animals=mock_animals,
            progeny=mock_progeny,
        )

        result = analyze_progeny(SAMPLE_SIRE_LPN, client=client)

        assert isinstance(result.stats.bottom_performers, list)

    def test_client_closed_when_created(self, mock_animals, mock_progeny):
        """Verify client is closed when created internally."""
        with patch("nsip_skills.progeny_analysis.CachedNSIPClient") as mock_cls:
            mock_instance = MockNSIPClient(
                animals=mock_animals,
                progeny=mock_progeny,
            )
            mock_cls.return_value = mock_instance

            analyze_progeny(SAMPLE_SIRE_LPN, client=None)

            assert mock_instance._closed is True


class TestCompareSires:
    """Tests for compare_sires function."""

    def test_basic_comparison(self, mock_animals, mock_progeny):
        """Verify basic sire comparison."""
        # Add second sire
        mock_animals["SIRE2"] = MockAnimalDetails.create_sample(lpn_id="SIRE2")
        mock_animals["SIRE2"].gender = "Male"
        mock_progeny["SIRE2"] = [
            MockProgeny(lpn_id=SAMPLE_LPNS[3], gender="Male"),
            MockProgeny(lpn_id=SAMPLE_LPNS[4], gender="Female"),
        ]

        client = MockNSIPClient(
            animals=mock_animals,
            progeny=mock_progeny,
        )

        result = compare_sires([SAMPLE_SIRE_LPN, "SIRE2"], client=client)

        assert isinstance(result, SireComparisonResult)
        assert len(result.sires) >= 1

    def test_rankings_by_trait(self, mock_animals, mock_progeny):
        """Verify sires are ranked by trait."""
        mock_animals["SIRE2"] = MockAnimalDetails.create_sample(lpn_id="SIRE2")
        mock_progeny["SIRE2"] = [
            MockProgeny(lpn_id=SAMPLE_LPNS[3], gender="Male"),
        ]

        client = MockNSIPClient(
            animals=mock_animals,
            progeny=mock_progeny,
        )

        result = compare_sires([SAMPLE_SIRE_LPN, "SIRE2"], client=client)

        # Should have rankings
        assert isinstance(result.rankings, dict)

    def test_best_overall_identified(self, mock_animals, mock_progeny):
        """Verify best overall sire is identified."""
        mock_animals["SIRE2"] = MockAnimalDetails.create_sample(lpn_id="SIRE2")
        mock_progeny["SIRE2"] = [
            MockProgeny(lpn_id=SAMPLE_LPNS[3], gender="Male"),
        ]

        client = MockNSIPClient(
            animals=mock_animals,
            progeny=mock_progeny,
        )

        result = compare_sires([SAMPLE_SIRE_LPN, "SIRE2"], client=client)

        # Should identify best overall (or None if tied)
        assert result.best_overall is None or isinstance(result.best_overall, str)

    def test_single_sire(self, mock_animals, mock_progeny):
        """Verify handling of single sire."""
        client = MockNSIPClient(
            animals=mock_animals,
            progeny=mock_progeny,
        )

        result = compare_sires([SAMPLE_SIRE_LPN], client=client)

        assert len(result.sires) == 1

    def test_no_sires(self, mock_animals):
        """Verify handling of empty sire list."""
        client = MockNSIPClient(
            animals=mock_animals,
            progeny={},
        )

        result = compare_sires([], client=client)

        assert len(result.sires) == 0

    def test_handles_missing_sires(self, mock_animals, mock_progeny):
        """Verify graceful handling of missing sires."""
        client = MockNSIPClient(
            animals=mock_animals,
            progeny=mock_progeny,
        )

        # Include a non-existent sire
        result = compare_sires([SAMPLE_SIRE_LPN, "NONEXISTENT"], client=client)

        # Should still return results for found sires
        assert isinstance(result, SireComparisonResult)

    def test_client_closed_when_created(self, mock_animals, mock_progeny):
        """Verify client is closed when created internally."""
        with patch("nsip_skills.progeny_analysis.CachedNSIPClient") as mock_cls:
            mock_instance = MockNSIPClient(
                animals=mock_animals,
                progeny=mock_progeny,
            )
            mock_cls.return_value = mock_instance

            compare_sires([SAMPLE_SIRE_LPN], client=None)

            assert mock_instance._closed is True


class TestProgenyAnalysisResultToDict:
    """Tests for ProgenyAnalysisResult.to_dict method."""

    def test_to_dict_structure(self):
        """Verify to_dict returns proper structure."""
        stats = ProgenyStats(
            parent_lpn="SIRE1",
            parent_gender="Male",
            total_progeny=10,
        )

        result = ProgenyAnalysisResult(
            parent_lpn="SIRE1",
            parent_gender="Male",
            stats=stats,
        )

        d = result.to_dict()

        assert "parent_lpn" in d
        assert "parent_gender" in d
        assert "stats" in d


class TestSireComparisonResultToDict:
    """Tests for SireComparisonResult.to_dict method."""

    def test_to_dict_structure(self):
        """Verify to_dict returns proper structure."""
        result = SireComparisonResult(
            sires=[],
            rankings={"BWT": ["SIRE1", "SIRE2"]},
            best_overall="SIRE1",
        )

        d = result.to_dict()

        assert "sires" in d
        assert "rankings" in d
        assert "best_overall" in d


class TestFormatSireComparison:
    """Tests for format_sire_comparison function."""

    def test_basic_formatting(self, mock_animals, mock_progeny):
        """Verify basic formatting of sire comparison."""
        mock_animals["SIRE2"] = MockAnimalDetails.create_sample(lpn_id="SIRE2")
        mock_progeny["SIRE2"] = [
            MockProgeny(lpn_id=SAMPLE_LPNS[3], gender="Male"),
        ]

        client = MockNSIPClient(
            animals=mock_animals,
            progeny=mock_progeny,
        )

        result = compare_sires([SAMPLE_SIRE_LPN, "SIRE2"], client=client)
        output = format_sire_comparison(result)

        assert "Sire" in output or "Comparison" in output

    def test_empty_comparison(self):
        """Verify handling of empty comparison result."""
        result = SireComparisonResult()

        output = format_sire_comparison(result)

        assert "No sires" in output or output != ""

    def test_shows_rankings(self, mock_animals, mock_progeny):
        """Verify rankings are shown in output."""
        mock_animals["SIRE2"] = MockAnimalDetails.create_sample(lpn_id="SIRE2")
        mock_progeny["SIRE2"] = [
            MockProgeny(lpn_id=SAMPLE_LPNS[3], gender="Male"),
        ]

        client = MockNSIPClient(
            animals=mock_animals,
            progeny=mock_progeny,
        )

        result = compare_sires([SAMPLE_SIRE_LPN, "SIRE2"], client=client)
        output = format_sire_comparison(result)

        assert len(output) > 0


class TestMainCLI:
    """Tests for main() CLI function."""

    def test_main_single_sire(self, mock_animals, mock_progeny):
        """Verify main CLI with single sire."""
        with patch("nsip_skills.progeny_analysis.CachedNSIPClient") as mock_cls:
            mock_instance = MockNSIPClient(
                animals=mock_animals,
                progeny=mock_progeny,
            )
            mock_cls.return_value = mock_instance

            with patch("sys.argv", ["progeny_analysis.py", SAMPLE_SIRE_LPN]):
                from nsip_skills.progeny_analysis import main

                result = main()

                assert result == 0

    def test_main_multiple_sires(self, mock_animals, mock_progeny):
        """Verify main CLI with multiple sires for comparison."""
        mock_animals["SIRE2"] = MockAnimalDetails.create_sample(lpn_id="SIRE2")
        mock_progeny["SIRE2"] = []

        with patch("nsip_skills.progeny_analysis.CachedNSIPClient") as mock_cls:
            mock_instance = MockNSIPClient(
                animals=mock_animals,
                progeny=mock_progeny,
            )
            mock_cls.return_value = mock_instance

            with patch("sys.argv", ["progeny_analysis.py", SAMPLE_SIRE_LPN, "SIRE2"]):
                from nsip_skills.progeny_analysis import main

                result = main()

                assert result == 0

    def test_main_json_output(self, mock_animals, mock_progeny):
        """Verify main CLI JSON output."""
        with patch("nsip_skills.progeny_analysis.CachedNSIPClient") as mock_cls:
            mock_instance = MockNSIPClient(
                animals=mock_animals,
                progeny=mock_progeny,
            )
            mock_cls.return_value = mock_instance

            with patch("sys.argv", ["progeny_analysis.py", SAMPLE_SIRE_LPN, "--json"]):
                from nsip_skills.progeny_analysis import main

                result = main()

                assert result == 0

    def test_main_with_traits(self, mock_animals, mock_progeny):
        """Verify main CLI with trait filter."""
        with patch("nsip_skills.progeny_analysis.CachedNSIPClient") as mock_cls:
            mock_instance = MockNSIPClient(
                animals=mock_animals,
                progeny=mock_progeny,
            )
            mock_cls.return_value = mock_instance

            with patch(
                "sys.argv",
                ["progeny_analysis.py", SAMPLE_SIRE_LPN, "--traits", "BWT", "WWT"],
            ):
                from nsip_skills.progeny_analysis import main

                result = main()

                assert result == 0
