---
description: Compare and analyze EBV traits across a group of animals
allowed-tools: Bash(uv run:*)
---

# /nsip:ebv-analyzer

Compare and analyze EBV traits across a group of animals.

## Usage

```
/nsip:ebv-analyzer <lpn_ids...> [--traits <trait_list>] [--breed-context <breed_id>]
```

## Arguments

- `lpn_ids`: One or more LPN IDs to analyze (space-separated)
- `--traits`: Comma-separated list of traits (default: BWT,WWT,PWWT,YFAT,YEMD,NLW)
- `--breed-context`: Breed ID for percentile calculations

## Process

1. Fetch EBV data for all specified animals
2. Calculate percentile rankings within the group
3. If breed context provided, compare to breed-wide ranges
4. Identify strengths and weaknesses for each animal
5. Generate comparison table and individual profiles

## Example

```bash
# Analyze specific animals
uv run python -m nsip_skills.ebv_analysis 6####92020###249 6####92020###250 6####92020###251

# Focus on specific traits
uv run python -m nsip_skills.ebv_analysis LPN1 LPN2 --traits WWT,PWWT,NLW

# With breed context for percentiles
uv run python -m nsip_skills.ebv_analysis LPN1 LPN2 --breed-context 486
```

## Output

- **Comparison Table**: Side-by-side EBV values with rankings
- **Percentile Ranks**: Position within group and breed
- **Strength/Weakness Profiles**: Per-animal trait analysis
- **Recommendations**: Suggestions for breeding use

## Trait Abbreviations

| Trait | Description |
|-------|-------------|
| BWT | Birth Weight |
| WWT | Weaning Weight |
| PWWT | Post-Weaning Weight |
| YWT | Yearling Weight |
| YFAT | Yearling Fat Depth |
| YEMD | Yearling Eye Muscle Depth |
| NLB | Number Lambs Born |
| NLW | Number Lambs Weaned |
| MWWT | Maternal Weaning Weight |

$ARGUMENTS
