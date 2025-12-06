---
description: Generate AI-powered breeding recommendations for flock improvement
allowed-tools: Bash(uv run:*)
---

# /nsip:breeding-recs

Generate AI-powered breeding recommendations for flock improvement.

## Usage

```
/nsip:breeding-recs <flock_file> [--goal <breeding_goal>] [--philosophy <type>]
```

## Arguments

- `flock_file`: Spreadsheet or list of flock LPN IDs
- `--goal`: Breeding goal (terminal, maternal, balanced). Default: balanced
- `--philosophy`: Operation type (commercial, seedstock, hobbyist). Default: commercial

## Process

1. Analyze complete flock composition and performance
2. Calculate index scores using appropriate breeding goal
3. Identify top 25% performers for retention
4. Identify bottom 25% for culling consideration
5. Analyze trait weaknesses requiring attention
6. Generate prioritized recommendations

## Recommendation Types

| Type | Description |
|------|-------------|
| PRIORITY | Top animals deserving premium matings |
| RETAIN | Animals to keep in breeding program |
| CULL | Candidates for removal |
| OUTSIDE_GENETICS | Traits needing external improvement |
| MANAGEMENT | Operational practice changes |

## Example

```bash
# Basic recommendations
uv run python -m nsip_skills.recommendation_engine flock.csv

# Terminal focus for commercial operation
uv run python -m nsip_skills.recommendation_engine flock.csv --goal terminal --philosophy commercial

# Seedstock breeder focus
uv run python -m nsip_skills.recommendation_engine flock.csv --philosophy seedstock

# JSON output
uv run python -m nsip_skills.recommendation_engine flock.csv --json
```

## Output

### Flock Summary
- Total animals, male/female breakdown
- Current average performance

### Priority Breeding Stock
Top performers deserving maximum genetic contribution:
- Animal ID, rank, score, and recommended action

### Retain List
Animals to keep in breeding program (top 25%)

### Cull Candidates
Bottom performers to consider removing (bottom 25%, flock size > 10)

### Trait Improvement Priorities
Traits below breed average requiring focus selection

### All Recommendations
Prioritized list of actions with:
- Rationale: Why this recommendation
- Impact: Expected outcome
- Action: Specific step to take

## Philosophy Guide

| Philosophy | Focus |
|------------|-------|
| Commercial | Proven genetics, low risk, practical |
| Seedstock | Comprehensive data, accuracy, innovation |
| Hobbyist | Balanced, manageable, educational |

$ARGUMENTS
