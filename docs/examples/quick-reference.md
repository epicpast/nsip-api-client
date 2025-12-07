# NSIP MCP Quick Reference

Single-page reference for experienced users. Find what you need in seconds.

---

## MCP Tools (15 Total)

### NSIP API Tools (10)

| Tool | What It Does | Example Prompt |
|------|--------------|----------------|
| `nsip_get_last_update` | Database timestamp | "When was the NSIP database last updated?" |
| `nsip_list_breeds` | Breed groups with individual breeds | "What breeds are available in NSIP?" |
| `nsip_get_statuses` | Animal status options (CURRENT, SOLD, etc.) | "What status values can animals have?" |
| `nsip_get_trait_ranges` | Min/max trait values for a breed | "What are the trait ranges for Katahdin?" |
| `nsip_search_animals` | Paginated search with filters | "Find Katahdin rams with high WWT" |
| `nsip_get_animal` | Full animal details + EBVs | "Get details for sheep 6332-12345" |
| `nsip_get_lineage` | Pedigree tree (sire/dam ancestry) | "Show the pedigree for 6332-12345" |
| `nsip_get_progeny` | Offspring list with pagination | "List all offspring of ram 6332-12345" |
| `nsip_search_by_lpn` | Complete profile (details+lineage+progeny) | "Give me everything about 6332-12345" |
| `get_server_health` | Server metrics and cache stats | "Check the server health status" |

### Shepherd Consultation Tools (5)

| Tool | What It Does | Example Prompt |
|------|--------------|----------------|
| `shepherd_consult` | General husbandry advice | "How do I introduce a new ram to my flock?" |
| `shepherd_breeding` | EBV interpretation, mating advice | "How should I interpret negative BWT EBVs?" |
| `shepherd_health` | Disease, nutrition, parasites | "Best deworming strategy for Southeast flocks?" |
| `shepherd_calendar` | Seasonal planning, schedules | "When should I prepare for fall lambing?" |
| `shepherd_economics` | Costs, ROI, market timing | "What's the ROI on a proven terminal sire?" |

---

## MCP Prompts

| Prompt | Type | Example Use |
|--------|------|-------------|
| `ebv_analyzer` | Single-shot | Compare EBVs: `lpn_ids="6332-001,6332-002"` |
| `flock_import` | Single-shot | Import spreadsheet: `file_path="my_flock.csv"` |
| `inbreeding_calculator` | Single-shot | Check COI: `lpn_id="6332-001"` or `mating="RAM,EWE"` |
| `mating_plan` | Guided interview | Optimize pairings: rams + ewes + goal + max COI |
| `progeny_report` | Single-shot | Sire evaluation: `sire_id="6332-001"` |
| `trait_improvement` | Guided interview | Multi-gen planning: target_trait + current + goal |
| `ancestry_builder` | Single-shot | Pedigree tree: `lpn_id="6332-001" generations=4` |
| `flock_dashboard` | Single-shot | Flock stats: `file_path="flock.csv"` |
| `selection_index` | Single-shot | Index scores: `lpn_ids + index_name` |
| `breeding_recommendations` | Guided interview | AI recommendations: rams + ewes + goal |
| `shepherd_consult` | Single-shot | General advice: `question + region` |
| `guided_mating_plan` | Multi-turn | Step-by-step mating plan creation |
| `guided_trait_improvement` | Multi-turn | Interactive improvement planning |

---

## MCP Resources

| URI Pattern | Returns | Example |
|-------------|---------|---------|
| `nsip://static/heritabilities` | Default heritabilities | `{BWT: {h2: 0.30}, WWT: {h2: 0.25}...}` |
| `nsip://static/heritabilities/{breed}` | Breed-specific h2 | `nsip://static/heritabilities/katahdin` |
| `nsip://static/indexes` | All selection indexes | Terminal, Maternal, Range, Hair, Balanced |
| `nsip://static/indexes/{name}` | Index definition + weights | `nsip://static/indexes/terminal` |
| `nsip://static/traits` | All trait definitions | Full glossary with units/interpretation |
| `nsip://static/traits/{code}` | Single trait info | `nsip://static/traits/WWT` |
| `nsip://static/regions` | All NSIP regions | 6 regions with states |
| `nsip://static/regions/{region}` | Region details | `nsip://static/regions/midwest` |
| `nsip://static/diseases/{region}` | Disease guide | `nsip://static/diseases/southeast` |
| `nsip://static/nutrition/{region}/{season}` | Feeding guide | `nsip://static/nutrition/midwest/spring` |
| `nsip://static/calendar` | Seasonal task templates | Monthly checklists |
| `nsip://static/economics/{category}` | Cost/revenue data | `nsip://static/economics/cost_templates` |

---

## Skills (Slash Commands)

| Command | Purpose | Example |
|---------|---------|---------|
| `/nsip:flock-import` | Import spreadsheet, enrich with NSIP EBVs | `/nsip:flock-import flock.csv --output enriched.csv` |
| `/nsip:ebv-analyzer` | Compare EBVs across animals | `/nsip:ebv-analyzer LPN1 LPN2 --traits WWT,PWWT` |
| `/nsip:inbreeding` | Calculate inbreeding coefficients | `/nsip:inbreeding LPN1 --mating DAM_LPN` |
| `/nsip:mating-plan` | Optimize ram-ewe pairings | `/nsip:mating-plan rams.csv ewes.csv --goal terminal` |
| `/nsip:progeny-report` | Evaluate sires by offspring | `/nsip:progeny-report SIRE_LPN --traits WWT,NLW` |
| `/nsip:trait-improvement` | Multi-generation selection planning | `/nsip:trait-improvement flock.csv --targets '{"WWT":5.0}'` |
| `/nsip:ancestry` | Generate pedigree trees | `/nsip:ancestry LPN1 --generations 4` |
| `/nsip:flock-dashboard` | Aggregate flock statistics | `/nsip:flock-dashboard flock.csv --name "My Flock"` |
| `/nsip:selection-index` | Calculate custom breeding indexes | `/nsip:selection-index flock.csv --index terminal` |
| `/nsip:breeding-recs` | AI-powered recommendations | `/nsip:breeding-recs flock.csv --goal terminal` |

---

## Common Tasks Cheat Sheet

| Task | Solution |
|------|----------|
| Find a Katahdin ram | `nsip_search_animals(breed_id=640, sorted_trait="WWT", reverse=True)` |
| Check an animal's pedigree | `nsip_get_lineage(lpn_id="6332-12345")` |
| Compare two animals | `/nsip:ebv-analyzer LPN1 LPN2 --traits BWT,WWT,PWWT,NLW` |
| Get breeding advice | `shepherd_breeding(question="...", region="midwest")` |
| Plan seasonal tasks | `shepherd_calendar(question="...", region="southeast", task_type="lambing")` |
| Analyze my flock | `/nsip:flock-dashboard my_flock.csv --name "Valley Farm"` |
| Check inbreeding risk | `/nsip:inbreeding --mating RAM_LPN,EWE_LPN` |
| Get complete animal profile | `nsip_search_by_lpn(lpn_id="6332-12345")` |
| Optimize mating plan | `/nsip:mating-plan rams.csv ewes.csv --max-inbreeding 5.0` |
| Plan trait improvement | `/nsip:trait-improvement flock.csv --targets '{"WWT":5.0}'` |

---

## NSIP Breed IDs

### Breed Groups

| ID | Group Name | Description |
|----|------------|-------------|
| 61 | Range | Rambouillet, Targhee |
| 62 | Maternal Wool | Columbia, Polypay |
| 64 | Hair | Katahdin, Dorper, St. Croix |
| 69 | Terminal | Suffolk, Hampshire, Texel |

### Common Individual Breeds

| ID | Breed |
|----|-------|
| 486 | South African Meat Merino |
| 610 | Targhee |
| 640 | Katahdin |
| 641 | St. Croix |
| 642 | Dorper |
| 643 | White Dorper |
| 690 | Suffolk |
| 691 | Hampshire |
| 692 | Texel |

---

## NSIP Trait Codes

### Growth Traits

| Code | Name | Units | Direction |
|------|------|-------|-----------|
| BWT | Birth Weight | lbs/kg | Lower better |
| WWT | Weaning Weight | lbs/kg | Higher better |
| MWWT | Maternal Weaning Weight | lbs/kg | Higher better |
| PWWT | Post-Weaning Weight | lbs/kg | Higher better |
| YWT | Yearling Weight | lbs/kg | Higher better |

### Carcass Traits

| Code | Name | Units | Direction |
|------|------|-------|-----------|
| YEMD | Yearling Eye Muscle Depth | mm | Higher better |
| YFAT | Yearling Fat Depth | mm | Context-dependent |
| PEMD | Post-Weaning Eye Muscle Depth | mm | Higher better |
| PFAT | Post-Weaning Fat Depth | mm | Context-dependent |

### Reproduction Traits

| Code | Name | Units | Direction |
|------|------|-------|-----------|
| NLB | Number of Lambs Born | count | Higher better |
| NLW | Number of Lambs Weaned | count | Higher better |

### Parasite Resistance

| Code | Name | Units | Direction |
|------|------|-------|-----------|
| WFEC | Weaning Fecal Egg Count | eggs/g | Lower better |
| PFEC | Post-Weaning Fecal Egg Count | eggs/g | Lower better |

### Wool Traits

| Code | Name | Units | Direction |
|------|------|-------|-----------|
| YGFW | Yearling Greasy Fleece Weight | lbs | Higher better |
| YFD | Yearling Fibre Diameter | microns | Lower better |
| YSL | Yearling Staple Length | mm | Higher better |

---

## Selection Indexes

| Index | Focus | Key Traits |
|-------|-------|------------|
| Terminal | Growth + carcass | WWT, PWWT, YEMD, -YFAT |
| Maternal | Reproduction | NLW, MWWT, -BWT |
| Range | Hardiness | WWT, NLW, fleece |
| Hair | Hair sheep | WWT, NLW, PFEC |
| Balanced | All traits equally | All |

---

## Shepherd Regions

| Region | States |
|--------|--------|
| `northeast` | ME, NH, VT, MA, RI, CT, NY, NJ, PA |
| `southeast` | MD, DE, VA, WV, NC, SC, GA, FL, AL, MS, LA, TN, KY |
| `midwest` | OH, IN, IL, MI, WI, MN, IA, MO, ND, SD, NE, KS |
| `southwest` | TX, OK, AR, AZ, NM |
| `mountain` | MT, WY, CO, UT, ID, NV |
| `pacific` | WA, OR, CA, AK, HI |

---

## Inbreeding Thresholds

| COI Range | Risk Level | Guidance |
|-----------|------------|----------|
| <6.25% | Low | Generally acceptable |
| 6.25-12.5% | Moderate | Consider alternatives |
| >12.5% | High | Avoid if possible |

---

## EBV Accuracy Levels

| Accuracy | Reliability | Data Source |
|----------|-------------|-------------|
| <40% | Low | Pedigree only |
| 40-70% | Moderate | Own + some progeny |
| >70% | High | Significant progeny data |

---

## Quick API Reference

### Tool Parameters

```
nsip_search_animals(
    page: int = 0,           # 0-indexed
    page_size: int = 15,     # 1-100
    breed_id: int = None,    # Filter by breed
    sorted_trait: str = None,# e.g., "WWT"
    reverse: bool = None,    # Descending order
    summarize: bool = False  # Reduce tokens
)

nsip_get_animal(
    search_string: str,      # LPN ID (min 5 chars)
    summarize: bool = False
)

shepherd_breeding(
    question: str,
    region: str = "midwest",
    production_goal: str = "balanced"  # terminal|maternal|balanced
)

shepherd_economics(
    question: str,
    flock_size: str = "medium",  # small|medium|large
    market_focus: str = "balanced"  # breeding_stock|market_lambs|balanced
)
```

---

## Server Health Metrics

| Metric | Target |
|--------|--------|
| Startup time | <3s |
| Tool discovery | <5s |
| Summarization | >=70% reduction |
| Validation | >=95% success |
| Cache hit rate | >=40% |
| Concurrent connections | 50+ |

---

## Transport Options

| Transport | Use Case | Command |
|-----------|----------|---------|
| stdio | Claude Desktop | `nsip-mcp-server` |
| HTTP | Web apps | `MCP_TRANSPORT=streamable-http MCP_PORT=8000 nsip-mcp-server` |
| WebSocket | Real-time | `MCP_TRANSPORT=websocket MCP_PORT=9000 nsip-mcp-server` |

---

## Error Codes

| Code | Meaning |
|------|---------|
| -32602 | Invalid parameters |
| -32000 | NSIP API error |
| -32001 | Cache error |
| -32002 | Summarization error |
| -32004 | Timeout error |
| -32005 | Resource not found |

---

*See full documentation: [MCP Server](../mcp-server.md) | [Prompts](../mcp-prompts.md) | [Resources](../mcp-resources.md) | [Skills](../nsip-skills.md)*
