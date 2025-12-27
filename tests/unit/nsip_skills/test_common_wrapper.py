"""
Unit tests for nsip_skills.common.nsip_wrapper

Tests:
- CacheEntry dataclass
- CachedNSIPClient initialization
- Cache key generation and operations
- API methods with caching
- Force refresh parameter
- Context manager support
- Error handling

Target: >95% coverage
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from nsip_skills.common.nsip_wrapper import CachedNSIPClient, CacheEntry


class TestCacheEntry:
    """Tests for CacheEntry dataclass."""

    def test_default_values(self):
        """Verify default TTL is set."""
        entry = CacheEntry(data={"test": "data"}, timestamp=time.time())
        assert entry.ttl == 3600

    def test_custom_ttl(self):
        """Verify custom TTL is preserved."""
        entry = CacheEntry(data={"test": "data"}, timestamp=time.time(), ttl=1800)
        assert entry.ttl == 1800


class TestCachedNSIPClientInit:
    """Tests for CachedNSIPClient initialization."""

    def test_default_cache_dir(self):
        """Verify default cache directory is created."""
        with patch("nsip_skills.common.nsip_wrapper.NSIPClient"):
            client = CachedNSIPClient()
            expected = Path.home() / ".cache" / "nsip"
            assert client.cache_dir == expected

    def test_custom_cache_dir(self, tmp_path):
        """Verify custom cache directory is used."""
        cache_dir = tmp_path / "custom_cache"
        with patch("nsip_skills.common.nsip_wrapper.NSIPClient"):
            client = CachedNSIPClient(cache_dir=cache_dir)
            assert client.cache_dir == cache_dir
            assert cache_dir.exists()

    def test_custom_ttl(self, tmp_path):
        """Verify custom TTL is set."""
        with patch("nsip_skills.common.nsip_wrapper.NSIPClient"):
            client = CachedNSIPClient(cache_dir=tmp_path, ttl=7200)
            assert client.ttl == 7200

    def test_timeout_passed_to_client(self, tmp_path):
        """Verify timeout is passed to underlying client."""
        with patch("nsip_skills.common.nsip_wrapper.NSIPClient") as mock_cls:
            CachedNSIPClient(cache_dir=tmp_path, timeout=60)
            mock_cls.assert_called_once_with(timeout=60)


class TestCacheKeyGeneration:
    """Tests for cache key generation."""

    def test_cache_key_deterministic(self, tmp_path):
        """Verify same inputs produce same key."""
        with patch("nsip_skills.common.nsip_wrapper.NSIPClient"):
            client = CachedNSIPClient(cache_dir=tmp_path)
            key1 = client._cache_key("test_method", param1="value1", param2=123)
            key2 = client._cache_key("test_method", param1="value1", param2=123)
            assert key1 == key2

    def test_cache_key_different_params(self, tmp_path):
        """Verify different params produce different keys."""
        with patch("nsip_skills.common.nsip_wrapper.NSIPClient"):
            client = CachedNSIPClient(cache_dir=tmp_path)
            key1 = client._cache_key("test_method", param="value1")
            key2 = client._cache_key("test_method", param="value2")
            assert key1 != key2

    def test_cache_key_param_order_independent(self, tmp_path):
        """Verify param order doesn't affect key."""
        with patch("nsip_skills.common.nsip_wrapper.NSIPClient"):
            client = CachedNSIPClient(cache_dir=tmp_path)
            key1 = client._cache_key("test", a=1, b=2)
            key2 = client._cache_key("test", b=2, a=1)
            assert key1 == key2

    def test_cache_path(self, tmp_path):
        """Verify cache path generation."""
        with patch("nsip_skills.common.nsip_wrapper.NSIPClient"):
            client = CachedNSIPClient(cache_dir=tmp_path)
            path = client._cache_path("abc123")
            assert path == tmp_path / "abc123.json"

    def test_cache_key_includes_version(self, tmp_path):
        """Verify cache key includes version for auto-invalidation."""
        from nsip_skills.common.nsip_wrapper import CACHE_VERSION

        with patch("nsip_skills.common.nsip_wrapper.NSIPClient"):
            client = CachedNSIPClient(cache_dir=tmp_path)

            # Key should be deterministic based on version
            key1 = client._cache_key("test_method", param="value")

            # Simulate version change by patching
            with patch("nsip_skills.common.nsip_wrapper.CACHE_VERSION", CACHE_VERSION + 1):
                key2 = client._cache_key("test_method", param="value")

            # Different versions should produce different keys
            assert key1 != key2


class TestCacheOperations:
    """Tests for cache get/set operations."""

    def test_set_and_get_cached(self, tmp_path):
        """Verify basic cache set and get."""
        with patch("nsip_skills.common.nsip_wrapper.NSIPClient"):
            client = CachedNSIPClient(cache_dir=tmp_path, ttl=3600)
            client._set_cached("test_key", {"value": 42})
            result = client._get_cached("test_key")
            assert result == {"value": 42}

    def test_memory_cache_hit(self, tmp_path):
        """Verify memory cache is checked first."""
        with patch("nsip_skills.common.nsip_wrapper.NSIPClient"):
            client = CachedNSIPClient(cache_dir=tmp_path)
            client._set_cached("memory_key", {"from": "memory"})
            # Delete file cache to ensure memory is used
            client._cache_path("memory_key").unlink()
            result = client._get_cached("memory_key")
            assert result == {"from": "memory"}

    def test_file_cache_fallback(self, tmp_path):
        """Verify file cache is used when memory cache is empty."""
        with patch("nsip_skills.common.nsip_wrapper.NSIPClient"):
            client = CachedNSIPClient(cache_dir=tmp_path)
            # Write directly to file cache
            cache_path = client._cache_path("file_key")
            cache_data = {"data": {"from": "file"}, "timestamp": time.time(), "ttl": 3600}
            with open(cache_path, "w") as f:
                json.dump(cache_data, f)

            result = client._get_cached("file_key")
            assert result == {"from": "file"}

    def test_cache_miss(self, tmp_path):
        """Verify cache miss returns None."""
        with patch("nsip_skills.common.nsip_wrapper.NSIPClient"):
            client = CachedNSIPClient(cache_dir=tmp_path)
            result = client._get_cached("nonexistent_key")
            assert result is None

    def test_memory_cache_expiry(self, tmp_path):
        """Verify expired memory cache entries are removed."""
        with patch("nsip_skills.common.nsip_wrapper.NSIPClient"):
            client = CachedNSIPClient(cache_dir=tmp_path, ttl=1)
            # Manually add an expired entry
            client._memory_cache["expired"] = CacheEntry(
                data={"old": True},
                timestamp=time.time() - 10,  # 10 seconds ago
                ttl=1,
            )
            result = client._get_cached("expired")
            assert result is None
            assert "expired" not in client._memory_cache

    def test_file_cache_expiry(self, tmp_path):
        """Verify expired file cache entries are removed."""
        with patch("nsip_skills.common.nsip_wrapper.NSIPClient"):
            client = CachedNSIPClient(cache_dir=tmp_path)
            cache_path = client._cache_path("old_file")
            cache_data = {
                "data": {"old": True},
                "timestamp": time.time() - 7200,  # 2 hours ago
                "ttl": 3600,
            }
            with open(cache_path, "w") as f:
                json.dump(cache_data, f)

            result = client._get_cached("old_file")
            assert result is None
            assert not cache_path.exists()

    def test_corrupted_file_cache_handled(self, tmp_path):
        """Verify corrupted file cache is handled gracefully."""
        with patch("nsip_skills.common.nsip_wrapper.NSIPClient"):
            client = CachedNSIPClient(cache_dir=tmp_path)
            cache_path = client._cache_path("corrupted")
            with open(cache_path, "w") as f:
                f.write("not valid json")

            result = client._get_cached("corrupted")
            assert result is None
            assert not cache_path.exists()

    def test_file_cache_missing_keys_handled(self, tmp_path):
        """Verify file cache with missing keys is handled."""
        with patch("nsip_skills.common.nsip_wrapper.NSIPClient"):
            client = CachedNSIPClient(cache_dir=tmp_path)
            cache_path = client._cache_path("malformed")
            with open(cache_path, "w") as f:
                json.dump({"incomplete": True}, f)  # Missing 'data' and 'timestamp'

            result = client._get_cached("malformed")
            assert result is None

    def test_set_cached_handles_write_error(self, tmp_path):
        """Verify write errors are non-fatal."""
        with patch("nsip_skills.common.nsip_wrapper.NSIPClient"):
            client = CachedNSIPClient(cache_dir=tmp_path)
            # Make cache dir read-only
            tmp_path.chmod(0o444)
            try:
                # Should not raise even if file write fails
                client._set_cached("fail_write", {"test": True})
                # Memory cache should still work
                assert "fail_write" in client._memory_cache
            finally:
                tmp_path.chmod(0o755)


class TestClearCache:
    """Tests for cache clearing."""

    def test_clear_cache_empty(self, tmp_path):
        """Verify clearing empty cache returns 0."""
        with patch("nsip_skills.common.nsip_wrapper.NSIPClient"):
            client = CachedNSIPClient(cache_dir=tmp_path)
            count = client.clear_cache()
            assert count == 0

    def test_clear_cache_with_entries(self, tmp_path):
        """Verify all cache entries are cleared."""
        with patch("nsip_skills.common.nsip_wrapper.NSIPClient"):
            client = CachedNSIPClient(cache_dir=tmp_path)
            # Add multiple entries
            for i in range(5):
                client._set_cached(f"key{i}", {"value": i})

            count = client.clear_cache()
            assert count >= 5
            assert len(client._memory_cache) == 0
            assert list(tmp_path.glob("*.json")) == []


class TestGetAnimalDetails:
    """Tests for get_animal_details method."""

    def test_basic_fetch(self, tmp_path):
        """Verify basic animal details fetch."""
        with patch("nsip_skills.common.nsip_wrapper.NSIPClient") as mock_cls:
            mock_client = MagicMock()
            mock_result = MagicMock()
            mock_result.to_dict.return_value = {"lpn_id": "TEST123", "breed": "Suffolk"}
            mock_client.get_animal_details.return_value = mock_result
            mock_cls.return_value = mock_client

            client = CachedNSIPClient(cache_dir=tmp_path)
            result = client.get_animal_details("TEST123")

            assert result == mock_result
            mock_client.get_animal_details.assert_called_once_with("TEST123")

    def test_cached_result(self, tmp_path):
        """Verify cached result is returned."""
        with patch("nsip_skills.common.nsip_wrapper.NSIPClient") as mock_cls:
            mock_client = MagicMock()
            mock_result = MagicMock()
            mock_result.to_dict.return_value = {"lpn_id": "TEST123", "breed": "Suffolk"}
            mock_client.get_animal_details.return_value = mock_result
            mock_cls.return_value = mock_client

            client = CachedNSIPClient(cache_dir=tmp_path)
            # First call
            client.get_animal_details("TEST123")
            # Second call should use cache
            with patch("nsip_client.models.AnimalDetails.from_api_response") as mock_from_api:
                mock_from_api.return_value = mock_result
                client.get_animal_details("TEST123")

            # API should only be called once
            assert mock_client.get_animal_details.call_count == 1

    def test_force_refresh(self, tmp_path):
        """Verify force_refresh bypasses cache."""
        with patch("nsip_skills.common.nsip_wrapper.NSIPClient") as mock_cls:
            mock_client = MagicMock()
            mock_result = MagicMock()
            mock_result.to_dict.return_value = {"lpn_id": "TEST123"}
            mock_client.get_animal_details.return_value = mock_result
            mock_cls.return_value = mock_client

            client = CachedNSIPClient(cache_dir=tmp_path)
            client.get_animal_details("TEST123")
            client.get_animal_details("TEST123", force_refresh=True)

            # API should be called twice due to force_refresh
            assert mock_client.get_animal_details.call_count == 2


class TestGetLineage:
    """Tests for get_lineage method."""

    def test_basic_fetch(self, tmp_path):
        """Verify basic lineage fetch."""
        with patch("nsip_skills.common.nsip_wrapper.NSIPClient") as mock_cls:
            mock_client = MagicMock()
            mock_result = MagicMock()
            mock_result.to_dict.return_value = {"lpn_id": "TEST123"}
            mock_client.get_lineage.return_value = mock_result
            mock_cls.return_value = mock_client

            client = CachedNSIPClient(cache_dir=tmp_path)
            result = client.get_lineage("TEST123")

            assert result == mock_result
            mock_client.get_lineage.assert_called_once_with("TEST123")


class TestGetProgeny:
    """Tests for get_progeny method."""

    def test_basic_fetch(self, tmp_path):
        """Verify basic progeny fetch."""
        with patch("nsip_skills.common.nsip_wrapper.NSIPClient") as mock_cls:
            mock_client = MagicMock()
            mock_animal = MagicMock()
            mock_animal.to_dict.return_value = {"lpn_id": "PROG1"}
            mock_result = MagicMock()
            mock_result.total_count = 1
            mock_result.animals = [mock_animal]
            mock_result.page = 0
            mock_result.page_size = 100
            mock_client.get_progeny.return_value = mock_result
            mock_cls.return_value = mock_client

            client = CachedNSIPClient(cache_dir=tmp_path)
            result = client.get_progeny("TEST123")

            assert result == mock_result
            mock_client.get_progeny.assert_called_once_with("TEST123", page=0, page_size=100)

    def test_pagination_params(self, tmp_path):
        """Verify pagination parameters are passed."""
        with patch("nsip_skills.common.nsip_wrapper.NSIPClient") as mock_cls:
            mock_client = MagicMock()
            mock_result = MagicMock()
            mock_result.total_count = 0
            mock_result.animals = []
            mock_result.page = 2
            mock_result.page_size = 50
            mock_client.get_progeny.return_value = mock_result
            mock_cls.return_value = mock_client

            client = CachedNSIPClient(cache_dir=tmp_path)
            client.get_progeny("TEST123", page=2, page_size=50)

            mock_client.get_progeny.assert_called_once_with("TEST123", page=2, page_size=50)


class TestGetAllProgeny:
    """Tests for get_all_progeny method."""

    def test_single_page(self, tmp_path):
        """Verify single page progeny fetch."""
        with patch("nsip_skills.common.nsip_wrapper.NSIPClient") as mock_cls:
            mock_client = MagicMock()
            mock_animal = MagicMock()
            mock_animal.to_dict.return_value = {"lpn_id": "PROG1"}
            mock_result = MagicMock()
            mock_result.total_count = 1
            mock_result.animals = [mock_animal]
            mock_result.page = 0
            mock_result.page_size = 100
            mock_client.get_progeny.return_value = mock_result
            mock_cls.return_value = mock_client

            client = CachedNSIPClient(cache_dir=tmp_path)
            progeny = client.get_all_progeny("TEST123")

            assert len(progeny) == 1
            assert progeny[0] == {"lpn_id": "PROG1"}

    def test_multiple_pages(self, tmp_path):
        """Verify pagination is handled."""
        with patch("nsip_skills.common.nsip_wrapper.NSIPClient") as mock_cls:
            mock_client = MagicMock()

            # First page - 100 animals
            animals_page1 = [MagicMock() for _ in range(100)]
            for i, a in enumerate(animals_page1):
                a.to_dict.return_value = {"lpn_id": f"PROG{i}"}
            result1 = MagicMock()
            result1.total_count = 150
            result1.animals = animals_page1
            result1.page = 0
            result1.page_size = 100

            # Second page - 50 animals
            animals_page2 = [MagicMock() for _ in range(50)]
            for i, a in enumerate(animals_page2):
                a.to_dict.return_value = {"lpn_id": f"PROG{100 + i}"}
            result2 = MagicMock()
            result2.total_count = 150
            result2.animals = animals_page2
            result2.page = 1
            result2.page_size = 100

            mock_client.get_progeny.side_effect = [result1, result2]
            mock_cls.return_value = mock_client

            client = CachedNSIPClient(cache_dir=tmp_path)
            progeny = client.get_all_progeny("TEST123")

            assert len(progeny) == 150


class TestSearchAnimals:
    """Tests for search_animals method."""

    def test_basic_search(self, tmp_path):
        """Verify basic search."""
        with patch("nsip_skills.common.nsip_wrapper.NSIPClient") as mock_cls:
            mock_client = MagicMock()
            mock_result = MagicMock()
            mock_result.total_count = 10
            mock_result.results = []
            mock_result.page = 0
            mock_result.page_size = 15
            mock_client.search_animals.return_value = mock_result
            mock_cls.return_value = mock_client

            client = CachedNSIPClient(cache_dir=tmp_path)
            result = client.search_animals()

            assert result == mock_result

    def test_search_with_criteria_dict(self, tmp_path):
        """Verify search with dict criteria."""
        with patch("nsip_skills.common.nsip_wrapper.NSIPClient") as mock_cls:
            mock_client = MagicMock()
            mock_result = MagicMock()
            mock_result.total_count = 5
            mock_result.results = []
            mock_result.page = 0
            mock_result.page_size = 15
            mock_client.search_animals.return_value = mock_result
            mock_cls.return_value = mock_client

            client = CachedNSIPClient(cache_dir=tmp_path)
            criteria = {"breed": "Suffolk"}
            client.search_animals(search_criteria=criteria)

            mock_client.search_animals.assert_called_once()

    def test_search_with_criteria_object(self, tmp_path):
        """Verify search with SearchCriteria object."""
        with patch("nsip_skills.common.nsip_wrapper.NSIPClient") as mock_cls:
            mock_client = MagicMock()
            mock_result = MagicMock()
            mock_result.total_count = 5
            mock_result.results = []
            mock_result.page = 0
            mock_result.page_size = 15
            mock_client.search_animals.return_value = mock_result
            mock_cls.return_value = mock_client

            with patch("nsip_client.models.SearchCriteria") as mock_criteria_cls:
                mock_criteria = MagicMock()
                mock_criteria.to_dict.return_value = {"breed": "Suffolk"}
                mock_criteria_cls.return_value = mock_criteria

                client = CachedNSIPClient(cache_dir=tmp_path)
                client.search_animals(search_criteria=mock_criteria)

                mock_client.search_animals.assert_called_once()


class TestGetAvailableBreedGroups:
    """Tests for get_available_breed_groups method."""

    def test_basic_fetch(self, tmp_path):
        """Verify breed groups fetch."""
        with patch("nsip_skills.common.nsip_wrapper.NSIPClient") as mock_cls:
            mock_client = MagicMock()
            mock_bg = MagicMock()
            mock_bg.id = 61
            mock_bg.name = "Range"
            mock_bg.breeds = []
            mock_client.get_available_breed_groups.return_value = [mock_bg]
            mock_cls.return_value = mock_client

            client = CachedNSIPClient(cache_dir=tmp_path)
            result = client.get_available_breed_groups()

            assert len(result) == 1
            assert result[0].id == 61


class TestGetTraitRangesByBreed:
    """Tests for get_trait_ranges_by_breed method."""

    def test_basic_fetch(self, tmp_path):
        """Verify trait ranges fetch."""
        with patch("nsip_skills.common.nsip_wrapper.NSIPClient") as mock_cls:
            mock_client = MagicMock()
            mock_client.get_trait_ranges_by_breed.return_value = {"BWT": {"min": -1.0, "max": 2.0}}
            mock_cls.return_value = mock_client

            client = CachedNSIPClient(cache_dir=tmp_path)
            result = client.get_trait_ranges_by_breed(breed_id=486)

            assert "BWT" in result
            mock_client.get_trait_ranges_by_breed.assert_called_once_with(486)


class TestGetStatusesByBreedGroup:
    """Tests for get_statuses_by_breed_group method."""

    def test_basic_fetch(self, tmp_path):
        """Verify statuses fetch."""
        with patch("nsip_skills.common.nsip_wrapper.NSIPClient") as mock_cls:
            mock_client = MagicMock()
            mock_client.get_statuses_by_breed_group.return_value = ["Active", "Culled"]
            mock_cls.return_value = mock_client

            client = CachedNSIPClient(cache_dir=tmp_path)
            result = client.get_statuses_by_breed_group()

            assert "Active" in result


class TestSearchByLpn:
    """Tests for search_by_lpn method."""

    def test_complete_profile(self, tmp_path):
        """Verify complete profile fetch."""
        with patch("nsip_skills.common.nsip_wrapper.NSIPClient") as mock_cls:
            mock_client = MagicMock()

            mock_details = MagicMock()
            mock_details.to_dict.return_value = {"lpn_id": "TEST123"}
            mock_client.get_animal_details.return_value = mock_details

            mock_lineage = MagicMock()
            mock_lineage.to_dict.return_value = {"sire": "SIRE1"}
            mock_client.get_lineage.return_value = mock_lineage

            mock_progeny = MagicMock()
            mock_progeny.total_count = 5
            mock_progeny.animals = []
            mock_progeny.page = 0
            mock_progeny.page_size = 100
            mock_client.get_progeny.return_value = mock_progeny

            mock_cls.return_value = mock_client

            client = CachedNSIPClient(cache_dir=tmp_path)
            result = client.search_by_lpn("TEST123")

            assert "details" in result
            assert "lineage" in result
            assert "progeny" in result


class TestBatchGetAnimals:
    """Tests for batch_get_animals method."""

    def test_basic_batch(self, tmp_path):
        """Verify basic batch fetch."""
        with patch("nsip_skills.common.nsip_wrapper.NSIPClient") as mock_cls:
            mock_client = MagicMock()
            mock_details = MagicMock()
            mock_details.to_dict.return_value = {"lpn_id": "TEST1"}
            mock_client.get_animal_details.return_value = mock_details
            mock_cls.return_value = mock_client

            client = CachedNSIPClient(cache_dir=tmp_path)
            result = client.batch_get_animals(["TEST1", "TEST2"])

            assert "TEST1" in result
            assert "TEST2" in result

    def test_batch_with_lineage(self, tmp_path):
        """Verify batch with lineage included."""
        with patch("nsip_skills.common.nsip_wrapper.NSIPClient") as mock_cls:
            mock_client = MagicMock()
            mock_details = MagicMock()
            mock_details.to_dict.return_value = {"lpn_id": "TEST1"}
            mock_lineage = MagicMock()
            mock_lineage.to_dict.return_value = {"sire": "SIRE1"}
            mock_client.get_animal_details.return_value = mock_details
            mock_client.get_lineage.return_value = mock_lineage
            mock_cls.return_value = mock_client

            client = CachedNSIPClient(cache_dir=tmp_path)
            result = client.batch_get_animals(["TEST1"], include_lineage=True)

            assert "lineage" in result["TEST1"]

    def test_batch_with_progeny(self, tmp_path):
        """Verify batch with progeny included."""
        with patch("nsip_skills.common.nsip_wrapper.NSIPClient") as mock_cls:
            mock_client = MagicMock()
            mock_details = MagicMock()
            mock_details.to_dict.return_value = {"lpn_id": "TEST1"}
            mock_progeny = MagicMock()
            mock_progeny.total_count = 0
            mock_progeny.animals = []
            mock_progeny.page = 0
            mock_progeny.page_size = 100
            mock_client.get_animal_details.return_value = mock_details
            mock_client.get_progeny.return_value = mock_progeny
            mock_cls.return_value = mock_client

            client = CachedNSIPClient(cache_dir=tmp_path)
            result = client.batch_get_animals(["TEST1"], include_progeny=True)

            assert "progeny" in result["TEST1"]

    def test_batch_error_skip(self, tmp_path):
        """Verify errors are skipped by default."""
        with patch("nsip_skills.common.nsip_wrapper.NSIPClient") as mock_cls:
            from nsip_client.exceptions import NSIPNotFoundError

            mock_client = MagicMock()
            mock_client.get_animal_details.side_effect = NSIPNotFoundError("Not found")
            mock_cls.return_value = mock_client

            client = CachedNSIPClient(cache_dir=tmp_path)
            result = client.batch_get_animals(["MISSING"])

            assert "error" in result["MISSING"]

    def test_batch_error_raise(self, tmp_path):
        """Verify errors are raised when on_error='raise'."""
        with patch("nsip_skills.common.nsip_wrapper.NSIPClient") as mock_cls:
            from nsip_client.exceptions import NSIPNotFoundError

            mock_client = MagicMock()
            mock_client.get_animal_details.side_effect = NSIPNotFoundError("Not found")
            mock_cls.return_value = mock_client

            client = CachedNSIPClient(cache_dir=tmp_path)
            with pytest.raises(NSIPNotFoundError):
                client.batch_get_animals(["MISSING"], on_error="raise")

    def test_batch_api_error_skip(self, tmp_path):
        """Verify API errors are skipped."""
        with patch("nsip_skills.common.nsip_wrapper.NSIPClient") as mock_cls:
            from nsip_client.exceptions import NSIPError

            mock_client = MagicMock()
            mock_client.get_animal_details.side_effect = NSIPError("API error")
            mock_cls.return_value = mock_client

            client = CachedNSIPClient(cache_dir=tmp_path)
            result = client.batch_get_animals(["FAIL"])

            assert "error" in result["FAIL"]

    def test_batch_api_error_raise(self, tmp_path):
        """Verify API errors are raised when on_error='raise'."""
        with patch("nsip_skills.common.nsip_wrapper.NSIPClient") as mock_cls:
            from nsip_client.exceptions import NSIPError

            mock_client = MagicMock()
            mock_client.get_animal_details.side_effect = NSIPError("API error")
            mock_cls.return_value = mock_client

            client = CachedNSIPClient(cache_dir=tmp_path)
            with pytest.raises(NSIPError):
                client.batch_get_animals(["FAIL"], on_error="raise")


class TestContextManager:
    """Tests for context manager support."""

    def test_enter_returns_self(self, tmp_path):
        """Verify __enter__ returns client."""
        with patch("nsip_skills.common.nsip_wrapper.NSIPClient"):
            client = CachedNSIPClient(cache_dir=tmp_path)
            result = client.__enter__()
            assert result is client

    def test_exit_closes_client(self, tmp_path):
        """Verify __exit__ closes underlying client."""
        with patch("nsip_skills.common.nsip_wrapper.NSIPClient") as mock_cls:
            mock_client = MagicMock()
            mock_cls.return_value = mock_client

            with CachedNSIPClient(cache_dir=tmp_path):
                pass

            mock_client.close.assert_called_once()

    def test_with_statement(self, tmp_path):
        """Verify with statement works correctly."""
        with patch("nsip_skills.common.nsip_wrapper.NSIPClient") as mock_cls:
            mock_client = MagicMock()
            mock_cls.return_value = mock_client

            with CachedNSIPClient(cache_dir=tmp_path) as client:
                assert client is not None

            mock_client.close.assert_called_once()

    def test_close_method(self, tmp_path):
        """Verify close method calls underlying client."""
        with patch("nsip_skills.common.nsip_wrapper.NSIPClient") as mock_cls:
            mock_client = MagicMock()
            mock_cls.return_value = mock_client

            client = CachedNSIPClient(cache_dir=tmp_path)
            client.close()

            mock_client.close.assert_called_once()
