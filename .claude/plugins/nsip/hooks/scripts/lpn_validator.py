#!/usr/bin/env python3
"""
LPN Validator Hook (PreToolUse)
Validates LPN ID format before making NSIP API calls to prevent errors.
"""

import json
import sys
from pathlib import Path

# Add script directory to path for sibling module imports
sys.path.insert(0, str(Path(__file__).parent))

from _config import config
from nsip_types import PreToolUseInput, HookOutput
from _validation import LPNValidator, LPNValidationResult, extract_lpn_from_params
from _exceptions import LPNValidationError


def main():
    """Process PreToolUse hook for LPN validation."""
    try:
        hook_data: PreToolUseInput = json.loads(sys.stdin.read())

        tool = hook_data.get("tool") or {}
        tool_name = tool.get("name", "") if isinstance(tool, dict) else ""
        tool_params = tool.get("parameters") or {} if isinstance(tool, dict) else {}

        # Extract LPN ID from parameters
        lpn_id = extract_lpn_from_params(tool_params)

        # If no LPN ID found, allow the call to proceed
        if lpn_id is None:
            output: HookOutput = {
                "continue": True,
                "metadata": {
                    "validation": "skipped",
                    "reason": "No LPN ID parameter found"
                }
            }
            print(json.dumps(output))
            return

        # Validate the LPN ID
        validator = LPNValidator()
        result: LPNValidationResult = validator.validate(str(lpn_id))

        if result.is_valid:
            output: HookOutput = {
                "continue": True,
                "metadata": {
                    "validation": "passed",
                    "lpn_id": result.normalized,
                    "tool": tool_name
                }
            }
        else:
            output: HookOutput = {
                "continue": False,
                "error": result.error_message,
                "metadata": {
                    "validation": "failed",
                    "lpn_id": lpn_id,
                    "tool": tool_name
                }
            }

        print(json.dumps(output))

    except json.JSONDecodeError as e:
        output: HookOutput = {
            "continue": True,
            "metadata": {"validation": "error", "error": f"Invalid JSON: {e}"}
        }
        print(json.dumps(output))

    except LPNValidationError as e:
        output: HookOutput = {
            "continue": False,
            "error": str(e),
            "metadata": {"validation": "error"}
        }
        print(json.dumps(output))

    except Exception as e:
        # Catch-all for any unexpected errors - always continue (fail-safe)
        output: HookOutput = {
            "continue": True,
            "metadata": {"validation": "skipped", "error": str(e)}
        }
        print(json.dumps(output))

    sys.exit(0)


if __name__ == "__main__":
    main()
