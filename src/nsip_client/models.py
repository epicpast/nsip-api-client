"""
Data models for NSIP API responses
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
from datetime import datetime


@dataclass
class SearchCriteria:
    """Search criteria for animal search"""

    breed_group_id: Optional[int] = None
    breed_id: Optional[int] = None
    born_after: Optional[str] = None  # Format: YYYY-MM-DD
    born_before: Optional[str] = None  # Format: YYYY-MM-DD
    gender: Optional[str] = None  # "Male", "Female", "Both"
    proven_only: Optional[bool] = None
    status: Optional[str] = None  # "CURRENT", "SOLD", "DEAD", etc.
    flock_id: Optional[str] = None
    trait_ranges: Optional[Dict[str, Dict[str, float]]] = None  # {"BWT": {"min": -1.0, "max": 1.0}}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API request"""
        data = {}
        if self.breed_group_id is not None:
            data["breedGroupId"] = self.breed_group_id
        if self.breed_id is not None:
            data["breedId"] = self.breed_id
        if self.born_after:
            data["bornAfter"] = self.born_after
        if self.born_before:
            data["bornBefore"] = self.born_before
        if self.gender:
            data["gender"] = self.gender
        if self.proven_only is not None:
            data["provenOnly"] = self.proven_only
        if self.status:
            data["status"] = self.status
        if self.flock_id:
            data["flockId"] = self.flock_id
        if self.trait_ranges:
            data["traitRanges"] = self.trait_ranges
        return data


@dataclass
class Trait:
    """Animal trait with value and accuracy"""

    name: str
    value: float
    accuracy: Optional[int] = None
    units: Optional[str] = None


@dataclass
class ContactInfo:
    """Contact information for animal owner"""

    farm_name: Optional[str] = None
    contact_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None


@dataclass
class AnimalDetails:
    """Detailed information about an animal"""

    lpn_id: str
    breed: Optional[str] = None
    breed_group: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    status: Optional[str] = None
    sire: Optional[str] = None
    dam: Optional[str] = None
    registration_number: Optional[str] = None
    total_progeny: Optional[int] = None
    flock_count: Optional[int] = None
    genotyped: Optional[str] = None
    traits: Dict[str, Trait] = field(default_factory=dict)
    contact_info: Optional[ContactInfo] = None
    raw_data: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "AnimalDetails":
        """Create AnimalDetails from API response"""
        traits = {}
        if "Traits" in data:
            for trait_name, trait_data in data["Traits"].items():
                if isinstance(trait_data, dict):
                    traits[trait_name] = Trait(
                        name=trait_name,
                        value=trait_data.get("Value", 0),
                        accuracy=trait_data.get("Accuracy"),
                    )

        contact = None
        if "ContactInfo" in data:
            contact = ContactInfo(
                farm_name=data["ContactInfo"].get("FarmName"),
                contact_name=data["ContactInfo"].get("ContactName"),
                phone=data["ContactInfo"].get("Phone"),
                email=data["ContactInfo"].get("Email"),
                address=data["ContactInfo"].get("Address"),
                city=data["ContactInfo"].get("City"),
                state=data["ContactInfo"].get("State"),
                zip_code=data["ContactInfo"].get("ZipCode"),
            )

        return cls(
            lpn_id=data.get("LpnId", ""),
            breed=data.get("Breed"),
            breed_group=data.get("BreedGroup"),
            date_of_birth=data.get("DateOfBirth"),
            gender=data.get("Gender"),
            status=data.get("Status"),
            sire=data.get("Sire"),
            dam=data.get("Dam"),
            registration_number=data.get("RegistrationNumber"),
            total_progeny=data.get("TotalProgeny"),
            flock_count=data.get("FlockCount"),
            genotyped=data.get("Genotyped"),
            traits=traits,
            contact_info=contact,
            raw_data=data,
        )


@dataclass
class ProgenyAnimal:
    """Individual progeny animal"""

    lpn_id: str
    sex: Optional[str] = None
    date_of_birth: Optional[str] = None
    traits: Dict[str, float] = field(default_factory=dict)


@dataclass
class Progeny:
    """Progeny information for an animal"""

    total_count: int
    animals: List[ProgenyAnimal] = field(default_factory=list)
    page: int = 0
    page_size: int = 10

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "Progeny":
        """Create Progeny from API response"""
        animals = []
        for animal_data in data.get("Results", []):
            progeny_animal = ProgenyAnimal(
                lpn_id=animal_data.get("LpnId", ""),
                sex=animal_data.get("Sex"),
                date_of_birth=animal_data.get("DateOfBirth"),
                traits=animal_data.get("Traits", {}),
            )
            animals.append(progeny_animal)

        return cls(
            total_count=data.get("TotalCount", 0),
            animals=animals,
            page=data.get("Page", 0),
            page_size=data.get("PageSize", 10),
        )


@dataclass
class LineageAnimal:
    """Individual animal in lineage/pedigree"""

    lpn_id: str
    farm_name: Optional[str] = None
    us_index: Optional[float] = None
    src_index: Optional[float] = None
    date_of_birth: Optional[str] = None
    sex: Optional[str] = None
    status: Optional[str] = None


@dataclass
class Lineage:
    """Pedigree/lineage information"""

    subject: Optional[LineageAnimal] = None
    sire: Optional[LineageAnimal] = None
    dam: Optional[LineageAnimal] = None
    generations: List[List[LineageAnimal]] = field(default_factory=list)
    raw_data: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "Lineage":
        """Create Lineage from API response"""
        # This is a simplified implementation
        # The actual lineage structure may be more complex
        return cls(raw_data=data)


@dataclass
class BreedGroup:
    """Breed group information"""

    id: int
    name: str
    breeds: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class SearchResults:
    """Search results container"""

    total_count: int
    results: List[Dict[str, Any]] = field(default_factory=list)
    page: int = 0
    page_size: int = 15

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "SearchResults":
        """Create SearchResults from API response"""
        return cls(
            total_count=data.get("TotalCount", 0),
            results=data.get("Results", []),
            page=data.get("Page", 0),
            page_size=data.get("PageSize", 15),
        )
