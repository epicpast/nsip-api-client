"""Static MCP resources serving knowledge base data.

This module provides URI-addressable resources for accessing static knowledge base
data including heritabilities, trait definitions, selection indexes, regions,
diseases, nutrition guides, calendar templates, and economics data.

Resource URIs:
    nsip://static/heritabilities/{breed}
    nsip://static/traits/{trait_code}
    nsip://static/traits
    nsip://static/indexes/{index_name}
    nsip://static/indexes
    nsip://static/regions/{region_id}
    nsip://static/regions
    nsip://static/diseases/{region}
    nsip://static/nutrition/{region}/{season}
    nsip://static/calendar/{task_type}
    nsip://static/economics/{category}
"""

import time
from typing import Any

from nsip_mcp.knowledge_base import (
    get_calendar_template,
    get_disease_guide,
    get_economics_template,
    get_heritabilities,
    get_nutrition_guide,
    get_region_info,
    get_selection_index,
    get_trait_info,
    list_regions,
    list_selection_indexes,
    list_traits,
)
from nsip_mcp.metrics import server_metrics
from nsip_mcp.server import mcp


def _record_resource_access(uri_pattern: str, start_time: float) -> None:
    """Record resource access metrics."""
    latency = time.time() - start_time
    server_metrics.record_resource_access(uri_pattern, latency)


@mcp.resource("nsip://static/heritabilities")
async def get_default_heritabilities() -> dict[str, Any]:
    """Get default heritability values for all traits.

    Returns:
        Dict mapping trait codes to their heritability values (0-1 scale).

    Example:
        {"BWT": 0.35, "WWT": 0.20, "PWWT": 0.25, "NLW": 0.10, ...}
    """
    start = time.time()
    result = get_heritabilities()
    _record_resource_access("nsip://static/heritabilities", start)
    return {"heritabilities": result, "breed": "default"}


@mcp.resource("nsip://static/heritabilities/{breed}")
async def get_breed_heritabilities(breed: str) -> dict[str, Any]:
    """Get heritability values for a specific breed.

    Args:
        breed: Breed name (e.g., 'suffolk', 'katahdin', 'rambouillet')

    Returns:
        Dict mapping trait codes to breed-specific heritability values.
        Falls back to defaults for traits without breed-specific data.
    """
    start = time.time()
    result = get_heritabilities(breed)
    _record_resource_access("nsip://static/heritabilities/{breed}", start)
    return {"heritabilities": result, "breed": breed}


@mcp.resource("nsip://static/traits")
async def get_all_traits() -> dict[str, Any]:
    """Get list of all available trait codes with basic info.

    Returns:
        Dict with trait codes as keys and basic trait info as values.
    """
    start = time.time()
    traits = list_traits()
    _record_resource_access("nsip://static/traits", start)
    return {"traits": traits, "count": len(traits)}


@mcp.resource("nsip://static/traits/{trait_code}")
async def get_trait_details(trait_code: str) -> dict[str, Any]:
    """Get detailed information about a specific trait.

    Args:
        trait_code: Trait code (e.g., 'BWT', 'WWT', 'PWWT', 'NLW')

    Returns:
        Dict with trait name, description, unit, interpretation, and category.
    """
    start = time.time()
    trait = get_trait_info(trait_code)
    _record_resource_access("nsip://static/traits/{trait_code}", start)
    if trait:
        return {"trait": trait, "code": trait_code}
    return {"error": f"Trait not found: {trait_code}", "code": trait_code}


@mcp.resource("nsip://static/indexes")
async def get_all_indexes() -> dict[str, Any]:
    """Get list of all available selection index names.

    Returns:
        Dict with index names and their basic descriptions.
    """
    start = time.time()
    indexes = list_selection_indexes()
    _record_resource_access("nsip://static/indexes", start)
    return {"indexes": indexes, "count": len(indexes)}


@mcp.resource("nsip://static/indexes/{index_name}")
async def get_index_details(index_name: str) -> dict[str, Any]:
    """Get detailed information about a selection index.

    Args:
        index_name: Index name (e.g., 'terminal', 'maternal', 'hair', 'balanced')

    Returns:
        Dict with index weights, description, use case, and breed focus.
    """
    start = time.time()
    index = get_selection_index(index_name)
    _record_resource_access("nsip://static/indexes/{index_name}", start)
    if index:
        return {"index": index, "name": index_name}
    return {"error": f"Index not found: {index_name}", "name": index_name}


@mcp.resource("nsip://static/regions")
async def get_all_regions() -> dict[str, Any]:
    """Get list of all NSIP member regions.

    Returns:
        Dict with region IDs and their basic info (name, states, climate).
    """
    start = time.time()
    regions = list_regions()
    _record_resource_access("nsip://static/regions", start)
    return {"regions": regions, "count": len(regions)}


@mcp.resource("nsip://static/regions/{region_id}")
async def get_region_details(region_id: str) -> dict[str, Any]:
    """Get detailed information about a specific region.

    Args:
        region_id: Region identifier (e.g., 'northeast', 'southeast', 'midwest')
            or state abbreviation (e.g., 'TX', 'OH')

    Returns:
        Dict with region name, states, climate, primary breeds, challenges,
        opportunities, and parasite season.
    """
    start = time.time()
    region = get_region_info(region_id)
    _record_resource_access("nsip://static/regions/{region_id}", start)
    if region:
        return {"region": region, "id": region_id}
    return {"error": f"Region not found: {region_id}", "id": region_id}


@mcp.resource("nsip://static/diseases/{region}")
async def get_disease_info(region: str) -> dict[str, Any]:
    """Get disease prevention guide for a specific region.

    Args:
        region: Region identifier (e.g., 'southeast', 'pacific')

    Returns:
        Dict with diseases, their risk levels, symptoms, prevention, and treatment.
    """
    start = time.time()
    diseases = get_disease_guide(region)
    _record_resource_access("nsip://static/diseases/{region}", start)
    return {"diseases": diseases, "region": region}


@mcp.resource("nsip://static/nutrition/{region}/{season}")
async def get_nutrition_info(region: str, season: str) -> dict[str, Any]:
    """Get nutrition guide for a specific region and season.

    Args:
        region: Region identifier
        season: Season (e.g., 'breeding', 'gestation', 'lactation', 'maintenance')

    Returns:
        Dict with nutrition requirements, feed recommendations, and supplements.
    """
    start = time.time()
    nutrition = get_nutrition_guide(region, season)
    _record_resource_access("nsip://static/nutrition/{region}/{season}", start)
    return {"nutrition": nutrition, "region": region, "season": season}


@mcp.resource("nsip://static/calendar/{task_type}")
async def get_calendar_info(task_type: str) -> dict[str, Any]:
    """Get calendar template for a specific task type.

    Args:
        task_type: Task type (e.g., 'breeding', 'lambing', 'shearing', 'health')

    Returns:
        Dict with task schedule, timing, priority, and detailed instructions.
    """
    start = time.time()
    calendar = get_calendar_template(task_type)
    _record_resource_access("nsip://static/calendar/{task_type}", start)
    return {"calendar": calendar, "task_type": task_type}


@mcp.resource("nsip://static/economics/{category}")
async def get_economics_info(category: str) -> dict[str, Any]:
    """Get economics template for a specific category.

    Args:
        category: Category (e.g., 'feed_costs', 'ewe_costs', 'lamb_costs', 'revenue')

    Returns:
        Dict with cost/revenue templates, ranges, and economic analysis guidance.
    """
    start = time.time()
    economics = get_economics_template(category)
    _record_resource_access("nsip://static/economics/{category}", start)
    return {"economics": economics, "category": category}
