"""
Mating plan optimization module.

Recommend optimal ram-ewe pairings based on EBVs, inbreeding constraints,
and breeding goals.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from nsip_skills.common.data_models import (
    PRESET_INDEXES,
    BreedingGoal,
    MatingPair,
    RiskLevel,
    SelectionIndex,
)
from nsip_skills.common.formatters import format_mating_recommendations
from nsip_skills.common.nsip_wrapper import CachedNSIPClient
from nsip_skills.inbreeding import calculate_projected_offspring_inbreeding

logger = logging.getLogger(__name__)


@dataclass
class MatingPlanResult:
    """Result of mating plan optimization."""

    pairs: list[MatingPair] = field(default_factory=list)
    unassigned_ewes: list[str] = field(default_factory=list)
    high_risk_pairs: list[MatingPair] = field(default_factory=list)  # COI > threshold
    breeding_goal: str = "balanced"
    max_inbreeding: float = 0.0625  # 6.25% default threshold

    def to_dict(self) -> dict[str, Any]:
        return {
            "pairs": [p.to_dict() for p in self.pairs],
            "unassigned_ewes": self.unassigned_ewes,
            "high_risk_pairs": [p.to_dict() for p in self.high_risk_pairs],
            "breeding_goal": self.breeding_goal,
            "max_inbreeding": self.max_inbreeding,
        }


def project_offspring_ebvs(
    ram_ebvs: dict[str, float],
    ewe_ebvs: dict[str, float],
) -> dict[str, float]:
    """
    Project offspring EBVs using midparent method.

    Offspring EBV = (Sire EBV + Dam EBV) / 2
    """
    all_traits = set(ram_ebvs.keys()) | set(ewe_ebvs.keys())
    projected = {}

    for trait in all_traits:
        ram_val = ram_ebvs.get(trait, 0)
        ewe_val = ewe_ebvs.get(trait, 0)
        # Only project if at least one parent has the trait
        if trait in ram_ebvs or trait in ewe_ebvs:
            projected[trait] = (ram_val + ewe_val) / 2

    return projected


def score_mating(
    projected_ebvs: dict[str, float],
    index: SelectionIndex,
    inbreeding_coefficient: float,
    inbreeding_penalty: float = 10.0,
) -> float:
    """
    Calculate composite score for a mating.

    Higher scores are better. Inbreeding is penalized.
    """
    # Base score from selection index
    base_score = index.calculate_score(projected_ebvs)

    # Penalize inbreeding (subtract penalty * coefficient * 100)
    inbreeding_cost = inbreeding_penalty * inbreeding_coefficient * 100

    return base_score - inbreeding_cost


def _get_breeding_index(
    breeding_goal: BreedingGoal, custom_index: SelectionIndex | None
) -> SelectionIndex:
    """Get the appropriate selection index for the breeding goal."""
    if custom_index:
        return custom_index
    goal_to_index = {
        BreedingGoal.TERMINAL: "terminal",
        BreedingGoal.MATERNAL: "maternal",
    }
    return PRESET_INDEXES.get(goal_to_index.get(breeding_goal, "range"), PRESET_INDEXES["range"])


def _extract_ebvs(
    lpns: list[str], fetched: dict[str, dict[str, Any]]
) -> dict[str, dict[str, float]]:
    """Extract EBV dictionaries from fetched animal data."""
    ebvs: dict[str, dict[str, float]] = {}
    for lpn in lpns:
        data = fetched.get(lpn, {})
        if "details" in data and data["details"].traits:
            ebvs[lpn] = {name: trait.value for name, trait in data["details"].traits.items()}
    return ebvs


def _score_pairing(
    ram: str,
    ewe: str,
    ram_ebvs: dict[str, float],
    ewe_ebvs: dict[str, float],
    index: SelectionIndex,
    inbreeding_generations: int,
    client: CachedNSIPClient,
    lineage_cache: dict[str, Any] | None = None,
) -> MatingPair:
    """Score a single ram-ewe pairing.

    Args:
        ram: Ram LPN ID
        ewe: Ewe LPN ID
        ram_ebvs: Ram's EBV dictionary
        ewe_ebvs: Ewe's EBV dictionary
        index: Selection index for scoring
        inbreeding_generations: Generations for inbreeding calc
        client: NSIP client
        lineage_cache: Optional pre-fetched lineage data to avoid N+1 queries
    """
    projected = project_offspring_ebvs(ram_ebvs, ewe_ebvs)
    pair_notes: list[str] = []

    try:
        # Use cached lineage if available (avoids N+1 query pattern)
        inbreeding_result = calculate_projected_offspring_inbreeding(
            sire_lpn=ram,
            dam_lpn=ewe,
            generations=inbreeding_generations,
            client=client,
            lineage_cache=lineage_cache,
        )
        coi = inbreeding_result.coefficient
        risk = inbreeding_result.risk_level or RiskLevel.LOW
    except Exception as e:
        # Log warning for silent failures (HIGH priority fix)
        logger.warning(f"Inbreeding calculation failed for {ram}x{ewe}: {e}")
        coi = 0.0
        risk = RiskLevel.LOW
        pair_notes.append(f"Inbreeding could not be calculated: {e}")

    composite = score_mating(projected, index, coi)

    pair = MatingPair(
        ram_lpn=ram,
        ewe_lpn=ewe,
        projected_offspring_ebvs=projected,
        projected_inbreeding=coi,
        inbreeding_risk=risk,
        composite_score=composite,
    )
    pair.notes.extend(pair_notes)
    return pair


def optimize_mating_plan(
    ram_lpns: list[str],
    ewe_lpns: list[str],
    breeding_goal: BreedingGoal | str = BreedingGoal.BALANCED,
    custom_index: SelectionIndex | None = None,
    max_inbreeding: float = 0.0625,
    max_ewes_per_ram: int | None = None,
    inbreeding_generations: int = 3,
    client: CachedNSIPClient | None = None,
) -> MatingPlanResult:
    """
    Optimize ram-ewe pairings for a breeding season.

    Args:
        ram_lpns: Available ram LPN IDs
        ewe_lpns: Ewes to mate
        breeding_goal: Target breeding strategy or BreedingGoal enum
        custom_index: Custom selection index (overrides breeding_goal)
        max_inbreeding: Maximum acceptable inbreeding coefficient (default: 6.25%)
        max_ewes_per_ram: Limit ewes per ram (None = no limit)
        inbreeding_generations: Generations for inbreeding calc (default: 3)
        client: Optional pre-configured client

    Returns:
        MatingPlanResult with optimal pairings
    """
    should_close = client is None
    if client is None:
        client = CachedNSIPClient()

    if isinstance(breeding_goal, str):
        breeding_goal = BreedingGoal(breeding_goal.lower())

    index = _get_breeding_index(breeding_goal, custom_index)
    result = MatingPlanResult(breeding_goal=breeding_goal.value, max_inbreeding=max_inbreeding)

    try:
        fetched = client.batch_get_animals(ram_lpns + ewe_lpns, on_error="skip")
        ram_ebvs = _extract_ebvs(ram_lpns, fetched)
        ewe_ebvs = _extract_ebvs(ewe_lpns, fetched)

        # Pre-fetch lineage for all animals to avoid N+1 query pattern
        # With R rams and E ewes, this reduces API calls from O(R*E*2) to O(R+E)
        all_lpns = set(ram_ebvs.keys()) | set(ewe_ebvs.keys())
        lineage_cache: dict[str, Any] = {}
        for lpn in all_lpns:
            try:
                lineage_cache[lpn] = client.get_lineage(lpn)
            except Exception as e:
                logger.debug(f"Could not fetch lineage for {lpn}: {e}")
                lineage_cache[lpn] = None

        # Score all possible pairings
        all_pairs: list[MatingPair] = []
        for ram in ram_ebvs:
            for ewe in ewe_ebvs:
                pair = _score_pairing(
                    ram,
                    ewe,
                    ram_ebvs[ram],
                    ewe_ebvs[ewe],
                    index,
                    inbreeding_generations,
                    client,
                    lineage_cache,
                )
                if pair.projected_inbreeding > max_inbreeding:
                    pair.notes.append(
                        f"High inbreeding risk: {pair.projected_inbreeding * 100:.1f}%"
                    )
                    result.high_risk_pairs.append(pair)
                all_pairs.append(pair)

        # Greedy assignment by score
        all_pairs.sort(key=lambda p: p.composite_score, reverse=True)
        assigned_ewes: set[str] = set()
        ram_assignments: dict[str, int] = {ram: 0 for ram in ram_ebvs}

        for pair in all_pairs:
            if pair.ewe_lpn in assigned_ewes:
                continue
            if pair.projected_inbreeding > max_inbreeding:
                continue
            if max_ewes_per_ram and ram_assignments[pair.ram_lpn] >= max_ewes_per_ram:
                continue
            pair.rank = len(result.pairs) + 1
            result.pairs.append(pair)
            assigned_ewes.add(pair.ewe_lpn)
            ram_assignments[pair.ram_lpn] += 1

        result.unassigned_ewes = [e for e in ewe_lpns if e not in assigned_ewes]
        return result

    finally:
        if should_close and client:
            client.close()


def main():
    """Command-line interface for mating optimization."""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Optimize mating plan")
    parser.add_argument("--rams", required=True, nargs="+", help="Ram LPN IDs")
    parser.add_argument("--ewes", required=True, nargs="+", help="Ewe LPN IDs")
    parser.add_argument(
        "--goal",
        choices=["terminal", "maternal", "balanced"],
        default="balanced",
        help="Breeding goal",
    )
    parser.add_argument("--max-inbreeding", type=float, default=6.25, help="Max inbreeding percent")
    parser.add_argument("--max-per-ram", type=int, help="Max ewes per ram")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    result = optimize_mating_plan(
        ram_lpns=args.rams,
        ewe_lpns=args.ewes,
        breeding_goal=args.goal,
        max_inbreeding=args.max_inbreeding / 100,
        max_ewes_per_ram=args.max_per_ram,
    )

    if args.json:
        print(json.dumps(result.to_dict(), indent=2, default=str))
    else:
        print(format_mating_recommendations(result.pairs))
        if result.unassigned_ewes:
            print(f"\nUnassigned ewes: {', '.join(result.unassigned_ewes)}")
        if result.high_risk_pairs:
            print(f"\nHigh inbreeding risk pairs: {len(result.high_risk_pairs)}")

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
