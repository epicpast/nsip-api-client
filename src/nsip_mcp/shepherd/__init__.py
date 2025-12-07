"""Shepherd Agent for comprehensive sheep husbandry guidance.

This module provides an AI-powered advisor for sheep breeding operations,
combining NSIP data with static knowledge and LLM-generated recommendations.

The Shepherd agent covers four domains:
1. Breeding - Genetic interpretation, mating advice, inbreeding management
2. Health - Disease prevention, parasites, nutrition, body condition
3. Calendar - Seasonal planning, lambing, shearing, marketing
4. Economics - Costs, ROI, market timing, profitability

The agent uses a neutral expert persona (veterinarian-like) and provides
evidence-based recommendations with proper uncertainty acknowledgment.
"""

from nsip_mcp.shepherd.agent import ShepherdAgent
from nsip_mcp.shepherd.persona import ShepherdPersona, format_shepherd_response
from nsip_mcp.shepherd.regions import (
    NSIP_REGIONS,
    detect_region,
    get_region_context,
)

__all__ = [
    "ShepherdAgent",
    "ShepherdPersona",
    "format_shepherd_response",
    "detect_region",
    "get_region_context",
    "NSIP_REGIONS",
]
