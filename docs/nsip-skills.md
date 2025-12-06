# NSIP Skills: Comprehensive Breeding Decision Support

This document provides detailed documentation for the NSIP Skills module, a suite of breeding decision support tools for sheep genetic improvement.

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Core Concepts](#core-concepts)
   - [Understanding EBVs](#understanding-ebvs)
   - [Selection Indexes](#selection-indexes)
   - [Inbreeding Coefficients](#inbreeding-coefficients)
   - [LPN IDs](#lpn-ids)
4. [The 10 NSIP Skills](#the-10-nsip-skills)
   - [Flock Import](#1-flock-import)
   - [EBV Analyzer](#2-ebv-analyzer)
   - [Inbreeding Calculator](#3-inbreeding-calculator)
   - [Mating Plan Optimizer](#4-mating-plan-optimizer)
   - [Progeny Report](#5-progeny-report)
   - [Trait Improvement Planner](#6-trait-improvement-planner)
   - [Ancestry Builder](#7-ancestry-builder)
   - [Flock Dashboard](#8-flock-dashboard)
   - [Selection Index Calculator](#9-selection-index-calculator)
   - [Breeding Recommendations](#10-breeding-recommendations)
5. [Common Workflows](#common-workflows)
6. [Data Formats](#data-formats)
7. [Troubleshooting](#troubleshooting)

---

## Introduction

### What is NSIP?

The **National Sheep Improvement Program (NSIP)** is a genetic evaluation program that calculates Estimated Breeding Values (EBVs) for sheep across the United States. EBVs predict the genetic merit an animal will pass to its offspring, enabling data-driven breeding decisions.

### What are NSIP Skills?

NSIP Skills is a collection of analysis tools that transform raw NSIP data into actionable breeding insights. These tools help breeders:

- **Evaluate** individual animals and compare candidates
- **Plan** matings that optimize genetic progress while managing inbreeding
- **Track** flock performance and identify improvement opportunities
- **Project** multi-generation genetic improvement trajectories

### Who Should Use NSIP Skills?

- **Commercial producers** seeking to improve lamb performance
- **Seedstock breeders** making selection and marketing decisions
- **New breeders** learning to use genetic data effectively
- **Consultants** advising multiple flocks

---

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Access to NSIP LPN IDs for your animals
- Basic familiarity with sheep breeding terminology

### Installation

```bash
# Install the package
pip install git+https://github.com/epicpast/nsip-api-client.git

# Or with uv
uv add git+https://github.com/epicpast/nsip-api-client.git
```

### Running Tools

All NSIP Skills can be run in two ways:

**1. As Python modules:**
```bash
uv run python -m nsip_skills.<module_name> [arguments]
```

**2. As Claude Code slash commands:**
```
/nsip:<command-name> [arguments]
```

### Your First Analysis

Start by importing your flock and generating a dashboard:

```bash
# Create a simple CSV with your LPN IDs
echo "lpn_id,local_tag" > my_flock.csv
echo "6402382024NCS310,Tag001" >> my_flock.csv
echo "6402382024NCS311,Tag002" >> my_flock.csv

# Import and enrich with NSIP data
uv run python -m nsip_skills.flock_import my_flock.csv

# Generate flock dashboard
uv run python -m nsip_skills.flock_stats enriched_my_flock.csv --name "My Flock"
```

---

## Core Concepts

### Understanding EBVs

**Estimated Breeding Values (EBVs)** predict the genetic merit an animal will transmit to its offspring. Unlike raw measurements, EBVs:

- Account for environmental effects (nutrition, management)
- Are expressed relative to a genetic base (typically breed average = 0)
- Can be compared across flocks and years
- Increase in accuracy as more data is collected

#### Key Traits

| Trait | Abbreviation | Units | Direction | Description |
|-------|--------------|-------|-----------|-------------|
| Birth Weight | BWT | kg | Lower better | Genetic effect on lamb birth weight. Lower values reduce dystocia risk. |
| Weaning Weight | WWT | kg | Higher better | Direct genetic effect on weight at weaning (~60 days). |
| Maternal Weaning Weight | MWWT | kg | Higher better | The dam's genetic influence on offspring weaning weight through milk/mothering. |
| Post-Weaning Weight | PWWT | kg | Higher better | Genetic effect on weight at ~150 days. Key growth indicator. |
| Yearling Weight | YWT | kg | Higher better | Genetic effect on weight at ~365 days. |
| Yearling Eye Muscle Depth | YEMD | mm | Higher better | Muscling indicator. Higher values = more meat. |
| Yearling Fat Depth | YFAT | mm | Context-dependent | Fat cover. Very low can reduce fertility; excessive reduces carcass value. |
| Number of Lambs Born | NLB | lambs | Higher better | Genetic effect on litter size at birth. |
| Number of Lambs Weaned | NLW | lambs | Higher better | Genetic effect on lambs raised to weaning. Combines fertility + survival. |

#### Trait Accuracy

Each EBV has an associated **accuracy** (0-100%) indicating reliability:

| Accuracy | Interpretation | Data Source |
|----------|----------------|-------------|
| <40% | Low - use with caution | Pedigree only |
| 40-70% | Moderate - reasonable confidence | Own performance + some progeny |
| >70% | High - reliable | Significant progeny data |

**Example interpretation:**
- BWT = -0.3 with 75% accuracy: This animal is genetically predicted to produce lambs 0.3 kg lighter than average, with high confidence.

### Selection Indexes

Selection indexes combine multiple traits into a single score, weighted by economic importance. This simplifies selection when multiple traits matter.

#### NSIP Preset Indexes

**Terminal Index** - For market lamb production:
```
Terminal Score = -0.5(BWT) + 1.0(WWT) + 1.5(PWWT) + 1.0(YWT) + 0.8(YEMD) - 0.3(YFAT)
```
Focus: Growth and carcass traits. Negative BWT weight favors lower birth weights for easier lambing.

**Maternal Index** - For replacement ewe selection:
```
Maternal Score = 2.0(NLB) + 2.5(NLW) + 1.5(MWWT) - 1.0(BWT) + 0.5(WWT)
```
Focus: Reproduction and mothering ability. Heavy weight on NLW (lambs weaned).

**Range Index** - For extensive operations:
```
Range Score = -0.5(BWT) + 1.0(WWT) + 1.0(PWWT) + 1.5(NLW) + 1.0(MWWT)
```
Focus: Balanced production suitable for range/pastoral systems.

**Hair Index** - For hair sheep breeds:
```
Hair Score = -0.5(BWT) + 1.2(WWT) + 1.5(PWWT) + 1.5(NLB) + 2.0(NLW) - 0.5(DAG)
```
Focus: Growth and reproduction without wool traits.

#### Custom Indexes

Create indexes tailored to your operation:

```bash
# Custom commercial index emphasizing growth and fertility
uv run python -m nsip_skills.selection_index flock.csv \
    --custom '{"WWT": 1.5, "PWWT": 1.0, "NLW": 2.0, "BWT": -0.5}'
```

### Inbreeding Coefficients

The **inbreeding coefficient (F or COI)** measures the probability that an animal inherits two copies of the same allele from a common ancestor. It's calculated using Wright's path coefficient method:

```
F = sum[(1/2)^(n1+n2+1) x (1 + FA)]
```

Where:
- n1 = generations from subject to common ancestor via sire
- n2 = generations from subject to common ancestor via dam
- FA = inbreeding coefficient of the common ancestor

#### Risk Thresholds

| COI Range | Risk Level | Interpretation |
|-----------|------------|----------------|
| <6.25% | Low | Generally acceptable. Equivalent to mating half-siblings or closer relatives avoided. |
| 6.25-12.5% | Moderate | Warrants attention. Consider alternative matings if available. |
| >12.5% | High | Avoid if possible. Increased risk of inbreeding depression. |

#### Inbreeding Depression

High inbreeding can reduce:
- Fertility and conception rates
- Lamb survival
- Growth rates
- Disease resistance
- Overall vigor

### LPN IDs

**LPN (Lot-Prefix-Number) IDs** uniquely identify animals in NSIP. Format example: `6402382024NCS310`

Components:
- Flock code prefix (assigned by NSIP)
- Year of birth
- Individual animal number

Always use the complete LPN ID when querying NSIP tools.

---

## The 10 NSIP Skills

### 1. Flock Import

**Purpose:** Import your flock data from spreadsheets and enrich it with NSIP breeding values.

**Why it matters:** Most breeders track their flock in spreadsheets with local tag numbers. This tool bridges your records to NSIP's genetic data, creating a unified dataset for analysis.

#### Usage

```bash
# Basic import from CSV
uv run python -m nsip_skills.flock_import my_flock.csv

# With custom output location
uv run python -m nsip_skills.flock_import my_flock.xlsx --output enriched_flock.xlsx

# Include pedigree information
uv run python -m nsip_skills.flock_import my_flock.csv --lineage
```

#### Claude Code Command
```
/nsip:flock-import my_flock.csv --output enriched_flock.csv
```

#### Input Format

Your spreadsheet must have a column for LPN IDs. Acceptable column names:
- `LPN_ID`, `lpn_id`, `LPN`, `lpn`

Optional columns preserved in output:
- `Name`, `name` - Your local name for the animal
- `Tag`, `tag` - Ear tag or other identifier
- `Notes`, `notes` - Any notes
- `Group`, `group` - Breeding group or pen

**Example input (CSV):**
```csv
lpn_id,tag,notes,group
6402382024NCS310,Blue-123,Best ewe,Breeding Ewes
6402382024NCS311,Blue-124,Good mother,Breeding Ewes
6402382024NCS312,Blue-125,,Replacement Ewes
```

#### Output

The enriched spreadsheet adds columns for:
- Breed, gender, date of birth, status
- Sire LPN, Dam LPN
- All available EBV traits with accuracy values
- Validation status

**Example output columns:**
```
lpn_id, tag, notes, group, breed, gender, date_of_birth, status,
sire, dam, progeny_count, BWT, BWT_acc, WWT, WWT_acc, PWWT, PWWT_acc, ...
```

#### Validation Report

The tool generates a validation report showing:
- Successfully fetched animals
- Animals not found in NSIP (check LPN ID accuracy)
- API errors encountered

---

### 2. EBV Analyzer

**Purpose:** Compare and analyze EBV traits across multiple animals.

**Why it matters:** When evaluating purchase candidates or selecting breeding stock, you need to compare animals side-by-side. This tool calculates percentile rankings and identifies each animal's genetic strengths and weaknesses.

#### Usage

```bash
# Compare specific animals
uv run python -m nsip_skills.ebv_analysis LPN1 LPN2 LPN3

# Focus on specific traits
uv run python -m nsip_skills.ebv_analysis LPN1 LPN2 --traits WWT PWWT NLW

# With breed context for percentiles
uv run python -m nsip_skills.ebv_analysis LPN1 LPN2 --breed 486
```

#### Claude Code Command
```
/nsip:ebv-analyzer LPN1 LPN2 LPN3 --traits BWT,WWT,PWWT,NLW
```

#### Output

**Trait Statistics:**
```
| Trait | Mean  | Std Dev | Min   | Max   | Count |
|-------|-------|---------|-------|-------|-------|
| BWT   | 0.245 | 0.312   | -0.15 | 0.55  | 3     |
| WWT   | 2.850 | 0.923   | 1.85  | 3.95  | 3     |
```

**Animal Comparison:**
```
| Animal          | BWT         | WWT         | PWWT        |
|-----------------|-------------|-------------|-------------|
| 6402382024NCS310| 0.25 (50%)  | 3.95 (95%)  | 5.20 (80%)  |
| 6402382024NCS311| -0.15 (90%) | 1.85 (15%)  | 4.10 (45%)  |
```

**Strength/Weakness Analysis:**
- **Top Performers** (most traits in top 25%): Lists animals with the most strengths
- **Needs Improvement** (most traits in bottom 25%): Lists animals with weaknesses
- **Rankings by Trait**: Shows best-to-worst order for each trait

#### Interpreting Results

- **Percentiles** show position within the comparison group (higher = better for most traits)
- **Strengths** are traits where the animal ranks in the top 25%
- **Weaknesses** are traits in the bottom 25%

**Note:** For BWT and fat traits, lower values are often preferable. The tool handles this automatically in rankings.

---

### 3. Inbreeding Calculator

**Purpose:** Calculate inbreeding coefficients using pedigree data.

**Why it matters:** Inbreeding depression can reduce performance and increase health problems. Before making breeding decisions, you should know the inbreeding level of existing animals and project inbreeding for proposed matings.

#### Usage

```bash
# Analyze single animal's inbreeding
uv run python -m nsip_skills.inbreeding 6402382024NCS310

# Extended pedigree analysis (5 generations)
uv run python -m nsip_skills.inbreeding 6402382024NCS310 --generations 5

# Project offspring inbreeding for a proposed mating
uv run python -m nsip_skills.inbreeding SIRE_LPN --mating DAM_LPN
```

#### Claude Code Command
```
/nsip:inbreeding 6402382024NCS310 --generations 4
/nsip:inbreeding --mating SIRE_LPN,DAM_LPN
```

#### Output

**Inbreeding Analysis:**
```
## Inbreeding Analysis: 6402382024NCS310

**Coefficient**: 3.12%
**Risk Level**: LOW
**Generations Analyzed**: 4

### Common Ancestors
- 6402382019ABC123: 1.56% contribution
- 6402382018DEF456: 1.56% contribution

### Pedigree
- Sire: 6402382021XYZ001
- Dam: 6402382020XYZ002
- Sire's Sire: 6402382019ABC123
- Sire's Dam: 6402382019ABC124
- Dam's Sire: 6402382018DEF456
- Dam's Dam: 6402382018DEF457
```

#### Mating Projection

When using `--mating`, the tool creates a virtual offspring pedigree:

```
## Projected Offspring Inbreeding: SIRE x DAM

**Projected Coefficient**: 6.25%
**Risk Level**: MODERATE
**Recommendation**: Proceed with caution - consider alternatives if available
```

---

### 4. Mating Plan Optimizer

**Purpose:** Generate optimized ram-ewe pairings for your breeding season.

**Why it matters:** Manually matching rams to ewes while considering EBVs, inbreeding, and breeding goals is time-consuming and error-prone. This tool automates the optimization to maximize genetic progress while respecting inbreeding constraints.

#### Usage

```bash
# Basic mating plan
uv run python -m nsip_skills.mating_optimizer --rams rams.csv --ewes ewes.csv

# Terminal focus with inbreeding limit
uv run python -m nsip_skills.mating_optimizer --rams rams.csv --ewes ewes.csv \
    --goal terminal --max-inbreeding 5.0

# Limit ram usage (for natural service)
uv run python -m nsip_skills.mating_optimizer --rams rams.csv --ewes ewes.csv \
    --max-per-ram 25
```

#### Claude Code Command
```
/nsip:mating-plan rams.csv ewes.csv --goal terminal --max-inbreeding 6.25
```

#### Input Format

Ram and ewe files should be CSVs with an `lpn_id` column:
```csv
lpn_id,local_tag
6402382023RAM001,Ram-Blue
6402382023RAM002,Ram-Red
```

Or provide LPN IDs directly:
```bash
uv run python -m nsip_skills.mating_optimizer \
    --rams RAM_LPN1 RAM_LPN2 \
    --ewes EWE_LPN1 EWE_LPN2 EWE_LPN3
```

#### Output

**Recommended Matings:**
```
| Rank | Ram              | Ewe              | Score | Inbreeding | Risk   |
|------|------------------|------------------|-------|------------|--------|
| 1    | 6402382023RAM001 | 6402382022EWE001 | 12.5  | 2.1%       | low    |
| 2    | 6402382023RAM001 | 6402382022EWE002 | 11.8  | 3.4%       | low    |
| 3    | 6402382023RAM002 | 6402382022EWE003 | 10.2  | 1.8%       | low    |
```

**Additional information:**
- **Unassigned ewes**: Ewes that couldn't be matched within inbreeding constraints
- **High-risk pairs**: Matings that exceed the inbreeding threshold (flagged but shown)
- **Projected offspring EBVs**: Expected trait values for each pairing

#### Breeding Goals

| Goal | Optimization Focus |
|------|-------------------|
| `terminal` | Maximize growth and carcass traits |
| `maternal` | Maximize reproduction and mothering |
| `balanced` | Weight all traits equally |

---

### 5. Progeny Report

**Purpose:** Evaluate sires (or dams) by analyzing their offspring performance.

**Why it matters:** An animal's own EBVs predict genetic merit, but **progeny testing** provides direct evidence of what genetics they actually transmit. This is especially valuable for sires with many offspring.

#### Usage

```bash
# Single sire analysis
uv run python -m nsip_skills.progeny_analysis SIRE_LPN

# Focus on growth traits
uv run python -m nsip_skills.progeny_analysis SIRE_LPN --traits WWT PWWT YWT

# Compare multiple sires
uv run python -m nsip_skills.progeny_analysis SIRE1 SIRE2 SIRE3
```

#### Claude Code Command
```
/nsip:progeny-report SIRE_LPN --traits WWT,PWWT,NLW
/nsip:progeny-report SIRE1 --compare SIRE2,SIRE3
```

#### Output

**Single Sire Analysis:**
```
## Progeny Analysis: 6402382020RAM001

**Parent Gender**: Male
**Total Progeny**: 47
**Males**: 22 | **Females**: 25

### Trait Averages
| Trait | Mean  | Std Dev |
|-------|-------|---------|
| BWT   | 0.180 | 0.245   |
| WWT   | 3.450 | 0.892   |
| PWWT  | 5.120 | 1.234   |

**Top Performers**: LPN001, LPN002, LPN003, LPN004, LPN005
```

**Sire Comparison:**
```
## Sire Comparison by Progeny Performance

| Sire             | Total Progeny | Males | Females |
|------------------|---------------|-------|---------|
| 6402382020RAM001 | 47            | 22    | 25      |
| 6402382020RAM002 | 35            | 18    | 17      |

### Progeny Trait Means
| Sire             | BWT   | WWT   | PWWT  | NLW   |
|------------------|-------|-------|-------|-------|
| 6402382020RAM001 | 0.180 | 3.450 | 5.120 | 0.095 |
| 6402382020RAM002 | 0.220 | 3.150 | 4.850 | 0.112 |

### Rankings by Trait
- **WWT**: 6402382020RAM001 > 6402382020RAM002
- **PWWT**: 6402382020RAM001 > 6402382020RAM002
- **NLW**: 6402382020RAM002 > 6402382020RAM001

**Best Overall Sire**: 6402382020RAM001
```

#### Interpreting Progeny Data

- **Progeny count** affects reliability - more offspring = more confidence
- **Consistency** (low standard deviation) indicates the sire "breeds true"
- **Top performers** may indicate heterosis or exceptional genetic combinations

---

### 6. Trait Improvement Planner

**Purpose:** Design multi-generation selection strategies to reach specific trait targets.

**Why it matters:** Genetic improvement takes time. This tool projects how many generations are needed to reach your goals and identifies which traits respond fastest to selection.

#### Usage

```bash
# Basic improvement plan
uv run python -m nsip_skills.trait_planner flock.csv \
    --targets '{"WWT": 5.0, "PWWT": 8.0}'

# Aggressive selection (top 10%)
uv run python -m nsip_skills.trait_planner flock.csv \
    --targets '{"NLW": 0.25}' --intensity 1.76
```

#### Claude Code Command
```
/nsip:trait-improvement flock.csv --targets '{"WWT": 5.0, "NLW": 0.20}' --intensity 1.4
```

#### Selection Intensity

| Intensity | Selection Rate | Use Case |
|-----------|----------------|----------|
| 1.0 | ~50% retained | Large flock, modest pressure |
| 1.4 | ~20% retained | Balanced approach (default) |
| 1.76 | ~10% retained | Aggressive improvement |
| 2.0 | ~5% retained | Maximum pressure |

**Warning:** Higher selection intensity accelerates improvement but increases inbreeding risk and reduces selection candidates.

#### Output

**Goals Summary:**
```
| Trait | Current | Target | Gap    |
|-------|---------|--------|--------|
| WWT   | 2.850   | 5.000  | +2.150 |
| PWWT  | 4.200   | 8.000  | +3.800 |
| NLW   | 0.085   | 0.200  | +0.115 |
```

**Projections:**
```
**WWT**
- Heritability: 0.25
- Gain/generation: +0.320
- Generations to target: 7
- Trajectory: Gen0: 2.850 -> Gen1: 3.170 -> Gen2: 3.490 -> ...

**NLW**
- Heritability: 0.10
- Gain/generation: +0.012
- Generations to target: 10
- Trajectory: Gen0: 0.085 -> Gen1: 0.097 -> Gen2: 0.109 -> ...
```

**Recommendations:**
- Traits with low heritability (NLW, MWWT) respond slowly - consider complementary management practices
- Consider outside genetics for traits with the largest gaps

#### Understanding Heritability

| Heritability | Response to Selection |
|--------------|----------------------|
| <0.15 | Slow - heavily influenced by environment |
| 0.15-0.30 | Moderate - genetic and environmental |
| >0.30 | Good - strongly genetic |

---

### 7. Ancestry Builder

**Purpose:** Generate comprehensive pedigree reports and visualizations.

**Why it matters:** Understanding an animal's genetic background helps explain its traits, identify potential inbreeding paths, and discover notable ancestors.

#### Usage

```bash
# Basic pedigree (4 generations)
uv run python -m nsip_skills.ancestry_builder 6402382024NCS310

# Extended ancestry
uv run python -m nsip_skills.ancestry_builder 6402382024NCS310 --generations 5

# Different output styles
uv run python -m nsip_skills.ancestry_builder 6402382024NCS310 --style markdown
```

#### Claude Code Command
```
/nsip:ancestry 6402382024NCS310 --generations 4 --style ascii
```

#### Output

**ASCII Pedigree Tree:**
```
                         2024NCS310 (F)
                        /              \
              2021XYZ001 (M)          2020XYZ002 (F)
              /         \          /         \
       2019ABC123  2019ABC124  2018DEF456  2018DEF457
```

**Detailed Ancestry:**
```
**Subject**: 6402382024NCS310 (F) b.2024 - Valley Farm

**Parents**:
  - Sire: 6402382021XYZ001 (M) b.2021 - Valley Farm
  - Dam:  6402382020XYZ002 (F) b.2020 - Valley Farm

**Grandparents**:
  - Sire's Sire: 6402382019ABC123 (M) b.2019 - Mountain View
  - Sire's Dam:  6402382019ABC124 (F) b.2019 - Valley Farm
  - Dam's Sire:  6402382018DEF456 (M) b.2018 - Hilltop Ranch
  - Dam's Dam:   6402382018DEF457 (F) b.2018 - Valley Farm

**Common Ancestors**: 6402382017GGG001
```

**Bloodline Breakdown:**
```
- Sire's Sire (6402382019ABC123): 25.0%
- Sire's Dam (6402382019ABC124): 25.0%
- Dam's Sire (6402382018DEF456): 25.0%
- Dam's Dam (6402382018DEF457): 25.0%
```

**Genetic Diversity Score:** 0.92 (Lower indicates repeated ancestors)

**Notable Ancestors:**
- Animals with high progeny counts (proven genetics)
- Animals with high index scores

---

### 8. Flock Dashboard

**Purpose:** Calculate aggregate statistics and generate a comprehensive flock performance overview.

**Why it matters:** Individual animal analysis is important, but understanding your flock as a whole reveals systematic strengths, weaknesses, and opportunities.

#### Usage

```bash
# Basic dashboard
uv run python -m nsip_skills.flock_stats flock.csv

# Named flock with breed comparison
uv run python -m nsip_skills.flock_stats flock.csv \
    --name "Valley Farm" --compare-breed 486
```

#### Claude Code Command
```
/nsip:flock-dashboard flock.csv --name "Valley Farm"
```

#### Output

**Flock Summary:**
```
## Flock Dashboard

**Flock**: Valley Farm
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
```

**Trait Summary:**
```
| Trait | Mean  | Median | Min   | Max   |
|-------|-------|--------|-------|-------|
| BWT   | 0.245 | 0.220  | -0.35 | 0.85  |
| WWT   | 2.950 | 2.880  | 0.50  | 5.20  |
| PWWT  | 4.350 | 4.200  | 1.20  | 7.80  |
| NLW   | 0.092 | 0.085  | -0.05 | 0.25  |
```

**Selection Index Rankings:**

Top 5 by Terminal Index:
1. 6402382024NCS310: 15.2
2. 6402382023NCS215: 14.8
3. ...

**Improvement Opportunities:**
- High variability in PWWT (CV=45%). Opportunity to standardize through selection.
- Below breed average on: NLW. Consider rams with strong NLW performance.
- Low proportion of young animals. Consider retaining more replacements.

---

### 9. Selection Index Calculator

**Purpose:** Calculate and rank animals by composite selection index scores.

**Why it matters:** When selecting breeding stock, you rarely optimize for a single trait. Selection indexes provide a single number that balances multiple economically important traits.

#### Usage

```bash
# Use preset terminal index
uv run python -m nsip_skills.selection_index flock.csv --index terminal

# Custom commercial index
uv run python -m nsip_skills.selection_index flock.csv \
    --index 'custom:{"WWT": 1.5, "PWWT": 1.0, "NLW": 2.0, "BWT": -0.5}'

# Show top 10 only
uv run python -m nsip_skills.selection_index flock.csv --index maternal --top 10

# List available presets
uv run python -m nsip_skills.selection_index --list-presets
```

#### Claude Code Command
```
/nsip:selection-index flock.csv --index terminal --top 20
/nsip:selection-index --list-presets
```

#### Output

**Index Rankings:**
```
## Terminal Index Rankings

*Emphasizes growth and carcass traits for meat production*

### Summary Statistics
- Animals ranked: 95
- Mean score: 8.45
- Std deviation: 3.21
- Top 10% threshold: 13.20
- Top 25% threshold: 10.85

### Index Weights
- BWT: -0.5
- WWT: +1.0
- PWWT: +1.5
- YWT: +1.0
- YEMD: +0.8
- YFAT: -0.3

### Rankings
| Rank | LPN ID           | Score | BWT   | WWT  | PWWT | YEMD | YFAT |
|------|------------------|-------|-------|------|------|------|------|
| 1    | 6402382024NCS310 | 15.20 | -0.38 | 4.20 | 6.80 | 0.85 | -0.2 |
| 2    | 6402382023NCS215 | 14.80 | -0.15 | 3.95 | 6.50 | 0.92 | -0.1 |
```

#### Custom Index Tips

- **Positive weights** favor higher EBV values
- **Negative weights** favor lower values (e.g., BWT: -0.5 prefers lighter birth weights)
- **Magnitude** reflects relative importance (2.0 vs 1.0 = twice as important)
- Start with a preset index and adjust based on your economic priorities

---

### 10. Breeding Recommendations

**Purpose:** Generate AI-powered, comprehensive breeding recommendations for your flock.

**Why it matters:** This tool synthesizes all the analyses into actionable recommendations: which animals to prioritize, which to cull, and what traits need attention.

#### Usage

```bash
# Basic recommendations
uv run python -m nsip_skills.recommendation_engine flock.csv

# Terminal focus for commercial operation
uv run python -m nsip_skills.recommendation_engine flock.csv \
    --goal terminal --philosophy commercial

# Seedstock breeder focus
uv run python -m nsip_skills.recommendation_engine flock.csv \
    --philosophy seedstock
```

#### Claude Code Command
```
/nsip:breeding-recs flock.csv --goal terminal --philosophy commercial
```

#### Operation Philosophies

| Philosophy | Focus |
|------------|-------|
| `commercial` | Proven genetics, low risk, practical recommendations |
| `seedstock` | Comprehensive data, accuracy, genetic innovation |
| `hobbyist` | Balanced, manageable, educational |

#### Output

**Flock Summary:**
```
## Breeding Recommendations
*Breeding Goal: Terminal*

### Flock Summary
- Total animals: 95
- Males: 8
- Females: 87
```

**Priority Breeding Stock:**
```
### Priority Breeding Stock
These animals should receive premium mating opportunities:
- **6402382024NCS310**
- **6402382023NCS215**
- **6402382023NCS218**
```

**Retain and Cull Lists:**
```
### Retain (24 animals)
Top performers to keep in breeding program: 6402382024NCS310, 6402382023NCS215, ...

### Cull Candidates (24 animals)
Bottom performers to remove: 6402382020NCS102, 6402382020NCS108, ...
```

**Trait Improvement Priorities:**
```
### Trait Improvement Priorities
1. **NLW** - Focus selection pressure here
2. **MWWT** - Focus selection pressure here
```

**Detailed Recommendations:**
```
### All Recommendations

**Priority: 6402382024NCS310**
- *Rationale*: Top performer (Rank 1, Score 15.2)
- *Impact*: Maximize genetic contribution through premium matings
- *Action*: Assign to top ewes, maximize mating opportunities

**Outside Genetics: NLW**
- *Rationale*: Flock average (-0.02) below breed average
- *Impact*: Improve NLW through selection or outside genetics
- *Action*: Search for rams with strong NLW EBVs

**Management: Ram:Ewe Ratio**
- *Rationale*: High ram percentage (8.4%)
- *Impact*: Reduce costs, focus resources on top rams
- *Action*: Reduce ram numbers to 1:25-35 ratio with ewes
```

---

## Common Workflows

### Workflow 1: Annual Breeding Season Preparation

```bash
# 1. Update flock data from latest spreadsheet
uv run python -m nsip_skills.flock_import current_flock.xlsx --output flock_2024.csv

# 2. Generate flock dashboard to understand current state
uv run python -m nsip_skills.flock_stats flock_2024.csv --name "Valley Farm 2024"

# 3. Get breeding recommendations
uv run python -m nsip_skills.recommendation_engine flock_2024.csv --goal terminal

# 4. Generate mating plan for breeding season
uv run python -m nsip_skills.mating_optimizer \
    --rams rams_2024.csv --ewes ewes_2024.csv \
    --goal terminal --max-inbreeding 5.0
```

### Workflow 2: Ram Purchase Decision

```bash
# 1. Compare candidate rams
uv run python -m nsip_skills.ebv_analysis \
    CANDIDATE_RAM_1 CANDIDATE_RAM_2 CANDIDATE_RAM_3

# 2. Check progeny performance (for proven sires)
uv run python -m nsip_skills.progeny_analysis CANDIDATE_RAM_1 \
    --compare CANDIDATE_RAM_2,CANDIDATE_RAM_3

# 3. Check inbreeding with your ewes
uv run python -m nsip_skills.inbreeding --mating CANDIDATE_RAM_1,YOUR_EWE_1
uv run python -m nsip_skills.inbreeding --mating CANDIDATE_RAM_1,YOUR_EWE_2

# 4. Review ancestry
uv run python -m nsip_skills.ancestry_builder CANDIDATE_RAM_1 --generations 4
```

### Workflow 3: Long-term Genetic Planning

```bash
# 1. Analyze current flock baseline
uv run python -m nsip_skills.flock_stats flock.csv --name "Baseline 2024"

# 2. Define improvement targets and timeline
uv run python -m nsip_skills.trait_planner flock.csv \
    --targets '{"WWT": 5.0, "NLW": 0.20, "BWT": -0.2}' \
    --intensity 1.4

# 3. Identify best current genetics to build on
uv run python -m nsip_skills.selection_index flock.csv --index maternal --top 10
```

---

## Data Formats

### Input Spreadsheets

**Supported formats:**
- CSV (.csv)
- Excel (.xlsx)
- Google Sheets URL

**Required column:**
- `lpn_id` (or `LPN_ID`, `LPN`, `lpn`)

**Optional columns preserved:**
- `name`, `tag`, `notes`, `group`

### Output Formats

**Default:** Human-readable markdown tables

**JSON output:** Add `--json` flag to any command for machine-readable output:
```bash
uv run python -m nsip_skills.flock_stats flock.csv --json > flock_stats.json
```

---

## Troubleshooting

### Common Issues

**"Animal not found in NSIP"**
- Verify the LPN ID is complete and correct
- Check for typos or transposed characters
- The animal may not be enrolled in NSIP

**"No trait data available"**
- The animal may be too young for EBVs
- Performance records may not have been submitted
- Check if the animal's flock participates in NSIP

**Slow API responses**
- The NSIP API can be slow during peak times
- Consider using batch operations for large flocks
- Results are cached for 1 hour to improve performance

**Unexpected inbreeding results**
- Inbreeding calculation depends on pedigree completeness
- Unknown ancestors are treated as unrelated
- Consider increasing `--generations` for more accurate analysis

### Getting Help

1. Check the command help: `uv run python -m nsip_skills.<module> --help`
2. Review the examples in this documentation
3. Examine the JSON output for detailed error information
4. Verify your LPN IDs against the NSIP website

---

## Technical Reference

### Module Architecture

```
nsip_skills/
├── common/
│   ├── data_models.py    # Shared dataclasses
│   ├── formatters.py     # Output formatting
│   ├── nsip_wrapper.py   # Cached API client
│   └── spreadsheet_io.py # File I/O
├── ancestry_builder.py   # /nsip:ancestry
├── ebv_analysis.py       # /nsip:ebv-analyzer
├── flock_import.py       # /nsip:flock-import
├── flock_stats.py        # /nsip:flock-dashboard
├── inbreeding.py         # /nsip:inbreeding
├── mating_optimizer.py   # /nsip:mating-plan
├── progeny_analysis.py   # /nsip:progeny-report
├── recommendation_engine.py  # /nsip:breeding-recs
├── selection_index.py    # /nsip:selection-index
└── trait_planner.py      # /nsip:trait-improvement
```

### API Caching

All NSIP API calls are cached for 1 hour to reduce load and improve performance. The cache is automatically managed and requires no user configuration.

### Trait Heritabilities (Defaults)

| Trait | Heritability |
|-------|--------------|
| BWT | 0.30 |
| WWT | 0.25 |
| PWWT | 0.35 |
| YWT | 0.40 |
| YEMD | 0.35 |
| YFAT | 0.30 |
| NLB | 0.10 |
| NLW | 0.10 |
| MWWT | 0.15 |
| FEC | 0.25 |

These values are used for genetic gain projections and may vary by breed.

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and updates.

## License

This software is provided as-is for educational and research purposes. NSIP data remains the property of the National Sheep Improvement Program.
