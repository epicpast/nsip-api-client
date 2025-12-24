"""
Progeny performance analysis module.

Evaluate sires and dams by their offspring performance.
"""

from __future__ import annotations

import logging
import statistics
from dataclasses import dataclass, field
from typing import Any

from nsip_skills.common.data_models import (
    PRESET_INDEXES,
    ProgenyStats,
    SelectionIndex,
)
from nsip_skills.common.formatters import format_markdown_table, format_progeny_stats
from nsip_skills.common.nsip_wrapper import CachedNSIPClient

logger = logging.getLogger(__name__)


@dataclass
class ProgenyAnalysisResult:
    """Result of analyzing a parent's progeny."""

    parent_lpn: str
    parent_gender: str
    stats: ProgenyStats
    progeny_details: list[dict[str, Any]] = field(default_factory=list)
    comparison_to_breed: dict[str, float] = field(default_factory=dict)  # trait -> diff from avg

    def to_dict(self) -> dict[str, Any]:
        return {
            "parent_lpn": self.parent_lpn,
            "parent_gender": self.parent_gender,
            "stats": self.stats.to_dict(),
            "progeny_details": self.progeny_details,
            "comparison_to_breed": self.comparison_to_breed,
        }


@dataclass
class SireComparisonResult:
    """Result of comparing multiple sires by progeny performance."""

    sires: list[ProgenyAnalysisResult] = field(default_factory=list)
    rankings: dict[str, list[str]] = field(default_factory=dict)  # trait -> [sire_lpn sorted]
    best_overall: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "sires": [s.to_dict() for s in self.sires],
            "rankings": self.rankings,
            "best_overall": self.best_overall,
        }


def analyze_progeny(
    parent_lpn: str,
    traits: list[str] | None = None,
    index: SelectionIndex | None = None,
    client: CachedNSIPClient | None = None,
) -> ProgenyAnalysisResult:
    """
    Analyze a parent's progeny performance.

    Args:
        parent_lpn: Sire or dam LPN ID
        traits: Specific traits to analyze (None = all)
        index: Selection index for scoring (default: range index)
        client: Optional pre-configured client

    Returns:
        ProgenyAnalysisResult with statistics and rankings
    """
    should_close = client is None
    if client is None:
        client = CachedNSIPClient()

    if index is None:
        index = PRESET_INDEXES["range"]

    try:
        # Get parent details to determine gender
        parent_details = client.get_animal_details(parent_lpn)
        parent_gender = parent_details.gender or "Unknown"

        # Get all progeny
        all_progeny = client.get_all_progeny(parent_lpn)

        stats = ProgenyStats(
            parent_lpn=parent_lpn,
            parent_gender=parent_gender,
            total_progeny=len(all_progeny),
        )

        # Collect trait values across progeny
        trait_values: dict[str, list[float]] = {}
        progeny_scores: list[tuple[str, float]] = []
        progeny_details: list[dict[str, Any]] = []

        # Pre-fetch all progeny details to avoid N+1 query pattern
        # This reduces API calls from O(n) to O(1) batch call
        progeny_lpns = [p.get("lpn_id", "") for p in all_progeny if p.get("lpn_id")]
        fetched_details = client.batch_get_animals(progeny_lpns, on_error="skip")

        for progeny in all_progeny:
            lpn = progeny.get("lpn_id", "")
            sex = progeny.get("sex", "")

            if sex and sex.lower().startswith("m"):
                stats.male_count += 1
            elif sex and sex.lower().startswith("f"):
                stats.female_count += 1

            # Get detailed traits from pre-fetched data
            fetched_data = fetched_details.get(lpn, {})
            details = fetched_data.get("details")
            if not details:
                logger.debug(f"Could not fetch details for progeny {lpn}")
                continue

            ebvs = {}
            for trait_name, trait_obj in details.traits.items():
                if traits and trait_name not in traits:
                    continue

                if trait_name not in trait_values:
                    trait_values[trait_name] = []
                trait_values[trait_name].append(trait_obj.value)
                ebvs[trait_name] = trait_obj.value

            # Calculate index score
            score = index.calculate_score(ebvs)
            progeny_scores.append((lpn, score))

            progeny_details.append(
                {
                    "lpn_id": lpn,
                    "sex": sex,
                    "date_of_birth": details.date_of_birth,
                    "ebvs": ebvs,
                    "index_score": score,
                }
            )

        # Calculate statistics
        for trait_name, values in trait_values.items():
            if values:
                stats.trait_means[trait_name] = statistics.mean(values)
                if len(values) > 1:
                    stats.trait_std_devs[trait_name] = statistics.stdev(values)
                else:
                    stats.trait_std_devs[trait_name] = 0.0

        # Identify top/bottom performers
        progeny_scores.sort(key=lambda x: x[1], reverse=True)

        n = len(progeny_scores)
        top_10_pct = max(1, n // 10)
        stats.top_performers = [lpn for lpn, _ in progeny_scores[:top_10_pct]]
        stats.bottom_performers = [lpn for lpn, _ in progeny_scores[-top_10_pct:]]

        return ProgenyAnalysisResult(
            parent_lpn=parent_lpn,
            parent_gender=parent_gender,
            stats=stats,
            progeny_details=progeny_details,
        )

    finally:
        if should_close and client:
            client.close()


def compare_sires(
    sire_lpns: list[str],
    traits: list[str] | None = None,
    index: SelectionIndex | None = None,
    client: CachedNSIPClient | None = None,
) -> SireComparisonResult:
    """
    Compare multiple sires by their progeny performance.

    Args:
        sire_lpns: List of sire LPN IDs to compare
        traits: Specific traits to analyze
        index: Selection index for scoring
        client: Optional pre-configured client

    Returns:
        SireComparisonResult with rankings by trait
    """
    should_close = client is None
    if client is None:
        client = CachedNSIPClient()

    result = SireComparisonResult()

    try:
        # Analyze each sire
        for lpn in sire_lpns:
            try:
                analysis = analyze_progeny(lpn, traits=traits, index=index, client=client)
                result.sires.append(analysis)
            except Exception as e:
                # Log warning instead of silently skipping sires
                logger.warning(f"Could not analyze sire {lpn}: {e}")
                continue

        if not result.sires:
            return result

        # Rank sires by each trait (higher mean = better)
        all_traits: set[str] = set()
        for sire in result.sires:
            all_traits.update(sire.stats.trait_means.keys())

        for trait in all_traits:
            sire_trait_means = [
                (s.parent_lpn, s.stats.trait_means.get(trait, 0)) for s in result.sires
            ]
            sire_trait_means.sort(key=lambda x: x[1], reverse=True)
            result.rankings[trait] = [lpn for lpn, _ in sire_trait_means]

        # Determine best overall (most first-place rankings)
        ranking_counts: dict[str, int] = {}
        for ranked_list in result.rankings.values():
            if ranked_list:
                top_sire = ranked_list[0]
                ranking_counts[top_sire] = ranking_counts.get(top_sire, 0) + 1

        if ranking_counts:
            result.best_overall = max(ranking_counts, key=lambda k: ranking_counts.get(k, 0))

        return result

    finally:
        if should_close and client:
            client.close()


def format_sire_comparison(result: SireComparisonResult) -> str:
    """Format sire comparison as markdown."""
    lines = ["## Sire Comparison by Progeny Performance", ""]

    if not result.sires:
        return "No sires to compare."

    # Summary table
    summary_headers = ["Sire", "Total Progeny", "Males", "Females"]
    summary_rows: list[list[Any]] = []
    for sire in result.sires:
        summary_rows.append(
            [
                sire.parent_lpn,
                sire.stats.total_progeny,
                sire.stats.male_count,
                sire.stats.female_count,
            ]
        )
    lines.append(format_markdown_table(summary_headers, summary_rows))
    lines.append("")

    # Trait means comparison
    if result.sires:
        all_traits = sorted(set().union(*[set(s.stats.trait_means.keys()) for s in result.sires]))
        if all_traits:
            lines.append("### Progeny Trait Means")
            trait_headers = ["Sire"] + all_traits
            trait_rows: list[list[str]] = []
            for sire in result.sires:
                trait_row: list[str] = [sire.parent_lpn]
                for trait in all_traits:
                    mean = sire.stats.trait_means.get(trait)
                    trait_row.append(f"{mean:.3f}" if mean is not None else "-")
                trait_rows.append(trait_row)
            lines.append(format_markdown_table(trait_headers, trait_rows))
            lines.append("")

    # Rankings
    if result.rankings:
        lines.append("### Rankings by Trait")
        for trait, ranked in sorted(result.rankings.items()):
            lines.append(f"- **{trait}**: {' > '.join(ranked)}")
        lines.append("")

    if result.best_overall:
        lines.append(f"**Best Overall Sire**: {result.best_overall}")

    return "\n".join(lines)


def main():
    """Command-line interface for progeny analysis."""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Analyze progeny performance")
    parser.add_argument("sire_lpns", nargs="+", help="Sire LPN ID(s)")
    parser.add_argument("--traits", nargs="+", help="Specific traits to analyze")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if len(args.sire_lpns) == 1:
        analysis_result = analyze_progeny(args.sire_lpns[0], traits=args.traits)
        if args.json:
            print(json.dumps(analysis_result.to_dict(), indent=2, default=str))
        else:
            print(format_progeny_stats(analysis_result.stats))
    else:
        comparison_result = compare_sires(args.sire_lpns, traits=args.traits)
        if args.json:
            print(json.dumps(comparison_result.to_dict(), indent=2, default=str))
        else:
            print(format_sire_comparison(comparison_result))

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
