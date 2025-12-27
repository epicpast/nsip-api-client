"""YAML knowledge base loader with LRU caching.

This module provides functions to load and cache YAML data files from the
knowledge base. All loaded files are cached using functools.lru_cache for
efficient repeated access.

The knowledge base contains:
- heritabilities.yaml: Trait heritability estimates by breed
- diseases.yaml: Disease prevention guides with regional risk levels
- nutrition.yaml: Nutrition guidelines by life stage and region
- selection_indexes.yaml: Predefined selection index weights
- trait_glossary.yaml: Trait codes, units, and interpretations
- regions.yaml: NSIP member regions with climate and breed info
- calendar_templates.yaml: Seasonal task checklists
- economics.yaml: Cost and market data templates
"""

import logging
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

# Path to knowledge base data directory
KB_DATA_PATH = Path(__file__).parent / "data"


class KnowledgeBaseError(Exception):
    """Error loading or accessing knowledge base data."""

    pass


@lru_cache(maxsize=50)
def _load_yaml_file(filename: str) -> dict[str, Any]:
    """Load and cache a YAML file from the knowledge base.

    Args:
        filename: Name of the YAML file (e.g., "heritabilities.yaml")

    Returns:
        Parsed YAML content as dictionary

    Raises:
        KnowledgeBaseError: If file not found or invalid YAML
    """
    filepath = KB_DATA_PATH / filename
    try:
        with open(filepath, encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if data is None:
                return {}
            return data
    except FileNotFoundError:
        logger.error(f"Knowledge base file not found: {filepath}")
        raise KnowledgeBaseError(f"Knowledge base file not found: {filename}") from None
    except yaml.YAMLError as e:
        logger.error(f"Invalid YAML in {filepath}: {e}")
        raise KnowledgeBaseError(f"Invalid YAML in {filename}: {e}") from e


def clear_cache() -> None:
    """Clear the knowledge base cache.

    Use this after updating YAML files to reload fresh data.
    """
    _load_yaml_file.cache_clear()


# List of all YAML files to pre-load
_PRELOAD_FILES = [
    "heritabilities.yaml",
    "diseases.yaml",
    "nutrition.yaml",
    "selection_indexes.yaml",
    "trait_glossary.yaml",
    "regions.yaml",
    "calendar_templates.yaml",
    "economics.yaml",
]


def preload_all() -> dict[str, bool]:
    """Pre-load all knowledge base files into cache.

    Call this at server startup to eliminate first-request latency.
    Files are loaded synchronously since YAML parsing is fast (<100ms total).

    Returns:
        Dict mapping filename to success status

    Example:
        >>> preload_all()
        {"heritabilities.yaml": True, "diseases.yaml": True, ...}
    """
    results = {}
    for filename in _PRELOAD_FILES:
        try:
            _load_yaml_file(filename)
            results[filename] = True
        except KnowledgeBaseError:
            results[filename] = False
            logger.warning(f"Failed to preload {filename}")
    return results


# =============================================================================
# Heritabilities
# =============================================================================


def get_heritabilities(breed: str | None = None) -> dict[str, float]:
    """Get trait heritability estimates.

    Args:
        breed: Optional breed name to get breed-specific estimates.
               If None, returns default heritabilities.

    Returns:
        Dict mapping trait codes to heritability values (0.0-1.0)

    Example:
        >>> get_heritabilities()
        {"BWT": 0.30, "WWT": 0.25, "PWWT": 0.35, ...}
        >>> get_heritabilities("katahdin")
        {"BWT": 0.30, "WWT": 0.25, "NLW": 0.12, ...}  # Breed-specific overrides
    """
    data = _load_yaml_file("heritabilities.yaml")
    default = data.get("default", {})

    if breed is None:
        return default

    # Merge breed-specific overrides with defaults
    breed_key = breed.lower().replace(" ", "_")
    breed_specific = data.get("by_breed", {}).get(breed_key, {})
    return {**default, **breed_specific}


# =============================================================================
# Disease Guides
# =============================================================================


def get_disease_guide(region: str) -> dict[str, Any]:
    """Get disease prevention guide for a region.

    Args:
        region: Region name (e.g., "southeast", "midwest")

    Returns:
        Dict with disease information filtered by regional risk:
        {
            "disease_name": {
                "description": str,
                "prevention": list[str],
                "treatment": str,
                "risk_level": str  # "low", "moderate", "high", "very_high"
            }
        }
    """
    data = _load_yaml_file("diseases.yaml")
    common = data.get("common_diseases", {})
    region_key = region.lower().replace(" ", "_")

    result = {}
    for disease_name, disease_info in common.items():
        regional_risk = disease_info.get("regional_risk", {})
        risk_level = regional_risk.get(region_key, "unknown")

        result[disease_name] = {
            "description": disease_info.get("description", ""),
            "prevention": disease_info.get("prevention", []),
            "treatment": disease_info.get("treatment", ""),
            "risk_level": risk_level,
        }

    return result


def list_diseases() -> list[str]:
    """List all diseases in the knowledge base.

    Returns:
        List of disease names
    """
    data = _load_yaml_file("diseases.yaml")
    return list(data.get("common_diseases", {}).keys())


# =============================================================================
# Nutrition Guides
# =============================================================================


def get_nutrition_guide(region: str | None = None, season: str | None = None) -> dict[str, Any]:
    """Get nutrition guidelines.

    Args:
        region: Optional region for regional considerations
        season: Optional season (e.g., "summer", "winter")

    Returns:
        Dict with life stage nutrition and optional regional/seasonal info
    """
    data = _load_yaml_file("nutrition.yaml")
    result = {
        "life_stages": data.get("life_stages", {}),
    }

    if region:
        region_key = region.lower().replace(" ", "_")
        regional = data.get("regional_considerations", {}).get(region_key, {})
        result["regional_considerations"] = regional

    if season:
        season_key = season.lower()
        seasonal = data.get("seasonal_adjustments", {}).get(season_key, {})
        result["seasonal_adjustments"] = seasonal

    return result


# =============================================================================
# Selection Indexes
# =============================================================================


def get_selection_index(index_name: str) -> dict[str, Any]:
    """Get a predefined selection index definition.

    Args:
        index_name: Name of the index (e.g., "terminal", "maternal", "range", "hair")

    Returns:
        Dict with index definition:
        {
            "name": str,
            "description": str,
            "weights": {"trait_code": weight, ...},
            "use_case": str
        }

    Raises:
        KnowledgeBaseError: If index not found
    """
    data = _load_yaml_file("selection_indexes.yaml")
    indexes = data.get("indexes", {})
    index_key = index_name.lower().replace(" ", "_")

    if index_key not in indexes:
        available = list(indexes.keys())
        raise KnowledgeBaseError(
            f"Selection index '{index_name}' not found. Available: {available}"
        )

    return indexes[index_key]


def list_selection_indexes() -> list[str]:
    """List all available selection indexes.

    Returns:
        List of index names
    """
    data = _load_yaml_file("selection_indexes.yaml")
    return list(data.get("indexes", {}).keys())


# =============================================================================
# Trait Glossary
# =============================================================================


def get_trait_info(trait_code: str) -> dict[str, Any]:
    """Get information about a trait.

    Args:
        trait_code: Trait abbreviation (e.g., "WWT", "NLW", "YEMD")

    Returns:
        Dict with trait information:
        {
            "name": str,
            "description": str,
            "unit": str,
            "interpretation": str,  # "higher_better" or "lower_better"
            "category": str  # "growth", "maternal", "carcass", "health"
        }

    Raises:
        KnowledgeBaseError: If trait not found
    """
    data = _load_yaml_file("trait_glossary.yaml")
    traits = data.get("traits", {})
    trait_key = trait_code.upper()

    if trait_key not in traits:
        available = list(traits.keys())
        raise KnowledgeBaseError(f"Trait '{trait_code}' not found. Available: {available}")

    return traits[trait_key]


def list_traits() -> list[str]:
    """List all trait codes in the glossary.

    Returns:
        List of trait codes
    """
    data = _load_yaml_file("trait_glossary.yaml")
    return list(data.get("traits", {}).keys())


def get_trait_glossary() -> dict[str, Any]:
    """Get the complete trait glossary.

    Returns:
        Dict mapping trait codes to their information:
        {
            "WWT": {"name": "Weaning Weight", "description": ..., ...},
            "NLW": {"name": "Number Lambs Weaned", ...},
            ...
        }
    """
    data = _load_yaml_file("trait_glossary.yaml")
    return data.get("traits", {})


# =============================================================================
# Regions
# =============================================================================


def get_region_info(region: str) -> dict[str, Any]:
    """Get information about a region.

    Args:
        region: Region name (e.g., "southeast", "midwest", "mountain")

    Returns:
        Dict with region information:
        {
            "name": str,
            "states": list[str],
            "climate": str,
            "primary_breeds": list[str],
            "lambing_season": str,
            "challenges": list[str]
        }

    Raises:
        KnowledgeBaseError: If region not found
    """
    data = _load_yaml_file("regions.yaml")
    regions = data.get("regions", {})
    region_key = region.lower().replace(" ", "_")

    if region_key not in regions:
        available = list(regions.keys())
        raise KnowledgeBaseError(f"Region '{region}' not found. Available: {available}")

    return regions[region_key]


def list_regions() -> list[str]:
    """List all NSIP member regions.

    Returns:
        List of region names
    """
    data = _load_yaml_file("regions.yaml")
    return list(data.get("regions", {}).keys())


def detect_region_from_state(state: str) -> str | None:
    """Detect region from a US state abbreviation.

    Args:
        state: Two-letter state abbreviation (e.g., "TX", "NY")

    Returns:
        Region name if found, None otherwise
    """
    data = _load_yaml_file("regions.yaml")
    state_upper = state.upper()

    for region_name, region_info in data.get("regions", {}).items():
        if state_upper in region_info.get("states", []):
            return region_name

    return None


# =============================================================================
# Calendar Templates
# =============================================================================


def get_calendar_template(region: str | None = None) -> dict[str, Any]:
    """Get seasonal calendar template.

    Args:
        region: Optional region for regional calendar adjustments

    Returns:
        Dict with monthly/seasonal tasks organized by category
    """
    data = _load_yaml_file("calendar_templates.yaml")
    result = {
        "general": data.get("general", {}),
    }

    if region:
        region_key = region.lower().replace(" ", "_")
        regional = data.get("regional_adjustments", {}).get(region_key, {})
        result["regional"] = regional

    return result


# =============================================================================
# Economics
# =============================================================================


def get_economics_template(category: str | None = None) -> dict[str, Any]:
    """Get economics data templates.

    Args:
        category: Optional category filter (e.g., "feed_costs", "market_data")

    Returns:
        Dict with economic data templates and calculation guidance
    """
    data = _load_yaml_file("economics.yaml")

    if category:
        category_key = category.lower().replace(" ", "_")
        if category_key in data:
            return {category_key: data[category_key]}
        raise KnowledgeBaseError(
            f"Economics category '{category}' not found. Available: {list(data.keys())}"
        )

    return data
