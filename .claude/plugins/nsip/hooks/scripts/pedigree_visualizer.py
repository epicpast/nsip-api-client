#!/usr/bin/env python3
"""
Pedigree Visualizer Hook (PostToolUse)
Generate visual family tree diagrams from lineage data.
Triggers on: mcp__nsip__nsip_get_lineage
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


class PedigreeVisualizer:
    """Generate ASCII and text-based pedigree visualizations."""

    def __init__(self):
        """Initialize visualizer."""
        config.EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    def _extract_lineage_data(self, result: dict) -> Optional[Dict]:
        """Extract lineage data from tool result."""
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

    def _format_animal_info(self, animal: dict) -> str:
        """Format animal information for display."""
        lpn = animal.get("LPN", "Unknown")
        name = animal.get("AnimalName", "Unnamed")
        breed = animal.get("Breed", "")
        return f"{name} ({lpn}) [{breed}]" if breed else f"{name} ({lpn})"

    def _generate_ascii_tree(self, lineage: dict) -> str:
        """Generate ASCII art family tree."""
        lines = ["=" * 80, "PEDIGREE VISUALIZATION", "=" * 80, ""]

        subject = lineage.get("subject", {})
        if subject:
            lines.extend(["Subject Animal:", f"  {self._format_animal_info(subject)}", ""])

        sire = lineage.get("sire", {})
        dam = lineage.get("dam", {})

        if sire or dam:
            lines.append("Parents (Generation 1):")
            lines.append(f"  Sire:  {self._format_animal_info(sire)}" if sire else "  Sire:  Unknown")
            lines.append(f"  Dam:   {self._format_animal_info(dam)}" if dam else "  Dam:   Unknown")
            lines.append("")

        grandparents = lineage.get("grandparents", {})
        if grandparents:
            lines.append("Grandparents (Generation 2):")
            for prefix, label in [("sire", "Paternal"), ("dam", "Maternal")]:
                gp_sire = grandparents.get(f"{prefix}_sire", {})
                gp_dam = grandparents.get(f"{prefix}_dam", {})
                if gp_sire or gp_dam:
                    lines.append(f"  {label}:")
                    if gp_sire:
                        lines.append(f"    Sire: {self._format_animal_info(gp_sire)}")
                    if gp_dam:
                        lines.append(f"    Dam:  {self._format_animal_info(gp_dam)}")
            lines.append("")

        total = sum([
            bool(sire), bool(dam),
            bool(grandparents.get("sire_sire")), bool(grandparents.get("sire_dam")),
            bool(grandparents.get("dam_sire")), bool(grandparents.get("dam_dam"))
        ])
        lines.extend([f"Total Ancestors Identified: {total}", "=" * 80])

        return "\n".join(lines)

    def _generate_hierarchy(self, lineage: dict) -> str:
        """Generate simple text hierarchy."""
        lines = ["LINEAGE HIERARCHY", ""]

        subject = lineage.get("subject", {})
        if subject:
            lines.append(f"└─ {self._format_animal_info(subject)}")

            sire = lineage.get("sire", {})
            dam = lineage.get("dam", {})
            grandparents = lineage.get("grandparents", {})

            if sire:
                lines.append(f"   ├─ SIRE: {self._format_animal_info(sire)}")
                if grandparents.get("sire_sire"):
                    lines.append(f"   │  ├─ {self._format_animal_info(grandparents['sire_sire'])}")
                if grandparents.get("sire_dam"):
                    lines.append(f"   │  └─ {self._format_animal_info(grandparents['sire_dam'])}")

            if dam:
                lines.append(f"   └─ DAM:  {self._format_animal_info(dam)}")
                if grandparents.get("dam_sire"):
                    lines.append(f"      ├─ {self._format_animal_info(grandparents['dam_sire'])}")
                if grandparents.get("dam_dam"):
                    lines.append(f"      └─ {self._format_animal_info(grandparents['dam_dam'])}")

        return "\n".join(lines)

    def visualize_and_save(self, result: dict) -> Optional[str]:
        """Generate and save pedigree visualization."""
        lineage_data = self._extract_lineage_data(result)
        if not lineage_data:
            return None

        try:
            ascii_tree = self._generate_ascii_tree(lineage_data)
            hierarchy = self._generate_hierarchy(lineage_data)
            output = f"{ascii_tree}\n\n{hierarchy}\n\nGenerated: {datetime.utcnow().isoformat()}Z\n"

            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filepath = config.EXPORT_DIR / f"pedigree_{timestamp}.txt"

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(output)

            return str(filepath)

        except OSError as e:
            raise ExportError(f"Failed to save pedigree: {e}")


def main():
    """Process PostToolUse hook for pedigree visualization."""
    try:
        hook_data: PostToolUseInput = json.loads(sys.stdin.read())

        tool_name = hook_data.get("tool", {}).get("name", "")
        tool_result = hook_data.get("result", {})

        if "get_lineage" not in tool_name.lower():
            output: HookOutput = {
                "continue": True,
                "metadata": {"pedigree_generated": False, "reason": "Not a lineage query"}
            }
            print(json.dumps(output))
            sys.exit(0)

        if tool_result.get("isError", False):
            output: HookOutput = {
                "continue": True,
                "metadata": {"pedigree_generated": False, "reason": "Tool returned error"}
            }
            print(json.dumps(output))
            sys.exit(0)

        visualizer = PedigreeVisualizer()
        filepath = visualizer.visualize_and_save(tool_result)

        if filepath:
            output: HookOutput = {
                "continue": True,
                "metadata": {"pedigree_generated": True, "export_path": filepath}
            }
        else:
            output: HookOutput = {
                "continue": True,
                "metadata": {"pedigree_generated": False, "reason": "Failed to generate"}
            }

        print(json.dumps(output))

    except json.JSONDecodeError as e:
        output: HookOutput = {
            "continue": True,
            "metadata": {"pedigree_generated": False, "error": f"Invalid JSON: {e}"}
        }
        print(json.dumps(output))

    except ExportError as e:
        output: HookOutput = {
            "continue": True,
            "metadata": {"pedigree_generated": False, "error": str(e)}
        }
        print(json.dumps(output))

    sys.exit(0)


if __name__ == "__main__":
    main()
