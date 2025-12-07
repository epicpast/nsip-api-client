"""NSIP region detection and context for regional adaptation.

This module provides region detection and context for adapting
Shepherd advice to specific NSIP member regions.
"""

from typing import Any, Optional

from nsip_mcp.knowledge_base import get_region_info, list_regions

# NSIP member regions with state mappings
NSIP_REGIONS = {
    "northeast": {
        "id": "northeast",
        "name": "Northeast",
        "states": ["ME", "NH", "VT", "MA", "RI", "CT", "NY", "NJ", "PA"],
        "climate": "humid continental",
        "typical_lambing": "March-April",
        "parasite_season": "May-October",
    },
    "southeast": {
        "id": "southeast",
        "name": "Southeast",
        "states": ["MD", "DE", "VA", "WV", "NC", "SC", "GA", "FL", "AL", "MS", "TN", "KY"],
        "climate": "humid subtropical",
        "typical_lambing": "January-March",
        "parasite_season": "year-round (peak spring/fall)",
    },
    "midwest": {
        "id": "midwest",
        "name": "Midwest",
        "states": ["OH", "IN", "IL", "MI", "WI", "MN", "IA", "MO", "ND", "SD", "NE", "KS"],
        "climate": "continental",
        "typical_lambing": "February-April",
        "parasite_season": "April-November",
    },
    "southwest": {
        "id": "southwest",
        "name": "Southwest",
        "states": ["TX", "OK", "AR", "LA", "AZ", "NM"],
        "climate": "semi-arid to arid",
        "typical_lambing": "December-February",
        "parasite_season": "spring (moisture dependent)",
    },
    "mountain": {
        "id": "mountain",
        "name": "Mountain West",
        "states": ["MT", "WY", "CO", "UT", "ID", "NV"],
        "climate": "semi-arid continental",
        "typical_lambing": "April-May",
        "parasite_season": "June-September",
    },
    "pacific": {
        "id": "pacific",
        "name": "Pacific",
        "states": ["WA", "OR", "CA", "AK", "HI"],
        "climate": "varied (mediterranean to temperate)",
        "typical_lambing": "January-March (varies by latitude)",
        "parasite_season": "year-round (coastal) / seasonal (inland)",
    },
}

# State to region mapping for quick lookup
_STATE_TO_REGION = {}
for region_id, data in NSIP_REGIONS.items():
    for state in data["states"]:
        _STATE_TO_REGION[state.upper()] = region_id


def detect_region(
    state: Optional[str] = None,
    zip_code: Optional[str] = None,
    flock_prefix: Optional[str] = None,
) -> Optional[str]:
    """Detect NSIP region from available information.

    Args:
        state: Two-letter state code (e.g., "OH", "TX")
        zip_code: US ZIP code (first digit indicates region)
        flock_prefix: NSIP flock prefix (some patterns indicate region)

    Returns:
        Region ID if detected, None otherwise

    Examples:
        >>> detect_region(state="OH")
        'midwest'
        >>> detect_region(zip_code="43201")
        'midwest'
    """
    # Try state first (most reliable)
    if state:
        region = _STATE_TO_REGION.get(state.upper())
        if region:
            return region

    # Try ZIP code prefix mapping
    if zip_code:
        prefix = zip_code[0] if zip_code else None
        zip_region_map = {
            "0": "northeast",  # 0xxxx - Northeast
            "1": "northeast",  # 1xxxx - Northeast
            "2": "southeast",  # 2xxxx - Mid-Atlantic/Southeast
            "3": "southeast",  # 3xxxx - Southeast
            "4": "midwest",  # 4xxxx - Midwest
            "5": "midwest",  # 5xxxx - Midwest/Plains
            "6": "midwest",  # 6xxxx - Midwest/Plains
            "7": "southwest",  # 7xxxx - Southwest
            "8": "mountain",  # 8xxxx - Mountain West
            "9": "pacific",  # 9xxxx - Pacific/West
        }
        if prefix in zip_region_map:
            return zip_region_map[prefix]

    # Could potentially infer from flock prefix patterns
    # (e.g., if certain prefix ranges are associated with regions)
    # For now, return None if no detection possible

    return None


def get_region_context(region_id: str) -> dict[str, Any]:
    """Get comprehensive context for a region.

    Combines static region data with knowledge base information
    for complete regional context.

    Args:
        region_id: Region identifier (e.g., "midwest", "pacific")

    Returns:
        Dict with region context including:
        - Basic info (name, states, climate)
        - Production characteristics
        - Health challenges
        - Seasonal timing
        - Breed recommendations
    """
    # Get base region data
    base_data = NSIP_REGIONS.get(region_id, {})

    # Get extended data from knowledge base
    kb_data = get_region_info(region_id) or {}

    # Merge data, preferring knowledge base for detailed info
    context = {
        "id": region_id,
        "name": kb_data.get("name") or base_data.get("name", region_id.title()),
        "states": base_data.get("states", []),
        "climate": kb_data.get("climate") or base_data.get("climate", "varies"),
        "typical_lambing": (
            kb_data.get("typical_lambing") or base_data.get("typical_lambing", "varies")
        ),
        "parasite_season": (
            kb_data.get("parasite_season") or base_data.get("parasite_season", "varies")
        ),
        "primary_breeds": kb_data.get("primary_breeds", []),
        "challenges": kb_data.get("challenges", []),
        "opportunities": kb_data.get("opportunities", []),
    }

    return context


def list_all_regions() -> list[dict[str, Any]]:
    """List all available NSIP regions with basic info.

    Returns:
        List of region dicts with id, name, and state count
    """
    # First try knowledge base - returns list of region IDs (strings)
    kb_region_ids = list_regions()
    if kb_region_ids:
        # Convert string IDs to full region dicts
        return [
            {
                "id": region_id,
                "name": NSIP_REGIONS.get(region_id, {}).get("name", region_id.title()),
                "states": NSIP_REGIONS.get(region_id, {}).get("states", []),
            }
            for region_id in kb_region_ids
        ]

    # Fall back to static data
    return [
        {
            "id": region_id,
            "name": data["name"],
            "states": data["states"],
        }
        for region_id, data in NSIP_REGIONS.items()
    ]


def get_regional_adaptation(
    region_id: str,
    topic: str,
) -> dict[str, Any]:
    """Get region-specific adaptations for a topic.

    Args:
        region_id: NSIP region identifier
        topic: Topic to adapt (breeding, health, calendar, economics)

    Returns:
        Dict with regional adaptations for the topic
    """
    context = get_region_context(region_id)

    adaptations = {
        "region": context["name"],
        "general_notes": [],
    }

    if topic == "breeding":
        breeds_str = ", ".join(context["primary_breeds"][:3]) or "Various"
        adaptations["general_notes"] = [
            f"Primary breeds in {context['name']}: {breeds_str}",
            f"Typical lambing season: {context['typical_lambing']}",
        ]
        adaptations["breed_recommendations"] = context.get("primary_breeds", [])

    elif topic == "health":
        adaptations["general_notes"] = [
            f"Parasite season: {context['parasite_season']}",
            f"Climate: {context['climate']}",
        ]
        adaptations["challenges"] = context.get("challenges", [])

    elif topic == "calendar":
        adaptations["general_notes"] = [
            f"Typical lambing: {context['typical_lambing']}",
            f"Climate considerations: {context['climate']}",
        ]
        adaptations["timing_adjustments"] = {
            "lambing": context["typical_lambing"],
            "parasite_management": context["parasite_season"],
        }

    elif topic == "economics":
        adaptations["general_notes"] = [
            f"Regional market characteristics vary in {context['name']}",
        ]
        adaptations["market_considerations"] = context.get("opportunities", [])

    return adaptations
