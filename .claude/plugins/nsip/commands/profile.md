---
description: Get complete animal profile (details, lineage, progeny)
argument-hint: "[LPN ID]"
allowed-tools: [mcp__nsip__nsip_search_by_lpn]
---

# /profile - Complete Animal Profile

## Outcome

Retrieve comprehensive profile combining animal details, pedigree, and offspring in a single query.

## Input

LPN ID from command argument or user prompt. Hooks validate format automatically.

## Data Source

`nsip_search_by_lpn` - Single tool that efficiently combines:
- Animal details (breed, traits, status)
- Lineage (sire, dam, grandparents)
- Progeny (offspring count and list)

## Output Focus

- Animal identity and status
- Pedigree summary: sire and dam LPN IDs
- Progeny count
- Top traits by accuracy
- Breeding value highlights

This is more efficient than calling /lookup, /lineage, and /progeny separately.
