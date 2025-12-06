#!/usr/bin/env python3
"""
Error Notifier Hook (PostToolUse)
Detect repeated failures and create alert files.
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

# Add script directory to path for sibling module imports
sys.path.insert(0, str(Path(__file__).parent))

from _config import config
from nsip_types import PostToolUseInput, HookOutput
from _exceptions import NSIPHookError


class ErrorNotifier:
    """Track and notify about repeated API failures."""

    def __init__(self):
        """Initialize error notifier."""
        config.LOG_DIR.mkdir(parents=True, exist_ok=True)
        self.tracker_file = config.LOG_DIR / "error_tracker.json"
        self.time_window = timedelta(minutes=config.ERROR_TIME_WINDOW_MINUTES)

    def _load_tracker(self) -> Dict:
        """Load error tracker state."""
        try:
            if self.tracker_file.exists():
                with open(self.tracker_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except (OSError, json.JSONDecodeError):
            pass
        return {"failures": [], "last_alert": None}

    def _save_tracker(self, tracker: Dict) -> None:
        """Save error tracker state."""
        try:
            with open(self.tracker_file, "w", encoding="utf-8") as f:
                json.dump(tracker, f, indent=2)
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

    def _clean_old_failures(self, failures: List[Dict]) -> List[Dict]:
        """Remove failures outside the time window."""
        cutoff = datetime.utcnow() - self.time_window
        recent = []

        for failure in failures:
            try:
                ts = datetime.fromisoformat(failure["timestamp"].rstrip("Z"))
                if ts > cutoff:
                    recent.append(failure)
            except (KeyError, ValueError):
                continue

        return recent

    def _create_alert(self, failures: List[Dict]) -> str:
        """Create alert file for repeated failures."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        alert_file = config.LOG_DIR / f"ALERT_{timestamp}.txt"

        tool_failures = {}
        for f in failures:
            tool = f.get("tool", "unknown")
            tool_failures.setdefault(tool, []).append(f)

        lines = [
            "=" * 80, "NSIP API FAILURE ALERT", "=" * 80, "",
            f"Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC",
            f"Failures: {len(failures)} in last {config.ERROR_TIME_WINDOW_MINUTES} minutes", "",
            "AFFECTED TOOLS:", "-" * 80
        ]

        for tool, fl in sorted(tool_failures.items()):
            lines.append(f"  {tool}: {len(fl)} failure(s)")

        lines.extend(["", "TROUBLESHOOTING:", "-" * 80,
            "1. Check internet connection",
            "2. Verify API: http://nsipsearch.nsip.org",
            "3. Try again in a few minutes",
            "4. Check Claude Code logs",
            "", "=" * 80
        ])

        try:
            with open(alert_file, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            return str(alert_file)
        except OSError:
            return ""

    def track_and_notify(self, tool_name: str, result: dict) -> Dict:
        """Track failures and create alerts if threshold exceeded."""
        if not self._is_failure(result):
            return {"error_tracked": False, "reason": "No failure detected"}

        tracker = self._load_tracker()

        tracker["failures"].append({
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "tool": tool_name,
            "error_reason": result.get("error", "Unknown error")
        })

        tracker["failures"] = self._clean_old_failures(tracker["failures"])
        failure_count = len(tracker["failures"])
        should_alert = failure_count >= config.ERROR_THRESHOLD

        # Check alert cooldown (10 minutes)
        if should_alert and tracker.get("last_alert"):
            try:
                last = datetime.fromisoformat(tracker["last_alert"].rstrip("Z"))
                if datetime.utcnow() - last < timedelta(minutes=10):
                    should_alert = False
            except ValueError:
                pass

        alert_path = None
        if should_alert:
            alert_path = self._create_alert(tracker["failures"])
            tracker["last_alert"] = datetime.utcnow().isoformat() + "Z"

        self._save_tracker(tracker)

        return {
            "error_tracked": True,
            "recent_failure_count": failure_count,
            "alert_created": bool(alert_path),
            "alert_path": alert_path,
            "threshold": config.ERROR_THRESHOLD
        }


def main():
    """Process PostToolUse hook for error notification."""
    try:
        hook_data: PostToolUseInput = json.loads(sys.stdin.read())

        tool_name = hook_data.get("tool", {}).get("name", "")
        tool_result = hook_data.get("result", {})

        if not tool_name.startswith("mcp__nsip__"):
            output: HookOutput = {
                "continue": True,
                "metadata": {"error_tracked": False, "reason": "Not an NSIP tool"}
            }
            print(json.dumps(output))
            sys.exit(0)

        notifier = ErrorNotifier()
        result = notifier.track_and_notify(tool_name, tool_result)

        output: HookOutput = {"continue": True, "metadata": result}

        if result.get("alert_created"):
            output["context"] = (
                f"ALERT: {result['recent_failure_count']} API failures. "
                f"Alert: {result['alert_path']}"
            )

        print(json.dumps(output))

    except json.JSONDecodeError as e:
        output: HookOutput = {
            "continue": True,
            "metadata": {"error_tracked": False, "error": f"Invalid JSON: {e}"}
        }
        print(json.dumps(output))

    sys.exit(0)


if __name__ == "__main__":
    main()
