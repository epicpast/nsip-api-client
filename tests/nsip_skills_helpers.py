"""
Shared test helpers for nsip_skills tests.

This module contains mock classes and constants used across nsip_skills tests.
Import from here instead of using relative imports from conftest.py.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# Sample LPN IDs for testing
SAMPLE_LPNS = [
    "6####92020###249",
    "6####92020###250",
    "6####92020###251",
    "6####92021###100",
    "6####92021###101",
]

SAMPLE_SIRE_LPN = "6####92018###001"
SAMPLE_DAM_LPN = "6####92019###002"


@dataclass
class MockTrait:
    """Mock trait object matching nsip_client AnimalDetails.traits structure."""

    name: str
    value: float
    accuracy: float = 0.5


@dataclass
class MockAnimalDetails:
    """Mock animal details matching nsip_client AnimalDetails structure."""

    lpn_id: str
    breed: str = "Suffolk"
    gender: str = "Male"
    date_of_birth: str = "2020-03-15"
    status: str = "Active"
    sire: str | None = None
    dam: str | None = None
    total_progeny: int = 0
    traits: dict[str, MockTrait] = field(default_factory=dict)

    @classmethod
    def create_sample(
        cls,
        lpn_id: str,
        sire: str | None = None,
        dam: str | None = None,
        trait_values: dict[str, float] | None = None,
    ) -> MockAnimalDetails:
        """Create a sample mock animal with realistic EBVs."""
        default_traits = {
            "BWT": 0.5,
            "WWT": 2.1,
            "PWWT": 3.5,
            "YFAT": -0.2,
            "YEMD": 0.8,
            "NLW": 0.12,
        }
        if trait_values:
            default_traits.update(trait_values)

        traits = {name: MockTrait(name=name, value=value) for name, value in default_traits.items()}

        return cls(
            lpn_id=lpn_id,
            sire=sire,
            dam=dam,
            traits=traits,
        )


@dataclass
class MockLineageAnimal:
    """Mock LineageAnimal matching nsip_client structure."""

    lpn_id: str
    farm_name: str | None = None
    us_index: float | None = None
    src_index: float | None = None
    date_of_birth: str | None = None
    sex: str | None = None
    status: str | None = None


class MockLineage:
    """Mock lineage object matching nsip_client Lineage structure.

    Tests pass string LPN IDs (sire="SIRE") but the real Lineage model
    has sire/dam as LineageAnimal objects. This class accepts both.
    """

    def __init__(
        self,
        lpn_id: str,
        sire: str | MockLineageAnimal | None = None,
        dam: str | MockLineageAnimal | None = None,
        sire_sire: str | None = None,
        sire_dam: str | None = None,
        dam_sire: str | None = None,
        dam_dam: str | None = None,
    ):
        self.lpn_id = lpn_id
        self.sire_sire = sire_sire
        self.sire_dam = sire_dam
        self.dam_sire = dam_sire
        self.dam_dam = dam_dam

        # Create subject as LineageAnimal
        self.subject = MockLineageAnimal(lpn_id=lpn_id)

        # Convert sire/dam to LineageAnimal objects
        if sire is None:
            self.sire = None
        elif isinstance(sire, str):
            self.sire = MockLineageAnimal(lpn_id=sire)
        else:
            self.sire = sire

        if dam is None:
            self.dam = None
        elif isinstance(dam, str):
            self.dam = MockLineageAnimal(lpn_id=dam)
        else:
            self.dam = dam


@dataclass
class MockProgeny:
    """Mock progeny object matching nsip_client structure."""

    lpn_id: str
    gender: str = "Male"
    date_of_birth: str = "2022-01-15"
    status: str = "Active"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict for API-like usage."""
        return {
            "lpn_id": self.lpn_id,
            "sex": self.gender,
            "date_of_birth": self.date_of_birth,
            "status": self.status,
        }


class MockNSIPClient:
    """Mock NSIP client for testing without API calls."""

    def __init__(
        self,
        animals: dict[str, MockAnimalDetails] | None = None,
        lineages: dict[str, MockLineage] | None = None,
        progeny: dict[str, list[MockProgeny]] | None = None,
    ):
        self.animals = animals or {}
        self.lineages = lineages or {}
        self.progeny = progeny or {}
        self._closed = False

    def get_animal_details(self, lpn_id: str) -> MockAnimalDetails:
        if lpn_id in self.animals:
            return self.animals[lpn_id]
        raise ValueError(f"Animal not found: {lpn_id}")

    def get_lineage(self, lpn_id: str) -> MockLineage:
        if lpn_id in self.lineages:
            return self.lineages[lpn_id]
        # Return empty lineage if not found
        return MockLineage(lpn_id=lpn_id)

    def get_progeny(self, lpn_id: str, page: int = 1) -> list[MockProgeny]:
        if lpn_id in self.progeny:
            return self.progeny[lpn_id]
        return []

    def get_all_progeny(self, lpn_id: str, force_refresh: bool = False) -> list[dict[str, Any]]:
        """Return progeny as list of dicts (matching CachedNSIPClient)."""
        progeny_list = self.get_progeny(lpn_id)
        return [p.to_dict() for p in progeny_list]

    def batch_get_animals(
        self,
        lpn_ids: list[str],
        include_lineage: bool = False,
        include_progeny: bool = False,
        on_error: str = "skip",
        force_refresh: bool = False,
    ) -> dict[str, dict[str, Any]]:
        """Batch fetch animals with optional lineage/progeny (matching CachedNSIPClient)."""
        result = {}
        for lpn_id in lpn_ids:
            if lpn_id in self.animals:
                entry: dict[str, Any] = {"details": self.animals[lpn_id]}
                if include_lineage:
                    entry["lineage"] = self.get_lineage(lpn_id)
                if include_progeny:
                    entry["progeny"] = self.get_progeny(lpn_id)
                result[lpn_id] = entry
            elif on_error == "skip":
                result[lpn_id] = {"error": "not found"}
            else:
                raise ValueError(f"Animal not found: {lpn_id}")
        return result

    def get_trait_ranges_by_breed(self, breed_id: int) -> dict[str, dict[str, float]]:
        return {
            "BWT": {"min": -2.0, "max": 3.0},
            "WWT": {"min": -5.0, "max": 10.0},
            "PWWT": {"min": -8.0, "max": 15.0},
            "YFAT": {"min": -1.5, "max": 1.5},
            "YEMD": {"min": -2.0, "max": 3.0},
            "NLW": {"min": -0.3, "max": 0.5},
        }

    def close(self):
        self._closed = True
