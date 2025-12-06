---
description: Design a multi-generation selection strategy for trait improvement
allowed-tools: Bash(uv run:*)
---

# /nsip:trait-improvement

Design a multi-generation selection strategy for trait improvement.

## Usage

```
/nsip:trait-improvement <flock_file> --targets <json_targets> [--intensity <value>]
```

## Arguments

- `flock_file`: Spreadsheet or list of current flock LPN IDs
- `--targets`: JSON dict of trait → target value (e.g., '{"WWT": 5.0, "NLW": 0.20}')
- `--intensity`: Selection intensity (1.4=top 20%, 1.76=top 10%, 2.0=top 5%)
- `--max-generations`: Maximum generations to project (default: 10)

## Process

1. Analyze current flock trait distributions
2. Calculate genetic gap to each target
3. Estimate response to selection using:
   - Trait heritabilities
   - Selection intensity
   - Phenotypic variation
4. Project improvement trajectory
5. Generate selection strategy recommendations

## Selection Intensity Guide

| Intensity | Selection Rate | Use When |
|-----------|----------------|----------|
| 1.0 | ~50% | Large flock, modest goals |
| 1.4 | ~20% | Balanced approach |
| 1.76 | ~10% | Aggressive improvement |
| 2.0 | ~5% | Maximum pressure |

## Example

```bash
# Basic improvement plan
uv run python -m nsip_skills.trait_planner flock.csv --targets '{"WWT": 5.0, "PWWT": 8.0}'

# Aggressive selection
uv run python -m nsip_skills.trait_planner flock.csv --targets '{"NLW": 0.25}' --intensity 1.76

# Long-term planning
uv run python -m nsip_skills.trait_planner flock.csv --targets '{"WWT": 7.0}' --max-generations 15
```

## Output

- **Current vs Target**: Gap analysis for each trait
- **Heritability Assessment**: Expected response rates
- **Generation-by-Generation Projections**: Improvement trajectory
- **Selection Requirements**: How strict selection must be
- **Timeline Estimates**: Generations to reach goals
- **Recommendations**: Strategic advice for fastest improvement

## Heritability Reference

| Trait | Heritability | Response |
|-------|--------------|----------|
| BWT | 0.30 | Moderate |
| WWT | 0.25 | Moderate |
| PWWT | 0.35 | Good |
| NLW | 0.10 | Slow |
| MWWT | 0.15 | Slow |

$ARGUMENTS
