"""
Shared validation utilities for NSIP hooks.

Consolidates LPN validation patterns from lpn_validator.py and smart_search_detector.py.
"""

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

# Add script directory to path for sibling module imports
sys.path.insert(0, str(Path(__file__).parent))

from _config import config
from _exceptions import LPNValidationError


@dataclass
class LPNValidationResult:
    """Result of LPN validation."""

    is_valid: bool
    lpn_id: str
    error_message: str = ""
    normalized: str = ""


class LPNValidator:
    """
    Unified LPN ID validation and extraction.

    Consolidates patterns from:
    - lpn_validator.py: Format validation (PreToolUse)
    - smart_search_detector.py: Pattern extraction (UserPromptSubmit)
    """

    # Patterns for detecting LPN IDs in text (from smart_search_detector.py)
    DETECTION_PATTERNS: List[re.Pattern] = [
        re.compile(r"\b\d{1,4}#{0,10}\d{4,10}#{0,10}\d{1,4}\b"),  # e.g., 6####92020###249
        re.compile(r"\b[A-Z]{2,4}\d{6,10}\b"),  # e.g., NSWK123456
        re.compile(r"\b\d{10,15}\b"),  # e.g., 621879202000024
        re.compile(r"\bLPN[:\s-]?([A-Z0-9#]+)\b", re.IGNORECASE),  # e.g., LPN:ABC123
    ]

    # Pattern for valid characters (from lpn_validator.py)
    VALID_CHARS_PATTERN = re.compile(config.LPN_VALID_CHARS_PATTERN)

    @classmethod
    def validate(cls, lpn_id: str) -> LPNValidationResult:
        """
        Validate an LPN ID format.

        Args:
            lpn_id: The LPN ID to validate

        Returns:
            LPNValidationResult with validation status and details
        """
        if not lpn_id:
            return LPNValidationResult(
                is_valid=False,
                lpn_id="",
                error_message="LPN ID cannot be empty"
            )

        # Normalize: strip whitespace
        normalized = lpn_id.strip()

        # Check minimum length
        if len(normalized) < config.LPN_MIN_LENGTH:
            return LPNValidationResult(
                is_valid=False,
                lpn_id=lpn_id,
                error_message=f"LPN ID '{lpn_id}' is too short (minimum {config.LPN_MIN_LENGTH} characters)",
                normalized=normalized
            )

        # Check maximum length
        if len(normalized) > config.LPN_MAX_LENGTH:
            return LPNValidationResult(
                is_valid=False,
                lpn_id=lpn_id,
                error_message=f"LPN ID '{lpn_id}' is too long (maximum {config.LPN_MAX_LENGTH} characters)",
                normalized=normalized
            )

        # Check for valid characters
        if not cls.VALID_CHARS_PATTERN.match(normalized):
            return LPNValidationResult(
                is_valid=False,
                lpn_id=lpn_id,
                error_message=f"LPN ID '{lpn_id}' contains invalid characters (only alphanumeric, #, -, _ allowed)",
                normalized=normalized
            )

        return LPNValidationResult(
            is_valid=True,
            lpn_id=lpn_id,
            normalized=normalized
        )

    @classmethod
    def validate_or_raise(cls, lpn_id: str) -> str:
        """
        Validate an LPN ID, raising exception on failure.

        Args:
            lpn_id: The LPN ID to validate

        Returns:
            Normalized LPN ID if valid

        Raises:
            LPNValidationError: If validation fails
        """
        result = cls.validate(lpn_id)
        if not result.is_valid:
            raise LPNValidationError(lpn_id, result.error_message)
        return result.normalized

    @classmethod
    def extract_from_text(cls, text: str) -> List[str]:
        """
        Extract LPN IDs from free-form text.

        Args:
            text: Text that may contain LPN IDs

        Returns:
            List of unique detected LPN IDs (order preserved)
        """
        detected_ids: List[str] = []

        for pattern in cls.DETECTION_PATTERNS:
            matches = pattern.findall(text)
            # Handle patterns with capture groups (like LPN:xxx)
            for match in matches:
                if isinstance(match, tuple):
                    detected_ids.extend(m for m in match if m)
                else:
                    detected_ids.append(match)

        # Remove duplicates while preserving order
        seen = set()
        unique_ids = []
        for lpn_id in detected_ids:
            if lpn_id not in seen:
                seen.add(lpn_id)
                unique_ids.append(lpn_id)

        return unique_ids

    @classmethod
    def extract_and_validate(cls, text: str) -> List[Tuple[str, LPNValidationResult]]:
        """
        Extract LPN IDs from text and validate each one.

        Args:
            text: Text that may contain LPN IDs

        Returns:
            List of (lpn_id, validation_result) tuples
        """
        extracted = cls.extract_from_text(text)
        return [(lpn_id, cls.validate(lpn_id)) for lpn_id in extracted]


def extract_lpn_from_params(params: dict) -> str | None:
    """
    Extract LPN ID from tool parameters.

    Checks common parameter names used across NSIP tools.

    Args:
        params: Tool parameters dictionary

    Returns:
        LPN ID if found, None otherwise
    """
    # Priority order for parameter names
    lpn_param_names = ["lpn_id", "animal_id", "id", "search_string"]

    for name in lpn_param_names:
        if name in params and params[name] is not None:
            return str(params[name])

    return None
