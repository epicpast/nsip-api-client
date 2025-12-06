---
description: Get detailed animal information by LPN ID
argument-hint: "[LPN ID]"
allowed-tools: [mcp__nsip__nsip_get_animal]
---

# /lookup - Animal Details

## Outcome

Retrieve and display detailed information for a specific animal by LPN ID.

## Input

LPN ID from command argument or user prompt. Hooks validate format automatically.

## Data Source

`nsip_get_animal` - Returns full animal profile including breed, status, breeding values, and contact info.

## Output Focus

- Animal identity: LPN ID, breed, gender, birth date, status
- Top 3-5 traits by accuracy (≥50%)
- Breeding values with accuracy percentages
- Contact information if available

For comprehensive profiles including lineage and progeny, suggest /profile instead.
