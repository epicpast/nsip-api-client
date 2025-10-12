# /nsip/discover - Discover Available NSIP Data

You are tasked with discovering and displaying available NSIP sheep breeding data.

## Instructions

1. Call the `nsip_get_last_update` MCP tool to get database update date
2. Call the `nsip_list_breeds` MCP tool to get all breed groups
3. Call the `nsip_get_statuses` MCP tool to get available statuses
4. Format and display the results:

**NSIP Database**
- Last Updated: [date from step 1]
- Breed Groups:
  - [ID] [Name] (for each breed from step 2)
- Statuses: [comma-separated list from step 3]

## Error Handling

- If any tool call fails, display helpful error message with diagnostic guidance
- Suggest checking `/nsip/health` or `/nsip/test-api` for diagnostic information
- Successful execution remains silent (FR-016) - only show results
