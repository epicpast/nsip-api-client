"""Dynamic MCP resources for breeding pair analysis.

This module provides URI-addressable resources for analyzing potential breeding
pairs, including projected offspring EBVs, inbreeding coefficients, and
mating recommendations.

Resource URIs:
    nsip://breeding/{ram_lpn}/{ewe_lpn}/projection      - Projected offspring EBVs
    nsip://breeding/{ram_lpn}/{ewe_lpn}/inbreeding      - Projected inbreeding coefficient
    nsip://breeding/{ram_lpn}/{ewe_lpn}/recommendation  - Mating recommendation
"""

import time
from typing import Any

from nsip_client.exceptions import NSIPAPIError, NSIPNotFoundError
from nsip_mcp.cache import response_cache
from nsip_mcp.knowledge_base import get_heritabilities
from nsip_mcp.metrics import server_metrics
from nsip_mcp.server import mcp
from nsip_mcp.tools import get_nsip_client


def _record_resource_access(uri_pattern: str, start_time: float) -> None:
    """Record resource access metrics."""
    latency = time.time() - start_time
    server_metrics.record_resource_access(uri_pattern, latency)


def _get_animal_ebvs(client, lpn_id: str) -> dict[str, float] | None:
    """Get EBVs for an animal, using cache."""
    cache_key = response_cache.make_key("get_animal_details", lpn_id=lpn_id)

    cached_result = response_cache.get(cache_key)
    if cached_result is not None:
        server_metrics.record_cache_hit()
        return cached_result.get("ebvs", {}) if isinstance(cached_result, dict) else None

    server_metrics.record_cache_miss()
    animal = client.get_animal_details(search_string=lpn_id)
    if animal:
        result = animal.to_dict()
        response_cache.set(cache_key, result)
        return result.get("ebvs", {})
    return None


def _project_offspring_ebv(sire_ebv: float | None, dam_ebv: float | None) -> float | None:
    """Project offspring EBV as average of parents.

    The expected breeding value of offspring is the average of the parents'
    breeding values, as each parent contributes half of their genetic merit.
    """
    if sire_ebv is None and dam_ebv is None:
        return None
    if sire_ebv is None:
        return dam_ebv
    if dam_ebv is None:
        return sire_ebv
    return (sire_ebv + dam_ebv) / 2


def _analyze_trait_strengths(projected_ebvs: dict) -> list[str]:
    """Analyze projected EBVs for breeding strengths."""
    strengths = []
    if projected_ebvs.get("PWWT", 0) > 5:
        strengths.append("Strong post-weaning growth potential")
    if projected_ebvs.get("WWT", 0) > 3:
        strengths.append("Good weaning weight genetics")
    if projected_ebvs.get("NLW", 0) > 0.1:
        strengths.append("Above-average lamb survival genetics")
    bwt = projected_ebvs.get("BWT", 0)
    if bwt < -0.5:
        strengths.append("Lower birth weight reduces lambing difficulty")
    return strengths


def _analyze_trait_concerns(projected_ebvs: dict, f_coefficient: float) -> list[str]:
    """Analyze projected EBVs and inbreeding for concerns."""
    concerns = []
    bwt = projected_ebvs.get("BWT", 0)
    if bwt > 1.5:
        concerns.append("Higher birth weight may increase dystocia risk")
    if f_coefficient > 0.0625:
        concerns.append(f"High inbreeding ({f_coefficient*100:.1f}%) - consider alternatives")
    elif f_coefficient > 0.03:
        concerns.append(f"Moderate inbreeding ({f_coefficient*100:.1f}%) - monitor carefully")
    return concerns


def _determine_recommendation(f_coefficient: float, strengths: list, concerns: list) -> tuple:
    """Determine overall breeding recommendation and summary."""
    if f_coefficient > 0.0625:
        return "avoid", "High inbreeding risk outweighs genetic benefits. Choose a different ram."
    if len(concerns) > len(strengths):
        return "caution", "Some concerns exist. Weigh benefits against risks for your goals."
    return "proceed", "Good genetic match. Mating should produce quality offspring."


def _find_common_ancestors(lineage1: dict, lineage2: dict, depth: int = 4) -> list[str]:
    """Find common ancestors in two lineage trees.

    Returns list of LPN IDs that appear in both lineages.
    """

    def extract_ancestors(lineage: dict, current_depth: int = 0) -> set[str]:
        if not lineage or current_depth >= depth:
            return set()

        ancestors = set()
        for key in ["sire", "dam"]:
            parent = lineage.get(key)
            if parent and isinstance(parent, dict):
                lpn = parent.get("lpn_id") or parent.get("lpnId")
                if lpn:
                    ancestors.add(lpn)
                ancestors.update(extract_ancestors(parent, current_depth + 1))
        return ancestors

    ancestors1 = extract_ancestors(lineage1)
    ancestors2 = extract_ancestors(lineage2)

    return list(ancestors1 & ancestors2)


def _estimate_inbreeding(common_ancestors: list, generations: int = 4) -> float:
    """Estimate inbreeding coefficient from common ancestors.

    Uses simplified Wright's coefficient calculation.
    F = sum((1/2)^(n1+n2+1)) for each common ancestor path.

    This is an approximation; accurate calculation requires full pedigree analysis.
    """
    if not common_ancestors:
        return 0.0

    # Simplified estimation: each common ancestor in recent generations
    # contributes roughly (0.5)^4 = 0.0625 to inbreeding
    # This is a rough approximation for demonstration
    estimated_f = len(common_ancestors) * 0.0625
    return min(estimated_f, 0.25)  # Cap at 25% for reasonable range


@mcp.resource("nsip://breeding/{ram_lpn}/{ewe_lpn}/projection")
async def get_breeding_projection(ram_lpn: str, ewe_lpn: str) -> dict[str, Any]:
    """Project offspring EBVs from a potential mating.

    Args:
        ram_lpn: LPN ID of the ram (sire)
        ewe_lpn: LPN ID of the ewe (dam)

    Returns:
        Dict containing:
        - Projected EBVs for offspring (average of parents)
        - Parent EBVs for comparison
        - Heritabilities affecting selection response

    Example:
        Resource URI: nsip://breeding/633292020054249/644312019012345/projection
    """
    start = time.time()

    try:
        client = get_nsip_client()

        # Get EBVs for both parents
        ram_ebvs = _get_animal_ebvs(client, ram_lpn)
        ewe_ebvs = _get_animal_ebvs(client, ewe_lpn)

        if ram_ebvs is None:
            _record_resource_access("nsip://breeding/{ram}/{ewe}/projection", start)
            return {"error": f"Ram not found: {ram_lpn}", "ram_lpn": ram_lpn, "ewe_lpn": ewe_lpn}

        if ewe_ebvs is None:
            _record_resource_access("nsip://breeding/{ram}/{ewe}/projection", start)
            return {"error": f"Ewe not found: {ewe_lpn}", "ram_lpn": ram_lpn, "ewe_lpn": ewe_lpn}

        # Project offspring EBVs
        projected = {}
        all_traits = set(ram_ebvs.keys()) | set(ewe_ebvs.keys())
        heritabilities = get_heritabilities()

        for trait in all_traits:
            ram_val = ram_ebvs.get(trait)
            ewe_val = ewe_ebvs.get(trait)
            projected_val = _project_offspring_ebv(ram_val, ewe_val)
            if projected_val is not None:
                projected[trait] = {
                    "value": round(projected_val, 2),
                    "sire_contribution": ram_val,
                    "dam_contribution": ewe_val,
                    "heritability": heritabilities.get(trait, 0.25),
                }

        _record_resource_access("nsip://breeding/{ram}/{ewe}/projection", start)

        return {
            "projection": {
                "offspring_ebvs": projected,
                "sire": {"lpn_id": ram_lpn, "ebvs": ram_ebvs},
                "dam": {"lpn_id": ewe_lpn, "ebvs": ewe_ebvs},
            },
            "ram_lpn": ram_lpn,
            "ewe_lpn": ewe_lpn,
        }

    except NSIPNotFoundError as e:
        _record_resource_access("nsip://breeding/{ram}/{ewe}/projection", start)
        return {"error": str(e), "ram_lpn": ram_lpn, "ewe_lpn": ewe_lpn}
    except NSIPAPIError as e:
        _record_resource_access("nsip://breeding/{ram}/{ewe}/projection", start)
        return {"error": f"API error: {str(e)}", "ram_lpn": ram_lpn, "ewe_lpn": ewe_lpn}


@mcp.resource("nsip://breeding/{ram_lpn}/{ewe_lpn}/inbreeding")
async def get_breeding_inbreeding(ram_lpn: str, ewe_lpn: str) -> dict[str, Any]:
    """Calculate projected inbreeding coefficient for offspring.

    Args:
        ram_lpn: LPN ID of the ram (sire)
        ewe_lpn: LPN ID of the ewe (dam)

    Returns:
        Dict containing:
        - Projected inbreeding coefficient (F)
        - Common ancestors found
        - Risk assessment (low/moderate/high)
        - Recommendations if inbreeding is concerning

    Example:
        Resource URI: nsip://breeding/633292020054249/644312019012345/inbreeding
    """
    start = time.time()

    try:
        client = get_nsip_client()

        # Get lineage for both parents
        ram_lineage = client.get_lineage(lpn_id=ram_lpn)
        ewe_lineage = client.get_lineage(lpn_id=ewe_lpn)

        if not ram_lineage:
            _record_resource_access("nsip://breeding/{ram}/{ewe}/inbreeding", start)
            return {"error": f"Ram lineage not found: {ram_lpn}"}

        if not ewe_lineage:
            _record_resource_access("nsip://breeding/{ram}/{ewe}/inbreeding", start)
            return {"error": f"Ewe lineage not found: {ewe_lpn}"}

        ram_lineage_dict = ram_lineage.to_dict()
        ewe_lineage_dict = ewe_lineage.to_dict()

        # Find common ancestors
        common_ancestors = _find_common_ancestors(ram_lineage_dict, ewe_lineage_dict)

        # Estimate inbreeding coefficient
        f_coefficient = _estimate_inbreeding(common_ancestors)

        # Assess risk level
        if f_coefficient < 0.03:
            risk_level = "low"
            recommendation = "Acceptable mating. No significant inbreeding concerns."
        elif f_coefficient < 0.0625:
            risk_level = "moderate"
            recommendation = "Consider alternatives. Moderate inbreeding may reduce vigor."
        else:
            risk_level = "high"
            recommendation = "Avoid this mating. High inbreeding risk for offspring health."

        _record_resource_access("nsip://breeding/{ram}/{ewe}/inbreeding", start)

        return {
            "inbreeding": {
                "coefficient": round(f_coefficient, 4),
                "percentage": round(f_coefficient * 100, 2),
                "common_ancestors": common_ancestors,
                "common_ancestor_count": len(common_ancestors),
                "risk_level": risk_level,
                "recommendation": recommendation,
            },
            "ram_lpn": ram_lpn,
            "ewe_lpn": ewe_lpn,
        }

    except NSIPNotFoundError as e:
        _record_resource_access("nsip://breeding/{ram}/{ewe}/inbreeding", start)
        return {"error": str(e), "ram_lpn": ram_lpn, "ewe_lpn": ewe_lpn}
    except NSIPAPIError as e:
        _record_resource_access("nsip://breeding/{ram}/{ewe}/inbreeding", start)
        return {"error": f"API error: {str(e)}", "ram_lpn": ram_lpn, "ewe_lpn": ewe_lpn}


@mcp.resource("nsip://breeding/{ram_lpn}/{ewe_lpn}/recommendation")
async def get_breeding_recommendation(ram_lpn: str, ewe_lpn: str) -> dict[str, Any]:
    """Get comprehensive mating recommendation for a breeding pair.

    Args:
        ram_lpn: LPN ID of the ram (sire)
        ewe_lpn: LPN ID of the ewe (dam)

    Returns:
        Dict containing:
        - Overall recommendation (proceed/caution/avoid)
        - Projected offspring EBVs summary
        - Inbreeding assessment
        - Strengths and concerns
        - Suggested alternatives if mating is not recommended

    Example:
        Resource URI: nsip://breeding/633292020054249/644312019012345/recommendation
    """
    start = time.time()

    try:
        client = get_nsip_client()

        # Get all data we need
        ram_ebvs = _get_animal_ebvs(client, ram_lpn)
        ewe_ebvs = _get_animal_ebvs(client, ewe_lpn)

        if ram_ebvs is None or ewe_ebvs is None:
            _record_resource_access("nsip://breeding/{ram}/{ewe}/recommendation", start)
            missing = ram_lpn if ram_ebvs is None else ewe_lpn
            return {"error": f"Animal not found: {missing}"}

        ram_lineage = client.get_lineage(lpn_id=ram_lpn)
        ewe_lineage = client.get_lineage(lpn_id=ewe_lpn)

        # Calculate inbreeding
        common_ancestors = []
        f_coefficient = 0.0
        if ram_lineage and ewe_lineage:
            common_ancestors = _find_common_ancestors(ram_lineage.to_dict(), ewe_lineage.to_dict())
            f_coefficient = _estimate_inbreeding(common_ancestors)

        # Project key EBVs
        key_traits = ["BWT", "WWT", "PWWT", "NLW", "MWWT"]
        projected_ebvs = {}
        for trait in key_traits:
            ram_val = ram_ebvs.get(trait)
            ewe_val = ewe_ebvs.get(trait)
            projected = _project_offspring_ebv(ram_val, ewe_val)
            if projected is not None:
                projected_ebvs[trait] = round(projected, 2)

        # Analyze strengths and concerns using helper functions
        strengths = _analyze_trait_strengths(projected_ebvs)
        concerns = _analyze_trait_concerns(projected_ebvs, f_coefficient)

        # Determine overall recommendation
        recommendation, summary = _determine_recommendation(f_coefficient, strengths, concerns)

        _record_resource_access("nsip://breeding/{ram}/{ewe}/recommendation", start)

        return {
            "recommendation": {
                "decision": recommendation,
                "summary": summary,
                "projected_ebvs": projected_ebvs,
                "inbreeding_coefficient": round(f_coefficient, 4),
                "strengths": strengths,
                "concerns": concerns,
            },
            "ram_lpn": ram_lpn,
            "ewe_lpn": ewe_lpn,
        }

    except NSIPNotFoundError as e:
        _record_resource_access("nsip://breeding/{ram}/{ewe}/recommendation", start)
        return {"error": str(e), "ram_lpn": ram_lpn, "ewe_lpn": ewe_lpn}
    except NSIPAPIError as e:
        _record_resource_access("nsip://breeding/{ram}/{ewe}/recommendation", start)
        return {"error": f"API error: {str(e)}", "ram_lpn": ram_lpn, "ewe_lpn": ewe_lpn}
