"""Knowledge base module for NSIP Shepherd agent.

This module provides static knowledge data and dynamic loading for:
- Trait heritabilities by breed
- Disease prevention guides by region
- Nutrition guidelines by life stage and region
- Selection index definitions (Terminal, Maternal, Range, Hair)
- Trait glossary (codes, units, interpretations)
- NSIP regions with climate and breed information
- Seasonal calendar templates
- Economic analysis templates

Usage:
    from nsip_mcp.knowledge_base import (
        get_heritabilities,
        get_disease_guide,
        get_nutrition_guide,
        get_selection_index,
        get_trait_info,
        get_region_info,
        get_calendar_template,
        get_economics_template,
        list_regions,
    )

    # Get trait heritabilities for a breed
    herit = get_heritabilities("katahdin")

    # Get disease guide for a region
    diseases = get_disease_guide("southeast")
"""

from nsip_mcp.knowledge_base.loader import (
    get_calendar_template,
    get_disease_guide,
    get_economics_template,
    get_heritabilities,
    get_nutrition_guide,
    get_region_info,
    get_selection_index,
    get_trait_glossary,
    get_trait_info,
    list_regions,
    list_selection_indexes,
    list_traits,
)

__all__ = [
    "get_heritabilities",
    "get_disease_guide",
    "get_nutrition_guide",
    "get_selection_index",
    "get_trait_glossary",
    "get_trait_info",
    "get_region_info",
    "get_calendar_template",
    "get_economics_template",
    "list_regions",
    "list_selection_indexes",
    "list_traits",
]
