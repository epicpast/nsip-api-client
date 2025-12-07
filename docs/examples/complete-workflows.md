# Complete Workflows for NSIP Tools

Real-world, end-to-end examples showing how to combine NSIP tools, prompts, resources, and skills to accomplish common sheep breeding tasks.

---

## Table of Contents

1. [Introduction](#introduction)
2. [Workflow: Evaluating a Ram for Purchase](#workflow-evaluating-a-ram-for-purchase)
3. [Workflow: Planning Next Season's Matings](#workflow-planning-next-seasons-matings)
4. [Workflow: Flock Health Planning](#workflow-flock-health-planning)
5. [Workflow: Evaluating Your Ram's Performance](#workflow-evaluating-your-rams-performance)
6. [Workflow: Starting a New Breeding Program](#workflow-starting-a-new-breeding-program)
7. [Quick Reference](#quick-reference)

---

## Introduction

The NSIP tools provide multiple ways to access sheep breeding data and get expert guidance:

| Component | What It Does | When to Use |
|-----------|--------------|-------------|
| **Tools** | Direct data lookup from NSIP database | Fetching animal details, lineage, progeny |
| **Prompts** | Structured analysis workflows | Comparing animals, calculating inbreeding |
| **Resources** | Static knowledge and reference data | Trait heritabilities, regional info, indexes |
| **Skills** | Complex breeding calculations | Flock statistics, mating optimization |
| **Shepherd** | Expert AI advice on breeding decisions | Interpreting data, making decisions |

### How to Use This Guide

Each workflow shows:
- **Goal**: What you are trying to accomplish
- **Tools Used**: Which NSIP capabilities are involved
- **Step-by-Step Instructions**: Exact prompts you can copy and use
- **What to Expect**: Sample outputs and how to interpret them

Replace example LPN IDs with your own animals' IDs when following these workflows.

---

## Workflow: Evaluating a Ram for Purchase

**Goal**: Thoroughly evaluate a ram before committing to a purchase. Understand his genetics, pedigree, and proven performance.

**Scenario**: You found a promising ram at a sale or breeder's website. His LPN ID is listed as `6402382023ABC456`. Should you buy him?

### Step 1: Look Up the Ram's Profile

Get his complete genetic profile including all EBVs and basic information.

**Prompt to use:**

```
Look up the complete profile for the ram with LPN ID 6402382023ABC456.
I need his breeding values, breed, birth date, and current status.
```

**What you will see:**
- LPN ID and registration details
- Breed and birth date
- All available EBV traits (BWT, WWT, PWWT, NLW, MWWT, etc.)
- Accuracy values for each trait
- Contact information for the breeder

**Key things to check:**
- Are the accuracy values high (above 60%)? Higher accuracy means more reliable predictions.
- Is he still listed as CURRENT status? (vs. SOLD, DEAD, etc.)

### Step 2: Check His Lineage

Understanding his pedigree helps you know what genetics you are bringing in.

**Prompt to use:**

```
Show me the pedigree for ram 6402382023ABC456. I want to see at least 3
generations of ancestors - his sire, dam, and grandparents.
```

**What you will see:**
- Sire and dam LPN IDs and names
- Grandparents on both sides
- Farm names showing where ancestors came from

**Key things to check:**
- Do you recognize any lines? Some bloodlines are known for specific traits.
- Are there any common ancestors in the pedigree (possible inbreeding)?
- Do the sire's and dam's farms have good reputations?

### Step 3: Review His Progeny Performance

If this ram has been used for breeding, his offspring tell the real story.

**Prompt to use:**

```
Generate a progeny report for ram 6402382023ABC456. Show me how many
offspring he has, their average EBVs, and identify his top performers.
```

**What you will see:**
- Total number of offspring
- Male vs. female lamb counts
- Average EBVs for key traits across all progeny
- List of top and bottom performing offspring

**Key things to check:**
- Does he have enough progeny (10+) for reliable evaluation?
- Are his progeny averages consistent with his own EBVs?
- Are his top performers significantly better than average?

**No progeny yet?**

If the ram is young and has no offspring, that is normal. You will rely more heavily on his own EBVs and his parents' records.

### Step 4: Compare to Breed Averages

Understand how this ram stacks up against the breed population.

**Prompt to use:**

```
Compare ram 6402382023ABC456 to the breed average for Katahdin (or whatever
his breed is). Show me where he ranks for growth traits and maternal traits.
```

**Alternative - get breed trait ranges:**

```
What are the trait ranges for Katahdin sheep? I want to know the min and max
values for WWT, PWWT, and NLW so I can evaluate a ram I'm considering.
```

**What you will see:**
- Breed population min/max for each trait
- Percentile ranking (where he falls in the population)
- Whether his values are above or below breed average

**Key things to check:**
- Is he in the top 25% for traits you care about?
- Any traits where he is below average (red flags)?
- How does he compare on the traits most important to your goals?

### Step 5: Get AI Breeding Advice

Bring it all together with expert interpretation of the data.

**Prompt to use:**

```
I'm considering buying ram 6402382023ABC456 for my terminal production
program in the Southeast. Based on his breeding values, pedigree, and
progeny performance, is he a good fit for producing fast-growing market
lambs? What are his strengths and weaknesses?
```

**What you will see:**
- Summary of his genetic strengths (which traits he excels at)
- Potential concerns or weaknesses
- Fit for your specific production goals
- Recommendations on how to use him if you purchase

**Key things to ask the Shepherd:**

```
What price range would be reasonable for a ram with these EBVs? Is the
genetic improvement worth a premium price?
```

### Decision Checklist

Before buying, confirm:

- [ ] EBVs are above breed average for your priority traits
- [ ] Accuracy values are reasonable (ideally 50%+ for young ram, 70%+ for proven sire)
- [ ] Pedigree does not introduce inbreeding concerns with your ewes
- [ ] Progeny (if any) confirm his genetic potential
- [ ] Price is justified by genetic merit
- [ ] He fits your production goals (terminal, maternal, etc.)

---

## Workflow: Planning Next Season's Matings

**Goal**: Create an optimized mating plan that improves your flock's genetics while avoiding inbreeding.

**Scenario**: You have 2 rams and 25 ewes. You want to match rams to ewes strategically for the best offspring.

### Step 1: Import Your Flock Data

Start by getting your flock's current genetic profile into the system.

**Option A - If you have a spreadsheet:**

```
I have a CSV file with my flock data at /path/to/my_flock.csv. Import it
and enrich with current NSIP EBVs. The file has columns for LPN_ID, Name,
Sex, and Birth_Date.
```

**Option B - If you know your flock prefix:**

```
Generate a flock dashboard for my flock. My flock prefix is 6402. Show me
all current animals and their average EBVs.
```

**Option C - If you have individual LPNs:**

```
Look up these animals from my flock and show me their EBVs:
Rams: 6402382022RAM001, 6402382021RAM002
Ewes: 6402382020EWE001, 6402382020EWE002, 6402382019EWE003
(add all your ewes...)
```

### Step 2: Analyze Current Flock Strengths and Weaknesses

Understand where your flock stands genetically.

**Prompt to use:**

```
Analyze the EBVs for my flock (LPNs listed above). Compare them across
BWT, WWT, PWWT, NLW, and MWWT. Which traits are our strengths? Which need
improvement? Rank my animals from best to worst on overall genetic merit.
```

**What you will see:**
- Trait-by-trait statistics (average, min, max, variation)
- Animals ranked for each trait
- Overall top performers and underperformers
- Identification of flock-wide weaknesses

**Key things to note:**
- Which traits show the most variation (room for improvement)?
- Which ewes are your genetic elite (keep their daughters)?
- Which ewes are below average (consider culling)?

### Step 3: Identify Trait Improvement Goals

Set specific, measurable breeding objectives.

**Prompt to use:**

```
I want to create a trait improvement plan for my Katahdin flock. My current
flock averages:
- WWT (Weaning Weight): +2.5 lbs
- NLW (Number Lambs Weaned): +0.08

I want to improve WWT to +4.0 lbs and NLW to +0.15 over the next 3
generations. Is this realistic? What selection intensity do I need?
```

**What you will see:**
- Expected genetic progress per generation
- Heritability information for each trait
- Whether your goals are achievable
- Recommended selection strategy

**Key insight:**
- Low-heritability traits (like NLW at 0.10) improve slowly
- High-heritability traits (like WWT at 0.20) improve faster
- You may need to prioritize 2-3 traits, not everything at once

### Step 4: Generate Mating Recommendations

Create optimized ram-ewe pairings.

**Prompt to use:**

```
Create a mating plan for my flock. I have these rams and ewes:

Rams:
- 6402382022RAM001 (high WWT, moderate NLW)
- 6402382021RAM002 (moderate WWT, high NLW)

Ewes (list all 25):
- 6402382020EWE001
- 6402382020EWE002
- 6402382019EWE003
... (continue for all ewes)

My goals are:
1. Improve weaning weight (priority)
2. Maintain or improve lambs weaned
3. Keep inbreeding below 6%

Match each ewe to the best ram and explain why.
```

**What you will see:**
- Recommended ram for each ewe
- Projected offspring EBVs for each pairing
- Inbreeding risk assessment
- Explanation of why each match was made

**Key decision points:**
- Should you use both rams or focus on one?
- Which ewes should go to which ram?
- Any ewes that should skip breeding this year?

### Step 5: Check Inbreeding Risk

Before finalizing, verify no matings are too closely related.

**Prompt to use for each concerning pairing:**

```
Calculate the inbreeding coefficient if I breed ram 6402382022RAM001 to
ewe 6402382020EWE005. Check for common ancestors in the last 4 generations.
```

**For the whole plan at once:**

```
Check all my proposed matings for inbreeding risk:
- Ram 6402382022RAM001 x Ewes: EWE001, EWE003, EWE007, EWE012...
- Ram 6402382021RAM002 x Ewes: EWE002, EWE004, EWE005, EWE006...

Flag any pairings with inbreeding coefficient above 3%.
```

**What you will see:**
- Inbreeding coefficient for each mating (as percentage)
- Risk level classification (Low/Moderate/High)
- Common ancestors identified
- Recommendation to proceed or avoid

**Inbreeding risk guide:**

| Coefficient | Risk Level | Action |
|-------------|------------|--------|
| < 3% | Low | Safe to proceed |
| 3-6% | Moderate | Proceed with caution, consider alternatives |
| > 6% | High | Avoid this mating |

### Final Mating Plan

After completing all steps, ask for a summary:

```
Summarize my final mating plan in a table format with columns for:
Ewe LPN, Assigned Ram, Projected WWT, Projected NLW, Inbreeding Risk
```

---

## Workflow: Flock Health Planning

**Goal**: Create a comprehensive health management plan tailored to your region and operation.

**Scenario**: You are running 50 ewes in Georgia (Southeast region) and want to stay ahead of health issues.

### Step 1: Get Regional Health Context

Understand the specific challenges for your area.

**Prompt to use:**

```
I'm raising sheep in Georgia (Southeast region). What are the main health
challenges I should be aware of? Include information about parasites,
diseases, and climate-related issues.
```

**What you will see:**
- Primary diseases affecting sheep in the Southeast
- Parasite pressure and peak seasons
- Climate considerations (heat stress, humidity)
- Regional vaccination recommendations

**Key Southeast challenges:**
- High parasite loads (especially Haemonchus/barber pole worm)
- Extended grazing season but also extended parasite season
- Heat stress during summer months
- Foot rot in humid conditions

### Step 2: Create a Seasonal Calendar

Build a month-by-month management schedule.

**Prompt to use:**

```
Create a seasonal management calendar for my sheep operation in Georgia.
I want to lamb in March. Include:
- When to put rams in
- Vaccination schedule
- Deworming strategy
- Shearing timing
- Key management tasks each month
```

**What you will see:**
- Month-by-month task list
- Breeding dates (work backward from lambing goal)
- Vaccination timing (pre-breeding, pre-lambing)
- Seasonal parasite management approach

**Sample calendar excerpt:**

| Month | Key Tasks |
|-------|-----------|
| September | Put rams in (for March lambing), flushing ewes |
| October | Remove rams, pregnancy check, vaccinate for abortion |
| November | Body condition scoring, adjust nutrition |
| December | Move to winter feeding program |
| January | Pre-lambing vaccinations, prepare lambing supplies |
| February | Final pre-lambing prep, move ewes to lambing area |
| March | Lambing, navel dipping, colostrum management |

### Step 3: Understand Disease Risks

Get specific prevention guidance for major threats.

**Prompt to use:**

```
What vaccinations should I give my sheep flock in the Southeast? Include:
- Core vaccines everyone needs
- Risk-based vaccines for our region
- Timing recommendations
- Any vaccines I should definitely NOT skip
```

**For specific disease questions:**

```
How do I prevent and manage barber pole worm (Haemonchus contortus) in
my Georgia flock? I have 50 ewes on 30 acres of pasture.
```

**What you will see:**
- Recommended vaccination protocol
- Disease-specific prevention strategies
- FAMACHA scoring guidance for parasite management
- When to call a veterinarian

### Step 4: Plan Your Nutrition Program

Match feeding to production stages and regional forage availability.

**Prompt to use:**

```
Help me plan nutrition for my 50-ewe flock through the production year.
We're in Georgia with mixed pasture (fescue/bermuda). I need guidance for:
- Flushing (pre-breeding)
- Early/mid/late gestation
- Lactation (twins vs singles)
- Growing lambs

What supplements do I need beyond pasture?
```

**What you will see:**
- Nutrient requirements by production stage
- Recommended supplementation
- Mineral requirements (especially selenium in the Southeast)
- Feeding rates and timing

**Key nutrition considerations:**

| Stage | Energy Need | Protein Need | Key Supplements |
|-------|-------------|--------------|-----------------|
| Maintenance | Low | Low | Mineral, salt |
| Flushing | Increasing | Moderate | Energy supplement |
| Late Gestation | High | High | Grain, protein supplement |
| Lactation (twins) | Very High | Very High | Grain, hay, minerals |

### Putting It Together

Ask for a consolidated plan:

```
Create a one-page health management summary for my Georgia flock with:
1. Annual vaccination schedule
2. Monthly parasite monitoring protocol
3. Nutrition calendar by production stage
4. Emergency contacts and when to call the vet
```

---

## Workflow: Evaluating Your Ram's Performance

**Goal**: Assess whether your current ram is delivering genetic improvement and decide on his continued use.

**Scenario**: You have been using ram `6402382020SIRE01` for two years. Is he doing a good job?

### Step 1: Pull Progeny Data

Get comprehensive offspring information.

**Prompt to use:**

```
Generate a detailed progeny report for my ram 6402382020SIRE01. I want to
see all his offspring, their EBVs, and how they compare to each other.
```

**What you will see:**
- Total number of offspring by sex
- EBV statistics across all progeny (mean, min, max, std dev)
- List of individual offspring with their values
- Identification of top and bottom performers

### Step 2: Compare Offspring to Breed Averages

Understand if his lambs are above or below breed standards.

**Prompt to use:**

```
Compare my ram's progeny averages to the Katahdin breed average. For each
trait, show whether his offspring are above or below breed average and by
how much.
```

**What you will see:**
- Progeny average vs. breed average for each trait
- Percentage above/below breed average
- Traits where offspring excel
- Traits where offspring underperform

**Key question to answer:**
Are his offspring, on average, better than the breed average? If not, genetic progress is stalled.

### Step 3: Identify His Strengths and Weaknesses

Get a clear picture of what genetics he is passing on.

**Prompt to use:**

```
Analyze my ram 6402382020SIRE01 as a sire. Based on his progeny performance:
1. What are his genetic strengths (traits where progeny excel)?
2. What are his weaknesses (traits where progeny lag)?
3. Is he improving my flock's genetics overall?
4. How consistent are his lambs (high or low variation)?
```

**What to look for:**
- **Strength**: Progeny consistently above breed average for specific traits
- **Weakness**: Progeny below breed average or high variation
- **Consistency**: Low standard deviation means predictable offspring

### Step 4: Decide on Continued Use

Make an evidence-based decision about keeping or replacing him.

**Prompt to use:**

```
I've been using ram 6402382020SIRE01 for 2 years. Based on his progeny
data, should I:
1. Continue using him for all ewes?
2. Use him only for certain ewes?
3. Replace him?

My breeding goals are improving weaning weight and maintaining good
maternal traits. What does the data suggest?
```

**Decision framework:**

| Situation | Recommendation |
|-----------|----------------|
| Progeny averaging above breed average for priority traits | Keep using him |
| Progeny average for most traits, excellent for one key trait | Use selectively for that trait |
| Progeny below breed average for priority traits | Consider replacement |
| High variation in offspring | May need more ewes to evaluate OR inconsistent genetics |
| Inbreeding concerns with your current ewes | Bring in outside genetics |

### Additional Evaluation Questions

**Compare to another ram you are considering:**

```
Compare my current ram 6402382020SIRE01 to the ram I'm considering buying
(6402382023NEW01). Based on their EBVs and progeny records, which one would
produce better offspring for terminal production?
```

**Economic impact analysis:**

```
If I replace my current ram with one that has 10% higher WWT EBV, what
is the expected impact on my lamb crop value? I sell lambs at
weaning (60-80 lbs) for $2.50/lb.
```

---

## Workflow: Starting a New Breeding Program

**Goal**: Build a sheep breeding program from the ground up using NSIP data for selection decisions.

**Scenario**: You are starting a new Katahdin flock focused on producing quality market lambs.

### Phase 1: Define Your Breeding Objectives

Before buying any animals, clarify your goals.

**Prompt to use:**

```
I'm starting a Katahdin sheep operation in Texas (Southwest region) focused
on producing market lambs. Help me define my breeding objectives:
1. What traits should I prioritize?
2. What are realistic improvement targets?
3. How should I weight different traits in selection?
```

**What you will see:**
- Recommended trait priorities for terminal production
- Realistic genetic gain expectations per generation
- Suggested selection index weights
- Regional considerations for Texas

**Key traits for terminal production:**
- **WWT (Weaning Weight)**: Primary economic trait for market lamb production
- **PWWT (Post-Weaning Weight)**: Important if feeding lambs longer
- **BWT (Birth Weight)**: Keep moderate to avoid lambing problems
- **NLW (Number Lambs Weaned)**: More lambs = more income

### Phase 2: Select Foundation Ewes

Build a quality genetic base.

**Prompt to use:**

```
I want to buy 20 foundation ewes for my new Katahdin flock. What EBV
criteria should I use to select high-quality ewes? Give me minimum and
target values for each important trait.
```

**Ewe selection criteria:**

| Trait | Minimum | Target (Top 25%) |
|-------|---------|------------------|
| WWT | Breed average | +3.0 or higher |
| NLW | Breed average | +0.10 or higher |
| MWWT | Breed average | +2.0 or higher |
| Accuracy | 40%+ | 60%+ |

**When shopping, evaluate candidates:**

```
Compare these 5 ewes I'm considering for my foundation flock:
6400123, 6400124, 6400125, 6400126, 6400127

Rank them by overall genetic merit for terminal lamb production
and maternal ability.
```

### Phase 3: Select Your First Ram

The ram contributes half the genetics to every lamb.

**Prompt to use:**

```
I'm selecting my first ram for a new 20-ewe Katahdin flock focused on
market lamb production. What EBV levels should I look for? What questions
should I ask the breeder?
```

**Ram selection criteria:**

| Trait | Minimum | Ideal |
|-------|---------|-------|
| WWT | Top 25% of breed | Top 10% of breed |
| PWWT | Top 25% of breed | Top 10% of breed |
| Accuracy | 50%+ | 70%+ (proven sire) |
| Progeny count | - | 10+ for proven sire |

**Evaluating a specific ram:**

```
I found a ram for sale: LPN 6402382022RAM999. The seller is asking $1,500.
Evaluate this ram for my new terminal Katahdin program. Is the price justified
by his genetics?
```

### Phase 4: Check Pedigree Compatibility

Make sure your rams and ewes are not related.

**Prompt to use:**

```
I'm building a new flock with these animals:
Ram: 6402382022RAM999
Ewes: 6400123, 6400124, 6400125, 6400126, 6400127...

Check for any pedigree conflicts. Are any of these animals related?
What inbreeding levels would result from these matings?
```

### Phase 5: Set Up Record Keeping and NSIP Enrollment

Track genetics properly from day one.

**Prompt to use:**

```
I'm starting a new NSIP-enrolled Katahdin flock. What records do I need
to keep for each animal? What data does NSIP need for genetic evaluation?
```

**Essential records for NSIP:**
- Birth date and type (single, twin, triplet)
- Birth weight
- Weaning weight (60-90 days)
- Dam ID for each lamb
- Sire ID (if using multiple rams, DNA testing may be needed)
- Disposal date and reason

### Phase 6: Create a Multi-Year Improvement Plan

Plan for long-term genetic progress.

**Prompt to use:**

```
Create a 5-year genetic improvement plan for my new Katahdin flock.
I'm starting with 20 ewes and 1 ram focused on terminal production.
Include:
- Annual genetic progress targets
- When to introduce new genetics
- Selection decisions at each stage
- Expected outcomes by year 5
```

**Sample 5-year timeline:**

| Year | Actions | Expected Progress |
|------|---------|-------------------|
| 1 | Establish flock, first lamb crop | Baseline established |
| 2 | Cull bottom ewes, keep best ewe lambs | WWT +0.5 lbs |
| 3 | Consider second ram for genetic diversity | WWT +1.0 lbs cumulative |
| 4 | First daughters of original ram breeding | Evaluate ram's true impact |
| 5 | Replace original ram if needed | WWT +1.5-2.0 lbs cumulative |

### Ongoing Management

**Annual review prompt:**

```
It's the end of year 1 for my breeding program. Review the EBVs of my
first lamb crop and tell me:
1. How did they compare to my foundation flock?
2. Did my ram deliver the expected improvement?
3. Which ewe lambs should I keep as replacements?
4. Which ewes should I cull?
```

---

## Quick Reference

### Common Prompts by Task

**Looking up animals:**
```
Look up LPN ID [your LPN here]
```

**Comparing animals:**
```
Compare these animals: [LPN1, LPN2, LPN3]
Rank them by [trait or overall merit]
```

**Checking inbreeding:**
```
What's the inbreeding if I breed [ram LPN] to [ewe LPN]?
```

**Getting regional advice:**
```
What sheep health challenges should I know about in [your state/region]?
```

**Understanding a trait:**
```
What does [trait abbreviation] mean and what's a good value?
```

**Planning breeding:**
```
I want lambs in [month]. When should breeding start?
```

### Tool Reference

| Tool | What It Does | Example Use |
|------|--------------|-------------|
| `nsip_get_animal` | Fetch single animal details | Looking up a ram for purchase |
| `nsip_get_lineage` | Fetch pedigree tree | Checking ancestry before mating |
| `nsip_get_progeny` | Fetch offspring list | Evaluating a sire's production |
| `nsip_search_by_lpn` | Complete profile (details+lineage+progeny) | Full animal evaluation |
| `nsip_search_animals` | Search by criteria | Finding animals in a breed |
| `nsip_list_breeds` | Get breed groups and IDs | Finding your breed's ID number |
| `nsip_get_trait_ranges` | Breed trait min/max | Understanding breed averages |

### Prompt Reference

| Prompt | Type | Best For |
|--------|------|----------|
| `ebv_analyzer` | Single-shot | Quick EBV comparison of 2-5 animals |
| `inbreeding` | Single-shot | Checking a specific mating pair |
| `ancestry` | Single-shot | Viewing pedigree tree |
| `progeny_report` | Single-shot | Sire evaluation |
| `selection_index` | Single-shot | Ranking animals by custom index |
| `flock_dashboard` | Single-shot | Flock overview |
| `guided_mating_plan` | Interview | Comprehensive mating optimization |
| `guided_trait_improvement` | Interview | Multi-generation planning |
| `guided_breeding_recommendations` | Interview | AI-powered recommendations |

### Shepherd Consultation Topics

| Domain | Example Questions |
|--------|-------------------|
| **Breeding** | "What does a WWT of +4.5 mean for market lambs?" |
| **Health** | "How do I manage barber pole worm in the Southeast?" |
| **Calendar** | "When should I vaccinate for enterotoxemia?" |
| **Economics** | "Is a $2,000 ram worth the investment for my 30-ewe flock?" |

---

*This guide provides real-world workflows for common sheep breeding tasks using NSIP tools. Replace example LPN IDs with your own animals' identifiers.*

*Last Updated: December 2025*
