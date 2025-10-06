"""
Pytest configuration and shared fixtures
"""

import pytest


@pytest.fixture
def sample_lpn_id():
    """Sample LPN ID for testing"""
    return "6####92020###249"


@pytest.fixture
def sample_breed_id():
    """Sample breed ID for testing"""
    return 486  # South African Meat Merino
