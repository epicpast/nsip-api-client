# nsip-skills

Breeding decision support tools for sheep genetics using NSIP EBV data.

## Installation

```bash
pip install nsip-skills

# With Google Sheets support
pip install nsip-skills[gsheets]
```

## Features

- **EBV Analysis**: Compare estimated breeding values across animals
- **Flock Import**: Import and enrich flock data from spreadsheets
- **Flock Statistics**: Aggregate flock performance metrics
- **Inbreeding Calculator**: Pedigree-based inbreeding coefficients
- **Mating Optimizer**: Optimize ram-ewe pairings
- **Progeny Analysis**: Evaluate sires by offspring performance
- **Trait Planner**: Multi-generation selection planning
- **Ancestry Builder**: Generate pedigree trees
- **Selection Index**: Calculate custom breeding indexes

## Quick Start

```python
from nsip_skills import ebv_analysis, inbreeding

# Compare EBVs
comparison = ebv_analysis.compare_animals(["LPN1", "LPN2", "LPN3"])

# Calculate inbreeding coefficient
coef = inbreeding.calculate_coefficient(sire="RAM_LPN", dam="EWE_LPN")
```

## CLI Tools

```bash
nsip-ebv-analysis LPN1 LPN2
nsip-inbreeding --mating RAM_LPN,EWE_LPN
nsip-flock-stats my_flock.csv
```

## Documentation

Full documentation is available at the [project repository](https://github.com/epicpast/nsip-api-client).

## License

MIT License - see [LICENSE](https://github.com/epicpast/nsip-api-client/blob/main/LICENSE) for details.
