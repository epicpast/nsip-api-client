# API Reference

Complete API reference for the NSIP Client.

## NSIPClient

Main client class for interacting with the NSIP API.

### Constructor

```python
NSIPClient(timeout: int = 30, base_url: str = None)
```

**Parameters:**
- `timeout` (int): Request timeout in seconds. Default: 30
- `base_url` (str, optional): Override the base URL for testing

**Example:**
```python
from nsip_client import NSIPClient

client = NSIPClient(timeout=60)
```

### Methods

#### get_date_last_updated()

Get the date when the database was last updated.

**Returns:** `Dict[str, Any]` - Dictionary containing update date

**Example:**
```python
info = client.get_date_last_updated()
print(info)  # {'date': '09/23/2025'}
```

---

#### get_available_breed_groups()

Get list of all available breed groups.

**Returns:** `List[BreedGroup]` - List of breed group objects

**Example:**
```python
groups = client.get_available_breed_groups()
for group in groups:
    print(f"{group.id}: {group.name}")
```

---

#### get_statuses_by_breed_group()

Get list of available animal status values.

**Returns:** `List[str]` - List of status strings

**Example:**
```python
statuses = client.get_statuses_by_breed_group()
print(statuses)  # ['CURRENT', 'SOLD', 'DEAD', ...]
```

---

#### get_trait_ranges_by_breed(breed_id: int)

Get the min/max trait ranges for a specific breed.

**Parameters:**
- `breed_id` (int): The breed ID

**Returns:** `Dict[str, Any]` - Trait ranges

**Raises:**
- `NSIPValidationError`: If breed_id is invalid

**Example:**
```python
ranges = client.get_trait_ranges_by_breed(486)
print(ranges['BWT'])  # {'min': -0.713, 'max': 0.0}
```

---

#### search_animals()

Search for animals based on criteria.

```python
search_animals(
    page: int = 0,
    page_size: int = 15,
    breed_id: Optional[int] = None,
    sorted_trait: Optional[str] = None,
    reverse: Optional[bool] = None,
    search_criteria: Optional[Union[SearchCriteria, Dict]] = None
) -> SearchResults
```

**Parameters:**
- `page` (int): Page number (0-indexed). Default: 0
- `page_size` (int): Results per page (1-100). Default: 15
- `breed_id` (int, optional): Filter by breed ID
- `sorted_trait` (str, optional): Trait to sort by (e.g., "BWT")
- `reverse` (bool, optional): Sort in reverse order
- `search_criteria` (SearchCriteria | dict, optional): Additional filters

**Returns:** `SearchResults` - Search results with pagination

**Raises:**
- `NSIPValidationError`: If parameters are invalid

**Example:**
```python
# Simple search
results = client.search_animals(breed_id=486, page_size=10)

# With criteria
from nsip_client import SearchCriteria
criteria = SearchCriteria(gender="Female", status="CURRENT")
results = client.search_animals(breed_id=486, search_criteria=criteria)

# Pagination
for page in range(3):
    results = client.search_animals(breed_id=486, page=page)
    print(f"Page {page}: {len(results.results)} animals")
```

---

#### get_animal_details(search_string: str)

Get detailed information about a specific animal.

**Parameters:**
- `search_string` (str): LPN ID or registration number

**Returns:** `AnimalDetails` - Complete animal information

**Raises:**
- `NSIPNotFoundError`: If animal not found
- `NSIPValidationError`: If search_string is empty

**Example:**
```python
animal = client.get_animal_details("6####92020###249")
print(f"Breed: {animal.breed}")
print(f"Gender: {animal.gender}")
print(f"DOB: {animal.date_of_birth}")

# Access traits
bwt = animal.traits['BWT']
print(f"BWT: {bwt.value} (Accuracy: {bwt.accuracy}%)")
```

---

#### get_lineage(lpn_id: str)

Get pedigree/lineage information for an animal.

**Parameters:**
- `lpn_id` (str): The LPN ID

**Returns:** `Lineage` - Pedigree information

**Raises:**
- `NSIPValidationError`: If lpn_id is empty

**Example:**
```python
lineage = client.get_lineage("6####92020###249")
# Note: Lineage structure depends on API response format
```

---

#### get_progeny(lpn_id: str, page: int = 0, page_size: int = 10)

Get offspring for a specific animal.

**Parameters:**
- `lpn_id` (str): Parent animal's LPN ID
- `page` (int): Page number (0-indexed). Default: 0
- `page_size` (int): Results per page. Default: 10

**Returns:** `Progeny` - Progeny information with pagination

**Raises:**
- `NSIPValidationError`: If parameters are invalid

**Example:**
```python
progeny = client.get_progeny("6####92020###249")
print(f"Total offspring: {progeny.total_count}")

for offspring in progeny.animals:
    print(f"  {offspring.lpn_id} - {offspring.sex}")
    print(f"  DOB: {offspring.date_of_birth}")
    print(f"  Traits: {offspring.traits}")
```

---

#### search_by_lpn(lpn_id: str)

Convenience method to get complete animal profile.

**Parameters:**
- `lpn_id` (str): LPN ID to search

**Returns:** `Dict[str, Any]` - Dictionary with keys:
- `details`: AnimalDetails object
- `lineage`: Lineage object
- `progeny`: Progeny object

**Example:**
```python
profile = client.search_by_lpn("6####92020###249")
print(profile['details'].breed)
print(f"Progeny count: {profile['progeny'].total_count}")
```

---

#### close()

Close the HTTP session.

**Example:**
```python
client.close()
```

### Context Manager

The client supports context manager protocol:

```python
with NSIPClient() as client:
    animal = client.get_animal_details("6####92020###249")
    print(animal.breed)
# Session automatically closed
```

---

## Data Models

### AnimalDetails

Represents detailed animal information.

**Attributes:**
- `lpn_id` (str): LPN ID
- `breed` (str): Breed name
- `breed_group` (str): Breed group name
- `date_of_birth` (str): Date of birth
- `gender` (str): Gender (Male/Female)
- `status` (str): Status (CURRENT, SOLD, etc.)
- `sire` (str): Sire LPN ID
- `dam` (str): Dam LPN ID
- `registration_number` (str): Registration number
- `total_progeny` (int): Number of offspring
- `flock_count` (int): Flock count
- `genotyped` (str): Genotyping status
- `traits` (Dict[str, Trait]): Dictionary of traits
- `contact_info` (ContactInfo): Owner contact info
- `raw_data` (Dict): Raw API response

**Methods:**
- `from_api_response(data: Dict) -> AnimalDetails`: Create from API response

---

### Trait

Represents a single genetic trait (EBV).

**Attributes:**
- `name` (str): Trait name (e.g., "BWT")
- `value` (float): Trait value
- `accuracy` (int, optional): Accuracy percentage
- `units` (str, optional): Units of measurement

---

### Progeny

Represents progeny information.

**Attributes:**
- `total_count` (int): Total number of offspring
- `animals` (List[ProgenyAnimal]): List of offspring
- `page` (int): Current page number
- `page_size` (int): Results per page

**Methods:**
- `from_api_response(data: Dict) -> Progeny`: Create from API response

---

### ProgenyAnimal

Individual offspring animal.

**Attributes:**
- `lpn_id` (str): LPN ID
- `sex` (str): Sex (M/F)
- `date_of_birth` (str): Date of birth
- `traits` (Dict[str, float]): Trait values

---

### SearchCriteria

Search filter criteria.

**Attributes:**
- `breed_group_id` (int, optional): Breed group filter
- `breed_id` (int, optional): Breed filter
- `born_after` (str, optional): Birth date start (YYYY-MM-DD)
- `born_before` (str, optional): Birth date end (YYYY-MM-DD)
- `gender` (str, optional): Gender filter
- `proven_only` (bool, optional): Only proven animals
- `status` (str, optional): Status filter
- `flock_id` (str, optional): Flock ID filter
- `trait_ranges` (Dict, optional): Trait range filters

**Methods:**
- `to_dict() -> Dict`: Convert to API request format

---

### SearchResults

Search results container.

**Attributes:**
- `total_count` (int): Total matching records
- `results` (List[Dict]): Current page results
- `page` (int): Current page number
- `page_size` (int): Page size

**Methods:**
- `from_api_response(data: Dict) -> SearchResults`: Create from API response

---

### ContactInfo

Owner contact information.

**Attributes:**
- `farm_name` (str): Farm name
- `contact_name` (str): Contact person
- `phone` (str): Phone number
- `email` (str): Email address
- `address` (str): Street address
- `city` (str): City
- `state` (str): State
- `zip_code` (str): ZIP code

---

## Exceptions

### NSIPError

Base exception for all NSIP client errors.

### NSIPAPIError

Raised when the API returns an error.

**Attributes:**
- `status_code` (int): HTTP status code
- `response` (str): Error response text

### NSIPNotFoundError

Raised when an animal or resource is not found.

**Attributes:**
- `search_string` (str): The search string that wasn't found

### NSIPConnectionError

Raised when connection to API fails.

### NSIPTimeoutError

Raised when request times out.

### NSIPValidationError

Raised when request parameters are invalid.

---

## CLI Reference

The package includes a command-line tool: `nsip-search`

### Commands

#### breeds

List available breed groups:
```bash
nsip-search breeds
```

#### search

Search for an animal by LPN ID:
```bash
# Basic search
nsip-search search 6####92020###249

# Get full profile
nsip-search search 6####92020###249 --full
```

#### find

Search for animals with filters:
```bash
# Search by breed
nsip-search find --breed-id 486

# Pagination
nsip-search find --breed-id 486 --page 2 --page-size 20
```

#### --version

Show version:
```bash
nsip-search --version
```
