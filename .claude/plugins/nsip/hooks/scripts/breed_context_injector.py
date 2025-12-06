#!/usr/bin/env python3
"""
Breed Context Injector Hook (PreToolUse)
Inject breed-specific context before searches and queries.
Triggers on: mcp__nsip__nsip_search_animals, mcp__nsip__nsip_get_trait_ranges
"""

import json
import sys
from pathlib import Path
from typing import Dict, Optional

# Add script directory to path for sibling module imports
sys.path.insert(0, str(Path(__file__).parent))

from _config import config
from nsip_types import PreToolUseInput, HookOutput, BreedInfo
from _exceptions import NSIPHookError


# Static breed information database
BREED_DATA: Dict[str, BreedInfo] = {
    "1": {
        "name": "Merino",
        "characteristics": "fine wool production, adapted to various climates",
        "key_traits": ["fleece weight", "fiber diameter", "staple length"],
        "breeding_focus": "wool quality and quantity"
    },
    "2": {
        "name": "Border Leicester",
        "characteristics": "maternal breed, good milk production, easy lambing",
        "key_traits": ["maternal ability", "growth rate", "carcass quality"],
        "breeding_focus": "maternal characteristics and lamb growth"
    },
    "3": {
        "name": "Poll Dorset",
        "characteristics": "terminal sire breed, excellent meat production",
        "key_traits": ["growth rate", "muscle depth", "fat depth"],
        "breeding_focus": "meat production and carcass quality"
    },
    "4": {
        "name": "White Suffolk",
        "characteristics": "terminal sire breed, rapid growth, good conformation",
        "key_traits": ["post-weaning weight", "eye muscle depth", "fat depth"],
        "breeding_focus": "meat production and growth rate"
    },
    "5": {
        "name": "Dorper",
        "characteristics": "hair sheep, adapted to harsh conditions, good meat",
        "key_traits": ["weaning weight", "adaptation", "meat quality"],
        "breeding_focus": "adaptability and meat production"
    },
    "6": {
        "name": "Corriedale",
        "characteristics": "dual-purpose breed, wool and meat production",
        "key_traits": ["fleece weight", "body weight", "fiber diameter"],
        "breeding_focus": "balanced wool and meat production"
    }
}


def get_breed_info(breed_id: str) -> Optional[BreedInfo]:
    """Get breed information from static data or cache."""
    if breed_id in BREED_DATA:
        return BREED_DATA[breed_id]

    # Check cache for custom breed data
    cache_file = config.CACHE_DIR / "breeds" / f"breed_{breed_id}.json"
    if cache_file.exists():
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            pass

    return None


def format_breed_context(breed_info: BreedInfo) -> str:
    """Format breed information as context message."""
    name = breed_info.get("name", "Unknown")
    chars = breed_info.get("characteristics", "")
    traits = breed_info.get("key_traits", [])
    focus = breed_info.get("breeding_focus", "")

    parts = [f"Breed: {name}."]
    if chars:
        parts.append(f"Known for: {chars}.")
    if traits:
        parts.append(f"Key traits: {', '.join(traits)}.")
    if focus:
        parts.append(f"Focus: {focus}.")

    return " ".join(parts)


def inject_context(parameters: dict) -> Dict:
    """Inject breed context based on parameters."""
    breed_id = None

    for param_name in ["breed_id", "breedId", "breed", "Breed"]:
        if param_name in parameters:
            breed_id = str(parameters[param_name])
            break

    if not breed_id:
        return {"context_injected": False, "reason": "No breed_id in parameters"}

    breed_info = get_breed_info(breed_id)

    if not breed_info:
        return {"context_injected": False, "reason": f"Unknown breed_id: {breed_id}"}

    return {
        "context_injected": True,
        "breed_id": breed_id,
        "breed_name": breed_info.get("name", "Unknown"),
        "context_message": format_breed_context(breed_info)
    }


def main():
    """Process PreToolUse hook for breed context injection."""
    try:
        hook_data: PreToolUseInput = json.loads(sys.stdin.read())

        tool = hook_data.get("tool") or {}
        tool_name = tool.get("name", "") if isinstance(tool, dict) else ""
        tool_params = tool.get("parameters") or {} if isinstance(tool, dict) else {}

        relevant_tools = ["search_animals", "get_trait_ranges"]
        is_relevant = any(tool in tool_name.lower() for tool in relevant_tools)

        if not is_relevant:
            output: HookOutput = {
                "continue": True,
                "metadata": {"context_injected": False, "reason": "Not a relevant tool"}
            }
            print(json.dumps(output))
            sys.exit(0)

        result = inject_context(tool_params)

        output: HookOutput = {"continue": True, "metadata": result}

        if result.get("context_message"):
            output["context"] = result["context_message"]

        print(json.dumps(output))

    except json.JSONDecodeError as e:
        output: HookOutput = {
            "continue": True,
            "metadata": {"context_injected": False, "error": f"Invalid JSON: {e}"}
        }
        print(json.dumps(output))

    except Exception as e:
        # Catch-all for any unexpected errors - always continue (fail-safe)
        output: HookOutput = {
            "continue": True,
            "metadata": {"context_injected": False, "error": str(e)}
        }
        print(json.dumps(output))

    sys.exit(0)


if __name__ == "__main__":
    main()
