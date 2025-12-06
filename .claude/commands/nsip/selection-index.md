---
description: Calculate and rank animals by selection index scores
allowed-tools: Bash(uv run:*)
---

# /nsip:selection-index

Calculate and rank animals by selection index scores.

## Usage

```
/nsip:selection-index <flock_file> [--index <name>] [--custom <json_weights>]
```

## Arguments

- `flock_file`: Spreadsheet or list of LPN IDs
- `--index`: Preset index name (terminal, maternal, range, hair)
- `--custom`: Custom trait weights as JSON (e.g., '{"WWT": 1.5, "NLW": 2.0}')
- `--top`: Show only top N animals (default: 20)
- `--list-presets`: Show available preset indexes

## Preset Indexes

| Index | Focus | Key Traits |
|-------|-------|------------|
| Terminal | Market lambs | PWWT+, YFAT-, YEMD+ |
| Maternal | Replacement ewes | NLW+, MWWT+, WWT+ |
| Range | Balanced production | All traits weighted |
| Hair | Hair sheep breeds | Growth without wool |

## Process

1. Fetch EBV data for all animals
2. Apply index weights to calculate composite scores:
   `Score = Σ(weight × EBV)`
3. Rank animals by total score
4. Calculate percentile positions
5. Identify selection thresholds

## Example

```bash
# Use preset terminal index
uv run python -m nsip_skills.selection_index flock.csv --index terminal

# Custom commercial index
uv run python -m nsip_skills.selection_index flock.csv --custom '{"WWT": 1.5, "PWWT": 1.0, "NLW": 2.0, "BWT": -0.5}'

# Show top 10 only
uv run python -m nsip_skills.selection_index flock.csv --index maternal --top 10

# List available presets
uv run python -m nsip_skills.selection_index --list-presets
```

## Output

### Summary Statistics
- Animals ranked: [count]
- Mean score: [value]
- Standard deviation: [value]
- Top 10% threshold: [score]
- Top 25% threshold: [score]

### Index Weights
Shows the contribution of each trait to the index.

### Rankings Table
| Rank | LPN ID | Score | BWT | WWT | PWWT | ... |
|------|--------|-------|-----|-----|------|-----|
| 1    | ABC123 | 85.5  | 2.1 | 5.2 | 8.3  | ... |
| 2    | DEF456 | 82.3  | 1.8 | 4.9 | 7.8  | ... |

## Custom Index Tips

- Positive weights favor higher EBV values
- Negative weights (e.g., BWT: -0.5) favor lower values
- Weights reflect relative economic importance
- Start with preset and adjust to your goals

$ARGUMENTS
