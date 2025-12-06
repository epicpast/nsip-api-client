---
description: Generate comprehensive flock performance statistics and insights
allowed-tools: Bash(uv run:*)
---

# /nsip:flock-dashboard

Generate comprehensive flock performance statistics and insights.

## Usage

```
/nsip:flock-dashboard <flock_file> [--name <flock_name>] [--compare-breed <breed_id>]
```

## Arguments

- `flock_file`: Spreadsheet with flock LPN IDs
- `--name`: Optional flock name for report
- `--compare-breed`: Breed ID for comparison percentiles

## Process

1. Fetch data for all flock animals
2. Calculate aggregate statistics:
   - Gender distribution
   - Age distribution by birth year
   - Status breakdown
   - Trait means, medians, and ranges
3. Calculate selection index scores for all animals
4. Identify top and bottom performers
5. Compare to breed average if specified
6. Generate improvement opportunities

## Example

```bash
# Basic dashboard
uv run python -m nsip_skills.flock_stats flock.csv

# Named flock with breed comparison
uv run python -m nsip_skills.flock_stats flock.csv --name "Valley Farm" --compare-breed 486

# JSON output
uv run python -m nsip_skills.flock_stats flock.csv --json
```

## Output

### Summary Statistics
- Total animals (count by gender)
- Status breakdown (Active, Sold, Dead)
- Age distribution (animals per birth year)

### Trait Summary Table
| Trait | Mean | Median | Std | Min | Max | Count |
|-------|------|--------|-----|-----|-----|-------|
| BWT   | 0.45 | 0.42   | 0.3 | -0.5| 1.2 | 95    |
| WWT   | 2.80 | 2.75   | 1.1 | 0.5 | 5.5 | 95    |

### Index Rankings
Top performers by each selection index:
- Terminal Index: [top 5 animals]
- Maternal Index: [top 5 animals]
- Range Index: [top 5 animals]

### Improvement Opportunities
Automatically identified areas for focus:
- Traits below breed average
- High variability areas
- Age structure concerns
- Ram:ewe ratio analysis

$ARGUMENTS
