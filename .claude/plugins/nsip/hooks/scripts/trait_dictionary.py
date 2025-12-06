#!/usr/bin/env python3
"""
Trait Dictionary Hook (PreToolUse)
Inject breeding terminology and trait definitions for NSIP queries.

Note: This hook provides minimal context since Opus 4.5 already has
comprehensive knowledge of NSIP traits. Only inject when specific
traits are detected in parameters.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List

# Add script directory to path for sibling module imports
sys.path.insert(0, str(Path(__file__).parent))

from _config import config
from nsip_types import PreToolUseInput, HookOutput, TraitDefinition
from _exceptions import NSIPHookError


# Core NSIP traits (subset - Opus 4.5 knows the full set)
TRAITS: Dict[str, TraitDefinition] = {
    "WWT": {"name": "Weaning Weight", "unit": "kg", "description": "Weight at weaning (~100 days)"},
    "PWWT": {"name": "Post-Weaning Weight", "unit": "kg", "description": "Weight gain after weaning"},
    "YWT": {"name": "Yearling Weight", "unit": "kg", "description": "Weight at ~12 months"},
    "PEMD": {"name": "Eye Muscle Depth", "unit": "mm", "description": "Ultrasound loin measurement"},
    "PFAT": {"name": "Fat Depth", "unit": "mm", "description": "Fat over loin"},
    "FEC": {"name": "Faecal Egg Count", "unit": "epg", "description": "Parasite resistance"},
    "CFW": {"name": "Clean Fleece Weight", "unit": "kg", "description": "Wool production"},
    "FD": {"name": "Fiber Diameter", "unit": "microns", "description": "Wool fineness"},
    "NLB": {"name": "Lambs Born", "unit": "count", "description": "Reproductive trait"},
    "NLW": {"name": "Lambs Weaned", "unit": "count", "description": "Maternal ability"},
}


def detect_mentioned_traits(parameters: dict) -> List[str]:
    """Detect which traits are mentioned in parameters."""
    param_str = json.dumps(parameters, default=str).upper()
    return [code for code in TRAITS if code in param_str]


def build_context(detected_traits: List[str]) -> str:
    """Build minimal context for detected traits."""
    if not detected_traits:
        return ""

    lines = ["Trait reference:"]
    for code in detected_traits[:3]:  # Max 3 to avoid bloat
        t = TRAITS[code]
        lines.append(f"  {code}: {t['name']} ({t['unit']})")

    return "\n".join(lines)


def main():
    """Process PreToolUse hook for trait dictionary."""
    try:
        hook_data: PreToolUseInput = json.loads(sys.stdin.read())

        tool_name = hook_data.get("tool", {}).get("name", "")
        tool_params = hook_data.get("tool", {}).get("parameters", {})

        if not tool_name.startswith("mcp__nsip__"):
            output: HookOutput = {
                "continue": True,
                "metadata": {"context_injected": False, "reason": "Not an NSIP tool"}
            }
            print(json.dumps(output))
            sys.exit(0)

        detected = detect_mentioned_traits(tool_params)
        context_msg = build_context(detected)

        output: HookOutput = {
            "continue": True,
            "metadata": {
                "context_injected": bool(detected),
                "detected_traits": detected
            }
        }

        if context_msg:
            output["context"] = context_msg

        print(json.dumps(output))

    except json.JSONDecodeError as e:
        output: HookOutput = {
            "continue": True,
            "metadata": {"context_injected": False, "error": f"Invalid JSON: {e}"}
        }
        print(json.dumps(output))

    sys.exit(0)


if __name__ == "__main__":
    main()
