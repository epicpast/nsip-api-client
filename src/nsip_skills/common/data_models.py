"""
Data models for NSIP skills analysis.

These dataclasses represent the outputs of various analysis operations,
designed to be easily serializable and displayable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RiskLevel(Enum):
    """Inbreeding risk classification."""

    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"

    @classmethod
    def from_coefficient(cls, coi: float) -> "RiskLevel":
        """Classify risk from inbreeding coefficient (0-1 scale)."""
        if coi < 0.0625:  # <6.25%
            return cls.LOW
        elif coi < 0.125:  # 6.25% - 12.5%
            return cls.MODERATE
        else:  # >12.5%
            return cls.HIGH


class BreedingGoal(Enum):
    """Breeding strategy goals."""

    TERMINAL = "terminal"  # Meat production focus
    MATERNAL = "maternal"  # Reproduction/nursing focus
    BALANCED = "balanced"  # Equal weight to both
    CUSTOM = "custom"  # User-defined weights


@dataclass
class TraitValue:
    """A single trait measurement with context."""

    name: str
    value: float
    accuracy: float | None = None  # 0-100 percentage
    percentile: float | None = None  # 0-100 percentile within breed
    breed_min: float | None = None
    breed_max: float | None = None
    breed_mean: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "accuracy": self.accuracy,
            "percentile": self.percentile,
            "breed_min": self.breed_min,
            "breed_max": self.breed_max,
            "breed_mean": self.breed_mean,
        }


@dataclass
class TraitProfile:
    """Collection of traits for an animal with analysis metadata."""

    lpn_id: str
    breed: str | None = None
    breed_id: int | None = None
    traits: dict[str, TraitValue] = field(default_factory=dict)
    strengths: list[str] = field(default_factory=list)  # Top 25% traits
    weaknesses: list[str] = field(default_factory=list)  # Bottom 25% traits

    def get_trait(self, name: str) -> TraitValue | None:
        """Get a specific trait by name."""
        return self.traits.get(name)

    def to_dict(self) -> dict[str, Any]:
        return {
            "lpn_id": self.lpn_id,
            "breed": self.breed,
            "breed_id": self.breed_id,
            "traits": {k: v.to_dict() for k, v in self.traits.items()},
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
        }


@dataclass
class AnimalAnalysis:
    """Comprehensive analysis of a single animal."""

    lpn_id: str
    name: str | None = None
    breed: str | None = None
    breed_id: int | None = None
    gender: str | None = None
    date_of_birth: str | None = None
    status: str | None = None
    sire_lpn: str | None = None
    dam_lpn: str | None = None
    trait_profile: TraitProfile | None = None
    inbreeding_coefficient: float | None = None
    inbreeding_risk: RiskLevel | None = None
    progeny_count: int | None = None
    index_scores: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "lpn_id": self.lpn_id,
            "name": self.name,
            "breed": self.breed,
            "breed_id": self.breed_id,
            "gender": self.gender,
            "date_of_birth": self.date_of_birth,
            "status": self.status,
            "sire_lpn": self.sire_lpn,
            "dam_lpn": self.dam_lpn,
            "trait_profile": self.trait_profile.to_dict() if self.trait_profile else None,
            "inbreeding_coefficient": self.inbreeding_coefficient,
            "inbreeding_risk": self.inbreeding_risk.value if self.inbreeding_risk else None,
            "progeny_count": self.progeny_count,
            "index_scores": self.index_scores,
        }


@dataclass
class PedigreeNode:
    """A node in a pedigree tree."""

    lpn_id: str
    name: str | None = None
    breed: str | None = None
    gender: str | None = None
    date_of_birth: str | None = None
    status: str | None = None
    farm_name: str | None = None
    us_index: float | None = None
    generation: int = 0  # 0 = subject, 1 = parents, 2 = grandparents, etc.

    def to_dict(self) -> dict[str, Any]:
        return {
            "lpn_id": self.lpn_id,
            "name": self.name,
            "breed": self.breed,
            "gender": self.gender,
            "date_of_birth": self.date_of_birth,
            "status": self.status,
            "farm_name": self.farm_name,
            "us_index": self.us_index,
            "generation": self.generation,
        }


@dataclass
class PedigreeTree:
    """Complete pedigree tree for an animal."""

    subject: PedigreeNode
    sire: PedigreeNode | None = None
    dam: PedigreeNode | None = None
    sire_sire: PedigreeNode | None = None
    sire_dam: PedigreeNode | None = None
    dam_sire: PedigreeNode | None = None
    dam_dam: PedigreeNode | None = None
    # Extended generations stored by path (e.g., "sss" = sire's sire's sire)
    extended: dict[str, PedigreeNode] = field(default_factory=dict)
    common_ancestors: list[str] = field(default_factory=list)  # LPN IDs appearing multiple times
    max_generations: int = 4

    def get_ancestor(self, path: str) -> PedigreeNode | None:
        """
        Get ancestor by path string.

        Path uses 's' for sire and 'd' for dam.
        Examples: 's' = sire, 'ds' = dam's sire, 'ssd' = sire's sire's dam
        """
        if not path:
            return self.subject
        if path == "s":
            return self.sire
        if path == "d":
            return self.dam
        if path == "ss":
            return self.sire_sire
        if path == "sd":
            return self.sire_dam
        if path == "ds":
            return self.dam_sire
        if path == "dd":
            return self.dam_dam
        return self.extended.get(path)

    def all_ancestors(self) -> list[PedigreeNode]:
        """Get all ancestors as a flat list."""
        ancestors = []
        if self.sire:
            ancestors.append(self.sire)
        if self.dam:
            ancestors.append(self.dam)
        if self.sire_sire:
            ancestors.append(self.sire_sire)
        if self.sire_dam:
            ancestors.append(self.sire_dam)
        if self.dam_sire:
            ancestors.append(self.dam_sire)
        if self.dam_dam:
            ancestors.append(self.dam_dam)
        ancestors.extend(self.extended.values())
        return ancestors

    def to_dict(self) -> dict[str, Any]:
        return {
            "subject": self.subject.to_dict(),
            "sire": self.sire.to_dict() if self.sire else None,
            "dam": self.dam.to_dict() if self.dam else None,
            "sire_sire": self.sire_sire.to_dict() if self.sire_sire else None,
            "sire_dam": self.sire_dam.to_dict() if self.sire_dam else None,
            "dam_sire": self.dam_sire.to_dict() if self.dam_sire else None,
            "dam_dam": self.dam_dam.to_dict() if self.dam_dam else None,
            "extended": {k: v.to_dict() for k, v in self.extended.items()},
            "common_ancestors": self.common_ancestors,
            "max_generations": self.max_generations,
        }


@dataclass
class InbreedingResult:
    """Result of inbreeding coefficient calculation."""

    lpn_id: str
    coefficient: float  # 0-1 scale (multiply by 100 for percentage)
    risk_level: RiskLevel | None = None  # Auto-computed from coefficient if None
    common_ancestors: list[str] = field(default_factory=list)  # LPN IDs of common ancestors
    paths: list[dict[str, Any]] = field(default_factory=list)  # Paths through pedigree
    generations_analyzed: int = 4
    pedigree: "PedigreeTree | None" = None  # Optional pedigree tree

    def __post_init__(self):
        """Auto-compute risk_level from coefficient if not provided."""
        if self.risk_level is None:
            self.risk_level = RiskLevel.from_coefficient(self.coefficient)

    @property
    def percentage(self) -> float:
        """Coefficient as percentage (0-100)."""
        return self.coefficient * 100

    def to_dict(self) -> dict[str, Any]:
        return {
            "lpn_id": self.lpn_id,
            "coefficient": self.coefficient,
            "percentage": self.percentage,
            "risk_level": self.risk_level.value if self.risk_level else None,
            "common_ancestors": self.common_ancestors,
            "paths": self.paths,
            "generations_analyzed": self.generations_analyzed,
        }


@dataclass
class MatingPair:
    """A proposed ram-ewe mating with projections."""

    ram_lpn: str
    ewe_lpn: str
    projected_offspring_ebvs: dict[str, float] = field(default_factory=dict)
    projected_inbreeding: float = 0.0
    inbreeding_risk: RiskLevel = RiskLevel.LOW
    composite_score: float = 0.0  # Overall breeding value score
    rank: int = 0
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ram_lpn": self.ram_lpn,
            "ewe_lpn": self.ewe_lpn,
            "projected_offspring_ebvs": self.projected_offspring_ebvs,
            "projected_inbreeding": self.projected_inbreeding,
            "inbreeding_risk": self.inbreeding_risk.value,
            "composite_score": self.composite_score,
            "rank": self.rank,
            "notes": self.notes,
        }


@dataclass
class ProgenyStats:
    """Statistics about a sire/dam's progeny."""

    parent_lpn: str
    parent_gender: str
    total_progeny: int = 0
    male_count: int = 0
    female_count: int = 0
    trait_means: dict[str, float] = field(default_factory=dict)
    trait_std_devs: dict[str, float] = field(default_factory=dict)
    top_performers: list[str] = field(default_factory=list)  # Top 10% by index
    bottom_performers: list[str] = field(default_factory=list)  # Bottom 10% by index

    def to_dict(self) -> dict[str, Any]:
        return {
            "parent_lpn": self.parent_lpn,
            "parent_gender": self.parent_gender,
            "total_progeny": self.total_progeny,
            "male_count": self.male_count,
            "female_count": self.female_count,
            "trait_means": self.trait_means,
            "trait_std_devs": self.trait_std_devs,
            "top_performers": self.top_performers,
            "bottom_performers": self.bottom_performers,
        }


@dataclass
class FlockSummary:
    """Aggregate statistics for a flock."""

    flock_id: str | None = None
    flock_name: str | None = None
    total_animals: int = 0
    male_count: int = 0
    female_count: int = 0
    status_breakdown: dict[str, int] = field(default_factory=dict)
    breed_breakdown: dict[str, int] = field(default_factory=dict)
    age_distribution: dict[str, int] = field(default_factory=dict)  # Year -> count
    trait_summary: dict[str, dict[str, float]] = field(
        default_factory=dict
    )  # Trait -> {mean, median, std, min, max}
    top_performers: list[AnimalAnalysis] = field(default_factory=list)
    needs_improvement: list[str] = field(default_factory=list)  # Trait names
    recommendations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "flock_id": self.flock_id,
            "flock_name": self.flock_name,
            "total_animals": self.total_animals,
            "male_count": self.male_count,
            "female_count": self.female_count,
            "status_breakdown": self.status_breakdown,
            "breed_breakdown": self.breed_breakdown,
            "age_distribution": self.age_distribution,
            "trait_summary": self.trait_summary,
            "top_performers": [a.to_dict() for a in self.top_performers],
            "needs_improvement": self.needs_improvement,
            "recommendations": self.recommendations,
        }


@dataclass
class SelectionIndex:
    """A breeding selection index definition."""

    name: str
    description: str | None = None
    trait_weights: dict[str, float] = field(default_factory=dict)
    is_preset: bool = False  # True for built-in indexes

    def calculate_score(self, ebvs: dict[str, float]) -> float:
        """Calculate index score from EBVs."""
        score = 0.0
        for trait, weight in self.trait_weights.items():
            if trait in ebvs:
                score += weight * ebvs[trait]
        return score

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "trait_weights": self.trait_weights,
            "is_preset": self.is_preset,
        }


# Pre-built selection indexes based on NSIP standards
TERMINAL_INDEX = SelectionIndex(
    name="Terminal Index",
    description="Emphasizes growth and carcass traits for meat production",
    trait_weights={
        "BWT": -0.5,  # Lower birth weight preferred (easier lambing)
        "WWT": 1.0,
        "PWWT": 1.5,
        "YWT": 1.0,
        "YEMD": 0.8,  # Eye muscle depth
        "YFAT": -0.3,  # Less fat preferred
    },
    is_preset=True,
)

MATERNAL_INDEX = SelectionIndex(
    name="Maternal Index",
    description="Emphasizes reproduction and mothering ability",
    trait_weights={
        "NLB": 2.0,  # Number lambs born
        "NLW": 2.5,  # Number lambs weaned (survival)
        "MWWT": 1.5,  # Maternal milk effect on weaning weight
        "BWT": -1.0,  # Lower birth weight for easier lambing
        "WWT": 0.5,
    },
    is_preset=True,
)

RANGE_INDEX = SelectionIndex(
    name="Range Index",
    description="Balanced index for range/pastoral operations",
    trait_weights={
        "BWT": -0.5,
        "WWT": 1.0,
        "PWWT": 1.0,
        "NLW": 1.5,
        "MWWT": 1.0,
    },
    is_preset=True,
)

HAIR_INDEX = SelectionIndex(
    name="Hair Sheep Index",
    description="For hair sheep breeds (no wool traits)",
    trait_weights={
        "BWT": -0.5,
        "WWT": 1.2,
        "PWWT": 1.5,
        "NLB": 1.5,
        "NLW": 2.0,
        "DAG": -0.5,  # Dag score (if applicable)
    },
    is_preset=True,
)

PRESET_INDEXES = {
    "terminal": TERMINAL_INDEX,
    "maternal": MATERNAL_INDEX,
    "range": RANGE_INDEX,
    "hair": HAIR_INDEX,
}


@dataclass
class FlockRecord:
    """A record from a flock spreadsheet (user input)."""

    lpn_id: str
    local_id: str | None = None  # User's tag/name
    notes: str | None = None
    group: str | None = None  # User-defined grouping
    row_number: int | None = None  # Original spreadsheet row

    def to_dict(self) -> dict[str, Any]:
        return {
            "lpn_id": self.lpn_id,
            "local_id": self.local_id,
            "notes": self.notes,
            "group": self.group,
            "row_number": self.row_number,
        }


@dataclass
class EnrichedFlockRecord:
    """Flock record enriched with NSIP data."""

    local: FlockRecord
    nsip_details: AnimalAnalysis | None = None
    fetch_error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "local": self.local.to_dict(),
            "nsip_details": self.nsip_details.to_dict() if self.nsip_details else None,
            "fetch_error": self.fetch_error,
        }
