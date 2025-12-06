"""
Pytest configuration and shared fixtures
"""

import sys
from pathlib import Path

# Add src to Python path for development imports - must be done BEFORE pytest collection
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


def pytest_configure(config):
    """Called after command line options are parsed and all plugins loaded."""
    # Ensure src path is in sys.path
    _src = Path(__file__).parent.parent / "src"
    if str(_src) not in sys.path:
        sys.path.insert(0, str(_src))


import pytest  # noqa: E402


@pytest.fixture
def sample_lpn_id():
    """Sample LPN ID for testing"""
    return "6####92020###249"


@pytest.fixture
def sample_breed_id():
    """Sample breed ID for testing"""
    return 486  # South African Meat Merino
