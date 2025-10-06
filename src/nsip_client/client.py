"""
NSIP Search API Client

Reverse-engineered API client for http://nsipsearch.nsip.org
Based on network traffic analysis from the NSIP Search web application.

API Base URL: http://nsipsearch.nsip.org/api
Authentication: None required (public API)
"""

from typing import Any, Dict, List, Optional, Union

import requests
from requests.exceptions import RequestException, Timeout

from .exceptions import (
    NSIPAPIError,
    NSIPConnectionError,
    NSIPNotFoundError,
    NSIPTimeoutError,
    NSIPValidationError,
)
from .models import (
    AnimalDetails,
    BreedGroup,
    Lineage,
    Progeny,
    SearchCriteria,
    SearchResults,
)


class NSIPClient:
    """Client for interacting with the NSIP Search API"""

    BASE_URL = "http://nsipsearch.nsip.org/api"

    def __init__(self, timeout: int = 30, base_url: str = None):
        """
        Initialize the NSIP API client

        Args:
            timeout: Request timeout in seconds (default: 30)
            base_url: Override the base URL (useful for testing)
        """
        self.timeout = timeout
        self.base_url = base_url or self.BASE_URL
        self.session = requests.Session()
        self.session.headers.update(
            {"Accept": "application/json, text/plain, */*", "User-Agent": "NSIP-Python-Client/1.0"}
        )

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Dict[str, Any] = None,
        data: Dict[str, Any] = None,
        json: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the API with error handling

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: URL parameters
            data: Form data
            json: JSON body

        Returns:
            Response JSON data

        Raises:
            NSIPAPIError: On API errors
            NSIPConnectionError: On connection errors
            NSIPTimeoutError: On timeout
        """
        url = f"{self.base_url}/{endpoint}"

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                data=data,
                json=json,
                timeout=self.timeout,
            )

            if response.status_code == 404:
                raise NSIPNotFoundError(
                    f"Resource not found at {url}",
                    search_string=params.get("searchString") if params else None,
                )

            response.raise_for_status()
            return response.json()

        except Timeout as e:
            raise NSIPTimeoutError(f"Request timed out after {self.timeout}s: {e}")
        except RequestException as e:
            if hasattr(e, "response") and e.response is not None:
                raise NSIPAPIError(
                    f"API request failed: {e}",
                    status_code=e.response.status_code,
                    response={"text": e.response.text},
                )
            raise NSIPConnectionError(f"Failed to connect to API: {e}")

    def get_date_last_updated(self) -> Dict[str, Any]:
        """
        Get the date when the database was last updated

        Returns:
            Dict containing the last update date

        Example:
            >>> client = NSIPClient()
            >>> client.get_date_last_updated()
            {'date': '09/23/2025'}
        """
        return self._make_request("GET", "search/getDateLastUpdated")

    def get_available_breed_groups(self) -> List[BreedGroup]:
        """
        Get list of available breed groups

        Returns:
            List of BreedGroup objects with their IDs and names

        Example:
            >>> client = NSIPClient()
            >>> groups = client.get_available_breed_groups()
            >>> for group in groups:
            ...     print(f"{group.id}: {group.name}")
            61: Range
            62: Maternal Wool
            64: Hair
            69: Terminal
        """
        data = self._make_request("GET", "search/getAvailableBreedGroups")
        # API returns a list, not a dict
        breed_list: List[Dict[str, Any]] = data  # type: ignore
        return [BreedGroup(id=int(g["Id"]), name=str(g["Name"])) for g in breed_list]

    def get_statuses_by_breed_group(self) -> List[str]:
        """
        Get list of available animal statuses

        Returns:
            List of status strings

        Example:
            >>> client = NSIPClient()
            >>> client.get_statuses_by_breed_group()
            ['CURRENT', 'SOLD', 'DEAD', 'COMMERCIAL', 'CULL', ...]
        """
        result = self._make_request("GET", "search/getStatusesByBreedGroup")
        if isinstance(result, list):
            return [str(item) for item in result]
        return []

    def get_trait_ranges_by_breed(self, breed_id: int) -> Dict[str, Any]:
        """
        Get trait ranges for a specific breed

        Args:
            breed_id: The breed ID

        Returns:
            Dict containing min/max values for each trait

        Example:
            >>> client = NSIPClient()
            >>> ranges = client.get_trait_ranges_by_breed(486)
            >>> ranges['BWT']
            {'min': -0.713, 'max': 0.0}
        """
        if not isinstance(breed_id, int) or breed_id <= 0:
            raise NSIPValidationError(f"Invalid breed_id: {breed_id}")

        return self._make_request(
            "GET", "search/getTraitRangesByBreed", params={"breedId": breed_id}
        )

    def search_animals(
        self,
        page: int = 0,
        page_size: int = 15,
        breed_id: Optional[int] = None,
        sorted_trait: Optional[str] = None,
        reverse: Optional[bool] = None,
        search_criteria: Optional[Union[SearchCriteria, Dict[str, Any]]] = None,
    ) -> SearchResults:
        """
        Search for animals based on criteria

        Args:
            page: Page number (0-indexed)
            page_size: Number of results per page (max 100)
            breed_id: Filter by breed ID
            sorted_trait: Trait to sort by (e.g., "BWT", "WWT")
            reverse: Sort in reverse order
            search_criteria: SearchCriteria object or dict with additional filters

        Returns:
            SearchResults object with animals and pagination info

        Example:
            >>> client = NSIPClient()
            >>> results = client.search_animals(breed_id=486, page_size=5)
            >>> print(f"Found {results.total_count} animals")
            >>> for animal in results.results:
            ...     print(animal['LpnId'])
        """
        if page < 0:
            raise NSIPValidationError(f"Page must be >= 0, got {page}")
        if page_size < 1 or page_size > 100:
            raise NSIPValidationError(f"Page size must be 1-100, got {page_size}")

        params = {
            "page": page,
            "pageSize": page_size,
            "breedId": breed_id if breed_id is not None else "undefined",
            "sortedBreedTrait": sorted_trait or "undefined",
            "reverse": reverse if reverse is not None else "undefined",
        }

        # Convert SearchCriteria to dict if needed
        criteria_dict = {}
        if search_criteria:
            if isinstance(search_criteria, SearchCriteria):
                criteria_dict = search_criteria.to_dict()
            else:
                criteria_dict = search_criteria

        data = self._make_request(
            "POST", "search/getPageOfSearchResults", params=params, json=criteria_dict
        )
        return SearchResults.from_api_response(data)

    def get_animal_details(self, search_string: str) -> AnimalDetails:
        """
        Get detailed information about a specific animal

        Args:
            search_string: LPN ID or registration number

        Returns:
            AnimalDetails object with complete animal information

        Raises:
            NSIPNotFoundError: If animal not found

        Example:
            >>> client = NSIPClient()
            >>> animal = client.get_animal_details("6####92020###249")
            >>> print(f"{animal.breed} - {animal.gender}")
            Katahdin - Female
            >>> print(f"BWT: {animal.traits['BWT'].value}")
            BWT: 0.246
        """
        if not search_string or not search_string.strip():
            raise NSIPValidationError("search_string cannot be empty")

        data = self._make_request(
            "GET", "details/getAnimalDetails", params={"searchString": search_string}
        )
        return AnimalDetails.from_api_response(data)

    def get_lineage(self, lpn_id: str) -> Lineage:
        """
        Get the lineage/pedigree information for an animal

        Args:
            lpn_id: The LPN ID of the animal

        Returns:
            Lineage object containing pedigree tree information

        Example:
            >>> client = NSIPClient()
            >>> lineage = client.get_lineage("6####92020###249")
            >>> print(lineage.sire.lpn_id if lineage.sire else "Unknown")
        """
        if not lpn_id or not lpn_id.strip():
            raise NSIPValidationError("lpn_id cannot be empty")

        data = self._make_request("GET", "details/getLineage", params={"lpnId": lpn_id})
        return Lineage.from_api_response(data)

    def get_progeny(self, lpn_id: str, page: int = 0, page_size: int = 10) -> Progeny:
        """
        Get progeny (offspring) for a specific animal

        Args:
            lpn_id: The LPN ID of the parent animal
            page: Page number (0-indexed)
            page_size: Number of results per page

        Returns:
            Progeny object with list of offspring and pagination info

        Example:
            >>> client = NSIPClient()
            >>> progeny = client.get_progeny("6####92020###249")
            >>> print(f"Total offspring: {progeny.total_count}")
            Total offspring: 6
            >>> for offspring in progeny.animals:
            ...     print(f"{offspring.lpn_id} - {offspring.sex}")
        """
        if not lpn_id or not lpn_id.strip():
            raise NSIPValidationError("lpn_id cannot be empty")
        if page < 0:
            raise NSIPValidationError(f"Page must be >= 0, got {page}")
        if page_size < 1:
            raise NSIPValidationError(f"Page size must be >= 1, got {page_size}")

        params = {"lpnId": lpn_id, "page": page, "pageSize": page_size}
        data = self._make_request("GET", "details/getPageOfProgeny", params=params)
        return Progeny.from_api_response(data)

    def search_by_lpn(self, lpn_id: str) -> Dict[str, Any]:
        """
        Convenience method to get all information about an animal by LPN ID

        Args:
            lpn_id: The LPN ID to search for

        Returns:
            Dict containing:
            - details: AnimalDetails object
            - lineage: Lineage object
            - progeny: Progeny object

        Example:
            >>> client = NSIPClient()
            >>> profile = client.search_by_lpn("6####92020###249")
            >>> print(profile['details'].breed)
            Katahdin
            >>> print(profile['progeny'].total_count)
            6
        """
        return {
            "details": self.get_animal_details(lpn_id),
            "lineage": self.get_lineage(lpn_id),
            "progeny": self.get_progeny(lpn_id),
        }

    def close(self) -> None:
        """Close the session"""
        self.session.close()

    def __enter__(self) -> "NSIPClient":
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit"""
        self.close()
