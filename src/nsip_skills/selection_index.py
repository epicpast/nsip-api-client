"""
Selection index calculation module.

Build and apply custom breeding indexes to rank animals.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass, field
from typing import Any

from nsip_skills.common.data_models import (
    PRESET_INDEXES,
    SelectionIndex,
)
from nsip_skills.common.formatters import format_markdown_table
from nsip_skills.common.nsip_wrapper import CachedNSIPClient


@dataclass
class IndexResult:
    """Result of applying a selection index to an animal."""

    lpn_id: str
    index_name: str
    total_score: float
    trait_contributions: dict[str, float] = field(default_factory=dict)  # trait -> contribution
    rank: int = 0
    percentile: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "lpn_id": self.lpn_id,
            "index_name": self.index_name,
            "total_score": self.total_score,
            "trait_contributions": self.trait_contributions,
            "rank": self.rank,
            "percentile": self.percentile,
        }


@dataclass
class IndexRankings:
    """Rankings of animals by selection index."""

    index: SelectionIndex
    results: list[IndexResult] = field(default_factory=list)
    mean_score: float = 0.0
    std_score: float = 0.0
    selection_threshold_10: float = 0.0  # Score for top 10%
    selection_threshold_25: float = 0.0  # Score for top 25%

    def to_dict(self) -> dict[str, Any]:
        return {
            "index": self.index.to_dict(),
            "results": [r.to_dict() for r in self.results],
            "mean_score": self.mean_score,
            "std_score": self.std_score,
            "selection_threshold_10": self.selection_threshold_10,
            "selection_threshold_25": self.selection_threshold_25,
        }


def get_preset_index(name: str) -> SelectionIndex:
    """
    Get a preset selection index by name.

    Available presets: terminal, maternal, range, hair
    """
    key = name.lower().replace(" ", "_").replace("index", "").strip("_")
    if key in PRESET_INDEXES:
        return PRESET_INDEXES[key]
    raise ValueError(f"Unknown preset index: {name}. Available: {list(PRESET_INDEXES.keys())}")


def create_custom_index(
    name: str,
    trait_weights: dict[str, float],
    description: str | None = None,
) -> SelectionIndex:
    """
    Create a custom selection index.

    Args:
        name: Name for the index
        trait_weights: Dict of trait -> weight
        description: Optional description

    Returns:
        SelectionIndex for use in scoring

    Example:
        my_index = create_custom_index(
            "My Commercial Index",
            {"WWT": 1.5, "PWWT": 1.0, "NLW": 2.0, "BWT": -0.5}
        )
    """
    return SelectionIndex(
        name=name,
        description=description,
        trait_weights=trait_weights,
        is_preset=False,
    )


def calculate_index_score(
    lpn_id: str,
    index: SelectionIndex,
    client: CachedNSIPClient | None = None,
) -> IndexResult:
    """
    Calculate selection index score for a single animal.

    Args:
        lpn_id: Animal's LPN ID
        index: Selection index to apply
        client: Optional pre-configured client

    Returns:
        IndexResult with score and trait breakdown
    """
    should_close = client is None
    if client is None:
        client = CachedNSIPClient()

    try:
        details = client.get_animal_details(lpn_id)

        ebvs = {name: trait.value for name, trait in details.traits.items()}

        # Calculate contributions from each trait
        contributions = {}
        total = 0.0

        for trait, weight in index.trait_weights.items():
            if trait in ebvs:
                contribution = weight * ebvs[trait]
                contributions[trait] = contribution
                total += contribution

        return IndexResult(
            lpn_id=lpn_id,
            index_name=index.name,
            total_score=total,
            trait_contributions=contributions,
        )

    finally:
        if should_close and client:
            client.close()


def rank_by_index(
    lpn_ids: list[str],
    index: SelectionIndex | str,
    client: CachedNSIPClient | None = None,
) -> IndexRankings:
    """
    Rank multiple animals by a selection index.

    Args:
        lpn_ids: List of animal LPN IDs
        index: SelectionIndex or preset name
        client: Optional pre-configured client

    Returns:
        IndexRankings with sorted results and statistics
    """
    should_close = client is None
    if client is None:
        client = CachedNSIPClient()

    # Resolve index
    if isinstance(index, str):
        index = get_preset_index(index)

    try:
        # Fetch all animals
        fetched = client.batch_get_animals(lpn_ids, on_error="skip")

        results: list[IndexResult] = []

        for lpn_id in lpn_ids:
            data = fetched.get(lpn_id, {})
            if "error" in data or "details" not in data:
                continue

            details = data["details"]
            ebvs = {name: trait.value for name, trait in details.traits.items()}

            contributions = {}
            total = 0.0

            for trait, weight in index.trait_weights.items():
                if trait in ebvs:
                    contribution = weight * ebvs[trait]
                    contributions[trait] = contribution
                    total += contribution

            results.append(
                IndexResult(
                    lpn_id=lpn_id,
                    index_name=index.name,
                    total_score=total,
                    trait_contributions=contributions,
                )
            )

        # Sort by score (highest first)
        results.sort(key=lambda r: r.total_score, reverse=True)

        # Assign ranks and percentiles
        n = len(results)
        for i, result in enumerate(results):
            result.rank = i + 1
            result.percentile = ((n - i) / n) * 100 if n > 0 else 0

        # Calculate statistics
        scores = [r.total_score for r in results]
        rankings = IndexRankings(index=index, results=results)

        if scores:
            rankings.mean_score = statistics.mean(scores)
            rankings.std_score = statistics.stdev(scores) if len(scores) > 1 else 0

            # Selection thresholds
            n = len(scores)
            if n >= 10:
                rankings.selection_threshold_10 = scores[n // 10]
            if n >= 4:
                rankings.selection_threshold_25 = scores[n // 4]

        return rankings

    finally:
        if should_close and client:
            client.close()


def format_index_rankings(rankings: IndexRankings, top_n: int = 20) -> str:
    """Format index rankings as markdown."""
    lines = [
        f"## {rankings.index.name} Rankings",
        "",
    ]

    if rankings.index.description:
        lines.append(f"*{rankings.index.description}*")
        lines.append("")

    # Statistics
    lines.append("### Summary Statistics")
    lines.append(f"- Animals ranked: {len(rankings.results)}")
    lines.append(f"- Mean score: {rankings.mean_score:.2f}")
    lines.append(f"- Std deviation: {rankings.std_score:.2f}")
    if rankings.selection_threshold_10 > 0:
        lines.append(f"- Top 10% threshold: {rankings.selection_threshold_10:.2f}")
    if rankings.selection_threshold_25 > 0:
        lines.append(f"- Top 25% threshold: {rankings.selection_threshold_25:.2f}")
    lines.append("")

    # Trait weights
    lines.append("### Index Weights")
    for trait, weight in sorted(rankings.index.trait_weights.items()):
        sign = "+" if weight >= 0 else ""
        lines.append(f"- {trait}: {sign}{weight}")
    lines.append("")

    # Rankings table
    lines.append("### Rankings")
    results = rankings.results[:top_n]

    if results:
        # Get all traits used
        traits = list(rankings.index.trait_weights.keys())

        headers = ["Rank", "LPN ID", "Score"] + traits
        rows = []

        for r in results:
            row = [r.rank, r.lpn_id, f"{r.total_score:.2f}"]
            for trait in traits:
                contrib = r.trait_contributions.get(trait)
                row.append(f"{contrib:.2f}" if contrib is not None else "-")
            rows.append(row)

        lines.append(format_markdown_table(headers, rows))

    return "\n".join(lines)


def list_preset_indexes() -> list[dict[str, Any]]:
    """List all available preset indexes."""
    return [
        {
            "name": idx.name,
            "key": key,
            "description": idx.description,
            "traits": list(idx.trait_weights.keys()),
        }
        for key, idx in PRESET_INDEXES.items()
    ]


def main():
    """Command-line interface for selection indexes."""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Calculate selection index rankings")
    parser.add_argument("lpn_ids", nargs="+", help="Animal LPN IDs")
    parser.add_argument(
        "--index",
        default="range",
        help="Index name: terminal, maternal, range, hair, or 'custom:JSON'",
    )
    parser.add_argument("--top", type=int, default=20, help="Show top N animals")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--list-presets", action="store_true", help="List preset indexes")

    args = parser.parse_args()

    if args.list_presets:
        presets = list_preset_indexes()
        if args.json:
            print(json.dumps(presets, indent=2))
        else:
            print("Available Preset Indexes:")
            for p in presets:
                print(f"\n{p['name']} ({p['key']})")
                print(f"  {p['description']}")
                print(f"  Traits: {', '.join(p['traits'])}")
        return 0

    # Parse index
    if args.index.startswith("custom:"):
        weights = json.loads(args.index[7:])
        index = create_custom_index("Custom Index", weights)
    else:
        index = args.index

    rankings = rank_by_index(args.lpn_ids, index)

    if args.json:
        print(json.dumps(rankings.to_dict(), indent=2, default=str))
    else:
        print(format_index_rankings(rankings, top_n=args.top))

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
