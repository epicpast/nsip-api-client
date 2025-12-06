---
description: Generate optimized mating recommendations for your flock
allowed-tools: Bash(uv run:*)
---

# /nsip:mating-plan

Generate optimized mating recommendations for your flock.

## Usage

```
/nsip:mating-plan <rams_file> <ewes_file> [--goal <breeding_goal>] [--max-inbreeding <pct>]
```

## Arguments

- `rams_file`: Spreadsheet or comma-separated list of ram LPN IDs
- `ewes_file`: Spreadsheet or comma-separated list of ewe LPN IDs
- `--goal`: Breeding goal (terminal, maternal, balanced). Default: balanced
- `--max-inbreeding`: Maximum acceptable inbreeding percentage. Default: 6.25
- `--max-uses`: Maximum times each ram can be assigned. Default: unlimited

## Process

1. Fetch EBVs and pedigree data for all candidates
2. For each potential ram-ewe pairing:
   - Project offspring EBVs using midparent method
   - Calculate projected inbreeding coefficient
   - Score against breeding goal index
3. Optimize assignments to maximize flock improvement
4. Flag any high-risk matings
5. Generate mating list with projections

## Breeding Goals

| Goal | Focus Traits | Use Case |
|------|--------------|----------|
| Terminal | PWWT, YFAT, YEMD | Market lambs |
| Maternal | NLW, MWWT, WWT | Replacement ewes |
| Balanced | All traits weighted | General purpose |

## Example

```bash
# Basic mating plan
uv run python -m nsip_skills.mating_optimizer rams.csv ewes.csv

# Terminal focus with inbreeding limit
uv run python -m nsip_skills.mating_optimizer rams.csv ewes.csv --goal terminal --max-inbreeding 5.0

# Limit ram usage
uv run python -m nsip_skills.mating_optimizer rams.csv ewes.csv --max-uses 25
```

## Output

- **Mating List**: Ewe → Ram assignments with scores
- **Projected Offspring**: Expected EBVs for each pairing
- **Inbreeding Alerts**: Flagged high-risk combinations
- **Alternative Options**: Second-choice rams for each ewe
- **Summary Statistics**: Expected flock improvement

## File Format

Input files can be:
- CSV with LPN_ID column
- Excel (.xlsx) with LPN_ID column
- Comma-separated LPN IDs directly on command line

$ARGUMENTS
