# NSIP MCP Resources Documentation

## Table of Contents

1. [Overview](#overview)
2. [Resource URI Scheme](#resource-uri-scheme)
3. [Static Resources](#static-resources)
   - [Heritabilities](#heritabilities)
   - [Selection Indexes](#selection-indexes)
   - [Trait Glossary](#trait-glossary)
   - [Region Information](#region-information)
   - [Disease Guides](#disease-guides)
   - [Nutrition Guidelines](#nutrition-guidelines)
   - [Calendar Templates](#calendar-templates)
   - [Economics Data](#economics-data)
4. [Usage Examples](#usage-examples)
5. [Integration with MCP Clients](#integration-with-mcp-clients)
6. [Caching Behavior](#caching-behavior)
7. [Error Handling](#error-handling)

---

## Overview

MCP Resources provide a standardized way for LLM applications to access structured data from the NSIP knowledge base. Unlike MCP Tools that execute operations, Resources expose read-only data through URI-based access patterns.

### Key Benefits

- **Static Knowledge Access**: Trait definitions, heritabilities, and selection indexes
- **Regional Adaptation**: Disease guides, nutrition, and calendar data by region
- **LRU Caching**: Efficient repeated access with automatic cache management
- **Structured Data**: JSON responses with consistent schemas

### Architecture

```
MCP Client (LLM)
      │
      ▼
┌─────────────────────────────────────────────────────────┐
│                    MCP Resource Layer                    │
│  ┌──────────────────────────────────────────────────┐   │
│  │  FastMCP @mcp.resource() Decorated Functions      │   │
│  │  - URI template parsing                           │   │
│  │  - Request routing                                │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Knowledge Base Layer                             │   │
│  │  - YAML file loading                              │   │
│  │  - LRU cache (50 entries)                         │   │
│  │  - Schema validation                              │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────────┐
│              YAML Data Files (knowledge_base/data/)      │
│  heritabilities.yaml, diseases.yaml, nutrition.yaml,    │
│  selection_indexes.yaml, trait_glossary.yaml,           │
│  regions.yaml, calendar_templates.yaml, economics.yaml  │
└─────────────────────────────────────────────────────────┘
```

---

## Resource URI Scheme

All NSIP resources use the `nsip://` URI scheme:

```
nsip://static/{category}/{identifier}
```

### URI Patterns

| URI Pattern | Description | Parameters |
|-------------|-------------|------------|
| `nsip://static/heritabilities` | Default heritabilities | None |
| `nsip://static/heritabilities/{breed}` | Breed-specific heritabilities | breed: string |
| `nsip://static/indexes` | All selection indexes | None |
| `nsip://static/indexes/{index_name}` | Specific index details | index_name: string |
| `nsip://static/traits` | All trait definitions | None |
| `nsip://static/traits/{trait_code}` | Specific trait info | trait_code: string |
| `nsip://static/regions` | All NSIP regions | None |
| `nsip://static/regions/{region}` | Specific region details | region: string |
| `nsip://static/diseases/{region}` | Disease guide for region | region: string |
| `nsip://static/nutrition/{region}/{season}` | Nutrition guide | region, season: string |
| `nsip://static/calendar` | Calendar templates | None |
| `nsip://static/economics/{category}` | Economics data | category: string |

---

## Static Resources

### Heritabilities

Heritability values indicate how much of trait variation is due to genetics. Higher values mean faster genetic progress through selection.

**URI:** `nsip://static/heritabilities` or `nsip://static/heritabilities/{breed}`

**Response Structure:**
```json
{
  "BWT": {"heritability": 0.30, "genetic_sd": 0.5, "units": "lbs"},
  "WWT": {"heritability": 0.25, "genetic_sd": 3.0, "units": "lbs"},
  "PWWT": {"heritability": 0.30, "genetic_sd": 4.0, "units": "lbs"},
  "NLW": {"heritability": 0.10, "genetic_sd": 0.15, "units": "count"},
  "YEMD": {"heritability": 0.35, "genetic_sd": 1.5, "units": "mm"},
  "YFAT": {"heritability": 0.25, "genetic_sd": 0.8, "units": "mm"}
}
```

**Available Breeds:**
- `default` - General sheep populations
- `katahdin` - Katahdin hair sheep
- `dorper` - Dorper and White Dorper
- `suffolk` - Suffolk terminal sires
- `hampshire` - Hampshire terminal sires

---

### Selection Indexes

Pre-defined trait weightings for common breeding goals.

**URI:** `nsip://static/indexes` or `nsip://static/indexes/{index_name}`

**Available Indexes:**

| Index Name | Description | Primary Traits |
|------------|-------------|----------------|
| `terminal` | Maximum growth and carcass merit | WWT, PWWT, YEMD, YFAT |
| `maternal` | Reproductive efficiency | NLW, MWWT, BWT |
| `range` | Hardiness for extensive systems | WWT, NLW, fleece |
| `hair` | Hair sheep emphasis | WWT, NLW, PFEC |
| `balanced` | Equal growth and maternal | All traits |

**Response Structure (single index):**
```json
{
  "name": "Terminal Sire Index",
  "description": "Emphasizes growth and carcass traits for terminal sires",
  "goal": "terminal",
  "traits": {
    "WWT": {"weight": 0.25, "direction": "positive"},
    "PWWT": {"weight": 0.30, "direction": "positive"},
    "YEMD": {"weight": 0.25, "direction": "positive"},
    "YFAT": {"weight": 0.20, "direction": "negative"}
  },
  "typical_applications": [
    "Suffolk, Hampshire, Texel sire selection",
    "Commercial lamb production",
    "Feedlot performance emphasis"
  ]
}
```

---

### Trait Glossary

Comprehensive trait definitions, units, and interpretation guidance.

**URI:** `nsip://static/traits` or `nsip://static/traits/{trait_code}`

**Response Structure (single trait):**
```json
{
  "code": "WWT",
  "name": "Weaning Weight",
  "description": "Direct genetic effect on lamb weight at weaning (approximately 120 days)",
  "category": "growth",
  "units": "lbs",
  "positive_is_better": true,
  "breed_averages": {
    "katahdin": 2.5,
    "suffolk": 4.0,
    "dorper": 3.0
  },
  "interpretation": {
    "excellent": "> 5.0",
    "above_average": "2.5 to 5.0",
    "average": "-1.0 to 2.5",
    "below_average": "< -1.0"
  }
}
```

**Trait Categories:**
- **Growth**: BWT, WWT, MWWT, PWWT, YWT
- **Carcass**: YEMD, YFAT, PEMD, PFAT
- **Reproduction**: NLB, NLW
- **Parasite Resistance**: WFEC, PFEC
- **Wool**: YGFW, YFD, YSL

---

### Region Information

NSIP regions with climate, breeds, and seasonal considerations.

**URI:** `nsip://static/regions` or `nsip://static/regions/{region}`

**Available Regions:**

| Region | States Covered |
|--------|----------------|
| `northeast` | ME, NH, VT, MA, RI, CT, NY, NJ, PA |
| `southeast` | MD, DE, VA, WV, NC, SC, GA, FL, AL, MS, LA, TN, KY |
| `midwest` | OH, IN, IL, MI, WI, MN, IA, MO, ND, SD, NE, KS |
| `southwest` | TX, OK, AR, AZ, NM |
| `mountain` | MT, WY, CO, UT, ID, NV |
| `pacific` | WA, OR, CA, AK, HI |

**Response Structure:**
```json
{
  "name": "Midwest",
  "states": ["OH", "IN", "IL", "MI", "WI", "MN", "IA", "MO", "ND", "SD", "NE", "KS"],
  "climate": "Continental with cold winters and hot summers",
  "common_breeds": ["Katahdin", "Dorper", "Suffolk", "Hampshire"],
  "parasite_season": "April through October",
  "primary_lambing": "February-April",
  "challenges": [
    "Cold stress in winter lambing",
    "Summer parasite pressure",
    "Predator management"
  ],
  "extension_contacts": {
    "ohio": "Ohio State University Extension",
    "michigan": "Michigan State University Extension"
  }
}
```

---

### Disease Guides

Region-specific disease prevention and management guidance.

**URI:** `nsip://static/diseases/{region}`

**Response Structure:**
```json
{
  "Ovine Progressive Pneumonia": {
    "risk_level": "moderate",
    "season": "year-round",
    "prevention": "Test and cull positive animals, closed flock",
    "signs": ["chronic weight loss", "respiratory distress", "hard udder"],
    "treatment": "No cure; manage through prevention"
  },
  "Haemonchus contortus": {
    "risk_level": "high",
    "season": "spring-fall",
    "prevention": "FAMACHA scoring, targeted selective treatment, pasture rotation",
    "signs": ["bottle jaw", "pale membranes", "weakness"],
    "treatment": "Effective anthelmintic based on FECRT"
  }
}
```

---

### Nutrition Guidelines

Life stage nutrition requirements with regional adjustments.

**URI:** `nsip://static/nutrition/{region}/{season}`

**Life Stages:**
- `maintenance` - Non-pregnant, non-lactating ewes
- `flushing` - Pre-breeding nutrition boost
- `gestation` - Early and late pregnancy
- `lactation` - Nursing ewes (singles, twins, triplets)

**Response Structure:**
```json
{
  "life_stage": "lactation",
  "region": "midwest",
  "season": "spring",
  "requirements": {
    "energy": {
      "singles": "4.0-4.5 Mcal ME/day",
      "twins": "5.0-6.0 Mcal ME/day"
    },
    "protein": {
      "singles": "13-15% CP",
      "twins": "15-17% CP"
    },
    "minerals": "High calcium, selenium, zinc",
    "water": "2.5-4 gallons/day"
  },
  "regional_notes": [
    "Selenium supplementation recommended in Midwest",
    "Spring pasture may cause grass tetany"
  ],
  "feed_options": [
    "High-quality hay + grain supplement",
    "Improved pasture with protein supplement",
    "Total mixed ration"
  ]
}
```

---

### Calendar Templates

Seasonal management task checklists.

**URI:** `nsip://static/calendar`

**Response Structure:**
```json
{
  "months": {
    "january": {
      "breeding": ["Late gestation nutrition increase", "Lamb jug preparation"],
      "health": ["Pre-lambing vaccinations (CDT)", "Body condition scoring"],
      "nutrition": ["Increase energy for late gestation"],
      "management": ["Prepare lambing supplies", "Check facilities"]
    },
    "march": {
      "breeding": ["Peak lambing season", "Lamb processing"],
      "health": ["Navel dipping", "Selenium/E for newborns"],
      "nutrition": ["Peak lactation feeding"],
      "management": ["Record keeping", "Creep feeding"]
    }
  },
  "task_templates": {
    "pre_lambing_checklist": [...],
    "lamb_processing": [...],
    "weaning_tasks": [...]
  }
}
```

---

### Economics Data

Cost templates and market information.

**URI:** `nsip://static/economics/{category}`

**Categories:**
- `cost_templates` - Annual costs per ewe and per lamb
- `revenue_templates` - Revenue sources and estimates
- `feed_costs` - Feed cost breakdown

**Response Structure (cost_templates):**
```json
{
  "cost_templates": {
    "annual_per_ewe": {
      "feed": {"low": 40, "average": 60, "high": 90},
      "minerals": {"low": 8, "average": 12, "high": 18},
      "health": {"low": 10, "average": 18, "high": 30},
      "shearing": {"low": 5, "average": 8, "high": 12},
      "labor": {"low": 15, "average": 25, "high": 40},
      "facilities": {"low": 8, "average": 15, "high": 25},
      "overhead": {"low": 5, "average": 10, "high": 15},
      "ram_share": {"low": 5, "average": 8, "high": 12}
    },
    "per_lamb": {
      "creep_feed": {"average": 15},
      "grower_feed": {"average": 25},
      "health": {"average": 8},
      "marketing": {"average": 10}
    }
  }
}
```

---

## Usage Examples

### Python Direct Access

```python
from nsip_mcp.knowledge_base import (
    get_heritabilities,
    get_trait_info,
    get_selection_index,
    get_region_info,
    get_disease_guide,
    get_nutrition_guide,
)

# Get default heritabilities
herit = get_heritabilities()
print(f"WWT heritability: {herit['WWT']['heritability']}")

# Get trait interpretation
trait = get_trait_info("WWT")
print(f"Trait: {trait['name']} - {trait['description']}")

# Get selection index
index = get_selection_index("terminal")
print(f"Index: {index['name']}")

# Get regional information
region = get_region_info("midwest")
print(f"Region climate: {region['climate']}")

# Get disease guide
diseases = get_disease_guide("southeast")
for disease, info in diseases.items():
    print(f"{disease}: Risk {info['risk_level']}")
```

### MCP Client Access

```json
{
  "jsonrpc": "2.0",
  "method": "resources/read",
  "params": {
    "uri": "nsip://static/traits/WWT"
  },
  "id": 1
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "contents": [{
      "uri": "nsip://static/traits/WWT",
      "mimeType": "application/json",
      "text": "{\"code\":\"WWT\",\"name\":\"Weaning Weight\",...}"
    }]
  },
  "id": 1
}
```

---

## Integration with MCP Clients

### Claude Desktop Configuration

MCP Resources are automatically available when the NSIP MCP Server is configured:

```json
{
  "mcpServers": {
    "nsip": {
      "command": "nsip-mcp-server",
      "env": {
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

### Listing Available Resources

```json
{
  "jsonrpc": "2.0",
  "method": "resources/list",
  "id": 1
}
```

---

## Caching Behavior

### LRU Cache

- **Cache Size**: 50 entries maximum
- **Eviction Policy**: Least Recently Used
- **Lifetime**: Per-server-session (cleared on restart)

### Cache Keys

```python
# YAML file loading cached by filename
cache_key = "heritabilities.yaml"
cache_key = "regions.yaml"
```

### When to Expect Fresh Data

- After server restart
- When cache is full and entry was evicted
- When underlying YAML files are modified

---

## Error Handling

### KnowledgeBaseError

Raised when requested data is not found.

```python
from nsip_mcp.knowledge_base.loader import KnowledgeBaseError

try:
    trait = get_trait_info("INVALID_TRAIT")
except KnowledgeBaseError as e:
    print(f"Error: {e}")  # "Trait 'INVALID_TRAIT' not found"
```

### Error Response Format

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32602,
    "message": "Resource not found: nsip://static/traits/INVALID",
    "data": {
      "uri": "nsip://static/traits/INVALID",
      "suggestion": "Check available traits with nsip://static/traits"
    }
  },
  "id": 1
}
```

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Trait not found` | Invalid trait code | Use `list_traits()` for valid codes |
| `Region not found` | Invalid region name | Use lowercase: `midwest`, not `Midwest` |
| `Index not found` | Invalid index name | Options: `terminal`, `maternal`, `range`, `hair`, `balanced` |
| `Category not found` | Invalid economics category | Options: `cost_templates`, `revenue_templates`, `feed_costs` |

---

## See Also

- [MCP Server Documentation](mcp-server.md) - Tools and transport configuration
- [MCP Prompts Documentation](mcp-prompts.md) - Guided workflows and skill prompts
- [Shepherd Agent Documentation](shepherd-agent.md) - AI-powered breeding advisor
- [NSIP Skills Documentation](nsip-skills.md) - Breeding analysis tools

---

*Last Updated: December 2025*
