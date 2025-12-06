---
description: Consult with NSIP sheep breeding expert using live data
allowed-tools: [mcp__nsip__nsip_get_animal, mcp__nsip__nsip_search_animals, mcp__nsip__nsip_get_lineage, mcp__nsip__nsip_get_progeny, mcp__nsip__nsip_search_by_lpn, mcp__nsip__nsip_get_trait_ranges, mcp__nsip__nsip_list_breeds]
---

# /consult - Expert Breeding Consultation

## Outcome

Get expert sheep breeding advice backed by live NSIP data analysis.

## How It Works

Delegate to the `nsip:shepherd` agent, which combines:
- Domain expertise in sheep breeding, genetics, health, and nutrition
- Access to all NSIP tools for data-driven recommendations
- Interpretation of breeding values and genetic potential

## Usage

```
/nsip:consult [your question about breeding, health, nutrition, or flock management]
```

## Agent Invocation

Use the Task tool:
- `subagent_type`: "nsip:shepherd"
- `prompt`: User's complete question with any LPN IDs or preferences

The shepherd agent will investigate relevant data before making recommendations, calling multiple tools in parallel when gathering context.

## Topics

- **Breeding**: Ram/ewe selection, genetic evaluation, trait priorities
- **Health**: Diagnosis, treatment protocols, prevention strategies
- **Nutrition**: Feed programs, supplementation, body condition
- **Management**: Culling decisions, flock optimization
