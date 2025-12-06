"""
Unit tests for nsip_skills.ancestry_builder

Tests:
- Bloodline breakdown calculation
- Genetic diversity scoring
- Notable ancestor identification
- Ancestry report generation
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

from nsip_skills.ancestry_builder import (
    AncestryReport,
    calculate_bloodline_breakdown,
    calculate_genetic_diversity,
    format_ancestry_report,
    generate_ancestry_report,
    identify_notable_ancestors,
)
from nsip_skills.common.data_models import PedigreeNode, PedigreeTree


class TestCalculateBloodlineBreakdown:
    """Tests for calculate_bloodline_breakdown function."""

    def test_all_grandparents_known(self):
        """Verify 25% allocation to each known grandparent."""
        subject = PedigreeNode(lpn_id="CHILD", generation=0)
        sire = PedigreeNode(lpn_id="SIRE", generation=1)
        dam = PedigreeNode(lpn_id="DAM", generation=1)
        sire_sire = PedigreeNode(lpn_id="SS", generation=2)
        sire_dam = PedigreeNode(lpn_id="SD", generation=2)
        dam_sire = PedigreeNode(lpn_id="DS", generation=2)
        dam_dam = PedigreeNode(lpn_id="DD", generation=2)

        tree = PedigreeTree(
            subject=subject,
            sire=sire,
            dam=dam,
            sire_sire=sire_sire,
            sire_dam=sire_dam,
            dam_sire=dam_sire,
            dam_dam=dam_dam,
        )

        breakdown = calculate_bloodline_breakdown(tree)

        # All four grandparents should have 25%
        assert len(breakdown) == 4
        for key, value in breakdown.items():
            assert value == 25.0
            assert "Unknown" not in key

    def test_some_grandparents_unknown(self):
        """Verify unknown grandparents are labeled appropriately."""
        subject = PedigreeNode(lpn_id="CHILD", generation=0)
        sire = PedigreeNode(lpn_id="SIRE", generation=1)
        dam = PedigreeNode(lpn_id="DAM", generation=1)
        sire_sire = PedigreeNode(lpn_id="SS", generation=2)
        # Missing: sire_dam, dam_sire, dam_dam

        tree = PedigreeTree(
            subject=subject,
            sire=sire,
            dam=dam,
            sire_sire=sire_sire,
        )

        breakdown = calculate_bloodline_breakdown(tree)

        # Should still have 4 entries
        assert len(breakdown) == 4
        # 3 should be unknown
        unknown_count = sum(1 for k in breakdown if "Unknown" in k)
        assert unknown_count == 3

    def test_no_grandparents(self):
        """Verify all unknown when no grandparent data."""
        subject = PedigreeNode(lpn_id="CHILD", generation=0)

        tree = PedigreeTree(subject=subject)

        breakdown = calculate_bloodline_breakdown(tree)

        # All should be unknown
        assert len(breakdown) == 4
        for key, value in breakdown.items():
            assert "Unknown" in key
            assert value == 25.0


class TestCalculateGeneticDiversity:
    """Tests for calculate_genetic_diversity function."""

    def test_all_unique_ancestors(self):
        """Verify diversity of 1.0 when all ancestors are unique."""
        subject = PedigreeNode(lpn_id="CHILD", generation=0)
        sire = PedigreeNode(lpn_id="SIRE", generation=1)
        dam = PedigreeNode(lpn_id="DAM", generation=1)
        sire_sire = PedigreeNode(lpn_id="SS", generation=2)
        sire_dam = PedigreeNode(lpn_id="SD", generation=2)
        dam_sire = PedigreeNode(lpn_id="DS", generation=2)
        dam_dam = PedigreeNode(lpn_id="DD", generation=2)

        tree = PedigreeTree(
            subject=subject,
            sire=sire,
            dam=dam,
            sire_sire=sire_sire,
            sire_dam=sire_dam,
            dam_sire=dam_sire,
            dam_dam=dam_dam,
        )

        diversity = calculate_genetic_diversity(tree)

        # All unique = 1.0 diversity
        assert diversity == 1.0

    def test_repeated_ancestors_reduce_diversity(self):
        """Verify diversity < 1.0 when ancestors are repeated."""
        subject = PedigreeNode(lpn_id="CHILD", generation=0)
        sire = PedigreeNode(lpn_id="SIRE", generation=1)
        dam = PedigreeNode(lpn_id="DAM", generation=1)
        # Same ancestor appears twice
        common = PedigreeNode(lpn_id="COMMON", generation=2)

        tree = PedigreeTree(
            subject=subject,
            sire=sire,
            dam=dam,
            sire_sire=common,
            dam_sire=common,  # Repeated
        )

        diversity = calculate_genetic_diversity(tree)

        # Should be less than 1.0 due to repeated ancestor
        assert diversity < 1.0

    def test_no_ancestors(self):
        """Verify diversity of 1.0 when no ancestor data."""
        subject = PedigreeNode(lpn_id="CHILD", generation=0)
        tree = PedigreeTree(subject=subject)

        diversity = calculate_genetic_diversity(tree)

        # No ancestors to compare = default 1.0
        assert diversity == 1.0


class TestIdentifyNotableAncestors:
    """Tests for identify_notable_ancestors function."""

    def test_high_progeny_count_notable(self):
        """Verify ancestors with high progeny count are notable."""
        subject = PedigreeNode(lpn_id="CHILD", generation=0)
        notable_sire = PedigreeNode(lpn_id="NOTABLE_SIRE", generation=1, farm_name="Test Farm")

        tree = PedigreeTree(subject=subject, sire=notable_sire)

        # Mock animal with high progeny
        animals = {
            "NOTABLE_SIRE": MockAnimalDetails.create_sample(
                lpn_id="NOTABLE_SIRE",
            ),
        }
        animals["NOTABLE_SIRE"].total_progeny = 100  # High progeny

        client = MockNSIPClient(animals=animals)

        notable = identify_notable_ancestors(tree, client)

        assert len(notable) > 0
        assert any(n["lpn_id"] == "NOTABLE_SIRE" for n in notable)
        assert any("progeny" in str(n.get("reasons", [])) for n in notable)

    def test_high_us_index_notable(self):
        """Verify ancestors with high US index are notable."""
        notable_ancestor = PedigreeNode(
            lpn_id="INDEX_STAR",
            generation=1,
            us_index=150.0,  # High index
            farm_name="Index Farm",
        )
        subject = PedigreeNode(lpn_id="CHILD", generation=0)

        tree = PedigreeTree(subject=subject, sire=notable_ancestor)

        animals = {
            "INDEX_STAR": MockAnimalDetails.create_sample(lpn_id="INDEX_STAR"),
        }
        client = MockNSIPClient(animals=animals)

        notable = identify_notable_ancestors(tree, client)

        assert len(notable) > 0
        assert any(n["lpn_id"] == "INDEX_STAR" for n in notable)

    def test_no_notable_ancestors(self):
        """Verify empty list when no notable ancestors."""
        subject = PedigreeNode(lpn_id="CHILD", generation=0)
        regular_sire = PedigreeNode(lpn_id="REGULAR", generation=1)

        tree = PedigreeTree(subject=subject, sire=regular_sire)

        # Regular animal with low progeny count
        animals = {
            "REGULAR": MockAnimalDetails.create_sample(lpn_id="REGULAR"),
        }
        animals["REGULAR"].total_progeny = 5

        client = MockNSIPClient(animals=animals)

        notable = identify_notable_ancestors(tree, client)

        assert len(notable) == 0

    def test_handles_missing_ancestor_data(self):
        """Verify graceful handling when ancestor details not found."""
        subject = PedigreeNode(lpn_id="CHILD", generation=0)
        unknown = PedigreeNode(lpn_id="UNKNOWN", generation=1)

        tree = PedigreeTree(subject=subject, sire=unknown)

        # Empty animals dict - ancestor not found
        client = MockNSIPClient(animals={})

        # Should not raise, just return empty
        notable = identify_notable_ancestors(tree, client)

        assert isinstance(notable, list)


class TestGenerateAncestryReport:
    """Tests for generate_ancestry_report function."""

    def test_basic_report_generation(self, mock_lineages, mock_animals):
        """Verify basic report is generated."""
        client = MockNSIPClient(
            animals=mock_animals,
            lineages=mock_lineages,
        )

        report = generate_ancestry_report(
            SAMPLE_LPNS[0],
            generations=2,
            include_notable=False,
            client=client,
        )

        assert isinstance(report, AncestryReport)
        assert report.subject_lpn == SAMPLE_LPNS[0]
        assert report.pedigree is not None
        assert isinstance(report.bloodline_breakdown, dict)
        assert 0 <= report.genetic_diversity <= 1

    def test_includes_notable_ancestors_when_requested(self, mock_lineages, mock_animals):
        """Verify notable ancestors are included when requested."""
        # Add an animal with high progeny count
        mock_animals[SAMPLE_SIRE_LPN].total_progeny = 100

        client = MockNSIPClient(
            animals=mock_animals,
            lineages=mock_lineages,
        )

        report = generate_ancestry_report(
            SAMPLE_LPNS[0],
            generations=2,
            include_notable=True,
            client=client,
        )

        # Should have analyzed notable ancestors
        assert isinstance(report.notable_ancestors, list)

    def test_default_generations(self, mock_lineages, mock_animals):
        """Verify default 4 generations are used."""
        client = MockNSIPClient(
            animals=mock_animals,
            lineages=mock_lineages,
        )

        report = generate_ancestry_report(
            SAMPLE_LPNS[0],
            client=client,
        )

        assert report is not None
        assert report.pedigree is not None

    def test_client_closed_when_created_internally(self, mock_lineages, mock_animals):
        """Verify client is closed when created internally."""
        with patch("nsip_skills.ancestry_builder.CachedNSIPClient") as mock_cls:
            mock_instance = MockNSIPClient(
                animals=mock_animals,
                lineages=mock_lineages,
            )
            mock_cls.return_value = mock_instance

            generate_ancestry_report(SAMPLE_LPNS[0], generations=2, client=None)

            assert mock_instance._closed is True

    def test_client_not_closed_when_passed(self, mock_lineages, mock_animals):
        """Verify client is not closed when passed in."""
        client = MockNSIPClient(
            animals=mock_animals,
            lineages=mock_lineages,
        )

        generate_ancestry_report(SAMPLE_LPNS[0], generations=2, client=client)

        assert client._closed is False


class TestAncestryReportToDict:
    """Tests for AncestryReport.to_dict method."""

    def test_to_dict(self, mock_lineages, mock_animals):
        """Verify to_dict returns all fields."""
        client = MockNSIPClient(
            animals=mock_animals,
            lineages=mock_lineages,
        )

        report = generate_ancestry_report(
            SAMPLE_LPNS[0],
            generations=2,
            client=client,
        )

        d = report.to_dict()

        assert "subject_lpn" in d
        assert "pedigree" in d
        assert "bloodline_breakdown" in d
        assert "notable_ancestors" in d
        assert "genetic_diversity" in d


class TestFormatAncestryReport:
    """Tests for format_ancestry_report function."""

    def test_basic_formatting(self, mock_lineages, mock_animals):
        """Verify basic report formatting."""
        client = MockNSIPClient(
            animals=mock_animals,
            lineages=mock_lineages,
        )

        report = generate_ancestry_report(
            SAMPLE_LPNS[0],
            generations=2,
            include_notable=False,
            client=client,
        )

        output = format_ancestry_report(report)

        assert SAMPLE_LPNS[0] in output
        assert "Ancestry Report" in output
        assert "Pedigree" in output
        assert "Bloodline Breakdown" in output
        assert "Genetic Diversity Score" in output

    def test_ascii_style(self, mock_lineages, mock_animals):
        """Verify ASCII style formatting."""
        client = MockNSIPClient(
            animals=mock_animals,
            lineages=mock_lineages,
        )

        report = generate_ancestry_report(
            SAMPLE_LPNS[0],
            generations=2,
            client=client,
        )

        output = format_ancestry_report(report, style="ascii")

        assert output is not None
        assert len(output) > 0

    def test_markdown_style(self, mock_lineages, mock_animals):
        """Verify markdown style formatting."""
        client = MockNSIPClient(
            animals=mock_animals,
            lineages=mock_lineages,
        )

        report = generate_ancestry_report(
            SAMPLE_LPNS[0],
            generations=2,
            client=client,
        )

        output = format_ancestry_report(report, style="markdown")

        assert output is not None
        assert len(output) > 0

    def test_low_diversity_warning(self):
        """Verify warning shown for low genetic diversity."""
        # Create report with low diversity
        subject = PedigreeNode(lpn_id="CHILD", generation=0)
        common = PedigreeNode(lpn_id="COMMON", generation=1)
        tree = PedigreeTree(
            subject=subject,
            sire=common,
            dam=common,  # Same parent - very low diversity
        )

        report = AncestryReport(
            subject_lpn="CHILD",
            pedigree=tree,
            genetic_diversity=0.5,  # Low
        )

        output = format_ancestry_report(report)

        assert "Lower score" in output or "inbreeding" in output.lower()

    def test_notable_ancestors_displayed(self):
        """Verify notable ancestors are shown when present."""
        subject = PedigreeNode(lpn_id="CHILD", generation=0)
        tree = PedigreeTree(subject=subject)

        report = AncestryReport(
            subject_lpn="CHILD",
            pedigree=tree,
            notable_ancestors=[
                {
                    "lpn_id": "NOTABLE1",
                    "generation": 2,
                    "reasons": ["100 progeny"],
                    "farm": "Famous Farm",
                }
            ],
        )

        output = format_ancestry_report(report)

        assert "NOTABLE1" in output
        assert "Notable Ancestors" in output

    def test_common_ancestors_displayed(self):
        """Verify common ancestors are shown when present."""
        subject = PedigreeNode(lpn_id="CHILD", generation=0)
        tree = PedigreeTree(
            subject=subject,
            common_ancestors=["COMMON1", "COMMON2"],
        )

        report = AncestryReport(
            subject_lpn="CHILD",
            pedigree=tree,
        )

        output = format_ancestry_report(report)

        assert "Common Ancestors" in output
        assert "COMMON1" in output
        assert "COMMON2" in output


class TestMainCLI:
    """Tests for main() CLI function."""

    def test_main_basic(self, mock_lineages, mock_animals):
        """Verify main CLI runs without error."""
        with patch("nsip_skills.ancestry_builder.CachedNSIPClient") as mock_cls:
            mock_instance = MockNSIPClient(
                animals=mock_animals,
                lineages=mock_lineages,
            )
            mock_cls.return_value = mock_instance

            with patch("sys.argv", ["ancestry_builder.py", SAMPLE_LPNS[0], "-g", "2"]):
                from nsip_skills.ancestry_builder import main

                result = main()

                assert result == 0

    def test_main_json_output(self, mock_lineages, mock_animals):
        """Verify main CLI JSON output."""
        with patch("nsip_skills.ancestry_builder.CachedNSIPClient") as mock_cls:
            mock_instance = MockNSIPClient(
                animals=mock_animals,
                lineages=mock_lineages,
            )
            mock_cls.return_value = mock_instance

            with patch("sys.argv", ["ancestry_builder.py", SAMPLE_LPNS[0], "--json"]):
                from nsip_skills.ancestry_builder import main

                result = main()

                assert result == 0
