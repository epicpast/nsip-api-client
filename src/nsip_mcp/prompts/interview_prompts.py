"""Guided interview prompts for complex breeding workflows.

This module provides multi-turn interview prompts that use MCP sampling
to progressively gather inputs for complex decision-making workflows.
These are used for scenarios that require multiple pieces of information
and interactive clarification.

Interview Prompts:
    - guided_mating_plan: Interactive mating optimization workflow
    - guided_trait_improvement: Multi-generation selection planning
    - guided_breeding_recommendations: AI-powered breeding recommendations
"""

from typing import Any

from nsip_mcp.knowledge_base import (
    get_heritabilities,
    get_region_info,
    get_selection_index,
    list_regions,
)
from nsip_mcp.metrics import server_metrics
from nsip_mcp.server import mcp


def _record_prompt_execution(prompt_name: str, success: bool) -> None:
    """Record prompt execution metrics."""
    server_metrics.record_prompt_execution(prompt_name, success)


INTERVIEW_SYSTEM_PROMPT = """You are an NSIP breeding assistant gathering information
for an advanced breeding analysis. Ask clear, specific questions and validate
responses. Be professional and helpful. When you have enough information,
summarize what you've collected and confirm with the user before proceeding."""


@mcp.prompt(
    name="guided_mating_plan",
    description="Interactive guided interview for optimizing ram-ewe pairings",
)
async def guided_mating_plan_prompt(
    rams: str = "",
    ewes: str = "",
    goal: str = "",
) -> list[dict[str, Any]]:
    """Start a guided mating plan interview.

    This prompt initiates an interactive workflow to gather all necessary
    information for optimal mating recommendations. If parameters are
    provided, it uses them; otherwise, it guides the user through input.

    Args:
        rams: Comma-separated ram LPN IDs (optional, will prompt if empty)
        ewes: Comma-separated ewe LPN IDs (optional, will prompt if empty)
        goal: Breeding goal - terminal, maternal, hair, balanced (optional)

    Returns:
        Prompt messages to start the guided interview

    Note:
        This is an interactive prompt that may use ctx.sample() for
        follow-up questions during execution.
    """
    try:
        # Get selection index options for context
        indexes = {}
        for idx_type in ["terminal", "maternal", "hair", "balanced"]:
            idx_info = get_selection_index(idx_type)
            if idx_info:
                indexes[idx_type] = idx_info.get("description", "")

        # Build the interview context
        context = f"""
{INTERVIEW_SYSTEM_PROMPT}

## Mating Plan Interview

I'll help you create an optimized mating plan. I need to gather some information.

### Current Inputs
"""
        if rams:
            context += f"- **Rams provided**: {rams}\n"
        else:
            context += "- **Rams**: Not yet provided\n"

        if ewes:
            context += f"- **Ewes provided**: {ewes}\n"
        else:
            context += "- **Ewes**: Not yet provided\n"

        if goal:
            context += f"- **Breeding goal**: {goal}\n"
        else:
            context += "- **Breeding goal**: Not yet specified\n"

        context += """
### Available Breeding Goals

"""
        for goal_type, desc in indexes.items():
            context += f"- **{goal_type.title()}**: {desc}\n"

        # Determine what information is still needed
        missing = []
        if not rams:
            missing.append("ram LPN IDs (comma-separated)")
        if not ewes:
            missing.append("ewe LPN IDs (comma-separated)")
        if not goal:
            missing.append("breeding goal (terminal, maternal, hair, or balanced)")

        if missing:
            context += """
### Information Needed

Please provide the following:
"""
            for i, item in enumerate(missing, 1):
                context += f"{i}. {item}\n"

            context += """
You can provide all at once or one at a time. For example:
- "My rams are 6332-123, 6332-456"
- "Ewes: 6332-789, 6332-101, 6332-102"
- "Goal: terminal"
"""
        else:
            context += """
### Ready for Analysis

I have all the information needed. Shall I proceed with the mating optimization?

**Summary:**
- Analyzing {ram_count} rams × {ewe_count} ewes
- Goal: {goal} index optimization
- Will consider inbreeding avoidance and EBV complementarity

Reply "proceed" to run the analysis or provide corrections.
""".format(ram_count=len(rams.split(",")), ewe_count=len(ewes.split(",")), goal=goal)

        _record_prompt_execution("guided_mating_plan", True)
        return [
            {"role": "system", "content": {"type": "text", "text": INTERVIEW_SYSTEM_PROMPT}},
            {"role": "user", "content": {"type": "text", "text": context}},
        ]

    except Exception as e:
        _record_prompt_execution("guided_mating_plan", False)
        return [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": f"Error starting mating plan interview: {str(e)}",
                },
            }
        ]


@mcp.prompt(
    name="guided_trait_improvement",
    description="Interactive multi-generation trait selection planning",
)
async def guided_trait_improvement_prompt(
    trait: str = "",
    current_average: str = "",
    target_value: str = "",
    generations: str = "",
    region: str = "",
) -> list[dict[str, Any]]:
    """Start a guided trait improvement planning interview.

    This prompt helps users plan multi-generation selection strategies
    for specific trait improvement goals.

    Args:
        trait: Target trait code (e.g., WWT, NLW, PWWT)
        current_average: Current flock average for the trait
        target_value: Target value to achieve
        generations: Number of generations to plan (default: 3)
        region: NSIP region for context

    Returns:
        Prompt messages to guide the trait improvement planning
    """
    try:
        # Get heritability data for context
        heritabilities = get_heritabilities()
        region_info = get_region_info(region) if region else None

        context = f"""
{INTERVIEW_SYSTEM_PROMPT}

## Trait Improvement Planning Interview

I'll help you create a multi-generation selection plan for trait improvement.

### Heritability Reference

Understanding heritability helps set realistic expectations:
"""
        if heritabilities:
            for trait_code, h2 in list(heritabilities.items())[:8]:
                progress = "faster" if h2 > 0.25 else "slower" if h2 < 0.15 else "moderate"
                context += f"- **{trait_code}**: h² = {h2} ({progress} genetic progress)\n"

        context += """
### Current Inputs
"""
        if trait:
            h2_value = heritabilities.get(trait)
            h2_str = str(h2_value) if h2_value is not None else "unknown"
            context += f"- **Target trait**: {trait} (h² = {h2_str})\n"
        else:
            context += "- **Target trait**: Not yet specified\n"

        if current_average:
            context += f"- **Current flock average**: {current_average}\n"
        else:
            context += "- **Current flock average**: Not yet provided\n"

        if target_value:
            context += f"- **Target value**: {target_value}\n"
        else:
            context += "- **Target value**: Not yet specified\n"

        if generations:
            context += f"- **Planning horizon**: {generations} generations\n"
        else:
            context += "- **Planning horizon**: Not yet specified (default: 3)\n"

        if region_info:
            context += f"- **Region**: {region_info.get('name', region)}\n"

        # Determine missing information
        missing = []
        if not trait:
            missing.append("target trait code (e.g., WWT for weaning weight)")
        if not current_average:
            missing.append("current flock average for the trait")
        if not target_value:
            missing.append("target value you want to achieve")

        if missing:
            context += """
### Information Needed

Please provide:
"""
            for i, item in enumerate(missing, 1):
                context += f"{i}. {item}\n"

            context += """
**Tip**: You can get your current flock average from the flock dashboard
or by analyzing your animals' EBVs.

Example responses:
- "I want to improve WWT (weaning weight)"
- "Current average is +2.5 lbs, I want to reach +5.0 lbs"
- "Plan over 4 generations"
"""
        else:
            # Calculate expected progress
            h2 = heritabilities.get(trait, 0.25)
            current = float(current_average)
            target = float(target_value)
            gap = target - current
            gen_count = int(generations) if generations else 3

            # Simple response to selection model
            # R = h² × S, where S is selection differential
            # Assume top 20% selection (S ≈ 1.4 standard deviations)
            expected_per_gen = h2 * 1.4 * abs(gap) / gen_count  # Rough estimate

            context += f"""
### Analysis Preview

Based on the information provided:
- **Gap to close**: {gap:+.2f} units
- **Heritability**: {h2}
- **Expected progress per generation**: ~{expected_per_gen:.2f} units
- **Estimated generations to goal**: {abs(gap) / expected_per_gen:.1f}

Shall I proceed with detailed selection recommendations?
Reply "proceed" or provide any corrections.
"""

        _record_prompt_execution("guided_trait_improvement", True)
        return [
            {"role": "system", "content": {"type": "text", "text": INTERVIEW_SYSTEM_PROMPT}},
            {"role": "user", "content": {"type": "text", "text": context}},
        ]

    except Exception as e:
        _record_prompt_execution("guided_trait_improvement", False)
        return [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": f"Error starting trait improvement interview: {str(e)}",
                },
            }
        ]


@mcp.prompt(
    name="guided_breeding_recommendations",
    description="AI-powered breeding recommendations with guided input gathering",
)
async def guided_breeding_recommendations_prompt(
    flock_data: str = "",
    priorities: str = "",
    constraints: str = "",
    region: str = "",
) -> list[dict[str, Any]]:
    """Start a guided breeding recommendations interview.

    This prompt gathers comprehensive flock information to provide
    AI-powered breeding recommendations tailored to the operation.

    Args:
        flock_data: Flock identifier or file path with flock data
        priorities: Comma-separated breeding priorities
        constraints: Any constraints (budget, facilities, timing)
        region: NSIP region for regional adaptation

    Returns:
        Prompt messages to guide the recommendations process
    """
    try:
        # Get region options
        all_regions = list_regions()
        region_info = get_region_info(region) if region else None

        context = f"""
{INTERVIEW_SYSTEM_PROMPT}

## Breeding Recommendations Interview

I'll help you develop a comprehensive breeding strategy tailored to your operation.

### NSIP Regions

"""
        if all_regions:
            for reg_id in all_regions[:6]:
                # list_regions() returns list of region ID strings
                context += f"- {reg_id}\n"

        context += """
### Current Information
"""
        if flock_data:
            context += f"- **Flock data**: {flock_data}\n"
        else:
            context += "- **Flock data**: Not yet provided\n"

        if priorities:
            context += f"- **Breeding priorities**: {priorities}\n"
        else:
            context += "- **Breeding priorities**: Not yet specified\n"

        if constraints:
            context += f"- **Constraints**: {constraints}\n"
        else:
            context += "- **Constraints**: Not yet specified\n"

        if region_info:
            context += f"- **Region**: {region_info.get('name', region)}\n"
            context += f"  - Climate: {region_info.get('climate', 'varies')}\n"
            context += f"  - Primary breeds: {', '.join(region_info.get('primary_breeds', []))}\n"

        # Information gathering
        missing = []
        if not flock_data:
            missing.append("flock identifier (LPN prefix) or file path to flock data")
        if not priorities:
            missing.append("breeding priorities (e.g., growth, maternal, parasite resistance)")

        if missing:
            context += """
### Information Needed

To provide personalized recommendations, please tell me:
"""
            for i, item in enumerate(missing, 1):
                context += f"{i}. {item}\n"

            context += """
**Priority Examples:**
- "Focus on growth and carcass quality" (terminal emphasis)
- "Improve lambing ease and milk production" (maternal emphasis)
- "Maximize parasite resistance" (hair sheep / sustainable)
- "Balance growth with maternal traits" (dual-purpose)

**Optional Information:**
- Budget constraints
- Facility limitations
- Breeding season preferences
- Number of ewes to breed
"""
        else:
            context += """
### Ready for Analysis

I have enough information to generate recommendations.

**I will analyze:**
1. Current flock genetic profile
2. Alignment with your priorities
3. Regional considerations
4. Practical implementation steps

Reply "proceed" to generate recommendations or add more details.
"""

        _record_prompt_execution("guided_breeding_recommendations", True)
        return [
            {"role": "system", "content": {"type": "text", "text": INTERVIEW_SYSTEM_PROMPT}},
            {"role": "user", "content": {"type": "text", "text": context}},
        ]

    except Exception as e:
        _record_prompt_execution("guided_breeding_recommendations", False)
        return [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": f"Error starting breeding recommendations interview: {str(e)}",
                },
            }
        ]


@mcp.prompt(
    name="guided_flock_import",
    description="Interactive flock data import with validation and enrichment",
)
async def guided_flock_import_prompt(
    file_path: str = "",
    flock_prefix: str = "",
    data_format: str = "",
) -> list[dict[str, Any]]:
    """Start a guided flock import interview.

    This prompt helps users import flock data from spreadsheets
    with validation and NSIP data enrichment.

    Args:
        file_path: Path to spreadsheet file (CSV, Excel)
        flock_prefix: NSIP flock prefix for LPN matching
        data_format: Expected data format (nsip, custom)

    Returns:
        Prompt messages to guide the import process
    """
    try:
        context = f"""
{INTERVIEW_SYSTEM_PROMPT}

## Flock Data Import Interview

I'll help you import and enrich your flock data with NSIP breeding values.

### Supported Formats

- **CSV files** (.csv) - Comma or tab separated
- **Excel files** (.xlsx, .xls)
- **NSIP export format** - Standard NSIP data export
- **Custom format** - We'll map your columns

### Current Information
"""
        if file_path:
            context += f"- **File**: {file_path}\n"
        else:
            context += "- **File**: Not yet provided\n"

        if flock_prefix:
            context += f"- **Flock prefix**: {flock_prefix}\n"
        else:
            context += "- **Flock prefix**: Not yet specified\n"

        if data_format:
            context += f"- **Format**: {data_format}\n"
        else:
            context += "- **Format**: Will auto-detect\n"

        missing = []
        if not file_path:
            missing.append("path to your flock data file")

        if missing:
            context += """
### Information Needed

Please provide:
"""
            for i, item in enumerate(missing, 1):
                context += f"{i}. {item}\n"

            context += """
**Expected Column Headers:**

For best results, your file should include:
- Animal ID (LPN ID, tag number, or name)
- Birth date
- Sex (M/F)
- Sire ID (optional)
- Dam ID (optional)

I can work with various column names and will help map them.

**Example:**
"Import my flock from /path/to/flock_data.csv"
"""
        else:
            context += """
### Ready to Import

I'll process your file with these steps:
1. Read and validate the file structure
2. Map columns to NSIP data fields
3. Look up animals by LPN ID
4. Enrich with current NSIP EBVs
5. Flag any animals not found in NSIP

Reply "proceed" to start the import or provide corrections.
"""

        _record_prompt_execution("guided_flock_import", True)
        return [
            {"role": "system", "content": {"type": "text", "text": INTERVIEW_SYSTEM_PROMPT}},
            {"role": "user", "content": {"type": "text", "text": context}},
        ]

    except Exception as e:
        _record_prompt_execution("guided_flock_import", False)
        return [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": f"Error starting flock import interview: {str(e)}",
                },
            }
        ]
