---
description: Search for animals with optional filters
allowed-tools: [mcp__nsip__nsip_search_animals]
---

# /search - Search Animals

## Outcome

Search the NSIP database for animals matching specified criteria.

## Input

User provides search criteria. If none given, prompt for at least one filter:
- Breed ID (from /discover)
- Status filter
- Trait criteria
- Pagination (page, page_size)

## Data Source

`nsip_search_animals` - Returns paginated results with animal summaries.

## Output Focus

- Total matches and current page position
- For each result: LPN ID, breed, status, key traits
- Pagination guidance if more results available
- Suggest /lookup or /profile for full details on specific animals

The breed_context_injector hook automatically adds breed context to searches.
