"""
Trait improvement planning module.

Design multi-generation selection strategies to improve flock traits.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass, field
from typing import Any

from nsip_skills.common.formatters import format_markdown_table
from nsip_skills.common.nsip_wrapper import CachedNSIPClient

# Approximate heritabilities for common sheep traits
# These are used for estimating genetic gain
TRAIT_HERITABILITIES = {
    "BWT": 0.30,  # Birth weight
    "WWT": 0.25,  # Weaning weight
    "PWWT": 0.35,  # Post-weaning weight
    "YWT": 0.40,  # Yearling weight
    "YEMD": 0.35,  # Yearling eye muscle depth
    "YFAT": 0.30,  # Yearling fat depth
    "NLB": 0.10,  # Number lambs born
    "NLW": 0.10,  # Number lambs weaned
    "MWWT": 0.15,  # Maternal weaning weight
    "FEC": 0.25,  # Fecal egg count
    "DAG": 0.30,  # Dag score
}

# Generation interval assumptions (years)
DEFAULT_GENERATION_INTERVAL = 3.0


@dataclass
class TraitGoal:
    """A target trait improvement goal."""

    trait: str
    current_mean: float
    target_value: float
    priority: int = 1  # Higher = more important

    @property
    def gap(self) -> float:
        """Difference between target and current."""
        return self.target_value - self.current_mean


@dataclass
class ImprovementProjection:
    """Projected improvement over generations."""

    trait: str
    current: float
    target: float
    heritability: float
    generations_needed: int
    improvement_per_generation: float
    projections: list[float] = field(default_factory=list)  # Value at each generation

    def to_dict(self) -> dict[str, Any]:
        return {
            "trait": self.trait,
            "current": self.current,
            "target": self.target,
            "heritability": self.heritability,
            "generations_needed": self.generations_needed,
            "improvement_per_generation": self.improvement_per_generation,
            "projections": self.projections,
        }


@dataclass
class ImprovementPlan:
    """Complete trait improvement plan."""

    goals: list[TraitGoal] = field(default_factory=list)
    projections: list[ImprovementProjection] = field(default_factory=list)
    selection_recommendations: list[str] = field(default_factory=list)
    generation_interval: float = DEFAULT_GENERATION_INTERVAL
    selection_intensity: float = 1.4  # Assumes top 20% selected

    def to_dict(self) -> dict[str, Any]:
        return {
            "goals": [
                {
                    "trait": g.trait,
                    "current_mean": g.current_mean,
                    "target_value": g.target_value,
                    "gap": g.gap,
                    "priority": g.priority,
                }
                for g in self.goals
            ],
            "projections": [p.to_dict() for p in self.projections],
            "selection_recommendations": self.selection_recommendations,
            "generation_interval": self.generation_interval,
            "selection_intensity": self.selection_intensity,
        }


def calculate_genetic_gain(
    heritability: float,
    selection_intensity: float,
    phenotypic_std: float,
) -> float:
    """
    Calculate expected genetic gain per generation.

    R = h² × i × σ_p

    Where:
    - R = response to selection (genetic gain)
    - h² = heritability
    - i = selection intensity (e.g., 1.4 for top 20%, 1.76 for top 10%)
    - σ_p = phenotypic standard deviation
    """
    return heritability * selection_intensity * phenotypic_std


def estimate_generations_to_goal(
    current: float,
    target: float,
    gain_per_gen: float,
) -> int:
    """Estimate generations needed to reach target."""
    if gain_per_gen == 0:
        return 999  # Infinite

    gap = target - current
    if gap <= 0:
        return 0  # Already at or above target

    return max(1, int(gap / gain_per_gen + 0.5))  # Round to nearest


def analyze_flock_traits(
    lpn_ids: list[str],
    traits: list[str] | None = None,
    client: CachedNSIPClient | None = None,
) -> dict[str, dict[str, float]]:
    """
    Analyze current trait distribution in a flock.

    Returns dict of trait -> {mean, std, min, max}.
    """
    should_close = client is None
    if client is None:
        client = CachedNSIPClient()

    try:
        fetched = client.batch_get_animals(lpn_ids, on_error="skip")

        trait_values: dict[str, list[float]] = {}

        for lpn in lpn_ids:
            data = fetched.get(lpn, {})
            if "details" not in data:
                continue

            for trait_name, trait_obj in data["details"].traits.items():
                if traits and trait_name not in traits:
                    continue
                if trait_name not in trait_values:
                    trait_values[trait_name] = []
                trait_values[trait_name].append(trait_obj.value)

        result = {}
        for trait, values in trait_values.items():
            if values:
                result[trait] = {
                    "mean": statistics.mean(values),
                    "std": statistics.stdev(values) if len(values) > 1 else 0,
                    "min": min(values),
                    "max": max(values),
                    "count": len(values),
                }

        return result

    finally:
        if should_close and client:
            client.close()


def create_improvement_plan(
    lpn_ids: list[str],
    targets: dict[str, float],
    selection_intensity: float = 1.4,
    generation_interval: float = DEFAULT_GENERATION_INTERVAL,
    max_generations: int = 10,
    client: CachedNSIPClient | None = None,
) -> ImprovementPlan:
    """
    Create a trait improvement plan for a flock.

    Args:
        lpn_ids: Current flock LPN IDs
        targets: Dict of trait -> target value
        selection_intensity: Selection intensity (1.4 = top 20%, 1.76 = top 10%)
        generation_interval: Years per generation
        max_generations: Maximum generations to project
        client: Optional pre-configured client

    Returns:
        ImprovementPlan with projections and recommendations
    """
    should_close = client is None
    if client is None:
        client = CachedNSIPClient()

    try:
        # Analyze current flock
        current_stats = analyze_flock_traits(lpn_ids, traits=list(targets.keys()), client=client)

        plan = ImprovementPlan(
            selection_intensity=selection_intensity,
            generation_interval=generation_interval,
        )

        for trait, target in targets.items():
            if trait not in current_stats:
                continue

            stats = current_stats[trait]
            current = stats["mean"]
            std = stats["std"]

            # Get heritability (use default if unknown)
            h2 = TRAIT_HERITABILITIES.get(trait, 0.25)

            # Calculate gain per generation
            gain = calculate_genetic_gain(h2, selection_intensity, std)

            # Create goal
            goal = TraitGoal(
                trait=trait,
                current_mean=current,
                target_value=target,
            )
            plan.goals.append(goal)

            # Calculate generations needed
            gens_needed = estimate_generations_to_goal(current, target, gain)

            # Project improvements
            projections = [current]
            value = current
            for _ in range(min(gens_needed, max_generations)):
                value += gain
                projections.append(value)

            plan.projections.append(
                ImprovementProjection(
                    trait=trait,
                    current=current,
                    target=target,
                    heritability=h2,
                    generations_needed=gens_needed,
                    improvement_per_generation=gain,
                    projections=projections,
                )
            )

        # Generate recommendations
        plan.selection_recommendations = _generate_recommendations(plan)

        return plan

    finally:
        if should_close and client:
            client.close()


def _generate_recommendations(plan: ImprovementPlan) -> list[str]:
    """Generate selection recommendations based on the plan."""
    recs = []

    # Find traits needing most generations
    sorted_projections = sorted(plan.projections, key=lambda p: p.generations_needed, reverse=True)

    if sorted_projections:
        hardest = sorted_projections[0]
        recs.append(
            f"**{hardest.trait}** requires most attention "
            f"({hardest.generations_needed} generations). "
            f"Consider introducing outside genetics with strong "
            f"{hardest.trait} performance."
        )

    # Find traits with low heritability
    low_h2 = [p for p in plan.projections if p.heritability < 0.2]
    if low_h2:
        trait_names = ", ".join(p.trait for p in low_h2)
        recs.append(
            f"Traits with low heritability ({trait_names}) respond slowly to selection. "
            f"Focus on management practices alongside genetic selection."
        )

    # Check for achievable quick wins
    quick_wins = [p for p in plan.projections if p.generations_needed <= 2]
    if quick_wins:
        trait_names = ", ".join(p.trait for p in quick_wins)
        recs.append(f"Quick wins achievable in 2 generations: {trait_names}")

    # Selection intensity advice
    if plan.selection_intensity < 1.5:
        recs.append(
            "Consider stricter selection (top 10% vs top 20%) to accelerate improvement, "
            "but balance against inbreeding risk."
        )

    return recs


def format_improvement_plan(plan: ImprovementPlan) -> str:
    """Format improvement plan as markdown."""
    lines = ["## Trait Improvement Plan", ""]

    # Goals summary
    lines.append("### Goals")
    headers = ["Trait", "Current", "Target", "Gap"]
    rows = []
    for goal in plan.goals:
        rows.append(
            [
                goal.trait,
                f"{goal.current_mean:.3f}",
                f"{goal.target_value:.3f}",
                f"{goal.gap:+.3f}",
            ]
        )
    lines.append(format_markdown_table(headers, rows))
    lines.append("")

    # Projections
    lines.append("### Projections")
    for proj in plan.projections:
        lines.append(f"**{proj.trait}**")
        lines.append(f"- Heritability: {proj.heritability:.2f}")
        lines.append(f"- Gain/generation: {proj.improvement_per_generation:+.4f}")
        lines.append(f"- Generations to target: {proj.generations_needed}")

        if proj.projections:
            gen_values = " → ".join(f"Gen{i}: {v:.3f}" for i, v in enumerate(proj.projections[:5]))
            lines.append(f"- Trajectory: {gen_values}")
        lines.append("")

    # Assumptions
    lines.append("### Assumptions")
    lines.append(
        f"- Selection intensity: {plan.selection_intensity:.2f} "
        f"(top {_intensity_to_pct(plan.selection_intensity)})"
    )
    lines.append(f"- Generation interval: {plan.generation_interval:.1f} years")
    lines.append("")

    # Recommendations
    if plan.selection_recommendations:
        lines.append("### Recommendations")
        for rec in plan.selection_recommendations:
            lines.append(f"- {rec}")

    return "\n".join(lines)


def _intensity_to_pct(i: float) -> str:
    """Convert selection intensity to approximate percentage."""
    if i >= 2.0:
        return "~5%"
    elif i >= 1.76:
        return "~10%"
    elif i >= 1.4:
        return "~20%"
    elif i >= 1.16:
        return "~30%"
    else:
        return "~50%"


def main():
    """Command-line interface for trait planning."""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Create trait improvement plan")
    parser.add_argument("lpn_ids", nargs="+", help="Flock LPN IDs")
    parser.add_argument("--targets", required=True, help="JSON dict of trait targets")
    parser.add_argument("--intensity", type=float, default=1.4, help="Selection intensity")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    targets = json.loads(args.targets)

    plan = create_improvement_plan(
        lpn_ids=args.lpn_ids,
        targets=targets,
        selection_intensity=args.intensity,
    )

    if args.json:
        print(json.dumps(plan.to_dict(), indent=2, default=str))
    else:
        print(format_improvement_plan(plan))

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
