# NSIP Search API Client

A Python client for the NSIP (National Sheep Improvement Program) Search API, reverse-engineered from http://nsipsearch.nsip.org

## Overview

This client provides programmatic access to sheep breeding data including:
- Animal details and genetic traits (EBVs)
- Pedigree/lineage information
- Progeny records
- Breed groups and trait ranges
- Search and filtering capabilities

## Installation

### From GitHub Release (Recommended)

Download the latest release from the [releases page](https://github.com/epicpast/nsip-api-client/releases):

```bash
# Install from wheel (recommended)
pip install https://github.com/epicpast/nsip-api-client/releases/latest/download/nsip_client-1.0.0-py3-none-any.whl

# Or install from source distribution
pip install https://github.com/epicpast/nsip-api-client/releases/download/v1.0.0/nsip-client-1.0.0.tar.gz
```

### From Git

```bash
# Install latest from main branch
pip install git+https://github.com/epicpast/nsip-api-client.git

# Install specific version tag
pip install git+https://github.com/epicpast/nsip-api-client.git@v1.0.0
```

### From Source

```bash
git clone https://github.com/epicpast/nsip-api-client.git
cd nsip-api-client
pip install -e .
```

## API Endpoints Discovered

### Base URL
```
http://nsipsearch.nsip.org/api
```

### Authentication
No authentication required - this is a public API.

### Endpoints

#### Search & Metadata
- `GET /search/getDateLastUpdated` - Get database last update date
- `GET /search/getAvailableBreedGroups` - List all breed groups
- `GET /search/getStatusesByBreedGroup` - List animal statuses
- `GET /search/getTraitRangesByBreed?breedId={id}` - Get trait ranges for a breed
- `POST /search/getPageOfSearchResults?page={p}&pageSize={size}&breedId={id}` - Search animals

#### Animal Details
- `GET /details/getAnimalDetails?searchString={lpnId}` - Get animal details
- `GET /details/getLineage?lpnId={lpnId}` - Get pedigree/lineage
- `GET /details/getPageOfProgeny?lpnId={lpnId}&page={p}&pageSize={size}` - Get offspring

## Usage

### Basic Example

```python
from nsip_client import NSIPClient

# Initialize client
client = NSIPClient()

# Get animal details
animal = client.get_animal_details("6401492020FLE249")
print(f"Breed: {animal['Breed']}")
print(f"DOB: {animal['DateOfBirth']}")

# Get progeny
progeny = client.get_progeny("6401492020FLE249")
print(f"Total offspring: {progeny['TotalCount']}")

# Get lineage
lineage = client.get_lineage("6401492020FLE249")
```

### Search Animals

```python
# Search by breed
results = client.search_animals(
    breed_id=486,  # South African Meat Merino
    page=0,
    page_size=15
)

for animal in results['Results']:
    print(animal['LpnId'])
```

### Get Breed Information

```python
# Get all breed groups
breed_groups = client.get_available_breed_groups()
for group in breed_groups:
    print(f"{group['Id']}: {group['Name']}")

# Get trait ranges for a breed
trait_ranges = client.get_trait_ranges_by_breed(486)
```

### Complete Animal Profile

```python
# Get all information at once
profile = client.search_by_lpn("6401492020FLE249")
print(profile['details'])
print(profile['lineage'])
print(profile['progeny'])
```

## API Response Structure

### Animal Details Response
```json
{
  "LpnId": "6401492020FLE249",
  "Breed": "Katahdin",
  "BreedGroup": "Hair",
  "DateOfBirth": "2/5/2020",
  "Gender": "Female",
  "Status": "CURRENT",
  "Sire": "6401492019FLE124",
  "Dam": "6401492018FLE035",
  "TotalProgeny": 6,
  "Genotyped": "No",
  "Traits": {
    "BWT": {"Value": 0.246, "Accuracy": 74},
    "WWT": {"Value": 3.051, "Accuracy": 71},
    ...
  },
  "ContactInfo": {
    "FarmName": "Beyond Blessed Farm",
    "ContactName": "Chris and Mandy Fletcher",
    "Phone": "(276)-759-4718",
    "Email": "mbfletcher08@gmail.com"
  }
}
```

## Breed Groups

- **61** - Range
- **62** - Maternal Wool
- **64** - Hair
- **69** - Terminal

## Common Traits (EBVs)

### Growth Traits
- **BWT** - Birth Weight
- **WWT** - Weaning Weight
- **MWWT** - Maternal Weaning Weight
- **PWWT** - Post Weaning Weight
- **YWT** - Yearling Weight

### Carcass Traits
- **YEMD** - Yearling Eye Muscle Depth
- **YFAT** - Yearling Fat
- **PEMD** - Post Weaning Eye Muscle Depth
- **PFAT** - Post Weaning Fat

### Wool Traits (for wool breeds)
- **YGFW** - Yearling Greasy Fleece Weight
- **YFD** - Yearling Fibre Diameter
- **YSL** - Yearling Staple Length

### Reproduction
- **NLB** - Number of Lambs Born
- **NLW** - Number of Lambs Weaned

### Parasite Resistance
- **WFEC** - Weaning Fecal Egg Count
- **PFEC** - Post Weaning Fecal Egg Count

### Indexes
- **US Range Index**
- **US Hair Index**
- **SRC$ Index**

## Network Traffic Analysis

The API was reverse-engineered using Chrome DevTools by:
1. Loading http://nsipsearch.nsip.org/#!/search
2. Performing searches and viewing animal details
3. Capturing network requests to identify API endpoints
4. Analyzing request/response headers and payloads

### Headers Used
```
Accept: application/json, text/plain, */*
User-Agent: Mozilla/5.0...
```

No authentication headers, cookies, or API keys required.

## Limitations

- This is a reverse-engineered client based on public web traffic
- The API is not officially documented
- Endpoints may change without notice
- Rate limiting behavior is unknown
- Some endpoints (like breed list by group) may need additional discovery

## Example: Your Sheep

```python
client = NSIPClient()

# Get details for your sheep
my_sheep = client.search_by_lpn("6401492020FLE249")

print(f"Name/ID: {my_sheep['details']['LpnId']}")
print(f"Breed: {my_sheep['details']['Breed']}")
print(f"Farm: {my_sheep['details']['ContactInfo']['FarmName']}")
print(f"Total Progeny: {my_sheep['details']['TotalProgeny']}")
print(f"US Hair Index: {my_sheep['details']['Traits']['USHairIndex']['Value']}")
```

## License

This client is provided as-is for educational and research purposes. The NSIP data remains property of the National Sheep Improvement Program.
