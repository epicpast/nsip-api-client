"""MCP Skill Prompts - Direct execution prompts for breeding tools.

This module provides 10 MCP prompts that match the existing slash commands,
enabling direct execution of breeding decision tools through the MCP protocol.

Prompts:
    flock_import        - Import and enrich flock data
    ebv_analyzer        - Compare EBVs across animals
    inbreeding          - Calculate inbreeding coefficients
    selection_index     - Calculate custom breeding indexes
    ancestry            - Generate pedigree reports
    flock_dashboard     - Generate flock statistics
    mating_plan         - Optimize breeding pairs (guided)
    trait_improvement   - Plan multi-generation selection (guided)
    progeny_report      - Evaluate sires by offspring
    breeding_recs       - AI-powered recommendations (guided)
"""

import logging
from typing import Any

from nsip_mcp.knowledge_base import (
    get_selection_index,
    get_trait_info,
)
from nsip_mcp.metrics import server_metrics
from nsip_mcp.server import mcp
from nsip_mcp.tools import get_nsip_client

logger = logging.getLogger(__name__)


def _record_prompt_execution(prompt_name: str, success: bool) -> None:
    """Record prompt execution metrics."""
    server_metrics.record_prompt_execution(prompt_name, success)


def _fetch_all_progeny(client: Any, sire_lpn: str, max_pages: int = 10) -> tuple[list, int]:
    """Fetch all progeny for a sire with pagination.

    Returns:
        Tuple of (list of progeny animals, total count)
    """
    all_animals = []
    page = 0
    page_size = 100
    total_count = 0

    while page < max_pages:
        progeny_page = client.get_progeny(lpn_id=sire_lpn, page=page, page_size=page_size)
        if not progeny_page:
            break
        total_count = progeny_page.total_count
        all_animals.extend(progeny_page.animals)
        if len(all_animals) >= total_count:
            break
        page += 1

    return all_animals, total_count


def _count_progeny_by_sex(progeny_animals: list) -> tuple[int, int]:
    """Count male and female offspring."""
    males = sum(1 for p in progeny_animals if p.sex in ("M", "1"))
    females = sum(1 for p in progeny_animals if p.sex in ("F", "2"))
    return males, females


def _collect_progeny_trait_stats(
    client: Any, progeny_animals: list, max_fetch: int = 50
) -> dict[str, list]:
    """Fetch detailed EBVs for progeny and collect trait statistics."""
    trait_stats: dict[str, list] = {}
    fetched = 0

    for prog in progeny_animals:
        if fetched >= max_fetch:
            break
        try:
            details = client.get_animal_details(search_string=prog.lpn_id)
            if details and details.traits:
                for name, trait_obj in details.traits.items():
                    if trait_obj and trait_obj.value is not None:
                        trait_stats.setdefault(name, []).append(trait_obj.value)
                fetched += 1
        except Exception as e:
            logger.debug(f"Failed to fetch progeny {prog.lpn_id}: {e}")

    return trait_stats


def _format_sire_ebvs(sire_traits: dict, trait_names: list[str]) -> str:
    """Format sire's own EBVs for display."""
    lines = []
    for name in trait_names:
        trait_data = sire_traits.get(name)
        if trait_data:
            val = trait_data.get("value") if isinstance(trait_data, dict) else None
            if val is not None:
                lines.append(f"- **{name}**: {val:.2f}")
    return "\n".join(lines) + "\n" if lines else ""


def _format_progeny_stats_table(trait_stats: dict, key_traits: list[str]) -> str:
    """Format progeny EBV statistics as a markdown table."""
    rows = []
    for trait in key_traits:
        values = trait_stats.get(trait, [])
        if values:
            avg = sum(values) / len(values)
            min_v, max_v = min(values), max(values)
            rows.append(f"| {trait} | {avg:.2f} | {min_v:.2f} | {max_v:.2f} | {len(values)} |")
    return "\n".join(rows) + "\n" if rows else ""


def _format_evaluation(sire_traits: dict, trait_stats: dict, traits: list[str]) -> str:
    """Format sire vs progeny comparison."""
    lines = []
    for name in traits:
        sire_trait = sire_traits.get(name)
        sire_val = sire_trait.get("value") if isinstance(sire_trait, dict) else None
        prog_vals = trait_stats.get(name, [])
        if sire_val is not None and prog_vals:
            prog_avg = sum(prog_vals) / len(prog_vals)
            if prog_avg > 0:
                lines.append(f"- {name}: Progeny averaging {prog_avg:.2f} (sire: {sire_val:.2f})")
    return "\n".join(lines) + "\n" if lines else ""


@mcp.prompt(
    name="ebv_analyzer", description="Compare and analyze EBV traits across a group of animals"
)
async def ebv_analyzer_prompt(
    lpn_ids: str,
    traits: str = "BWT,WWT,PWWT,YFAT,YEMD,NLW",
) -> list[dict[str, Any]]:
    """Compare EBVs across multiple animals.

    Args:
        lpn_ids: Comma-separated list of LPN IDs to compare
        traits: Comma-separated list of trait codes to analyze

    Returns:
        Prompt messages with comparison table and analysis
    """
    try:
        client = get_nsip_client()
        lpn_list = [lpn.strip() for lpn in lpn_ids.split(",")]
        trait_list = [t.strip().upper() for t in traits.split(",")]

        # Fetch animal data
        animals_data: list[dict[str, Any]] = []
        for lpn in lpn_list:
            try:
                animal = client.get_animal_details(search_string=lpn)
                if animal:
                    animals_data.append(animal.to_dict())
            except Exception as e:
                logger.debug(f"Failed to fetch animal {lpn}: {e}")
                continue

        if not animals_data:
            _record_prompt_execution("ebv_analyzer", False)
            msg = f"No animals found for LPN IDs: {lpn_ids}. Please verify the IDs."
            return [{"role": "user", "content": {"type": "text", "text": msg}}]

        # Build comparison table
        table_rows = []
        header = ["Animal"] + trait_list
        table_rows.append("| " + " | ".join(header) + " |")
        table_rows.append("| " + " | ".join(["---"] * len(header)) + " |")

        for animal_dict in animals_data:
            name = animal_dict.get("name", animal_dict.get("lpn_id", "Unknown"))
            ebvs = animal_dict.get("ebvs", {})
            row = [name]
            for trait in trait_list:
                value = ebvs.get(trait)
                row.append(f"{value:.2f}" if value is not None else "N/A")
            table_rows.append("| " + " | ".join(row) + " |")

        table = "\n".join(table_rows)

        # Get trait interpretations
        trait_notes = []
        for trait in trait_list:
            info = get_trait_info(trait)
            if info:
                interp = info.get("interpretation", "")
                trait_notes.append(f"- **{trait}**: {info.get('name', trait)} ({interp})")

        analysis = f"""## EBV Comparison Analysis

### Comparison Table

{table}

### Trait Interpretations

{chr(10).join(trait_notes)}

### Summary

Compared {len(animals_data)} animals across {len(trait_list)} traits.
Use this data to identify the best candidates for your breeding goals.
"""

        _record_prompt_execution("ebv_analyzer", True)
        return [{"role": "user", "content": {"type": "text", "text": analysis}}]

    except Exception as e:
        _record_prompt_execution("ebv_analyzer", False)
        return [
            {"role": "user", "content": {"type": "text", "text": f"Error analyzing EBVs: {str(e)}"}}
        ]


@mcp.prompt(
    name="selection_index", description="Calculate and rank animals by selection index scores"
)
async def selection_index_prompt(
    lpn_ids: str,
    index_name: str = "balanced",
) -> list[dict[str, Any]]:
    """Calculate selection index scores for animals.

    Args:
        lpn_ids: Comma-separated list of LPN IDs to score
        index_name: Selection index to use (terminal, maternal, hair, balanced, etc.)

    Returns:
        Prompt messages with ranked animals and index breakdown
    """
    try:
        client = get_nsip_client()
        lpn_list = [lpn.strip() for lpn in lpn_ids.split(",")]

        # Get index definition
        index_def = get_selection_index(index_name)
        if not index_def:
            _record_prompt_execution("selection_index", False)
            msg = f"Unknown index: {index_name}. Available: terminal, maternal, hair, balanced"
            return [{"role": "user", "content": {"type": "text", "text": msg}}]

        weights = index_def.get("weights", {})

        # Calculate scores
        scored_animals: list[dict[str, Any]] = []
        for lpn in lpn_list:
            try:
                animal = client.get_animal_details(search_string=lpn)
                if not animal:
                    continue

                data = animal.to_dict()
                ebvs = data.get("ebvs", {})

                # Calculate weighted score
                score = 0.0
                contributions = {}
                for trait, weight in weights.items():
                    ebv_val = ebvs.get(trait)
                    if ebv_val is not None:
                        contribution = float(ebv_val) * weight
                        score += contribution
                        contributions[trait] = contribution

                scored_animals.append(
                    {
                        "lpn_id": data.get("lpn_id"),
                        "name": data.get("name", "Unknown"),
                        "score": round(score, 2),
                        "contributions": contributions,
                    }
                )

            except Exception as e:
                logger.debug(f"Failed to score animal: {e}")
                continue

        if not scored_animals:
            _record_prompt_execution("selection_index", False)
            return [
                {
                    "role": "user",
                    "content": {"type": "text", "text": "No animals found for scoring."},
                }
            ]

        # Sort by score
        scored_animals.sort(key=lambda x: x["score"], reverse=True)

        # Build output
        idx_name = index_def.get("name", index_name)
        idx_desc = index_def.get("description", "N/A")
        result = f"""## Selection Index Rankings: {idx_name}

**Index Description**: {idx_desc}

### Rankings

| Rank | Animal | Score |
| --- | --- | --- |
"""
        for i, scored in enumerate(scored_animals, 1):
            name = scored["name"]
            lpn = scored["lpn_id"]
            score = scored["score"]
            result += f"| {i} | {name} ({lpn}) | {score:.2f} |\n"

        result += """
### Index Weights

"""
        for trait, weight in weights.items():
            direction = "higher better" if weight > 0 else "lower better"
            result += f"- **{trait}**: {weight:+.2f} ({direction})\n"

        result += f"""
### Use Case

{index_def.get("use_case", "General purpose selection.")}
"""

        _record_prompt_execution("selection_index", True)
        return [{"role": "user", "content": {"type": "text", "text": result}}]

    except Exception as e:
        _record_prompt_execution("selection_index", False)
        return [
            {
                "role": "user",
                "content": {"type": "text", "text": f"Error calculating index: {str(e)}"},
            }
        ]


@mcp.prompt(name="ancestry", description="Generate comprehensive ancestry/pedigree reports")
async def ancestry_prompt(lpn_id: str) -> list[dict[str, Any]]:
    """Generate a pedigree report for an animal.

    Args:
        lpn_id: LPN ID of the animal

    Returns:
        Prompt messages with formatted pedigree tree
    """
    try:
        client = get_nsip_client()

        # Get animal details
        animal = client.get_animal_details(search_string=lpn_id)
        if not animal:
            _record_prompt_execution("ancestry", False)
            return [
                {"role": "user", "content": {"type": "text", "text": f"Animal not found: {lpn_id}"}}
            ]

        # Get lineage
        lineage = client.get_lineage(lpn_id=lpn_id)

        animal_data = animal.to_dict()

        def format_ancestor(ancestor, prefix: str = "") -> str:
            """Format a LineageAnimal for display."""
            if not ancestor:
                return f"{prefix}Unknown"

            # Handle both dict (from to_dict) and object forms
            if isinstance(ancestor, dict):
                lpn = ancestor.get("lpn_id", "N/A")
                farm = ancestor.get("farm_name") or "Unknown"
            else:
                lpn = getattr(ancestor, "lpn_id", "N/A")
                farm = getattr(ancestor, "farm_name", None) or "Unknown"
            return f"{prefix}{farm} ({lpn})"

        # Get lineage ancestors directly from the Lineage object
        sire = lineage.sire if lineage else None
        dam = lineage.dam if lineage else None

        # For grandparents, we need to check generations list
        # generations[0] = [sire, dam], generations[1] = [ss, sd, ds, dd], etc.
        sire_sire = None
        sire_dam = None
        dam_sire = None
        dam_dam = None
        if lineage and lineage.generations and len(lineage.generations) > 1:
            gen1 = lineage.generations[1]  # Grandparent generation
            if len(gen1) >= 4:
                sire_sire = gen1[0]
                sire_dam = gen1[1]
                dam_sire = gen1[2]
                dam_dam = gen1[3]

        result = f"""## Pedigree Report: {lpn_id}

**LPN ID**: {animal_data.get("lpn_id", lpn_id)}
**Breed**: {animal_data.get("breed", "Unknown")}
**Birth Date**: {animal_data.get("date_of_birth", "Unknown")}
**Sex**: {animal_data.get("gender", "Unknown")}

### Pedigree Tree

```
                    ┌── {format_ancestor(sire_sire)}
         ┌── SIRE: {format_ancestor(sire)}
         │         └── {format_ancestor(sire_dam)}
{lpn_id}
         │         ┌── {format_ancestor(dam_sire)}
         └── DAM:  {format_ancestor(dam)}
                   └── {format_ancestor(dam_dam)}
```

### Key EBVs

"""
        # traits is a dict of Trait objects, not raw values
        traits = animal_data.get("traits", {})
        key_traits = ["BWT", "WWT", "PWWT", "NLW", "MWWT"]
        for trait_name in key_traits:
            trait_data = traits.get(trait_name)
            if trait_data:
                # Handle both dict (from to_dict) and Trait object
                if isinstance(trait_data, dict):
                    val = trait_data.get("value")
                else:
                    val = getattr(trait_data, "value", None)
                if val is not None:
                    result += f"- **{trait_name}**: {val:.2f}\n"

        _record_prompt_execution("ancestry", True)
        return [{"role": "user", "content": {"type": "text", "text": result}}]

    except Exception as e:
        _record_prompt_execution("ancestry", False)
        return [
            {
                "role": "user",
                "content": {"type": "text", "text": f"Error generating pedigree: {str(e)}"},
            }
        ]


@mcp.prompt(name="inbreeding", description="Calculate inbreeding coefficients using pedigree data")
async def inbreeding_prompt(
    ram_lpn: str,
    ewe_lpn: str,
) -> list[dict[str, Any]]:
    """Calculate projected inbreeding for a potential mating.

    Args:
        ram_lpn: LPN ID of the ram (sire)
        ewe_lpn: LPN ID of the ewe (dam)

    Returns:
        Prompt messages with inbreeding analysis and recommendations
    """
    try:
        client = get_nsip_client()

        # Get lineage for both parents
        ram_lineage = client.get_lineage(lpn_id=ram_lpn)
        ewe_lineage = client.get_lineage(lpn_id=ewe_lpn)

        if not ram_lineage or not ewe_lineage:
            _record_prompt_execution("inbreeding", False)
            missing = "ram" if not ram_lineage else "ewe"
            return [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": f"Could not find lineage for {missing}. Verify the LPN ID.",
                    },
                }
            ]

        # Find common ancestors
        def extract_ancestors(lineage: dict, depth: int = 4) -> set[str]:
            ancestors = set()

            def traverse(data: dict, current_depth: int):
                if not data or current_depth >= depth:
                    return
                for key in ["sire", "dam"]:
                    parent = data.get(key)
                    if parent and isinstance(parent, dict):
                        lpn = parent.get("lpn_id") or parent.get("lpnId")
                        if lpn:
                            ancestors.add(lpn)
                        traverse(parent, current_depth + 1)

            traverse(lineage, 0)
            return ancestors

        ram_ancestors = extract_ancestors(ram_lineage.to_dict())
        ewe_ancestors = extract_ancestors(ewe_lineage.to_dict())

        common = ram_ancestors & ewe_ancestors

        # Estimate inbreeding
        f_coef = len(common) * 0.0625 if common else 0.0
        f_coef = min(f_coef, 0.25)

        # Determine risk level
        if f_coef < 0.03:
            risk = "LOW"
            recommendation = "This mating has acceptable inbreeding levels."
        elif f_coef < 0.0625:
            risk = "MODERATE"
            recommendation = "Consider alternatives. Monitor offspring for reduced vigor."
        else:
            risk = "HIGH"
            recommendation = "Avoid this mating. High risk of inbreeding depression."

        result = f"""## Inbreeding Analysis

**Potential Mating**: Ram {ram_lpn} × Ewe {ewe_lpn}

### Results

- **Inbreeding Coefficient (F)**: {f_coef:.4f} ({f_coef * 100:.2f}%)
- **Risk Level**: {risk}
- **Common Ancestors Found**: {len(common)}

### Common Ancestors

"""
        if common:
            for ancestor in list(common)[:10]:
                result += f"- {ancestor}\n"
            if len(common) > 10:
                result += f"- ... and {len(common) - 10} more\n"
        else:
            result += "No common ancestors found within 4 generations.\n"

        result += f"""
### Recommendation

{recommendation}

### Inbreeding Risk Guide

| F Coefficient | Risk Level | Impact |
| --- | --- | --- |
| < 3% | Low | Acceptable for most programs |
| 3-6% | Moderate | Some reduction in fitness possible |
| > 6% | High | Significant inbreeding depression likely |
"""

        _record_prompt_execution("inbreeding", True)
        return [{"role": "user", "content": {"type": "text", "text": result}}]

    except Exception as e:
        _record_prompt_execution("inbreeding", False)
        return [
            {
                "role": "user",
                "content": {"type": "text", "text": f"Error calculating inbreeding: {str(e)}"},
            }
        ]


@mcp.prompt(
    name="progeny_report", description="Evaluate sires by analyzing their offspring performance"
)
async def progeny_report_prompt(sire_lpn: str) -> list[dict[str, Any]]:
    """Generate a progeny performance report for a sire.

    Args:
        sire_lpn: LPN ID of the sire to evaluate

    Returns:
        Prompt messages with offspring statistics and sire evaluation
    """
    try:
        client = get_nsip_client()

        # Get sire details
        sire = client.get_animal_details(search_string=sire_lpn)
        if not sire:
            _record_prompt_execution("progeny_report", False)
            return [
                {"role": "user", "content": {"type": "text", "text": f"Sire not found: {sire_lpn}"}}
            ]

        # Get all progeny with pagination
        all_progeny_animals, total_count = _fetch_all_progeny(client, sire_lpn)

        if not all_progeny_animals:
            _record_prompt_execution("progeny_report", False)
            return [
                {
                    "role": "user",
                    "content": {"type": "text", "text": f"No progeny found for sire: {sire_lpn}"},
                }
            ]

        sire_data = sire.to_dict()
        sire_traits = sire_data.get("traits", {})

        # Count by sex and collect trait statistics
        males, females = _count_progeny_by_sex(all_progeny_animals)
        max_fetch = min(len(all_progeny_animals), 50)
        trait_stats = _collect_progeny_trait_stats(client, all_progeny_animals, max_fetch)

        # Build the report
        sire_ebvs = _format_sire_ebvs(sire_traits, ["BWT", "WWT", "PWWT", "NLW"])
        sample_note = f" (based on {max_fetch} sampled)" if max_fetch < total_count else ""
        key_traits = ["BWT", "WWT", "PWWT", "YWT", "NLW", "MWWT"]
        stats_table = _format_progeny_stats_table(trait_stats, key_traits)
        evaluation = _format_evaluation(sire_traits, trait_stats, ["PWWT", "NLW"])

        result = f"""## Progeny Report: {sire_lpn}

**Sire LPN**: {sire_lpn}
**Breed**: {sire_data.get("breed", "Unknown")}
**Total Progeny**: {total_count}
**Ram Lambs**: {males} | **Ewe Lambs**: {females}

### Sire's Own EBVs

{sire_ebvs}
### Progeny EBV Averages{sample_note}

| Trait | Average | Min | Max | Count |
| --- | --- | --- | --- | --- |
{stats_table}
### Evaluation

{evaluation}"""

        _record_prompt_execution("progeny_report", True)
        return [{"role": "user", "content": {"type": "text", "text": result}}]

    except Exception as e:
        _record_prompt_execution("progeny_report", False)
        return [
            {
                "role": "user",
                "content": {"type": "text", "text": f"Error generating progeny report: {str(e)}"},
            }
        ]


@mcp.prompt(
    name="flock_dashboard",
    description="Generate comprehensive flock performance statistics and insights",
)
async def flock_dashboard_prompt(flock_prefix: str) -> list[dict[str, Any]]:
    """Generate a flock performance dashboard.

    Args:
        flock_prefix: Flock ID prefix (first 4-5 digits of LPN)

    Returns:
        Prompt messages with flock statistics and performance metrics
    """
    try:
        client = get_nsip_client()

        # Search for flock animals using SearchCriteria with flock_id filter
        from nsip_client.models import SearchCriteria

        search_criteria = SearchCriteria(flock_id=flock_prefix)
        search_result = client.search_animals(
            page=0,
            page_size=100,
            search_criteria=search_criteria,  # Max allowed by API
        )
        if not search_result or not search_result.results:
            _record_prompt_execution("flock_dashboard", False)
            return [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": f"No animals found for flock: {flock_prefix}",
                    },
                }
            ]

        # search_result.results is a list of dicts from the API
        animals: list[dict[str, Any]] = search_result.results

        # Calculate statistics
        total = len(animals)
        males = sum(1 for a in animals if a.get("sex") == "M")
        females = sum(1 for a in animals if a.get("sex") == "F")

        # EBV statistics
        trait_stats: dict[str, list] = {}
        for animal in animals:
            ebvs = animal.get("ebvs", {})
            for trait, value in ebvs.items():
                if value is not None:
                    if trait not in trait_stats:
                        trait_stats[trait] = []
                    trait_stats[trait].append(float(value))

        result = f"""## Flock Dashboard: {flock_prefix}

### Overview

- **Total Animals**: {total}
- **Males**: {males}
- **Females**: {females}
- **Records Retrieved**: {len(animals)}

### Flock EBV Averages

| Trait | Average | Min | Max | Count |
| --- | --- | --- | --- | --- |
"""
        priority_traits = ["BWT", "WWT", "PWWT", "YWT", "NLW", "MWWT", "FEC"]
        for trait in priority_traits:
            values = trait_stats.get(trait, [])
            if values:
                avg = sum(values) / len(values)
                min_v = min(values)
                max_v = max(values)
                cnt = len(values)
                result += f"| {trait} | {avg:.2f} | {min_v:.2f} | {max_v:.2f} | {cnt} |\n"

        # Top performers
        result += """
### Top Performers by PWWT

"""
        # Find animals with PWWT data
        with_pwwt = [
            (a, a.get("ebvs", {}).get("PWWT"))
            for a in animals
            if a.get("ebvs", {}).get("PWWT") is not None
        ]
        with_pwwt.sort(key=lambda x: x[1], reverse=True)

        for animal, pwwt in with_pwwt[:5]:
            name = animal.get("name", animal.get("lpn_id", "Unknown"))
            result += f"1. **{name}**: PWWT = {pwwt:.2f}\n"

        result += """
### Recommendations

Based on the flock averages, consider:
- Focus selection on traits with the most variation (opportunity for improvement)
- Identify animals in the top 20% for replacement stock
- Cull animals consistently below flock average across multiple traits
"""

        _record_prompt_execution("flock_dashboard", True)
        return [{"role": "user", "content": {"type": "text", "text": result}}]

    except Exception as e:
        _record_prompt_execution("flock_dashboard", False)
        return [
            {
                "role": "user",
                "content": {"type": "text", "text": f"Error generating dashboard: {str(e)}"},
            }
        ]
