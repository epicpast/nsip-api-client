"""
Flock statistics and dashboard module.

Calculate aggregate statistics and generate flock performance summaries.
"""

from __future__ import annotations

import statistics
from collections import Counter
from dataclasses import dataclass, field
from typing import Any

from nsip_skills.common.data_models import (
    PRESET_INDEXES,
    AnimalAnalysis,
    FlockSummary,
    SelectionIndex,
    TraitProfile,
    TraitValue,
)
from nsip_skills.common.formatters import format_flock_summary
from nsip_skills.common.nsip_wrapper import CachedNSIPClient


@dataclass
class FlockDashboard:
    """Complete flock performance dashboard."""

    summary: FlockSummary
    breed_breakdown: dict[str, FlockSummary] = field(default_factory=dict)  # Per-breed stats
    index_rankings: dict[str, list[tuple[str, float]]] = field(
        default_factory=dict
    )  # index -> [(lpn, score)]
    improvement_opportunities: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary.to_dict(),
            "breed_breakdown": {k: v.to_dict() for k, v in self.breed_breakdown.items()},
            "index_rankings": self.index_rankings,
            "improvement_opportunities": self.improvement_opportunities,
        }


def _update_gender_counts(summary: FlockSummary, gender: str | None) -> None:
    """Update gender counts in summary."""
    if gender:
        if gender.lower().startswith("m"):
            summary.male_count += 1
        elif gender.lower().startswith("f"):
            summary.female_count += 1


def _process_animal_traits(
    details: Any,
    lpn_id: str,
    trait_values: dict[str, list[float]],
    indexes: list[SelectionIndex],
    index_scores: dict[str, list[tuple[str, float]]],
) -> tuple[TraitProfile, dict[str, float]]:
    """Process animal traits and calculate index scores."""
    ebvs: dict[str, float] = {}
    trait_profile = TraitProfile(lpn_id=lpn_id, breed=details.breed)

    for trait_name, trait_obj in details.traits.items():
        if trait_name not in trait_values:
            trait_values[trait_name] = []
        trait_values[trait_name].append(trait_obj.value)
        ebvs[trait_name] = trait_obj.value
        trait_profile.traits[trait_name] = TraitValue(
            name=trait_name, value=trait_obj.value, accuracy=trait_obj.accuracy
        )

    animal_index_scores = {}
    for idx in indexes:
        score = idx.calculate_score(ebvs)
        index_scores[idx.name].append((lpn_id, score))
        animal_index_scores[idx.name] = score

    return trait_profile, animal_index_scores


def _compute_trait_summary(trait_values: dict[str, list[float]]) -> dict[str, dict[str, float]]:
    """Compute summary statistics for all traits."""
    result: dict[str, dict[str, float]] = {}
    for trait, values in trait_values.items():
        if values:
            result[trait] = {
                "mean": statistics.mean(values),
                "median": statistics.median(values),
                "std": statistics.stdev(values) if len(values) > 1 else 0,
                "min": min(values),
                "max": max(values),
                "count": len(values),
            }
    return result


def calculate_flock_stats(
    lpn_ids: list[str],
    flock_name: str | None = None,
    indexes: list[SelectionIndex] | None = None,
    client: CachedNSIPClient | None = None,
) -> FlockDashboard:
    """
    Calculate comprehensive flock statistics.

    Args:
        lpn_ids: LPN IDs of all animals in flock
        flock_name: Optional name for the flock
        indexes: Selection indexes to calculate (default: all presets)
        client: Optional pre-configured client

    Returns:
        FlockDashboard with summary and analysis
    """
    should_close = client is None
    if client is None:
        client = CachedNSIPClient()

    if indexes is None:
        indexes = list(PRESET_INDEXES.values())

    try:
        fetched = client.batch_get_animals(lpn_ids, on_error="skip")
        summary = FlockSummary(flock_name=flock_name, total_animals=len(lpn_ids))

        trait_values: dict[str, list[float]] = {}
        status_counts: Counter[str] = Counter()
        breed_counts: Counter[str] = Counter()
        birth_years: Counter[str] = Counter()
        animal_analyses: list[AnimalAnalysis] = []
        index_scores: dict[str, list[tuple[str, float]]] = {idx.name: [] for idx in indexes}

        for lpn_id in lpn_ids:
            data = fetched.get(lpn_id, {})
            if "error" in data or "details" not in data:
                continue

            details = data["details"]
            _update_gender_counts(summary, details.gender)

            if details.status:
                status_counts[details.status] += 1
            if details.breed:
                breed_counts[details.breed] += 1
            if details.date_of_birth:
                birth_years[details.date_of_birth[:4]] += 1

            trait_profile, animal_index_scores = _process_animal_traits(
                details, lpn_id, trait_values, indexes, index_scores
            )

            animal_analyses.append(
                AnimalAnalysis(
                    lpn_id=lpn_id,
                    breed=details.breed,
                    gender=details.gender,
                    date_of_birth=details.date_of_birth,
                    status=details.status,
                    sire_lpn=details.sire,
                    dam_lpn=details.dam,
                    trait_profile=trait_profile,
                    progeny_count=details.total_progeny,
                    index_scores=animal_index_scores,
                )
            )

        summary.status_breakdown = dict(status_counts)
        summary.breed_breakdown = dict(breed_counts)
        summary.age_distribution = dict(birth_years)
        summary.trait_summary = _compute_trait_summary(trait_values)

        for idx_name in index_scores:
            index_scores[idx_name].sort(key=lambda x: x[1], reverse=True)

        if indexes and index_scores[indexes[0].name]:
            top_lpns = [lpn for lpn, _ in index_scores[indexes[0].name][:10]]
            summary.top_performers = [a for a in animal_analyses if a.lpn_id in top_lpns][:5]

        opportunities = _identify_opportunities(summary, trait_values)
        summary.recommendations = opportunities

        return FlockDashboard(
            summary=summary, index_rankings=index_scores, improvement_opportunities=opportunities
        )

    finally:
        if should_close and client:
            client.close()


def _identify_opportunities(
    summary: FlockSummary,
    trait_values: dict[str, list[float]],
) -> list[str]:
    """Identify improvement opportunities from flock statistics."""
    opportunities = []

    # Check trait variability
    for trait, values in trait_values.items():
        if len(values) < 5:
            continue

        cv = (
            statistics.stdev(values) / abs(statistics.mean(values))
            if statistics.mean(values) != 0
            else 0
        )

        if cv > 0.5:
            opportunities.append(
                f"High variability in {trait} (CV={cv:.1%}). "
                f"Opportunity to standardize through selection."
            )

    # Check for underperforming traits
    if summary.trait_summary:
        # Find traits with negative means (below breed average)
        negative_traits = [t for t, s in summary.trait_summary.items() if s.get("mean", 0) < 0]
        if negative_traits:
            opportunities.append(
                f"Below breed average on: {', '.join(negative_traits)}. "
                f"Consider rams with strong performance in these areas."
            )

    # Age distribution check
    if summary.age_distribution:
        years = sorted(summary.age_distribution.keys())
        if len(years) >= 2:
            recent = summary.age_distribution.get(years[-1], 0)
            older = sum(summary.age_distribution.get(y, 0) for y in years[:-1])
            if recent < older * 0.3:
                opportunities.append(
                    "Low proportion of young animals. Consider retaining more replacements."
                )

    # Gender balance
    if summary.male_count > 0 and summary.female_count > 0:
        ratio = summary.male_count / summary.female_count
        if ratio > 0.15:  # More than 15% rams
            opportunities.append(
                f"High ram:ewe ratio ({ratio:.1%}). Consider culling underperforming rams."
            )

    return opportunities


def compare_to_breed_average(
    summary: FlockSummary,
    breed_id: int,
    client: CachedNSIPClient | None = None,
) -> dict[str, float]:
    """
    Compare flock trait means to breed population ranges.

    Returns dict of trait -> percentile position within breed range.
    """
    should_close = client is None
    if client is None:
        client = CachedNSIPClient()

    try:
        breed_ranges = client.get_trait_ranges_by_breed(breed_id)
        comparisons = {}

        for trait, stats in summary.trait_summary.items():
            if trait not in breed_ranges:
                continue

            trait_range = breed_ranges[trait]
            breed_min = trait_range.get("min", 0)
            breed_max = trait_range.get("max", 0)
            flock_mean = stats.get("mean", 0)

            if breed_max != breed_min:
                percentile = ((flock_mean - breed_min) / (breed_max - breed_min)) * 100
                comparisons[trait] = max(0, min(100, percentile))

        return comparisons

    finally:
        if should_close and client:
            client.close()


def format_flock_dashboard(dashboard: FlockDashboard) -> str:
    """Format complete flock dashboard as markdown."""
    lines = [format_flock_summary(dashboard.summary)]

    # Index rankings
    if dashboard.index_rankings:
        lines.append("")
        lines.append("### Selection Index Rankings")

        for idx_name, rankings in dashboard.index_rankings.items():
            if rankings:
                lines.append(f"\n**{idx_name}**")
                top_5 = rankings[:5]
                for rank, (lpn, score) in enumerate(top_5, 1):
                    lines.append(f"{rank}. {lpn}: {score:.2f}")

    return "\n".join(lines)


def _extract_lpn_ids_from_source(source: str) -> list[str]:
    """Extract LPN IDs from a file path or return as-is if already LPN IDs."""
    from pathlib import Path

    from nsip_skills.common.spreadsheet_io import extract_flock_records, read_spreadsheet

    # Check if source looks like a file path
    path = Path(source)
    is_file = (
        path.exists()
        or source.endswith(".csv")
        or source.endswith(".xlsx")
        or source.startswith("http")
    )

    if is_file and path.exists():
        # Read spreadsheet and extract LPN IDs
        data = read_spreadsheet(source)
        records = extract_flock_records(data)
        return [r.lpn_id for r in records]

    return [source]  # Treat as single LPN ID


def main():
    """Command-line interface for flock statistics."""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Calculate flock statistics")
    parser.add_argument(
        "source",
        nargs="+",
        help="Flock data source: file path (CSV/Excel) or LPN IDs",
    )
    parser.add_argument("--name", help="Flock name")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    # Extract LPN IDs from source(s)
    lpn_ids: list[str] = []
    for src in args.source:
        lpn_ids.extend(_extract_lpn_ids_from_source(src))

    dashboard = calculate_flock_stats(
        lpn_ids=lpn_ids,
        flock_name=args.name,
    )

    if args.json:
        print(json.dumps(dashboard.to_dict(), indent=2, default=str))
    else:
        print(format_flock_dashboard(dashboard))

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
