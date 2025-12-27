"""
NSIP Skills - Breeding decision support tools for sheep genetics.

This package provides analysis and planning tools for sheep breeders,
built on top of the nsip_client library for direct NSIP API access.

Available modules:
    - flock_import: Import and enrich flock data from spreadsheets
    - ebv_analysis: Compare and rank animals by EBV traits
    - inbreeding: Calculate pedigree-based inbreeding coefficients
    - mating_optimizer: Recommend optimal ram-ewe pairings
    - progeny_analysis: Evaluate sires by offspring performance
    - trait_planner: Design multi-generation improvement strategies
    - ancestry_builder: Generate pedigree reports and visualizations
    - flock_stats: Calculate aggregate flock statistics
    - selection_index: Build and apply custom breeding indexes
    - recommendation_engine: AI-powered breeding recommendations

Example usage:
    >>> from nsip_skills import CachedNSIPClient
    >>> client = CachedNSIPClient()
    >>> # Use client for cached NSIP API operations
"""

__version__ = "1.4.5"

# Re-export common utilities for convenience
from nsip_skills.common.data_models import (
    AnimalAnalysis,
    FlockSummary,
    InbreedingResult,
    MatingPair,
    PedigreeTree,
    TraitProfile,
)
from nsip_skills.common.nsip_wrapper import CachedNSIPClient

__all__ = [
    "__version__",
    "CachedNSIPClient",
    "AnimalAnalysis",
    "FlockSummary",
    "InbreedingResult",
    "MatingPair",
    "PedigreeTree",
    "TraitProfile",
]
