#!/usr/bin/env python3
"""
API Health Check Hook (SessionStart)
Verifies NSIP API connectivity and availability at session start.
"""

import json
import sys
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path
from typing import Tuple, Optional, Dict

# Add script directory to path for sibling module imports
sys.path.insert(0, str(Path(__file__).parent))

from _config import config
from nsip_types import HookOutput
from _exceptions import APIHealthError


NSIP_API_BASE = "http://nsipsearch.nsip.org/api"
HEALTH_CHECK_ENDPOINT = f"{NSIP_API_BASE}/GetLastUpdate"


def check_api_health() -> Tuple[bool, Optional[Dict], Optional[str]]:
    """
    Check NSIP API health by calling GetLastUpdate endpoint.

    Returns:
        Tuple of (is_healthy, response_data, error_message)
    """
    try:
        req = urllib.request.Request(
            HEALTH_CHECK_ENDPOINT,
            headers={'User-Agent': 'Claude-Code-NSIP-Plugin/1.0'}
        )

        with urllib.request.urlopen(req, timeout=config.API_TIMEOUT_SECONDS) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                return True, data, None
            return False, None, f"HTTP {response.status}"

    except urllib.error.HTTPError as e:
        return False, None, f"HTTP Error {e.code}: {e.reason}"

    except urllib.error.URLError as e:
        return False, None, f"Connection Error: {e.reason}"

    except TimeoutError:
        return False, None, f"Timeout after {config.API_TIMEOUT_SECONDS}s"

    except json.JSONDecodeError as e:
        return False, None, f"Invalid JSON response: {e}"


def format_health_report(is_healthy: bool, data: Optional[Dict], error: Optional[str]) -> Dict:
    """Format health check report."""
    report = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "api_healthy": is_healthy,
        "api_endpoint": HEALTH_CHECK_ENDPOINT
    }

    if is_healthy and data:
        report["last_update"] = data.get("LastUpdate", "Unknown")
        report["status"] = "API is operational"
    else:
        report["status"] = "API is not accessible"
        report["error"] = error

    return report


def main():
    """Process SessionStart hook for API health check."""
    try:
        is_healthy, data, error = check_api_health()
        health_report = format_health_report(is_healthy, data, error)

        if is_healthy:
            output: HookOutput = {
                "continue": True,
                "metadata": {"health_check": "passed", **health_report}
            }
        else:
            output: HookOutput = {
                "continue": True,
                "warning": f"NSIP API health check failed: {error}",
                "metadata": {"health_check": "failed", **health_report}
            }

        print(json.dumps(output))

    except APIHealthError as e:
        output: HookOutput = {
            "continue": True,
            "metadata": {
                "health_check": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        }
        print(json.dumps(output))


if __name__ == "__main__":
    main()
