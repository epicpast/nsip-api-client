# NSIP MCP Tools - Example Prompts Guide

This guide provides copy-paste prompts for using the 15 NSIP MCP tools with Claude Desktop or any MCP-compatible AI assistant. Each section includes practical examples, expected responses, and common use cases for sheep breeders and farmers.

---

## Table of Contents

1. [Introduction](#introduction)
2. [Basic Discovery Prompts](#basic-discovery-prompts)
3. [Animal Search Prompts](#animal-search-prompts)
4. [Pedigree and Genetics Prompts](#pedigree-and-genetics-prompts)
5. [Shepherd Consultation Prompts](#shepherd-consultation-prompts)
6. [Advanced Multi-Tool Workflows](#advanced-multi-tool-workflows)

---

## Introduction

### What Are NSIP MCP Tools?

The NSIP MCP tools provide AI assistants with direct access to the National Sheep Improvement Program (NSIP) database. This database contains:

- **Genetic data (EBVs)** - Estimated Breeding Values for growth, carcass, wool, and reproduction traits
- **Pedigree information** - Sire, dam, and multi-generational ancestry
- **Progeny records** - Offspring lists and performance data
- **Breeder contacts** - Farm information for registered animals

### When to Use These Tools

| Scenario | Recommended Tools |
|----------|-------------------|
| "What breeds are in NSIP?" | `nsip_list_breeds` |
| "Find rams with high weaning weight" | `nsip_search_animals` |
| "Tell me about sheep ABC123" | `nsip_get_animal` or `nsip_search_by_lpn` |
| "Show the pedigree of this animal" | `nsip_get_lineage` |
| "What offspring does this ram have?" | `nsip_get_progeny` |
| "How do I interpret these EBVs?" | `shepherd_breeding` |
| "What deworming schedule should I use?" | `shepherd_health` |
| "When should I start breeding season?" | `shepherd_calendar` |
| "Is this ram worth the price?" | `shepherd_economics` |

### Tool Categories

**NSIP API Tools (10)** - Query the NSIP database for animal and breeding data

**Shepherd Consultation Tools (5)** - Get expert advice on breeding, health, calendar, and economics

---

## Basic Discovery Prompts

These prompts help you understand what data is available in the NSIP database before diving into specific searches.

### 1. Check Database Freshness

**Prompt:**
```
When was the NSIP database last updated?
```

**What it does:** Calls `nsip_get_last_update` to verify you are working with current data.

**Expected response:**
```
The NSIP database was last updated on 12/15/2024.
```

**Use case:** Before making important breeding decisions, verify the data is recent.

---

### 2. List Available Breed Groups

**Prompt:**
```
What sheep breeds are available in the NSIP database?
```

**What it does:** Calls `nsip_list_breeds` to retrieve all breed groups and their individual breeds.

**Expected response:**
```
The NSIP database contains 4 breed groups with the following breeds:

**Range (ID: 61)**
- South African Meat Merino (ID: 486)
- Targhee (ID: 610)
- Rambouillet (ID: 612)

**Maternal Wool (ID: 62)**
- Columbia (ID: 620)
- Polypay (ID: 621)
- Finnsheep (ID: 622)

**Hair (ID: 64)**
- Katahdin (ID: 640)
- Dorper (ID: 641)
- St. Croix (ID: 642)
- White Dorper (ID: 643)

**Terminal (ID: 69)**
- Suffolk (ID: 690)
- Hampshire (ID: 691)
- Texel (ID: 692)
- Shropshire (ID: 693)
```

**Use cases:**
- Identify the correct breed ID before searching
- Understand which breed groups are tracked by NSIP
- Find breed IDs for trait range queries

---

### 3. Get Animal Status Options

**Prompt:**
```
What status values can animals have in NSIP?
```

**What it does:** Calls `nsip_get_statuses` to list all possible animal statuses.

**Expected response:**
```
Animals in NSIP can have these statuses:
- CURRENT - Active in the flock
- SOLD - Transferred to another owner
- DEAD - Deceased
- COMMERCIAL - Sold to commercial operation
- CULL - Removed from breeding program
- EXPORTED - Sold internationally
```

**Use case:** Filter searches to find only active breeding stock by understanding status values.

---

### 4. Explore Trait Ranges for a Breed

**Prompt:**
```
What are the trait value ranges for Katahdin sheep?
```

**What it does:** Calls `nsip_get_trait_ranges` with the Katahdin breed ID (640).

**Expected response:**
```
Trait ranges for Katahdin sheep (Breed ID: 640):

**Growth Traits**
| Trait | Min | Max | Description |
|-------|-----|-----|-------------|
| BWT | -0.71 | 0.96 | Birth Weight (lbs) |
| WWT | -5.2 | 8.4 | Weaning Weight (lbs) |
| MWWT | -3.1 | 4.2 | Maternal Weaning Weight |
| YWT | -8.5 | 12.3 | Yearling Weight (lbs) |

**Carcass Traits**
| Trait | Min | Max | Description |
|-------|-----|-----|-------------|
| PFAT | -0.08 | 0.12 | Post-Weaning Fat Depth |
| PEMD | -1.2 | 2.1 | Post-Weaning Eye Muscle Depth |

**Reproduction**
| Trait | Min | Max | Description |
|-------|-----|-----|-------------|
| NLB | -0.15 | 0.35 | Number of Lambs Born |
| NLW | -0.12 | 0.28 | Number of Lambs Weaned |

**Parasite Resistance**
| Trait | Min | Max | Description |
|-------|-----|-----|-------------|
| WFEC | -0.45 | 0.52 | Weaning Fecal Egg Count |
| PFEC | -0.38 | 0.48 | Post-Weaning Fecal Egg Count |
```

**Use cases:**
- Understand the range of genetic variation within a breed
- Set realistic trait targets for selection
- Identify exceptional animals (those near max values)

---

### 5. Alternative Breed Query

**Prompt:**
```
Show me the EBV ranges for Suffolk sheep so I know what values to look for when selecting terminal sires.
```

**What it does:** Calls `nsip_get_trait_ranges` with Suffolk breed ID (690).

**Expected response:**
```
Suffolk sheep (Breed ID: 690) trait ranges:

As a terminal breed, Suffolk excel in growth and carcass traits:

| Trait | Min | Max | Selection Focus |
|-------|-----|-----|-----------------|
| BWT | -0.5 | 1.2 | Lower is better (easier lambing) |
| WWT | -4.8 | 11.2 | Higher is better |
| YWT | -7.2 | 15.8 | Higher is better |
| PFAT | -0.12 | 0.15 | Moderate preferred |
| PEMD | -1.5 | 3.2 | Higher is better (more loin) |

For terminal sire selection, prioritize rams with:
- WWT above 6.0 (top 25%)
- BWT below 0.3 (moderate birth weight)
- PEMD above 1.5 (good muscling)
```

---

## Animal Search Prompts

These prompts help you find specific animals or groups of animals based on various criteria.

### 6. Search by Breed

**Prompt:**
```
Find Katahdin sheep in the NSIP database.
```

**What it does:** Calls `nsip_search_animals` with breed_id=640.

**Expected response:**
```
Found 15 Katahdin sheep (showing page 1 of 102):

| LPN ID | Gender | Birth Date | Status | WWT | YWT |
|--------|--------|------------|--------|-----|-----|
| 6401492020FLE249 | Female | 2/5/2020 | CURRENT | 3.05 | 5.12 |
| 6401492020FLE251 | Female | 2/8/2020 | CURRENT | 2.87 | 4.89 |
| 6401492019RAM124 | Male | 3/12/2019 | CURRENT | 4.21 | 7.35 |
...

Total: 1,523 animals found. Use pagination to see more.
```

**Use case:** Browse animals in a specific breed to identify candidates for purchase or comparison.

---

### 7. Search with Trait Sorting

**Prompt:**
```
Find Katahdin rams with the highest weaning weight EBVs.
```

**What it does:** Calls `nsip_search_animals` with breed_id=640, sorted_trait="WWT", reverse=true, and filters for males.

**Expected response:**
```
Top Katahdin rams by Weaning Weight (WWT):

| Rank | LPN ID | WWT | WWT Acc | YWT | Status |
|------|--------|-----|---------|-----|--------|
| 1 | 6401492019RAM087 | 8.12 | 89% | 12.1 | CURRENT |
| 2 | 6401492018RAM234 | 7.89 | 92% | 11.8 | CURRENT |
| 3 | 6401492020RAM156 | 7.65 | 85% | 11.2 | SOLD |
| 4 | 6401492019RAM445 | 7.52 | 88% | 10.9 | CURRENT |
| 5 | 6401492018RAM112 | 7.34 | 91% | 10.5 | CURRENT |
...

These rams are in the top 1% for WWT within the Katahdin breed.
```

**Use case:** Identify top genetics for trait improvement in your flock.

---

### 8. Pagination for Large Results

**Prompt:**
```
Show me page 3 of Katahdin sheep, with 25 animals per page.
```

**What it does:** Calls `nsip_search_animals` with page=2 (0-indexed), page_size=25, breed_id=640.

**Expected response:**
```
Katahdin sheep (Page 3 of 61, showing animals 51-75):

| LPN ID | Gender | Birth Date | Status | BWT | WWT |
|--------|--------|------------|--------|-----|-----|
| 6401492019FLE089 | Female | 1/15/2019 | CURRENT | 0.12 | 2.45 |
| 6401492019FLE090 | Female | 1/16/2019 | CURRENT | -0.08 | 3.12 |
...

Navigation:
- Previous: Page 2 (animals 26-50)
- Next: Page 4 (animals 76-100)
- Total: 1,523 animals across 61 pages
```

**Use case:** Browse through large result sets systematically.

---

### 9. Search with Multiple Criteria

**Prompt:**
```
Find Polypay ewes that are currently active in breeding programs, sorted by number of lambs weaned.
```

**What it does:** Calls `nsip_search_animals` with breed_id=621 (Polypay), sorted_trait="NLW", reverse=true, and search_criteria for female and CURRENT status.

**Expected response:**
```
Top Polypay ewes by Number of Lambs Weaned (NLW):

| LPN ID | NLW | NLW Acc | NLB | Age | Status |
|--------|-----|---------|-----|-----|--------|
| 6211492017EWE334 | 0.28 | 94% | 0.32 | 7 | CURRENT |
| 6211492018EWE112 | 0.26 | 91% | 0.29 | 6 | CURRENT |
| 6211492019EWE445 | 0.24 | 87% | 0.27 | 5 | CURRENT |
...

These ewes represent the top maternal genetics in the Polypay breed.
Note: NLW combines genetics for litter size and lamb survival.
```

**Use case:** Find exceptional maternal animals for breeding stock purchases.

---

### 10. Get Detailed Animal Information

**Prompt:**
```
Give me all the details about sheep with LPN ID 6401492020FLE249.
```

**What it does:** Calls `nsip_get_animal` with the specified LPN ID.

**Expected response:**
```
**Animal Profile: 6401492020FLE249**

**Basic Information**
- Breed: Katahdin
- Gender: Female
- Date of Birth: February 5, 2020
- Status: CURRENT
- Genotyped: Yes

**Parentage**
- Sire: 6401492019RAM124
- Dam: 6401492018EWE035

**EBV Summary (Estimated Breeding Values)**

| Trait | Value | Accuracy | Percentile |
|-------|-------|----------|------------|
| BWT | 0.25 | 74% | 65th |
| WWT | 3.05 | 71% | 78th |
| MWWT | 1.82 | 68% | 72nd |
| YWT | 5.12 | 68% | 75th |
| NLB | 0.12 | 62% | 68th |
| NLW | 0.09 | 58% | 65th |
| WFEC | -0.18 | 55% | 70th |

**Contact Information**
- Farm: [Farm Name]
- Contact: [Owner Name]
- Phone: [Phone Number]
- Email: [Email Address]
```

**Use case:** Get complete information about a specific animal before purchase or breeding decisions.

---

### 11. Get Complete Animal Profile

**Prompt:**
```
Show me everything about sheep 6401492019RAM124 including its pedigree and offspring.
```

**What it does:** Calls `nsip_search_by_lpn` which retrieves details, lineage, and progeny in one call.

**Expected response:**
```
**Complete Profile: 6401492019RAM124**

**Animal Details**
- Breed: Katahdin
- Gender: Male (Ram)
- Birth Date: March 12, 2019
- Status: CURRENT
- Genotyped: Yes

**Top Traits**
| Trait | Value | Accuracy |
|-------|-------|----------|
| WWT | 4.21 | 92% |
| YWT | 7.35 | 89% |
| MWWT | 2.15 | 85% |

**Pedigree (3 Generations)**
```
                    [GGS: 640149201XRAM...]
        [GS: 6401492016RAM089]
                    [GGD: 640149201XEWE...]
[SIRE: 6401492017RAM234]
                    [GGS: 640149201XRAM...]
        [GD: 6401492016EWE112]
                    [GGD: 640149201XEWE...]

                    [GGS: 640149201XRAM...]
        [GS: 6401492015RAM156]
                    [GGD: 640149201XEWE...]
[DAM: 6401492016EWE078]
                    [GGS: 640149201XRAM...]
        [GD: 6401492015EWE234]
                    [GGD: 640149201XEWE...]
```

**Progeny Summary**
- Total Offspring: 47
- Males: 24
- Females: 23
- Average Offspring WWT: 3.85 (above breed average)

**Contact**
- Farm: [Farm Name]
- Phone: [Phone Number]
```

**Use case:** Comprehensive evaluation of a sire prospect including proven offspring performance.

---

## Pedigree and Genetics Prompts

These prompts help you explore ancestry, family relationships, and genetic inheritance.

### 12. View Animal Lineage

**Prompt:**
```
Show me the pedigree of sheep 6401492020FLE249.
```

**What it does:** Calls `nsip_get_lineage` to retrieve the ancestral tree.

**Expected response:**
```
**Pedigree Tree: 6401492020FLE249**

**Generation 1 (Parents)**
- Sire: 6401492019RAM124 (Katahdin, WWT: 4.21)
- Dam: 6401492018EWE035 (Katahdin, WWT: 2.89)

**Generation 2 (Grandparents)**
Paternal:
- Grandsire: 6401492017RAM234 (WWT: 3.95)
- Granddam: 6401492016EWE112 (WWT: 3.12)

Maternal:
- Grandsire: 6401492016RAM156 (WWT: 3.78)
- Granddam: 6401492015EWE089 (WWT: 2.67)

**Generation 3 (Great-Grandparents)**
[8 ancestors listed with basic trait information]

**Pedigree Analysis**
- Inbreeding Coefficient: 2.3% (acceptable)
- Common Ancestor: 6401492014RAM089 appears on both sides
- Strong WWT genetics on sire line
```

**Use case:** Evaluate genetic background and check for inbreeding before mating decisions.

---

### 13. Find Offspring of a Sire

**Prompt:**
```
Show me all the offspring of ram 6401492019RAM124.
```

**What it does:** Calls `nsip_get_progeny` with the ram's LPN ID.

**Expected response:**
```
**Progeny Report: 6401492019RAM124**

**Summary**
- Total Offspring: 47
- Birth Years: 2020, 2021, 2022, 2023
- Average Lamb WWT: 3.85 (breed average: 2.8)
- Lambing Ease: 94% unassisted

**Offspring List (Page 1 of 5)**

| LPN ID | Gender | Birth Date | Dam | WWT | Status |
|--------|--------|------------|-----|-----|--------|
| 6401492020FLE249 | Female | 2/5/2020 | 6401492018EWE035 | 3.05 | CURRENT |
| 6401492020RAM251 | Male | 2/8/2020 | 6401492018EWE089 | 4.12 | SOLD |
| 6401492020FLE253 | Female | 2/10/2020 | 6401492019EWE112 | 3.45 | CURRENT |
...

**Progeny Performance by Trait**
| Trait | Avg | Min | Max | vs Breed Avg |
|-------|-----|-----|-----|--------------|
| WWT | 3.85 | 2.12 | 5.23 | +1.05 |
| YWT | 6.42 | 4.15 | 8.89 | +1.32 |
| BWT | 0.18 | -0.12 | 0.45 | -0.02 |
```

**Use case:** Evaluate a sire's proven performance through his offspring.

---

### 14. Paginate Through Large Progeny Lists

**Prompt:**
```
Show me page 3 of offspring for ram 6401492018RAM112 with 20 animals per page.
```

**What it does:** Calls `nsip_get_progeny` with page=2 (0-indexed) and page_size=20.

**Expected response:**
```
**Progeny Page 3 of 6: 6401492018RAM112**

Showing offspring 41-60 of 112 total:

| LPN ID | Gender | Birth Date | Dam | WWT | YWT |
|--------|--------|------------|-----|-----|-----|
| 6401492021FLE089 | Female | 1/28/2021 | ... | 3.21 | 5.45 |
| 6401492021RAM090 | Male | 1/29/2021 | ... | 3.89 | 6.12 |
...

Navigation: Page 2 | [Page 3] | Page 4
```

---

### 15. Understanding Trait Inheritance

**Prompt:**
```
What trait ranges should I expect for Dorper sheep, and which traits are most heritable?
```

**What it does:** Calls `nsip_get_trait_ranges` for Dorper (breed_id=641), then may invoke `shepherd_breeding` for heritability context.

**Expected response:**
```
**Dorper Trait Ranges (Breed ID: 641)**

| Trait | Min | Max | Heritability | Selection Response |
|-------|-----|-----|--------------|-------------------|
| BWT | -0.45 | 0.85 | 35% | Moderate |
| WWT | -4.2 | 9.8 | 25% | Moderate |
| YWT | -6.5 | 14.2 | 30% | Moderate |
| PFAT | -0.10 | 0.14 | 40% | High |
| PEMD | -1.0 | 2.8 | 45% | High |

**Selection Guidance:**
- High heritability traits (PFAT, PEMD): Expect faster genetic progress
- Moderate heritability (BWT, WWT, YWT): Progress is steady but slower
- Low heritability (reproduction): Focus on management alongside genetics

For Dorper, prioritize:
1. Growth (WWT, YWT) - their primary strength
2. Muscling (PEMD) - highly heritable
3. Moderate BWT - for lambing ease
```

---

## Shepherd Consultation Prompts

The Shepherd is an AI-powered expert advisor with knowledge across four domains: breeding, health, calendar, and economics. These tools provide evidence-based guidance tailored to your region and situation.

### General Consultation

### 16. Ask a General Question

**Prompt:**
```
What should I consider when starting a Katahdin sheep operation in the Southeast?
```

**What it does:** Calls `shepherd_consult` with region="southeast".

**Expected response:**
```
**Starting a Katahdin Operation in the Southeast**

The Southeast presents both opportunities and challenges for Katahdin production:

**Regional Advantages**
- Hair sheep are well-suited to humid, hot climates
- Strong local markets for grass-fed lamb
- Extended grazing season reduces feed costs
- Katahdin parasite resistance valuable in high-parasite environment

**Key Considerations**

1. **Parasite Management** (Critical)
   - Southeast has highest parasite pressure in the US
   - Select for FAMACHA-resistant genetics (low WFEC EBVs)
   - Plan for rotational grazing from day one
   - Budget for fecal egg count monitoring

2. **Heat Stress**
   - Provide shade in all paddocks
   - Consider breeding schedule to lamb in cooler months
   - Water availability is critical (1-2 gal/head/day minimum)

3. **Fescue Toxicosis**
   - If using fescue pastures, test for endophyte levels
   - Consider novel endophyte varieties
   - Dilute fescue with legumes and other grasses

4. **Market Opportunities**
   - Direct-to-consumer lamb sales growing rapidly
   - Ethnic markets strong in urban Southeast
   - Consider USDA-inspected processing access

**Recommended Starting Steps**
1. Visit established Katahdin farms in your area
2. Start with 10-20 quality ewes from NSIP-recorded flocks
3. Invest in a proven ram with good parasite resistance
4. Establish relationship with sheep-knowledgeable vet

Would you like specific recommendations on any of these topics?
```

---

### Breeding Domain

### 17. EBV Interpretation

**Prompt:**
```
How do I interpret EBVs when selecting a terminal sire for my commercial ewes?
```

**What it does:** Calls `shepherd_breeding` with production_goal="terminal".

**Expected response:**
```
**Interpreting EBVs for Terminal Sire Selection**

When crossing a terminal sire on commercial ewes, focus on traits that maximize lamb value at market:

**Priority 1: Growth Traits**
- **WWT (Weaning Weight)**: Most important. Higher = heavier lambs at weaning.
  - Target: Top 25% for the breed (check breed-specific ranges)
  - Example: Suffolk WWT > 7.0 is excellent

- **YWT (Yearling Weight)**: Important if selling older lambs.
  - Correlates with WWT, so high WWT usually means high YWT

**Priority 2: Carcass Quality**
- **PEMD (Eye Muscle Depth)**: More saleable meat
  - Higher is better
  - Important for premium markets

- **PFAT (Fat Depth)**: Affects yield grade
  - Moderate preferred (too high = excess fat trim)
  - Too low = poor finish

**Priority 3: Birth Weight**
- **BWT**: Balance is key
  - Too high = lambing difficulty on smaller ewes
  - Too low = less vigorous lambs
  - Target: Moderate to slightly below average

**Reading the Numbers**
- EBVs are expressed in the UNITS of the trait (lbs for weight)
- A WWT of +5.0 means offspring average 5 lbs heavier at weaning than breed base
- Accuracy percentage shows reliability (higher = more progeny data)

**Example Selection Criteria for Terminal Sire:**
| Trait | Minimum | Target | Weight |
|-------|---------|--------|--------|
| WWT | +5.0 | +7.0+ | 40% |
| PEMD | +1.0 | +2.0+ | 25% |
| BWT | -0.2 | +0.3 | 20% |
| PFAT | -0.05 | 0 | 15% |

**Red Flags to Avoid:**
- Very high BWT (>0.8) without knowing ewe size
- Low accuracy (<50%) on critical traits
- Extreme values in any direction
```

---

### 18. Inbreeding Management

**Prompt:**
```
I've been using the same ram for 3 years. How do I avoid inbreeding problems?
```

**What it does:** Calls `shepherd_breeding` with focus on inbreeding management.

**Expected response:**
```
**Managing Inbreeding After Using One Ram for 3 Years**

**Your Situation Assessment**

After 3 years with one ram, you likely have:
- Year 1 daughters reaching breeding age
- Year 2 daughters approaching breeding age
- Potential father-daughter matings if ram is retained

**Inbreeding Risk Levels**
| Mating | Coefficient | Risk Level |
|--------|-------------|------------|
| Father x Daughter | 25% | CRITICAL |
| Half-siblings | 12.5% | HIGH |
| First Cousins | 6.25% | MODERATE |
| Unrelated | 0% | NONE |

**Immediate Actions**

1. **Identify At-Risk Ewes**
   - All daughters of your current ram
   - Use NSIP lineage tools to verify parentage

2. **Options for Breeding Season**

   **Option A: New Ram (Recommended)**
   - Purchase unrelated ram from different bloodlines
   - Use NSIP database to verify no common ancestors
   - Check lineage goes back 3-4 generations

   **Option B: Ram Rotation with Neighbor**
   - Exchange rams temporarily
   - Verify neighbor's ram is unrelated to your ewes

   **Option C: Artificial Insemination**
   - Access to diverse genetics without buying rams
   - Consider for top ewes

3. **Long-Term Strategy**
   - Replace rams every 2-3 years maximum
   - Keep detailed breeding records
   - Use NSIP to check common ancestors before purchase

**Using NSIP to Check Relatedness**
```
Search for potential new ram:
"Show me the pedigree of ram [LPN_ID]"

Then compare to your ewes:
"Show me the pedigree of ewe [LPN_ID]"

Look for common ancestors in first 3 generations.
```

**When Buying a New Ram, Ask:**
1. Full LPN ID for NSIP lookup
2. Three-generation pedigree
3. Inbreeding coefficient if available
```

---

### 19. Mating Planning

**Prompt:**
```
I have a high-growth ram and want to improve my flock's weaning weights. What's the best mating strategy?
```

**What it does:** Calls `shepherd_breeding` with production_goal="balanced" and focus on trait improvement.

**Expected response:**
```
**Mating Strategy to Improve Weaning Weight**

**Understanding Your Genetic Starting Point**

Before planning matings, assess your ewes:
1. Individual ewe WWT EBVs (if NSIP recorded)
2. Historical weaning weights of lambs
3. Current average vs breed average

**Mating Strategy Options**

**Strategy 1: Positive Assortative Mating**
Best for: Rapid improvement in top ewes

- Mate your best WWT ewes to the high-growth ram
- Keep replacement ewes from these matings
- Creates elite genetics quickly

Pros: Fastest genetic progress
Cons: May widen gap between top and bottom ewes

**Strategy 2: Corrective Mating**
Best for: Lifting the bottom of your flock

- Mate your lowest WWT ewes to the high-growth ram
- All ewes benefit from improved genetics
- More uniform flock over time

Pros: Improves weakest animals
Cons: Slower overall progress

**Strategy 3: Balanced Approach (Recommended)**
Best for: Most operations

- Use high-growth ram across ALL ewes
- Select replacement ewes based on their own EBVs
- Keep records to track improvement

**Expected Genetic Progress**

Assuming your ram is top 10% for WWT (+6.0 EBV):

| Ewe Group | Ewe WWT | Expected Lamb WWT | Improvement |
|-----------|---------|-------------------|-------------|
| Top 25% | +3.0 | +4.5 | Excellent |
| Average | +1.0 | +3.5 | Good |
| Bottom 25% | -1.0 | +2.5 | Significant |

*Lamb EBV = (Sire EBV + Dam EBV) / 2, approximately*

**Don't Forget Other Traits**

While focusing on WWT, monitor:
- Birth weight (avoid lambing problems)
- Maternal traits in replacement ewes
- Structural soundness

**Tracking Progress**

1. Weigh all lambs at weaning (or consistent age)
2. Record which ram x ewe produced each lamb
3. Submit to NSIP for official EBVs (if registered)
4. Compare year-over-year averages
```

---

### Health Domain

### 20. Parasite Management

**Prompt:**
```
What's the best deworming strategy for my sheep in the Southeast?
```

**What it does:** Calls `shepherd_health` with region="southeast" and appropriate context.

**Expected response:**
```
**Parasite Management Strategy for the Southeast**

The Southeast has the highest parasite pressure in North America due to warm, humid conditions. A strategic approach is essential.

**Targeted Selective Treatment (TST) Protocol**

Instead of deworming all sheep on a schedule, treat only those that need it:

1. **FAMACHA Scoring (Every 2 Weeks)**
   - Score 1-2: No treatment needed
   - Score 3: Monitor closely, consider treatment
   - Score 4-5: Treat immediately

2. **Body Condition Scoring**
   - Sudden weight loss may indicate parasitism
   - Even FAMACHA 3 with poor BCS should be treated

3. **Fecal Egg Counts**
   - Baseline your flock in spring
   - Test before and after treatments (efficacy check)
   - Individual animals >2000 EPG need treatment

**Treatment Timing (Critical Windows)**

| Period | Risk Level | Action |
|--------|------------|--------|
| Spring (warm-up) | HIGH | Increase monitoring to weekly |
| Summer | VERY HIGH | Peak parasite season |
| Fall | MODERATE | Preparing for winter |
| Winter | LOW | Minimal treatment needed |

**Effective Dewormers for Southeast**

Due to resistance, always verify efficacy with fecal reduction test:

1. **Moxidectin (Cydectin)** - Often most effective
   - Sheep dose: 0.4 mg/kg
   - Oral formulation preferred

2. **Levamisole (Prohibit/Levasole)**
   - Still effective in many flocks
   - Narrow safety margin - dose carefully

3. **Combination Treatment**
   - For heavily parasitized animals
   - Use two classes together (not sequentially)

**Avoid:**
- Ivermectin alone (widespread resistance)
- Albendazole alone (often resistant)
- Regular whole-flock treatments

**Pasture Management (Equally Important)**

- Rotational grazing with 60+ day rest periods
- Multi-species grazing (cattle break parasite cycle)
- Avoid grazing below 4 inches
- Clip pastures after grazing

**Genetic Selection**

Over time, select for parasite-resistant animals:
- Cull ewes requiring frequent treatment
- Keep replacements from low-treatment ewes
- Select rams with low WFEC EBVs

Would you like more detail on any of these strategies?
```

---

### 21. Nutrition Planning

**Prompt:**
```
What nutrition program should I follow for my ewes during late gestation?
```

**What it does:** Calls `shepherd_health` with life_stage="gestation".

**Expected response:**
```
**Late Gestation Nutrition Program**

Late gestation (final 6 weeks before lambing) is the most nutritionally demanding period. Lamb birth weight and ewe milk production depend on nutrition now.

**Energy Requirements by Litter Size**

| Weeks Before Lambing | Singles | Twins | Triplets |
|---------------------|---------|-------|----------|
| 6 weeks | 100% | 110% | 120% |
| 4 weeks | 110% | 130% | 150% |
| 2 weeks | 120% | 150% | 180% |

*Percentages relative to maintenance requirements*

**Daily Nutritional Needs (150 lb Ewe)**

| Nutrient | Singles | Twins |
|----------|---------|-------|
| Dry Matter | 4.0 lbs | 4.5 lbs |
| Crude Protein | 11% | 13% |
| TDN (Energy) | 60% | 65% |
| Calcium | 0.35% | 0.45% |
| Phosphorus | 0.25% | 0.30% |

**Sample Feeding Program**

**For Ewes on Good Pasture/Hay:**
- Hay (grass): Free choice
- Grain mix: Start at 0.5 lb/day, increase to 1.5-2 lbs by lambing
- Mineral: Sheep-specific free choice

**For Ewes on Limited Forage:**
- Hay: 4-5 lbs/day
- Grain: 1.5-2.5 lbs/day (higher for twins/triplets)
- Soybean meal: 0.25 lbs if protein is limiting

**Critical Supplements**

1. **Selenium/Vitamin E**
   - Prevents white muscle disease in lambs
   - Inject ewes 4-6 weeks before lambing
   - Or feed selenium-fortified mineral

2. **Calcium (Late Gestation Caution)**
   - Don't over-supplement calcium now
   - Excess predisposes to milk fever at lambing
   - Switch to higher calcium AFTER lambing

3. **Salt and Water**
   - Fresh water essential (consumption increases)
   - Salt free choice

**Body Condition Target**

- Score 3.0-3.5 at lambing (1-5 scale)
- Thin ewes: Separate and feed extra
- Over-conditioned: Increase exercise, monitor for toxemia

**Warning Signs of Inadequate Nutrition**

- Pregnancy toxemia (ketosis) - weakness, off-feed, sweet breath
- Dropping body condition
- Wool breaks

**Week-by-Week Checklist**

- **6 weeks out**: Increase grain to 0.5 lb, ultrasound if available
- **4 weeks out**: Increase grain to 1.0 lb, give selenium injection
- **2 weeks out**: Increase grain to 1.5 lb, prepare lambing area
- **Lambing**: Maintain intake, have energy drench ready
```

---

### Calendar Domain

### 22. Breeding Schedule Planning

**Prompt:**
```
When should I start breeding season for spring lambing in the Midwest?
```

**What it does:** Calls `shepherd_calendar` with region="midwest" and task_type="breeding".

**Expected response:**
```
**Spring Lambing Breeding Schedule - Midwest**

**Target Lambing Period:** March 15 - April 30
**Breeding Season:** October 10 - November 25

**Breeding Calendar**

| Date | Activity | Notes |
|------|----------|-------|
| **Sept 1** | Ram soundness exam | Breeding soundness exam by vet |
| **Sept 15** | Flush ewes | Increase nutrition 2-3 weeks pre-breeding |
| **Oct 1** | Final prep | Check ram:ewe ratio (1:25-40) |
| **Oct 10** | Ram turnout | Start of breeding season |
| **Oct 15** | Apply marking harness | Change colors every 17 days |
| **Nov 1** | Change harness color | Detect repeat breeders |
| **Nov 18** | Change harness color | Final cycle check |
| **Nov 25** | Remove rams | End breeding (50-day season) |

**Gestation Timeline**

Sheep gestation: ~147 days (145-152 range)

| Breeding Date | Expected Lambing |
|---------------|------------------|
| Oct 10 | March 6 |
| Oct 25 | March 21 |
| Nov 10 | April 5 |
| Nov 25 | April 20 |

**Midwest-Specific Considerations**

**Advantages of March-April Lambing:**
- Warming temperatures reduce lamb mortality
- Pasture available as lambs grow
- Aligns with natural breeding season (no lights needed)
- Lambs ready for fall sales at premium weights

**Challenges to Prepare For:**
- Late winter storms possible in early March
- Mud season coincides with early lambs
- Barn space needed for weather protection

**Ram Management**

1. **Condition**: Body score 3.5+ before breeding
2. **Nutrition**: Increase energy 4-6 weeks before turnout
3. **Health**: Deworm and vaccinate before breeding
4. **Ratio**: 1 mature ram per 35-40 ewes, 1 ram lamb per 15-20

**Ewe Preparation**

1. **Flushing**: Increase nutrition 17 days before ram turnout
2. **Vaccinations**: CDT booster 4-6 weeks pre-breeding
3. **Foot check**: Trim hooves, treat any issues
4. **Cull**: Remove non-productive ewes before breeding

Would you like a detailed lambing preparation calendar as well?
```

---

### 23. Seasonal Task Planning

**Prompt:**
```
What should I be doing with my sheep flock in January in the Northeast?
```

**What it does:** Calls `shepherd_calendar` with region="northeast" and general seasonal focus.

**Expected response:**
```
**January Sheep Management - Northeast Region**

**Current Flock Status (Typical)**
- Late gestation for March lambing flocks
- Maintenance for May lambing flocks
- Winter feeding in full swing

**Weekly Task Calendar**

**Week 1 (Jan 1-7)**
- [ ] Review feed inventory for winter duration
- [ ] Check hay quality (send for analysis if uncertain)
- [ ] Monitor water systems for freezing
- [ ] Body condition score pregnant ewes

**Week 2 (Jan 8-14)**
- [ ] Increase grain for ewes 8 weeks from lambing
- [ ] Order lambing supplies (see checklist below)
- [ ] Ultrasound ewes for pregnancy/multiples (if available)
- [ ] Check barn ventilation (drafts vs. ammonia)

**Week 3 (Jan 15-21)**
- [ ] Selenium/Vitamin E injections (6 weeks pre-lambing)
- [ ] Separate thin ewes for extra feeding
- [ ] Clean and prepare lambing pens
- [ ] Test heat lamps and backup generators

**Week 4 (Jan 22-31)**
- [ ] CDT vaccination for ewes (4-6 weeks pre-lambing)
- [ ] Final lambing supply check
- [ ] Set up monitoring system (cameras, schedule)
- [ ] Arrange lambing assistance if needed

**Cold Weather Management**

**Water (Critical)**
- Check water sources twice daily
- Tank heaters functioning
- Break ice on outdoor troughs
- Consumption: 1-2 gallons/ewe/day (more if lactating)

**Bedding**
- Deep bed with straw for insulation
- Remove wet spots weekly
- Extra bedding in cold snaps

**Ventilation vs. Warmth**
- Fresh air more important than warmth for adult sheep
- Avoid sealed barns (ammonia buildup)
- Protect from drafts at sheep level
- Adequate ventilation above head height

**Nutrition Focus**

Late gestation ewes need increased energy:

| Weeks to Lamb | Grain (lbs/day) | Hay Quality |
|---------------|-----------------|-------------|
| 8+ | 0.5-1.0 | Good grass/mixed |
| 6 | 1.0-1.5 | Good grass/mixed |
| 4 | 1.5-2.0 | Add some legume |
| 2 | 2.0-2.5 | Best quality available |

**Lambing Supply Checklist**

Essential:
- [ ] OB sleeves and lubricant
- [ ] Iodine (7%) for navels
- [ ] Lamb feeding tubes and syringes
- [ ] Colostrum replacer
- [ ] Heat lamp with spare bulbs
- [ ] Towels and clean rags
- [ ] Ear tags and applicator
- [ ] Record keeping forms

Nice to have:
- [ ] Lamb warming box
- [ ] Scale for birth weights
- [ ] Elastrator and bands
- [ ] Prolapse harness
- [ ] Calcium drench

**Weather Monitoring**

Watch forecasts for:
- Extended cold (below 0F) - increase feeding
- Major storms - ensure 3+ day feed supply
- Ice storms - protect water systems

Northeast January average: 20-30F (varies by location)
```

---

### Economics Domain

### 24. ROI on Genetics

**Prompt:**
```
Is it worth paying $2,500 for a proven ram with excellent EBVs?
```

**What it does:** Calls `shepherd_economics` with context on genetic investment.

**Expected response:**
```
**ROI Analysis: $2,500 Ram Investment**

The value of a high-quality ram depends on how much genetic improvement he brings and how many lambs he sires.

**Scenario: 50-Ewe Flock**

**Assumptions:**
- Ram used for 3 breeding seasons
- 45 ewes bred per year (90% conception)
- 1.6 lambs weaned per ewe
- Market lambs sold at $200/head average
- Superior ram improves weaning weight by 5 lbs per lamb

**Value Calculation**

| Factor | Calculation | Value |
|--------|-------------|-------|
| Lambs sired per year | 45 ewes x 1.6 | 72 lambs |
| Lambs over 3 years | 72 x 3 | 216 lambs |
| Extra weight per lamb | 5 lbs | |
| Value per lb gain | $2.00/lb | $10/lamb |
| **Total added value** | 216 x $10 | **$2,160** |

**But That's Not All...**

**Retained Daughters**

If you keep 15 replacement ewe lambs per year:
- 45 daughters retained over 3 years
- Each produces for 6+ years
- Improved genetics compound over time

Conservative estimate of daughter value: $1,500+ over their lifetime

**Salvage Value**

After 3 years, the ram can be:
- Sold to another breeder: $500-1,000
- Sold as meat ram: $200-300

**Total ROI Summary**

| Investment | $2,500 |
|------------|--------|
| Market lamb improvement | $2,160 |
| Daughter genetic value | $1,500+ |
| Salvage value | $500 |
| **Total Return** | **$4,160+** |
| **Net Profit** | **$1,660+** |

**When $2,500 is NOT Worth It:**

- Small flock (<20 ewes) - fewer lambs to spread cost
- Single-use breeding - can't amortize over multiple years
- No record keeping - can't verify genetic improvement
- Unproven genetics - high accuracy EBVs matter

**When $2,500 IS Worth It:**

- Medium/large flock (40+ ewes)
- Keeping replacement ewes (genetic multiplier)
- Verified EBVs with high accuracy (>80%)
- Significant improvement over current genetics

**Alternative: Lease or AI**

If $2,500 upfront is difficult:
- Ram lease: $500-800/season
- AI with proven genetics: $50-100/straw
- Cooperative ownership with neighbors

**Bottom Line:**

For a 50-ewe flock keeping replacements, a $2,500 proven ram typically returns $1,600+ profit over 3 years, plus the long-term value of improved daughter genetics. The investment is justified if:

1. You can verify his EBVs are significantly better than your current ram
2. You'll use him for 2+ seasons
3. You keep replacement ewes from his daughters
```

---

### 25. Break-Even Analysis

**Prompt:**
```
What's the break-even price for my market lambs if I'm selling them at 120 pounds?
```

**What it does:** Calls `shepherd_economics` with market_focus="market_lambs".

**Expected response:**
```
**Break-Even Analysis: 120 lb Market Lambs**

**Cost Components**

I'll walk through typical costs - adjust these for your operation:

**Per-Ewe Annual Costs**

| Category | Low | Average | High |
|----------|-----|---------|------|
| Feed (hay/pasture) | $75 | $100 | $150 |
| Grain/supplement | $50 | $75 | $100 |
| Minerals/salt | $10 | $15 | $20 |
| Health (vaccines, dewormers) | $15 | $25 | $40 |
| Shearing (wool breeds) | $5 | $10 | $15 |
| Breeding (ram share) | $20 | $35 | $50 |
| Miscellaneous | $10 | $20 | $30 |
| **Total per ewe** | **$185** | **$280** | **$405** |

**Per-Lamb Costs (Birth to Market)**

| Category | Low | Average | High |
|----------|-----|---------|------|
| Creep feed | $20 | $35 | $50 |
| Grower feed (post-weaning) | $40 | $60 | $80 |
| Health | $5 | $10 | $15 |
| Marketing (transport, fees) | $10 | $20 | $30 |
| **Total per lamb** | **$75** | **$125** | **$175** |

**Break-Even Calculation**

Assumptions:
- 1.5 lambs weaned per ewe
- 120 lb market weight
- Average costs

```
Cost per lamb = (Ewe cost / lambs weaned) + lamb cost
Cost per lamb = ($280 / 1.5) + $125
Cost per lamb = $187 + $125 = $312
```

**Break-even price = $312 / 120 lbs = $2.60/lb live weight**

**Sensitivity Analysis**

| Lambs Weaned | Break-Even/lb |
|--------------|---------------|
| 1.0 | $3.38 |
| 1.25 | $2.99 |
| 1.5 | $2.60 |
| 1.75 | $2.35 |
| 2.0 | $2.15 |

**Key Insight:** Lambing percentage has HUGE impact on profitability.

**Ways to Improve Break-Even**

1. **Increase lambing percentage**
   - Best ewes produce 1.8-2.0 lambs weaned
   - Select for NLB and NLW EBVs

2. **Reduce feed costs**
   - Extend grazing season
   - Stockpile pasture for winter
   - Buy hay in bulk during summer

3. **Increase market weight**
   - 140 lb lambs spread fixed costs further
   - But watch feed conversion efficiency

4. **Premium markets**
   - Direct sales: $5-8/lb hanging
   - Ethnic markets: Premium for specific weights/timing
   - Breeding stock: 2-3x market lamb value

**Current Market Context**

Check current prices at:
- USDA Market News: https://www.ams.usda.gov/market-news
- Local auction reports

Typical 2024 ranges:
- Auction: $1.80-2.50/lb
- Direct to consumer: $5-8/lb hanging weight
- Breeding stock: $300-800 depending on quality
```

---

## Advanced Multi-Tool Workflows

These prompts demonstrate how to combine multiple tools for comprehensive analysis.

### 26. Compare Two Animals

**Prompt:**
```
Compare the genetics of ram 6401492019RAM124 and ram 6401492018RAM112 to help me decide which one to buy.
```

**What it does:** Calls `nsip_get_animal` twice (or `nsip_search_by_lpn` twice), then provides comparative analysis.

**Expected response:**
```
**Ram Comparison: Side-by-Side Genetic Analysis**

**Basic Information**

| Attribute | Ram A: ...RAM124 | Ram B: ...RAM112 |
|-----------|------------------|------------------|
| Breed | Katahdin | Katahdin |
| Age | 5 years | 6 years |
| Status | CURRENT | CURRENT |
| Genotyped | Yes | Yes |

**EBV Comparison**

| Trait | Ram A | Acc | Ram B | Acc | Advantage |
|-------|-------|-----|-------|-----|-----------|
| BWT | +0.15 | 92% | +0.32 | 95% | Ram A (lower BWT) |
| WWT | +4.21 | 92% | +3.89 | 94% | Ram A (+0.32) |
| MWWT | +2.15 | 85% | +2.45 | 88% | Ram B (+0.30) |
| YWT | +7.35 | 89% | +6.92 | 91% | Ram A (+0.43) |
| NLB | +0.08 | 78% | +0.12 | 82% | Ram B (+0.04) |
| WFEC | -0.22 | 72% | -0.15 | 75% | Ram A (more resistant) |

**Progeny Performance**

| Metric | Ram A | Ram B |
|--------|-------|-------|
| Total Offspring | 47 | 112 |
| Avg Offspring WWT | +3.85 | +3.62 |
| Lambing Ease | 94% unassisted | 89% unassisted |
| Offspring in NSIP | 38 | 95 |

**Pedigree Quality**

| Factor | Ram A | Ram B |
|--------|-------|-------|
| Inbreeding Coef. | 2.3% | 3.1% |
| Known Generations | 4 | 5 |
| Common Ancestors | None in 3 gen | None in 3 gen |

**Recommendation**

**For Growth-Focused Selection: Ram A**
- Higher WWT (+4.21 vs +3.89)
- Higher YWT (+7.35 vs +6.92)
- Better lambing ease (lower BWT)
- Better parasite resistance (WFEC)

**For Maternal Trait Improvement: Ram B**
- Higher MWWT (+2.45 vs +2.15)
- Higher NLB (+0.12 vs +0.08)
- More progeny data (higher confidence)

**Overall Recommendation:**

If you're selecting for market lamb production, **Ram A** offers better growth genetics with lower birth weights (easier lambing).

If you're building your replacement ewe flock and want maternal genetics, **Ram B** has an edge in maternal traits.

**Questions to Ask the Sellers:**

1. Ram A: Why fewer progeny at 5 years old?
2. Ram B: Any lambing difficulty in offspring?
3. Both: Health history and any genetic testing results?
```

---

### 27. Evaluate a Potential Sire

**Prompt:**
```
I'm considering buying ram 6401492019RAM087 to improve my flock's weaning weights. Can you evaluate him as a sire prospect?
```

**What it does:** Calls `nsip_search_by_lpn` for complete profile, then `nsip_get_trait_ranges` for breed context, potentially `shepherd_breeding` for advice.

**Expected response:**
```
**Sire Prospect Evaluation: 6401492019RAM087**

**Quick Summary**
This ram ranks in the **top 2%** of Katahdin breed for Weaning Weight.
He has excellent progeny data supporting his EBVs.

---

**Genetic Profile**

| Trait | Value | Accuracy | Breed Rank |
|-------|-------|----------|------------|
| WWT | +8.12 | 89% | Top 2% |
| YWT | +12.1 | 86% | Top 3% |
| BWT | +0.28 | 91% | 60th %ile |
| MWWT | +1.95 | 82% | Top 25% |
| NLB | +0.05 | 75% | 55th %ile |
| WFEC | -0.12 | 68% | Top 35% |

**Trait Analysis**

**Strengths:**
- Exceptional growth (WWT +8.12 is elite)
- Strong yearling weight follows through
- Moderate birth weight (shouldn't cause problems)
- Good maternal effect (his daughters should milk well)

**Neutral:**
- Average reproduction genetics
- Parasite resistance slightly above average

**No Weaknesses Identified**

---

**Progeny Verification**

| Metric | Value | Assessment |
|--------|-------|------------|
| Total Offspring | 89 | Excellent data |
| Avg Offspring WWT | +4.85 | Transmitting well |
| Offspring Range | +2.1 to +7.2 | Consistent |
| Sons in NSIP | 12 | Active influence |
| Daughters in NSIP | 31 | Building maternal line |

**Key Finding:** His offspring average WWT (+4.85) confirms he's transmitting his genetics effectively. Expected offspring average would be ~4.0 (half his EBV), so his progeny are exceeding expectations.

---

**Pedigree Quality**

```
SIRE: 6401492017RAM234 (WWT: +6.8, top 5%)
DAM: 6401492016EWE156 (WWT: +4.2, MWWT: +2.8)

Strong growth genetics on both sides.
No concerning inbreeding (COI: 1.8%)
```

---

**What to Expect in Your Flock**

If your current ewes average WWT of +2.0:

| Scenario | Ewe WWT | Expected Lamb WWT |
|----------|---------|-------------------|
| Your top ewes | +3.5 | +5.8 |
| Average ewes | +2.0 | +5.1 |
| Below average | +0.5 | +4.3 |

All offspring should be significantly above breed average.

---

**Risk Assessment**

| Factor | Risk Level | Notes |
|--------|------------|-------|
| Genetic improvement | LOW | Proven with 89 offspring |
| Birth weight issues | LOW | +0.28 BWT is moderate |
| Inbreeding | LOW | 1.8% COI, no common ancestors likely |
| Health issues | UNKNOWN | Ask seller for health history |
| Longevity | UNKNOWN | At 5 years, breeding life is limited |

---

**Recommendation: STRONG BUY**

This ram is an exceptional sire prospect for weaning weight improvement:

1. **Proven genetics** - 89 offspring confirm his EBVs
2. **Top 2% ranking** - Elite growth potential
3. **Balanced traits** - No red flags in other areas
4. **Good accuracy** - 89% on WWT means reliable prediction

**Questions to Ask Seller:**
1. Why is he being sold? (Age? Replacement daughters?)
2. Any health issues or injuries?
3. Breeding soundness exam this year?
4. Any known offspring with problems?

**Price Guidance:**
For a top 2% proven ram with this data, expect to pay $2,000-4,000 depending on age and demand.
```

---

### 28. Plan a Breeding Program

**Prompt:**
```
Help me plan a breeding program to improve both growth and parasite resistance in my Katahdin flock over the next 5 years.
```

**What it does:** Combines `nsip_get_trait_ranges` for goals, `shepherd_breeding` for strategy, and general breeding program design.

**Expected response:**
```
**5-Year Breeding Improvement Plan**
**Focus: Growth (WWT) and Parasite Resistance (WFEC)**

---

**Year 0: Baseline Assessment**

**Step 1: Evaluate Current Flock**
- Record WWT on all lambs this year
- FAMACHA score all animals monthly
- Identify sheep requiring frequent deworming
- Submit data to NSIP if not already enrolled

**Step 2: Set Improvement Targets**

| Trait | Current (estimate) | Year 5 Goal | Annual Progress |
|-------|-------------------|-------------|-----------------|
| WWT | +1.5 | +3.5 | +0.4/year |
| WFEC | 0 | -0.20 | -0.04/year |

**Step 3: Identify Selection Candidates**

Current ewes to KEEP as breeding foundation:
- WWT above flock average
- Rarely need deworming (3 or fewer treatments/year)
- Good structural soundness
- Decent reproduction

Ewes to CULL:
- Require frequent deworming (5+ treatments)
- Below average growth
- Poor udders or feet

---

**Year 1: Foundation Building**

**Ram Selection Priority:**
Find a ram with:
- WWT: +5.0 or higher (top 20%)
- WFEC: -0.15 or lower (top 30%)
- Accuracy: 70%+ on both traits

**Search prompt to use:**
```
Find Katahdin rams with WWT above +5.0 and WFEC below -0.15
```

**Breeding Strategy:**
- Use new ram on ALL ewes
- Keep detailed records (who bred who)
- Weigh all lambs at 120 days

**Culling:**
- Remove bottom 15% of ewes by deworming frequency
- Replace with purchased ewes OR wait for Year 1 ewe lambs

---

**Year 2: First Selection Decisions**

**Ewe Lamb Selection:**
From Year 1 lamb crop, keep replacements based on:
1. Individual WWT (top 30% of ewe lambs)
2. Dam's deworming history
3. Sire's WFEC EBV (if using multiple rams)

**Ram Lamb Evaluation:**
- Identify standout ram lambs
- Consider retaining one for future use (if unrelated to ewes)
- Sell others as breeding stock

**Continued Ram Use:**
- If ram is young, continue using
- If need new ram, prioritize WFEC improvement

---

**Year 3: Accelerating Progress**

**Key Actions:**
- Year 1 daughters now breeding
- NSIP EBVs now available for your animals
- Use actual EBVs to refine selection

**Ram Strategy Options:**

**Option A: Same Ram**
If still performing, continue (avoid breeding to his daughters)

**Option B: New Ram - Double Down on Gains**
- Prioritize traits where you've made least progress
- If WWT improving well, emphasize WFEC
- If WFEC improving, emphasize WWT

**Selection Index:**
Create a simple index to rank animals:
```
Selection Score = (WWT x 0.5) + (WFEC x -0.5)
```
Higher score = better candidate

---

**Year 4: Refinement**

**By Now You Should Have:**
- Flock average WWT improved by ~1.2-1.6 units
- Fewer ewes needing frequent deworming
- NSIP records on most animals
- Clear genetic trends visible

**Fine-Tuning:**
- Tighten selection pressure (keep fewer, better replacements)
- Consider AI for genetic diversity
- Evaluate if any trait needs extra emphasis

**Culling Intensifies:**
- Now culling on actual EBVs, not just phenotype
- Remove any daughters that don't meet targets

---

**Year 5: Evaluation and Next Phase**

**Measure Progress:**

| Metric | Year 0 | Year 5 | Improvement |
|--------|--------|--------|-------------|
| Avg Flock WWT | +1.5 | +3.2 | +1.7 |
| Avg WFEC | 0 | -0.15 | -0.15 |
| Dewormings/ewe/year | 4 | 2 | 50% reduction |
| Avg lamb 120-day weight | 85 lbs | 92 lbs | +7 lbs |

**Economic Impact:**
- 7 lbs more per lamb x $2.00/lb = $14/lamb
- 50 ewes x 1.5 lambs x $14 = $1,050/year additional revenue
- Reduced dewormer costs: ~$200/year savings
- **Total annual benefit: ~$1,250**

---

**Key Success Factors**

1. **Consistent Record Keeping**
   - Weigh EVERY lamb at weaning
   - Record EVERY deworming treatment
   - Track parentage accurately

2. **Patience**
   - Genetic change is slow but permanent
   - Don't expect overnight results
   - Trust the process

3. **Balanced Selection**
   - Don't sacrifice one trait completely for another
   - Maintain structural soundness and reproduction
   - Watch for unintended consequences

4. **Use NSIP Data**
   - Submit your data annually
   - Use official EBVs when available
   - Connect with other NSIP breeders

---

**Recommended Prompts Throughout the Program**

**Finding Rams:**
```
Find Katahdin rams with WWT above +5.0 and WFEC below -0.15
```

**Evaluating Candidates:**
```
Show me the complete profile for ram [LPN_ID] including progeny
```

**Understanding Traits:**
```
How do I balance selecting for growth and parasite resistance?
```

**Economic Questions:**
```
Is it worth paying $3,000 for a ram with these EBVs?
```

Would you like me to help identify specific ram candidates for Year 1?
```

---

### 29. Flock Health Planning

**Prompt:**
```
I just bought 20 Katahdin ewes from three different farms. What health and management steps should I take before breeding season in 60 days?
```

**What it does:** Combines `shepherd_health` and `shepherd_calendar` for comprehensive guidance.

**Expected response:**
```
**60-Day New Ewe Integration and Breeding Prep Plan**

Congratulations on your new ewes! Here's a detailed plan to get them healthy and ready for breeding.

---

**Week 1: Arrival and Quarantine (Days 1-7)**

**Quarantine Protocol (Critical)**
- Isolate new ewes from existing animals for 30 days minimum
- Separate pasture or pen with no shared fence lines
- Use dedicated equipment (feeders, waterers)
- Handle new ewes LAST when doing chores

**Day 1 Actions:**
- [ ] Provide clean water and good hay (reduce stress)
- [ ] Observe for shipping fever symptoms (cough, nasal discharge)
- [ ] Record body condition score (1-5 scale)
- [ ] Check for obvious health issues (limping, wounds)

**Day 2-3 Actions:**
- [ ] FAMACHA score all ewes
- [ ] Collect fecal samples for egg counts
- [ ] Foot inspection - check for rot or scald

**Day 7 Actions:**
- [ ] Deworm based on FAMACHA/FEC results (not blanket treatment)
- [ ] Treat any foot issues identified
- [ ] Begin transitioning to your feed program

---

**Week 2-3: Health Assessment (Days 8-21)**

**Vaccinations**
- [ ] CDT (Clostridium perfringens types C&D + tetanus)
  - If history unknown, give 2 doses 3-4 weeks apart
- [ ] Rabies (if endemic in your area)
- [ ] Optional: Footrot vaccine if history of issues

**Parasite Management**
- [ ] Fecal egg count results back - treat as needed
- [ ] FAMACHA weekly during quarantine
- [ ] Document which ewes need treatment (for future culling decisions)

**Disease Testing (Based on Risk)**
Consider testing for diseases from seller farms:
- [ ] OPP (Ovine Progressive Pneumonia) - blood test
- [ ] CL (Caseous Lymphadenitis) - check for abscesses
- [ ] Johne's Disease - if high-risk source

**Identification**
- [ ] Apply your farm tags
- [ ] Record original farm ID for NSIP tracking
- [ ] Create individual records for each ewe

---

**Week 4: Integration Begins (Days 22-28)**

**Mixing with Existing Flock (if you have one)**
- Introduce through fence first (visual contact)
- Mix in small groups if possible
- Watch for aggressive behavior
- Provide multiple feed/water stations

**If These Are Your First Sheep**
- Begin moving to permanent pasture/housing
- Establish feeding routine
- Continue daily observation

**Body Condition Management**
Target BCS 3.0-3.5 for breeding

| Current BCS | Action |
|-------------|--------|
| Below 2.5 | Increase grain, separate for extra feeding |
| 2.5-3.5 | Maintain current nutrition |
| Above 4.0 | Reduce grain, increase exercise |

---

**Week 5-6: Pre-Breeding Preparation (Days 29-42)**

**Flushing (Nutritional Boost)**
Start 17 days before ram introduction:
- Increase energy intake by 15-20%
- Add 0.5-1 lb grain per day
- Move to lush pasture if available
- Continue until breeding is confirmed

**Hoof Care**
- [ ] Trim all hooves
- [ ] Treat any remaining foot issues
- [ ] Walk ewes on clean, dry surface daily

**Ram Preparation (if you have one)**
- [ ] Breeding soundness exam by vet
- [ ] Good nutrition (BCS 3.5+)
- [ ] Trim hooves
- [ ] Shear around sheath if needed

---

**Week 7-8: Final Prep and Breeding (Days 43-60)**

**Pre-Breeding Checklist**
- [ ] All ewes vaccinated
- [ ] All ewes dewormed as needed (not blanket)
- [ ] Body condition 3.0-3.5
- [ ] Hooves trimmed
- [ ] Individual records complete

**Ram Introduction (Day 60)**
- [ ] Check ram marking harness
- [ ] Introduce ram in morning
- [ ] Observe for breeding activity
- [ ] Record breeding dates

**Monitoring**
- Continue FAMACHA every 2 weeks
- Watch for repeat breeders (harness marks)
- Note any ewes not cycling

---

**Records to Establish**

Create a record for each ewe:

| Field | Information |
|-------|-------------|
| Your ID | |
| Original ID/LPN | |
| Source Farm | |
| Purchase Date | |
| Age/Birth Date | |
| Breed | |
| Initial BCS | |
| Initial FAMACHA | |
| Vaccination Dates | |
| Deworming (dates/products) | |
| Breeding Date | |
| Notes | |

---

**Budget for 60-Day Prep (20 Ewes)**

| Item | Cost |
|------|------|
| Quarantine feed (hay) | $100-150 |
| CDT vaccines (40 doses) | $20-30 |
| Dewormer | $30-50 |
| Fecal testing | $50-100 |
| Hoof care supplies | $20-30 |
| Misc. (tags, etc.) | $30-50 |
| **Total** | **$250-410** |

---

**Red Flags to Watch For**

**Immediate Vet Call:**
- High fever (>104F)
- Severe respiratory distress
- Profuse diarrhea
- Inability to stand
- Sudden death

**Monitor Closely:**
- Off feed for >24 hours
- Mild cough or nasal discharge
- Limping
- Isolation from group

Would you like more detail on any of these steps?
```

---

### 30. Year-End Economics Review

**Prompt:**
```
Help me analyze whether my 50-ewe Katahdin operation was profitable this year. I sold 68 lambs at an average of $275 each, my total expenses were about $18,000, and I kept 12 replacement ewe lambs.
```

**What it does:** Calls `shepherd_economics` for profitability analysis.

**Expected response:**
```
**Annual Profitability Analysis: 50-Ewe Katahdin Operation**

---

**Revenue Summary**

| Source | Calculation | Amount |
|--------|-------------|--------|
| Market lambs sold | 68 x $275 | $18,700 |
| Replacement ewes (value) | 12 x $350* | $4,200 |
| Cull ewes (estimate) | 5 x $150 | $750 |
| Wool (Katahdin = none) | N/A | $0 |
| **Total Revenue** | | **$23,650** |

*Replacement ewes valued at conservative breeding stock price

---

**Expense Analysis**

Your reported expenses: $18,000

Typical breakdown for 50-ewe operation:

| Category | % of Total | Your Estimate |
|----------|------------|---------------|
| Feed (hay, grain, mineral) | 45% | $8,100 |
| Pasture (rent, maintenance) | 15% | $2,700 |
| Health (vaccines, dewormer, vet) | 10% | $1,800 |
| Ram expense (amortized) | 5% | $900 |
| Marketing (transport, processing) | 8% | $1,440 |
| Equipment/facilities | 7% | $1,260 |
| Supplies/misc | 5% | $900 |
| Labor (hired) | 5% | $900 |
| **Total** | 100% | **$18,000** |

---

**Profitability Calculation**

| Metric | Amount |
|--------|--------|
| Total Revenue | $23,650 |
| Total Expenses | $18,000 |
| **Net Income** | **$5,650** |

---

**Key Performance Indicators**

| Metric | Your Operation | Industry Target | Assessment |
|--------|----------------|-----------------|------------|
| Lambing % | 160% (80/50) | 150%+ | EXCELLENT |
| Lamb mortality | 15% (80 born, 68 sold + 12 kept) | <10% | NEEDS WORK |
| Revenue/ewe | $473 | $400-500 | GOOD |
| Expense/ewe | $360 | $300-400 | AVERAGE |
| Profit/ewe | $113 | $75-150 | GOOD |
| Feed cost/ewe | ~$162 | $150-200 | AVERAGE |

---

**Strengths of Your Operation**

1. **Strong lambing percentage** (160%)
   - Above industry average
   - Indicates good ewe genetics and management

2. **Good lamb prices** ($275 average)
   - Above auction prices (~$200-240)
   - Suggests direct marketing or breeding stock sales

3. **Positive cash flow**
   - $5,650 net is solid for a 50-ewe flock

---

**Areas for Improvement**

1. **Lamb Mortality (15%)**

   You had 80 lambs born but only 80 accounted for (68 sold + 12 kept).

   If mortality is truly 15%, that's 12 lambs lost.
   Lost revenue: 12 x $275 = $3,300

   **Actions to reduce mortality:**
   - Better lambing supervision
   - Improved lamb housing
   - Earlier intervention for weak lambs
   - Review ewe nutrition in late gestation

2. **Feed Efficiency**

   At $8,100 for feed (estimated), you're spending $162/ewe.

   **Potential savings:**
   - Extended grazing season
   - Stockpiled forage
   - Better hay purchasing timing
   - Reduced waste in feeding

---

**What-If Scenarios**

**If you reduced lamb mortality to 5%:**
- 4 additional lambs sold
- Additional revenue: $1,100
- New net income: $6,750

**If you increased lambing to 180%:**
- 90 lambs instead of 80
- 10 additional lambs to sell
- Additional revenue: $2,750
- New net income: $8,400

**If you cut feed costs by 15%:**
- Savings: $1,215
- New net income: $6,865

---

**Year-Over-Year Tracking**

Start tracking these metrics annually:

| Year | Ewes | Lambs Born | % Sold | Avg Price | Revenue | Expenses | Profit |
|------|------|------------|--------|-----------|---------|----------|--------|
| 2024 | 50 | 80 | 68 | $275 | $23,650 | $18,000 | $5,650 |
| 2025 | | | | | | | |
| 2026 | | | | | | | |

---

**Recommendations for Next Year**

1. **Focus on lamb survival**
   - Target 90%+ survival
   - Worth $3,000+ in additional revenue

2. **Evaluate marketing channels**
   - Your $275 average is good
   - Could breeding stock sales increase this further?

3. **Track expenses by category**
   - Know exactly where money goes
   - Identify biggest savings opportunities

4. **Consider genetic investment**
   - Higher WWT genetics = heavier lambs
   - 5 lbs more per lamb x 70 lambs x $2/lb = $700/year

---

**Bottom Line**

Your operation is profitable at $113/ewe, which is above average for the industry. The biggest opportunity is reducing lamb mortality - this alone could add $1,000-3,000 to your bottom line.

Would you like to dive deeper into any of these areas?
```

---

## Quick Reference

### All 15 Tools at a Glance

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `nsip_get_last_update` | Database freshness | None |
| `nsip_list_breeds` | Available breeds | None |
| `nsip_get_statuses` | Animal status options | None |
| `nsip_get_trait_ranges` | Trait min/max by breed | breed_id |
| `nsip_search_animals` | Find animals | breed_id, sorted_trait, page |
| `nsip_get_animal` | Animal details | search_string (LPN ID) |
| `nsip_get_lineage` | Pedigree tree | lpn_id |
| `nsip_get_progeny` | Offspring list | lpn_id, page |
| `nsip_search_by_lpn` | Complete profile | lpn_id |
| `get_server_health` | Server metrics | None |
| `shepherd_consult` | General advice | question, region |
| `shepherd_breeding` | Genetics advice | question, region, production_goal |
| `shepherd_health` | Health/nutrition | question, region, life_stage |
| `shepherd_calendar` | Seasonal planning | question, region, task_type |
| `shepherd_economics` | Financial analysis | question, flock_size, market_focus |

### Common Breed IDs

| Breed | ID | Group |
|-------|----|----|
| Katahdin | 640 | Hair |
| Dorper | 641 | Hair |
| St. Croix | 642 | Hair |
| Suffolk | 690 | Terminal |
| Hampshire | 691 | Terminal |
| Texel | 692 | Terminal |
| Polypay | 621 | Maternal Wool |
| Targhee | 610 | Range |

### NSIP Regions

- `northeast` - New England, Mid-Atlantic
- `southeast` - South Atlantic, Gulf states
- `midwest` - Great Lakes, Corn Belt
- `southwest` - Texas, Oklahoma, New Mexico
- `mountain` - Rockies, Great Basin
- `pacific` - West Coast

---

*This document provides example prompts for the NSIP MCP Tools. For technical documentation, see [mcp-server.md](../mcp-server.md). For installation instructions, see [getting-started-guide.md](../getting-started-guide.md).*
