"""Common utilities for NSIP skills."""

from nsip_skills.common.data_models import (
    AnimalAnalysis,
    FlockSummary,
    InbreedingResult,
    MatingPair,
    PedigreeTree,
    TraitProfile,
)
from nsip_skills.common.formatters import (
    format_markdown_table,
    format_pedigree_tree,
    format_trait_comparison,
)
from nsip_skills.common.nsip_wrapper import CachedNSIPClient
from nsip_skills.common.spreadsheet_io import (
    read_spreadsheet,
    write_spreadsheet,
)

__all__ = [
    # Client
    "CachedNSIPClient",
    # Data models
    "AnimalAnalysis",
    "FlockSummary",
    "InbreedingResult",
    "MatingPair",
    "PedigreeTree",
    "TraitProfile",
    # Formatters
    "format_markdown_table",
    "format_pedigree_tree",
    "format_trait_comparison",
    # Spreadsheet I/O
    "read_spreadsheet",
    "write_spreadsheet",
]
