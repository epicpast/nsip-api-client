---
description: Get trait value ranges for a specific breed
argument-hint: "[breed ID]"
allowed-tools: [mcp__nsip__nsip_get_trait_ranges]
---

# /traits - Breed Trait Ranges

## Outcome

Display the min/max value ranges for all traits in a specific breed, useful for understanding what values are typical or exceptional.

## Input

Numeric breed ID from command argument or user prompt. Use /discover to find breed IDs.

## Data Source

`nsip_get_trait_ranges` - Returns trait ranges for the specified breed.

## Output Focus

- Breed name and ID
- For each trait: name, min value, max value, unit
- Brief context on how to interpret ranges for breeding selection

The trait_dictionary hook provides additional trait definitions automatically.
