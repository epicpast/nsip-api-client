"""Dynamic MCP resources for NSIP animal data.

This module provides URI-addressable resources for accessing animal data from
the NSIP API, including animal details, lineage/pedigree, progeny, and
combined profiles.

Resource URIs:
    nsip://animals/{lpn_id}/details   - Full animal details
    nsip://animals/{lpn_id}/lineage   - Pedigree tree (ancestors)
    nsip://animals/{lpn_id}/progeny   - Offspring list
    nsip://animals/{lpn_id}/profile   - Combined profile (details + lineage + progeny)
"""

import time
from typing import Any

from nsip_client.exceptions import NSIPAPIError, NSIPNotFoundError
from nsip_mcp.cache import response_cache
from nsip_mcp.metrics import server_metrics
from nsip_mcp.server import mcp
from nsip_mcp.tools import get_nsip_client


def _record_resource_access(uri_pattern: str, start_time: float) -> None:
    """Record resource access metrics."""
    latency = time.time() - start_time
    server_metrics.record_resource_access(uri_pattern, latency)


def _cached_api_call(method_name: str, lpn_id: str, api_call):
    """Execute API call with caching."""
    cache_key = response_cache.make_key(method_name, lpn_id=lpn_id)

    cached_result = response_cache.get(cache_key)
    if cached_result is not None:
        server_metrics.record_cache_hit()
        return cached_result

    server_metrics.record_cache_miss()
    result = api_call()
    response_cache.set(cache_key, result)
    return result


@mcp.resource("nsip://animals/{lpn_id}/details")
async def get_animal_details_resource(lpn_id: str) -> dict[str, Any]:
    """Get full details for an animal by LPN ID.

    Args:
        lpn_id: Lifetime Performance Number (e.g., '633292020054249')

    Returns:
        Dict containing animal details including:
        - Basic info (name, sex, birth date, status)
        - Breed information
        - EBV data for all measured traits
        - Accuracy percentages for EBVs

    Example:
        Resource URI: nsip://animals/633292020054249/details
    """
    start = time.time()

    try:
        client = get_nsip_client()

        def api_call():
            animal = client.get_animal_details(search_string=lpn_id)
            if animal:
                return animal.to_dict()
            return None

        result = _cached_api_call("get_animal_details", lpn_id, api_call)

        _record_resource_access("nsip://animals/{lpn_id}/details", start)

        if result:
            return {"animal": result, "lpn_id": lpn_id}
        return {"error": f"Animal not found: {lpn_id}", "lpn_id": lpn_id}

    except NSIPNotFoundError:
        _record_resource_access("nsip://animals/{lpn_id}/details", start)
        return {"error": f"Animal not found: {lpn_id}", "lpn_id": lpn_id}
    except NSIPAPIError as e:
        _record_resource_access("nsip://animals/{lpn_id}/details", start)
        return {"error": f"API error: {str(e)}", "lpn_id": lpn_id}


@mcp.resource("nsip://animals/{lpn_id}/lineage")
async def get_animal_lineage_resource(lpn_id: str) -> dict[str, Any]:
    """Get pedigree/lineage tree for an animal.

    Args:
        lpn_id: Lifetime Performance Number

    Returns:
        Dict containing pedigree information:
        - Sire (father) and dam (mother)
        - Grandparents (paternal and maternal)
        - Great-grandparents when available
        - Inbreeding coefficient if calculable

    Example:
        Resource URI: nsip://animals/633292020054249/lineage
    """
    start = time.time()

    try:
        client = get_nsip_client()

        def api_call():
            lineage = client.get_lineage(lpn_id=lpn_id)
            if lineage:
                return lineage.to_dict()
            return None

        result = _cached_api_call("get_lineage", lpn_id, api_call)

        _record_resource_access("nsip://animals/{lpn_id}/lineage", start)

        if result:
            return {"lineage": result, "lpn_id": lpn_id}
        return {"error": f"Lineage not found: {lpn_id}", "lpn_id": lpn_id}

    except NSIPNotFoundError:
        _record_resource_access("nsip://animals/{lpn_id}/lineage", start)
        return {"error": f"Animal not found: {lpn_id}", "lpn_id": lpn_id}
    except NSIPAPIError as e:
        _record_resource_access("nsip://animals/{lpn_id}/lineage", start)
        return {"error": f"API error: {str(e)}", "lpn_id": lpn_id}


@mcp.resource("nsip://animals/{lpn_id}/progeny")
async def get_animal_progeny_resource(lpn_id: str) -> dict[str, Any]:
    """Get list of offspring for an animal.

    Args:
        lpn_id: Lifetime Performance Number (typically for rams/sires)

    Returns:
        Dict containing:
        - List of progeny with their LPN IDs, names, and basic EBVs
        - Total count of offspring
        - Gender breakdown (ram lambs vs ewe lambs)

    Example:
        Resource URI: nsip://animals/633292020054249/progeny
    """
    start = time.time()

    try:
        client = get_nsip_client()

        def api_call():
            progeny = client.get_progeny(lpn_id=lpn_id)
            if progeny and progeny.animals:
                return [p.to_dict() for p in progeny.animals]
            return []

        result = _cached_api_call("get_progeny", lpn_id, api_call)

        _record_resource_access("nsip://animals/{lpn_id}/progeny", start)

        return {
            "progeny": result,
            "lpn_id": lpn_id,
            "count": len(result) if result else 0,
        }

    except NSIPNotFoundError:
        _record_resource_access("nsip://animals/{lpn_id}/progeny", start)
        return {"error": f"Animal not found: {lpn_id}", "lpn_id": lpn_id}
    except NSIPAPIError as e:
        _record_resource_access("nsip://animals/{lpn_id}/progeny", start)
        return {"error": f"API error: {str(e)}", "lpn_id": lpn_id}


@mcp.resource("nsip://animals/{lpn_id}/profile")
async def get_animal_profile_resource(lpn_id: str) -> dict[str, Any]:
    """Get complete profile for an animal (details + lineage + progeny).

    Args:
        lpn_id: Lifetime Performance Number

    Returns:
        Dict containing:
        - Full animal details
        - Complete pedigree/lineage
        - All known progeny
        - Combined statistics

    Note:
        This is a convenience resource that combines three API calls.
        For performance-critical applications, prefer individual resources.

    Example:
        Resource URI: nsip://animals/633292020054249/profile
    """
    start = time.time()

    try:
        client = get_nsip_client()

        # Get details
        def details_call():
            animal = client.get_animal_details(search_string=lpn_id)
            return animal.to_dict() if animal else None

        details = _cached_api_call("get_animal_details", lpn_id, details_call)

        # Get lineage
        def lineage_call():
            lineage = client.get_lineage(lpn_id=lpn_id)
            return lineage.to_dict() if lineage else None

        lineage = _cached_api_call("get_lineage", lpn_id, lineage_call)

        # Get progeny
        def progeny_call():
            progeny = client.get_progeny(lpn_id=lpn_id)
            return [p.to_dict() for p in progeny.animals] if progeny and progeny.animals else []

        progeny = _cached_api_call("get_progeny", lpn_id, progeny_call)

        _record_resource_access("nsip://animals/{lpn_id}/profile", start)

        if not details:
            return {"error": f"Animal not found: {lpn_id}", "lpn_id": lpn_id}

        return {
            "profile": {
                "details": details,
                "lineage": lineage,
                "progeny": progeny,
                "progeny_count": len(progeny) if progeny else 0,
            },
            "lpn_id": lpn_id,
        }

    except NSIPNotFoundError:
        _record_resource_access("nsip://animals/{lpn_id}/profile", start)
        return {"error": f"Animal not found: {lpn_id}", "lpn_id": lpn_id}
    except NSIPAPIError as e:
        _record_resource_access("nsip://animals/{lpn_id}/profile", start)
        return {"error": f"API error: {str(e)}", "lpn_id": lpn_id}
