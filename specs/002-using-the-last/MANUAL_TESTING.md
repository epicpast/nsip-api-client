# Manual Testing Guide - Claude Code Plugin

**Feature**: Claude Code Plugin Distribution (002-using-the-last)
**Status**: Automated tests complete (59/59 passed) - Manual testing required
**Tasks**: T023 (Installation), T024 (Error Scenarios)

---

## Prerequisites

- Claude Code CLI or VS Code extension installed
- Python 3.10+ available
- nsip-api-client package installed in virtual environment
- NSIP API credentials (base URL and API key)

---

## T023: Manual Plugin Installation Test

**Goal**: Verify end-to-end plugin installation and usage in real Claude Code environment

### Test Environment Setup

```bash
# Verify prerequisites
python --version  # Should be 3.10+
which python      # Should point to venv if using one

# Verify package installed
pip list | grep nsip

# Set credentials (optional - test both with/without)
export NSIP_BASE_URL="https://api.nsip.org.au"  # Replace with actual URL
export NSIP_API_KEY="your-api-key-here"         # Replace with actual key
```

### Test Steps

#### Step 1: Add Marketplace
```bash
/plugin marketplace add epicpast/nsip-api-client
```

**Expected Result**:
- ✓ Marketplace added successfully
- ✓ Confirmation message displayed
- ⏱️ Time recorded: _______ seconds

**Actual Result**:
- [ ] PASS
- [ ] FAIL - Notes: _______________________

---

#### Step 2: Install Plugin
```bash
/plugin install nsip-api-client
```

**Expected Result** (with credentials):
- ✓ Plugin installs successfully
- ✓ MCP server starts automatically (silent - no output per FR-016)
- ✓ No errors displayed
- ⏱️ Time recorded: _______ seconds

**Expected Result** (without credentials):
- ✓ Plugin installs successfully
- ✓ MCP server starts (credentials not needed for startup per FR-004)
- ✓ No errors displayed

**Actual Result**:
- [ ] PASS
- [ ] FAIL - Notes: _______________________

---

#### Step 3: Verify MCP Tools Available
```bash
# In Claude Code, ask:
"List all available MCP tools"
```

**Expected Result**:
- ✓ 10 NSIP tools listed:
  - [ ] nsip_get_last_update
  - [ ] nsip_list_breeds
  - [ ] nsip_get_statuses
  - [ ] nsip_get_trait_ranges
  - [ ] nsip_search_animals
  - [ ] nsip_get_animal
  - [ ] nsip_get_lineage
  - [ ] nsip_get_progeny
  - [ ] nsip_search_by_lpn
  - [ ] get_server_health

**Actual Result**:
- [ ] PASS - All 10 tools available
- [ ] FAIL - Missing tools: _______________________

---

#### Step 4: Test Slash Commands

**Test 4a: /nsip/discover**
```bash
/nsip/discover
```

**Expected Result**:
- ✓ Database update date displayed
- ✓ All breed groups listed with IDs
- ✓ Available statuses shown
- ✓ Formatted output (not raw JSON)
- ⏱️ Execution time: _______ seconds (should be <30s per SC-004)

**Actual Result**:
- [ ] PASS
- [ ] FAIL - Notes: _______________________

---

**Test 4b: /nsip/lookup**
```bash
/nsip/lookup [LPN-ID]  # Replace with actual LPN ID
```

**Expected Result**:
- ✓ Animal details displayed (breed, status)
- ✓ Top 3 traits shown with accuracy
- ✓ Breeding values summary
- ✓ Formatted output
- ⏱️ Execution time: _______ seconds

**Actual Result**:
- [ ] PASS
- [ ] FAIL - Notes: _______________________

---

**Test 4c: /nsip/profile**
```bash
/nsip/profile [LPN-ID]
```

**Expected Result**:
- ✓ Comprehensive profile displayed
- ✓ Animal details + lineage + progeny
- ✓ Sire and Dam LPN IDs shown
- ✓ Progeny count displayed
- ⏱️ Execution time: _______ seconds

**Actual Result**:
- [ ] PASS
- [ ] FAIL - Notes: _______________________

---

**Test 4d: /nsip/health**
```bash
/nsip/health
```

**Expected Result**:
- ✓ Server performance metrics displayed
- ✓ MCP server startup time shown
- ✓ API response times shown
- ✓ Cache metrics displayed
- ✓ Request success rates shown

**Actual Result**:
- [ ] PASS
- [ ] FAIL - Notes: _______________________

---

#### Step 5: Verify Success Criteria

**SC-001**: Installation to first tool call in <2 minutes
- Total time from `/plugin install` to first successful tool call: _______ seconds
- [ ] PASS (<120 seconds)
- [ ] FAIL

**SC-003**: All 10 tools available immediately
- [ ] PASS (all 10 tools available after installation)
- [ ] FAIL

**SC-004**: Slash commands complete in <30 seconds
- All slash commands tested completed in: _______ seconds (average)
- [ ] PASS (<30 seconds average)
- [ ] FAIL

---

#### Step 6: Test on Both Platforms

**Terminal Test** (Claude Code CLI):
- [ ] Installation successful
- [ ] All 10 tools available
- [ ] Slash commands work
- Notes: _______________________

**VS Code Test** (Claude Code Extension):
- [ ] Installation successful
- [ ] All 10 tools available
- [ ] Slash commands work
- Notes: _______________________

**SC-005 Verification**: 100% feature parity
- [ ] PASS (identical functionality on both platforms)
- [ ] FAIL - Differences: _______________________

---

## T024: Error Scenario Testing

**Goal**: Verify error handling across all edge cases

### Test 1: Missing Credentials (Runtime Error)

**Setup**:
```bash
# Unset credentials
unset NSIP_BASE_URL
unset NSIP_API_KEY

# Install/enable plugin
/plugin install nsip-api-client
```

**Test**: Call any NSIP tool
```bash
/nsip/discover
```

**Expected Result** (per FR-017, clarification Q2):
- ✓ MCP server is running (started without credentials)
- ✓ Tool call fails with generic message: "Authentication failed"
- ✗ NO credential names exposed (not "NSIP_BASE_URL missing")
- ✗ NO credential values exposed
- ✓ Suggestion to check environment variables (generic)

**Actual Result**:
- [ ] PASS - Generic error, no credential exposure
- [ ] FAIL - Details: _______________________

---

### Test 2: Invalid Credentials

**Setup**:
```bash
export NSIP_BASE_URL="https://invalid.example.com"
export NSIP_API_KEY="invalid-key-12345"

# Restart plugin
/plugin disable nsip-api-client
/plugin enable nsip-api-client
```

**Test**: Call any NSIP tool
```bash
/nsip/test-api
```

**Expected Result**:
- ✓ MCP server is running
- ✓ Generic "Authentication failed" message only
- ✗ NO indication of which credential is wrong
- ✗ NO credential values in error

**Actual Result**:
- [ ] PASS
- [ ] FAIL - Details: _______________________

---

### Test 3: Python Not Available (Startup Error)

**Setup**:
```bash
# Temporarily rename Python executable (restore after test!)
# OR test in environment without Python 3.10+
```

**Test**: Enable plugin
```bash
/plugin enable nsip-api-client
```

**Expected Result** (per FR-004, clarification Q3):
- ✗ Plugin enable FAILS with diagnostic error
- ✓ Error indicates Python requirement
- ✓ Plugin remains disabled
- ✓ User can fix and retry

**Actual Result**:
- [ ] PASS
- [ ] FAIL - Details: _______________________
- **CAUTION**: Restore Python after test!

---

### Test 4: Invalid LPN ID

**Test**: Lookup non-existent animal
```bash
/nsip/lookup INVALID-ID-999999
```

**Expected Result**:
- ✓ Helpful error message: "Animal not found. Verify LPN ID and try again."
- ✗ NO credential exposure
- ✓ Clear guidance to user

**Actual Result**:
- [ ] PASS
- [ ] FAIL - Details: _______________________

---

### Test 5: Plugin Disable/Re-enable (Clean Shutdown)

**Test**:
```bash
# Check plugin status
/plugin list

# Disable plugin
/plugin disable nsip-api-client

# Verify MCP server stopped
# (Tools should no longer be available)

# Re-enable plugin
/plugin enable nsip-api-client

# Verify tools available again
"List available MCP tools"
```

**Expected Result** (per FR-014, FR-005, SC-007):
- ✓ Disable: MCP server stops cleanly, no orphaned processes
- ✓ Disable: Silent success (no output per FR-016)
- ✓ Re-enable: MCP server starts successfully
- ✓ Re-enable: Configuration preserved (no re-setup needed)
- ✓ Re-enable: All 10 tools available again
- ✗ NO errors on either operation

**Actual Result**:
- [ ] PASS
- [ ] FAIL - Details: _______________________

---

### Test 6: Manual .mcp.json Coexistence (Edge Case)

**Setup**:
```bash
# Create manual .mcp.json in Claude Code config directory
# With different MCP server name or configuration
```

**Test**: Enable plugin
```bash
/plugin enable nsip-api-client
```

**Expected Result** (edge case from spec.md:L98):
- ✓ Plugin-scoped config takes precedence
- ✓ Plugin MCP server starts with plugin configuration
- ✓ No conflicts with manual .mcp.json
- ✓ Documented behavior in README

**Actual Result**:
- [ ] PASS
- [ ] FAIL - Details: _______________________

---

## Overall Test Results

### Summary

| Test Category | Total | Pass | Fail | Notes |
|---------------|-------|------|------|-------|
| T023: Installation | 6 | ___ | ___ | _____ |
| T023: Slash Commands | 4 | ___ | ___ | _____ |
| T023: Success Criteria | 4 | ___ | ___ | _____ |
| T023: Cross-Platform | 2 | ___ | ___ | _____ |
| T024: Error Scenarios | 6 | ___ | ___ | _____ |
| **TOTAL** | **22** | **___** | **___** | **___** |

### Pass/Fail Criteria

- **PASS**: All 22 tests pass
- **PARTIAL**: 18-21 tests pass (investigate failures)
- **FAIL**: <18 tests pass (critical issues, do not release)

---

## Completion Checklist

- [ ] All automated tests passing (59/59) ✅ **DONE**
- [ ] T023 completed and documented (installation tests)
- [ ] T024 completed and documented (error scenarios)
- [ ] Success criteria validated (SC-001, SC-003, SC-004, SC-005, SC-007)
- [ ] Cross-platform testing complete (terminal + VS Code)
- [ ] Edge cases tested and documented
- [ ] Issues logged (if any)
- [ ] Ready for release

---

## Notes and Issues

**Date**: _____________
**Tester**: _____________
**Environment**: _____________

**Issues Found**:
1. _______________________________
2. _______________________________
3. _______________________________

**Recommendations**:
1. _______________________________
2. _______________________________

---

## Sign-off

**Manual Testing Status**:
- [ ] COMPLETE - All tests passed
- [ ] COMPLETE - Issues documented, recommend release
- [ ] INCOMPLETE - Critical issues, DO NOT release

**Tester Signature**: _____________
**Date**: _____________
