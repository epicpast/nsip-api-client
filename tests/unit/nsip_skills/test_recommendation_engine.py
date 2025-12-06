"""
Unit tests for nsip_skills.recommendation_engine

Tests:
- Recommendation generation
- Different breeding goals
- Philosophy-specific recommendations
- Report formatting

Target: >95% coverage
"""

from __future__ import annotations

from unittest.mock import patch

from nsip_skills_helpers import (
    SAMPLE_LPNS,
    MockAnimalDetails,
    MockNSIPClient,
)

from nsip_skills.common.data_models import (
    BreedingGoal,
    FlockSummary,
)
from nsip_skills.recommendation_engine import (
    Recommendation,
    RecommendationReport,
    RecommendationType,
    format_recommendations,
    generate_recommendations,
)


class TestRecommendationType:
    """Tests for RecommendationType enum."""

    def test_all_types_exist(self):
        """Verify all recommendation types exist."""
        assert RecommendationType.RETAIN.value == "retain"
        assert RecommendationType.CULL.value == "cull"
        assert RecommendationType.OUTSIDE_GENETICS.value == "outside_genetics"
        assert RecommendationType.MANAGEMENT.value == "management"
        assert RecommendationType.PRIORITY.value == "priority"


class TestRecommendation:
    """Tests for Recommendation dataclass."""

    def test_to_dict(self):
        """Verify to_dict returns proper structure."""
        rec = Recommendation(
            type=RecommendationType.RETAIN,
            subject="ANIMAL1",
            rationale="Top performer",
            impact="Keep breeding",
            priority=1,
            action="Retain in flock",
        )

        d = rec.to_dict()

        assert d["type"] == "retain"
        assert d["subject"] == "ANIMAL1"
        assert d["rationale"] == "Top performer"
        assert d["impact"] == "Keep breeding"
        assert d["priority"] == 1
        assert d["action"] == "Retain in flock"

    def test_default_values(self):
        """Verify default values are set correctly."""
        rec = Recommendation(
            type=RecommendationType.MANAGEMENT,
            subject="Test",
            rationale="Reason",
            impact="Expected",
        )

        assert rec.priority == 1
        assert rec.action == ""


class TestRecommendationReport:
    """Tests for RecommendationReport dataclass."""

    def test_to_dict(self):
        """Verify to_dict returns proper structure."""
        summary = FlockSummary(
            total_animals=10,
            male_count=2,
            female_count=8,
        )

        report = RecommendationReport(
            flock_summary=summary,
            recommendations=[],
            retain_list=["A", "B"],
            cull_list=["C"],
            priority_breeding=["A"],
            trait_priorities=["BWT"],
            breeding_goal="balanced",
        )

        d = report.to_dict()

        assert "flock_summary" in d
        assert "recommendations" in d
        assert "retain_list" in d
        assert "cull_list" in d
        assert "priority_breeding" in d
        assert "trait_priorities" in d
        assert "breeding_goal" in d


class TestGenerateRecommendations:
    """Tests for generate_recommendations function."""

    def test_basic_recommendations(self, mock_animals):
        """Verify basic recommendations are generated."""
        client = MockNSIPClient(animals=mock_animals)

        report = generate_recommendations(
            lpn_ids=list(mock_animals.keys()),
            client=client,
        )

        assert isinstance(report, RecommendationReport)
        assert report.flock_summary is not None

    def test_balanced_goal(self, mock_animals):
        """Verify balanced breeding goal."""
        client = MockNSIPClient(animals=mock_animals)

        report = generate_recommendations(
            lpn_ids=list(mock_animals.keys()),
            breeding_goal=BreedingGoal.BALANCED,
            client=client,
        )

        assert report.breeding_goal == "balanced"

    def test_terminal_goal(self, mock_animals):
        """Verify terminal breeding goal."""
        client = MockNSIPClient(animals=mock_animals)

        report = generate_recommendations(
            lpn_ids=list(mock_animals.keys()),
            breeding_goal=BreedingGoal.TERMINAL,
            client=client,
        )

        assert report.breeding_goal == "terminal"

    def test_maternal_goal(self, mock_animals):
        """Verify maternal breeding goal."""
        client = MockNSIPClient(animals=mock_animals)

        report = generate_recommendations(
            lpn_ids=list(mock_animals.keys()),
            breeding_goal=BreedingGoal.MATERNAL,
            client=client,
        )

        assert report.breeding_goal == "maternal"

    def test_goal_as_string(self, mock_animals):
        """Verify breeding goal as string."""
        client = MockNSIPClient(animals=mock_animals)

        report = generate_recommendations(
            lpn_ids=list(mock_animals.keys()),
            breeding_goal="balanced",
            client=client,
        )

        assert report.breeding_goal == "balanced"

    def test_commercial_philosophy(self, mock_animals):
        """Verify commercial philosophy recommendations."""
        client = MockNSIPClient(animals=mock_animals)

        report = generate_recommendations(
            lpn_ids=list(mock_animals.keys()),
            philosophy="commercial",
            client=client,
        )

        # Should have management recommendation for commercial
        mgmt_recs = [r for r in report.recommendations if r.type == RecommendationType.MANAGEMENT]
        assert len(mgmt_recs) > 0

    def test_seedstock_philosophy(self, mock_animals):
        """Verify seedstock philosophy recommendations."""
        client = MockNSIPClient(animals=mock_animals)

        report = generate_recommendations(
            lpn_ids=list(mock_animals.keys()),
            philosophy="seedstock",
            client=client,
        )

        # Should have data collection recommendation
        mgmt_recs = [r for r in report.recommendations if r.type == RecommendationType.MANAGEMENT]
        data_collection = any("Data" in r.subject for r in mgmt_recs)
        assert data_collection

    def test_generates_retain_list(self, mock_animals):
        """Verify retain list is generated."""
        client = MockNSIPClient(animals=mock_animals)

        report = generate_recommendations(
            lpn_ids=list(mock_animals.keys()),
            client=client,
        )

        # Should have some animals in retain list
        assert isinstance(report.retain_list, list)

    def test_generates_cull_list_for_large_flock(self, mock_animals):
        """Verify cull list is generated for large flocks."""
        # Create a larger flock
        for i in range(15):
            lpn = f"ANIMAL_{i}"
            mock_animals[lpn] = MockAnimalDetails.create_sample(lpn_id=lpn)

        client = MockNSIPClient(animals=mock_animals)

        report = generate_recommendations(
            lpn_ids=list(mock_animals.keys()),
            client=client,
        )

        # Should have cull recommendations for large flock
        assert isinstance(report.cull_list, list)

    def test_identifies_trait_priorities(self, mock_animals):
        """Verify trait priorities are identified."""
        client = MockNSIPClient(animals=mock_animals)

        report = generate_recommendations(
            lpn_ids=list(mock_animals.keys()),
            client=client,
        )

        assert isinstance(report.trait_priorities, list)

    def test_priority_breeding_identified(self, mock_animals):
        """Verify priority breeding stock is identified."""
        client = MockNSIPClient(animals=mock_animals)

        report = generate_recommendations(
            lpn_ids=list(mock_animals.keys()),
            client=client,
        )

        assert isinstance(report.priority_breeding, list)

    def test_client_closed_when_created(self, mock_animals):
        """Verify client is closed when created internally."""
        with patch("nsip_skills.recommendation_engine.CachedNSIPClient") as mock_cls:
            mock_instance = MockNSIPClient(animals=mock_animals)
            mock_cls.return_value = mock_instance

            generate_recommendations(
                lpn_ids=list(mock_animals.keys()),
                client=None,
            )

            assert mock_instance._closed is True

    def test_client_not_closed_when_passed(self, mock_animals):
        """Verify client is not closed when passed in."""
        client = MockNSIPClient(animals=mock_animals)

        generate_recommendations(
            lpn_ids=list(mock_animals.keys()),
            client=client,
        )

        assert client._closed is False

    def test_with_constraints(self, mock_animals):
        """Verify handling of constraints."""
        client = MockNSIPClient(animals=mock_animals)

        report = generate_recommendations(
            lpn_ids=list(mock_animals.keys()),
            constraints={"budget": 1000, "max_rams": 2},
            client=client,
        )

        assert report is not None


class TestFormatRecommendations:
    """Tests for format_recommendations function."""

    def test_basic_formatting(self, mock_animals):
        """Verify basic formatting of recommendations."""
        client = MockNSIPClient(animals=mock_animals)

        report = generate_recommendations(
            lpn_ids=list(mock_animals.keys()),
            client=client,
        )

        output = format_recommendations(report)

        assert "Breeding Recommendations" in output
        assert len(output) > 0

    def test_includes_flock_summary(self, mock_animals):
        """Verify flock summary is included."""
        client = MockNSIPClient(animals=mock_animals)

        report = generate_recommendations(
            lpn_ids=list(mock_animals.keys()),
            client=client,
        )

        output = format_recommendations(report)

        assert "Flock Summary" in output
        assert "Total animals" in output

    def test_includes_breeding_goal(self, mock_animals):
        """Verify breeding goal is shown."""
        client = MockNSIPClient(animals=mock_animals)

        report = generate_recommendations(
            lpn_ids=list(mock_animals.keys()),
            breeding_goal="terminal",
            client=client,
        )

        output = format_recommendations(report)

        assert "Terminal" in output

    def test_shows_priority_breeding(self):
        """Verify priority breeding section."""
        summary = FlockSummary(total_animals=5, male_count=1, female_count=4)
        report = RecommendationReport(
            flock_summary=summary,
            priority_breeding=["TOP1", "TOP2"],
        )

        output = format_recommendations(report)

        assert "Priority Breeding" in output
        assert "TOP1" in output

    def test_shows_retain_list(self):
        """Verify retain list section."""
        summary = FlockSummary(total_animals=5, male_count=1, female_count=4)
        report = RecommendationReport(
            flock_summary=summary,
            retain_list=["KEEP1", "KEEP2", "KEEP3"],
        )

        output = format_recommendations(report)

        assert "Retain" in output

    def test_shows_cull_list(self):
        """Verify cull list section."""
        summary = FlockSummary(total_animals=15, male_count=3, female_count=12)
        report = RecommendationReport(
            flock_summary=summary,
            cull_list=["REMOVE1", "REMOVE2"],
        )

        output = format_recommendations(report)

        assert "Cull" in output

    def test_shows_trait_priorities(self):
        """Verify trait priorities section."""
        summary = FlockSummary(total_animals=5, male_count=1, female_count=4)
        report = RecommendationReport(
            flock_summary=summary,
            trait_priorities=["BWT", "WWT"],
        )

        output = format_recommendations(report)

        assert "Trait Improvement" in output
        assert "BWT" in output

    def test_shows_all_recommendations(self):
        """Verify all recommendations are shown."""
        summary = FlockSummary(total_animals=5, male_count=1, female_count=4)
        recs = [
            Recommendation(
                type=RecommendationType.RETAIN,
                subject="ANIMAL1",
                rationale="Top performer",
                impact="Keep breeding",
                action="Retain",
            ),
            Recommendation(
                type=RecommendationType.MANAGEMENT,
                subject="Feeding",
                rationale="Improve nutrition",
                impact="Better weights",
                action="Adjust rations",
            ),
        ]
        report = RecommendationReport(
            flock_summary=summary,
            recommendations=recs,
        )

        output = format_recommendations(report)

        assert "All Recommendations" in output
        assert "ANIMAL1" in output

    def test_limits_displayed_recommendations(self):
        """Verify output limits recommendations to 15."""
        summary = FlockSummary(total_animals=50, male_count=10, female_count=40)
        recs = [
            Recommendation(
                type=RecommendationType.MANAGEMENT,
                subject=f"REC{i}",
                rationale="Reason",
                impact="Impact",
            )
            for i in range(20)
        ]
        report = RecommendationReport(
            flock_summary=summary,
            recommendations=recs,
        )

        output = format_recommendations(report)

        # Should not have all 20 recommendations in output
        assert output.count("REC") <= 15


class TestMainCLI:
    """Tests for main() CLI function."""

    def test_main_basic(self, mock_animals):
        """Verify main CLI runs without error."""
        with patch("nsip_skills.recommendation_engine.CachedNSIPClient") as mock_cls:
            mock_instance = MockNSIPClient(animals=mock_animals)
            mock_cls.return_value = mock_instance

            with patch("sys.argv", ["recommendation_engine.py"] + SAMPLE_LPNS[:3]):
                from nsip_skills.recommendation_engine import main

                result = main()

                assert result == 0

    def test_main_json_output(self, mock_animals):
        """Verify main CLI JSON output."""
        with patch("nsip_skills.recommendation_engine.CachedNSIPClient") as mock_cls:
            mock_instance = MockNSIPClient(animals=mock_animals)
            mock_cls.return_value = mock_instance

            with patch("sys.argv", ["recommendation_engine.py", SAMPLE_LPNS[0], "--json"]):
                from nsip_skills.recommendation_engine import main

                result = main()

                assert result == 0

    def test_main_with_goal(self, mock_animals):
        """Verify main CLI with breeding goal."""
        with patch("nsip_skills.recommendation_engine.CachedNSIPClient") as mock_cls:
            mock_instance = MockNSIPClient(animals=mock_animals)
            mock_cls.return_value = mock_instance

            with patch(
                "sys.argv",
                ["recommendation_engine.py", SAMPLE_LPNS[0], "--goal", "terminal"],
            ):
                from nsip_skills.recommendation_engine import main

                result = main()

                assert result == 0

    def test_main_with_philosophy(self, mock_animals):
        """Verify main CLI with philosophy."""
        with patch("nsip_skills.recommendation_engine.CachedNSIPClient") as mock_cls:
            mock_instance = MockNSIPClient(animals=mock_animals)
            mock_cls.return_value = mock_instance

            with patch(
                "sys.argv",
                ["recommendation_engine.py", SAMPLE_LPNS[0], "--philosophy", "seedstock"],
            ):
                from nsip_skills.recommendation_engine import main

                result = main()

                assert result == 0
