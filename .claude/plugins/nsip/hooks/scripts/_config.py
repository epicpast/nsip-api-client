"""
Centralized configuration for NSIP hooks.

All hardcoded values consolidated here for easy tuning and consistency.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple


@dataclass(frozen=True)
class NSIPConfig:
    """Immutable configuration for NSIP hooks."""

    # Directory paths
    LOG_DIR: Path = Path.home() / ".claude-code" / "nsip-logs"
    CACHE_DIR: Path = Path.home() / ".claude-code" / "nsip-cache"
    EXPORT_DIR: Path = Path.home() / ".claude-code" / "nsip-exports"

    # Retry configuration
    RETRY_MAX_ATTEMPTS: int = 3
    RETRY_BACKOFF_SECONDS: Tuple[int, ...] = (1, 2, 4)

    # Error notification thresholds
    ERROR_THRESHOLD: int = 3
    ERROR_TIME_WINDOW_MINUTES: int = 5

    # Cache configuration
    CACHE_TTL_MINUTES: int = 60
    CACHE_MAX_ENTRIES: int = 1000

    # API configuration
    API_TIMEOUT_SECONDS: int = 5
    API_BASE_URL: str = "http://nsipsearch.nsip.org/api"

    # LPN validation
    LPN_MIN_LENGTH: int = 5
    LPN_MAX_LENGTH: int = 50
    LPN_VALID_CHARS_PATTERN: str = r"^[A-Za-z0-9#\-_]+$"

    def ensure_directories(self) -> None:
        """Create all configured directories if they don't exist."""
        self.LOG_DIR.mkdir(parents=True, exist_ok=True)
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self.EXPORT_DIR.mkdir(parents=True, exist_ok=True)


# Singleton instance for import
config = NSIPConfig()
