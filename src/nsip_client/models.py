"""
Data models for NSIP API responses
"""

import re
from dataclasses import asdict, dataclass, field
from typing import Any

# Precompiled regex patterns for _parse_lineage_content (performance optimization)
_RE_FARM_NAME = re.compile(r"<div>([^<]+)</div>")
_RE_US_INDEX = re.compile(r"US (?:Hair )?Index: ([\d.]+)")
_RE_SRC_INDEX = re.compile(r"SRC\$ Index: ([\d.]+)")
_RE_DOB = re.compile(r"DOB: ([^<]+)")
_RE_SEX = re.compile(r"Sex: ([^<]+)")
_RE_STATUS = re.compile(r"Status: ([^<]+)")


@dataclass
class SearchCriteria:
    """Search criteria for animal search"""

    breed_group_id: int | None = None
    breed_id: int | None = None
    born_after: str | None = None  # Format: YYYY-MM-DD
    born_before: str | None = None  # Format: YYYY-MM-DD
    gender: str | None = None  # "Male", "Female", "Both"
    proven_only: bool | None = None
    status: str | None = None  # "CURRENT", "SOLD", "DEAD", etc.
    flock_id: str | None = None
    # {"BWT": {"min": -1.0, "max": 1.0}}
    trait_ranges: dict[str, dict[str, float]] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API request"""
        data: dict[str, Any] = {}
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
    accuracy: int | None = None
    units: str | None = None


@dataclass
class ContactInfo:
    """Contact information for animal owner"""

    farm_name: str | None = None
    contact_name: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None


@dataclass
class AnimalDetails:
    """Detailed information about an animal"""

    lpn_id: str
    breed: str | None = None
    breed_group: str | None = None
    date_of_birth: str | None = None
    gender: str | None = None
    status: str | None = None
    sire: str | None = None
    dam: str | None = None
    registration_number: str | None = None
    total_progeny: int | None = None
    flock_count: int | None = None
    genotyped: str | None = None
    traits: dict[str, Trait] = field(default_factory=dict)
    contact_info: ContactInfo | None = None
    raw_data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AnimalDetails":
        """Reconstruct AnimalDetails from a to_dict() output.

        This handles the snake_case format produced by to_dict(), which differs
        from the API response format handled by from_api_response().
        """
        # Reconstruct traits from serialized dicts
        traits = {}
        if "traits" in data and isinstance(data["traits"], dict):
            for name, trait_data in data["traits"].items():
                if isinstance(trait_data, dict):
                    traits[name] = Trait(
                        name=trait_data.get("name") or name,
                        value=trait_data.get("value", 0.0),
                        accuracy=trait_data.get("accuracy"),
                        units=trait_data.get("units"),
                    )

        # Reconstruct contact info
        contact = None
        if "contact_info" in data and data["contact_info"]:
            ci = data["contact_info"]
            contact = ContactInfo(
                farm_name=ci.get("farm_name"),
                contact_name=ci.get("contact_name"),
                phone=ci.get("phone"),
                email=ci.get("email"),
                address=ci.get("address"),
                city=ci.get("city"),
                state=ci.get("state"),
                zip_code=ci.get("zip_code"),
            )

        return cls(
            lpn_id=data.get("lpn_id", ""),
            breed=data.get("breed"),
            breed_group=data.get("breed_group"),
            date_of_birth=data.get("date_of_birth"),
            gender=data.get("gender"),
            status=data.get("status"),
            sire=data.get("sire"),
            dam=data.get("dam"),
            registration_number=data.get("registration_number"),
            total_progeny=data.get("total_progeny"),
            flock_count=data.get("flock_count"),
            genotyped=data.get("genotyped"),
            traits=traits,
            contact_info=contact,
            raw_data=data.get("raw_data", {}),
        )

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> "AnimalDetails":
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
    sex: str | None = None
    date_of_birth: str | None = None
    traits: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return asdict(self)


@dataclass
class Progeny:
    """Progeny information for an animal"""

    total_count: int
    animals: list[ProgenyAnimal] = field(default_factory=list)
    page: int = 0
    page_size: int = 10

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> "Progeny":
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


def _parse_lineage_content(content: str) -> dict[str, Any]:
    """Extract fields from HTML content string in lineage response.

    The NSIP lineage API returns data embedded in HTML divs like:
    <div>Farm Name</div><div>US Hair Index: 102.03</div><div>DOB: 2/13/2024</div>...

    Uses precompiled regex patterns (_RE_*) for performance in batch operations.
    """
    result: dict[str, Any] = {}

    # Farm name (first div content)
    farm_match = _RE_FARM_NAME.search(content)
    if farm_match:
        result["farm_name"] = farm_match.group(1)

    # US Hair Index or US Index
    us_match = _RE_US_INDEX.search(content)
    if us_match:
        result["us_index"] = float(us_match.group(1))

    # SRC$ Index
    src_match = _RE_SRC_INDEX.search(content)
    if src_match:
        result["src_index"] = float(src_match.group(1))

    # Date of Birth
    dob_match = _RE_DOB.search(content)
    if dob_match:
        result["date_of_birth"] = dob_match.group(1).strip()

    # Sex
    sex_match = _RE_SEX.search(content)
    if sex_match:
        result["sex"] = sex_match.group(1).strip()

    # Status
    status_match = _RE_STATUS.search(content)
    if status_match:
        result["status"] = status_match.group(1).strip()

    return result


@dataclass
class LineageAnimal:
    """Individual animal in lineage/pedigree"""

    lpn_id: str
    farm_name: str | None = None
    us_index: float | None = None
    src_index: float | None = None
    date_of_birth: str | None = None
    sex: str | None = None
    status: str | None = None


@dataclass
class Lineage:
    """Pedigree/lineage information"""

    subject: LineageAnimal | None = None
    sire: LineageAnimal | None = None
    dam: LineageAnimal | None = None
    generations: list[list[LineageAnimal]] = field(default_factory=list)
    raw_data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return asdict(self)

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> "Lineage":
        """Create Lineage from API response.

        Parses the nested HTML structure returned by NSIP lineage endpoint.
        Structure: {lpnId, content (HTML), children: [sire, dam]}

        The API returns a tree where each node has:
        - lpnId: Animal identifier
        - content: HTML string with farm name, indexes, DOB, etc.
        - children: Array of [sire_node, dam_node] (recursive)
        """
        # Handle wrapped response format
        if "data" in data and isinstance(data["data"], dict):
            node = data["data"]
        else:
            node = data

        def parse_node(n: dict[str, Any] | None) -> LineageAnimal | None:
            """Parse a single node into LineageAnimal."""
            if not n or "lpnId" not in n:
                return None
            content = n.get("content", "")
            parsed = _parse_lineage_content(content)
            return LineageAnimal(
                lpn_id=n["lpnId"],
                farm_name=parsed.get("farm_name"),
                us_index=parsed.get("us_index"),
                src_index=parsed.get("src_index"),
                date_of_birth=parsed.get("date_of_birth"),
                sex=parsed.get("sex"),
                status=parsed.get("status"),
            )

        def collect_generations(
            n: dict[str, Any], generations: list[list[LineageAnimal]], depth: int = 0
        ) -> None:
            """Recursively collect ancestors by generation depth."""
            children = n.get("children", [])
            if not children:
                return

            # Ensure generation list exists for this depth
            while len(generations) <= depth:
                generations.append([])

            # Add children (sire, dam) to this generation
            for child in children:
                animal = parse_node(child)
                if animal:
                    generations[depth].append(animal)
                # Recurse into grandchildren
                collect_generations(child, generations, depth + 1)

        # Parse subject animal
        subject = parse_node(node)

        # Parse parents (first level children)
        children = node.get("children", [])
        sire = parse_node(children[0]) if len(children) > 0 else None
        dam = parse_node(children[1]) if len(children) > 1 else None

        # Collect all generations recursively
        generations: list[list[LineageAnimal]] = []
        collect_generations(node, generations)

        return cls(
            subject=subject,
            sire=sire,
            dam=dam,
            generations=generations,
            raw_data=data,
        )


@dataclass
class BreedGroup:
    """Breed group information"""

    id: int
    name: str
    breeds: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class SearchResults:
    """Search results container"""

    total_count: int
    results: list[dict[str, Any]] = field(default_factory=list)
    page: int = 0
    page_size: int = 15

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> "SearchResults":
        """Create SearchResults from API response

        Supports both PascalCase (TotalCount, Results) and camelCase (recordCount, records)
        """
        return cls(
            total_count=data.get("TotalCount") or data.get("recordCount") or 0,
            results=data.get("Results") or data.get("records") or [],
            page=data.get("Page") or data.get("page") or 0,
            page_size=data.get("PageSize") or data.get("pageSize") or 15,
        )
