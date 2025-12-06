---
description: Generate comprehensive ancestry/pedigree reports
allowed-tools: Bash(uv run:*)
---

# /nsip:ancestry

Generate comprehensive ancestry/pedigree reports.

## Usage

```
/nsip:ancestry <lpn_id> [--generations <n>] [--style <format>]
```

## Arguments

- `lpn_id`: Animal LPN ID to trace
- `--generations`: Generations to display (default: 4)
- `--style`: Output style (ascii, markdown). Default: ascii

## Process

1. Recursively fetch lineage data from NSIP
2. Build complete pedigree tree structure
3. Annotate ancestors with key information
4. Calculate genetic contribution percentages
5. Identify notable ancestors (proven sires, high producers)
6. Detect common ancestors indicating inbreeding

## Example

```bash
# Basic pedigree
uv run python -m nsip_skills.ancestry_builder 6####92020###249

# Extended ancestry
uv run python -m nsip_skills.ancestry_builder LPN_ID --generations 5

# Markdown output
uv run python -m nsip_skills.ancestry_builder LPN_ID --style markdown

# JSON for processing
uv run python -m nsip_skills.ancestry_builder LPN_ID --json
```

## Output

### Pedigree Tree (ASCII)
```
                              Subject: 6####92020###249
                             /                          \
                      Sire: SS123                   Dam: DD456
                     /          \                  /          \
              Sire's Sire    Sire's Dam     Dam's Sire    Dam's Dam
```

### Bloodline Breakdown
- Sire's Sire (SS123): 25%
- Sire's Dam (SD123): 25%
- Dam's Sire (DS123): 25%
- Dam's Dam (DD123): 25%

### Notable Ancestors
Animals with:
- High progeny counts (proven genetics)
- High US Index scores
- Significant influence on the breed

### Common Ancestors
If any ancestor appears multiple times, they're flagged as inbreeding indicators.

$ARGUMENTS
