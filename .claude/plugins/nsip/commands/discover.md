---
description: Discover available NSIP breeds, statuses, and database info
allowed-tools: [mcp__nsip__nsip_get_last_update, mcp__nsip__nsip_list_breeds, mcp__nsip__nsip_get_statuses]
---

# /discover - NSIP Database Overview

## Outcome

Display comprehensive NSIP database information: last update timestamp, all breed groups with their individual breeds, and available animal status values.

## Data Sources

These tools return independent data and should be called in parallel:

| Tool | Returns |
|------|---------|
| `nsip_get_last_update` | Database last update timestamp |
| `nsip_list_breeds` | Breed groups with nested breed lists (IDs needed for /traits) |
| `nsip_get_statuses` | Available animal status values (CURRENT, SOLD, etc.) |

## Output Focus

- Display database timestamp prominently
- List breed groups with their numeric IDs (users need these for /traits and /search)
- Show individual breeds under each group with their IDs
- List all available status values

Hooks handle API connectivity issues automatically.
