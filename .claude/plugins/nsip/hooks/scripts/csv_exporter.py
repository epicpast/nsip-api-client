#!/usr/bin/env python3
"""
CSV Exporter Hook (PostToolUse)
Exports search results and animal data to CSV files for analysis.
"""

import json
import sys
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add script directory to path for sibling module imports
sys.path.insert(0, str(Path(__file__).parent))

from _config import config
from nsip_types import PostToolUseInput, HookOutput
from _exceptions import ExportError


def flatten_dict(d: dict, parent_key: str = '', sep: str = '_') -> dict:
    """Flatten nested dictionary for CSV export."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k

        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            items.append((new_key, ', '.join(map(str, v)) if v else ''))
        else:
            items.append((new_key, v))

    return dict(items)


def extract_results(result_data: dict) -> List[Dict[str, Any]]:
    """Extract exportable data from tool result."""
    if isinstance(result_data, list):
        return result_data

    for key in ['animals', 'results', 'data', 'items']:
        if key in result_data and isinstance(result_data[key], list):
            return result_data[key]

    if 'lpn_id' in result_data or 'animal_id' in result_data:
        return [result_data]

    if 'content' in result_data:
        content = result_data['content']
        if isinstance(content, list):
            return content
        elif isinstance(content, dict):
            return extract_results(content)

    return []


def export_to_csv(data: List[Dict[str, Any]], filename: str) -> Optional[str]:
    """Export data to CSV file."""
    if not data:
        return None

    config.EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    filepath = config.EXPORT_DIR / filename

    flattened_data = [flatten_dict(item) for item in data]

    all_keys = set()
    for item in flattened_data:
        all_keys.update(item.keys())
    all_keys = sorted(all_keys)

    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=all_keys)
            writer.writeheader()

            for item in flattened_data:
                row = {key: item.get(key, '') for key in all_keys}
                writer.writerow(row)

        return str(filepath)

    except OSError as e:
        raise ExportError(f"Failed to write CSV: {e}")


def generate_filename(tool_name: str) -> str:
    """Generate filename for export."""
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    base_name = tool_name.replace('mcp__nsip__', '').replace('__', '_')
    return f"{base_name}_{timestamp}.csv"


def main():
    """Process PostToolUse hook for CSV export."""
    try:
        hook_data: PostToolUseInput = json.loads(sys.stdin.read())

        tool_name = hook_data.get("tool", {}).get("name", "")
        tool_result = hook_data.get("result", {})

        if tool_result.get("isError", False):
            output: HookOutput = {
                "continue": True,
                "metadata": {"exported": False, "reason": "Error result not exported"}
            }
            print(json.dumps(output))
            return

        data_to_export = extract_results(tool_result)

        if not data_to_export:
            output: HookOutput = {
                "continue": True,
                "metadata": {"exported": False, "reason": "No exportable data found"}
            }
            print(json.dumps(output))
            return

        filename = generate_filename(tool_name)
        filepath = export_to_csv(data_to_export, filename)

        output: HookOutput = {
            "continue": True,
            "metadata": {
                "exported": True,
                "filepath": filepath,
                "record_count": len(data_to_export),
                "export_dir": str(config.EXPORT_DIR)
            }
        }

        print(json.dumps(output))

    except json.JSONDecodeError as e:
        output: HookOutput = {
            "continue": True,
            "metadata": {"exported": False, "error": f"Invalid JSON: {e}"}
        }
        print(json.dumps(output))

    except ExportError as e:
        output: HookOutput = {
            "continue": True,
            "metadata": {"exported": False, "error": str(e)}
        }
        print(json.dumps(output))


if __name__ == "__main__":
    main()
