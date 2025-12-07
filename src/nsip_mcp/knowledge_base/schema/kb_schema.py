"""Pydantic models for knowledge base data validation.

These models define the expected structure of knowledge base YAML files
and can be used for runtime validation if needed.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TraitCategory(str, Enum):
    """Categories for EBV traits."""

    GROWTH = "growth"
    MATERNAL = "maternal"
    CARCASS = "carcass"
    HEALTH = "health"
    WOOL = "wool"


class TraitInterpretation(str, Enum):
    """How to interpret trait values."""

    HIGHER_BETTER = "higher_better"
    LOWER_BETTER = "lower_better"


class RiskLevel(str, Enum):
    """Disease risk levels by region."""

    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"
    UNKNOWN = "unknown"


class Climate(str, Enum):
    """Climate types for regions."""

    HUMID_CONTINENTAL = "humid_continental"
    HUMID_SUBTROPICAL = "humid_subtropical"
    CONTINENTAL = "continental"
    SEMI_ARID = "semi_arid"
    ALPINE_SEMI_ARID = "alpine_semi_arid"
    VARIED = "varied"


@dataclass
class TraitInfo:
    """Information about a genetic trait."""

    code: str
    name: str
    description: str
    unit: str
    interpretation: TraitInterpretation
    category: TraitCategory
    heritability_range: tuple[float, float] = (0.0, 1.0)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "unit": self.unit,
            "interpretation": self.interpretation.value,
            "category": self.category.value,
            "heritability_range": list(self.heritability_range),
        }


@dataclass
class SelectionIndex:
    """Definition of a selection index."""

    name: str
    description: str
    weights: dict[str, float]
    use_case: str
    breed_focus: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "weights": self.weights,
            "use_case": self.use_case,
            "breed_focus": self.breed_focus,
        }


@dataclass
class RegionInfo:
    """Information about an NSIP member region."""

    name: str
    states: list[str]
    climate: Climate
    primary_breeds: list[str]
    lambing_season: str
    challenges: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "states": self.states,
            "climate": self.climate.value,
            "primary_breeds": self.primary_breeds,
            "lambing_season": self.lambing_season,
            "challenges": self.challenges,
        }


@dataclass
class DiseaseInfo:
    """Information about a sheep disease."""

    name: str
    description: str
    prevention: list[str]
    treatment: str
    regional_risk: dict[str, RiskLevel]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "prevention": self.prevention,
            "treatment": self.treatment,
            "regional_risk": {k: v.value for k, v in self.regional_risk.items()},
        }


@dataclass
class LifeStageNutrition:
    """Nutrition guidelines for a life stage."""

    name: str
    description: str
    timing: str
    protein_percent: str
    energy_adjustment: str
    critical_nutrients: list[str] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "timing": self.timing,
            "protein_percent": self.protein_percent,
            "energy_adjustment": self.energy_adjustment,
            "critical_nutrients": self.critical_nutrients,
            "notes": self.notes,
        }


@dataclass
class CalendarTask:
    """A task in the seasonal calendar."""

    name: str
    description: str
    timing: str
    category: str
    priority: str = "normal"  # "high", "normal", "low"
    region_specific: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "timing": self.timing,
            "category": self.category,
            "priority": self.priority,
            "region_specific": self.region_specific,
        }


@dataclass
class EconomicsCategory:
    """An economics calculation category."""

    name: str
    description: str
    variables: list[str]
    formula: str
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "variables": self.variables,
            "formula": self.formula,
            "notes": self.notes,
        }
