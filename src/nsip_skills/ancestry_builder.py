"""
Ancestry/pedigree report generation module.

Build and visualize pedigree trees with comprehensive ancestor information.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from nsip_skills.common.data_models import PedigreeTree
from nsip_skills.common.formatters import format_pedigree_tree
from nsip_skills.common.nsip_wrapper import CachedNSIPClient
from nsip_skills.inbreeding import build_pedigree_tree

logger = logging.getLogger(__name__)


@dataclass
class AncestryReport:
    """Complete ancestry report for an animal."""

    subject_lpn: str
    pedigree: PedigreeTree
    bloodline_breakdown: dict[str, float] = field(
        default_factory=dict
    )  # ancestor -> % contribution
    notable_ancestors: list[dict[str, Any]] = field(default_factory=list)
    genetic_diversity: float = 0.0  # 0-1 score based on unique ancestors

    def to_dict(self) -> dict[str, Any]:
        return {
            "subject_lpn": self.subject_lpn,
            "pedigree": self.pedigree.to_dict(),
            "bloodline_breakdown": self.bloodline_breakdown,
            "notable_ancestors": self.notable_ancestors,
            "genetic_diversity": self.genetic_diversity,
        }


def calculate_bloodline_breakdown(tree: PedigreeTree) -> dict[str, float]:
    """
    Calculate genetic contribution from each grandparent.

    Returns dict of grandparent LPN -> percentage contribution.
    """
    breakdown = {}

    # Each grandparent contributes 25% theoretically
    grandparents = [
        ("Sire's Sire", tree.sire_sire),
        ("Sire's Dam", tree.sire_dam),
        ("Dam's Sire", tree.dam_sire),
        ("Dam's Dam", tree.dam_dam),
    ]

    for label, node in grandparents:
        if node:
            key = f"{label} ({node.lpn_id})"
            breakdown[key] = 25.0
        else:
            breakdown[f"{label} (Unknown)"] = 25.0

    return breakdown


def calculate_genetic_diversity(tree: PedigreeTree) -> float:
    """
    Calculate genetic diversity score based on unique ancestors.

    Score of 1.0 means all ancestors are unique.
    Lower scores indicate inbreeding/repeated ancestors.
    """
    ancestors = tree.all_ancestors()
    if not ancestors:
        return 1.0

    unique_ids = {a.lpn_id for a in ancestors}
    total_positions = len(ancestors)

    return len(unique_ids) / total_positions


def identify_notable_ancestors(
    tree: PedigreeTree,
    client: CachedNSIPClient,
) -> list[dict[str, Any]]:
    """
    Identify notable ancestors (high progeny count, high index scores).
    """
    notable = []

    for ancestor in tree.all_ancestors():
        try:
            details = client.get_animal_details(ancestor.lpn_id)

            # Consider notable if high progeny count or proven
            is_notable = False
            reasons = []

            if details.total_progeny and details.total_progeny > 50:
                is_notable = True
                reasons.append(f"{details.total_progeny} progeny")

            # Check if they have high index values
            if ancestor.us_index and ancestor.us_index > 100:
                is_notable = True
                reasons.append(f"US Index: {ancestor.us_index:.0f}")

            if is_notable:
                notable.append(
                    {
                        "lpn_id": ancestor.lpn_id,
                        "generation": ancestor.generation,
                        "reasons": reasons,
                        "farm": ancestor.farm_name or "Unknown",
                    }
                )

        except Exception as e:
            # Log and skip ancestors whose details can't be fetched
            logger.debug(f"Could not fetch details for ancestor {ancestor.lpn_id}: {e}")
            continue

    return notable


def generate_ancestry_report(
    lpn_id: str,
    generations: int = 4,
    include_notable: bool = True,
    client: CachedNSIPClient | None = None,
) -> AncestryReport:
    """
    Generate a comprehensive ancestry report.

    Args:
        lpn_id: Subject animal's LPN ID
        generations: Number of generations to trace (default: 4)
        include_notable: Include notable ancestor analysis
        client: Optional pre-configured client

    Returns:
        AncestryReport with pedigree and analysis
    """
    should_close = client is None
    if client is None:
        client = CachedNSIPClient()

    try:
        # Build pedigree tree
        pedigree = build_pedigree_tree(lpn_id, generations=generations, client=client)

        # Calculate metrics
        bloodline = calculate_bloodline_breakdown(pedigree)
        diversity = calculate_genetic_diversity(pedigree)

        # Find notable ancestors if requested
        notable = []
        if include_notable:
            notable = identify_notable_ancestors(pedigree, client)

        return AncestryReport(
            subject_lpn=lpn_id,
            pedigree=pedigree,
            bloodline_breakdown=bloodline,
            notable_ancestors=notable,
            genetic_diversity=diversity,
        )

    finally:
        if should_close and client:
            client.close()


def format_ancestry_report(report: AncestryReport, style: str = "ascii") -> str:
    """Format ancestry report as human-readable text."""
    lines = [
        f"## Ancestry Report: {report.subject_lpn}",
        "",
    ]

    # Pedigree tree
    lines.append("### Pedigree")
    lines.append(format_pedigree_tree(report.pedigree, style=style))
    lines.append("")

    # Bloodline breakdown
    lines.append("### Bloodline Breakdown")
    for ancestor, pct in report.bloodline_breakdown.items():
        lines.append(f"- {ancestor}: {pct:.1f}%")
    lines.append("")

    # Genetic diversity
    lines.append(f"**Genetic Diversity Score**: {report.genetic_diversity:.2f}")
    if report.genetic_diversity < 0.9:
        lines.append("  (Lower score indicates repeated ancestors/inbreeding)")
    lines.append("")

    # Notable ancestors
    if report.notable_ancestors:
        lines.append("### Notable Ancestors")
        for notable in report.notable_ancestors:
            reasons = ", ".join(notable["reasons"])
            lines.append(f"- **{notable['lpn_id']}** (Gen {notable['generation']}): {reasons}")
            lines.append(f"  Farm: {notable['farm']}")

    # Common ancestors (if any)
    if report.pedigree.common_ancestors:
        lines.append("")
        lines.append("### Common Ancestors (Inbreeding Indicators)")
        for ca in report.pedigree.common_ancestors:
            lines.append(f"- {ca}")

    return "\n".join(lines)


def main():
    """Command-line interface for ancestry reports."""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Generate ancestry/pedigree reports")
    parser.add_argument("lpn_id", help="Animal LPN ID")
    parser.add_argument("--generations", "-g", type=int, default=4, help="Generations to trace")
    parser.add_argument("--style", choices=["ascii", "markdown"], default="ascii")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    report = generate_ancestry_report(
        lpn_id=args.lpn_id,
        generations=args.generations,
    )

    if args.json:
        print(json.dumps(report.to_dict(), indent=2, default=str))
    else:
        print(format_ancestry_report(report, style=args.style))

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
