"""
NSIP Client - Python API client for the National Sheep Improvement Program
"""

from .client import NSIPClient
from .models import SearchCriteria, AnimalDetails, Progeny, Lineage
from .exceptions import NSIPError, NSIPAPIError, NSIPNotFoundError

__version__ = "1.0.0"
__all__ = [
    "NSIPClient",
    "SearchCriteria",
    "AnimalDetails",
    "Progeny",
    "Lineage",
    "NSIPError",
    "NSIPAPIError",
    "NSIPNotFoundError",
]
