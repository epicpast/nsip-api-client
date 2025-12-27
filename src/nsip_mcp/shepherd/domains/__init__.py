"""Shepherd domain modules for specialized husbandry guidance.

Each domain provides expert-level guidance in a specific area:
- Breeding: Genetic interpretation, selection, mating advice
- Health: Disease prevention, parasites, nutrition
- Calendar: Seasonal management and planning
- Economics: Costs, profitability, market timing

All domains implement the DomainHandler protocol, ensuring a consistent
interface for the Shepherd agent to dispatch questions to the appropriate
domain handler.
"""

from nsip_mcp.shepherd.domains.base import DomainHandler, ensure_domain_handler
from nsip_mcp.shepherd.domains.breeding import BreedingDomain
from nsip_mcp.shepherd.domains.calendar import CalendarDomain
from nsip_mcp.shepherd.domains.economics import EconomicsDomain
from nsip_mcp.shepherd.domains.health import HealthDomain

__all__ = [
    "DomainHandler",
    "ensure_domain_handler",
    "BreedingDomain",
    "HealthDomain",
    "CalendarDomain",
    "EconomicsDomain",
]
