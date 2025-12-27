"""
Cached wrapper around NSIPClient for skills usage.

Provides local file-based caching to reduce API calls and improve
performance for batch operations.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from nsip_client import NSIPClient
from nsip_client.exceptions import NSIPError, NSIPNotFoundError
from nsip_client.models import (
    AnimalDetails,
    BreedGroup,
    Lineage,
    Progeny,
    SearchCriteria,
    SearchResults,
)

logger = logging.getLogger(__name__)

# Cache version - increment when model schemas change to auto-invalidate old entries
# History:
#   v2: Fixed Lineage.from_api_response() to parse nested HTML format (2025-12-06)
#   v1: Initial cache format
CACHE_VERSION = 2

# Safety limit for pagination loops to prevent infinite loops or excessive API calls
MAX_PAGES = 100


@dataclass
class CacheEntry:
    """A cached API response with metadata."""

    data: Any
    timestamp: float
    ttl: int = 3600  # 1 hour default


class CachedNSIPClient:
    """
    NSIPClient wrapper with local file-based caching.

    Caches API responses to ~/.cache/nsip/ with configurable TTL.
    Reduces API calls for repeated lookups in batch operations.

    Example:
        client = CachedNSIPClient()
        animal = client.get_animal_details("6####92020###249")
        # Subsequent calls use cache until TTL expires

    Args:
        cache_dir: Directory for cache files (default: ~/.cache/nsip)
        ttl: Cache time-to-live in seconds (default: 3600 = 1 hour)
        timeout: API request timeout in seconds (default: 30)
    """

    def __init__(
        self,
        cache_dir: str | Path | None = None,
        ttl: int = 3600,
        timeout: int = 30,
    ):
        self.cache_dir = Path(cache_dir or Path.home() / ".cache" / "nsip")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = ttl
        self._client = NSIPClient(timeout=timeout)
        self._memory_cache: dict[str, CacheEntry] = {}

    def _cache_key(self, method: str, **params: Any) -> str:
        """Generate a deterministic cache key from method and parameters."""
        # Sort params for consistent keys
        sorted_params = json.dumps(params, sort_keys=True, default=str)
        # Include cache version to auto-invalidate on schema changes
        key_string = f"v{CACHE_VERSION}:{method}:{sorted_params}"
        return hashlib.sha256(key_string.encode()).hexdigest()[:16]

    def _cache_path(self, key: str) -> Path:
        """Get the file path for a cache key."""
        return self.cache_dir / f"{key}.json"

    def _get_cached(self, key: str) -> Any | None:
        """Retrieve from cache if valid, else None."""
        # Check memory cache first
        if key in self._memory_cache:
            entry = self._memory_cache[key]
            if time.time() - entry.timestamp < entry.ttl:
                return entry.data
            del self._memory_cache[key]

        # Check file cache
        path = self._cache_path(key)
        if path.exists():
            try:
                with open(path) as f:
                    cached = json.load(f)
                if time.time() - cached["timestamp"] < cached.get("ttl", self.ttl):
                    # Promote to memory cache
                    self._memory_cache[key] = CacheEntry(
                        data=cached["data"],
                        timestamp=cached["timestamp"],
                        ttl=cached.get("ttl", self.ttl),
                    )
                    return cached["data"]
                # Expired, remove file
                path.unlink(missing_ok=True)
            except (json.JSONDecodeError, KeyError, OSError):
                path.unlink(missing_ok=True)
        return None

    def _set_cached(self, key: str, data: Any) -> None:
        """Store data in both memory and file cache."""
        timestamp = time.time()
        self._memory_cache[key] = CacheEntry(data=data, timestamp=timestamp, ttl=self.ttl)

        path = self._cache_path(key)
        try:
            with open(path, "w") as f:
                json.dump({"data": data, "timestamp": timestamp, "ttl": self.ttl}, f)
        except OSError as e:
            # Cache write failure is non-fatal, log at DEBUG for troubleshooting
            logger.debug(f"Cache write failed for {key}: {e}")

    def clear_cache(self) -> int:
        """Clear all cached data. Returns count of entries cleared."""
        count = len(self._memory_cache)
        self._memory_cache.clear()
        for path in self.cache_dir.glob("*.json"):
            try:
                path.unlink()
                count += 1
            except OSError:
                # File may be locked or already deleted; continue clearing others
                pass
        return count

    # ========== API Methods with Caching ==========

    def get_animal_details(self, lpn_id: str, force_refresh: bool = False) -> AnimalDetails:
        """
        Get detailed information for a single animal.

        Args:
            lpn_id: The LPN ID or registration number
            force_refresh: Bypass cache and fetch fresh data

        Returns:
            AnimalDetails with traits, contact info, pedigree

        Raises:
            NSIPNotFoundError: If animal not found
        """
        key = self._cache_key("get_animal_details", lpn_id=lpn_id)
        if not force_refresh:
            cached = self._get_cached(key)
            if cached is not None:
                # Use from_dict() for cached data (snake_case format from to_dict())
                return AnimalDetails.from_dict(cached)

        result = self._client.get_animal_details(lpn_id)
        self._set_cached(key, result.to_dict())
        return result

    def get_lineage(self, lpn_id: str, force_refresh: bool = False) -> Lineage:
        """
        Get pedigree/ancestry information for an animal.

        Args:
            lpn_id: The LPN ID
            force_refresh: Bypass cache and fetch fresh data

        Returns:
            Lineage with sire, dam, and extended generations
        """
        key = self._cache_key("get_lineage", lpn_id=lpn_id)
        if not force_refresh:
            cached = self._get_cached(key)
            if cached is not None:
                return Lineage.from_api_response(cached)

        result = self._client.get_lineage(lpn_id)
        self._set_cached(key, result.to_dict())
        return result

    def get_progeny(
        self,
        lpn_id: str,
        page: int = 0,
        page_size: int = 100,
        force_refresh: bool = False,
    ) -> Progeny:
        """
        Get offspring list for an animal.

        Args:
            lpn_id: The LPN ID
            page: Page number (0-indexed)
            page_size: Results per page (max 100)
            force_refresh: Bypass cache and fetch fresh data

        Returns:
            Progeny with total count and list of offspring
        """
        key = self._cache_key("get_progeny", lpn_id=lpn_id, page=page, page_size=page_size)
        if not force_refresh:
            cached = self._get_cached(key)
            if cached is not None:
                return Progeny.from_api_response(cached)

        result = self._client.get_progeny(lpn_id, page=page, page_size=page_size)
        # Convert to dict for caching
        cache_data = {
            "total_count": result.total_count,
            "animals": [a.to_dict() for a in result.animals],
            "page": result.page,
            "page_size": result.page_size,
        }
        self._set_cached(key, cache_data)
        return result

    def get_all_progeny(self, lpn_id: str, force_refresh: bool = False) -> list[dict[str, Any]]:
        """
        Fetch all progeny for an animal (handles pagination).

        Args:
            lpn_id: The LPN ID
            force_refresh: Bypass cache and fetch fresh data

        Returns:
            List of all progeny animals

        Note:
            Limited to MAX_PAGES iterations to prevent runaway loops.
        """
        all_progeny: list[dict[str, Any]] = []
        page = 0
        page_size = 100

        while page < MAX_PAGES:
            progeny = self.get_progeny(
                lpn_id, page=page, page_size=page_size, force_refresh=force_refresh
            )
            for animal in progeny.animals:
                all_progeny.append(animal.to_dict())
            if len(progeny.animals) < page_size or len(all_progeny) >= progeny.total_count:
                break
            page += 1

        return all_progeny

    def search_animals(
        self,
        page: int = 0,
        page_size: int = 15,
        breed_id: int | None = None,
        sorted_trait: str | None = None,
        reverse: bool | None = None,
        search_criteria: SearchCriteria | dict[str, Any] | None = None,
        force_refresh: bool = False,
    ) -> SearchResults:
        """
        Search for animals with filtering and pagination.

        Args:
            page: Page number (0-indexed)
            page_size: Results per page (1-100)
            breed_id: Filter by breed
            sorted_trait: Sort by trait (e.g., "BWT", "WWT")
            reverse: Sort in reverse order
            search_criteria: Advanced filtering
            force_refresh: Bypass cache and fetch fresh data

        Returns:
            SearchResults with total count and result list
        """
        criteria_dict = None
        if isinstance(search_criteria, SearchCriteria):
            criteria_dict = search_criteria.to_dict()
        elif isinstance(search_criteria, dict):
            criteria_dict = search_criteria

        key = self._cache_key(
            "search_animals",
            page=page,
            page_size=page_size,
            breed_id=breed_id,
            sorted_trait=sorted_trait,
            reverse=reverse,
            search_criteria=criteria_dict,
        )

        if not force_refresh:
            cached = self._get_cached(key)
            if cached is not None:
                return SearchResults.from_api_response(cached)

        result = self._client.search_animals(
            page=page,
            page_size=page_size,
            breed_id=breed_id,
            sorted_trait=sorted_trait,
            reverse=reverse,
            search_criteria=search_criteria,
        )
        # Convert to cacheable dict
        cache_data = {
            "total_count": result.total_count,
            "results": result.results,
            "page": result.page,
            "page_size": result.page_size,
        }
        self._set_cached(key, cache_data)
        return result

    def get_available_breed_groups(self, force_refresh: bool = False) -> list[BreedGroup]:
        """Get all available breed groups."""
        key = self._cache_key("get_available_breed_groups")
        if not force_refresh:
            cached = self._get_cached(key)
            if cached is not None:
                return [BreedGroup(**bg) for bg in cached]

        result = self._client.get_available_breed_groups()
        cache_data = [{"id": bg.id, "name": bg.name, "breeds": bg.breeds} for bg in result]
        self._set_cached(key, cache_data)
        return result

    def get_trait_ranges_by_breed(
        self, breed_id: int, force_refresh: bool = False
    ) -> dict[str, Any]:
        """Get min/max trait values for a breed."""
        key = self._cache_key("get_trait_ranges_by_breed", breed_id=breed_id)
        if not force_refresh:
            cached = self._get_cached(key)
            if cached is not None:
                return cached

        result = self._client.get_trait_ranges_by_breed(breed_id)
        self._set_cached(key, result)
        return result

    def get_statuses_by_breed_group(self, force_refresh: bool = False) -> list[str]:
        """Get available animal statuses."""
        key = self._cache_key("get_statuses_by_breed_group")
        if not force_refresh:
            cached = self._get_cached(key)
            if cached is not None:
                return cached

        result = self._client.get_statuses_by_breed_group()
        self._set_cached(key, result)
        return result

    def search_by_lpn(self, lpn_id: str, force_refresh: bool = False) -> dict[str, Any]:
        """
        Get complete profile: details + lineage + progeny.

        Args:
            lpn_id: The LPN ID
            force_refresh: Bypass cache and fetch fresh data

        Returns:
            Dict with keys: details, lineage, progeny
        """
        details = self.get_animal_details(lpn_id, force_refresh=force_refresh)
        lineage = self.get_lineage(lpn_id, force_refresh=force_refresh)
        progeny = self.get_progeny(lpn_id, force_refresh=force_refresh)

        return {
            "details": details,
            "lineage": lineage,
            "progeny": progeny,
        }

    def batch_get_animals(
        self,
        lpn_ids: list[str],
        include_lineage: bool = False,
        include_progeny: bool = False,
        on_error: str = "skip",
        force_refresh: bool = False,
    ) -> dict[str, dict[str, Any]]:
        """
        Batch fetch multiple animals with optional lineage/progeny.

        Args:
            lpn_ids: List of LPN IDs to fetch
            include_lineage: Also fetch lineage for each animal
            include_progeny: Also fetch progeny for each animal
            on_error: "skip" (default) or "raise" on individual failures
            force_refresh: Bypass cache for all fetches

        Returns:
            Dict mapping lpn_id to data dict with keys:
            - details: AnimalDetails (always)
            - lineage: Lineage (if include_lineage)
            - progeny: Progeny (if include_progeny)
            - error: str (if on_error="skip" and fetch failed)
        """
        results: dict[str, dict[str, Any]] = {}

        for lpn_id in lpn_ids:
            try:
                entry: dict[str, Any] = {}
                entry["details"] = self.get_animal_details(lpn_id, force_refresh=force_refresh)

                if include_lineage:
                    entry["lineage"] = self.get_lineage(lpn_id, force_refresh=force_refresh)

                if include_progeny:
                    entry["progeny"] = self.get_progeny(lpn_id, force_refresh=force_refresh)

                results[lpn_id] = entry

            except NSIPNotFoundError as e:
                if on_error == "raise":
                    raise
                results[lpn_id] = {"error": f"Not found: {e}"}
            except NSIPError as e:
                if on_error == "raise":
                    raise
                results[lpn_id] = {"error": f"API error: {e}"}

        return results

    def close(self) -> None:
        """Close the underlying client session."""
        self._client.close()

    def __enter__(self) -> CachedNSIPClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
