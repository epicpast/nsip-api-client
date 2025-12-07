# NSIP Shepherd Agent Documentation

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Persona Design](#persona-design)
4. [Domains](#domains)
   - [Breeding Domain](#breeding-domain)
   - [Health Domain](#health-domain)
   - [Calendar Domain](#calendar-domain)
   - [Economics Domain](#economics-domain)
5. [Region Detection](#region-detection)
6. [Usage Examples](#usage-examples)
7. [Integration Guide](#integration-guide)
8. [Response Formatting](#response-formatting)
9. [Best Practices](#best-practices)

---

## Overview

The NSIP Shepherd Agent is an AI-powered breeding advisor that provides expert guidance across four domains: breeding/genetics, health/nutrition, seasonal management, and operation economics. It uses a neutral expert persona (veterinarian-like) and adapts advice to the user's regional context.

### Key Features

- **Multi-Domain Expertise**: Breeding, health, calendar, and economics guidance
- **Regional Adaptation**: Automatic region detection and context-aware advice
- **Evidence-Based**: References NSIP data, heritabilities, and research
- **Neutral Expert Persona**: Professional, actionable, uncertainty-aware
- **Question Classification**: Automatic routing to appropriate domain

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   ShepherdAgent                          │
│  ┌─────────────────────────────────────────────────┐    │
│  │  Persona                                         │    │
│  │  - Neutral expert tone                           │    │
│  │  - Uncertainty phrases                           │    │
│  │  - Response formatting                           │    │
│  └─────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────┐    │
│  │  Region Detection                                │    │
│  │  - State code mapping                            │    │
│  │  - ZIP code inference                            │    │
│  │  - Regional context                              │    │
│  └─────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────┐    │
│  │  Domain Handlers                                 │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────┐│    │
│  │  │ Breeding │ │ Health   │ │ Calendar │ │ Econ ││    │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────┘│    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              Knowledge Base (YAML)                       │
│  heritabilities, diseases, nutrition, regions, etc.      │
└─────────────────────────────────────────────────────────┘
```

---

## Persona Design

The Shepherd uses a neutral expert persona designed to be professional and evidence-based, similar to a veterinarian's communication style.

### Communication Guidelines

```python
from nsip_mcp.shepherd import ShepherdPersona

persona = ShepherdPersona()
print(persona.get_system_prompt())
```

**Core Principles:**

1. **Professional Tone**: Clear, direct language without unnecessary jargon
2. **Evidence-Based**: Cite data sources when making recommendations
3. **Acknowledge Uncertainty**: Use appropriate qualifiers when data is limited
4. **Actionable Advice**: Always provide concrete next steps
5. **Regional Respect**: Adapt advice to user's geographic context
6. **Safety First**: Recommend veterinary consultation for serious health concerns

### Response Structure

Every Shepherd response follows this structure:

1. **Direct Answer** - Address the question first
2. **Context** - Relevant background or data
3. **Recommendations** - Specific, actionable suggestions
4. **Considerations** - Caveats, regional variations, when to seek help
5. **Sources** - Data sources cited

### Uncertainty Handling

```python
from nsip_mcp.shepherd.persona import ShepherdPersona

persona = ShepherdPersona()

# High confidence (0.9+) - no qualifier
statement = persona.format_uncertainty(
    "Select for NLW to improve lambing rates.",
    confidence=0.9
)
# Output: "Select for NLW to improve lambing rates."

# Moderate confidence (0.5-0.7)
statement = persona.format_uncertainty(
    "This approach should work for most operations.",
    confidence=0.6
)
# Output: "Research suggests this approach should work for most operations."
```

---

## Domains

### Breeding Domain

The breeding domain handles genetic selection, EBV interpretation, mating recommendations, and inbreeding management.

**Module:** `nsip_mcp.shepherd.domains.breeding`

#### Capabilities

| Method | Description |
|--------|-------------|
| `interpret_ebv()` | Explain EBV values in context |
| `recommend_selection_strategy()` | Selection approach for goals |
| `assess_inbreeding_risk()` | Evaluate inbreeding coefficient |
| `estimate_genetic_progress()` | Project multi-generation improvement |

#### Example: EBV Interpretation

```python
from nsip_mcp.shepherd.domains.breeding import BreedingDomain

breeding = BreedingDomain()

result = breeding.interpret_ebv(
    trait="WWT",
    value=5.0,
    accuracy=0.7,
    breed_average=2.5
)

print(result)
# {
#   "trait": "WWT",
#   "value": 5.0,
#   "accuracy": 0.7,
#   "interpretation": "Above average - strong genetic potential for weaning weight",
#   "percentile": "Top 15%",
#   "recommendations": ["Use as sire for growth-focused matings", ...]
# }
```

#### Example: Inbreeding Assessment

```python
result = breeding.assess_inbreeding_risk(coefficient=0.0625)
# {
#   "coefficient": 0.0625,
#   "risk_level": "Moderate",
#   "interpretation": "Equivalent to half-sibling mating",
#   "recommendations": [
#     "Consider introducing unrelated genetics",
#     "Avoid this mating if alternatives exist"
#   ]
# }
```

---

### Health Domain

The health domain provides guidance on disease prevention, parasite management, nutrition, and vaccination schedules.

**Module:** `nsip_mcp.shepherd.domains.health`

#### Capabilities

| Method | Description |
|--------|-------------|
| `get_disease_prevention()` | Regional disease guide |
| `get_nutrition_recommendations()` | Life stage nutrition |
| `assess_parasite_risk()` | Parasite risk assessment |
| `get_vaccination_schedule()` | Vaccination program |

#### Example: Parasite Risk Assessment

```python
from nsip_mcp.shepherd.domains.health import HealthDomain

health = HealthDomain()

result = health.assess_parasite_risk(
    region="southeast",
    season="summer",
    stocking_rate="high"
)

print(result)
# {
#   "region": "Southeast",
#   "risk_level": "Very High",
#   "primary_parasites": ["Haemonchus contortus", ...],
#   "monitoring": ["FAMACHA scoring weekly", ...],
#   "control_strategies": [
#     "Increase FAMACHA checking frequency",
#     "Rotate pastures with 60+ day rest",
#     ...
#   ]
# }
```

#### Example: Nutrition Recommendations

```python
result = health.get_nutrition_recommendations(
    life_stage="lactation",
    region="midwest",
    body_condition=2.5
)
# Returns requirements for twins, singles, with BCS adjustments
```

---

### Calendar Domain

The calendar domain handles seasonal planning, breeding timing, and task scheduling.

**Module:** `nsip_mcp.shepherd.domains.calendar`

#### Capabilities

| Method | Description |
|--------|-------------|
| `get_seasonal_tasks()` | Tasks by season and type |
| `calculate_breeding_dates()` | Breeding calendar from lambing target |
| `get_marketing_windows()` | Regional market timing |
| `create_annual_calendar()` | Full year calendar |

#### Example: Breeding Date Calculation

```python
from nsip_mcp.shepherd.domains.calendar import CalendarDomain

calendar = CalendarDomain()

result = calendar.calculate_breeding_dates(
    target_lambing="march"
)

print(result)
# {
#   "target_lambing": "March",
#   "breeding_start": "October 1",
#   "breeding_end": "October 21",
#   "ram_preparation": "September 1",
#   "gestation_days": 147,
#   "preparation_tasks": [
#     "Ram fertility check",
#     "Ewe flushing nutrition",
#     ...
#   ]
# }
```

---

### Economics Domain

The economics domain provides cost analysis, profitability assessment, and ROI calculations.

**Module:** `nsip_mcp.shepherd.domains.economics`

#### Capabilities

| Method | Description |
|--------|-------------|
| `get_cost_breakdown()` | Itemized production costs |
| `calculate_breakeven()` | Breakeven price analysis |
| `calculate_ram_roi()` | Ram purchase ROI |
| `analyze_flock_profitability()` | Full profitability analysis |
| `compare_marketing_options()` | Marketing channel comparison |

#### Example: Breakeven Analysis

```python
from nsip_mcp.shepherd.domains.economics import EconomicsDomain

economics = EconomicsDomain()

result = economics.calculate_breakeven(
    annual_costs_per_ewe=150,
    lambs_per_ewe=1.5,
    lamb_weight=110,
    cost_per_lamb=50
)

print(result)
# {
#   "breakeven_analysis": {
#     "per_lamb": 116.67,
#     "per_pound": 1.06,
#     "per_cwt": 106.06
#   },
#   "interpretation": "Competitive breakeven - well positioned for most markets"
# }
```

#### Example: Ram ROI

```python
result = economics.calculate_ram_roi(
    ram_cost=2000,
    years_used=4,
    ewes_per_year=35,
    lamb_value_increase=20
)
# Returns total return, net benefit, ROI percentage, payback period
```

---

## Region Detection

The Shepherd automatically detects and adapts to NSIP member regions.

### Supported Regions

| Region | States | Climate |
|--------|--------|---------|
| `northeast` | ME, NH, VT, MA, RI, CT, NY, NJ, PA | Humid continental |
| `southeast` | MD, DE, VA, WV, NC, SC, GA, FL, AL, MS, TN, KY | Humid subtropical |
| `midwest` | OH, IN, IL, MI, WI, MN, IA, MO, ND, SD, NE, KS | Continental |
| `southwest` | TX, OK, AR, LA, AZ, NM | Semi-arid to arid |
| `mountain` | MT, WY, CO, UT, ID, NV | Semi-arid continental |
| `pacific` | WA, OR, CA, AK, HI | Varied (mediterranean to temperate) |

### Detection Methods

```python
from nsip_mcp.shepherd import detect_region

# From state code
region = detect_region(state="OH")  # Returns "midwest"

# From ZIP code
region = detect_region(zip_code="43201")  # Returns "midwest"
```

### Regional Context

```python
from nsip_mcp.shepherd import get_region_context

context = get_region_context("midwest")
print(context)
# {
#   "id": "midwest",
#   "name": "Midwest",
#   "states": ["OH", "IN", "IL", ...],
#   "climate": "Continental with cold winters and hot summers",
#   "typical_lambing": "February-April",
#   "parasite_season": "April-November",
#   "challenges": ["Cold stress in winter lambing", ...],
#   "primary_breeds": ["Katahdin", "Dorper", "Suffolk", ...]
# }
```

---

## Usage Examples

### Basic Consultation

```python
from nsip_mcp.shepherd import ShepherdAgent

agent = ShepherdAgent(region="midwest", production_goal="terminal")

# Ask a question - domain auto-detected
result = agent.consult("How do I improve weaning weights?")

print(result["domain"])        # "breeding"
print(result["answer"])        # Detailed answer
print(result["recommendations"])  # Actionable steps
```

### Domain-Specific Query

```python
from nsip_mcp.shepherd.agent import Domain

# Force specific domain
result = agent.consult(
    "What are my options?",
    domain=Domain.ECONOMICS
)
```

### With Context

```python
result = agent.consult(
    "How should I feed my ewes?",
    context={
        "life_stage": "late_gestation",
        "body_condition": 2.5,
        "flock_size": 50
    }
)
```

### Quick Reference

```python
# Get quick reference on a topic
quick = agent.get_quick_answer("ebv")
print(quick["summary"])
# "Estimated Breeding Values predict genetic merit for traits"
print(quick["key_points"])
# ["Positive = above breed average", ...]
```

---

## Integration Guide

### MCP Integration

The Shepherd integrates with MCP prompts for LLM access:

```python
# In prompts/shepherd_prompts.py
from nsip_mcp.shepherd import ShepherdAgent

@mcp.prompt(name="shepherd_consult")
async def shepherd_consult_prompt(
    question: str,
    region: str = None,
    domain: str = None
) -> str:
    agent = ShepherdAgent(region=region)
    result = agent.consult(question, domain=domain)
    return format_shepherd_response(result)
```

### Direct Python Usage

```python
from nsip_mcp.shepherd import ShepherdAgent, ShepherdPersona

# Custom persona settings
persona = ShepherdPersona(
    cite_sources=True,
    acknowledge_uncertainty=True
)

agent = ShepherdAgent(
    persona=persona,
    region="pacific",
    production_goal="maternal"
)

# Use throughout application
result = agent.consult("When should I start breeding season?")
```

---

## Response Formatting

The Shepherd provides a helper function for consistent response formatting:

```python
from nsip_mcp.shepherd.persona import format_shepherd_response

response = format_shepherd_response(
    answer="Select for NLW to improve lambing rates.",
    context="NLW (Number of Lambs Weaned) has ~0.10 heritability.",
    recommendations=[
        "Keep records of lambing ease and survival",
        "Retain ewe lambs from dams with 2+ lambs weaned",
        "Consider udder quality and mothering behavior"
    ],
    considerations=[
        "Progress will be gradual due to moderate heritability",
        "Environmental factors also impact lambing success"
    ],
    sources=["NSIP trait interpretations", "Extension guidelines"]
)

print(response)
```

**Output:**
```markdown
Select for NLW to improve lambing rates.

### Context

NLW (Number of Lambs Weaned) has ~0.10 heritability.

### Recommendations

- Keep records of lambing ease and survival
- Retain ewe lambs from dams with 2+ lambs weaned
- Consider udder quality and mothering behavior

### Considerations

- Progress will be gradual due to moderate heritability
- Environmental factors also impact lambing success

---
*Sources:*
- NSIP trait interpretations
- Extension guidelines
```

---

## Best Practices

### 1. Always Set Region

Regional context significantly improves advice quality:

```python
# Good - region-aware advice
agent = ShepherdAgent(region="southeast")

# Also good - detect from state
agent.set_region(state="GA")
```

### 2. Provide Context When Available

Additional context leads to more specific recommendations:

```python
result = agent.consult(
    "How should I manage parasites?",
    context={
        "season": "summer",
        "stocking_rate": "high",
        "pasture_type": "permanent"
    }
)
```

### 3. Use Domain Classification

Let the agent classify questions automatically, or specify when you need a specific perspective:

```python
# Auto-classify (usually best)
result = agent.consult("What vaccines do I need?")

# Force economics perspective on a health question
result = agent.consult(
    "Is it worth vaccinating for CL?",
    domain=Domain.ECONOMICS
)
```

### 4. Handle Uncertainty

Check for uncertainty indicators in responses:

```python
result = agent.consult("...")

if "uncertainty" in result:
    print("Note:", result["uncertainty"])

if result.get("needs_veterinary_consultation"):
    print("Recommend consulting a veterinarian")
```

### 5. Cite Sources

The Shepherd automatically includes sources when available:

```python
result = agent.consult("What heritability can I expect for WWT?")
print(result.get("sources", []))
# ["NSIP heritability estimates", "Breed evaluation data"]
```

---

## See Also

- [MCP Server Documentation](mcp-server.md) - Tools and transport configuration
- [MCP Resources Documentation](mcp-resources.md) - Static knowledge access
- [MCP Prompts Documentation](mcp-prompts.md) - Prompt patterns and interviews
- [NSIP Skills Documentation](nsip-skills.md) - Breeding analysis tools

---

*Last Updated: December 2025*
