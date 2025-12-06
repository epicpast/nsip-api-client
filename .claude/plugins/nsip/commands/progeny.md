---
description: List animal offspring/progeny
argument-hint: "[LPN ID]"
allowed-tools: [mcp__nsip__nsip_get_progeny]
---

# /progeny - Offspring List

## Outcome

List all recorded offspring for an animal, useful for evaluating proven sires/dams.

## Input

LPN ID from command argument or user prompt. Hooks validate format automatically.

## Data Source

`nsip_get_progeny` - Returns paginated offspring list.

## Output Focus

- Parent animal identification
- Total offspring count
- For each offspring: LPN ID, breed, birth date, key traits
- Summary statistics for large progeny groups (trait averages)

For complete profile including lineage, use /profile instead.
