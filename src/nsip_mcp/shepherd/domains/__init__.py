"""Shepherd domain modules for specialized husbandry guidance.

Each domain provides expert-level guidance in a specific area:
- Breeding: Genetic interpretation, selection, mating advice
- Health: Disease prevention, parasites, nutrition
- Calendar: Seasonal management and planning
- Economics: Costs, profitability, market timing
"""

from nsip_mcp.shepherd.domains.breeding import BreedingDomain
from nsip_mcp.shepherd.domains.calendar import CalendarDomain
from nsip_mcp.shepherd.domains.economics import EconomicsDomain
from nsip_mcp.shepherd.domains.health import HealthDomain

__all__ = [
    "BreedingDomain",
    "HealthDomain",
    "CalendarDomain",
    "EconomicsDomain",
]
