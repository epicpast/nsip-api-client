"""Base protocol for Shepherd domain handlers.

This module defines the common interface that all domain handlers must implement.
Using a Protocol allows for structural subtyping (duck typing) while providing
type safety benefits.
"""

from typing import Any, Protocol, runtime_checkable

from nsip_mcp.shepherd.persona import ShepherdPersona


@runtime_checkable
class DomainHandler(Protocol):
    """Protocol defining the common interface for all Shepherd domains.

    All domain handlers (BreedingDomain, HealthDomain, CalendarDomain,
    EconomicsDomain) share this common structure:

    - persona: ShepherdPersona for formatting responses
    - Domain-specific methods for their area of expertise

    Using @runtime_checkable allows isinstance() checks at runtime,
    which is useful for validation and dispatching.

    Example:
        >>> from nsip_mcp.shepherd.domains import BreedingDomain
        >>> from nsip_mcp.shepherd.domains.base import DomainHandler
        >>> domain = BreedingDomain()
        >>> isinstance(domain, DomainHandler)
        True
    """

    persona: ShepherdPersona

    def format_response(
        self,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Format a response using the domain's persona.

        Args:
            content: The main response content
            metadata: Optional metadata to include

        Returns:
            Formatted response dictionary
        """
        ...


def ensure_domain_handler(handler: object) -> DomainHandler:
    """Validate that an object implements the DomainHandler protocol.

    Args:
        handler: Object to validate

    Returns:
        The handler, typed as DomainHandler

    Raises:
        TypeError: If handler doesn't implement the protocol
    """
    if not isinstance(handler, DomainHandler):
        raise TypeError(
            f"{type(handler).__name__} does not implement DomainHandler protocol. "
            f"Ensure it has a 'persona' attribute and 'format_response' method."
        )
    return handler
