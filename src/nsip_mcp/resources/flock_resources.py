"""Dynamic MCP resources for flock-level data and reports.

This module provides URI-addressable resources for accessing flock-level
aggregated data and reports.

Resource URIs:
    nsip://flock/search                    - Search for animals in a flock
    nsip://flock/{flock_id}/summary        - Flock summary statistics
    nsip://flock/{flock_id}/ebv_averages   - Average EBVs across flock

Note:
    Flock ID is typically the first 4-5 digits of the LPN ID, representing
    the flock/farm identifier assigned by NSIP.
"""

import time
from typing import Any

from nsip_client.exceptions import NSIPAPIError
from nsip_mcp.cache import response_cache
from nsip_mcp.metrics import server_metrics
from nsip_mcp.server import mcp
from nsip_mcp.tools import get_nsip_client


def _record_resource_access(uri_pattern: str, start_time: float) -> None:
    """Record resource access metrics."""
    latency = time.time() - start_time
    server_metrics.record_resource_access(uri_pattern, latency)


@mcp.resource("nsip://flock/search")
async def search_flock_animals() -> dict[str, Any]:
    """Search for animals - provides search guidance.

    Returns:
        Dict with information about how to search for animals using
        the nsip_search_animals tool or more specific URIs.

    Note:
        This resource provides guidance. For actual searches, use the
        nsip_search_animals MCP tool with specific parameters.
    """
    start = time.time()
    _record_resource_access("nsip://flock/search", start)

    return {
        "message": "Use nsip_search_animals tool for flock searches",
        "parameters": {
            "breed_group": (
                "Filter by breed group (61=Range, 62=Maternal Wool, 64=Hair, 69=Terminal)"
            ),
            "lpn_id": "Search by LPN ID or partial flock prefix",
            "name": "Search by animal name",
            "status": "Filter by status (e.g., 'A' for active)",
            "sex": "Filter by sex ('M' or 'F')",
        },
        "examples": [
            "nsip_search_animals(lpn_id='6332') - Search flock 6332",
            "nsip_search_animals(breed_group=64, sex='M') - Hair sheep rams",
        ],
    }


@mcp.resource("nsip://flock/{flock_id}/summary")
async def get_flock_summary(flock_id: str) -> dict[str, Any]:
    """Get summary statistics for a flock.

    Args:
        flock_id: Flock identifier (typically 4-5 digit prefix of LPN)

    Returns:
        Dict containing:
        - Total animal count
        - Breakdown by sex
        - Breakdown by status
        - Birth year distribution

    Example:
        Resource URI: nsip://flock/6332/summary
    """
    start = time.time()

    try:
        client = get_nsip_client()

        # Search for animals with this flock prefix
        cache_key = response_cache.make_key("search_animals_flock", flock_id=flock_id)
        cached_result = response_cache.get(cache_key)

        if cached_result is not None:
            server_metrics.record_cache_hit()
            animals = cached_result
        else:
            server_metrics.record_cache_miss()
            # API limitation: NSIP Search API does not support LPN prefix filtering
            # server-side. We must fetch and filter client-side. This is documented
            # in REMEDIATION_TASKS.md as a known limitation.
            search_result = client.search_animals(page_size=100)
            # Filter client-side by flock prefix (API doesn't support server-side)
            if search_result and search_result.results:
                animals = [
                    a
                    for a in search_result.results
                    if isinstance(a, dict)
                    and (a.get("lpn_id") or a.get("LpnId") or "").startswith(flock_id)
                ][:100]  # Limit to 100 for performance
            else:
                animals = []
            response_cache.set(cache_key, animals)

        if not animals:
            _record_resource_access("nsip://flock/{flock_id}/summary", start)
            return {
                "error": f"No animals found for flock: {flock_id}",
                "flock_id": flock_id,
            }

        # Calculate summary statistics
        total = len(animals)

        # Sex breakdown
        males = sum(1 for a in animals if a.get("sex") == "M")
        females = sum(1 for a in animals if a.get("sex") == "F")

        # Status breakdown
        status_counts: dict[str, int] = {}
        for animal in animals:
            status = animal.get("status", "Unknown")
            status_counts[status] = status_counts.get(status, 0) + 1

        # Birth year distribution
        birth_years: dict[str, int] = {}
        for animal in animals:
            birth_date = animal.get("birth_date") or animal.get("birthDate")
            if birth_date:
                year = birth_date[:4] if isinstance(birth_date, str) else str(birth_date.year)
                birth_years[year] = birth_years.get(year, 0) + 1

        _record_resource_access("nsip://flock/{flock_id}/summary", start)

        return {
            "summary": {
                "total_animals": total,
                "sex_breakdown": {"males": males, "females": females},
                "status_breakdown": status_counts,
                "birth_years": dict(sorted(birth_years.items(), reverse=True)),
            },
            "flock_id": flock_id,
        }

    except NSIPAPIError as e:
        _record_resource_access("nsip://flock/{flock_id}/summary", start)
        return {"error": f"API error: {str(e)}", "flock_id": flock_id}


@mcp.resource("nsip://flock/{flock_id}/ebv_averages")
async def get_flock_ebv_averages(flock_id: str) -> dict[str, Any]:
    """Get average EBVs across all animals in a flock.

    Args:
        flock_id: Flock identifier (typically 4-5 digit prefix of LPN)

    Returns:
        Dict containing:
        - Average EBV for each trait
        - Min/max range for each trait
        - Sample size (animals with data for each trait)

    Example:
        Resource URI: nsip://flock/6332/ebv_averages
    """
    start = time.time()

    try:
        client = get_nsip_client()

        # Search for animals with this flock prefix
        cache_key = response_cache.make_key("search_animals_flock", flock_id=flock_id)
        cached_result = response_cache.get(cache_key)

        if cached_result is not None:
            server_metrics.record_cache_hit()
            animals = cached_result
        else:
            server_metrics.record_cache_miss()
            # API limitation: LPN prefix must be filtered client-side (see above)
            search_result = client.search_animals(page_size=100)
            if search_result and search_result.results:
                animals = [
                    a
                    for a in search_result.results
                    if isinstance(a, dict)
                    and (a.get("lpn_id") or a.get("LpnId") or "").startswith(flock_id)
                ][:100]
            else:
                animals = []
            response_cache.set(cache_key, animals)

        if not animals:
            _record_resource_access("nsip://flock/{flock_id}/ebv_averages", start)
            return {
                "error": f"No animals found for flock: {flock_id}",
                "flock_id": flock_id,
            }

        # Collect EBV data for each trait
        trait_data: dict[str, list[float]] = {}

        for animal in animals:
            ebvs = animal.get("ebvs", {})
            if not ebvs:
                continue

            for trait, value in ebvs.items():
                if value is not None and isinstance(value, (int, float)):
                    if trait not in trait_data:
                        trait_data[trait] = []
                    trait_data[trait].append(float(value))

        # Calculate statistics for each trait
        ebv_stats = {}
        for trait, values in trait_data.items():
            if values:
                ebv_stats[trait] = {
                    "average": round(sum(values) / len(values), 3),
                    "min": round(min(values), 3),
                    "max": round(max(values), 3),
                    "count": len(values),
                }

        _record_resource_access("nsip://flock/{flock_id}/ebv_averages", start)

        return {
            "ebv_averages": ebv_stats,
            "flock_id": flock_id,
            "total_animals": len(animals),
            "traits_measured": list(ebv_stats.keys()),
        }

    except NSIPAPIError as e:
        _record_resource_access("nsip://flock/{flock_id}/ebv_averages", start)
        return {"error": f"API error: {str(e)}", "flock_id": flock_id}
