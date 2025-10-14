"""
Data models for NSIP API responses
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


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
    # {"BWT": {"min": -1.0, "max": 1.0}}
    trait_ranges: Optional[Dict[str, Dict[str, float]]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API request"""
        data: Dict[str, Any] = {}
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

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        from dataclasses import asdict

        return asdict(self)

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "AnimalDetails":
        """Create AnimalDetails from API response

        Supports both the new nested format (with 'data' wrapper and searchResultViewModel)
        and the legacy flat format (PascalCase fields at root level) for backward compatibility.

        New format structure:
        {
            "success": true,
            "data": {
                "progenyCount": int,
                "dateOfBirth": str,
                "gender": str,
                "genotyped": str,
                "flockCount": str,
                "breed": {
                    "breedName": str,
                    "breedId": int
                },
                "searchResultViewModel": {
                    "lpnId": str,
                    "lpnSre": str (sire),
                    "lpnDam": str (dam),
                    "status": str,
                    "regNumber": str,
                    "bwt": float,
                    "accbwt": float,
                    ...
                },
                "contactInfo": {...}
            }
        }

        Legacy format: PascalCase fields at root level
        """
        # Check if this is the new nested format
        is_nested_format = "data" in data and isinstance(data["data"], dict)

        if is_nested_format:
            # Extract from nested structure
            data_section = data["data"]
            search_result = data_section.get("searchResultViewModel", {})
            breed_obj = data_section.get("breed", {})
            contact_obj = data_section.get("contactInfo", data_section.get("ContactInfo", {}))

            # Extract basic fields from nested structure
            lpn_id = search_result.get("lpnId", "")
            breed_name = breed_obj.get("breedName")
            date_of_birth = data_section.get("dateOfBirth")
            gender = data_section.get("gender")
            status = search_result.get("status")
            sire = search_result.get("lpnSre")
            dam = search_result.get("lpnDam")
            registration_number = search_result.get("regNumber")
            total_progeny = data_section.get("progenyCount")
            flock_count_str = data_section.get("flockCount")
            flock_count = (
                int(flock_count_str) if flock_count_str and str(flock_count_str).isdigit() else None
            )
            genotyped = data_section.get("genotyped")

            # Extract traits from searchResultViewModel
            # The API includes trait values and accuracies as separate fields
            trait_mapping = {
                "bwt": ("BWT", "accbwt"),
                "wwt": ("WWT", "accwwt"),
                "pwwt": ("PWWT", "accpwwt"),
                "ywt": ("YWT", "accywt"),
                "fat": ("FAT", "accfat"),
                "emd": ("EMD", "accemd"),
                "nlb": ("NLB", "accnlb"),
                "nwt": ("NWT", "accnwt"),
                "pwt": ("PWT", "accpwt"),
                "dag": ("DAG", "accdag"),
                "wgr": ("WGR", "accwgr"),
                "wec": ("WEC", "accwec"),
                "fec": ("FEC", "accfec"),
            }

            traits = {}
            for trait_key, (trait_name, acc_key) in trait_mapping.items():
                if trait_key in search_result and search_result[trait_key] is not None:
                    accuracy = search_result.get(acc_key)
                    # Convert accuracy from decimal (0.80) to percentage (80) if needed
                    if accuracy is not None and accuracy <= 1.0:
                        accuracy = int(accuracy * 100)

                    traits[trait_name] = Trait(
                        name=trait_name,
                        value=float(search_result[trait_key]),
                        accuracy=accuracy if accuracy else None,
                    )

            # Extract contact info (handle both camelCase and PascalCase)
            contact = None
            if contact_obj:
                contact = ContactInfo(
                    farm_name=contact_obj.get("farmName", contact_obj.get("FarmName")),
                    contact_name=contact_obj.get("customerName", contact_obj.get("ContactName")),
                    phone=contact_obj.get("phone", contact_obj.get("Phone")),
                    email=contact_obj.get("email", contact_obj.get("Email")),
                    address=contact_obj.get("address", contact_obj.get("Address")),
                    city=contact_obj.get("city", contact_obj.get("City")),
                    state=contact_obj.get("state", contact_obj.get("State")),
                    zip_code=contact_obj.get("zipCode", contact_obj.get("ZipCode")),
                )
        else:
            # Legacy format - extract from root level with PascalCase
            lpn_id = data.get("LpnId", "")
            breed_name = data.get("Breed")
            date_of_birth = data.get("DateOfBirth")
            gender = data.get("Gender")
            status = data.get("Status")
            sire = data.get("Sire")
            dam = data.get("Dam")
            registration_number = data.get("RegistrationNumber")
            total_progeny = data.get("TotalProgeny")
            flock_count = data.get("FlockCount")
            genotyped = data.get("Genotyped")

            # Extract traits from legacy format
            traits = {}
            if "Traits" in data:
                for trait_name, trait_data in data["Traits"].items():
                    if isinstance(trait_data, dict):
                        traits[trait_name] = Trait(
                            name=trait_name,
                            value=trait_data.get("Value", 0),
                            accuracy=trait_data.get("Accuracy"),
                        )

            # Extract contact info from legacy format
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
            lpn_id=lpn_id,
            breed=breed_name,
            breed_group=data.get("BreedGroup"),  # Not present in new format yet
            date_of_birth=date_of_birth,
            gender=gender,
            status=status,
            sire=sire,
            dam=dam,
            registration_number=registration_number,
            total_progeny=total_progeny,
            flock_count=flock_count,
            genotyped=genotyped,
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

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        from dataclasses import asdict

        return asdict(self)


@dataclass
class Progeny:
    """Progeny information for an animal"""

    total_count: int
    animals: List[ProgenyAnimal] = field(default_factory=list)
    page: int = 0
    page_size: int = 10

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "Progeny":
        """Create Progeny from API response

        The progeny endpoint returns a different structure than other endpoints:
        - Uses "records" instead of "Results"
        - Uses "recordCount" instead of "TotalCount"
        - Uses lowercase field names (lpnId, dob, sex) instead of PascalCase
        - Does not include Page/PageSize in response
        """
        animals = []

        # Try both response formats (records vs Results)
        records = data.get("records", data.get("Results", []))

        for animal_data in records:
            # Map lowercase field names to expected format
            progeny_animal = ProgenyAnimal(
                lpn_id=animal_data.get("lpnId", animal_data.get("LpnId", "")),
                sex=animal_data.get("sex", animal_data.get("Sex")),
                date_of_birth=animal_data.get("dob", animal_data.get("DateOfBirth")),
                traits=animal_data.get("Traits", {}),  # Traits still use PascalCase
            )
            animals.append(progeny_animal)

        # Try both field naming conventions
        total_count = data.get("recordCount", data.get("TotalCount", 0))

        return cls(
            total_count=total_count,
            animals=animals,
            page=data.get("Page", 0),
            page_size=data.get("PageSize", len(animals)),
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

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        from dataclasses import asdict

        return asdict(self)

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
        """Create SearchResults from API response

        Supports both PascalCase (TotalCount, Results) and camelCase (recordCount, records)
        """
        return cls(
            total_count=data.get("TotalCount") or data.get("recordCount") or 0,
            results=data.get("Results") or data.get("records") or [],
            page=data.get("Page") or data.get("page") or 0,
            page_size=data.get("PageSize") or data.get("pageSize") or 15,
        )
