# NSIP MCP Resources: Example Prompts and Templates

This guide provides practical examples for using NSIP MCP Resources. Resources offer URI-based access to static reference data and dynamic animal information, designed to help sheep producers make informed breeding decisions.

---

## Table of Contents

1. [What Are MCP Resources?](#what-are-mcp-resources)
2. [Static Reference Resources](#static-reference-resources)
   - [Heritabilities](#heritabilities)
   - [Selection Indexes](#selection-indexes)
   - [Trait Glossary](#trait-glossary)
   - [Region Information](#region-information)
   - [Disease Guides](#disease-guides)
   - [Nutrition Guidelines](#nutrition-guidelines)
   - [Calendar Templates](#calendar-templates)
   - [Economics Data](#economics-data)
3. [Animal Resources](#animal-resources)
   - [Animal Details](#animal-details)
   - [Animal Lineage](#animal-lineage)
   - [Animal Progeny](#animal-progeny)
   - [Complete Profile](#complete-profile)
4. [Breeding Resources](#breeding-resources)
   - [Offspring Projection](#offspring-projection)
   - [Inbreeding Analysis](#inbreeding-analysis)
   - [Mating Recommendation](#mating-recommendation)
5. [Flock Resources](#flock-resources)
   - [Flock Search Guidance](#flock-search-guidance)
   - [Flock Summary](#flock-summary)
   - [Flock EBV Averages](#flock-ebv-averages)
6. [Example Prompts That Leverage Resources](#example-prompts-that-leverage-resources)
7. [Combining Resources with Tools](#combining-resources-with-tools)
8. [Quick Reference Tables](#quick-reference-tables)

---

## What Are MCP Resources?

MCP Resources provide **URI-based access to data** through the Model Context Protocol. Unlike MCP Tools that execute operations, Resources expose read-only data through predictable URI patterns.

**Key Characteristics:**

- **URI Scheme**: All NSIP resources use the `nsip://` prefix
- **Read-Only**: Resources return data; they don't modify anything
- **Cached**: Static resources are cached for performance (LRU cache, 50 entries)
- **Structured**: Returns JSON with consistent schemas

**When to Use Resources vs Tools:**

| Use Resources For | Use Tools For |
|-------------------|---------------|
| Reference data (heritabilities, indexes) | Searching animals |
| Static knowledge (traits, regions) | Fetching live data with pagination |
| Contextual information for decisions | Performing calculations |
| Background knowledge for prompts | Server health monitoring |

---

## Static Reference Resources

Static resources serve knowledge base data that rarely changes. They provide the scientific foundation for breeding decisions.

### Heritabilities

Heritability values indicate how much of a trait's variation is genetic. Higher values mean faster progress through selection.

**URIs:**
- `nsip://static/heritabilities` - Default values for all breeds
- `nsip://static/heritabilities/{breed}` - Breed-specific values

**Available Breeds:** `default`, `katahdin`, `dorper`, `suffolk`, `hampshire`, `rambouillet`

**Example Prompts:**

```
"What are the heritabilities for Katahdin traits?"
```

Expected resource access: `nsip://static/heritabilities/katahdin`

```
"How heritable is weaning weight compared to number of lambs weaned?"
```

Expected resource access: `nsip://static/heritabilities`

**Sample Response:**
```json
{
  "heritabilities": {
    "BWT": {"heritability": 0.30, "genetic_sd": 0.5, "units": "lbs"},
    "WWT": {"heritability": 0.25, "genetic_sd": 3.0, "units": "lbs"},
    "PWWT": {"heritability": 0.30, "genetic_sd": 4.0, "units": "lbs"},
    "NLW": {"heritability": 0.10, "genetic_sd": 0.15, "units": "count"},
    "YEMD": {"heritability": 0.35, "genetic_sd": 1.5, "units": "mm"},
    "YFAT": {"heritability": 0.25, "genetic_sd": 0.8, "units": "mm"}
  },
  "breed": "katahdin"
}
```

**Interpretation Guidance:**
- **High heritability (>0.30)**: Fast progress, respond well to selection (e.g., YEMD, PWWT)
- **Moderate heritability (0.15-0.30)**: Steady progress with consistent selection (e.g., WWT, BWT)
- **Low heritability (<0.15)**: Slow progress, consider management improvements (e.g., NLW, NLB)

---

### Selection Indexes

Pre-defined trait weightings for common breeding goals. Indexes combine multiple EBVs into a single ranking value.

**URIs:**
- `nsip://static/indexes` - List all available indexes
- `nsip://static/indexes/{index_name}` - Specific index details

**Available Indexes:**

| Index Name | Purpose | Primary Traits |
|------------|---------|----------------|
| `terminal` | Maximum growth and carcass merit | PWWT, YEMD, WWT |
| `maternal` | Reproductive efficiency | NLW, NLB, MWWT |
| `range` | Hardiness for extensive systems | WWT, NLW, MWWT |
| `hair` | Hair sheep production | NLW, FEC, PWWT |
| `balanced` | Equal growth and maternal | All traits |
| `growth_only` | Pure growth emphasis | PWWT, YWT, WWT |
| `parasite_resistance` | Parasite resistance focus | FEC, DAG |
| `wool_merit` | Wool production emphasis | CFW, FD, GFW |

**Example Prompts:**

```
"Show me the Terminal Sire Index formula and what it's used for."
```

Expected resource access: `nsip://static/indexes/terminal`

```
"Which selection index should I use for Katahdin sheep?"
```

Expected resource access: `nsip://static/indexes/hair`

```
"What traits are in the maternal index and how are they weighted?"
```

Expected resource access: `nsip://static/indexes/maternal`

**Sample Response (Terminal Index):**
```json
{
  "index": {
    "name": "Terminal Sire Index",
    "description": "Maximizes growth and carcass traits for market lamb production.",
    "weights": {
      "BWT": -0.5,
      "WWT": 1.0,
      "PWWT": 1.5,
      "YWT": 1.0,
      "YEMD": 0.8,
      "YFAT": -0.3
    },
    "use_case": "Use for terminal sire breeds (Suffolk, Hampshire, Texel) where all offspring go to market.",
    "breed_focus": ["suffolk", "hampshire", "texel", "charollais"]
  },
  "name": "terminal"
}
```

**Weight Interpretation:**
- **Positive weights**: Higher EBV values improve the index score
- **Negative weights**: Lower EBV values improve the index score (e.g., BWT, YFAT)
- **Larger magnitude**: Greater emphasis on that trait

---

### Trait Glossary

Comprehensive definitions for all NSIP EBV traits, including units, interpretation, and category.

**URIs:**
- `nsip://static/traits` - List all available traits
- `nsip://static/traits/{trait_code}` - Specific trait details

**Trait Categories:**

| Category | Traits | Description |
|----------|--------|-------------|
| Growth | BWT, WWT, PWWT, YWT | Body weight and growth rate |
| Carcass | YEMD, YFAT, PFAT | Meat yield and quality |
| Maternal | NLB, NLW, MWWT | Reproduction and mothering |
| Health | FEC, DAG | Disease and parasite resistance |
| Wool | GFW, CFW, FD, SL, SS | Fleece production and quality |

**Example Prompts:**

```
"What does the WWT trait mean and how should I interpret it?"
```

Expected resource access: `nsip://static/traits/WWT`

```
"Explain the difference between direct growth traits and maternal traits."
```

Expected resource access: `nsip://static/traits` (for category information)

```
"What is post-weaning weight and why is it important for terminal sires?"
```

Expected resource access: `nsip://static/traits/PWWT`

**Sample Response (WWT):**
```json
{
  "trait": {
    "name": "Weaning Weight",
    "description": "Genetic potential for weight at weaning (60-day adjusted). Higher values indicate faster pre-weaning growth.",
    "unit": "lbs",
    "interpretation": "higher_better",
    "category": "growth",
    "notes": "Heavily influenced by maternal effects (milk, mothering). Direct WWT measures lamb's own growth genes; MWWT measures dam's contribution."
  },
  "code": "WWT"
}
```

**Common Trait Codes Quick Reference:**

| Code | Full Name | Higher is Better? |
|------|-----------|-------------------|
| BWT | Birth Weight | Context-dependent (moderate preferred) |
| WWT | Weaning Weight | Yes |
| PWWT | Post-Weaning Weight | Yes |
| NLW | Number of Lambs Weaned | Yes |
| NLB | Number of Lambs Born | Yes |
| MWWT | Maternal Weaning Weight | Yes |
| YEMD | Yearling Eye Muscle Depth | Yes |
| YFAT | Yearling Fat Depth | No (leaner preferred) |
| FEC | Fecal Egg Count | No (lower = more resistant) |

---

### Region Information

NSIP regions with climate, common breeds, challenges, and opportunities.

**URIs:**
- `nsip://static/regions` - List all regions
- `nsip://static/regions/{region_id}` - Specific region details

**Available Regions:**

| Region ID | Name | States Covered |
|-----------|------|----------------|
| `northeast` | Northeast | ME, NH, VT, MA, RI, CT, NY, NJ, PA |
| `southeast` | Southeast | MD, DE, VA, WV, NC, SC, GA, FL, AL, MS, LA, TN, KY |
| `midwest` | Midwest | OH, IN, IL, MI, WI, MN, IA, MO, ND, SD, NE, KS |
| `southwest` | Southwest | TX, OK, AR, AZ, NM |
| `mountain` | Mountain | MT, WY, CO, UT, ID, NV |
| `pacific` | Pacific | WA, OR, CA, AK, HI |

**Example Prompts:**

```
"What breeds work best in the Southeast region?"
```

Expected resource access: `nsip://static/regions/southeast`

```
"What challenges should I expect raising sheep in Texas?"
```

Expected resource access: `nsip://static/regions/southwest`

```
"When is parasite season in the Midwest?"
```

Expected resource access: `nsip://static/regions/midwest`

**Sample Response (Southeast):**
```json
{
  "region": {
    "name": "Southeast",
    "states": ["MD", "DE", "VA", "WV", "NC", "SC", "GA", "FL", "AL", "MS", "LA", "TN", "KY"],
    "climate": "humid_subtropical",
    "primary_breeds": ["Katahdin", "St. Croix", "Dorper", "Gulf Coast Native", "Barbados Blackbelly"],
    "typical_lambing": "Fall preferred, year-round possible",
    "challenges": [
      "Severe internal parasite pressure (Haemonchus)",
      "Heat stress in summer",
      "Endophyte-infected tall fescue",
      "High humidity promotes disease",
      "Foot rot very common"
    ],
    "opportunities": [
      "Year-round grazing possible",
      "Ethnic market demand strong",
      "Growing interest in hair sheep",
      "Low winter feed costs"
    ],
    "parasite_season": "Year-round (peaks March-October)"
  },
  "id": "southeast"
}
```

---

### Disease Guides

Region-specific disease prevention and management guidance.

**URI:** `nsip://static/diseases/{region}`

**Example Prompts:**

```
"What health challenges are common in the Southeast?"
```

Expected resource access: `nsip://static/diseases/southeast`

```
"How do I prevent Haemonchus in my flock?"
```

Expected resource access: `nsip://static/diseases/southeast` (where Haemonchus is most problematic)

```
"What diseases should I vaccinate for in the Midwest?"
```

Expected resource access: `nsip://static/diseases/midwest`

**Sample Response:**
```json
{
  "diseases": {
    "Haemonchus contortus": {
      "risk_level": "high",
      "season": "spring-fall",
      "prevention": "FAMACHA scoring, targeted selective treatment, pasture rotation",
      "signs": ["bottle jaw", "pale membranes", "weakness"],
      "treatment": "Effective anthelmintic based on FECRT"
    },
    "Ovine Progressive Pneumonia": {
      "risk_level": "moderate",
      "season": "year-round",
      "prevention": "Test and cull positive animals, closed flock",
      "signs": ["chronic weight loss", "respiratory distress", "hard udder"],
      "treatment": "No cure; manage through prevention"
    }
  },
  "region": "southeast"
}
```

---

### Nutrition Guidelines

Life-stage nutrition requirements with regional adjustments.

**URI:** `nsip://static/nutrition/{region}/{season}`

**Life Stages (Season Parameter):**
- `maintenance` - Non-pregnant, non-lactating ewes
- `flushing` - Pre-breeding nutrition boost
- `gestation` - Pregnant ewes (early and late)
- `lactation` - Nursing ewes

**Example Prompts:**

```
"What should I feed lactating ewes in the Midwest?"
```

Expected resource access: `nsip://static/nutrition/midwest/lactation`

```
"How much protein do ewes need during late gestation?"
```

Expected resource access: `nsip://static/nutrition/{region}/gestation`

```
"What supplements are important in the Pacific Northwest?"
```

Expected resource access: `nsip://static/nutrition/pacific/maintenance`

**Sample Response:**
```json
{
  "nutrition": {
    "life_stage": "lactation",
    "requirements": {
      "energy": {
        "singles": "4.0-4.5 Mcal ME/day",
        "twins": "5.0-6.0 Mcal ME/day"
      },
      "protein": {
        "singles": "13-15% CP",
        "twins": "15-17% CP"
      },
      "minerals": "High calcium, selenium, zinc",
      "water": "2.5-4 gallons/day"
    },
    "regional_notes": [
      "Selenium supplementation recommended in Midwest",
      "Spring pasture may cause grass tetany"
    ],
    "feed_options": [
      "High-quality hay + grain supplement",
      "Improved pasture with protein supplement",
      "Total mixed ration"
    ]
  },
  "region": "midwest",
  "season": "lactation"
}
```

---

### Calendar Templates

Seasonal management task checklists.

**URI:** `nsip://static/calendar/{task_type}`

**Task Types:** `breeding`, `lambing`, `shearing`, `health`

**Example Prompts:**

```
"What should I do to prepare for lambing season?"
```

Expected resource access: `nsip://static/calendar/lambing`

```
"When should I vaccinate my flock?"
```

Expected resource access: `nsip://static/calendar/health`

---

### Economics Data

Cost templates and economic analysis guidance.

**URI:** `nsip://static/economics/{category}`

**Categories:** `cost_templates`, `revenue_templates`, `feed_costs`

**Example Prompts:**

```
"What are typical annual costs per ewe?"
```

Expected resource access: `nsip://static/economics/cost_templates`

```
"How much does it cost to raise a lamb to market weight?"
```

Expected resource access: `nsip://static/economics/cost_templates`

---

## Animal Resources

Animal resources provide dynamic access to live NSIP API data for individual animals.

### Animal Details

Full details for a specific animal including EBVs, breed, and status.

**URI:** `nsip://animals/{lpn_id}/details`

**Example Prompts:**

```
"Look up the EBVs for animal 633292020054249"
```

Expected resource access: `nsip://animals/633292020054249/details`

```
"What breed is animal 644312019012345?"
```

Expected resource access: `nsip://animals/644312019012345/details`

**Sample Response:**
```json
{
  "animal": {
    "lpn_id": "633292020054249",
    "name": "SMITH FARMS 249",
    "sex": "M",
    "birth_date": "2020-03-15",
    "breed": "Katahdin",
    "status": "A",
    "ebvs": {
      "BWT": 0.3,
      "WWT": 4.2,
      "PWWT": 6.8,
      "NLW": 0.15,
      "FEC": -0.8
    },
    "accuracies": {
      "BWT": 0.65,
      "WWT": 0.58,
      "PWWT": 0.52
    }
  },
  "lpn_id": "633292020054249"
}
```

---

### Animal Lineage

Pedigree/ancestry tree for an animal.

**URI:** `nsip://animals/{lpn_id}/lineage`

**Example Prompts:**

```
"Show me the pedigree for ram 633292020054249"
```

Expected resource access: `nsip://animals/633292020054249/lineage`

```
"Who are the parents and grandparents of this ewe?"
```

Expected resource access: `nsip://animals/{lpn_id}/lineage`

**Sample Response:**
```json
{
  "lineage": {
    "animal": {
      "lpn_id": "633292020054249",
      "name": "SMITH FARMS 249"
    },
    "sire": {
      "lpn_id": "633292018032100",
      "name": "SMITH FARMS 100",
      "sire": { "lpn_id": "...", "name": "..." },
      "dam": { "lpn_id": "...", "name": "..." }
    },
    "dam": {
      "lpn_id": "633292017045088",
      "name": "SMITH FARMS 088",
      "sire": { "lpn_id": "...", "name": "..." },
      "dam": { "lpn_id": "...", "name": "..." }
    }
  },
  "lpn_id": "633292020054249"
}
```

---

### Animal Progeny

List of offspring for an animal (typically used for rams/sires).

**URI:** `nsip://animals/{lpn_id}/progeny`

**Example Prompts:**

```
"How many offspring has this ram produced?"
```

Expected resource access: `nsip://animals/{lpn_id}/progeny`

```
"Show me the lambs sired by ram 633292018032100"
```

Expected resource access: `nsip://animals/633292018032100/progeny`

---

### Complete Profile

Combined details, lineage, and progeny in one request.

**URI:** `nsip://animals/{lpn_id}/profile`

**Example Prompts:**

```
"Give me the complete profile for ram 633292020054249"
```

Expected resource access: `nsip://animals/633292020054249/profile`

**Note:** This is a convenience resource that combines three API calls. For performance-critical applications, prefer individual resources.

---

## Breeding Resources

Breeding resources analyze potential mating pairs for projected outcomes.

### Offspring Projection

Project expected EBVs for offspring from a specific ram and ewe pairing.

**URI:** `nsip://breeding/{ram_lpn}/{ewe_lpn}/projection`

**Example Prompts:**

```
"What EBVs would offspring from ram 633292020054249 and ewe 644312019012345 have?"
```

Expected resource access: `nsip://breeding/633292020054249/644312019012345/projection`

```
"Project the offspring genetics if I mate these two animals"
```

Expected resource access: `nsip://breeding/{ram_lpn}/{ewe_lpn}/projection`

**Sample Response:**
```json
{
  "projection": {
    "offspring_ebvs": {
      "WWT": {
        "value": 3.5,
        "sire_contribution": 4.2,
        "dam_contribution": 2.8,
        "heritability": 0.25
      },
      "PWWT": {
        "value": 5.2,
        "sire_contribution": 6.8,
        "dam_contribution": 3.6,
        "heritability": 0.30
      }
    },
    "sire": { "lpn_id": "633292020054249", "ebvs": {...} },
    "dam": { "lpn_id": "644312019012345", "ebvs": {...} }
  },
  "ram_lpn": "633292020054249",
  "ewe_lpn": "644312019012345"
}
```

**Key Concept:** Offspring EBV = (Sire EBV + Dam EBV) / 2

---

### Inbreeding Analysis

Calculate projected inbreeding coefficient for offspring.

**URI:** `nsip://breeding/{ram_lpn}/{ewe_lpn}/inbreeding`

**Example Prompts:**

```
"Are ram 633292020054249 and ewe 644312019012345 related?"
```

Expected resource access: `nsip://breeding/633292020054249/644312019012345/inbreeding`

```
"What is the inbreeding risk if I mate these animals?"
```

Expected resource access: `nsip://breeding/{ram_lpn}/{ewe_lpn}/inbreeding`

**Sample Response:**
```json
{
  "inbreeding": {
    "coefficient": 0.0312,
    "percentage": 3.12,
    "common_ancestors": ["633292015021050"],
    "common_ancestor_count": 1,
    "risk_level": "moderate",
    "recommendation": "Consider alternatives. Moderate inbreeding may reduce vigor."
  },
  "ram_lpn": "633292020054249",
  "ewe_lpn": "644312019012345"
}
```

**Risk Level Thresholds:**
- **Low (<3%)**: Acceptable mating
- **Moderate (3-6.25%)**: Consider alternatives
- **High (>6.25%)**: Avoid this mating

---

### Mating Recommendation

Comprehensive analysis with overall recommendation.

**URI:** `nsip://breeding/{ram_lpn}/{ewe_lpn}/recommendation`

**Example Prompts:**

```
"Should I breed ram 633292020054249 to ewe 644312019012345?"
```

Expected resource access: `nsip://breeding/633292020054249/644312019012345/recommendation`

```
"Give me a breeding recommendation for this pair"
```

Expected resource access: `nsip://breeding/{ram_lpn}/{ewe_lpn}/recommendation`

**Sample Response:**
```json
{
  "recommendation": {
    "decision": "proceed",
    "summary": "Good genetic match. Mating should produce quality offspring.",
    "projected_ebvs": {
      "BWT": 0.2,
      "WWT": 3.5,
      "PWWT": 5.2,
      "NLW": 0.12
    },
    "inbreeding_coefficient": 0.0156,
    "strengths": [
      "Strong post-weaning growth potential",
      "Good weaning weight genetics"
    ],
    "concerns": []
  },
  "ram_lpn": "633292020054249",
  "ewe_lpn": "644312019012345"
}
```

**Decision Values:**
- **proceed**: Good match, no significant concerns
- **caution**: Some concerns exist, weigh benefits against risks
- **avoid**: High inbreeding or significant genetic concerns

---

## Flock Resources

Flock resources provide aggregated data across multiple animals.

### Flock Search Guidance

Information about how to search for animals in a flock.

**URI:** `nsip://flock/search`

**Example Prompts:**

```
"How do I search for all animals in my flock?"
```

Expected resource access: `nsip://flock/search`

---

### Flock Summary

Summary statistics for animals with a common flock prefix.

**URI:** `nsip://flock/{flock_id}/summary`

**Example Prompts:**

```
"Give me a summary of flock 6332"
```

Expected resource access: `nsip://flock/6332/summary`

```
"How many rams and ewes are in flock 6443?"
```

Expected resource access: `nsip://flock/6443/summary`

**Sample Response:**
```json
{
  "summary": {
    "total_animals": 85,
    "sex_breakdown": { "males": 12, "females": 73 },
    "status_breakdown": { "A": 78, "D": 5, "C": 2 },
    "birth_years": { "2024": 25, "2023": 30, "2022": 20, "2021": 10 }
  },
  "flock_id": "6332"
}
```

---

### Flock EBV Averages

Average EBVs across all animals in a flock.

**URI:** `nsip://flock/{flock_id}/ebv_averages`

**Example Prompts:**

```
"What are the average EBVs for flock 6332?"
```

Expected resource access: `nsip://flock/6332/ebv_averages`

```
"How does my flock compare on weaning weight?"
```

Expected resource access: `nsip://flock/{flock_id}/ebv_averages`

**Sample Response:**
```json
{
  "ebv_averages": {
    "WWT": { "average": 2.85, "min": -1.2, "max": 6.8, "count": 78 },
    "PWWT": { "average": 4.12, "min": -0.5, "max": 9.2, "count": 72 },
    "NLW": { "average": 0.08, "min": -0.15, "max": 0.35, "count": 45 }
  },
  "flock_id": "6332",
  "total_animals": 85,
  "traits_measured": ["WWT", "PWWT", "NLW", "BWT", "MWWT"]
}
```

---

## Example Prompts That Leverage Resources

Here are complete example prompts that demonstrate effective use of NSIP MCP Resources:

### Understanding Breed-Specific Genetics

```
"I'm starting a Katahdin flock in Georgia. What traits should I focus on
and what are realistic heritability expectations?"
```

Resources accessed:
- `nsip://static/heritabilities/katahdin`
- `nsip://static/regions/southeast`
- `nsip://static/indexes/hair`

### Evaluating a Potential Ram Purchase

```
"I'm considering buying ram 633292020054249 for my commercial flock.
Can you evaluate his EBVs and tell me if he'd be a good terminal sire?"
```

Resources accessed:
- `nsip://animals/633292020054249/details`
- `nsip://animals/633292020054249/progeny`
- `nsip://static/indexes/terminal`
- `nsip://static/traits/PWWT`
- `nsip://static/traits/YEMD`

### Planning a Mating

```
"Will ram 633292020054249 and ewe 644312019012345 make a good match?
What would their lambs be like and is there any inbreeding concern?"
```

Resources accessed:
- `nsip://breeding/633292020054249/644312019012345/recommendation`
- `nsip://breeding/633292020054249/644312019012345/projection`
- `nsip://breeding/633292020054249/644312019012345/inbreeding`

### Regional Health Planning

```
"I'm moving my flock from Ohio to Kentucky. What health challenges
should I expect and how should I adjust my parasite management?"
```

Resources accessed:
- `nsip://static/regions/midwest` (Ohio)
- `nsip://static/regions/southeast` (Kentucky)
- `nsip://static/diseases/southeast`

### Selection Index Customization

```
"I want to select for both growth and parasite resistance in my hair sheep.
Which index should I use and how does it weight the traits?"
```

Resources accessed:
- `nsip://static/indexes/hair`
- `nsip://static/traits/FEC`
- `nsip://static/traits/PWWT`
- `nsip://static/heritabilities/katahdin`

---

## Combining Resources with Tools

Resources and Tools work together: **Resources provide context, Tools provide live data.**

### Pattern 1: Context + Search

First get context from resources, then search with tools:

```
User: "Find high-growth Katahdin rams in the NSIP database"

1. Access resource: nsip://static/indexes/hair
   → Learn key traits: PWWT, WWT, NLW

2. Access resource: nsip://static/traits/PWWT
   → Understand interpretation: higher_better

3. Use tool: nsip_search_animals(breed_group=64, sex="M")
   → Get live search results

4. Interpret results using trait knowledge from resources
```

### Pattern 2: Breeding Decision Workflow

Combine breeding resources with animal tools:

```
User: "Help me plan matings for my 5 ewes using my new ram"

1. Use tool: nsip_get_animal(lpn_id="ram_id")
   → Get ram's complete EBVs

2. For each ewe:
   a. Access resource: nsip://breeding/{ram}/{ewe}/recommendation
      → Get mating recommendation

   b. Access resource: nsip://breeding/{ram}/{ewe}/inbreeding
      → Check inbreeding risk

3. Access resource: nsip://static/indexes/{production_goal}
   → Use to rank matings by breeding goal
```

### Pattern 3: Flock Analysis with Context

```
User: "How does my flock compare to breed averages?"

1. Access resource: nsip://flock/{flock_id}/ebv_averages
   → Get flock statistics

2. Access resource: nsip://static/heritabilities/{breed}
   → Get breed context

3. Access resource: nsip://static/traits/{trait}
   → Understand interpretation for each trait

4. Compare flock averages to breed expectations
```

---

## Quick Reference Tables

### All Static Resource URIs

| URI Pattern | Description | Parameters |
|-------------|-------------|------------|
| `nsip://static/heritabilities` | Default heritabilities | None |
| `nsip://static/heritabilities/{breed}` | Breed-specific heritabilities | breed |
| `nsip://static/indexes` | All selection indexes | None |
| `nsip://static/indexes/{index_name}` | Specific index | index_name |
| `nsip://static/traits` | All trait definitions | None |
| `nsip://static/traits/{trait_code}` | Specific trait | trait_code |
| `nsip://static/regions` | All regions | None |
| `nsip://static/regions/{region_id}` | Specific region | region_id |
| `nsip://static/diseases/{region}` | Disease guide | region |
| `nsip://static/nutrition/{region}/{season}` | Nutrition guide | region, season |
| `nsip://static/calendar/{task_type}` | Calendar template | task_type |
| `nsip://static/economics/{category}` | Economics data | category |

### All Dynamic Resource URIs

| URI Pattern | Description | Parameters |
|-------------|-------------|------------|
| `nsip://animals/{lpn_id}/details` | Animal details | lpn_id |
| `nsip://animals/{lpn_id}/lineage` | Pedigree tree | lpn_id |
| `nsip://animals/{lpn_id}/progeny` | Offspring list | lpn_id |
| `nsip://animals/{lpn_id}/profile` | Complete profile | lpn_id |
| `nsip://breeding/{ram}/{ewe}/projection` | Offspring EBV projection | ram_lpn, ewe_lpn |
| `nsip://breeding/{ram}/{ewe}/inbreeding` | Inbreeding analysis | ram_lpn, ewe_lpn |
| `nsip://breeding/{ram}/{ewe}/recommendation` | Mating recommendation | ram_lpn, ewe_lpn |
| `nsip://flock/search` | Search guidance | None |
| `nsip://flock/{flock_id}/summary` | Flock summary | flock_id |
| `nsip://flock/{flock_id}/ebv_averages` | Flock EBV averages | flock_id |

### Breed Names for Heritabilities

| Parameter | Breeds Covered |
|-----------|----------------|
| `default` | General sheep populations |
| `katahdin` | Katahdin hair sheep |
| `dorper` | Dorper and White Dorper |
| `suffolk` | Suffolk terminal sires |
| `hampshire` | Hampshire terminal sires |
| `rambouillet` | Rambouillet range sheep |

### Region IDs

| Region ID | Full Name |
|-----------|-----------|
| `northeast` | Northeast |
| `southeast` | Southeast |
| `midwest` | Midwest |
| `southwest` | Southwest |
| `mountain` | Mountain |
| `pacific` | Pacific |

---

## See Also

- [MCP Resources Documentation](/docs/mcp-resources.md) - Complete technical reference
- [MCP Server Documentation](/docs/mcp-server.md) - Tools and transport configuration
- [MCP Prompts Documentation](/docs/mcp-prompts.md) - Guided workflow prompts
- [Shepherd Agent Documentation](/docs/shepherd-agent.md) - AI-powered breeding advisor
- [NSIP Skills Documentation](/docs/nsip-skills.md) - Breeding analysis CLI tools

---

*Last Updated: December 2025*
