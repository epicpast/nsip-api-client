# NSIP MCP Prompts Documentation

## Table of Contents

1. [Overview](#overview)
2. [Prompt Types](#prompt-types)
3. [Skill Prompts](#skill-prompts)
   - [EBV Analyzer](#ebv-analyzer)
   - [Flock Import](#flock-import)
   - [Inbreeding Calculator](#inbreeding-calculator)
   - [Mating Plan](#mating-plan)
   - [Progeny Report](#progeny-report)
   - [Trait Improvement](#trait-improvement)
   - [Ancestry Builder](#ancestry-builder)
   - [Flock Dashboard](#flock-dashboard)
   - [Selection Index](#selection-index)
   - [Breeding Recommendations](#breeding-recommendations)
4. [Shepherd Consultation Prompts](#shepherd-consultation-prompts)
5. [Guided Interview Prompts](#guided-interview-prompts)
6. [Integration Guide](#integration-guide)
7. [Best Practices](#best-practices)

---

## Overview

MCP Prompts provide pre-configured interaction patterns for the NSIP MCP Server. They enable LLM applications to execute complex breeding analysis workflows with consistent, structured outputs.

### Key Features

- **10 Skill Prompts**: Converted from slash commands for LLM-native access
- **Shepherd Consultation**: AI-powered breeding advice with domain expertise
- **Guided Interviews**: Multi-turn workflows for complex decisions
- **Consistent Formatting**: Markdown output suitable for LLM responses

### Architecture

```
MCP Client (LLM)
      │
      ▼
┌─────────────────────────────────────────────────────────┐
│                    MCP Prompts Layer                     │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Skill Prompts                                    │   │
│  │  - Single-shot analysis execution                 │   │
│  │  - Direct tool invocation                         │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Shepherd Prompts                                 │   │
│  │  - Domain-aware consultation                      │   │
│  │  - Regional adaptation                            │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Interview Prompts                                │   │
│  │  - Multi-turn guided workflows                    │   │
│  │  - Progressive input collection                   │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────────┐
│  NSIP Skills + Knowledge Base + Shepherd Agent          │
└─────────────────────────────────────────────────────────┘
```

---

## Prompt Types

### Single-Shot Prompts

Execute immediately with provided parameters. Best for:
- Simple analyses with known inputs
- Quick lookups and comparisons
- Generating reports from specific data

### Guided Interview Prompts

Collect inputs through multi-turn conversation. Best for:
- Complex decisions requiring multiple data points
- Users unfamiliar with required parameters
- Workflows where optimal inputs depend on earlier answers

### Shepherd Consultation Prompts

Domain-expert conversations. Best for:
- Open-ended breeding questions
- Regional and contextual advice
- Integrating multiple knowledge sources

---

## Skill Prompts

### EBV Analyzer

Compare Estimated Breeding Values across multiple animals.

**Prompt Name:** `ebv_analyzer`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `lpn_ids` | string | Yes | Comma-separated LPN IDs |
| `traits` | string | No | Comma-separated trait codes (default: BWT,WWT,PWWT,YFAT,YEMD,NLW) |

**Example Invocation:**
```json
{
  "jsonrpc": "2.0",
  "method": "prompts/get",
  "params": {
    "name": "ebv_analyzer",
    "arguments": {
      "lpn_ids": "6332-001,6332-002,6332-003",
      "traits": "WWT,PWWT,YEMD"
    }
  },
  "id": 1
}
```

**Output Format:**
```markdown
## EBV Comparison Report

### Animals Analyzed
- 6332-001: Ram Alpha (Katahdin)
- 6332-002: Ram Beta (Katahdin)
- 6332-003: Ram Gamma (Katahdin)

### Trait Comparison

| Animal | WWT | PWWT | YEMD |
|--------|-----|------|------|
| Ram Alpha | 5.2 | 7.8 | 1.5 |
| Ram Beta | 4.1 | 6.2 | 2.1 |
| Ram Gamma | 6.0 | 8.5 | 0.9 |

### Key Insights
- **Best for WWT**: Ram Gamma (6.0)
- **Best for PWWT**: Ram Gamma (8.5)
- **Best for YEMD**: Ram Beta (2.1)
```

---

### Flock Import

Import spreadsheet data and enrich with NSIP breeding values.

**Prompt Name:** `flock_import`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_path` | string | Yes | Path to CSV/Excel file |
| `flock_name` | string | No | Name for the flock |

**Expected File Format:**
```csv
lpn_id,local_tag,group
6332-001,Tag001,Rams
6332-002,Tag002,Rams
6332-101,Tag101,Ewes
```

**Output Format:**
```markdown
## Flock Import Report

### Import Summary
- **File**: my_flock.csv
- **Animals Found**: 50
- **Enriched**: 48 (96%)
- **Not Found**: 2

### Enrichment Results
| LPN ID | Local Tag | Status | Breed | EBVs Retrieved |
|--------|-----------|--------|-------|----------------|
| 6332-001 | Tag001 | Success | Katahdin | 12 traits |
| 6332-002 | Tag002 | Success | Katahdin | 12 traits |
...

### Animals Not Found
- 6332-999: No NSIP record
- 6332-998: No NSIP record
```

---

### Inbreeding Calculator

Calculate inbreeding coefficients using pedigree data.

**Prompt Name:** `inbreeding_calculator`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `lpn_id` | string | Conditional | Single animal for coefficient |
| `mating` | string | Conditional | Ram,Ewe pair for projected offspring |

**Use Cases:**

1. **Individual Coefficient:**
```json
{
  "arguments": {
    "lpn_id": "6332-001"
  }
}
```

2. **Projected Mating:**
```json
{
  "arguments": {
    "mating": "6332-001,6332-101"
  }
}
```

**Output Format:**
```markdown
## Inbreeding Analysis

### Animal: 6332-001
- **Inbreeding Coefficient (F)**: 3.125%
- **Risk Level**: Low

### Pedigree Analysis
- **Generations Analyzed**: 4
- **Common Ancestors Found**: 1
  - Great-grandsire appears on both sides

### Interpretation
An inbreeding coefficient of 3.125% is within acceptable ranges for most breeding programs. This level may provide some benefits through linebreeding while minimizing inbreeding depression risk.
```

---

### Mating Plan

Generate optimized mating recommendations.

**Prompt Name:** `mating_plan`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `rams` | string | Yes | Comma-separated ram LPN IDs |
| `ewes` | string | Yes | Comma-separated ewe LPN IDs |
| `goal` | string | No | Selection goal (terminal, maternal, balanced) |
| `max_inbreeding` | float | No | Maximum acceptable COI (default: 6.25%) |

**Output Format:**
```markdown
## Mating Plan Recommendations

### Configuration
- **Rams**: 3 available
- **Ewes**: 25 to mate
- **Goal**: Terminal sire production
- **Max Inbreeding**: 6.25%

### Recommended Pairings

#### Ram: 6332-001 (Ram Alpha)
Assigned 8 ewes:
| Ewe | Projected WWT | Projected YEMD | COI |
|-----|---------------|----------------|-----|
| 6332-101 | +4.5 | +1.2 | 2.1% |
| 6332-102 | +5.0 | +1.0 | 0.0% |
...

### Excluded Pairings
- 6332-001 x 6332-108: COI 9.4% exceeds maximum

### Expected Outcomes
- Average projected WWT: +4.2
- Average projected YEMD: +1.1
- Average COI: 1.8%
```

---

### Progeny Report

Evaluate sires by analyzing offspring performance.

**Prompt Name:** `progeny_report`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `sire_id` | string | Yes | Sire LPN ID |
| `traits` | string | No | Traits to analyze |

**Output Format:**
```markdown
## Progeny Report: Ram Alpha (6332-001)

### Summary Statistics
- **Total Progeny**: 45
- **Lambs with Records**: 42

### Offspring Performance

| Trait | N | Mean | Min | Max | Breed Avg | vs Avg |
|-------|---|------|-----|-----|-----------|--------|
| WWT | 42 | 4.8 | 2.1 | 7.2 | 2.5 | +92% |
| PWWT | 38 | 6.5 | 3.0 | 9.8 | 3.5 | +86% |
| YEMD | 35 | 1.3 | 0.5 | 2.1 | 0.8 | +63% |

### Consistency Score: 8.5/10
Progeny show consistent improvement across key traits.
```

---

### Trait Improvement

Plan multi-generation selection strategies.

**Prompt Name:** `trait_improvement`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `target_trait` | string | Yes | Trait code to improve |
| `current_mean` | float | Yes | Current flock average |
| `target_mean` | float | Yes | Goal value |
| `generations` | int | No | Planning horizon (default: 5) |

**Output Format:**
```markdown
## Trait Improvement Plan: WWT

### Current Status
- **Current Mean**: 2.5
- **Target Mean**: 5.0
- **Improvement Needed**: +2.5

### Selection Strategy

| Generation | Projected Mean | Selection Differential | Progress |
|------------|----------------|----------------------|----------|
| 1 | 3.0 | 2.0 | +0.5 |
| 2 | 3.5 | 2.0 | +0.5 |
| 3 | 4.0 | 2.0 | +0.5 |
| 4 | 4.5 | 2.0 | +0.5 |
| 5 | 5.0 | 2.0 | +0.5 |

### Recommendations
1. Select replacement rams from top 10% for WWT
2. Cull bottom 20% of ewes
3. Maintain selection pressure across generations
```

---

### Ancestry Builder

Generate pedigree tree reports.

**Prompt Name:** `ancestry_builder`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `lpn_id` | string | Yes | Animal LPN ID |
| `generations` | int | No | Depth (default: 3) |

---

### Flock Dashboard

Generate comprehensive flock statistics.

**Prompt Name:** `flock_dashboard`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_path` | string | Yes | Path to flock data file |
| `flock_name` | string | No | Display name |

---

### Selection Index

Calculate custom breeding index scores.

**Prompt Name:** `selection_index`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `lpn_ids` | string | Yes | Animals to score |
| `index_name` | string | No | Preset index (terminal, maternal, etc.) |
| `custom_weights` | string | No | Custom trait weights as JSON |

---

### Breeding Recommendations

AI-powered breeding recommendations using Shepherd agent.

**Prompt Name:** `breeding_recommendations`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `rams` | string | Yes | Available ram LPN IDs |
| `ewes` | string | Yes | Available ewe LPN IDs |
| `goal` | string | No | Production goal |
| `region` | string | No | NSIP region for context |

---

## Shepherd Consultation Prompts

The Shepherd agent provides expert-level consultation across four domains.

### General Consultation

**Prompt Name:** `shepherd_consult`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `question` | string | Yes | User's breeding question |
| `region` | string | No | NSIP region for context |
| `domain` | string | No | Force specific domain |

**Domains:**
- `breeding` - Genetic selection, EBV interpretation, mating decisions
- `health` - Disease prevention, nutrition, body condition
- `calendar` - Seasonal management, timing, schedules
- `economics` - Costs, ROI, market analysis

**Example:**
```json
{
  "arguments": {
    "question": "How should I select replacement ewes for better lambing rates?",
    "region": "midwest"
  }
}
```

**Response Format:**
```markdown
## Shepherd Consultation

### Your Question
How should I select replacement ewes for better lambing rates?

### Response
For improving lambing rates in the Midwest region, focus on these selection criteria:

**Primary Traits to Select For:**
1. **NLW (Number of Lambs Weaned)** - Most direct predictor of reproductive success
2. **NLB (Number of Lambs Born)** - Indicates prolificacy potential
3. **MWWT (Maternal Weaning Weight)** - Reflects maternal ability

**Selection Strategy:**
- Retain ewe lambs from dams with 2+ lambs weaned
- Select from litters that survived without intervention
- Consider udder quality and mothering behavior

### Recommendations
1. Keep records of lambing ease and lamb survival
2. Cull ewes that fail to raise their lambs
3. Select from families with consistent twin production

### Considerations
- Heritability of NLW is moderate (~0.10), progress will be gradual
- Environmental factors significantly impact lambing success
- Regional climate affects optimal lambing time

### Sources
- NSIP trait interpretations
- Midwest extension guidelines
```

---

## Guided Interview Prompts

Complex workflows that collect inputs progressively.

### Guided Mating Plan

**Prompt Name:** `guided_mating_plan`

**Flow:**
1. Ask about available rams
2. Ask about ewe group
3. Ask about production goal
4. Ask about inbreeding tolerance
5. Generate recommendations

**Example Interaction:**
```
Assistant: Let's create a mating plan for your flock.
           First, please provide the LPN IDs for your available rams.

User: 6332-001, 6332-002

Assistant: Great\! Now please list the LPN IDs for your ewes,
           or provide a file path containing them.

User: Here is my file: /data/ewes.csv

Assistant: I see 25 ewes in the file. What is your primary breeding goal?
           - Terminal (maximize growth/carcass)
           - Maternal (reproduction/mothering)
           - Balanced (both traits)

User: Terminal

Assistant: What is the maximum inbreeding coefficient you will accept?
           (Typical range: 3.125% to 6.25%)

User: 5%

Assistant: [Executes mating_optimizer with collected parameters]
           Here are your optimized mating recommendations...
```

---

### Guided Trait Improvement

**Prompt Name:** `guided_trait_improvement`

**Flow:**
1. Ask about target trait
2. Ask about current flock performance
3. Ask about improvement goals
4. Ask about selection intensity
5. Generate multi-generation plan

---

## Integration Guide

### Invoking Prompts from MCP Clients

```python
import asyncio
from mcp import ClientSession

async def use_prompt():
    async with ClientSession(transport) as session:
        # List available prompts
        prompts = await session.list_prompts()
        
        # Get a specific prompt
        result = await session.get_prompt(
            "ebv_analyzer",
            arguments={
                "lpn_ids": "6332-001,6332-002",
                "traits": "WWT,PWWT"
            }
        )
        
        # Use the prompt messages
        for message in result.messages:
            print(message.content)
```

### Chaining Prompts

Prompts can be chained for complex workflows:

```python
# 1. Import flock data
import_result = await session.get_prompt("flock_import", {...})

# 2. Analyze flock statistics
dashboard = await session.get_prompt("flock_dashboard", {...})

# 3. Get breeding recommendations
recs = await session.get_prompt("breeding_recommendations", {...})
```

---

## Best Practices

### 1. Input Validation

- Validate LPN ID format before invoking prompts
- Check file paths exist for import prompts
- Verify numeric parameters are within expected ranges

### 2. Error Handling

```python
try:
    result = await session.get_prompt("ebv_analyzer", {...})
except McpError as e:
    if e.code == -32602:
        print("Invalid parameters:", e.message)
    elif e.code == -32603:
        print("Internal error:", e.message)
```

### 3. Performance Considerations

- Use `summarize=True` for large result sets
- Batch animal lookups when possible
- Cache frequently accessed prompts

### 4. Regional Context

- Always provide region when available for better recommendations
- Regional data affects disease guides, nutrition, and calendar suggestions

### 5. Prompt Selection

| Use Case | Recommended Prompt |
|----------|--------------------|
| Quick EBV lookup | `ebv_analyzer` |
| Complex mating decisions | `guided_mating_plan` |
| Open-ended questions | `shepherd_consult` |
| Import new data | `flock_import` |
| Sire evaluation | `progeny_report` |

---

## See Also

- [MCP Server Documentation](mcp-server.md) - Tools and transport configuration
- [MCP Resources Documentation](mcp-resources.md) - Static knowledge access
- [Shepherd Agent Documentation](shepherd-agent.md) - AI-powered breeding advisor
- [NSIP Skills Documentation](nsip-skills.md) - Breeding analysis tools

---

*Last Updated: December 2025*
