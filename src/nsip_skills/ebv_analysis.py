"""
EBV (Estimated Breeding Value) analysis module.

Compare and rank animals by their genetic traits, identify strengths
and weaknesses, and provide trait-based recommendations.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass, field
from typing import Any

from nsip_skills.common.data_models import (
    TraitProfile,
    TraitValue,
)
from nsip_skills.common.formatters import format_markdown_table, format_trait_comparison
from nsip_skills.common.nsip_wrapper import CachedNSIPClient


@dataclass
class EBVComparison:
    """Result of comparing EBVs across multiple animals."""

    profiles: list[TraitProfile] = field(default_factory=list)
    trait_stats: dict[str, dict[str, float]] = field(
        default_factory=dict
    )  # trait -> {mean, std, min, max}
    rankings: dict[str, list[str]] = field(
        default_factory=dict
    )  # trait -> [lpn_id sorted best to worst]
    top_overall: list[str] = field(default_factory=list)  # Animals with most top-25% traits
    needs_work: list[str] = field(default_factory=list)  # Animals with most bottom-25% traits

    def to_dict(self) -> dict[str, Any]:
        return {
            "profiles": [p.to_dict() for p in self.profiles],
            "trait_stats": self.trait_stats,
            "rankings": self.rankings,
            "top_overall": self.top_overall,
            "needs_work": self.needs_work,
        }


# Higher is better for most traits, but not all
LOWER_IS_BETTER = {"BWT", "YFAT", "PFAT", "FAT", "DAG", "FEC", "WFEC", "PFEC"}


def calculate_percentile(value: float, values: list[float], lower_is_better: bool = False) -> float:
    """Calculate percentile rank of a value within a list."""
    if not values:
        return 50.0

    sorted_values = sorted(values)
    n = len(sorted_values)

    # Count values less than the given value
    count_below = sum(1 for v in sorted_values if v < value)

    if lower_is_better:
        # Invert: lower values should get higher percentiles
        count_below = sum(1 for v in sorted_values if v > value)

    return (count_below / n) * 100


def analyze_traits(
    lpn_ids: list[str],
    traits: list[str] | None = None,
    client: CachedNSIPClient | None = None,
    breed_context: int | None = None,
) -> EBVComparison:
    """
    Analyze and compare EBV traits across multiple animals.

    Args:
        lpn_ids: List of LPN IDs to analyze
        traits: Specific traits to analyze (None = all available)
        client: Optional pre-configured client
        breed_context: Breed ID for context (percentile calculations)

    Returns:
        EBVComparison with profiles, stats, and rankings

    Example:
        comparison = analyze_traits(["LPN1", "LPN2", "LPN3"])
        print(f"Top performer for WWT: {comparison.rankings['WWT'][0]}")
    """
    should_close = client is None
    if client is None:
        client = CachedNSIPClient()

    try:
        # Fetch all animal details
        fetched = client.batch_get_animals(lpn_ids, on_error="skip")

        # Build profiles
        profiles: list[TraitProfile] = []
        all_trait_values: dict[str, list[tuple[str, float]]] = {}  # trait -> [(lpn_id, value)]

        for lpn_id in lpn_ids:
            data = fetched.get(lpn_id, {})
            if "error" in data or "details" not in data:
                continue

            details = data["details"]
            profile = TraitProfile(
                lpn_id=lpn_id,
                breed=details.breed,
            )

            for trait_name, trait_obj in details.traits.items():
                if traits and trait_name not in traits:
                    continue

                profile.traits[trait_name] = TraitValue(
                    name=trait_name,
                    value=trait_obj.value,
                    accuracy=trait_obj.accuracy,
                )

                if trait_name not in all_trait_values:
                    all_trait_values[trait_name] = []
                all_trait_values[trait_name].append((lpn_id, trait_obj.value))

            profiles.append(profile)

        # Calculate statistics and rankings
        result = EBVComparison(profiles=profiles)

        for trait_name, values in all_trait_values.items():
            trait_values = [v for _, v in values]

            if trait_values:
                result.trait_stats[trait_name] = {
                    "mean": statistics.mean(trait_values),
                    "std": statistics.stdev(trait_values) if len(trait_values) > 1 else 0,
                    "min": min(trait_values),
                    "max": max(trait_values),
                    "count": len(trait_values),
                }

                # Rank animals by this trait
                lower_better = trait_name in LOWER_IS_BETTER
                sorted_by_trait = sorted(
                    values,
                    key=lambda x: x[1],
                    reverse=not lower_better,
                )
                result.rankings[trait_name] = [lpn_id for lpn_id, _ in sorted_by_trait]

        # Calculate percentiles and identify strengths/weaknesses
        for profile in profiles:
            strengths = []
            weaknesses = []

            for trait_name, trait_val in profile.traits.items():
                trait_floats: list[float] = [v for _, v in all_trait_values.get(trait_name, [])]
                if not trait_floats:
                    continue

                lower_better = trait_name in LOWER_IS_BETTER
                percentile = calculate_percentile(trait_val.value, trait_floats, lower_better)
                trait_val.percentile = percentile

                if percentile >= 75:
                    strengths.append(trait_name)
                elif percentile <= 25:
                    weaknesses.append(trait_name)

            profile.strengths = strengths
            profile.weaknesses = weaknesses

        # Identify overall top performers and those needing work
        strength_counts = [(p.lpn_id, len(p.strengths)) for p in profiles]
        weakness_counts = [(p.lpn_id, len(p.weaknesses)) for p in profiles]

        strength_counts.sort(key=lambda x: x[1], reverse=True)
        weakness_counts.sort(key=lambda x: x[1], reverse=True)

        result.top_overall = [lpn_id for lpn_id, count in strength_counts if count > 0][:5]
        result.needs_work = [lpn_id for lpn_id, count in weakness_counts if count > 0][:5]

        return result

    finally:
        if should_close and client:
            client.close()


def get_breed_ranges(
    breed_id: int, client: CachedNSIPClient | None = None
) -> dict[str, dict[str, float]]:
    """
    Get trait ranges for a breed to provide context for EBV values.

    Returns dict of trait -> {min, max} from breed population.
    """
    should_close = client is None
    if client is None:
        client = CachedNSIPClient()

    try:
        return client.get_trait_ranges_by_breed(breed_id)
    finally:
        if should_close and client:
            client.close()


def format_ebv_report(comparison: EBVComparison, traits: list[str] | None = None) -> str:
    """Format EBV comparison as a human-readable report."""
    lines = ["## EBV Trait Analysis", ""]

    # Summary stats
    if comparison.trait_stats:
        lines.append("### Trait Statistics")
        headers = ["Trait", "Mean", "Std Dev", "Min", "Max", "Count"]
        rows = []
        for trait, stats in sorted(comparison.trait_stats.items()):
            rows.append(
                [
                    trait,
                    f"{stats['mean']:.3f}",
                    f"{stats['std']:.3f}",
                    f"{stats['min']:.3f}",
                    f"{stats['max']:.3f}",
                    int(stats["count"]),
                ]
            )
        lines.append(format_markdown_table(headers, rows))
        lines.append("")

    # Animal comparison
    if comparison.profiles:
        lines.append("### Animal Comparison")
        lines.append(format_trait_comparison(comparison.profiles, traits))
        lines.append("")

    # Top performers
    if comparison.top_overall:
        lines.append(f"**Top Performers** (most strengths): {', '.join(comparison.top_overall)}")

    if comparison.needs_work:
        lines.append(f"**Needs Improvement** (most weaknesses): {', '.join(comparison.needs_work)}")

    # Rankings
    if comparison.rankings:
        lines.append("")
        lines.append("### Rankings by Trait")
        for trait, ranked_ids in sorted(comparison.rankings.items()):
            top_3 = ranked_ids[:3]
            lines.append(f"- **{trait}**: {' > '.join(top_3)}")

    return "\n".join(lines)


def main():
    """Command-line interface for EBV analysis."""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Analyze and compare EBV traits")
    parser.add_argument("lpn_ids", nargs="+", help="LPN IDs to analyze")
    parser.add_argument("--traits", nargs="+", help="Specific traits to analyze")
    parser.add_argument("--breed", type=int, help="Breed ID for context")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    comparison = analyze_traits(
        lpn_ids=args.lpn_ids,
        traits=args.traits,
        breed_context=args.breed,
    )

    if args.json:
        print(json.dumps(comparison.to_dict(), indent=2, default=str))
    else:
        print(format_ebv_report(comparison, args.traits))

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
