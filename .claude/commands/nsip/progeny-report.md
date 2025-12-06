---
description: Evaluate sires by analyzing their offspring performance
allowed-tools: Bash(uv run:*)
---

# /nsip:progeny-report

Evaluate sires by analyzing their offspring performance.

## Usage

```
/nsip:progeny-report <sire_lpn> [--traits <trait_list>] [--compare <sire_lpn2,...>]
```

## Arguments

- `sire_lpn`: Sire LPN ID to analyze
- `--traits`: Traits to focus on (default: all available)
- `--compare`: Additional sire LPN IDs for comparison
- `--index`: Selection index to rank by (terminal, maternal, range)

## Process

1. Fetch all progeny records for the sire
2. Retrieve EBV data for all offspring
3. Calculate progeny statistics:
   - Mean EBVs across traits
   - Variance within progeny group
   - Top and bottom performer identification
4. If comparing: rank sires by offspring quality
5. Identify exceptional individuals

## Example

```bash
# Single sire analysis
uv run python -m nsip_skills.progeny_analysis 6####92018###001

# Focus on growth traits
uv run python -m nsip_skills.progeny_analysis SIRE_LPN --traits WWT,PWWT,YWT

# Compare multiple sires
uv run python -m nsip_skills.progeny_analysis SIRE1 --compare SIRE2,SIRE3,SIRE4

# Rank by maternal index
uv run python -m nsip_skills.progeny_analysis SIRE_LPN --index maternal
```

## Output

- **Progeny Summary**: Count by gender, status breakdown
- **Trait Means**: Average EBVs of all offspring
- **Consistency Analysis**: Variance and reliability
- **Top Performers**: Highest-scoring offspring
- **Sire Ranking**: When comparing multiple sires
- **Genetic Gain**: Comparison to expected values

## Sire Comparison

When using `--compare`, the output includes:
- Side-by-side progeny statistics
- Ranking by overall offspring quality
- Trait-specific rankings
- Recommendations for breeding use

$ARGUMENTS
