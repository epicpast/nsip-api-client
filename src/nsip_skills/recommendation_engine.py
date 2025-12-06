"""
Breeding recommendations engine.

AI-powered suggestions for flock improvement based on analysis.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from nsip_skills.common.data_models import (
    PRESET_INDEXES,
    BreedingGoal,
    FlockSummary,
)
from nsip_skills.common.nsip_wrapper import CachedNSIPClient
from nsip_skills.flock_stats import calculate_flock_stats
from nsip_skills.selection_index import rank_by_index


class RecommendationType(Enum):
    """Type of breeding recommendation."""

    RETAIN = "retain"  # Keep this animal for breeding
    CULL = "cull"  # Remove from breeding program
    OUTSIDE_GENETICS = "outside_genetics"  # Consider introducing
    MANAGEMENT = "management"  # Management practice change
    PRIORITY = "priority"  # Prioritize this animal for premium matings


@dataclass
class Recommendation:
    """A single breeding recommendation."""

    type: RecommendationType
    subject: str  # LPN ID or trait name
    rationale: str
    impact: str  # Expected impact
    priority: int = 1  # 1 = highest priority
    action: str = ""  # Specific action to take

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type.value,
            "subject": self.subject,
            "rationale": self.rationale,
            "impact": self.impact,
            "priority": self.priority,
            "action": self.action,
        }


@dataclass
class RecommendationReport:
    """Complete recommendation report for a flock."""

    flock_summary: FlockSummary
    recommendations: list[Recommendation] = field(default_factory=list)
    retain_list: list[str] = field(default_factory=list)
    cull_list: list[str] = field(default_factory=list)
    priority_breeding: list[str] = field(default_factory=list)
    trait_priorities: list[str] = field(default_factory=list)
    breeding_goal: str = "balanced"

    def to_dict(self) -> dict[str, Any]:
        return {
            "flock_summary": self.flock_summary.to_dict(),
            "recommendations": [r.to_dict() for r in self.recommendations],
            "retain_list": self.retain_list,
            "cull_list": self.cull_list,
            "priority_breeding": self.priority_breeding,
            "trait_priorities": self.trait_priorities,
            "breeding_goal": self.breeding_goal,
        }


def _get_index_for_goal(breeding_goal: BreedingGoal) -> Any:
    """Select the appropriate index for the breeding goal."""
    goal_to_index = {
        BreedingGoal.TERMINAL: "terminal",
        BreedingGoal.MATERNAL: "maternal",
    }
    return PRESET_INDEXES.get(goal_to_index.get(breeding_goal, "range"), PRESET_INDEXES["range"])


def _generate_retention_recs(rankings: Any, report: RecommendationReport) -> list[Recommendation]:
    """Generate retention and priority breeding recommendations."""
    recs = []
    n = len(rankings.results)
    top_25_pct = max(1, n // 4)

    for result in rankings.results[:top_25_pct]:
        report.retain_list.append(result.lpn_id)

        if result.rank <= 5:
            report.priority_breeding.append(result.lpn_id)
            recs.append(
                Recommendation(
                    type=RecommendationType.PRIORITY,
                    subject=result.lpn_id,
                    rationale=f"Top performer (Rank {result.rank}, Score {result.total_score:.1f})",
                    impact="Maximize genetic contribution through premium matings",
                    priority=1,
                    action="Assign to top ewes, maximize mating opportunities",
                )
            )
    return recs


def _generate_cull_recs(rankings: Any, report: RecommendationReport) -> list[Recommendation]:
    """Generate culling recommendations for bottom performers."""
    recs: list[Recommendation] = []
    n = len(rankings.results)
    if n <= 10:  # Don't recommend culling if flock is too small
        return recs

    top_25_pct = max(1, n // 4)
    bottom_25_pct = rankings.results[-top_25_pct:]

    for result in bottom_25_pct:
        report.cull_list.append(result.lpn_id)
        recs.append(
            Recommendation(
                type=RecommendationType.CULL,
                subject=result.lpn_id,
                rationale=f"Bottom performer (Rank {result.rank}, Score {result.total_score:.1f})",
                impact="Remove low-performing genetics from breeding pool",
                priority=3,
                action="Remove from breeding program; consider for market",
            )
        )
    return recs


def _generate_trait_recs(
    summary: FlockSummary, report: RecommendationReport
) -> list[Recommendation]:
    """Generate trait improvement recommendations."""
    recs: list[Recommendation] = []
    if not summary.trait_summary:
        return recs

    trait_means = {t: s["mean"] for t, s in summary.trait_summary.items()}
    sorted_traits = sorted(trait_means.items(), key=lambda x: x[1])

    for trait, mean in sorted_traits[:3]:
        if mean < 0:  # Below average
            report.trait_priorities.append(trait)
            recs.append(
                Recommendation(
                    type=RecommendationType.OUTSIDE_GENETICS,
                    subject=trait,
                    rationale=f"Flock average ({mean:.2f}) below breed average",
                    impact=f"Improve {trait} through selection or outside genetics",
                    priority=2,
                    action=f"Search for rams with strong {trait} EBVs",
                )
            )
    return recs


def _generate_management_recs(summary: FlockSummary, philosophy: str) -> list[Recommendation]:
    """Generate management and philosophy-specific recommendations."""
    recs = []

    # Ram ratio check
    if summary.male_count > 0 and summary.female_count > 0:
        ram_ratio = summary.male_count / (summary.male_count + summary.female_count)
        if ram_ratio > 0.15:
            recs.append(
                Recommendation(
                    type=RecommendationType.MANAGEMENT,
                    subject="Ram:Ewe Ratio",
                    rationale=f"High ram percentage ({ram_ratio:.1%})",
                    impact="Reduce costs, focus resources on top rams",
                    priority=2,
                    action="Reduce ram numbers to 1:25-35 ratio with ewes",
                )
            )

    # Philosophy-specific recommendations
    if philosophy == "seedstock":
        recs.append(
            Recommendation(
                type=RecommendationType.MANAGEMENT,
                subject="Data Collection",
                rationale="Seedstock operations benefit from comprehensive data",
                impact="Improve accuracy of EBVs for sale animals",
                priority=2,
                action="Record all birth/weaning weights, submit to NSIP regularly",
            )
        )
    elif philosophy == "commercial":
        recs.append(
            Recommendation(
                type=RecommendationType.MANAGEMENT,
                subject="Ram Purchases",
                rationale="Commercial operations should focus on proven genetics",
                impact="Faster genetic improvement with less risk",
                priority=3,
                action="Purchase rams from NSIP-participating flocks with high accuracy EBVs",
            )
        )

    return recs


def generate_recommendations(
    lpn_ids: list[str],
    breeding_goal: BreedingGoal | str = BreedingGoal.BALANCED,
    philosophy: str = "commercial",
    constraints: dict[str, Any] | None = None,
    client: CachedNSIPClient | None = None,
) -> RecommendationReport:
    """
    Generate breeding recommendations for a flock.

    Args:
        lpn_ids: All animals in the flock
        breeding_goal: Target breeding strategy
        philosophy: "commercial", "seedstock", or "hobbyist"
        constraints: Optional constraints (budget, space, etc.)
        client: Optional pre-configured client

    Returns:
        RecommendationReport with prioritized recommendations
    """
    should_close = client is None
    if client is None:
        client = CachedNSIPClient()

    if isinstance(breeding_goal, str):
        breeding_goal = BreedingGoal(breeding_goal.lower())

    index = _get_index_for_goal(breeding_goal)

    try:
        dashboard = calculate_flock_stats(lpn_ids, client=client)
        summary = dashboard.summary
        rankings = rank_by_index(lpn_ids, index, client=client)

        report = RecommendationReport(
            flock_summary=summary,
            breeding_goal=breeding_goal.value,
        )

        # Collect all recommendations from helper functions
        recs = []
        recs.extend(_generate_retention_recs(rankings, report))
        recs.extend(_generate_cull_recs(rankings, report))
        recs.extend(_generate_trait_recs(summary, report))
        recs.extend(_generate_management_recs(summary, philosophy))

        recs.sort(key=lambda r: r.priority)
        report.recommendations = recs

        return report

    finally:
        if should_close and client:
            client.close()


def format_recommendations(report: RecommendationReport) -> str:
    """Format recommendations as markdown."""
    lines = [
        "## Breeding Recommendations",
        f"*Breeding Goal: {report.breeding_goal.title()}*",
        "",
    ]

    # Summary
    lines.append("### Flock Summary")
    lines.append(f"- Total animals: {report.flock_summary.total_animals}")
    lines.append(f"- Males: {report.flock_summary.male_count}")
    lines.append(f"- Females: {report.flock_summary.female_count}")
    lines.append("")

    # Action lists
    if report.priority_breeding:
        lines.append("### Priority Breeding Stock")
        lines.append("These animals should receive premium mating opportunities:")
        for lpn in report.priority_breeding:
            lines.append(f"- **{lpn}**")
        lines.append("")

    if report.retain_list:
        lines.append(f"### Retain ({len(report.retain_list)} animals)")
        lines.append(
            f"Top performers to keep in breeding program: {', '.join(report.retain_list[:10])}"
        )
        if len(report.retain_list) > 10:
            lines.append(f"  ...and {len(report.retain_list) - 10} more")
        lines.append("")

    if report.cull_list:
        lines.append(f"### Cull Candidates ({len(report.cull_list)} animals)")
        lines.append(f"Bottom performers to remove: {', '.join(report.cull_list[:10])}")
        if len(report.cull_list) > 10:
            lines.append(f"  ...and {len(report.cull_list) - 10} more")
        lines.append("")

    if report.trait_priorities:
        lines.append("### Trait Improvement Priorities")
        for trait in report.trait_priorities:
            lines.append(f"1. **{trait}** - Focus selection pressure here")
        lines.append("")

    # All recommendations
    lines.append("### All Recommendations")
    for rec in report.recommendations[:15]:  # Limit to top 15
        icon = {
            RecommendationType.PRIORITY: "",
            RecommendationType.RETAIN: "",
            RecommendationType.CULL: "",
            RecommendationType.OUTSIDE_GENETICS: "",
            RecommendationType.MANAGEMENT: "",
        }.get(rec.type, "")

        lines.append(f"\n**{icon} {rec.type.value.replace('_', ' ').title()}: {rec.subject}**")
        lines.append(f"- *Rationale*: {rec.rationale}")
        lines.append(f"- *Impact*: {rec.impact}")
        lines.append(f"- *Action*: {rec.action}")

    return "\n".join(lines)


def main():
    """Command-line interface for recommendations."""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Generate breeding recommendations")
    parser.add_argument("lpn_ids", nargs="+", help="Flock LPN IDs")
    parser.add_argument(
        "--goal",
        choices=["terminal", "maternal", "balanced"],
        default="balanced",
        help="Breeding goal",
    )
    parser.add_argument(
        "--philosophy",
        choices=["commercial", "seedstock", "hobbyist"],
        default="commercial",
        help="Operation philosophy",
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    report = generate_recommendations(
        lpn_ids=args.lpn_ids,
        breeding_goal=args.goal,
        philosophy=args.philosophy,
    )

    if args.json:
        print(json.dumps(report.to_dict(), indent=2, default=str))
    else:
        print(format_recommendations(report))

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
