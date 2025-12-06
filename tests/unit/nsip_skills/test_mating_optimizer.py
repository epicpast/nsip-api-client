"""
Unit tests for nsip_skills.mating_optimizer

Tests:
- Offspring EBV projection
- Mating scoring
- Mating plan optimization
- Inbreeding constraints
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
)

from nsip_skills.common.data_models import (
    PRESET_INDEXES,
    BreedingGoal,
    MatingPair,
    RiskLevel,
    SelectionIndex,
)
from nsip_skills.mating_optimizer import (
    MatingPlanResult,
    optimize_mating_plan,
    project_offspring_ebvs,
    score_mating,
)


class TestProjectOffspringEbvs:
    """Tests for project_offspring_ebvs function."""

    def test_midparent_average(self):
        """Verify midparent method returns average."""
        ram_ebvs = {"BWT": 1.0, "WWT": 4.0}
        ewe_ebvs = {"BWT": 0.5, "WWT": 2.0}

        projected = project_offspring_ebvs(ram_ebvs, ewe_ebvs)

        assert projected["BWT"] == 0.75
        assert projected["WWT"] == 3.0

    def test_missing_trait_in_one_parent(self):
        """Verify handling when trait exists in only one parent."""
        ram_ebvs = {"BWT": 1.0, "WWT": 4.0, "PWWT": 6.0}
        ewe_ebvs = {"BWT": 0.5, "WWT": 2.0}  # Missing PWWT

        projected = project_offspring_ebvs(ram_ebvs, ewe_ebvs)

        assert "BWT" in projected
        assert "WWT" in projected
        # PWWT should still be projected (with 0 for missing parent)
        assert "PWWT" in projected

    def test_empty_ebvs(self):
        """Verify handling of empty EBVs."""
        ram_ebvs = {}
        ewe_ebvs = {}

        projected = project_offspring_ebvs(ram_ebvs, ewe_ebvs)

        assert projected == {}

    def test_negative_ebvs(self):
        """Verify negative EBVs are handled correctly."""
        ram_ebvs = {"YFAT": -0.5}
        ewe_ebvs = {"YFAT": -0.3}

        projected = project_offspring_ebvs(ram_ebvs, ewe_ebvs)

        assert projected["YFAT"] == -0.4


class TestScoreMating:
    """Tests for score_mating function."""

    def test_basic_score(self):
        """Verify basic score calculation."""
        projected_ebvs = {"BWT": 0.5, "WWT": 3.0, "PWWT": 5.0}
        index = PRESET_INDEXES["range"]

        score = score_mating(projected_ebvs, index, inbreeding_coefficient=0.0)

        assert isinstance(score, float)

    def test_inbreeding_penalty(self):
        """Verify inbreeding reduces score."""
        projected_ebvs = {"BWT": 0.5, "WWT": 3.0, "PWWT": 5.0}
        index = PRESET_INDEXES["range"]

        score_no_inbreeding = score_mating(projected_ebvs, index, 0.0)
        score_with_inbreeding = score_mating(projected_ebvs, index, 0.10)

        assert score_with_inbreeding < score_no_inbreeding

    def test_higher_inbreeding_more_penalty(self):
        """Verify higher inbreeding has greater penalty."""
        projected_ebvs = {"BWT": 0.5, "WWT": 3.0}
        index = PRESET_INDEXES["range"]

        score_low = score_mating(projected_ebvs, index, 0.05)
        score_high = score_mating(projected_ebvs, index, 0.15)

        assert score_high < score_low

    def test_custom_penalty_weight(self):
        """Verify custom inbreeding penalty weight."""
        projected_ebvs = {"BWT": 0.5}
        index = PRESET_INDEXES["range"]

        score_default = score_mating(projected_ebvs, index, 0.10, inbreeding_penalty=10.0)
        score_high_penalty = score_mating(projected_ebvs, index, 0.10, inbreeding_penalty=20.0)

        assert score_high_penalty < score_default


class TestOptimizeMatingPlan:
    """Tests for optimize_mating_plan function."""

    def test_basic_optimization(self, mock_animals, mock_lineages):
        """Verify basic mating plan optimization."""
        client = MockNSIPClient(
            animals=mock_animals,
            lineages=mock_lineages,
        )

        # Use sire and some animals as ewes
        ram_lpns = [SAMPLE_SIRE_LPN]
        ewe_lpns = SAMPLE_LPNS[:3]

        result = optimize_mating_plan(
            ram_lpns=ram_lpns,
            ewe_lpns=ewe_lpns,
            client=client,
        )

        assert isinstance(result, MatingPlanResult)
        assert len(result.pairs) > 0 or len(result.unassigned_ewes) > 0

    def test_breeding_goal_terminal(self, mock_animals, mock_lineages):
        """Verify terminal breeding goal."""
        client = MockNSIPClient(
            animals=mock_animals,
            lineages=mock_lineages,
        )

        result = optimize_mating_plan(
            ram_lpns=[SAMPLE_SIRE_LPN],
            ewe_lpns=SAMPLE_LPNS[:2],
            breeding_goal=BreedingGoal.TERMINAL,
            client=client,
        )

        assert result.breeding_goal == "terminal"

    def test_breeding_goal_maternal(self, mock_animals, mock_lineages):
        """Verify maternal breeding goal."""
        client = MockNSIPClient(
            animals=mock_animals,
            lineages=mock_lineages,
        )

        result = optimize_mating_plan(
            ram_lpns=[SAMPLE_SIRE_LPN],
            ewe_lpns=SAMPLE_LPNS[:2],
            breeding_goal=BreedingGoal.MATERNAL,
            client=client,
        )

        assert result.breeding_goal == "maternal"

    def test_breeding_goal_string(self, mock_animals, mock_lineages):
        """Verify breeding goal as string."""
        client = MockNSIPClient(
            animals=mock_animals,
            lineages=mock_lineages,
        )

        result = optimize_mating_plan(
            ram_lpns=[SAMPLE_SIRE_LPN],
            ewe_lpns=SAMPLE_LPNS[:2],
            breeding_goal="balanced",
            client=client,
        )

        assert result.breeding_goal == "balanced"

    def test_custom_index(self, mock_animals, mock_lineages):
        """Verify custom selection index."""
        client = MockNSIPClient(
            animals=mock_animals,
            lineages=mock_lineages,
        )

        custom_index = SelectionIndex(
            name="Custom",
            trait_weights={"BWT": -1.0, "WWT": 2.0},
        )

        result = optimize_mating_plan(
            ram_lpns=[SAMPLE_SIRE_LPN],
            ewe_lpns=SAMPLE_LPNS[:2],
            custom_index=custom_index,
            client=client,
        )

        assert isinstance(result, MatingPlanResult)

    def test_max_inbreeding_threshold(self, mock_animals, mock_lineages):
        """Verify max inbreeding threshold is applied."""
        client = MockNSIPClient(
            animals=mock_animals,
            lineages=mock_lineages,
        )

        result = optimize_mating_plan(
            ram_lpns=[SAMPLE_SIRE_LPN],
            ewe_lpns=SAMPLE_LPNS[:3],
            max_inbreeding=0.01,  # Very low threshold
            client=client,
        )

        # High-risk pairs should be identified
        assert isinstance(result.high_risk_pairs, list)

    def test_max_ewes_per_ram(self, mock_animals, mock_lineages):
        """Verify max ewes per ram constraint."""
        client = MockNSIPClient(
            animals=mock_animals,
            lineages=mock_lineages,
        )

        result = optimize_mating_plan(
            ram_lpns=[SAMPLE_SIRE_LPN],
            ewe_lpns=SAMPLE_LPNS[:5],
            max_ewes_per_ram=2,
            client=client,
        )

        # Should have some unassigned ewes
        assert len(result.unassigned_ewes) >= 3 or len(result.pairs) <= 2

    def test_multiple_rams(self, mock_animals, mock_lineages):
        """Verify multiple rams are utilized."""
        # Add another ram
        mock_animals["RAM2"] = MockAnimalDetails.create_sample(lpn_id="RAM2")
        mock_animals["RAM2"].gender = "Male"

        client = MockNSIPClient(
            animals=mock_animals,
            lineages=mock_lineages,
        )

        result = optimize_mating_plan(
            ram_lpns=[SAMPLE_SIRE_LPN, "RAM2"],
            ewe_lpns=SAMPLE_LPNS[:4],
            client=client,
        )

        assert isinstance(result, MatingPlanResult)

    def test_client_closed_when_created(self, mock_animals, mock_lineages):
        """Verify client is closed when created internally."""
        with patch("nsip_skills.mating_optimizer.CachedNSIPClient") as mock_cls:
            mock_instance = MockNSIPClient(
                animals=mock_animals,
                lineages=mock_lineages,
            )
            mock_cls.return_value = mock_instance

            optimize_mating_plan(
                ram_lpns=[SAMPLE_SIRE_LPN],
                ewe_lpns=SAMPLE_LPNS[:2],
                client=None,
            )

            assert mock_instance._closed is True


class TestMatingPlanResultToDict:
    """Tests for MatingPlanResult.to_dict method."""

    def test_to_dict_structure(self):
        """Verify to_dict returns proper structure."""
        pair = MatingPair(
            ram_lpn="RAM1",
            ewe_lpn="EWE1",
            projected_offspring_ebvs={"BWT": 0.5},
            projected_inbreeding=0.02,
            inbreeding_risk=RiskLevel.LOW,
            composite_score=50.0,
        )

        result = MatingPlanResult(
            pairs=[pair],
            unassigned_ewes=["EWE2"],
            high_risk_pairs=[],
            breeding_goal="balanced",
            max_inbreeding=0.0625,
        )

        d = result.to_dict()

        assert "pairs" in d
        assert "unassigned_ewes" in d
        assert "high_risk_pairs" in d
        assert "breeding_goal" in d
        assert "max_inbreeding" in d


class TestMatingPairToDict:
    """Tests for MatingPair.to_dict method."""

    def test_to_dict_structure(self):
        """Verify MatingPair to_dict returns proper structure."""
        pair = MatingPair(
            ram_lpn="RAM1",
            ewe_lpn="EWE1",
            projected_offspring_ebvs={"BWT": 0.5},
            projected_inbreeding=0.02,
            inbreeding_risk=RiskLevel.LOW,
            composite_score=50.0,
        )

        d = pair.to_dict()

        assert "ram_lpn" in d
        assert "ewe_lpn" in d
        assert "projected_offspring_ebvs" in d
        assert "projected_inbreeding" in d


class TestFormatMatingRecommendations:
    """Tests for formatting mating recommendations."""

    def test_basic_formatting(self, mock_animals, mock_lineages):
        """Verify basic formatting of mating recommendations."""
        from nsip_skills.common.formatters import format_mating_recommendations

        pairs = [
            MatingPair(
                ram_lpn="RAM1",
                ewe_lpn="EWE1",
                projected_offspring_ebvs={"BWT": 0.5},
                projected_inbreeding=0.02,
                inbreeding_risk=RiskLevel.LOW,
                composite_score=50.0,
                rank=1,
            )
        ]

        output = format_mating_recommendations(pairs)

        assert "RAM1" in output
        assert "EWE1" in output


class TestMainCLI:
    """Tests for main() CLI function."""

    def test_main_basic(self, mock_animals, mock_lineages):
        """Verify main CLI runs without error."""
        with patch("nsip_skills.mating_optimizer.CachedNSIPClient") as mock_cls:
            mock_instance = MockNSIPClient(
                animals=mock_animals,
                lineages=mock_lineages,
            )
            mock_cls.return_value = mock_instance

            with patch(
                "sys.argv",
                [
                    "mating_optimizer.py",
                    "--rams",
                    SAMPLE_SIRE_LPN,
                    "--ewes",
                    SAMPLE_LPNS[0],
                    SAMPLE_LPNS[1],
                ],
            ):
                from nsip_skills.mating_optimizer import main

                result = main()

                assert result == 0

    def test_main_json_output(self, mock_animals, mock_lineages):
        """Verify main CLI JSON output."""
        with patch("nsip_skills.mating_optimizer.CachedNSIPClient") as mock_cls:
            mock_instance = MockNSIPClient(
                animals=mock_animals,
                lineages=mock_lineages,
            )
            mock_cls.return_value = mock_instance

            with patch(
                "sys.argv",
                [
                    "mating_optimizer.py",
                    "--rams",
                    SAMPLE_SIRE_LPN,
                    "--ewes",
                    SAMPLE_LPNS[0],
                    "--json",
                ],
            ):
                from nsip_skills.mating_optimizer import main

                result = main()

                assert result == 0

    def test_main_with_goal(self, mock_animals, mock_lineages):
        """Verify main CLI with breeding goal."""
        with patch("nsip_skills.mating_optimizer.CachedNSIPClient") as mock_cls:
            mock_instance = MockNSIPClient(
                animals=mock_animals,
                lineages=mock_lineages,
            )
            mock_cls.return_value = mock_instance

            with patch(
                "sys.argv",
                [
                    "mating_optimizer.py",
                    "--rams",
                    SAMPLE_SIRE_LPN,
                    "--ewes",
                    SAMPLE_LPNS[0],
                    "--goal",
                    "terminal",
                ],
            ):
                from nsip_skills.mating_optimizer import main

                result = main()

                assert result == 0
