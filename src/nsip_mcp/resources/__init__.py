"""MCP Resources for NSIP data access.

This module provides URI-addressable resources for accessing:
- Static knowledge base data (heritabilities, traits, regions, indexes)
- Dynamic NSIP API data (animals, lineage, progeny, breeding projections)

Resource URI Scheme:
    nsip://static/{resource_type}/{params}  - Static knowledge base
    nsip://animals/{lpn_id}/{data_type}     - Animal data from NSIP API
    nsip://breeding/{ram}/{ewe}/{analysis}  - Breeding pair analysis
    nsip://flock/{flock_id}/{report_type}   - Flock-level reports
"""

# Import resource modules to register them with the MCP server
# These are imported after server.py imports this module
from nsip_mcp.resources import (
    animal_resources,  # noqa: F401
    breeding_resources,  # noqa: F401
    flock_resources,  # noqa: F401
    static_resources,  # noqa: F401
)

__all__ = [
    "static_resources",
    "animal_resources",
    "breeding_resources",
    "flock_resources",
]
