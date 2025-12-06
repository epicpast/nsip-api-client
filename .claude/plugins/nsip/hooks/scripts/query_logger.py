#!/usr/bin/env python3
"""
Query Logger Hook (PostToolUse)
Logs all NSIP API calls with timestamps for audit and debugging.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Add script directory to path for sibling module imports
sys.path.insert(0, str(Path(__file__).parent))

from _config import config
from nsip_types import PostToolUseInput, HookOutput


def log_query(tool_name: str, parameters: dict, result: dict, duration_ms: float = None) -> None:
    """Log a query to the JSONL log file."""
    config.LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = config.LOG_DIR / "query_log.jsonl"

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "tool": tool_name,
        "parameters": parameters,
        "success": not result.get("isError", False),
        "error": result.get("error"),
        "result_size": len(json.dumps(result)),
        "duration_ms": duration_ms
    }

    # Redact sensitive data if any
    if "api_key" in log_entry["parameters"]:
        log_entry["parameters"]["api_key"] = "***REDACTED***"

    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
    except OSError:
        pass


def main():
    """Process PostToolUse hook for query logging."""
    try:
        hook_data: PostToolUseInput = json.loads(sys.stdin.read())

        tool = hook_data.get("tool") or {}
        tool_name = tool.get("name", "unknown") if isinstance(tool, dict) else "unknown"
        tool_params = tool.get("parameters") or {} if isinstance(tool, dict) else {}
        tool_result = hook_data.get("result") or {}
        metadata = hook_data.get("metadata") or {}
        duration_ms = metadata.get("duration_ms") if isinstance(metadata, dict) else None

        log_query(tool_name, tool_params, tool_result, duration_ms)

        output: HookOutput = {
            "continue": True,
            "metadata": {
                "logged": True,
                "log_file": str(config.LOG_DIR / "query_log.jsonl"),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        }

        print(json.dumps(output))

    except json.JSONDecodeError as e:
        output: HookOutput = {
            "continue": True,
            "metadata": {"logged": False, "error": f"Invalid JSON: {e}"}
        }
        print(json.dumps(output))

    except Exception as e:
        # Catch-all for any unexpected errors - always continue (fail-safe)
        output: HookOutput = {
            "continue": True,
            "metadata": {"logged": False, "error": str(e)}
        }
        print(json.dumps(output))

    sys.exit(0)


if __name__ == "__main__":
    main()
