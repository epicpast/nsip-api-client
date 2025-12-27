"""
Output formatting utilities for NSIP skills.

Provides functions to format analysis results as markdown tables,
ASCII pedigree trees, and other human-readable formats.
"""

from __future__ import annotations

from typing import Any

from nsip_skills.common.data_models import (
    AnimalAnalysis,
    FlockSummary,
    InbreedingResult,
    MatingPair,
    PedigreeNode,
    PedigreeTree,
    ProgenyStats,
    TraitProfile,
)


def format_markdown_table(
    headers: list[str],
    rows: list[list[Any]],
    alignment: list[str] | None = None,
) -> str:
    """
    Format data as a markdown table.

    Args:
        headers: Column header names
        rows: List of row data (each row is a list of values)
        alignment: List of 'l', 'c', or 'r' for left/center/right alignment

    Returns:
        Markdown table string
    """
    if not headers:
        return ""

    # Calculate column widths
    widths = [len(str(h)) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            if i < len(widths):
                widths[i] = max(widths[i], len(str(val)))

    # Default alignment
    if alignment is None:
        alignment = ["l"] * len(headers)

    # Build header row
    header_cells = [str(h).ljust(widths[i]) for i, h in enumerate(headers)]
    header_line = "| " + " | ".join(header_cells) + " |"

    # Build separator row with alignment
    sep_cells = []
    for i, a in enumerate(alignment):
        w = widths[i] if i < len(widths) else 3
        if a == "c":
            sep_cells.append(":" + "-" * (w - 2) + ":" if w > 2 else ":-:")
        elif a == "r":
            sep_cells.append("-" * (w - 1) + ":")
        else:
            sep_cells.append("-" * w)
    sep_line = "| " + " | ".join(sep_cells) + " |"

    # Build data rows
    data_lines = []
    for row in rows:
        cells = []
        for i, val in enumerate(row):
            w = widths[i] if i < len(widths) else 0
            cells.append(str(val).ljust(w))
        data_lines.append("| " + " | ".join(cells) + " |")

    return "\n".join([header_line, sep_line] + data_lines)


def format_trait_comparison(
    profiles: list[TraitProfile],
    traits: list[str] | None = None,
    include_percentiles: bool = True,
) -> str:
    """
    Format trait comparison across multiple animals.

    Args:
        profiles: List of TraitProfile objects
        traits: Specific traits to include (None = all available)
        include_percentiles: Show percentile ranks if available

    Returns:
        Markdown table comparing traits
    """
    if not profiles:
        return "No animals to compare."

    # Determine traits to show
    if traits is None:
        all_traits: set[str] = set()
        for p in profiles:
            all_traits.update(p.traits.keys())
        traits = sorted(all_traits)

    if not traits:
        return "No trait data available."

    # Build headers and rows
    headers = ["Animal"] + traits
    rows = []

    for profile in profiles:
        row: list[Any] = [profile.lpn_id]
        for trait in traits:
            tv = profile.traits.get(trait)
            if tv is None:
                row.append("-")
            elif include_percentiles and tv.percentile is not None:
                row.append(f"{tv.value:.2f} ({tv.percentile:.0f}%)")
            else:
                row.append(f"{tv.value:.2f}")
        rows.append(row)

    return format_markdown_table(headers, rows)


def format_pedigree_tree(tree: PedigreeTree, style: str = "ascii") -> str:
    """
    Format a pedigree tree for display.

    Args:
        tree: PedigreeTree object
        style: "ascii" for text tree, "markdown" for nested list

    Returns:
        Formatted pedigree string
    """
    if style == "markdown":
        return _format_pedigree_markdown(tree)
    return _format_pedigree_ascii(tree)


def _format_node(node: PedigreeNode | None, include_details: bool = True) -> str:
    """Format a single pedigree node."""
    if node is None:
        return "[Unknown]"

    parts = [node.lpn_id]
    if include_details:
        if node.gender:
            parts.append(f"({node.gender[0]})")
        if node.date_of_birth:
            parts.append(f"b.{node.date_of_birth[:4]}")
        if node.farm_name:
            parts.append(f"- {node.farm_name}")
    return " ".join(parts)


def _format_node_short(node: PedigreeNode | None, max_len: int = 20) -> str:
    """Format a pedigree node in short form for tree display."""
    if node is None:
        return "[Unknown]"

    # Use last 6 chars of LPN for brevity
    short_id = node.lpn_id[-10:] if len(node.lpn_id) > 10 else node.lpn_id
    parts = [short_id]
    if node.gender:
        parts.append(f"({node.gender[0]})")
    result = " ".join(parts)
    if len(result) > max_len:
        return result[: max_len - 2] + ".."
    return result


def _format_pedigree_ascii(tree: PedigreeTree) -> str:
    """Format pedigree as ASCII art tree with visual branches."""
    lines = []

    # Get short node representations
    subj = _format_node_short(tree.subject)
    sire = _format_node_short(tree.sire)
    dam = _format_node_short(tree.dam)
    ss = _format_node_short(tree.sire_sire)
    sd = _format_node_short(tree.sire_dam)
    ds = _format_node_short(tree.dam_sire)
    dd = _format_node_short(tree.dam_dam)

    # Build the visual tree
    # Row 1: Subject centered
    lines.append("```")
    lines.append(f"                         {subj}")
    lines.append("                        /              \\")

    # Row 2: Parents
    lines.append(f"              {sire:<18}    {dam}")
    lines.append("              /         \\          /         \\")

    # Row 3: Grandparents
    lines.append(f"       {ss:<12} {sd:<12} {ds:<12} {dd}")
    lines.append("```")
    lines.append("")

    # Detailed list below the tree
    lines.append("**Subject**: " + _format_node(tree.subject))
    lines.append("")
    lines.append("**Parents**:")
    lines.append(f"  • Sire: {_format_node(tree.sire)}")
    lines.append(f"  • Dam:  {_format_node(tree.dam)}")
    lines.append("")
    lines.append("**Grandparents**:")
    lines.append(f"  • Sire's Sire: {_format_node(tree.sire_sire)}")
    lines.append(f"  • Sire's Dam:  {_format_node(tree.sire_dam)}")
    lines.append(f"  • Dam's Sire:  {_format_node(tree.dam_sire)}")
    lines.append(f"  • Dam's Dam:   {_format_node(tree.dam_dam)}")

    # Extended generations if available
    if tree.extended:
        lines.append("")
        lines.append("**Great-grandparents**:")
        for path, node in sorted(tree.extended.items()):
            if len(path) == 3:
                label = path.replace("s", "Sire's ").replace("d", "Dam's ").strip("' ")
                lines.append(f"  • {label}: {_format_node(node)}")

    # Common ancestors
    if tree.common_ancestors:
        lines.append("")
        lines.append(f"**Common Ancestors**: {', '.join(tree.common_ancestors)}")

    return "\n".join(lines)


def _format_pedigree_markdown(tree: PedigreeTree) -> str:
    """Format pedigree as markdown nested list."""
    lines = []

    lines.append(f"### Pedigree: {_format_node(tree.subject)}")
    lines.append("")
    lines.append(f"- **Sire**: {_format_node(tree.sire)}")
    if tree.sire_sire or tree.sire_dam:
        lines.append(f"  - Sire's Sire: {_format_node(tree.sire_sire)}")
        lines.append(f"  - Sire's Dam: {_format_node(tree.sire_dam)}")

    lines.append(f"- **Dam**: {_format_node(tree.dam)}")
    if tree.dam_sire or tree.dam_dam:
        lines.append(f"  - Dam's Sire: {_format_node(tree.dam_sire)}")
        lines.append(f"  - Dam's Dam: {_format_node(tree.dam_dam)}")

    if tree.common_ancestors:
        lines.append("")
        lines.append(f"**Common Ancestors**: {', '.join(tree.common_ancestors)}")

    return "\n".join(lines)


def format_inbreeding_result(result: InbreedingResult) -> str:
    """Format inbreeding calculation result."""
    risk_value = result.risk_level.value.upper() if result.risk_level else "UNKNOWN"

    lines = [
        f"## Inbreeding Analysis: {result.lpn_id}",
        "",
        f"**Coefficient**: {result.percentage:.2f}%",
        f"**Risk Level**: {risk_value}",
        f"**Generations Analyzed**: {result.generations_analyzed}",
    ]

    if result.common_ancestors:
        lines.append("")
        lines.append("### Common Ancestors")
        for ancestor in result.common_ancestors:
            # Handle both string LPN IDs and dict formats
            if isinstance(ancestor, str):
                lines.append(f"- {ancestor}")
            else:
                lines.append(
                    f"- {ancestor.get('lpn_id', 'Unknown')}: "
                    f"{ancestor.get('contribution', 0):.1f}% contribution"
                )

    if result.pedigree:
        lines.append("")
        lines.append("### Pedigree")
        tree = result.pedigree
        if tree.sire:
            lines.append(f"- Sire: {tree.sire.lpn_id}")
        if tree.dam:
            lines.append(f"- Dam: {tree.dam.lpn_id}")
        if tree.sire_sire:
            lines.append(f"- Sire's Sire: {tree.sire_sire.lpn_id}")
        if tree.sire_dam:
            lines.append(f"- Sire's Dam: {tree.sire_dam.lpn_id}")
        if tree.dam_sire:
            lines.append(f"- Dam's Sire: {tree.dam_sire.lpn_id}")
        if tree.dam_dam:
            lines.append(f"- Dam's Dam: {tree.dam_dam.lpn_id}")

    return "\n".join(lines)


def format_mating_recommendations(pairs: list[MatingPair], top_n: int = 10) -> str:
    """Format mating pair recommendations as markdown."""
    if not pairs:
        return "No mating recommendations available."

    lines = ["## Recommended Matings", ""]

    # Sort by composite score
    sorted_pairs = sorted(pairs, key=lambda p: p.composite_score, reverse=True)[:top_n]

    headers = ["Rank", "Ram", "Ewe", "Score", "Inbreeding", "Risk"]
    rows = []

    for i, pair in enumerate(sorted_pairs, 1):
        rows.append(
            [
                i,
                pair.ram_lpn,
                pair.ewe_lpn,
                f"{pair.composite_score:.1f}",
                f"{pair.projected_inbreeding * 100:.1f}%",
                pair.inbreeding_risk.value,
            ]
        )

    lines.append(format_markdown_table(headers, rows))

    return "\n".join(lines)


def format_progeny_stats(stats: ProgenyStats) -> str:
    """Format progeny statistics as markdown."""
    lines = [
        f"## Progeny Analysis: {stats.parent_lpn}",
        "",
        f"**Parent Gender**: {stats.parent_gender}",
        f"**Total Progeny**: {stats.total_progeny}",
        f"**Males**: {stats.male_count} | **Females**: {stats.female_count}",
        "",
    ]

    if stats.trait_means:
        lines.append("### Trait Averages")
        headers = ["Trait", "Mean", "Std Dev"]
        rows = []
        for trait in sorted(stats.trait_means.keys()):
            mean = stats.trait_means[trait]
            std = stats.trait_std_devs.get(trait, 0)
            rows.append([trait, f"{mean:.3f}", f"{std:.3f}"])
        lines.append(format_markdown_table(headers, rows))

    if stats.top_performers:
        lines.append("")
        lines.append(f"**Top Performers**: {', '.join(stats.top_performers[:5])}")

    return "\n".join(lines)


def format_flock_summary(summary: FlockSummary) -> str:
    """Format flock summary as markdown dashboard."""
    lines = [
        "## Flock Dashboard",
        "",
    ]

    if summary.flock_name:
        lines.append(f"**Flock**: {summary.flock_name}")

    lines.extend(
        [
            f"**Total Animals**: {summary.total_animals}",
            f"**Males**: {summary.male_count} | **Females**: {summary.female_count}",
            "",
        ]
    )

    # Status breakdown
    if summary.status_breakdown:
        lines.append("### Status Distribution")
        for status, count in sorted(summary.status_breakdown.items()):
            lines.append(f"- {status}: {count}")
        lines.append("")

    # Trait summary
    if summary.trait_summary:
        lines.append("### Trait Summary")
        headers = ["Trait", "Mean", "Median", "Min", "Max"]
        rows = []
        for trait, stats in sorted(summary.trait_summary.items()):
            rows.append(
                [
                    trait,
                    f"{stats.get('mean', 0):.3f}",
                    f"{stats.get('median', 0):.3f}",
                    f"{stats.get('min', 0):.3f}",
                    f"{stats.get('max', 0):.3f}",
                ]
            )
        lines.append(format_markdown_table(headers, rows))
        lines.append("")

    # Recommendations
    if summary.recommendations:
        lines.append("### Recommendations")
        for rec in summary.recommendations:
            lines.append(f"- {rec}")

    return "\n".join(lines)


def format_animal_card(analysis: AnimalAnalysis) -> str:
    """Format a single animal's analysis as a compact card."""
    lines = [
        f"### {analysis.lpn_id}",
    ]

    if analysis.breed:
        lines.append(f"**Breed**: {analysis.breed}")

    details = []
    if analysis.gender:
        details.append(f"Gender: {analysis.gender}")
    if analysis.date_of_birth:
        details.append(f"DOB: {analysis.date_of_birth}")
    if analysis.status:
        details.append(f"Status: {analysis.status}")
    if details:
        lines.append(" | ".join(details))

    if analysis.sire_lpn or analysis.dam_lpn:
        lines.append(
            f"**Sire**: {analysis.sire_lpn or 'Unknown'} | **Dam**: {analysis.dam_lpn or 'Unknown'}"
        )

    if analysis.trait_profile:
        lines.append("")
        if analysis.trait_profile.strengths:
            lines.append(f"**Strengths**: {', '.join(analysis.trait_profile.strengths)}")
        if analysis.trait_profile.weaknesses:
            lines.append(f"**Weaknesses**: {', '.join(analysis.trait_profile.weaknesses)}")

    if analysis.index_scores:
        lines.append("")
        lines.append(
            "**Index Scores**: "
            + " | ".join(f"{k}: {v:.1f}" for k, v in analysis.index_scores.items())
        )

    return "\n".join(lines)


def format_validation_report(
    valid: list[str],
    not_found: list[str],
    errors: dict[str, str],
) -> str:
    """Format a validation report for flock import."""
    lines = ["## Import Validation Report", ""]

    lines.append(f"**Successfully fetched**: {len(valid)} animals")

    if not_found:
        lines.append(f"**Not found in NSIP**: {len(not_found)}")
        for lpn in not_found[:10]:  # Show first 10
            lines.append(f"  - {lpn}")
        if len(not_found) > 10:
            lines.append(f"  - ... and {len(not_found) - 10} more")

    if errors:
        lines.append(f"**Errors**: {len(errors)}")
        for lpn, error in list(errors.items())[:5]:
            lines.append(f"  - {lpn}: {error}")

    return "\n".join(lines)
