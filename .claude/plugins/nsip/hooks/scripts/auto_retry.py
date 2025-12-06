#!/usr/bin/env python3
"""
Auto Retry Hook (PostToolUse)
Detect API failures and log retry recommendations.

Note: Hooks cannot re-invoke tools. This hook logs failures and provides
retry recommendations; actual retry must be handled by Claude.
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple

# Add script directory to path for sibling module imports
sys.path.insert(0, str(Path(__file__).parent))

from _config import config
from nsip_types import PostToolUseInput, HookOutput, RetryResult
from _exceptions import RetryExhaustedError


class AutoRetryHandler:
    """Handle automatic retry logic for failed API calls."""

    def __init__(self):
        """Initialize retry handler."""
        config.LOG_DIR.mkdir(parents=True, exist_ok=True)
        self.log_file = config.LOG_DIR / "retry_log.jsonl"

    def _log_retry(self, entry: dict) -> None:
        """Log retry attempt to JSONL file."""
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except OSError:
            pass

    def _is_failure(self, result: dict) -> Tuple[bool, str]:
        """Determine if result indicates a failure."""
        if result.get("isError", False):
            return True, f"Error flag: {result.get('error', 'Unknown error')}"

        content = result.get("content", [])
        if not content:
            return True, "Empty content returned"

        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict):
                    text = item.get("text", "")
                    if isinstance(text, str) and ("error" in text.lower() or "failed" in text.lower()):
                        return True, f"Error in response: {text[:100]}"

        if "timeout" in str(result).lower():
            return True, "Timeout detected"

        return False, ""

    def handle_failure(self, tool_name: str, parameters: dict, result: dict) -> RetryResult:
        """Handle failed tool execution with retry recommendation."""
        is_failure, reason = self._is_failure(result)

        if not is_failure:
            return {
                "retry_needed": False,
                "retry_count": 0,
                "status": "success",
                "reason": "No failure detected"
            }

        # Log the failure
        self._log_retry({
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "tool": tool_name,
            "parameters": parameters,
            "status": "failed",
            "failure_reason": reason,
            "max_retries": config.RETRY_MAX_ATTEMPTS,
            "backoff_delays": list(config.RETRY_BACKOFF_SECONDS)
        })

        return {
            "retry_needed": True,
            "retry_count": 0,
            "status": "failed",
            "reason": reason,
            "context_message": (
                f"API call failed: {reason}. "
                f"Retry recommended with backoff delays: {config.RETRY_BACKOFF_SECONDS}s"
            )
        }


def main():
    """Process PostToolUse hook for auto-retry."""
    try:
        hook_data: PostToolUseInput = json.loads(sys.stdin.read())

        tool = hook_data.get("tool") or {}
        tool_name = tool.get("name", "") if isinstance(tool, dict) else ""
        tool_params = tool.get("parameters") or {} if isinstance(tool, dict) else {}
        tool_result = hook_data.get("result") or {}

        # Only handle NSIP tools
        if not tool_name.startswith("mcp__nsip__"):
            output: HookOutput = {
                "continue": True,
                "metadata": {"retry_handled": False, "reason": "Not an NSIP tool"}
            }
            print(json.dumps(output))
            sys.exit(0)

        handler = AutoRetryHandler()
        retry_result = handler.handle_failure(tool_name, tool_params, tool_result)

        output: HookOutput = {
            "continue": True,
            "metadata": {"retry_handled": True, **retry_result}
        }

        if retry_result.get("context_message"):
            output["context"] = retry_result["context_message"]

        print(json.dumps(output))

    except json.JSONDecodeError as e:
        output: HookOutput = {
            "continue": True,
            "metadata": {"retry_handled": False, "error": f"Invalid JSON: {e}"}
        }
        print(json.dumps(output))

    except Exception as e:
        # Catch-all for any unexpected errors - always continue (fail-safe)
        output: HookOutput = {
            "continue": True,
            "metadata": {"retry_handled": False, "error": str(e)}
        }
        print(json.dumps(output))

    sys.exit(0)


if __name__ == "__main__":
    main()
