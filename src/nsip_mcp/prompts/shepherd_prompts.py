"""Shepherd consultation prompts for sheep husbandry guidance.

This module provides prompts for the Shepherd agent to deliver
expert advice on breeding, health, calendar management, and economics.
These prompts use a neutral expert persona (veterinarian-like) and
provide evidence-based recommendations.
"""

from typing import Any

from nsip_mcp.knowledge_base import (
    get_calendar_template,
    get_disease_guide,
    get_economics_template,
    get_heritabilities,
    get_nutrition_guide,
    get_region_info,
    get_selection_index,
    list_regions,
)
from nsip_mcp.metrics import server_metrics
from nsip_mcp.server import mcp


def _record_prompt_execution(prompt_name: str, success: bool) -> None:
    """Record prompt execution metrics."""
    server_metrics.record_prompt_execution(prompt_name, success)


SHEPHERD_PERSONA = """You are the NSIP Shepherd, a neutral expert advisor on sheep
husbandry with the professional demeanor of a veterinarian. You provide evidence-based
recommendations, cite data sources, acknowledge uncertainty when information is limited,
and give actionable next steps. You respect regional differences in sheep production."""


def _format_cost_component(component: str, values: dict) -> str:
    """Format a single cost component for display."""
    if not isinstance(values, dict) or "average" not in values:
        return ""
    avg = values.get("average", 0)
    low = values.get("low", 0)
    high = values.get("high", 0)
    desc = values.get("description", "")
    result = f"- **{component.title()}**: ${avg} (range: ${low}-${high})"
    if desc:
        result += f" - {desc}"
    return result + "\n"


def _format_revenue_item(market_type: str, data: dict) -> str:
    """Format a single revenue item for display."""
    if not isinstance(data, dict):
        return ""
    result = ""
    if "typical_range" in data:
        ranges = data.get("typical_range", {})
        result = f"- **{market_type.replace('_', ' ').title()}**: "
        result += f"${ranges.get('average', 0)} average "
        result += f"(range: ${ranges.get('low', 0)}-${ranges.get('high', 0)})\n"
    elif "market_types" in data:
        result = f"**{market_type.replace('_', ' ').title()}**:\n"
        for mtype, mdata in data.get("market_types", {}).items():
            if isinstance(mdata, dict) and "typical_range" in mdata:
                tr = mdata.get("typical_range", {})
                result += f"  - {mtype.title()}: ${tr.get('average', 0)} "
                result += f"({mdata.get('unit', '')})\n"
    return result


@mcp.prompt(
    name="shepherd_breeding",
    description="Get expert advice on breeding decisions and genetic improvement",
)
async def shepherd_breeding_prompt(
    question: str,
    region: str = "midwest",
    production_goal: str = "balanced",
) -> list[dict[str, Any]]:
    """Get Shepherd advice on breeding decisions.

    Args:
        question: The breeding question or scenario
        region: NSIP region for regional context
        production_goal: Production focus (terminal, maternal, hair, balanced)

    Returns:
        Prompt messages with expert breeding guidance
    """
    try:
        # Get relevant knowledge base data
        region_info = get_region_info(region)
        heritabilities = get_heritabilities()
        index_info = get_selection_index(production_goal)

        region_name = region_info.get("name", region) if region_info else region
        breeds_list = ", ".join(region_info.get("primary_breeds", [])) if region_info else "Various"

        context = f"""
{SHEPHERD_PERSONA}

## Context

**Region**: {region_name}
**Production Goal**: {production_goal}
**Primary Breeds for Region**: {breeds_list}

## Heritability Reference

Key trait heritabilities for selection:
- Birth Weight (BWT): {heritabilities.get('BWT', 0.35)} - Moderate, responds well to selection
- Weaning Weight (WWT): {heritabilities.get('WWT', 0.20)} - Lower, maternal effects important
- Post-Weaning Weight (PWWT): {heritabilities.get('PWWT', 0.25)} - Moderate
- Number Lambs Weaned (NLW): {heritabilities.get('NLW', 0.10)} - Low, slow progress

## Selection Index: {index_info.get('name', production_goal) if index_info else production_goal}

{index_info.get('description', '') if index_info else ''}
{index_info.get('use_case', '') if index_info else ''}

## User Question

{question}

Please provide evidence-based breeding advice addressing this question. Include:
1. Direct answer to the question
2. Relevant genetic principles
3. Specific recommendations with expected outcomes
4. Any cautions or considerations
"""

        _record_prompt_execution("shepherd_breeding", True)
        return [
            {"role": "system", "content": {"type": "text", "text": SHEPHERD_PERSONA}},
            {"role": "user", "content": {"type": "text", "text": context}},
        ]

    except Exception as e:
        _record_prompt_execution("shepherd_breeding", False)
        return [
            {
                "role": "user",
                "content": {"type": "text", "text": f"Error preparing breeding advice: {str(e)}"},
            }
        ]


@mcp.prompt(
    name="shepherd_health",
    description="Get expert advice on sheep health, disease prevention, and nutrition",
)
async def shepherd_health_prompt(
    question: str,
    region: str = "midwest",
    life_stage: str = "maintenance",
) -> list[dict[str, Any]]:
    """Get Shepherd advice on health and nutrition.

    Args:
        question: The health or nutrition question
        region: NSIP region for disease risk context
        life_stage: Life stage (maintenance, flushing, gestation, lactation)

    Returns:
        Prompt messages with expert health guidance
    """
    try:
        # Get relevant knowledge base data
        region_info = get_region_info(region)
        diseases = get_disease_guide(region)
        nutrition = get_nutrition_guide(region, life_stage)

        context = f"""
{SHEPHERD_PERSONA}

## Context

**Region**: {region_info.get('name', region) if region_info else region}
**Life Stage**: {life_stage}
**Parasite Season**: {region_info.get('parasite_season', 'varies') if region_info else 'varies'}

## Regional Health Challenges

{chr(10).join(region_info.get('challenges', [])) if region_info else 'Consult local extension'}

## Common Diseases for Region

"""
        if diseases and isinstance(diseases, dict):
            # diseases is a dict: {disease_name: {description, prevention, ...}}
            for disease_name, disease_info in list(diseases.items())[:5]:
                if isinstance(disease_info, dict):
                    prevention_list = disease_info.get("prevention", [])
                    # prevention may be a list or string
                    if isinstance(prevention_list, list):
                        prevention = prevention_list[0] if prevention_list else "Consult vet"
                    else:
                        prevention = str(prevention_list)
                    context += f"- **{disease_name.replace('_', ' ').title()}**: {prevention}\n"

        context += f"""
## Nutrition for {life_stage.title()}

"""
        if nutrition:
            energy = nutrition.get("energy", "Varies by condition")
            protein = nutrition.get("protein", "Varies by stage")
            minerals = nutrition.get("minerals", "Sheep-specific mineral required")
            context += f"- Energy: {energy}\n"
            context += f"- Protein: {protein}\n"
            context += f"- Minerals: {minerals}\n"

        context += f"""
## User Question

{question}

Please provide evidence-based health/nutrition advice. Include:
1. Direct answer addressing the concern
2. Relevant prevention or treatment approaches
3. When to consult a veterinarian
4. Regional considerations if applicable
"""

        _record_prompt_execution("shepherd_health", True)
        return [
            {"role": "system", "content": {"type": "text", "text": SHEPHERD_PERSONA}},
            {"role": "user", "content": {"type": "text", "text": context}},
        ]

    except Exception as e:
        _record_prompt_execution("shepherd_health", False)
        return [
            {
                "role": "user",
                "content": {"type": "text", "text": f"Error preparing health advice: {str(e)}"},
            }
        ]


@mcp.prompt(
    name="shepherd_calendar", description="Get seasonal management advice and task planning"
)
async def shepherd_calendar_prompt(
    question: str,
    region: str = "midwest",
    task_type: str = "general",
) -> list[dict[str, Any]]:
    """Get Shepherd advice on seasonal management.

    Args:
        question: The calendar or planning question
        region: NSIP region for timing context
        task_type: Task category (breeding, lambing, shearing, health)

    Returns:
        Prompt messages with seasonal management guidance
    """
    try:
        # Get relevant knowledge base data
        region_info = get_region_info(region)
        calendar = get_calendar_template(task_type)

        context = f"""
{SHEPHERD_PERSONA}

## Context

**Region**: {region_info.get('name', region) if region_info else region}
**Task Focus**: {task_type}
**Typical Lambing**: {region_info.get('typical_lambing', 'Varies') if region_info else 'Varies'}

## Seasonal Tasks: {task_type.title()}

"""
        if calendar and isinstance(calendar, dict):
            tasks = calendar.get("tasks", [])
            for task in tasks[:8]:  # Top 8 tasks
                if isinstance(task, dict):
                    context += f"### {task.get('name', 'Task')}\n"
                    context += f"- **Timing**: {task.get('timing', 'As needed')}\n"
                    context += f"- **Priority**: {task.get('priority', 'moderate')}\n"
                    context += f"- **Details**: {task.get('details', '')}\n\n"

        context += """
## Regional Considerations

"""
        if region_info:
            climate = region_info.get("climate", "varies")
            challenges = ", ".join(region_info.get("challenges", []))
            context += f"- Climate: {climate}\n"
            context += f"- Challenges: {challenges}\n"

        context += f"""
## User Question

{question}

Please provide seasonal management advice. Include:
1. Recommended timing for your region
2. Priority tasks and their sequence
3. Common mistakes to avoid
4. Adjustments for weather or conditions
"""

        _record_prompt_execution("shepherd_calendar", True)
        return [
            {"role": "system", "content": {"type": "text", "text": SHEPHERD_PERSONA}},
            {"role": "user", "content": {"type": "text", "text": context}},
        ]

    except Exception as e:
        _record_prompt_execution("shepherd_calendar", False)
        return [
            {
                "role": "user",
                "content": {"type": "text", "text": f"Error preparing calendar advice: {str(e)}"},
            }
        ]


@mcp.prompt(
    name="shepherd_economics",
    description="Get advice on sheep operation economics and profitability",
)
async def shepherd_economics_prompt(
    question: str,
    flock_size: str = "medium",
    market_focus: str = "balanced",
) -> list[dict[str, Any]]:
    """Get Shepherd advice on economics and profitability.

    Args:
        question: The economics or business question
        flock_size: Flock size category (small, medium, large)
        market_focus: Market focus (direct, auction, breeding_stock)

    Returns:
        Prompt messages with economic guidance
    """
    try:
        # Get relevant knowledge base data
        # Keys are: feed_costs, cost_templates, revenue_templates,
        # profitability_analysis, genetic_investment_roi, scale_considerations
        cost_templates = get_economics_template("cost_templates")
        ewe_costs = cost_templates.get("cost_templates", {}).get("ewe_annual_costs", {})

        revenue_templates = get_economics_template("revenue_templates")
        revenue = revenue_templates.get("revenue_templates", {})

        scale_data = get_economics_template("scale_considerations")
        scale_info = scale_data.get("scale_considerations", {}).get("flock_size_economics", {})

        # Build cost section
        components = ewe_costs.get("components", {}) if ewe_costs else {}
        cost_lines = "".join(
            _format_cost_component(comp, vals) for comp, vals in components.items()
        )

        # Add total if available
        total = ewe_costs.get("total", {}) if ewe_costs else {}
        total_line = ""
        if total:
            total_line = f"\n**Total Annual Cost**: ${total.get('average', 0)} "
            total_line += f"(range: ${total.get('low', 0)}-${total.get('high', 0)})\n"

        # Build revenue section
        revenue_lines = "".join(
            _format_revenue_item(mt, data) for mt, data in (revenue or {}).items()
        )

        # Build scale section
        scale_lines = ""
        if scale_info and flock_size in scale_info:
            info = scale_info.get(flock_size, {})
            scale_lines = f"- Size: {info.get('size', 'varies')}\n"
            scale_lines += "".join(f"- {char}\n" for char in info.get("characteristics", []))

        context = f"""
{SHEPHERD_PERSONA}

## Context

**Flock Size**: {flock_size}
**Market Focus**: {market_focus}

## Cost Templates (Annual per Ewe)

{cost_lines}{total_line}
## Revenue Potential

{revenue_lines}
## Scale Considerations: {flock_size.title()} Flock

{scale_lines}
## User Question

{question}

Please provide economic analysis and advice. Include:
1. Cost/revenue estimates relevant to the question
2. Breakeven analysis if applicable
3. Strategies to improve profitability
4. Risks and considerations
5. Market timing recommendations if relevant
"""

        _record_prompt_execution("shepherd_economics", True)
        return [
            {"role": "system", "content": {"type": "text", "text": SHEPHERD_PERSONA}},
            {"role": "user", "content": {"type": "text", "text": context}},
        ]

    except Exception as e:
        _record_prompt_execution("shepherd_economics", False)
        return [
            {
                "role": "user",
                "content": {"type": "text", "text": f"Error preparing economics advice: {str(e)}"},
            }
        ]


@mcp.prompt(
    name="shepherd_consult",
    description="General Shepherd consultation for any sheep husbandry question",
)
async def shepherd_consult_prompt(
    question: str,
    region: str = "",
) -> list[dict[str, Any]]:
    """Get general Shepherd consultation.

    Args:
        question: Any sheep husbandry question
        region: Optional region for context (auto-detected if possible)

    Returns:
        Prompt messages with comprehensive guidance
    """
    try:
        # Get all regions for reference
        all_regions = list_regions()

        # Try to get region info if provided
        region_info = None
        if region:
            region_info = get_region_info(region)

        # Build regions list for display
        # list_regions() returns list of strings like ['northeast', 'southeast', ...]
        regions_list = (
            ", ".join([r.title() for r in all_regions]) if all_regions else "Various US regions"
        )

        context = f"""
{SHEPHERD_PERSONA}

## Available Knowledge Domains

I can help with questions about:
- **Breeding**: Genetic selection, EBV interpretation, mating plans, inbreeding
- **Health & Nutrition**: Disease prevention, parasites, feeding programs
- **Calendar**: Seasonal management, lambing preparation, shearing
- **Economics**: Costs, profitability, marketing, ROI analysis

## NSIP Regions

{regions_list}

"""
        if region_info:
            context += f"""
## Your Region: {region_info.get('name', region)}

- Primary Breeds: {', '.join(region_info.get('primary_breeds', []))}
- Challenges: {', '.join(region_info.get('challenges', [])[:3])}
- Typical Lambing: {region_info.get('typical_lambing', 'Varies')}
"""

        context += f"""
## Your Question

{question}

Please provide comprehensive guidance. I'll:
1. Identify which domain(s) your question falls into
2. Provide evidence-based recommendations
3. Consider regional factors if applicable
4. Suggest next steps or additional resources
"""

        _record_prompt_execution("shepherd_consult", True)
        return [
            {"role": "system", "content": {"type": "text", "text": SHEPHERD_PERSONA}},
            {"role": "user", "content": {"type": "text", "text": context}},
        ]

    except Exception as e:
        _record_prompt_execution("shepherd_consult", False)
        return [
            {
                "role": "user",
                "content": {"type": "text", "text": f"Error preparing consultation: {str(e)}"},
            }
        ]
