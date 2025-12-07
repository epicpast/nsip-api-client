# NSIP Skills: Claude Code Slash Commands Guide

This document provides comprehensive examples for all 10 NSIP Skills slash commands available in Claude Code. These commands provide breeding decision support tools for sheep genetic improvement using data from the National Sheep Improvement Program (NSIP).

## Table of Contents

1. [Introduction](#introduction)
2. [Data Import and Flock Management](#data-import-and-flock-management)
   - [/nsip:flock-import](#nsipflock-import)
   - [/nsip:flock-dashboard](#nsipflock-dashboard)
3. [EBV Analysis](#ebv-analysis)
   - [/nsip:ebv-analyzer](#nsipebv-analyzer)
   - [/nsip:selection-index](#nsipselection-index)
4. [Pedigree and Inbreeding](#pedigree-and-inbreeding)
   - [/nsip:ancestry](#nsipancestry)
   - [/nsip:inbreeding](#nsipinbreeding)
5. [Breeding Planning](#breeding-planning)
   - [/nsip:mating-plan](#nsipmating-plan)
   - [/nsip:trait-improvement](#nsiptrait-improvement)
   - [/nsip:breeding-recs](#nsipbreeding-recs)
6. [Sire Evaluation](#sire-evaluation)
   - [/nsip:progeny-report](#nsipprogeny-report)
7. [Example Workflows](#example-workflows)
8. [Quick Reference](#quick-reference)

---

## Introduction

### What are NSIP Skills?

NSIP Skills are Claude Code slash commands that transform raw NSIP genetic data into actionable breeding insights. Each command invokes a specialized Python module in the `nsip_skills` package, providing:

- **Automated data enrichment** from the NSIP database
- **Statistical analysis** of EBVs (Estimated Breeding Values)
- **Inbreeding calculations** using Wright's path coefficient method
- **Optimization algorithms** for mating decisions
- **Multi-generation projections** for genetic improvement planning

### Prerequisites

Before using these commands, ensure you have:

1. **LPN IDs** for your animals (the unique NSIP identifier format, e.g., `6402382024NCS310`)
2. **Spreadsheet files** in CSV or Excel format with an `lpn_id` column
3. Basic understanding of EBV terminology (see the [Core Concepts](#understanding-ebvs) section in `docs/nsip-skills.md`)

### Command Syntax

All NSIP Skills follow this pattern:

```
/nsip:<command-name> <required_arguments> [--optional-flags]
```

Alternatively, you can run them as Python modules:

```bash
uv run python -m nsip_skills.<module_name> <arguments>
```

---

## Data Import and Flock Management

### /nsip:flock-import

**Purpose:** Import your flock data from a spreadsheet and enrich it with NSIP breeding values, lineage, and status information.

**When to use:** Start here if you have a spreadsheet of your animals with LPN IDs and want to add genetic data from NSIP.

#### Syntax

```
/nsip:flock-import <spreadsheet_path> [--output <output_path>] [--lineage] [--progeny]
```

#### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `spreadsheet_path` | Yes | Path to CSV, Excel (.xlsx), or Google Sheets URL |
| `--output` | No | Output file path (default: `enriched_<input_name>.csv`) |
| `--lineage` | No | Include sire/dam lineage data |
| `--progeny` | No | Include progeny counts |

#### Input File Format

Your spreadsheet must have a column named one of: `LPN_ID`, `lpn_id`, `LPN`, or `lpn`

Optional columns that will be preserved:
- `Name` or `name` - Your local name for the animal
- `Tag` or `tag` - Ear tag or other identifier
- `Notes` or `notes` - Any notes
- `Group` or `group` - Breeding group or pen

**Example input file (my_flock.csv):**
```csv
lpn_id,tag,group,notes
6402382024NCS310,Blue-123,Breeding Ewes,Best lamb producer
6402382024NCS311,Blue-124,Breeding Ewes,Good mother
6402382023RAM001,Red-001,Rams,Main sire
6402382022EWE001,Green-050,Replacements,
```

#### Examples

**Basic import:**
```
/nsip:flock-import my_flock.csv
```

**Import with custom output and lineage data:**
```
/nsip:flock-import my_flock.xlsx --output enriched_2024.xlsx --lineage
```

**Import with full data (lineage + progeny):**
```
/nsip:flock-import flock.csv --lineage --progeny
```

#### Expected Output

The enriched spreadsheet adds columns for:
- Breed, gender, date of birth, status
- Sire LPN, Dam LPN (if `--lineage` used)
- All available EBV traits (BWT, WWT, PWWT, YEMD, YFAT, NLB, NLW, etc.)
- Accuracy values for each trait (e.g., `BWT_acc`, `WWT_acc`)
- Validation status for any animals not found

**Console output:**
```
## Flock Import Report

**Source**: my_flock.csv
**Total Records**: 4

### Successfully Fetched
- 6402382024NCS310
- 6402382024NCS311
- 6402382023RAM001
- 6402382022EWE001

### Not Found
(none)

### Errors
(none)

Exported to: enriched_my_flock.csv
```

---

### /nsip:flock-dashboard

**Purpose:** Generate comprehensive flock performance statistics, identify top performers, and highlight improvement opportunities.

**When to use:** After importing your flock, use this to get an overview of your genetic progress and identify areas for focus.

#### Syntax

```
/nsip:flock-dashboard <flock_file> [--name <flock_name>] [--compare-breed <breed_id>] [--json]
```

#### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `flock_file` | Yes | Spreadsheet with flock LPN IDs |
| `--name` | No | Flock name for the report |
| `--compare-breed` | No | Breed ID for comparison percentiles |
| `--json` | No | Output as JSON instead of markdown |

#### Examples

**Basic dashboard:**
```
/nsip:flock-dashboard enriched_flock.csv
```

**Named flock with breed comparison:**
```
/nsip:flock-dashboard flock.csv --name "Valley Farm 2024" --compare-breed 486
```

**JSON output for further processing:**
```
/nsip:flock-dashboard flock.csv --json > flock_stats.json
```

#### Expected Output

```
## Flock Dashboard

**Flock**: Valley Farm 2024
**Total Animals**: 95
**Males**: 8 | **Females**: 87

### Status Distribution
- CURRENT: 82
- SOLD: 10
- DEAD: 3

### Age Distribution
- 2024: 25 animals
- 2023: 30 animals
- 2022: 28 animals
- 2021: 12 animals

### Trait Summary
| Trait | Mean  | Median | Std Dev | Min   | Max   | Count |
|-------|-------|--------|---------|-------|-------|-------|
| BWT   | 0.245 | 0.220  | 0.312   | -0.35 | 0.85  | 95    |
| WWT   | 2.950 | 2.880  | 0.923   | 0.50  | 5.20  | 95    |
| PWWT  | 4.350 | 4.200  | 1.234   | 1.20  | 7.80  | 95    |
| NLW   | 0.092 | 0.085  | 0.045   | -0.05 | 0.25  | 95    |

### Top Performers by Terminal Index
1. 6402382024NCS310: 15.2
2. 6402382023NCS215: 14.8
3. 6402382023NCS218: 14.1
4. 6402382022NCS105: 13.9
5. 6402382024NCS312: 13.5

### Improvement Opportunities
- **High variability in PWWT** (CV=28%): Opportunity to standardize through selection
- **Below breed average on NLW**: Consider rams with strong NLW performance
- **Age structure**: Low proportion of young animals - consider retaining more replacements
```

---

## EBV Analysis

### /nsip:ebv-analyzer

**Purpose:** Compare and analyze EBV traits across multiple animals, identifying strengths, weaknesses, and relative rankings.

**When to use:** When evaluating purchase candidates, selecting breeding stock, or comparing animals for specific traits.

#### Syntax

```
/nsip:ebv-analyzer <lpn_id1> <lpn_id2> [...] [--traits <trait_list>] [--breed-context <breed_id>]
```

#### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `lpn_ids` | Yes | One or more LPN IDs to analyze (space-separated) |
| `--traits` | No | Comma-separated traits to focus on (default: BWT,WWT,PWWT,YFAT,YEMD,NLW) |
| `--breed-context` | No | Breed ID for percentile calculations |

#### Trait Abbreviations

| Trait | Description | Direction |
|-------|-------------|-----------|
| BWT | Birth Weight | Lower is better |
| WWT | Weaning Weight | Higher is better |
| PWWT | Post-Weaning Weight | Higher is better |
| YWT | Yearling Weight | Higher is better |
| YFAT | Yearling Fat Depth | Context-dependent |
| YEMD | Yearling Eye Muscle Depth | Higher is better |
| NLB | Number Lambs Born | Higher is better |
| NLW | Number Lambs Weaned | Higher is better |
| MWWT | Maternal Weaning Weight | Higher is better |

#### Examples

**Compare three rams:**
```
/nsip:ebv-analyzer 6402382023RAM001 6402382023RAM002 6402382022RAM005
```

**Focus on terminal traits for market lamb production:**
```
/nsip:ebv-analyzer RAM1 RAM2 RAM3 --traits WWT,PWWT,YEMD,YFAT
```

**Compare with breed context:**
```
/nsip:ebv-analyzer RAM1 RAM2 --breed-context 486
```

#### Expected Output

```
## EBV Trait Analysis

### Trait Statistics
| Trait | Mean  | Std Dev | Min   | Max   | Count |
|-------|-------|---------|-------|-------|-------|
| BWT   | 0.180 | 0.245   | -0.15 | 0.45  | 3     |
| WWT   | 3.200 | 0.892   | 2.15  | 4.25  | 3     |
| PWWT  | 5.450 | 1.123   | 4.10  | 6.80  | 3     |
| YEMD  | 0.820 | 0.156   | 0.65  | 0.98  | 3     |
| NLW   | 0.095 | 0.032   | 0.06  | 0.13  | 3     |

### Animal Comparison
| Animal           | BWT          | WWT          | PWWT         | YEMD         | NLW          |
|------------------|--------------|--------------|--------------|--------------|--------------|
| 6402382023RAM001 | -0.15 (95%)  | 4.25 (98%)   | 6.80 (95%)   | 0.98 (99%)   | 0.06 (25%)   |
| 6402382023RAM002 | 0.20 (45%)   | 3.25 (55%)   | 5.45 (60%)   | 0.82 (75%)   | 0.13 (95%)   |
| 6402382022RAM005 | 0.45 (15%)   | 2.15 (20%)   | 4.10 (25%)   | 0.65 (35%)   | 0.10 (65%)   |

**Top Performers** (most strengths): 6402382023RAM001, 6402382023RAM002
**Needs Improvement** (most weaknesses): 6402382022RAM005

### Rankings by Trait
- **BWT**: 6402382023RAM001 > 6402382023RAM002 > 6402382022RAM005
- **WWT**: 6402382023RAM001 > 6402382023RAM002 > 6402382022RAM005
- **PWWT**: 6402382023RAM001 > 6402382023RAM002 > 6402382022RAM005
- **YEMD**: 6402382023RAM001 > 6402382023RAM002 > 6402382022RAM005
- **NLW**: 6402382023RAM002 > 6402382022RAM005 > 6402382023RAM001
```

---

### /nsip:selection-index

**Purpose:** Calculate and rank animals by composite selection index scores that combine multiple traits weighted by economic importance.

**When to use:** When you need to rank animals for selection decisions based on multiple traits simultaneously.

#### Syntax

```
/nsip:selection-index <flock_file> [--index <name>] [--custom <json_weights>] [--top <n>] [--list-presets]
```

#### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `flock_file` | Yes | Spreadsheet or list of LPN IDs |
| `--index` | No | Preset index name: `terminal`, `maternal`, `range`, `hair` |
| `--custom` | No | Custom trait weights as JSON |
| `--top` | No | Show only top N animals (default: 20) |
| `--list-presets` | No | Show available preset indexes |

#### Preset Indexes

| Index | Focus | Key Trait Weights |
|-------|-------|-------------------|
| Terminal | Market lambs | PWWT+, YEMD+, BWT-, YFAT- |
| Maternal | Replacement ewes | NLW++, MWWT+, WWT+ |
| Range | Balanced production | All traits weighted |
| Hair | Hair sheep breeds | Growth + reproduction, no wool |

#### Examples

**Rank by terminal index:**
```
/nsip:selection-index flock.csv --index terminal
```

**Custom commercial index emphasizing growth and fertility:**
```
/nsip:selection-index flock.csv --custom '{"WWT": 1.5, "PWWT": 1.0, "NLW": 2.0, "BWT": -0.5}'
```

**Show top 10 maternal performers:**
```
/nsip:selection-index flock.csv --index maternal --top 10
```

**List available presets:**
```
/nsip:selection-index --list-presets
```

#### Expected Output

```
## Terminal Index Rankings

*Emphasizes growth and carcass traits for meat production*

### Summary Statistics
- Animals ranked: 95
- Mean score: 8.45
- Standard deviation: 3.21
- Top 10% threshold: 13.20
- Top 25% threshold: 10.85

### Index Weights
| Trait | Weight | Direction |
|-------|--------|-----------|
| BWT   | -0.5   | Lower preferred |
| WWT   | +1.0   | Higher preferred |
| PWWT  | +1.5   | Higher preferred |
| YWT   | +1.0   | Higher preferred |
| YEMD  | +0.8   | Higher preferred |
| YFAT  | -0.3   | Lower preferred |

### Rankings
| Rank | LPN ID           | Score | Percentile | BWT   | WWT  | PWWT | YEMD |
|------|------------------|-------|------------|-------|------|------|------|
| 1    | 6402382024NCS310 | 15.20 | 99%        | -0.38 | 4.20 | 6.80 | 0.85 |
| 2    | 6402382023NCS215 | 14.80 | 98%        | -0.15 | 3.95 | 6.50 | 0.92 |
| 3    | 6402382023NCS218 | 14.10 | 97%        | -0.22 | 3.80 | 6.20 | 0.88 |
| ...  | ...              | ...   | ...        | ...   | ...  | ...  | ...  |
```

---

## Pedigree and Inbreeding

### /nsip:ancestry

**Purpose:** Generate comprehensive pedigree reports showing ancestry, bloodline contributions, and common ancestors.

**When to use:** To understand an animal's genetic background, verify pedigrees, or identify potential inbreeding paths.

#### Syntax

```
/nsip:ancestry <lpn_id> [--generations <n>] [--style <format>] [--json]
```

#### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `lpn_id` | Yes | Animal LPN ID to trace |
| `--generations` | No | Generations to display (default: 4) |
| `--style` | No | Output style: `ascii` or `markdown` (default: ascii) |
| `--json` | No | Output as JSON for processing |

#### Examples

**Basic 4-generation pedigree:**
```
/nsip:ancestry 6402382024NCS310
```

**Extended 5-generation ancestry:**
```
/nsip:ancestry 6402382024NCS310 --generations 5
```

**Markdown format for documentation:**
```
/nsip:ancestry 6402382024NCS310 --style markdown
```

#### Expected Output

```
## Pedigree Report: 6402382024NCS310

### Subject
- **LPN**: 6402382024NCS310
- **Gender**: Female
- **DOB**: 2024-02-15
- **Farm**: Valley Farm
- **US Index**: 125.4

### Pedigree Tree (4 Generations)

                              6402382024NCS310 (F)
                             /                    \
                   6402382021XYZ001 (M)     6402382020XYZ002 (F)
                  /            \           /            \
         6402382019ABC123  6402382019ABC124  6402382018DEF456  6402382018DEF457
              |      |          |      |          |      |          |      |
            (GGS)  (GGD)      (GGS)  (GGD)      (GGS)  (GGD)      (GGS)  (GGD)

### Bloodline Breakdown
| Ancestor | Relationship | Contribution |
|----------|--------------|--------------|
| 6402382019ABC123 | Sire's Sire | 25.0% |
| 6402382019ABC124 | Sire's Dam | 25.0% |
| 6402382018DEF456 | Dam's Sire | 25.0% |
| 6402382018DEF457 | Dam's Dam | 25.0% |

### Common Ancestors
- 6402382017GGG001: Appears on both sire and dam sides (potential inbreeding)

### Notable Ancestors
- 6402382019ABC123: High progeny count (127), US Index 142.3
- 6402382018DEF456: Proven sire, US Index 138.5

### Genetic Diversity Score
- **Score**: 0.92 (1.0 = no common ancestors, lower = more inbreeding)
```

---

### /nsip:inbreeding

**Purpose:** Calculate inbreeding coefficients using Wright's path coefficient method. Can analyze existing animals or project offspring inbreeding for proposed matings.

**When to use:** Before making breeding decisions to avoid excessive inbreeding, or to evaluate the genetic diversity of your flock.

#### Syntax

```
/nsip:inbreeding <lpn_id> [--generations <n>] [--mating <dam_lpn>] [--json]
```

#### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `lpn_id` | Yes | Animal LPN ID to analyze (or sire LPN if using --mating) |
| `--generations` | No | Generations to trace (default: 4) |
| `--mating` | No | Dam LPN ID for projected offspring calculation |
| `--json` | No | Output as JSON |

#### Risk Thresholds

| Coefficient | Risk Level | Interpretation |
|-------------|------------|----------------|
| < 6.25% | LOW | Generally acceptable |
| 6.25% - 12.5% | MODERATE | Warrants attention, consider alternatives |
| > 12.5% | HIGH | Avoid if possible |

#### Examples

**Analyze single animal:**
```
/nsip:inbreeding 6402382024NCS310
```

**Extended pedigree analysis (5 generations):**
```
/nsip:inbreeding 6402382024NCS310 --generations 5
```

**Project offspring inbreeding for a proposed mating:**
```
/nsip:inbreeding 6402382023RAM001 --mating 6402382022EWE015
```

#### Expected Output (Single Animal)

```
## Inbreeding Analysis: 6402382024NCS310

**Coefficient**: 3.12%
**Risk Level**: LOW
**Generations Analyzed**: 4

### Interpretation
This animal has a low inbreeding coefficient (< 6.25%), indicating acceptable
genetic diversity. No immediate concerns for inbreeding depression.

### Common Ancestors
| Ancestor | Contribution | Path Count |
|----------|--------------|------------|
| 6402382017GGG001 | 1.56% | 2 |
| 6402382016HHH002 | 1.56% | 2 |

### Path Details
| Ancestor | Sire Path | Dam Path | Contribution |
|----------|-----------|----------|--------------|
| 6402382017GGG001 | 3 | 3 | 1.56% |
| 6402382016HHH002 | 4 | 3 | 0.78% |
| 6402382016HHH002 | 3 | 4 | 0.78% |
```

#### Expected Output (Mating Projection)

```
## Projected Offspring Inbreeding

**Sire**: 6402382023RAM001
**Dam**: 6402382022EWE015

**Projected Coefficient**: 6.25%
**Risk Level**: MODERATE
**Recommendation**: PROCEED WITH CAUTION

### Interpretation
This mating would produce offspring with moderate inbreeding. Consider
alternative matings if available, but proceed if this is the best genetic
match for your breeding goals.

### Common Ancestors Between Parents
| Ancestor | Contribution |
|----------|--------------|
| 6402382019ABC123 | 3.12% |
| 6402382018DEF456 | 3.12% |

### Alternative Recommendations
Consider these rams for lower inbreeding:
- 6402382023RAM002 (projected COI: 2.1%)
- 6402382022RAM008 (projected COI: 1.8%)
```

---

## Breeding Planning

### /nsip:mating-plan

**Purpose:** Generate optimized ram-ewe pairings that maximize genetic progress while respecting inbreeding constraints.

**When to use:** At the start of breeding season to assign rams to ewes for optimal outcomes.

#### Syntax

```
/nsip:mating-plan <rams_file> <ewes_file> [--goal <breeding_goal>] [--max-inbreeding <pct>] [--max-uses <n>]
```

#### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `rams_file` | Yes | CSV with ram LPN IDs or comma-separated list |
| `ewes_file` | Yes | CSV with ewe LPN IDs or comma-separated list |
| `--goal` | No | Breeding goal: `terminal`, `maternal`, `balanced` (default: balanced) |
| `--max-inbreeding` | No | Maximum inbreeding percentage (default: 6.25) |
| `--max-uses` | No | Maximum times each ram can be assigned |

#### Breeding Goals

| Goal | Focus | Use Case |
|------|-------|----------|
| Terminal | PWWT, YEMD, YFAT | Producing market lambs |
| Maternal | NLW, MWWT, WWT | Breeding replacement ewes |
| Balanced | All traits equally weighted | General purpose |

#### Examples

**Basic mating plan:**
```
/nsip:mating-plan rams.csv ewes.csv
```

**Terminal focus with strict inbreeding limit:**
```
/nsip:mating-plan rams.csv ewes.csv --goal terminal --max-inbreeding 5.0
```

**Natural service with ram usage limits:**
```
/nsip:mating-plan rams.csv ewes.csv --max-uses 25
```

**Inline LPN IDs:**
```
/nsip:mating-plan RAM001,RAM002 EWE001,EWE002,EWE003
```

#### Expected Output

```
## Mating Plan

**Breeding Goal**: Terminal
**Max Inbreeding**: 5.0%
**Rams**: 3 | **Ewes**: 45

### Recommended Matings

| Rank | Ram              | Ewe              | Score | Inbreeding | Risk   |
|------|------------------|------------------|-------|------------|--------|
| 1    | 6402382023RAM001 | 6402382022EWE001 | 14.5  | 2.1%       | LOW    |
| 2    | 6402382023RAM001 | 6402382022EWE002 | 13.8  | 3.4%       | LOW    |
| 3    | 6402382023RAM002 | 6402382022EWE003 | 13.2  | 1.8%       | LOW    |
| 4    | 6402382023RAM001 | 6402382022EWE004 | 12.9  | 2.5%       | LOW    |
| ...  | ...              | ...              | ...   | ...        | ...    |

### Ram Usage Summary
| Ram              | Assigned Ewes | Avg Score | Avg Inbreeding |
|------------------|---------------|-----------|----------------|
| 6402382023RAM001 | 20            | 12.5      | 2.8%           |
| 6402382023RAM002 | 15            | 11.8      | 2.2%           |
| 6402382022RAM005 | 10            | 10.2      | 1.9%           |

### Unassigned Ewes
The following ewes could not be assigned within inbreeding constraints:
- 6402382021EWE045 (all rams exceed 5.0% inbreeding threshold)

### High-Risk Pairs (Flagged but Shown)
| Ram              | Ewe              | Inbreeding | Reason         |
|------------------|------------------|------------|----------------|
| 6402382023RAM001 | 6402382021EWE045 | 7.8%       | Exceeds limit  |

### Projected Flock Improvement
- **Expected PWWT gain**: +0.45 kg
- **Expected WWT gain**: +0.32 kg
- **Average offspring inbreeding**: 2.4%
```

---

### /nsip:trait-improvement

**Purpose:** Design a multi-generation selection strategy to reach specific trait targets, projecting timelines and selection intensity requirements.

**When to use:** For long-term genetic planning and setting realistic improvement goals.

#### Syntax

```
/nsip:trait-improvement <flock_file> --targets <json_targets> [--intensity <value>] [--max-generations <n>]
```

#### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `flock_file` | Yes | Spreadsheet with current flock LPN IDs |
| `--targets` | Yes | JSON dict of trait targets (e.g., `'{"WWT": 5.0, "NLW": 0.20}'`) |
| `--intensity` | No | Selection intensity (default: 1.4 = top 20%) |
| `--max-generations` | No | Maximum generations to project (default: 10) |

#### Selection Intensity Guide

| Intensity | Selection Rate | Description |
|-----------|----------------|-------------|
| 1.0 | ~50% retained | Low pressure, maintains diversity |
| 1.4 | ~20% retained | Balanced approach (recommended) |
| 1.76 | ~10% retained | Aggressive improvement |
| 2.0 | ~5% retained | Maximum pressure, use carefully |

#### Heritability Reference

| Trait | Heritability | Response to Selection |
|-------|--------------|----------------------|
| BWT | 0.30 | Moderate |
| WWT | 0.25 | Moderate |
| PWWT | 0.35 | Good |
| YWT | 0.40 | Good |
| YEMD | 0.35 | Good |
| NLB | 0.10 | Slow |
| NLW | 0.10 | Slow |
| MWWT | 0.15 | Slow |

#### Examples

**Basic improvement plan:**
```
/nsip:trait-improvement flock.csv --targets '{"WWT": 5.0, "PWWT": 8.0}'
```

**Aggressive selection for fertility:**
```
/nsip:trait-improvement flock.csv --targets '{"NLW": 0.25}' --intensity 1.76
```

**Long-term 15-generation projection:**
```
/nsip:trait-improvement flock.csv --targets '{"WWT": 7.0}' --max-generations 15
```

#### Expected Output

```
## Trait Improvement Plan

**Selection Intensity**: 1.4 (top 20%)
**Max Generations**: 10

### Current vs Target Analysis

| Trait | Current Mean | Target | Gap    | Heritability |
|-------|--------------|--------|--------|--------------|
| WWT   | 2.850        | 5.000  | +2.150 | 0.25         |
| PWWT  | 4.200        | 8.000  | +3.800 | 0.35         |
| NLW   | 0.085        | 0.200  | +0.115 | 0.10         |

### Improvement Projections

**WWT (Weaning Weight)**
- Heritability: 0.25
- Expected gain per generation: +0.320 kg
- Generations to target: 7
- Trajectory:
  - Gen 0: 2.850
  - Gen 1: 3.170
  - Gen 2: 3.490
  - Gen 3: 3.810
  - Gen 4: 4.130
  - Gen 5: 4.450
  - Gen 6: 4.770
  - Gen 7: 5.090 (TARGET REACHED)

**PWWT (Post-Weaning Weight)**
- Heritability: 0.35
- Expected gain per generation: +0.510 kg
- Generations to target: 8
- Trajectory:
  - Gen 0: 4.200
  - Gen 1: 4.710
  - ...
  - Gen 8: 8.280 (TARGET REACHED)

**NLW (Number Lambs Weaned)**
- Heritability: 0.10
- Expected gain per generation: +0.012 lambs
- Generations to target: 10 (may not reach target)
- Trajectory:
  - Gen 0: 0.085
  - Gen 1: 0.097
  - ...
  - Gen 10: 0.205 (NEAR TARGET)

### Recommendations

1. **WWT and PWWT**: Good response expected with standard selection
2. **NLW**: Low heritability means slow progress
   - Consider purchasing rams with proven NLW EBVs
   - Implement management practices to support lamb survival
   - Selection alone may take 10+ generations
3. **Selection Pressure**: Current intensity (1.4) is balanced
   - Increasing to 1.76 would accelerate progress by ~25%
   - Monitor inbreeding if using higher intensity
```

---

### /nsip:breeding-recs

**Purpose:** Generate AI-powered, comprehensive breeding recommendations including priority stock, cull candidates, and improvement strategies.

**When to use:** For holistic flock management decisions combining selection, culling, and strategic planning.

#### Syntax

```
/nsip:breeding-recs <flock_file> [--goal <breeding_goal>] [--philosophy <type>] [--json]
```

#### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `flock_file` | Yes | Spreadsheet with flock LPN IDs |
| `--goal` | No | Breeding goal: `terminal`, `maternal`, `balanced` (default: balanced) |
| `--philosophy` | No | Operation type: `commercial`, `seedstock`, `hobbyist` (default: commercial) |
| `--json` | No | Output as JSON |

#### Operation Philosophies

| Philosophy | Focus |
|------------|-------|
| Commercial | Proven genetics, low risk, practical recommendations |
| Seedstock | Comprehensive data, accuracy, genetic innovation |
| Hobbyist | Balanced, manageable, educational |

#### Examples

**Basic recommendations:**
```
/nsip:breeding-recs flock.csv
```

**Terminal focus for commercial operation:**
```
/nsip:breeding-recs flock.csv --goal terminal --philosophy commercial
```

**Seedstock breeder focus:**
```
/nsip:breeding-recs flock.csv --philosophy seedstock
```

#### Expected Output

```
## Breeding Recommendations

**Breeding Goal**: Terminal
**Philosophy**: Commercial
**Generated**: 2024-12-07

### Flock Summary
- **Total Animals**: 95
- **Males**: 8 (8.4%)
- **Females**: 87 (91.6%)
- **Average Terminal Index**: 8.45

### Priority Breeding Stock
These animals should receive premium mating opportunities:

| LPN ID           | Rank | Score | Key Strengths           |
|------------------|------|-------|-------------------------|
| 6402382024NCS310 | 1    | 15.2  | PWWT (99%), YEMD (95%) |
| 6402382023NCS215 | 2    | 14.8  | WWT (98%), PWWT (92%)  |
| 6402382023NCS218 | 3    | 14.1  | YEMD (97%), BWT (90%)  |

### Retain List (Top 25% - 24 animals)
Animals to keep in breeding program:
6402382024NCS310, 6402382023NCS215, 6402382023NCS218, 6402382022NCS105,
6402382024NCS312, 6402382023NCS220, ...

### Cull Candidates (Bottom 25% - 24 animals)
Animals to consider removing:
6402382020NCS102, 6402382020NCS108, 6402382019NCS095, 6402382021NCS042, ...

### Trait Improvement Priorities
These traits are below breed average and need focus:

| Trait | Flock Mean | Breed Avg | Gap    | Priority |
|-------|------------|-----------|--------|----------|
| NLW   | 0.085      | 0.120     | -0.035 | HIGH     |
| MWWT  | 1.200      | 1.450     | -0.250 | MEDIUM   |

### Detailed Recommendations

**Priority: 6402382024NCS310**
- *Rationale*: Top performer (Rank 1, Score 15.2)
- *Impact*: Maximize genetic contribution through premium matings
- *Action*: Assign to top 20% of ewes, maximize mating opportunities

**Priority: 6402382023NCS215**
- *Rationale*: Second-ranked performer (Score 14.8)
- *Impact*: Strong growth genetics
- *Action*: Primary sire for terminal lamb production

**Outside Genetics: NLW**
- *Rationale*: Flock average (0.085) below breed average (0.120)
- *Impact*: Limiting reproductive efficiency
- *Action*: Search for rams with NLW EBV > 0.15 for purchase

**Cull: 6402382020NCS102**
- *Rationale*: Bottom 5% performer (Score 2.1)
- *Impact*: Reducing flock genetic merit
- *Action*: Remove from breeding program

**Management: Ram:Ewe Ratio**
- *Rationale*: High ram percentage (8.4%)
- *Impact*: Inefficient resource allocation
- *Action*: Reduce ram numbers to 1:25-35 ratio
```

---

## Sire Evaluation

### /nsip:progeny-report

**Purpose:** Evaluate sires (or dams) by analyzing their offspring performance, providing direct evidence of genetic transmission.

**When to use:** To verify a sire's genetic merit based on actual progeny performance, compare multiple sires, or evaluate before purchasing proven sires.

#### Syntax

```
/nsip:progeny-report <sire_lpn> [--traits <trait_list>] [--compare <sire_lpn2,...>] [--index <index_name>]
```

#### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `sire_lpn` | Yes | Sire LPN ID to analyze |
| `--traits` | No | Comma-separated traits to focus on |
| `--compare` | No | Additional sire LPN IDs for comparison |
| `--index` | No | Selection index: `terminal`, `maternal`, `range` |

#### Examples

**Single sire analysis:**
```
/nsip:progeny-report 6402382020RAM001
```

**Focus on growth traits:**
```
/nsip:progeny-report 6402382020RAM001 --traits WWT,PWWT,YWT
```

**Compare multiple sires:**
```
/nsip:progeny-report 6402382020RAM001 --compare 6402382020RAM002,6402382019RAM005
```

**Rank by maternal index:**
```
/nsip:progeny-report 6402382020RAM001 --index maternal
```

#### Expected Output (Single Sire)

```
## Progeny Analysis: 6402382020RAM001

**Parent Gender**: Male
**Total Progeny**: 47
**Males**: 22 (47%) | **Females**: 25 (53%)

### Progeny Trait Averages
| Trait | Mean  | Std Dev | Consistency |
|-------|-------|---------|-------------|
| BWT   | 0.180 | 0.245   | Moderate    |
| WWT   | 3.450 | 0.892   | Good        |
| PWWT  | 5.120 | 1.234   | Moderate    |
| YEMD  | 0.820 | 0.156   | Good        |
| NLW   | 0.095 | 0.045   | Good        |

### Index Scores
- **Range Index Mean**: 12.5
- **Top Performer**: 6402382022NCS015 (Score: 16.2)

### Top 5 Offspring
| LPN ID           | Sex | DOB  | Score | Notable Traits |
|------------------|-----|------|-------|----------------|
| 6402382022NCS015 | F   | 2022 | 16.2  | PWWT, YEMD     |
| 6402382022NCS018 | M   | 2022 | 15.8  | WWT, PWWT      |
| 6402382023NCS102 | F   | 2023 | 15.1  | NLW, MWWT      |
| 6402382022NCS022 | F   | 2022 | 14.9  | YEMD, WWT      |
| 6402382023NCS108 | M   | 2023 | 14.5  | PWWT, YWT      |

### Interpretation
- **Strengths**: Consistent WWT and YEMD transmission
- **Weaknesses**: Higher BWT variation - monitor for lambing difficulty
- **Recommendation**: Proven sire for terminal production
```

#### Expected Output (Sire Comparison)

```
## Sire Comparison by Progeny Performance

### Overview
| Sire             | Total Progeny | Males | Females | Avg Index |
|------------------|---------------|-------|---------|-----------|
| 6402382020RAM001 | 47            | 22    | 25      | 12.5      |
| 6402382020RAM002 | 35            | 18    | 17      | 11.8      |
| 6402382019RAM005 | 62            | 28    | 34      | 10.9      |

### Progeny Trait Means
| Sire             | BWT   | WWT   | PWWT  | YEMD  | NLW   |
|------------------|-------|-------|-------|-------|-------|
| 6402382020RAM001 | 0.180 | 3.450 | 5.120 | 0.820 | 0.095 |
| 6402382020RAM002 | 0.220 | 3.150 | 4.850 | 0.780 | 0.112 |
| 6402382019RAM005 | 0.250 | 2.950 | 4.520 | 0.750 | 0.088 |

### Progeny Consistency (Std Dev)
| Sire             | BWT   | WWT   | PWWT  | YEMD  | NLW   |
|------------------|-------|-------|-------|-------|-------|
| 6402382020RAM001 | 0.245 | 0.892 | 1.234 | 0.156 | 0.045 |
| 6402382020RAM002 | 0.198 | 0.756 | 1.012 | 0.142 | 0.052 |
| 6402382019RAM005 | 0.312 | 1.023 | 1.456 | 0.189 | 0.038 |

### Rankings by Trait
- **BWT** (lower better): RAM001 > RAM002 > RAM005
- **WWT**: RAM001 > RAM002 > RAM005
- **PWWT**: RAM001 > RAM002 > RAM005
- **YEMD**: RAM001 > RAM002 > RAM005
- **NLW**: RAM002 > RAM001 > RAM005

### Overall Assessment

**Best Overall Sire**: 6402382020RAM001
- Highest progeny performance across most traits
- Good consistency (low variation)
- Strong recommendation for terminal production

**Alternative Choice**: 6402382020RAM002
- Better NLW transmission
- Most consistent offspring (lowest variation)
- Consider for maternal improvement

**Considerations for**: 6402382019RAM005
- Largest progeny count (proven)
- Highest variation - less predictable
- Lower average performance
```

---

## Example Workflows

### Workflow 1: "I have a spreadsheet of my flock, help me analyze it"

This workflow takes you from raw data to actionable insights.

```
# Step 1: Import and enrich your flock data
/nsip:flock-import my_flock.csv --output enriched_flock.csv --lineage

# Step 2: Generate flock overview and statistics
/nsip:flock-dashboard enriched_flock.csv --name "My Farm 2024"

# Step 3: Get comprehensive breeding recommendations
/nsip:breeding-recs enriched_flock.csv --goal terminal

# Step 4: Rank by your preferred selection index
/nsip:selection-index enriched_flock.csv --index terminal --top 20
```

### Workflow 2: "Compare these three rams for terminal traits"

Evaluating purchase candidates or selecting breeding rams.

```
# Step 1: Compare EBVs directly
/nsip:ebv-analyzer RAM_LPN1 RAM_LPN2 RAM_LPN3 --traits WWT,PWWT,YEMD,YFAT,BWT

# Step 2: Check progeny performance (for proven sires)
/nsip:progeny-report RAM_LPN1 --compare RAM_LPN2,RAM_LPN3 --index terminal

# Step 3: Review ancestry for each candidate
/nsip:ancestry RAM_LPN1 --generations 4
/nsip:ancestry RAM_LPN2 --generations 4
/nsip:ancestry RAM_LPN3 --generations 4

# Step 4: Check inbreeding with your ewes
/nsip:inbreeding RAM_LPN1 --mating YOUR_TOP_EWE
/nsip:inbreeding RAM_LPN2 --mating YOUR_TOP_EWE
/nsip:inbreeding RAM_LPN3 --mating YOUR_TOP_EWE
```

### Workflow 3: "Check if this mating will cause inbreeding"

Before finalizing breeding decisions.

```
# Check single mating
/nsip:inbreeding RAM_LPN --mating EWE_LPN

# If moderate/high risk, check alternatives
/nsip:inbreeding ALTERNATIVE_RAM --mating EWE_LPN

# Generate optimized mating plan for entire flock
/nsip:mating-plan rams.csv ewes.csv --max-inbreeding 5.0
```

### Workflow 4: "Plan a 5-year improvement strategy for growth"

Long-term genetic planning.

```
# Step 1: Establish baseline
/nsip:flock-dashboard flock.csv --name "Baseline 2024"

# Step 2: Define targets and project timeline
/nsip:trait-improvement flock.csv --targets '{"WWT": 5.0, "PWWT": 8.0}' --max-generations 10

# Step 3: Identify current top genetics to build on
/nsip:selection-index flock.csv --index terminal --top 10

# Step 4: Get recommendations including outside genetics needs
/nsip:breeding-recs flock.csv --goal terminal --philosophy seedstock

# Step 5: Search for rams to address trait gaps
# (Use NSIP website or /nsip:ebv-analyzer with candidate LPNs)
```

### Workflow 5: Annual Breeding Season Preparation

Complete preparation workflow.

```
# 1. Update flock data
/nsip:flock-import current_inventory.xlsx --output flock_2024.csv --lineage

# 2. Review flock status
/nsip:flock-dashboard flock_2024.csv --name "Farm 2024"

# 3. Get breeding recommendations
/nsip:breeding-recs flock_2024.csv --goal terminal

# 4. Separate rams and ewes for mating plan
# (Create rams.csv and ewes.csv from enriched data)

# 5. Generate optimized mating plan
/nsip:mating-plan rams.csv ewes.csv --goal terminal --max-inbreeding 5.0 --max-uses 25

# 6. Review any high-risk matings and adjust
```

---

## Quick Reference

### All Commands Summary

| Command | Purpose | Key Arguments |
|---------|---------|---------------|
| `/nsip:flock-import` | Import spreadsheet, enrich with NSIP data | `<file>`, `--lineage`, `--output` |
| `/nsip:flock-dashboard` | Flock statistics and overview | `<file>`, `--name`, `--compare-breed` |
| `/nsip:ebv-analyzer` | Compare traits across animals | `<lpn_ids...>`, `--traits` |
| `/nsip:selection-index` | Rank by selection index | `<file>`, `--index`, `--custom` |
| `/nsip:ancestry` | Generate pedigree reports | `<lpn_id>`, `--generations` |
| `/nsip:inbreeding` | Calculate inbreeding coefficients | `<lpn_id>`, `--mating` |
| `/nsip:mating-plan` | Optimize ram-ewe pairings | `<rams>`, `<ewes>`, `--goal` |
| `/nsip:trait-improvement` | Multi-generation planning | `<file>`, `--targets`, `--intensity` |
| `/nsip:breeding-recs` | AI-powered recommendations | `<file>`, `--goal`, `--philosophy` |
| `/nsip:progeny-report` | Sire evaluation by offspring | `<sire_lpn>`, `--compare` |

### Common Flags

| Flag | Description | Used By |
|------|-------------|---------|
| `--json` | Output as JSON | Most commands |
| `--traits` | Specify traits to analyze | ebv-analyzer, progeny-report |
| `--generations` | Pedigree depth | ancestry, inbreeding |
| `--goal` | terminal/maternal/balanced | mating-plan, breeding-recs |
| `--index` | Selection index to use | selection-index, progeny-report |

### Selection Index Presets

| Index | Key Traits | Best For |
|-------|------------|----------|
| `terminal` | PWWT+, YEMD+, BWT- | Market lamb production |
| `maternal` | NLW++, MWWT+, WWT+ | Replacement ewe selection |
| `range` | All balanced | General purpose |
| `hair` | Growth + NLW | Hair sheep breeds |

### Inbreeding Risk Levels

| Level | Coefficient | Action |
|-------|-------------|--------|
| LOW | < 6.25% | Acceptable |
| MODERATE | 6.25% - 12.5% | Consider alternatives |
| HIGH | > 12.5% | Avoid if possible |

---

## Additional Resources

- **Full Documentation**: `docs/nsip-skills.md` - Complete reference with core concepts
- **API Reference**: `docs/API_REFERENCE.md` - For programmatic usage
- **MCP Server**: `docs/mcp-server.md` - MCP tool documentation
- **Shepherd Agent**: `docs/shepherd-agent.md` - AI breeding advisor

---

*This document was created for Claude Code users working with NSIP sheep breeding data. For questions or feedback, see the project repository.*
