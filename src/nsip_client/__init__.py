"""
NSIP Client - Python API client for the National Sheep Improvement Program
"""

from .client import NSIPClient
from .exceptions import NSIPAPIError, NSIPError, NSIPNotFoundError
from .models import AnimalDetails, Lineage, Progeny, SearchCriteria

__version__ = "1.4.3"
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
