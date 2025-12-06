#!/usr/bin/env python3
"""
Fallback Cache Hook (PostToolUse)
Provide cached data when API calls fail.
"""

import json
import sys
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict

# Add script directory to path for sibling module imports
sys.path.insert(0, str(Path(__file__).parent))

from _config import config
from nsip_types import PostToolUseInput, HookOutput, CacheEntry
from _exceptions import CacheReadError


class FallbackCacheHandler:
    """Handle fallback to cached data on API failures."""

    def __init__(self):
        """Initialize fallback cache handler."""
        config.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        config.LOG_DIR.mkdir(parents=True, exist_ok=True)
        self.log_file = config.LOG_DIR / "fallback_log.jsonl"

    def _log_fallback(self, entry: dict) -> None:
        """Log fallback usage to JSONL file."""
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except OSError:
            pass

    def _is_failure(self, result: dict) -> bool:
        """Determine if result indicates a failure."""
        if result.get("isError", False):
            return True

        content = result.get("content", [])
        if not content:
            return True

        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict):
                    text = item.get("text", "")
                    if isinstance(text, str) and ("error" in text.lower() or "failed" in text.lower()):
                        return True

        return False

    def _get_cache_key(self, tool_name: str, parameters: dict) -> str:
        """Generate cache key from tool name and parameters."""
        param_str = json.dumps(parameters, sort_keys=True)
        key_str = f"{tool_name}:{param_str}"
        return hashlib.sha256(key_str.encode()).hexdigest()

    def _load_cached_data(self, tool_name: str, parameters: dict) -> Optional[CacheEntry]:
        """Load cached data for given tool and parameters."""
        try:
            cache_key = self._get_cache_key(tool_name, parameters)
            cache_path = config.CACHE_DIR / f"{cache_key}.json"

            if not cache_path.exists():
                return None

            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)

        except (OSError, json.JSONDecodeError):
            return None

    def handle_fallback(self, tool_name: str, parameters: dict, result: dict) -> Dict:
        """Handle fallback to cached data if API failed."""
        if not self._is_failure(result):
            return {"fallback_used": False, "reason": "No failure detected"}

        cached = self._load_cached_data(tool_name, parameters)

        if not cached:
            self._log_fallback({
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "tool": tool_name,
                "status": "no_cache_available"
            })
            return {"fallback_used": False, "reason": "No cached data available"}

        cached_at = cached.get("cached_at", "Unknown")

        # Calculate cache age
        try:
            cached_time = datetime.fromisoformat(cached_at.rstrip("Z"))
            age_seconds = (datetime.utcnow() - cached_time).total_seconds()
            age_minutes = int(age_seconds / 60)
            age_hours = int(age_minutes / 60)
            age_str = f"{age_hours}h" if age_hours > 0 else f"{age_minutes}m"
        except (ValueError, TypeError):
            age_str = "unknown"

        self._log_fallback({
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "tool": tool_name,
            "cached_at": cached_at,
            "cache_age": age_str,
            "status": "fallback_used"
        })

        return {
            "fallback_used": True,
            "cached_at": cached_at,
            "cache_age": age_str,
            "cached_result": cached.get("result", {}),
            "context_message": f"Using cached data ({age_str} old). Data may be outdated."
        }


def main():
    """Process PostToolUse hook for fallback cache."""
    try:
        hook_data: PostToolUseInput = json.loads(sys.stdin.read())

        tool_name = hook_data.get("tool", {}).get("name", "")
        tool_params = hook_data.get("tool", {}).get("parameters", {})
        tool_result = hook_data.get("result", {})

        if not tool_name.startswith("mcp__nsip__"):
            output: HookOutput = {
                "continue": True,
                "metadata": {"fallback_checked": False, "reason": "Not an NSIP tool"}
            }
            print(json.dumps(output))
            sys.exit(0)

        handler = FallbackCacheHandler()
        fallback_result = handler.handle_fallback(tool_name, tool_params, tool_result)

        output: HookOutput = {
            "continue": True,
            "metadata": {"fallback_checked": True, **fallback_result}
        }

        if fallback_result.get("context_message"):
            output["context"] = fallback_result["context_message"]

        print(json.dumps(output))

    except json.JSONDecodeError as e:
        output: HookOutput = {
            "continue": True,
            "metadata": {"fallback_checked": False, "error": f"Invalid JSON: {e}"}
        }
        print(json.dumps(output))

    except CacheReadError as e:
        output: HookOutput = {
            "continue": True,
            "metadata": {"fallback_checked": False, "error": str(e)}
        }
        print(json.dumps(output))

    sys.exit(0)


if __name__ == "__main__":
    main()
