"""
Pytest fixtures for nsip_skills unit tests.

Provides mock NSIP API responses and common test data.
"""

from __future__ import annotations

from typing import Any

import pytest

# Import all mock classes from the shared helpers module
from nsip_skills_helpers import (
    SAMPLE_DAM_LPN,
    SAMPLE_LPNS,
    SAMPLE_SIRE_LPN,
    MockAnimalDetails,
    MockLineage,
    MockNSIPClient,
    MockProgeny,
)


@pytest.fixture
def sample_lpn_ids() -> list[str]:
    """Sample LPN IDs for testing."""
    return SAMPLE_LPNS.copy()


@pytest.fixture
def sample_sire_lpn() -> str:
    """Sample sire LPN ID."""
    return SAMPLE_SIRE_LPN


@pytest.fixture
def sample_dam_lpn() -> str:
    """Sample dam LPN ID."""
    return SAMPLE_DAM_LPN


@pytest.fixture
def mock_animals() -> dict[str, MockAnimalDetails]:
    """Create mock animals with realistic data."""
    animals = {}

    # Create main test animals
    for i, lpn in enumerate(SAMPLE_LPNS):
        trait_variations = {
            "BWT": 0.3 + (i * 0.2),
            "WWT": 1.5 + (i * 0.5),
            "PWWT": 2.0 + (i * 0.7),
            "YFAT": -0.3 + (i * 0.1),
            "YEMD": 0.5 + (i * 0.2),
            "NLW": 0.08 + (i * 0.02),
        }
        animals[lpn] = MockAnimalDetails.create_sample(
            lpn_id=lpn,
            sire=SAMPLE_SIRE_LPN if i < 3 else None,
            dam=SAMPLE_DAM_LPN if i < 2 else None,
            trait_values=trait_variations,
        )

    # Create sire and dam
    animals[SAMPLE_SIRE_LPN] = MockAnimalDetails.create_sample(
        lpn_id=SAMPLE_SIRE_LPN,
        trait_values={"BWT": 0.8, "WWT": 4.0, "PWWT": 6.5, "NLW": 0.15},
    )
    animals[SAMPLE_SIRE_LPN].gender = "Male"
    animals[SAMPLE_SIRE_LPN].total_progeny = 45

    animals[SAMPLE_DAM_LPN] = MockAnimalDetails.create_sample(
        lpn_id=SAMPLE_DAM_LPN,
        trait_values={"BWT": 0.2, "WWT": 2.5, "PWWT": 4.0, "NLW": 0.18},
    )
    animals[SAMPLE_DAM_LPN].gender = "Female"
    animals[SAMPLE_DAM_LPN].total_progeny = 12

    return animals


@pytest.fixture
def mock_lineages() -> dict[str, MockLineage]:
    """Create mock lineage data."""
    return {
        SAMPLE_LPNS[0]: MockLineage(
            lpn_id=SAMPLE_LPNS[0],
            sire=SAMPLE_SIRE_LPN,
            dam=SAMPLE_DAM_LPN,
            sire_sire="6####92015###100",
            sire_dam="6####92016###200",
            dam_sire="6####92015###300",
            dam_dam="6####92016###400",
        ),
        SAMPLE_SIRE_LPN: MockLineage(
            lpn_id=SAMPLE_SIRE_LPN,
            sire="6####92015###100",
            dam="6####92016###200",
        ),
        SAMPLE_DAM_LPN: MockLineage(
            lpn_id=SAMPLE_DAM_LPN,
            sire="6####92015###300",
            dam="6####92016###400",
        ),
    }


@pytest.fixture
def mock_progeny() -> dict[str, list[MockProgeny]]:
    """Create mock progeny data."""
    return {
        SAMPLE_SIRE_LPN: [
            MockProgeny(lpn_id=SAMPLE_LPNS[0], gender="Male"),
            MockProgeny(lpn_id=SAMPLE_LPNS[1], gender="Female"),
            MockProgeny(lpn_id=SAMPLE_LPNS[2], gender="Male"),
        ],
        SAMPLE_DAM_LPN: [
            MockProgeny(lpn_id=SAMPLE_LPNS[0], gender="Male"),
            MockProgeny(lpn_id=SAMPLE_LPNS[1], gender="Female"),
        ],
    }


@pytest.fixture
def mock_client(
    mock_animals: dict[str, MockAnimalDetails],
    mock_lineages: dict[str, MockLineage],
    mock_progeny: dict[str, list[MockProgeny]],
) -> MockNSIPClient:
    """Create a mock NSIP client with all test data."""
    return MockNSIPClient(
        animals=mock_animals,
        lineages=mock_lineages,
        progeny=mock_progeny,
    )


@pytest.fixture
def sample_csv_content() -> str:
    """Sample CSV content for spreadsheet tests."""
    return """LPN_ID,Name,Tag,Notes
6####92020###249,Ram A,001,Top performer
6####92020###250,Ram B,002,Good maternal traits
6####92020###251,Ewe C,003,High NLW
"""


@pytest.fixture
def sample_flock_records() -> list[dict[str, Any]]:
    """Sample flock records for import tests."""
    return [
        {"lpn_id": SAMPLE_LPNS[0], "name": "Ram A", "tag": "001"},
        {"lpn_id": SAMPLE_LPNS[1], "name": "Ram B", "tag": "002"},
        {"lpn_id": SAMPLE_LPNS[2], "name": "Ewe C", "tag": "003"},
    ]
