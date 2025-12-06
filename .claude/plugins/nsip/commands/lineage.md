---
description: Get animal pedigree tree (lineage/ancestry)
argument-hint: "[LPN ID]"
allowed-tools: [mcp__nsip__nsip_get_lineage]
---

# /lineage - Pedigree Tree

## Outcome

Display the ancestry/pedigree tree for an animal, showing parents and grandparents.

## Input

LPN ID from command argument or user prompt. Hooks validate format automatically.

## Data Source

`nsip_get_lineage` - Returns multi-generation pedigree data.

## Output Focus

- Subject animal identification
- Sire and dam with their LPN IDs and breeds
- Grandparents (paternal and maternal lines) if available
- Visual tree structure for clarity

The pedigree_visualizer hook automatically exports ASCII tree diagrams to file.

For ancestry plus offspring, use /profile instead.
