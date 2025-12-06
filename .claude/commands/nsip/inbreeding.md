---
description: Calculate inbreeding coefficients using pedigree data
allowed-tools: Bash(uv run:*)
---

# /nsip:inbreeding

Calculate inbreeding coefficients using pedigree data.

## Usage

```
/nsip:inbreeding <lpn_id> [--generations <n>] [--mating <sire_lpn>,<dam_lpn>]
```

## Arguments

- `lpn_id`: Animal LPN ID to analyze
- `--generations`: Generations to trace (default: 4)
- `--mating`: Project offspring inbreeding for proposed mating (sire,dam format)

## Process

1. Build pedigree tree from NSIP lineage data
2. Trace paths to identify common ancestors
3. Calculate Wright's inbreeding coefficient using path method:
   `F = Σ[(1/2)^(n1+n2+1) × (1 + FA)]`
4. Assign risk level based on coefficient
5. For matings: project offspring coefficient

## Risk Thresholds

| Risk Level | Coefficient | Interpretation |
|------------|-------------|----------------|
| LOW | < 6.25% | Generally acceptable |
| MODERATE | 6.25-12.5% | Warrants attention |
| HIGH | > 12.5% | Avoid if possible |

## Example

```bash
# Analyze single animal
uv run python -m nsip_skills.inbreeding 6####92020###249

# Extended pedigree analysis
uv run python -m nsip_skills.inbreeding 6####92020###249 --generations 5

# Project offspring inbreeding
uv run python -m nsip_skills.inbreeding --mating SIRE_LPN,DAM_LPN
```

## Output

- **Inbreeding Coefficient**: Percentage with risk level
- **Common Ancestors**: Animals appearing on both sides of pedigree
- **Pedigree Tree**: Visual representation of ancestry
- **Path Details**: How common ancestors connect

## Mating Projections

When using `--mating`, the output includes:
- Projected offspring inbreeding coefficient
- Risk assessment for the mating
- Recommendation (proceed/caution/avoid)

$ARGUMENTS
