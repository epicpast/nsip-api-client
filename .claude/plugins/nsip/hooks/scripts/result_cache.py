#!/usr/bin/env python3
"""
Result Cache Hook (PostToolUse)
Caches frequently accessed animal data to improve performance and reduce API load.
"""

import json
import sys
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict

# Add script directory to path for sibling module imports
sys.path.insert(0, str(Path(__file__).parent))

from _config import config
from nsip_types import PostToolUseInput, HookOutput, CacheEntry
from _exceptions import CacheWriteError


CACHEABLE_TOOLS = [
    "nsip_get_animal",
    "nsip_search_by_lpn",
    "nsip_get_lineage",
    "nsip_get_progeny"
]


class ResultCache:
    """Simple file-based cache for NSIP results."""

    def __init__(self):
        """Initialize cache."""
        config.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(minutes=config.CACHE_TTL_MINUTES)

    def _get_cache_key(self, tool_name: str, parameters: dict) -> str:
        """Generate cache key from tool name and parameters."""
        param_str = json.dumps(parameters, sort_keys=True)
        key_str = f"{tool_name}:{param_str}"
        return hashlib.sha256(key_str.encode()).hexdigest()

    def _get_cache_path(self, cache_key: str):
        """Get path to cache file."""
        return config.CACHE_DIR / f"{cache_key}.json"

    def get(self, tool_name: str, parameters: dict) -> Optional[dict]:
        """Get cached result if available and not expired."""
        cache_key = self._get_cache_key(tool_name, parameters)
        cache_path = self._get_cache_path(cache_key)

        if not cache_path.exists():
            return None

        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                entry: CacheEntry = json.load(f)

            cached_at = datetime.fromisoformat(entry["cached_at"].rstrip("Z"))
            if datetime.utcnow() - cached_at > self.ttl:
                cache_path.unlink()
                return None

            return entry["result"]

        except (OSError, json.JSONDecodeError, KeyError, ValueError):
            return None

    def set(self, tool_name: str, parameters: dict, result: dict) -> None:
        """Store result in cache."""
        cache_key = self._get_cache_key(tool_name, parameters)
        cache_path = self._get_cache_path(cache_key)

        try:
            entry: CacheEntry = {
                "tool": tool_name,
                "parameters": parameters,
                "result": result,
                "cached_at": datetime.utcnow().isoformat() + "Z"
            }

            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(entry, f, indent=2)

        except OSError:
            pass

    def get_stats(self) -> Dict:
        """Get cache statistics."""
        cache_files = list(config.CACHE_DIR.glob("*.json"))
        total_size = sum(f.stat().st_size for f in cache_files if f.exists())

        return {
            "entries": len(cache_files),
            "total_size_bytes": total_size,
            "cache_dir": str(config.CACHE_DIR),
            "max_entries": config.CACHE_MAX_ENTRIES,
            "ttl_minutes": config.CACHE_TTL_MINUTES
        }


def should_cache_tool(tool_name: str) -> bool:
    """Determine if a tool's results should be cached."""
    base_name = tool_name.replace("mcp__nsip__", "")
    return base_name in CACHEABLE_TOOLS


def main():
    """Process PostToolUse hook for result caching."""
    try:
        hook_data: PostToolUseInput = json.loads(sys.stdin.read())

        tool_name = hook_data.get("tool", {}).get("name", "")
        tool_params = hook_data.get("tool", {}).get("parameters", {})
        tool_result = hook_data.get("result", {})

        cache = ResultCache()

        if should_cache_tool(tool_name) and not tool_result.get("isError", False):
            cache.set(tool_name, tool_params, tool_result)

            output: HookOutput = {
                "continue": True,
                "metadata": {
                    "cached": True,
                    "cache_stats": cache.get_stats()
                }
            }
        else:
            output: HookOutput = {
                "continue": True,
                "metadata": {
                    "cached": False,
                    "reason": "Not cacheable or error result"
                }
            }

        print(json.dumps(output))

    except json.JSONDecodeError as e:
        output: HookOutput = {
            "continue": True,
            "metadata": {"cached": False, "error": f"Invalid JSON: {e}"}
        }
        print(json.dumps(output))

    except CacheWriteError as e:
        output: HookOutput = {
            "continue": True,
            "metadata": {"cached": False, "error": str(e)}
        }
        print(json.dumps(output))


if __name__ == "__main__":
    main()
