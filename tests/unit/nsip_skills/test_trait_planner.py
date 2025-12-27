"""
Unit tests for nsip_skills.trait_planner

Tests:
- Genetic gain calculation formula
- Generations-to-goal estimation
- Improvement plan creation
- Heritability usage
- Selection recommendations

Target: >80% coverage
"""

from unittest.mock import patch

from nsip_skills_helpers import SAMPLE_LPNS, MockNSIPClient

from nsip_skills.trait_planner import (
    TRAIT_HERITABILITIES,
    ImprovementPlan,
    ImprovementProjection,
    TraitGoal,
    _generate_recommendations,
    _intensity_to_pct,
    analyze_flock_traits,
    calculate_genetic_gain,
    create_improvement_plan,
    estimate_generations_to_goal,
    format_improvement_plan,
)


class TestTraitHeritabilities:
    """Tests for heritability constants."""

    def test_common_traits_defined(self):
        """Verify common traits have heritabilities."""
        required_traits = ["BWT", "WWT", "PWWT", "NLW", "MWWT"]

        for trait in required_traits:
            assert trait in TRAIT_HERITABILITIES
            assert 0 < TRAIT_HERITABILITIES[trait] < 1

    def test_heritabilities_reasonable(self):
        """Verify heritabilities are in reasonable range."""
        for trait, h2 in TRAIT_HERITABILITIES.items():
            assert 0.05 <= h2 <= 0.50, f"{trait} heritability {h2} out of range"


class TestTraitGoal:
    """Tests for TraitGoal dataclass."""

    def test_basic_creation(self):
        """Verify basic goal creation."""
        goal = TraitGoal(
            trait="WWT",
            current_mean=2.0,
            target_value=5.0,
        )

        assert goal.trait == "WWT"
        assert goal.current_mean == 2.0
        assert goal.target_value == 5.0
        assert goal.priority == 1

    def test_gap_calculation(self):
        """Verify gap property calculation."""
        goal = TraitGoal(
            trait="WWT",
            current_mean=2.0,
            target_value=5.0,
        )

        assert goal.gap == 3.0

    def test_negative_gap(self):
        """Verify negative gap (already at/above target)."""
        goal = TraitGoal(
            trait="BWT",
            current_mean=1.0,
            target_value=0.5,
        )

        assert goal.gap == -0.5


class TestCalculateGeneticGain:
    """Tests for calculate_genetic_gain function."""

    def test_basic_calculation(self):
        """Verify R = h² × i × σ_p formula."""
        # R = h² × i × σ_p
        # R = 0.25 × 1.4 × 2.0 = 0.7
        gain = calculate_genetic_gain(
            heritability=0.25,
            selection_intensity=1.4,
            phenotypic_std=2.0,
        )

        assert abs(gain - 0.7) < 0.001

    def test_higher_heritability_more_gain(self):
        """Verify higher heritability = more gain."""
        low_h2 = calculate_genetic_gain(0.1, 1.4, 2.0)
        high_h2 = calculate_genetic_gain(0.4, 1.4, 2.0)

        assert high_h2 > low_h2

    def test_higher_intensity_more_gain(self):
        """Verify higher selection intensity = more gain."""
        low_intensity = calculate_genetic_gain(0.25, 1.0, 2.0)
        high_intensity = calculate_genetic_gain(0.25, 2.0, 2.0)

        assert high_intensity > low_intensity

    def test_higher_variance_more_gain(self):
        """Verify higher phenotypic std = more gain."""
        low_std = calculate_genetic_gain(0.25, 1.4, 1.0)
        high_std = calculate_genetic_gain(0.25, 1.4, 3.0)

        assert high_std > low_std

    def test_zero_heritability(self):
        """Verify zero heritability = zero gain."""
        gain = calculate_genetic_gain(0.0, 1.4, 2.0)

        assert gain == 0.0


class TestEstimateGenerationsToGoal:
    """Tests for estimate_generations_to_goal function."""

    def test_basic_estimation(self):
        """Verify basic generation estimation."""
        # Gap of 3.0, gain of 1.0 per gen = 3 generations
        gens = estimate_generations_to_goal(
            current=2.0,
            target=5.0,
            gain_per_gen=1.0,
        )

        assert gens == 3

    def test_already_at_target(self):
        """Verify zero generations when at target."""
        gens = estimate_generations_to_goal(
            current=5.0,
            target=5.0,
            gain_per_gen=1.0,
        )

        assert gens == 0

    def test_above_target(self):
        """Verify zero generations when above target."""
        gens = estimate_generations_to_goal(
            current=6.0,
            target=5.0,
            gain_per_gen=1.0,
        )

        assert gens == 0

    def test_zero_gain(self):
        """Verify handling of zero gain."""
        gens = estimate_generations_to_goal(
            current=2.0,
            target=5.0,
            gain_per_gen=0.0,
        )

        # Should return very large number (infinite generations)
        assert gens >= 999

    def test_fractional_rounding(self):
        """Verify fractional generations are rounded."""
        # Gap of 2.5, gain of 1.0 = 2.5 gens → rounds to 3
        gens = estimate_generations_to_goal(
            current=2.0,
            target=4.5,
            gain_per_gen=1.0,
        )

        assert gens == 2 or gens == 3  # Depends on rounding


class TestImprovementProjection:
    """Tests for ImprovementProjection dataclass."""

    def test_basic_creation(self):
        """Verify basic projection creation."""
        proj = ImprovementProjection(
            trait="WWT",
            current=2.0,
            target=5.0,
            heritability=0.25,
            generations_needed=6,
            improvement_per_generation=0.5,
            projections=[2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0],
        )

        assert proj.trait == "WWT"
        assert proj.generations_needed == 6
        assert len(proj.projections) == 7

    def test_to_dict(self):
        """Verify projection serialization."""
        proj = ImprovementProjection(
            trait="BWT",
            current=0.5,
            target=0.3,
            heritability=0.30,
            generations_needed=2,
            improvement_per_generation=-0.1,
        )
        d = proj.to_dict()

        assert d["trait"] == "BWT"
        assert d["heritability"] == 0.30


class TestAnalyzeFlockTraits:
    """Tests for analyze_flock_traits function."""

    def test_basic_analysis(self, mock_animals, sample_lpn_ids):
        """Verify basic trait analysis."""
        client = MockNSIPClient(animals=mock_animals)

        result = analyze_flock_traits(sample_lpn_ids, client=client)

        assert len(result) > 0
        for _trait, stats in result.items():
            assert "mean" in stats
            assert "std" in stats
            assert "min" in stats
            assert "max" in stats
            assert "count" in stats

    def test_filter_by_traits(self, mock_animals, sample_lpn_ids):
        """Verify trait filtering."""
        client = MockNSIPClient(animals=mock_animals)

        result = analyze_flock_traits(
            sample_lpn_ids,
            traits=["BWT", "WWT"],
            client=client,
        )

        assert "BWT" in result
        assert "WWT" in result
        assert "PWWT" not in result


class TestCreateImprovementPlan:
    """Tests for create_improvement_plan function."""

    def test_basic_plan(self, mock_animals, sample_lpn_ids):
        """Verify basic plan creation."""
        client = MockNSIPClient(animals=mock_animals)

        plan = create_improvement_plan(
            sample_lpn_ids,
            targets={"WWT": 5.0},
            client=client,
        )

        assert len(plan.goals) > 0
        assert len(plan.projections) > 0

    def test_multiple_targets(self, mock_animals, sample_lpn_ids):
        """Verify plan with multiple targets."""
        client = MockNSIPClient(animals=mock_animals)

        plan = create_improvement_plan(
            sample_lpn_ids,
            targets={"WWT": 5.0, "PWWT": 8.0, "NLW": 0.20},
            client=client,
        )

        assert len(plan.goals) == 3
        assert len(plan.projections) == 3

    def test_selection_intensity(self, mock_animals, sample_lpn_ids):
        """Verify selection intensity is stored."""
        client = MockNSIPClient(animals=mock_animals)

        plan = create_improvement_plan(
            sample_lpn_ids,
            targets={"WWT": 5.0},
            selection_intensity=1.76,
            client=client,
        )

        assert plan.selection_intensity == 1.76

    def test_recommendations_generated(self, mock_animals, sample_lpn_ids):
        """Verify recommendations are generated."""
        client = MockNSIPClient(animals=mock_animals)

        plan = create_improvement_plan(
            sample_lpn_ids,
            targets={"WWT": 10.0},  # High target
            client=client,
        )

        assert len(plan.selection_recommendations) > 0


class TestGenerateRecommendations:
    """Tests for _generate_recommendations function."""

    def test_hardest_trait_identified(self):
        """Verify hardest trait is called out."""
        projections = [
            ImprovementProjection(
                trait="EASY",
                current=4.0,
                target=5.0,
                heritability=0.40,
                generations_needed=2,
                improvement_per_generation=0.5,
            ),
            ImprovementProjection(
                trait="HARD",
                current=0.0,
                target=10.0,
                heritability=0.10,
                generations_needed=20,
                improvement_per_generation=0.5,
            ),
        ]
        plan = ImprovementPlan(projections=projections)

        recs = _generate_recommendations(plan)

        assert any("HARD" in r for r in recs)

    def test_low_heritability_flagged(self):
        """Verify low heritability traits are noted."""
        projections = [
            ImprovementProjection(
                trait="LOW_H2",
                current=0.0,
                target=1.0,
                heritability=0.10,  # Low
                generations_needed=10,
                improvement_per_generation=0.1,
            ),
        ]
        plan = ImprovementPlan(projections=projections)

        recs = _generate_recommendations(plan)

        assert any("heritability" in r.lower() for r in recs)

    def test_quick_wins_identified(self):
        """Verify quick wins are called out."""
        projections = [
            ImprovementProjection(
                trait="QUICK",
                current=4.5,
                target=5.0,
                heritability=0.40,
                generations_needed=1,
                improvement_per_generation=0.5,
            ),
        ]
        plan = ImprovementPlan(projections=projections)

        recs = _generate_recommendations(plan)

        assert any("quick" in r.lower() or "1" in r or "2" in r for r in recs)


class TestIntensityToPercent:
    """Tests for _intensity_to_pct helper."""

    def test_top_5_percent(self):
        """Verify ~5% for intensity >= 2.0."""
        result = _intensity_to_pct(2.0)
        assert "5%" in result

    def test_top_10_percent(self):
        """Verify ~10% for intensity ~1.76."""
        result = _intensity_to_pct(1.76)
        assert "10%" in result

    def test_top_20_percent(self):
        """Verify ~20% for intensity ~1.4."""
        result = _intensity_to_pct(1.4)
        assert "20%" in result

    def test_top_30_percent(self):
        """Verify ~30% for intensity ~1.16."""
        result = _intensity_to_pct(1.16)
        assert "30%" in result


class TestFormatImprovementPlan:
    """Tests for format_improvement_plan function."""

    def test_basic_formatting(self):
        """Verify basic plan formatting."""
        goals = [
            TraitGoal(trait="WWT", current_mean=2.0, target_value=5.0),
        ]
        projections = [
            ImprovementProjection(
                trait="WWT",
                current=2.0,
                target=5.0,
                heritability=0.25,
                generations_needed=6,
                improvement_per_generation=0.5,
                projections=[2.0, 2.5, 3.0],
            ),
        ]
        plan = ImprovementPlan(
            goals=goals,
            projections=projections,
            selection_intensity=1.4,
        )

        output = format_improvement_plan(plan)

        assert "WWT" in output
        assert "2.0" in output or "2.00" in output
        assert "5.0" in output or "5.00" in output

    def test_with_recommendations(self):
        """Verify recommendations are included."""
        plan = ImprovementPlan(
            goals=[],
            projections=[],
            selection_recommendations=["Focus on WWT", "Consider outside genetics"],
        )

        output = format_improvement_plan(plan)

        assert "Focus on WWT" in output
        assert "Consider outside genetics" in output


class TestMainCLI:
    """Tests for main() CLI function."""

    def test_main_basic(self, mock_animals, sample_lpn_ids):
        """Verify main CLI with basic arguments."""
        with patch("nsip_skills.trait_planner.CachedNSIPClient") as mock_cls:
            mock_instance = MockNSIPClient(animals=mock_animals)
            mock_cls.return_value = mock_instance

            with patch(
                "sys.argv",
                ["trait_planner.py"] + sample_lpn_ids + ["--targets", '{"WWT": 5.0}'],
            ):
                from nsip_skills.trait_planner import main

                result = main()

                assert result == 0

    def test_main_with_intensity(self, mock_animals, sample_lpn_ids):
        """Verify main CLI with --intensity flag."""
        with patch("nsip_skills.trait_planner.CachedNSIPClient") as mock_cls:
            mock_instance = MockNSIPClient(animals=mock_animals)
            mock_cls.return_value = mock_instance

            with patch(
                "sys.argv",
                [
                    "trait_planner.py",
                ]
                + sample_lpn_ids
                + ["--targets", '{"WWT": 5.0}', "--intensity", "1.76"],
            ):
                from nsip_skills.trait_planner import main

                result = main()

                assert result == 0

    def test_main_json_output(self, mock_animals, sample_lpn_ids):
        """Verify main CLI with --json flag."""
        with patch("nsip_skills.trait_planner.CachedNSIPClient") as mock_cls:
            mock_instance = MockNSIPClient(animals=mock_animals)
            mock_cls.return_value = mock_instance

            with patch(
                "sys.argv",
                ["trait_planner.py"] + sample_lpn_ids + ["--targets", '{"WWT": 5.0}', "--json"],
            ):
                from nsip_skills.trait_planner import main

                result = main()

                assert result == 0

    def test_main_multiple_targets(self, mock_animals, sample_lpn_ids):
        """Verify main CLI with multiple targets."""
        with patch("nsip_skills.trait_planner.CachedNSIPClient") as mock_cls:
            mock_instance = MockNSIPClient(animals=mock_animals)
            mock_cls.return_value = mock_instance

            with patch(
                "sys.argv",
                ["trait_planner.py"]
                + sample_lpn_ids
                + ["--targets", '{"WWT": 5.0, "PWWT": 8.0, "NLW": 0.2}'],
            ):
                from nsip_skills.trait_planner import main

                result = main()

                assert result == 0

    def test_main_all_options(self, mock_animals, sample_lpn_ids):
        """Verify main CLI with all options combined."""
        with patch("nsip_skills.trait_planner.CachedNSIPClient") as mock_cls:
            mock_instance = MockNSIPClient(animals=mock_animals)
            mock_cls.return_value = mock_instance

            with patch(
                "sys.argv",
                ["trait_planner.py"]
                + sample_lpn_ids
                + [
                    "--targets",
                    '{"WWT": 5.0}',
                    "--intensity",
                    "2.0",
                    "--json",
                ],
            ):
                from nsip_skills.trait_planner import main

                result = main()

                assert result == 0


class TestIntensityToPercentEdgeCases:
    """Tests for _intensity_to_pct edge cases."""

    def test_very_low_intensity(self):
        """Verify low intensity returns ~50%."""
        result = _intensity_to_pct(0.5)
        assert "50%" in result

    def test_borderline_values(self):
        """Verify borderline intensity values."""
        # Test exactly at thresholds
        assert "5%" in _intensity_to_pct(2.0)
        assert "10%" in _intensity_to_pct(1.76)
        assert "20%" in _intensity_to_pct(1.4)
        assert "30%" in _intensity_to_pct(1.16)


class TestAnalyzeFlockTraitsEdgeCases:
    """Tests for analyze_flock_traits edge cases."""

    def test_empty_flock(self):
        """Verify handling of empty flock."""
        client = MockNSIPClient(animals={})

        result = analyze_flock_traits([], client=client)

        assert result == {}

    def test_animals_without_traits(self, mock_animals):
        """Verify handling when some animals lack traits."""
        # Create animals with minimal trait data
        from nsip_skills_helpers import MockAnimalDetails

        minimal_animals = {}
        for lpn in SAMPLE_LPNS[:2]:
            minimal_animals[lpn] = MockAnimalDetails.create_sample(lpn_id=lpn)
            # Clear traits
            minimal_animals[lpn].traits = {}

        client = MockNSIPClient(animals=minimal_animals)

        result = analyze_flock_traits(SAMPLE_LPNS[:2], client=client)

        # Should still return a dict (possibly empty)
        assert isinstance(result, dict)


class TestCreateImprovementPlanEdgeCases:
    """Tests for create_improvement_plan edge cases."""

    def test_already_at_target(self, mock_animals, sample_lpn_ids):
        """Verify handling when already at target."""
        client = MockNSIPClient(animals=mock_animals)

        # Set target below current mean (assuming WWT mean is around 2.5)
        plan = create_improvement_plan(
            sample_lpn_ids,
            targets={"WWT": 0.1},  # Very low target
            client=client,
        )

        # Should still create plan with 0 generations needed
        assert len(plan.projections) > 0

    def test_client_closed(self, mock_animals, sample_lpn_ids):
        """Verify client is closed when created internally."""
        with patch("nsip_skills.trait_planner.CachedNSIPClient") as mock_cls:
            mock_instance = MockNSIPClient(animals=mock_animals)
            mock_cls.return_value = mock_instance

            create_improvement_plan(
                sample_lpn_ids,
                targets={"WWT": 5.0},
                client=None,
            )

            assert mock_instance._closed is True
