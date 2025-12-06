#!/usr/bin/env python3
"""
Breeding Report Hook (PostToolUse)
Generate formatted breeding reports with trait analysis.
Triggers on: mcp__nsip__nsip_get_animal, mcp__nsip__nsip_search_by_lpn
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

# Add script directory to path for sibling module imports
sys.path.insert(0, str(Path(__file__).parent))

from _config import config
from nsip_types import PostToolUseInput, HookOutput
from _exceptions import ExportError


class BreedingReportGenerator:
    """Generate comprehensive breeding reports in Markdown format."""

    def __init__(self):
        """Initialize report generator."""
        config.EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    def _extract_animal_data(self, result: dict) -> Optional[Dict]:
        """Extract animal data from tool result."""
        try:
            if "content" in result:
                content = result["content"]
                if isinstance(content, list) and len(content) > 0:
                    if isinstance(content[0], dict) and "text" in content[0]:
                        text_data = content[0]["text"]
                        if isinstance(text_data, str):
                            return json.loads(text_data)
                        return text_data
            return result
        except (json.JSONDecodeError, KeyError, IndexError):
            return None

    def _format_basic_info(self, animal: dict) -> str:
        """Format basic animal information section."""
        return "\n".join([
            "## Basic Information", "",
            f"- **LPN ID:** {animal.get('LPN', 'Unknown')}",
            f"- **Name:** {animal.get('AnimalName', 'Unnamed')}",
            f"- **Breed:** {animal.get('Breed', 'Unknown')}",
            f"- **Sex:** {animal.get('Sex', 'Unknown')}",
            f"- **Birth Date:** {animal.get('BirthDate', 'Unknown')}",
            f"- **Status:** {animal.get('Status', 'Unknown')}"
        ])

    def _format_traits(self, animal: dict) -> str:
        """Format trait information section."""
        trait_fields = {
            "WWT": "Weaning Weight", "PWWT": "Post-Weaning Weight",
            "YWT": "Yearling Weight", "PEMD": "Eye Muscle Depth",
            "PFEC": "Parasite Resistance", "NFAT": "Fat Depth"
        }

        lines = ["## Production Traits", ""]
        found = False

        for field, label in trait_fields.items():
            if field in animal and animal[field]:
                val = animal[field]
                lines.append(f"- **{label}:** {val:.2f}" if isinstance(val, float) else f"- **{label}:** {val}")
                found = True

        if not found:
            lines.append("*No trait data available*")

        return "\n".join(lines)

    def _format_ebvs(self, animal: dict) -> str:
        """Format breeding value section."""
        lines = ["## Breeding Values (EBVs)", ""]

        ebvs = {k: v for k, v in animal.items() if "EBV" in k.upper() or "BV" in k.upper()}

        if ebvs:
            for field, val in sorted(ebvs.items()):
                lines.append(f"- **{field}:** {val:.3f}" if isinstance(val, float) else f"- **{field}:** {val}")
        else:
            lines.append("*No breeding values available*")

        return "\n".join(lines)

    def generate_report(self, result: dict) -> Optional[str]:
        """Generate and save breeding report."""
        animal = self._extract_animal_data(result)
        if not animal:
            return None

        try:
            name = animal.get("AnimalName", "Unnamed")
            lpn = animal.get("LPN", "Unknown")

            report = "\n\n".join([
                f"# Breeding Report: {name} ({lpn})",
                f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC",
                "---",
                self._format_basic_info(animal),
                self._format_traits(animal),
                self._format_ebvs(animal),
                "---",
                "*Report generated automatically. Review with breeding specialist.*"
            ])

            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filepath = config.EXPORT_DIR / f"breeding_report_{timestamp}.md"

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(report)

            return str(filepath)

        except OSError as e:
            raise ExportError(f"Failed to save report: {e}")


def main():
    """Process PostToolUse hook for breeding report generation."""
    try:
        hook_data: PostToolUseInput = json.loads(sys.stdin.read())

        tool_name = hook_data.get("tool", {}).get("name", "")
        tool_result = hook_data.get("result", {})

        is_animal_query = any(kw in tool_name.lower() for kw in ["get_animal", "search_by_lpn"])

        if not is_animal_query:
            output: HookOutput = {
                "continue": True,
                "metadata": {"report_generated": False, "reason": "Not an animal query"}
            }
            print(json.dumps(output))
            sys.exit(0)

        if tool_result.get("isError", False):
            output: HookOutput = {
                "continue": True,
                "metadata": {"report_generated": False, "reason": "Tool returned error"}
            }
            print(json.dumps(output))
            sys.exit(0)

        generator = BreedingReportGenerator()
        filepath = generator.generate_report(tool_result)

        if filepath:
            output: HookOutput = {
                "continue": True,
                "metadata": {"report_generated": True, "export_path": filepath}
            }
        else:
            output: HookOutput = {
                "continue": True,
                "metadata": {"report_generated": False, "reason": "Failed to generate"}
            }

        print(json.dumps(output))

    except json.JSONDecodeError as e:
        output: HookOutput = {
            "continue": True,
            "metadata": {"report_generated": False, "error": f"Invalid JSON: {e}"}
        }
        print(json.dumps(output))

    except ExportError as e:
        output: HookOutput = {
            "continue": True,
            "metadata": {"report_generated": False, "error": str(e)}
        }
        print(json.dumps(output))

    sys.exit(0)


if __name__ == "__main__":
    main()
