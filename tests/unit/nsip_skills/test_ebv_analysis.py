"""
Unit tests for nsip_skills.ebv_analysis

Tests:
- Percentile calculation
- Trait analysis
- EBV comparison
- Breed ranges
- Report formatting

Target: >95% coverage
"""

from __future__ import annotations

from unittest.mock import patch

from nsip_skills_helpers import (
    SAMPLE_LPNS,
    MockNSIPClient,
)

from nsip_skills.common.data_models import TraitProfile
from nsip_skills.ebv_analysis import (
    LOWER_IS_BETTER,
    EBVComparison,
    analyze_traits,
    calculate_percentile,
    format_ebv_report,
    get_breed_ranges,
    main,
)


class TestLowerIsBetter:
    """Tests for LOWER_IS_BETTER constant."""

    def test_birth_weight_in_set(self):
        """Verify birth weight is in lower-is-better set."""
        assert "BWT" in LOWER_IS_BETTER

    def test_fat_traits_in_set(self):
        """Verify fat traits are in lower-is-better set."""
        assert "YFAT" in LOWER_IS_BETTER
        assert "PFAT" in LOWER_IS_BETTER
        assert "FAT" in LOWER_IS_BETTER

    def test_dag_and_fec_in_set(self):
        """Verify DAG and FEC traits are in lower-is-better set."""
        assert "DAG" in LOWER_IS_BETTER
        assert "FEC" in LOWER_IS_BETTER

    def test_wwt_not_in_set(self):
        """Verify weaning weight is NOT in lower-is-better set."""
        assert "WWT" not in LOWER_IS_BETTER


class TestCalculatePercentile:
    """Tests for calculate_percentile function."""

    def test_middle_value(self):
        """Verify 50th percentile for middle value."""
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        percentile = calculate_percentile(3.0, values)
        assert 40 <= percentile <= 60

    def test_highest_value(self):
        """Verify ~100th percentile for highest value."""
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        percentile = calculate_percentile(5.0, values)
        assert percentile >= 80

    def test_lowest_value(self):
        """Verify ~0th percentile for lowest value."""
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        percentile = calculate_percentile(1.0, values)
        # 0 values below 1.0 out of 5 total = 0%
        assert percentile <= 20

    def test_lower_better_inverts(self):
        """Verify lower_better inverts percentile ranking."""
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        # With lower_is_better=False, 5.0 ranks high
        percentile_normal = calculate_percentile(5.0, values, lower_is_better=False)
        # With lower_is_better=True, 5.0 ranks low
        percentile_inverted = calculate_percentile(5.0, values, lower_is_better=True)
        assert percentile_inverted < percentile_normal

    def test_lower_better_for_lowest_value(self):
        """Verify lowest value ranks highest when lower is better."""
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        percentile = calculate_percentile(1.0, values, lower_is_better=True)
        # With lower_is_better=True, 1.0 should be top percentile
        assert percentile >= 80

    def test_empty_values(self):
        """Verify handling of empty value list."""
        percentile = calculate_percentile(3.0, [])
        assert percentile == 50.0

    def test_single_value_matching(self):
        """Verify handling of single value matching."""
        values = [3.0]
        percentile = calculate_percentile(3.0, values)
        # 0 values below 3.0 out of 1 = 0%
        assert percentile == 0.0

    def test_value_above_range(self):
        """Verify handling of value above distribution."""
        values = [1.0, 2.0, 3.0]
        percentile = calculate_percentile(10.0, values)
        # 3 values below 10.0 out of 3 = 100%
        assert percentile == 100.0

    def test_value_below_range(self):
        """Verify handling of value below distribution."""
        values = [5.0, 6.0, 7.0]
        percentile = calculate_percentile(1.0, values)
        # 0 values below 1.0 out of 3 = 0%
        assert percentile == 0.0


class TestEBVComparison:
    """Tests for EBVComparison dataclass."""

    def test_default_values(self):
        """Verify default values are set correctly."""
        comparison = EBVComparison()
        assert comparison.profiles == []
        assert comparison.trait_stats == {}
        assert comparison.rankings == {}
        assert comparison.top_overall == []
        assert comparison.needs_work == []

    def test_to_dict_structure(self):
        """Verify to_dict returns proper structure."""
        profile = TraitProfile(lpn_id="TEST1")
        comparison = EBVComparison(
            profiles=[profile],
            trait_stats={"BWT": {"mean": 0.5, "std": 0.1, "min": 0.2, "max": 0.8}},
            rankings={"BWT": ["TEST1", "TEST2"]},
            top_overall=["TEST1"],
            needs_work=["TEST2"],
        )

        d = comparison.to_dict()

        assert "profiles" in d
        assert "trait_stats" in d
        assert "rankings" in d
        assert "top_overall" in d
        assert "needs_work" in d
        assert len(d["profiles"]) == 1
        assert d["top_overall"] == ["TEST1"]


class TestAnalyzeTraits:
    """Tests for analyze_traits function."""

    def test_basic_analysis(self, mock_animals):
        """Verify basic trait analysis returns EBVComparison."""
        client = MockNSIPClient(animals=mock_animals)
        lpn_ids = list(mock_animals.keys())[:3]

        result = analyze_traits(lpn_ids, client=client)

        assert isinstance(result, EBVComparison)
        assert len(result.profiles) > 0

    def test_with_trait_filter(self, mock_animals):
        """Verify trait filter limits analyzed traits."""
        client = MockNSIPClient(animals=mock_animals)
        lpn_ids = list(mock_animals.keys())[:3]

        result = analyze_traits(lpn_ids, traits=["BWT", "WWT"], client=client)

        # Should only have filtered traits in stats
        for trait in result.trait_stats:
            assert trait in ["BWT", "WWT"]

    def test_calculates_trait_stats(self, mock_animals):
        """Verify trait statistics are calculated."""
        client = MockNSIPClient(animals=mock_animals)
        lpn_ids = list(mock_animals.keys())[:5]

        result = analyze_traits(lpn_ids, client=client)

        # Should have stats for at least some traits
        if result.trait_stats:
            first_trait = list(result.trait_stats.keys())[0]
            stats = result.trait_stats[first_trait]
            assert "mean" in stats
            assert "std" in stats
            assert "min" in stats
            assert "max" in stats
            assert "count" in stats

    def test_single_value_std_deviation_returns_zero(self, mock_animals):
        """Verify standard deviation is 0 for single-value trait analysis.

        When only one animal has a trait value, std deviation should be 0
        (not an error), since statistics.stdev() requires at least 2 values.
        """
        # Get exactly one animal
        client = MockNSIPClient(animals=mock_animals)
        lpn_ids = list(mock_animals.keys())[:1]

        result = analyze_traits(lpn_ids, client=client)

        # Verify std is 0 for traits with only one value
        for trait_name, stats in result.trait_stats.items():
            if stats.get("count", 0) == 1:
                assert stats["std"] == 0, f"std should be 0 for single-value trait {trait_name}"

    def test_calculates_rankings(self, mock_animals):
        """Verify animals are ranked by trait."""
        client = MockNSIPClient(animals=mock_animals)
        lpn_ids = list(mock_animals.keys())[:5]

        result = analyze_traits(lpn_ids, client=client)

        # Should have rankings for traits
        if result.rankings:
            first_trait = list(result.rankings.keys())[0]
            rankings = result.rankings[first_trait]
            assert isinstance(rankings, list)
            assert len(rankings) > 0

    def test_identifies_strengths_weaknesses(self, mock_animals):
        """Verify strengths and weaknesses are identified."""
        client = MockNSIPClient(animals=mock_animals)
        lpn_ids = list(mock_animals.keys())[:5]

        result = analyze_traits(lpn_ids, client=client)

        # Each profile should have strengths/weaknesses lists
        for profile in result.profiles:
            assert isinstance(profile.strengths, list)
            assert isinstance(profile.weaknesses, list)

    def test_identifies_top_overall(self, mock_animals):
        """Verify top overall performers are identified."""
        client = MockNSIPClient(animals=mock_animals)
        lpn_ids = list(mock_animals.keys())[:5]

        result = analyze_traits(lpn_ids, client=client)

        assert isinstance(result.top_overall, list)

    def test_identifies_needs_work(self, mock_animals):
        """Verify animals needing work are identified."""
        client = MockNSIPClient(animals=mock_animals)
        lpn_ids = list(mock_animals.keys())[:5]

        result = analyze_traits(lpn_ids, client=client)

        assert isinstance(result.needs_work, list)

    def test_empty_lpn_list(self):
        """Verify handling of empty LPN list."""
        client = MockNSIPClient()

        result = analyze_traits([], client=client)

        assert result.profiles == []
        assert result.trait_stats == {}
        assert result.rankings == {}

    def test_missing_animals_handled(self, mock_animals):
        """Verify graceful handling of missing animals."""
        client = MockNSIPClient(animals=mock_animals)
        lpns = list(mock_animals.keys())[:2] + ["NONEXISTENT"]

        result = analyze_traits(lpns, client=client)

        # Should still have results for found animals
        assert isinstance(result, EBVComparison)

    def test_client_closed_when_created(self, mock_animals):
        """Verify client is closed when created internally."""
        with patch("nsip_skills.ebv_analysis.CachedNSIPClient") as mock_cls:
            mock_instance = MockNSIPClient(animals=mock_animals)
            mock_cls.return_value = mock_instance

            analyze_traits(list(mock_animals.keys())[:2], client=None)

            assert mock_instance._closed is True

    def test_client_not_closed_when_passed(self, mock_animals):
        """Verify client is not closed when passed in."""
        client = MockNSIPClient(animals=mock_animals)

        analyze_traits(list(mock_animals.keys())[:2], client=client)

        assert client._closed is False

    def test_breed_context_parameter(self, mock_animals):
        """Verify breed_context parameter is accepted."""
        client = MockNSIPClient(animals=mock_animals)
        lpns = list(mock_animals.keys())[:2]

        result = analyze_traits(lpns, breed_context=486, client=client)

        assert isinstance(result, EBVComparison)


class TestGetBreedRanges:
    """Tests for get_breed_ranges function."""

    def test_returns_ranges(self, mock_animals):
        """Verify breed ranges are returned."""
        client = MockNSIPClient(animals=mock_animals)

        result = get_breed_ranges(486, client=client)

        assert isinstance(result, dict)

    def test_client_closed_when_created(self, mock_animals):
        """Verify client is closed when created internally."""
        with patch("nsip_skills.ebv_analysis.CachedNSIPClient") as mock_cls:
            mock_instance = MockNSIPClient(animals=mock_animals)
            mock_cls.return_value = mock_instance

            get_breed_ranges(486, client=None)

            assert mock_instance._closed is True

    def test_client_not_closed_when_passed(self, mock_animals):
        """Verify client is not closed when passed in."""
        client = MockNSIPClient(animals=mock_animals)

        get_breed_ranges(486, client=client)

        assert client._closed is False


class TestFormatEbvReport:
    """Tests for format_ebv_report function."""

    def test_basic_formatting(self, mock_animals):
        """Verify basic report formatting."""
        client = MockNSIPClient(animals=mock_animals)
        comparison = analyze_traits(list(mock_animals.keys())[:3], client=client)

        output = format_ebv_report(comparison)

        assert "EBV Trait Analysis" in output
        assert len(output) > 0

    def test_includes_trait_statistics(self, mock_animals):
        """Verify trait statistics are included."""
        client = MockNSIPClient(animals=mock_animals)
        comparison = analyze_traits(list(mock_animals.keys())[:3], client=client)

        output = format_ebv_report(comparison)

        # Should mention stats if there are any
        if comparison.trait_stats:
            assert "Trait Statistics" in output or "Mean" in output

    def test_includes_animal_comparison(self, mock_animals):
        """Verify animal comparison is included."""
        client = MockNSIPClient(animals=mock_animals)
        comparison = analyze_traits(list(mock_animals.keys())[:3], client=client)

        output = format_ebv_report(comparison)

        if comparison.profiles:
            assert "Animal Comparison" in output or "Comparison" in output

    def test_includes_top_performers(self, mock_animals):
        """Verify top performers are shown."""
        client = MockNSIPClient(animals=mock_animals)
        comparison = analyze_traits(list(mock_animals.keys())[:5], client=client)

        output = format_ebv_report(comparison)

        if comparison.top_overall:
            assert "Top Performers" in output

    def test_includes_needs_improvement(self, mock_animals):
        """Verify needs improvement section is shown."""
        client = MockNSIPClient(animals=mock_animals)
        comparison = analyze_traits(list(mock_animals.keys())[:5], client=client)

        output = format_ebv_report(comparison)

        if comparison.needs_work:
            assert "Needs Improvement" in output

    def test_includes_rankings(self, mock_animals):
        """Verify rankings are shown."""
        client = MockNSIPClient(animals=mock_animals)
        comparison = analyze_traits(list(mock_animals.keys())[:3], client=client)

        output = format_ebv_report(comparison)

        if comparison.rankings:
            assert "Rankings by Trait" in output

    def test_with_trait_filter(self, mock_animals):
        """Verify trait filter is applied to output."""
        client = MockNSIPClient(animals=mock_animals)
        comparison = analyze_traits(
            list(mock_animals.keys())[:3], traits=["BWT", "WWT"], client=client
        )

        output = format_ebv_report(comparison, traits=["BWT"])

        assert len(output) > 0

    def test_handles_empty_comparison(self):
        """Verify handling of empty comparison."""
        empty_comparison = EBVComparison()

        output = format_ebv_report(empty_comparison)

        assert output is not None
        assert isinstance(output, str)
        assert "EBV Trait Analysis" in output


class TestMainCLI:
    """Tests for main() CLI function."""

    def test_main_basic(self, mock_animals):
        """Verify main CLI runs without error."""
        with patch("nsip_skills.ebv_analysis.CachedNSIPClient") as mock_cls:
            mock_instance = MockNSIPClient(animals=mock_animals)
            mock_cls.return_value = mock_instance

            with patch("sys.argv", ["ebv_analysis.py", SAMPLE_LPNS[0], SAMPLE_LPNS[1]]):
                result = main()

                assert result == 0

    def test_main_with_traits(self, mock_animals):
        """Verify main CLI with trait filter."""
        with patch("nsip_skills.ebv_analysis.CachedNSIPClient") as mock_cls:
            mock_instance = MockNSIPClient(animals=mock_animals)
            mock_cls.return_value = mock_instance

            with patch(
                "sys.argv",
                ["ebv_analysis.py", SAMPLE_LPNS[0], "--traits", "BWT", "WWT"],
            ):
                result = main()

                assert result == 0

    def test_main_json_output(self, mock_animals):
        """Verify main CLI JSON output."""
        with patch("nsip_skills.ebv_analysis.CachedNSIPClient") as mock_cls:
            mock_instance = MockNSIPClient(animals=mock_animals)
            mock_cls.return_value = mock_instance

            with patch("sys.argv", ["ebv_analysis.py", SAMPLE_LPNS[0], "--json"]):
                result = main()

                assert result == 0

    def test_main_with_breed(self, mock_animals):
        """Verify main CLI with breed context."""
        with patch("nsip_skills.ebv_analysis.CachedNSIPClient") as mock_cls:
            mock_instance = MockNSIPClient(animals=mock_animals)
            mock_cls.return_value = mock_instance

            with patch(
                "sys.argv",
                ["ebv_analysis.py", SAMPLE_LPNS[0], "--breed", "486"],
            ):
                result = main()

                assert result == 0

    def test_main_multiple_animals(self, mock_animals):
        """Verify main CLI with multiple animals."""
        with patch("nsip_skills.ebv_analysis.CachedNSIPClient") as mock_cls:
            mock_instance = MockNSIPClient(animals=mock_animals)
            mock_cls.return_value = mock_instance

            with patch(
                "sys.argv",
                ["ebv_analysis.py"] + SAMPLE_LPNS[:4],
            ):
                result = main()

                assert result == 0
