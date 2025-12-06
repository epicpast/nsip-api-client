---
description: Validate NSIP API connectivity and configuration
allowed-tools: [mcp__nsip__nsip_get_last_update]
---

# /test-api - API Connectivity Test

## Outcome

Verify NSIP API connectivity and display connection status.

## Data Source

`nsip_get_last_update` - Simple API call to verify connectivity.

## Output

**On success:**
- Confirmation: "NSIP API connectivity verified"
- Database last update timestamp
- API endpoint in use

**On failure:**
- Error indication with possible causes
- Network troubleshooting suggestions
- Default API URL: `http://nsipsearch.nsip.org/api`

Note: The NSIP API is public and requires no authentication.
