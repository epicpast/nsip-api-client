"""
Unit tests for nsip_skills.inbreeding

Tests:
- Pedigree tree building
- Wright's coefficient calculation
- Path tracing algorithm
- Common ancestor detection
- Projected offspring inbreeding

Target: >80% coverage
"""

from unittest.mock import patch

from nsip_skills_helpers import SAMPLE_LPNS, MockLineage, MockNSIPClient

from nsip_skills.common.data_models import (
    InbreedingResult,
    PedigreeNode,
    PedigreeTree,
    RiskLevel,
)
from nsip_skills.inbreeding import (
    build_pedigree_tree,
    calculate_inbreeding,
    calculate_path_contribution,
    calculate_projected_offspring_inbreeding,
    find_common_ancestors,
    format_inbreeding_report,
    trace_paths_to_ancestor,
)


class TestBuildPedigreeTree:
    """Tests for build_pedigree_tree function."""

    def test_single_generation(self, mock_lineages):
        """Verify tree with just subject."""
        client = MockNSIPClient(lineages=mock_lineages)
        lpn_id = SAMPLE_LPNS[0]

        tree = build_pedigree_tree(lpn_id, generations=1, client=client)

        assert tree.subject.lpn_id == lpn_id
        assert tree.subject.generation == 0

    def test_two_generations(self, mock_lineages):
        """Verify tree with parents."""
        client = MockNSIPClient(lineages=mock_lineages)
        lpn_id = SAMPLE_LPNS[0]

        tree = build_pedigree_tree(lpn_id, generations=2, client=client)

        assert tree.subject.lpn_id == lpn_id
        if tree.sire:
            assert tree.sire.generation == 1
        if tree.dam:
            assert tree.dam.generation == 1

    def test_three_generations(self, mock_lineages):
        """Verify tree with grandparents."""
        client = MockNSIPClient(lineages=mock_lineages)
        lpn_id = SAMPLE_LPNS[0]

        tree = build_pedigree_tree(lpn_id, generations=3, client=client)

        # Check grandparents exist
        if tree.sire_sire:
            assert tree.sire_sire.generation == 2
        if tree.dam_dam:
            assert tree.dam_dam.generation == 2

    def test_unknown_parents_handled(self):
        """Verify unknown parents don't cause errors."""
        # Animal with no lineage data
        lineages = {"ORPHAN": MockLineage(lpn_id="ORPHAN")}
        client = MockNSIPClient(lineages=lineages)

        tree = build_pedigree_tree("ORPHAN", generations=3, client=client)

        assert tree.subject.lpn_id == "ORPHAN"
        assert tree.sire is None
        assert tree.dam is None

    def test_client_closed(self, mock_lineages):
        """Verify client is closed when created internally."""
        with patch("nsip_skills.inbreeding.CachedNSIPClient") as mock_cls:
            mock_instance = MockNSIPClient(lineages=mock_lineages)
            mock_cls.return_value = mock_instance

            build_pedigree_tree(SAMPLE_LPNS[0], generations=2, client=None)

            assert mock_instance._closed is True


class TestFindCommonAncestors:
    """Tests for find_common_ancestors function."""

    def test_no_common_ancestors(self):
        """Verify no common ancestors when lineages don't overlap."""
        # Create non-overlapping pedigrees
        subject = PedigreeNode(lpn_id="CHILD", generation=0)
        sire = PedigreeNode(lpn_id="SIRE_UNIQUE", generation=1)
        dam = PedigreeNode(lpn_id="DAM_UNIQUE", generation=1)
        ss = PedigreeNode(lpn_id="SS_UNIQUE", generation=2)
        sd = PedigreeNode(lpn_id="SD_UNIQUE", generation=2)
        ds = PedigreeNode(lpn_id="DS_UNIQUE", generation=2)
        dd = PedigreeNode(lpn_id="DD_UNIQUE", generation=2)

        tree = PedigreeTree(
            subject=subject,
            sire=sire,
            dam=dam,
            sire_sire=ss,
            sire_dam=sd,
            dam_sire=ds,
            dam_dam=dd,
        )

        common = find_common_ancestors(tree)

        assert len(common) == 0

    def test_common_grandparent(self):
        """Verify detection of common grandparent (half-sibling mating)."""
        subject = PedigreeNode(lpn_id="CHILD", generation=0)
        sire = PedigreeNode(lpn_id="SIRE", generation=1)
        dam = PedigreeNode(lpn_id="DAM", generation=1)
        # Same sire for both parents = common ancestor
        common_grandparent = PedigreeNode(lpn_id="COMMON_SIRE", generation=2)

        tree = PedigreeTree(
            subject=subject,
            sire=sire,
            dam=dam,
            sire_sire=common_grandparent,
            dam_sire=common_grandparent,
        )

        common = find_common_ancestors(tree)

        assert "COMMON_SIRE" in common

    def test_multiple_common_ancestors(self):
        """Verify detection of multiple common ancestors."""
        subject = PedigreeNode(lpn_id="CHILD", generation=0)
        sire = PedigreeNode(lpn_id="SIRE", generation=1)
        dam = PedigreeNode(lpn_id="DAM", generation=1)
        common_ss = PedigreeNode(lpn_id="COMMON_SS", generation=2)
        common_sd = PedigreeNode(lpn_id="COMMON_SD", generation=2)

        tree = PedigreeTree(
            subject=subject,
            sire=sire,
            dam=dam,
            sire_sire=common_ss,
            sire_dam=common_sd,
            dam_sire=common_ss,
            dam_dam=common_sd,
        )

        common = find_common_ancestors(tree)

        assert "COMMON_SS" in common
        assert "COMMON_SD" in common


class TestTracePathsToAncestor:
    """Tests for trace_paths_to_ancestor function."""

    def test_direct_parent_path(self):
        """Verify path to parent is length 1."""
        subject = PedigreeNode(lpn_id="CHILD", generation=0)
        sire = PedigreeNode(lpn_id="SIRE", generation=1)

        tree = PedigreeTree(subject=subject, sire=sire)

        paths = trace_paths_to_ancestor(tree, "SIRE", "sire")

        # Path from sire side to sire should be 1 step
        # trace_paths_to_ancestor returns list of path lengths (integers)
        assert len(paths) > 0
        assert any(path == 1 for path in paths)

    def test_grandparent_path(self):
        """Verify path to grandparent is length 2."""
        subject = PedigreeNode(lpn_id="CHILD", generation=0)
        sire = PedigreeNode(lpn_id="SIRE", generation=1)
        sire_sire = PedigreeNode(lpn_id="SS", generation=2)

        tree = PedigreeTree(
            subject=subject,
            sire=sire,
            sire_sire=sire_sire,
        )

        paths = trace_paths_to_ancestor(tree, "SS", "sire")

        # Path from sire side to sire's sire should be 2 steps
        # trace_paths_to_ancestor returns list of path lengths (integers)
        assert len(paths) > 0
        assert any(path == 2 for path in paths)


class TestCalculatePathContribution:
    """Tests for calculate_path_contribution function."""

    def test_parent_contribution(self):
        """Verify contribution through single parent path.

        For direct parent mating: F = (1/2)^(1+1+1) = 0.125
        """
        # Single path through parent, length 1 on each side
        contribution = calculate_path_contribution(
            path_length_sire=1,
            path_length_dam=1,
            ancestor_inbreeding=0.0,
        )

        # (1/2)^(1+1+1) = (1/2)^3 = 0.125
        assert abs(contribution - 0.125) < 0.001

    def test_grandparent_contribution(self):
        """Verify contribution through grandparent paths.

        For common grandparent: F = (1/2)^(2+2+1) = 0.03125
        """
        contribution = calculate_path_contribution(
            path_length_sire=2,
            path_length_dam=2,
            ancestor_inbreeding=0.0,
        )

        # (1/2)^(2+2+1) = (1/2)^5 = 0.03125
        assert abs(contribution - 0.03125) < 0.001

    def test_inbred_ancestor_increases_contribution(self):
        """Verify inbred ancestor increases contribution.

        With FA = 0.25: (1/2)^n * (1 + FA)
        """
        contribution_normal = calculate_path_contribution(2, 2, 0.0)
        contribution_inbred = calculate_path_contribution(2, 2, 0.25)

        assert contribution_inbred > contribution_normal
        # Should be 1.25x the normal contribution
        assert abs(contribution_inbred - contribution_normal * 1.25) < 0.001


class TestCalculateInbreeding:
    """Tests for calculate_inbreeding function."""

    def test_no_inbreeding(self, mock_lineages):
        """Verify zero inbreeding for unrelated parents."""
        # Create unique lineage with no common ancestors
        lineages = {
            "CHILD": MockLineage(
                lpn_id="CHILD",
                sire="SIRE_A",
                dam="DAM_A",
            ),
            "SIRE_A": MockLineage(
                lpn_id="SIRE_A",
                sire="SS_A",
                dam="SD_A",
            ),
            "DAM_A": MockLineage(
                lpn_id="DAM_A",
                sire="DS_B",
                dam="DD_B",
            ),
        }
        client = MockNSIPClient(lineages=lineages)

        result = calculate_inbreeding("CHILD", generations=3, client=client)

        assert result.coefficient == 0.0
        assert result.risk_level == RiskLevel.LOW
        assert len(result.common_ancestors) == 0

    def test_half_sibling_mating(self):
        """Verify inbreeding from half-sibling mating.

        Half-siblings share one parent: F ≈ 0.125
        """
        # Create half-sibling mating: sire and dam share the same father
        lineages = {
            "CHILD": MockLineage(
                lpn_id="CHILD",
                sire="SIRE",
                dam="DAM",
                sire_sire="COMMON",  # Same grandparent
                dam_sire="COMMON",  # Same grandparent
            ),
            "SIRE": MockLineage(
                lpn_id="SIRE",
                sire="COMMON",
            ),
            "DAM": MockLineage(
                lpn_id="DAM",
                sire="COMMON",
            ),
            "COMMON": MockLineage(lpn_id="COMMON"),
        }
        client = MockNSIPClient(lineages=lineages)

        result = calculate_inbreeding("CHILD", generations=3, client=client)

        assert result.coefficient > 0
        assert "COMMON" in result.common_ancestors

    def test_risk_level_assignment(self):
        """Verify risk levels are assigned based on coefficient."""
        lineages = {
            "LOW": MockLineage(lpn_id="LOW"),
        }
        client = MockNSIPClient(lineages=lineages)

        result = calculate_inbreeding("LOW", generations=2, client=client)

        # With no common ancestors, should be low risk
        assert result.risk_level == RiskLevel.LOW

    def test_pedigree_included(self, mock_lineages):
        """Verify pedigree tree is included in result."""
        client = MockNSIPClient(lineages=mock_lineages)

        result = calculate_inbreeding(
            SAMPLE_LPNS[0],
            generations=3,
            client=client,
        )

        assert result.pedigree is not None
        assert result.pedigree.subject.lpn_id == SAMPLE_LPNS[0]


class TestCalculateProjectedOffspringInbreeding:
    """Tests for calculate_projected_offspring_inbreeding function."""

    def test_unrelated_parents(self):
        """Verify projected inbreeding for unrelated parents."""
        # Create unrelated parents
        lineages = {
            "SIRE": MockLineage(
                lpn_id="SIRE",
                sire="SS_A",
                dam="SD_A",
            ),
            "DAM": MockLineage(
                lpn_id="DAM",
                sire="DS_B",
                dam="DD_B",
            ),
        }
        client = MockNSIPClient(lineages=lineages)

        result = calculate_projected_offspring_inbreeding(
            "SIRE",
            "DAM",
            generations=3,
            client=client,
        )

        assert result.coefficient >= 0
        assert result.lpn_id == "SIRE x DAM (projected)"

    def test_related_parents_higher_inbreeding(self):
        """Verify projected inbreeding is higher for related parents."""
        # Create related parents (share a grandparent)
        lineages = {
            "SIRE": MockLineage(
                lpn_id="SIRE",
                sire="COMMON",
            ),
            "DAM": MockLineage(
                lpn_id="DAM",
                sire="COMMON",
            ),
            "COMMON": MockLineage(lpn_id="COMMON"),
        }
        client = MockNSIPClient(lineages=lineages)

        result = calculate_projected_offspring_inbreeding(
            "SIRE",
            "DAM",
            generations=3,
            client=client,
        )

        assert result.coefficient > 0
        assert "COMMON" in result.common_ancestors

    def test_risk_level_for_mating(self):
        """Verify risk level helps identify risky matings."""
        # Create parents that would produce high-risk offspring
        lineages = {
            "SIRE": MockLineage(lpn_id="SIRE", sire="COMMON", dam="COMMON2"),
            "DAM": MockLineage(lpn_id="DAM", sire="COMMON", dam="COMMON2"),
            "COMMON": MockLineage(lpn_id="COMMON"),
            "COMMON2": MockLineage(lpn_id="COMMON2"),
        }
        client = MockNSIPClient(lineages=lineages)

        result = calculate_projected_offspring_inbreeding(
            "SIRE",
            "DAM",
            generations=3,
            client=client,
        )

        # Should flag as risky mating
        assert result.risk_level in [RiskLevel.MODERATE, RiskLevel.HIGH]


class TestFormatInbreedingReport:
    """Tests for format_inbreeding_report function."""

    def test_basic_formatting(self):
        """Verify basic report formatting."""
        result = InbreedingResult(
            lpn_id="TEST123",
            coefficient=0.05,
        )

        output = format_inbreeding_report(result)

        assert "TEST123" in output
        assert "5" in output  # 5%

    def test_with_common_ancestors(self):
        """Verify common ancestors are shown."""
        result = InbreedingResult(
            lpn_id="TEST123",
            coefficient=0.10,
            common_ancestors=["ANCESTOR1", "ANCESTOR2"],
        )

        output = format_inbreeding_report(result)

        assert "ANCESTOR1" in output
        assert "ANCESTOR2" in output

    def test_risk_indicators(self):
        """Verify risk level is indicated."""
        low = InbreedingResult(lpn_id="LOW", coefficient=0.03)
        mod = InbreedingResult(lpn_id="MOD", coefficient=0.08)
        high = InbreedingResult(lpn_id="HIGH", coefficient=0.20)

        low_output = format_inbreeding_report(low)
        mod_output = format_inbreeding_report(mod)
        high_output = format_inbreeding_report(high)

        assert "low" in low_output.lower()
        assert "moderate" in mod_output.lower()
        assert "high" in high_output.lower()

    def test_with_pedigree(self):
        """Verify pedigree tree is included."""
        subject = PedigreeNode(lpn_id="CHILD", generation=0)
        sire = PedigreeNode(lpn_id="SIRE", generation=1)
        tree = PedigreeTree(subject=subject, sire=sire)

        result = InbreedingResult(
            lpn_id="CHILD",
            coefficient=0.05,
            pedigree=tree,
        )

        output = format_inbreeding_report(result)

        assert "CHILD" in output
        assert "SIRE" in output


class TestMainCLI:
    """Tests for main() CLI function."""

    def test_main_basic(self, mock_lineages):
        """Verify main CLI with basic arguments."""
        with patch("nsip_skills.inbreeding.CachedNSIPClient") as mock_cls:
            mock_instance = MockNSIPClient(lineages=mock_lineages)
            mock_cls.return_value = mock_instance

            with patch("sys.argv", ["inbreeding.py", SAMPLE_LPNS[0]]):
                from nsip_skills.inbreeding import main

                result = main()

                assert result == 0

    def test_main_with_generations(self, mock_lineages):
        """Verify main CLI with --generations flag."""
        with patch("nsip_skills.inbreeding.CachedNSIPClient") as mock_cls:
            mock_instance = MockNSIPClient(lineages=mock_lineages)
            mock_cls.return_value = mock_instance

            with patch(
                "sys.argv",
                ["inbreeding.py", SAMPLE_LPNS[0], "--generations", "5"],
            ):
                from nsip_skills.inbreeding import main

                result = main()

                assert result == 0

    def test_main_with_mating(self, mock_lineages):
        """Verify main CLI with --mating flag for projected offspring."""
        # Add dam lineage
        mock_lineages["DAM123"] = MockLineage(lpn_id="DAM123")

        with patch("nsip_skills.inbreeding.CachedNSIPClient") as mock_cls:
            mock_instance = MockNSIPClient(lineages=mock_lineages)
            mock_cls.return_value = mock_instance

            with patch(
                "sys.argv",
                ["inbreeding.py", SAMPLE_LPNS[0], "--mating", "DAM123"],
            ):
                from nsip_skills.inbreeding import main

                result = main()

                assert result == 0

    def test_main_json_output(self, mock_lineages):
        """Verify main CLI with --json flag."""
        with patch("nsip_skills.inbreeding.CachedNSIPClient") as mock_cls:
            mock_instance = MockNSIPClient(lineages=mock_lineages)
            mock_cls.return_value = mock_instance

            with patch("sys.argv", ["inbreeding.py", SAMPLE_LPNS[0], "--json"]):
                from nsip_skills.inbreeding import main

                result = main()

                assert result == 0

    def test_main_mating_json_output(self, mock_lineages):
        """Verify main CLI with --mating and --json flags."""
        mock_lineages["DAM456"] = MockLineage(lpn_id="DAM456")

        with patch("nsip_skills.inbreeding.CachedNSIPClient") as mock_cls:
            mock_instance = MockNSIPClient(lineages=mock_lineages)
            mock_cls.return_value = mock_instance

            with patch(
                "sys.argv",
                ["inbreeding.py", SAMPLE_LPNS[0], "--mating", "DAM456", "--json"],
            ):
                from nsip_skills.inbreeding import main

                result = main()

                assert result == 0

    def test_calculate_inbreeding_creates_client(self, mock_lineages):
        """Verify calculate_inbreeding creates and closes client when not provided."""
        with patch("nsip_skills.inbreeding.CachedNSIPClient") as mock_cls:
            mock_instance = MockNSIPClient(lineages=mock_lineages)
            mock_cls.return_value = mock_instance

            from nsip_skills.inbreeding import calculate_inbreeding

            calculate_inbreeding(SAMPLE_LPNS[0], generations=3, client=None)

            assert mock_instance._closed is True


class TestTracePathsEdgeCases:
    """Tests for trace_paths_to_ancestor edge cases."""

    def test_invalid_side(self):
        """Verify invalid side parameter raises ValueError."""
        import pytest

        subject = PedigreeNode(lpn_id="CHILD", generation=0)
        tree = PedigreeTree(subject=subject)

        with pytest.raises(ValueError, match="Invalid side"):
            trace_paths_to_ancestor(tree, "TARGET", "invalid")

    def test_ancestor_is_subject(self):
        """Verify path to subject returns empty (can't be own ancestor)."""
        subject = PedigreeNode(lpn_id="CHILD", generation=0)
        tree = PedigreeTree(subject=subject)

        paths = trace_paths_to_ancestor(tree, "CHILD", "sire")

        # Subject can't be its own ancestor through sire side
        assert len(paths) == 0

    def test_dam_side_path(self):
        """Verify path tracing through dam side."""
        subject = PedigreeNode(lpn_id="CHILD", generation=0)
        dam = PedigreeNode(lpn_id="DAM", generation=1)
        dam_dam = PedigreeNode(lpn_id="DD", generation=2)

        tree = PedigreeTree(
            subject=subject,
            dam=dam,
            dam_dam=dam_dam,
        )

        paths = trace_paths_to_ancestor(tree, "DD", "dam")

        assert len(paths) > 0
        assert any(path == 2 for path in paths)
