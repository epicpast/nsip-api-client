---
applyTo: "src/nsip_skills/**/*.py"
---

# NSIP Skills Module Guidelines

## Module Purpose
Breeding decision support tools using NSIP EBV (Estimated Breeding Value) data.

## Key Algorithms

### Inbreeding Calculation (Wright's Path Coefficient)
```
F = sum[(1/2)^(n1+n2+1) * (1 + FA)]
```
Where n1/n2 are path lengths through common ancestor, FA is ancestor's inbreeding coefficient.

### Genetic Gain Formula
```
R = h^2 * i * sigma_p
```
Where R = response per generation, h^2 = heritability, i = selection intensity, sigma_p = phenotypic std dev.

## Preset Selection Indexes (weights in data_models.py)
- **Terminal**: BWT(-0.5), WWT(1.0), PWWT(1.5), YWT(1.0), YEMD(0.8), YFAT(-0.3)
- **Maternal**: NLB(2.0), NLW(2.5), MWWT(1.5), BWT(-1.0), WWT(0.5)
- **Range**: BWT(-0.5), WWT(1.0), PWWT(1.0), NLW(1.5), MWWT(1.0)
- **Hair**: BWT(-0.5), WWT(1.2), PWWT(1.5), NLB(1.5), NLW(2.0), DAG(-0.5)

## Dependencies
- Uses `nsip_client` for API access (do not import MCP modules here)
- Uses pandas for data analysis
- Uses numpy for numerical operations

## Common Patterns

### NSIP Client Usage
```python
from nsip_client import NSIPClient

client = NSIPClient()
animal = client.get_animal_details(lpn_id)
lineage = client.get_lineage(lpn_id)
```

### DataFrame Operations
- Use type hints: `pd.DataFrame`, `pd.Series`
- Handle missing data with `fillna()` or `dropna()`
- Prefer vectorized operations over loops

## CLI Entry Points
Each module should have a `main()` function for CLI usage.
Entry points are defined in `packaging/nsip-skills/pyproject.toml`.
