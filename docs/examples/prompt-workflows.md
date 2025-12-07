# NSIP MCP Prompts: Example Workflows for Sheep Farmers

A practical guide showing how to use the NSIP prompt workflows to make better breeding decisions. This guide is written for sheep farmers and breeders who want to get the most out of AI-assisted breeding analysis.

---

## Table of Contents

1. [Introduction: What Are MCP Prompts?](#introduction-what-are-mcp-prompts)
2. [Single-Shot Analysis Prompts](#single-shot-analysis-prompts)
   - [EBV Analyzer](#ebv-analyzer)
   - [Flock Dashboard](#flock-dashboard)
   - [Progeny Report](#progeny-report)
   - [Selection Index](#selection-index)
   - [Ancestry Report](#ancestry-report)
   - [Inbreeding Calculator](#inbreeding-calculator)
3. [Guided Interview Prompts](#guided-interview-prompts)
   - [Mating Plan Interview](#mating-plan-interview)
   - [Trait Improvement Planning](#trait-improvement-planning)
   - [Breeding Recommendations Interview](#breeding-recommendations-interview)
   - [Flock Import Interview](#flock-import-interview)
4. [Shepherd Consultation Prompts](#shepherd-consultation-prompts)
   - [General Shepherd Consultation](#general-shepherd-consultation)
   - [Breeding and Genetics Focus](#breeding-and-genetics-focus)
   - [Health and Nutrition Focus](#health-and-nutrition-focus)
   - [Seasonal Calendar Planning](#seasonal-calendar-planning)
   - [Economics and Profitability](#economics-and-profitability)
5. [Real-World Scenarios](#real-world-scenarios)
   - [Improving My Flock's Growth Rate](#scenario-1-improving-my-flocks-growth-rate)
   - [Planning Matings for Next Season](#scenario-2-planning-matings-for-next-season)
   - [Analyzing My Ram's Offspring Performance](#scenario-3-analyzing-my-rams-offspring-performance)
   - [Regional Health Concerns](#scenario-4-regional-health-concerns)
   - [Should I Buy This Ram?](#scenario-5-should-i-buy-this-ram)
   - [Understanding My Flock Report](#scenario-6-understanding-my-flock-report)
6. [Quick Reference](#quick-reference)

---

## Introduction: What Are MCP Prompts?

### The Difference Between Tools and Prompts

When you work with NSIP through an AI assistant like Claude, there are two ways to access information:

**Tools** are like simple lookups. You ask for specific data and get it back:
- "Look up animal 6332-12345" returns that animal's breeding values
- "Show me the progeny for this sire" returns a list of offspring

**Prompts** are like expert consultations. They combine data retrieval with analysis and recommendations:
- The EBV Analyzer does not just show you numbers; it creates a comparison table and helps you understand what the values mean
- The Shepherd prompts provide expert advice that considers your region, production goals, and specific situation

Think of tools as asking a librarian to find a book, while prompts are like asking an expert to read the book and explain what it means for your situation.

### Types of Prompts Available

1. **Single-Shot Prompts**: You provide all the information upfront, and you get a complete analysis back immediately. Best when you know exactly what you want.

2. **Guided Interview Prompts**: The AI walks you through a series of questions to gather what it needs. Best for complex decisions where you might not know all the right inputs.

3. **Shepherd Consultation Prompts**: Expert advice on breeding, health, seasonal management, and economics. Best for open-ended questions where you want professional guidance.

---

## Single-Shot Analysis Prompts

These prompts give you immediate analysis when you provide the required information upfront.

### EBV Analyzer

**What it does:** Compares Estimated Breeding Values across multiple animals so you can see side-by-side how they rank for different traits.

**When to use it:**
- Comparing rams before a breeding decision
- Evaluating potential purchases at a sale
- Ranking your ewes for replacement selection

**How to ask:**

> "Compare the EBVs for these three rams I'm considering: 6332-001, 6332-002, and 6332-003. Focus on growth and carcass traits."

Or more specifically:

> "Analyze the breeding values for animals 6332-001, 6332-002 comparing WWT, PWWT, YEMD, and NLW."

**What you get back:**

The AI will create a comparison table showing each animal's values for the traits you specified, along with explanations of what each trait measures and which animal ranks highest for each characteristic.

**Example output:**

```
## EBV Comparison Analysis

### Comparison Table

| Animal | WWT | PWWT | YEMD | NLW |
| --- | --- | --- | --- | --- |
| Big Sky 2024 (6332-001) | 4.5 | 6.8 | 1.2 | 0.08 |
| Mountain Thunder (6332-002) | 5.2 | 7.5 | 0.9 | 0.12 |
| Valley Pride (6332-003) | 3.8 | 5.9 | 1.5 | 0.15 |

### Trait Interpretations

- **WWT**: Weaning Weight - Higher values mean lambs gain weight faster to weaning
- **PWWT**: Post-Weaning Weight - Growth rate after weaning
- **YEMD**: Yearling Eye Muscle Depth - More muscle = more meat
- **NLW**: Number of Lambs Weaned - Maternal ability measure

### Summary

Compared 3 animals across 4 traits.
- Best for growth (WWT/PWWT): Mountain Thunder
- Best for carcass (YEMD): Valley Pride
- Best for maternal (NLW): Valley Pride
```

**Pro tip:** If you do not specify traits, the analyzer uses a default set of common traits: BWT, WWT, PWWT, YFAT, YEMD, and NLW.

---

### Flock Dashboard

**What it does:** Generates an overview of your flock's genetic performance, showing averages, ranges, and identifying top performers.

**When to use it:**
- Getting a snapshot of your flock's current genetic status
- Identifying which animals stand out from the group
- Finding areas where your flock could improve

**How to ask:**

> "Generate a flock dashboard for flock prefix 6332. Show me how my animals are performing overall."

Or:

> "I want to see my flock statistics. My flock ID prefix is 6332."

**What you get back:**

A summary showing:
- Total animals in your flock by sex
- Average EBVs across your flock for key traits
- Min and max values showing the range in your flock
- Your top performers ranked by important traits
- Recommendations based on the data

**Example output:**

```
## Flock Dashboard: 6332

### Overview

- **Total Animals**: 75
- **Males**: 12
- **Females**: 63

### Flock EBV Averages

| Trait | Average | Min | Max | Count |
| --- | --- | --- | --- | --- |
| BWT | 0.3 | -0.5 | 1.2 | 75 |
| WWT | 3.2 | 0.5 | 6.8 | 75 |
| PWWT | 4.5 | 1.2 | 9.1 | 75 |
| NLW | 0.08 | -0.05 | 0.22 | 63 |

### Top Performers by PWWT

1. **Big Sky 2023**: PWWT = 9.1
2. **Valley Thunder**: PWWT = 8.5
3. **Mountain Belle**: PWWT = 8.2

### Recommendations

Based on the flock averages, consider:
- Focus selection on traits with the most variation
- Identify animals in the top 20% for replacement stock
- Cull animals consistently below flock average across multiple traits
```

---

### Progeny Report

**What it does:** Evaluates a sire by analyzing how his offspring are performing. This is one of the best ways to judge a ram's true genetic merit.

**When to use it:**
- Deciding whether to keep using a ram
- Evaluating a ram before purchasing his offspring
- Understanding whether a sire is producing consistent results

**How to ask:**

> "Give me a progeny report for my herd sire 6332-001. I want to know how his lambs are performing."

Or:

> "Evaluate the offspring of sire 6332-001. Show me if he's producing quality lambs."

**What you get back:**

A detailed analysis of the sire's offspring including:
- Total number of progeny and sex breakdown
- The sire's own EBVs for reference
- Average EBVs of his offspring
- How consistent his offspring are
- Evaluation of whether he is improving the traits you care about

**Example output:**

```
## Progeny Report: 6332-001

**Sire LPN**: 6332-001
**Breed**: Katahdin
**Total Progeny**: 45
**Ram Lambs**: 22 | **Ewe Lambs**: 23

### Sire's Own EBVs

- **BWT**: 0.25
- **WWT**: 5.2
- **PWWT**: 7.8
- **NLW**: 0.12

### Progeny EBV Averages (based on 45 sampled)

| Trait | Average | Min | Max | Count |
| --- | --- | --- | --- | --- |
| BWT | 0.20 | -0.3 | 0.8 | 45 |
| WWT | 4.8 | 2.1 | 6.5 | 45 |
| PWWT | 7.2 | 4.5 | 9.1 | 42 |
| NLW | 0.10 | -0.02 | 0.18 | 23 |

### Evaluation

- PWWT: Progeny averaging 7.2 (sire: 7.8)
- NLW: Progeny averaging 0.10 (sire: 0.12)

This sire is producing offspring that closely match his own EBVs,
indicating he breeds true to his genetic predictions.
```

---

### Selection Index

**What it does:** Calculates a single score that combines multiple EBVs based on their economic importance. This makes it easier to rank animals when you care about several traits at once.

**When to use it:**
- Ranking animals for overall breeding merit (not just one trait)
- Comparing animals for your specific production focus
- Deciding which animals to keep or cull

**How to ask:**

> "Calculate terminal index scores for rams 6332-001, 6332-002, and 6332-003. I'm producing market lambs."

Or:

> "Score these ewes using the maternal index: 6332-101, 6332-102, 6332-103"

Or for a balanced approach:

> "Rank these animals by balanced index: 6332-001, 6332-002, 6332-003"

**Available indexes:**

| Index | Best For |
|-------|----------|
| **Terminal** | Producing market lambs for meat - emphasizes growth and carcass |
| **Maternal** | Producing replacement ewes - emphasizes reproduction and mothering |
| **Hair** | Hair sheep breeds like Katahdin - balanced for low-input systems |
| **Balanced** | Dual-purpose flocks - weights both growth and maternal traits |

**Example output:**

```
## Selection Index Rankings: Terminal

**Index Description**: Emphasizes growth rate and carcass quality for
market lamb production. Higher weaning and post-weaning weights are
heavily weighted.

### Rankings

| Rank | Animal | Score |
| --- | --- | --- |
| 1 | Mountain Thunder (6332-002) | 45.80 |
| 2 | Big Sky 2024 (6332-001) | 42.35 |
| 3 | Valley Pride (6332-003) | 38.90 |

### Index Weights

- **WWT**: +1.50 (higher better)
- **PWWT**: +2.00 (higher better)
- **YEMD**: +3.00 (higher better)
- **YFAT**: -1.00 (lower better)
- **BWT**: -0.50 (lower better)

### Use Case

Select rams that rank highly on this index when your primary goal
is producing fast-growing, well-muscled market lambs.
```

---

### Ancestry Report

**What it does:** Generates a pedigree tree showing an animal's parents, grandparents, and key breeding values inherited from each line.

**When to use it:**
- Understanding an animal's genetic background
- Identifying potential inbreeding connections
- Tracing which side of the family contributed specific traits

**How to ask:**

> "Show me the pedigree for animal 6332-001. I want to see where his genetics come from."

Or:

> "Generate an ancestry report for 6332-101"

**Example output:**

```
## Pedigree Report: 6332-001

**LPN ID**: 6332-001
**Breed**: Katahdin
**Birth Date**: 2022-03-15
**Sex**: Male

### Pedigree Tree

                    +-- Sire's Sire: Highland Pride (6332-SS1)
         +-- SIRE: Mountain King (6332-S1)
         |          +-- Sire's Dam: Valley Queen (6332-SD1)
6332-001
         |          +-- Dam's Sire: Thunder Ridge (6332-DS1)
         +-- DAM:  Spring Belle (6332-D1)
                   +-- Dam's Dam: Prairie Rose (6332-DD1)

### Key EBVs

- **BWT**: 0.25
- **WWT**: 5.2
- **PWWT**: 7.8
- **NLW**: 0.12
- **MWWT**: 2.4
```

---

### Inbreeding Calculator

**What it does:** Calculates the inbreeding coefficient for a potential mating, helping you avoid breeding animals that are too closely related.

**When to use it:**
- Before breeding a ram to a specific ewe
- When evaluating whether to keep a ram for use with your flock
- Checking if a purchased animal shares ancestors with your flock

**How to ask:**

> "Check the inbreeding if I breed ram 6332-001 to ewe 6332-101"

Or:

> "What would be the inbreeding coefficient for offspring from ram 6332-001 and ewe 6332-102?"

**Understanding the results:**

| F Coefficient | Risk Level | What It Means |
|---------------|------------|---------------|
| Below 3% | Low | Safe for most breeding programs |
| 3% to 6% | Moderate | Some caution needed, may see minor effects |
| Above 6% | High | Avoid this mating - significant inbreeding depression likely |

**Example output:**

```
## Inbreeding Analysis

**Potential Mating**: Ram 6332-001 x Ewe 6332-101

### Results

- **Inbreeding Coefficient (F)**: 0.0312 (3.12%)
- **Risk Level**: MODERATE
- **Common Ancestors Found**: 1

### Common Ancestors

- 6332-GS001 (appears as grandsire on both sides)

### Recommendation

Consider alternatives. Monitor offspring for reduced vigor.

### Inbreeding Risk Guide

| F Coefficient | Risk Level | Impact |
| --- | --- | --- |
| < 3% | Low | Acceptable for most programs |
| 3-6% | Moderate | Some reduction in fitness possible |
| > 6% | High | Significant inbreeding depression likely |
```

---

## Guided Interview Prompts

These prompts walk you through a conversation, gathering information step by step. They are ideal when you are not sure exactly what inputs are needed or when the analysis requires multiple pieces of information.

### Mating Plan Interview

**What it does:** Guides you through creating an optimized mating plan by asking about your available rams, ewes, and breeding goals.

**When to use it:**
- Planning your breeding season
- When you have multiple rams and need to decide which ewes each should cover
- When you want to avoid inbreeding while optimizing for specific traits

**How to start:**

> "Help me create a mating plan for next breeding season."

Or if you have some information ready:

> "I need a mating plan. I have rams 6332-001 and 6332-002, and I want to focus on terminal production."

**The conversation flow:**

The AI will ask you for:
1. Your available ram LPN IDs
2. Your ewe LPN IDs (or a file containing them)
3. Your breeding goal (terminal, maternal, balanced, or hair)
4. Your maximum acceptable inbreeding level (optional)

**Example conversation:**

```
You: Help me create a mating plan

AI: Let's create a mating plan for your flock. I need to gather
    some information.

    Current Inputs:
    - Rams: Not yet provided
    - Ewes: Not yet provided
    - Breeding goal: Not yet specified

    Available Breeding Goals:
    - Terminal: Emphasizes growth rate and carcass quality
    - Maternal: Emphasizes reproduction and mothering ability
    - Hair: Balanced for hair sheep breeds
    - Balanced: Weighs both growth and maternal traits

    Please provide the ram LPN IDs (comma-separated), ewe LPN IDs,
    and your breeding goal.

You: My rams are 6332-001 and 6332-002. I have 25 ewes in my flock
     with prefix 6332. Goal is terminal production.

AI: I have all the information needed. Shall I proceed with the
    mating optimization?

    Summary:
    - Analyzing 2 rams x 25 ewes
    - Goal: terminal index optimization
    - Will consider inbreeding avoidance and EBV complementarity

    Reply "proceed" to run the analysis or provide corrections.

You: proceed

AI: [Generates detailed mating recommendations with projected outcomes]
```

---

### Trait Improvement Planning

**What it does:** Helps you create a multi-generation plan to improve a specific trait in your flock.

**When to use it:**
- Setting long-term breeding goals
- Understanding how quickly you can improve a particular trait
- Planning selection intensity and culling strategies

**How to start:**

> "I want to improve weaning weights in my flock over the next few generations."

Or with more detail:

> "Help me plan trait improvement. I want to increase my flock's WWT from the current average of +2.0 to +4.0."

**The conversation flow:**

The AI will ask about:
1. Which trait you want to improve
2. Your current flock average for that trait
3. Your target value
4. How many generations you want to plan for
5. Your region (optional, for context)

**Example conversation:**

```
You: I want to improve post-weaning weight in my flock

AI: I'll help you create a multi-generation selection plan for
    trait improvement.

    Heritability Reference:
    - PWWT: h2 = 0.25 (moderate genetic progress)

    This means about 25% of the variation in post-weaning weight
    is due to genetics, so selection will produce gradual but
    consistent improvement.

    Current Inputs:
    - Target trait: Not yet specified (you mentioned PWWT)
    - Current flock average: Not yet provided
    - Target value: Not yet specified
    - Planning horizon: Default is 3 generations

    What is your current flock average for PWWT, and what value
    are you trying to reach?

You: Current average is +3.5, I want to get to +6.0 over 4 generations

AI: Analysis Preview:
    - Gap to close: +2.5 units
    - Heritability: 0.25
    - Expected progress per generation: ~0.35 units
    - Estimated generations to goal: 7.1 generations

    Note: With moderate heritability, reaching +6.0 from +3.5 will
    take longer than 4 generations at typical selection intensity.

    Options:
    1. Accept slower progress (4 generations gets you to ~4.9)
    2. Increase selection pressure (keep only top rams)
    3. Adjust target to realistic 4-generation goal

    Shall I proceed with detailed recommendations?
```

---

### Breeding Recommendations Interview

**What it does:** Gathers comprehensive information about your operation to provide AI-powered breeding recommendations tailored to your specific situation.

**When to use it:**
- Getting personalized guidance for your breeding program
- When you are not sure what direction to take your flock
- When you want recommendations that consider your constraints

**How to start:**

> "I want breeding recommendations for my flock"

Or with context:

> "Help me develop a breeding strategy. I'm raising Katahdins in Georgia for market lambs, but I want to improve maternal traits too."

**The conversation flow:**

The AI will ask about:
1. Your flock data (flock prefix or file with animal IDs)
2. Your breeding priorities (what you want to improve)
3. Any constraints (budget, facilities, timing)
4. Your region (for regional adaptation)

**Example conversation:**

```
You: I need help with breeding recommendations

AI: I'll help you develop a breeding strategy tailored to your
    operation. I need to gather some information.

    NSIP Regions:
    - northeast, southeast, midwest, southwest, mountain, pacific

    Current Information:
    - Flock data: Not yet provided
    - Breeding priorities: Not yet specified
    - Constraints: Not yet specified

    To provide personalized recommendations, please tell me:
    1. Your flock identifier (LPN prefix) or file path to flock data
    2. Your breeding priorities (e.g., growth, maternal, parasite resistance)

    Priority Examples:
    - "Focus on growth and carcass quality" (terminal emphasis)
    - "Improve lambing ease and milk production" (maternal emphasis)
    - "Maximize parasite resistance" (hair sheep / sustainable)
    - "Balance growth with maternal traits" (dual-purpose)

You: My flock prefix is 6332. I'm in the midwest raising Katahdins.
     I want to balance growth with maternal ability, but lambing ease
     is also important because I lamb during cold weather.

AI: I have enough information to generate recommendations.

    I will analyze:
    1. Current flock genetic profile
    2. Alignment with your priorities (balanced growth/maternal, lambing ease)
    3. Regional considerations (midwest, cold-weather lambing)
    4. Practical implementation steps

    Reply "proceed" to generate recommendations or add more details.
```

---

### Flock Import Interview

**What it does:** Helps you import your flock data from a spreadsheet and enrich it with current NSIP breeding values.

**When to use it:**
- When you have a spreadsheet of your animals and want to add NSIP data
- Setting up a new flock database
- Updating your records with the latest EBVs

**How to start:**

> "I have a spreadsheet of my flock and want to import it with NSIP data"

Or:

> "Help me import my flock from a CSV file at /path/to/my_flock.csv"

**Supported file formats:**
- CSV files (.csv) - Comma or tab separated
- Excel files (.xlsx, .xls)

**Expected column headers:**
For best results, your file should include:
- Animal ID (LPN ID, tag number, or name)
- Birth date
- Sex (M/F)
- Sire ID (optional)
- Dam ID (optional)

The AI can work with various column names and will help map them to NSIP fields.

---

## Shepherd Consultation Prompts

The Shepherd is an AI-powered expert advisor that provides professional guidance across four areas of sheep management. Think of the Shepherd as having the professional demeanor of a veterinarian: evidence-based, acknowledges uncertainty, and gives actionable advice.

### General Shepherd Consultation

**What it does:** Answers any sheep husbandry question by automatically routing to the appropriate specialty area (breeding, health, calendar, or economics).

**When to use it:**
- Any general question about sheep management
- When you are not sure which specialty area applies
- For questions that span multiple topics

**How to ask:**

> "Ask the Shepherd: How do I select replacements to improve my flock?"

Or simply:

> "I'm having trouble with lambs not gaining weight. What should I look for?"

**Available knowledge domains:**
- **Breeding**: Genetic selection, EBV interpretation, mating plans, inbreeding
- **Health and Nutrition**: Disease prevention, parasites, feeding programs
- **Calendar**: Seasonal management, lambing preparation, shearing
- **Economics**: Costs, profitability, marketing, ROI analysis

**Example:**

```
You: I have a ram with really good growth EBVs but his NLW is
     negative. Should I use him on my ewes?

AI: ## Shepherd Consultation

    This is a common breeding decision that involves balancing
    competing traits. Let me break this down.

    ### Understanding the Trade-off

    - **Growth EBVs** (WWT, PWWT) determine how fast lambs gain weight
    - **NLW (Number of Lambs Weaned)** indicates maternal ability

    A negative NLW means this ram's daughters may have lower
    reproductive performance than breed average.

    ### My Recommendation

    **It depends on your production system:**

    1. **If you sell all lambs as market animals**: Use him freely.
       His growth genetics will benefit your lamb crop without
       affecting your breeding program.

    2. **If you keep replacement ewe lambs from him**: Use
       cautiously. His daughters may have lower lambing rates or
       poorer mothering ability.

    3. **Compromise approach**: Use him on older ewes you do not
       plan to keep replacements from, while using a more balanced
       ram on younger ewes producing future breeding stock.

    ### Key Principle

    Heritability of NLW is relatively low (~0.10), so environmental
    factors (nutrition, health, management) have a bigger impact
    on actual lamb survival than genetics.

    Would you like me to look up this ram's specific values to
    give more detailed advice?
```

---

### Breeding and Genetics Focus

**What it does:** Provides expert advice specifically on genetic selection, EBV interpretation, and mating decisions.

**When to use it:**
- Questions about what EBV values mean
- Help understanding heritability and genetic progress
- Mating strategy decisions
- Selection pressure and culling decisions

**How to ask:**

> "Ask the Shepherd about breeding: What does a WWT EBV of 5.0 mean for my flock?"

Or:

> "I need genetics advice. How do I select for multiple traits at once without losing progress on any of them?"

**What it considers:**
- Trait heritabilities (how quickly you can change each trait)
- Your production goal (terminal, maternal, balanced)
- Your region and typical breeds
- Selection index weights

**Example:**

```
You: Ask the Shepherd about breeding: I want to improve both growth
     and maternal traits. How do I do this without sacrificing one
     for the other?

AI: ## Context

    **Region**: (provide for regional context)
    **Production Goal**: Balanced

    ## Heritability Reference

    Key trait heritabilities for selection:
    - Birth Weight (BWT): 0.35 - Moderate, responds well
    - Weaning Weight (WWT): 0.20 - Lower, maternal effects important
    - Post-Weaning Weight (PWWT): 0.25 - Moderate
    - Number Lambs Weaned (NLW): 0.10 - Low, slow progress

    ## Balanced Selection Strategy

    **The Challenge**: When you select hard for growth, you may
    inadvertently select against maternal traits (and vice versa).

    **The Solution**: Use a balanced selection index that weights
    both trait groups according to their economic importance to
    your operation.

    ### Recommended Approach

    1. **Use selection indexes instead of single traits**
       The balanced index weights both growth (WWT, PWWT) and
       maternal (NLW, MWWT) traits appropriately.

    2. **Set minimum thresholds**
       Do not select any animal below breed average for maternal
       traits, even if growth is exceptional.

    3. **Consider independent culling levels**
       - Cull bottom 10% for PWWT
       - Cull bottom 20% for NLW
       - Keep animals that pass both thresholds

    4. **Accept slower progress**
       Improving multiple traits simultaneously means slower
       progress on each compared to single-trait selection.

    ### Expected Outcomes

    With balanced selection:
    - Growth traits: +0.3 to +0.5 units per generation
    - Maternal traits: +0.02 to +0.05 units per generation

    Progress on maternal traits is slower due to lower heritability.
```

---

### Health and Nutrition Focus

**What it does:** Provides guidance on disease prevention, parasite management, nutrition programs, and flock health.

**When to use it:**
- Questions about specific diseases or health problems
- Nutrition questions for different life stages
- Parasite control strategies
- Vaccination schedules

**How to ask:**

> "Ask the Shepherd about health: What parasite control strategies work best in the Southeast?"

Or:

> "I need nutrition advice. How should I feed ewes during late gestation?"

**What it considers:**
- Your region and climate
- Life stage (maintenance, flushing, gestation, lactation)
- Common diseases in your area
- Seasonal parasite pressure

**Example:**

```
You: Ask the Shepherd about health: What should I watch for with
     internal parasites in Virginia?

AI: ## Context

    **Region**: Southeast (Virginia)
    **Parasite Season**: Extended - April through October

    ## Regional Health Challenges

    - Barber pole worm (Haemonchus) is primary threat
    - High humidity extends parasite season
    - Warm winters allow overwintering larvae

    ## Common Diseases for Region

    - **Haemonchiosis**: FAMACHA scoring essential
    - **Coccidiosis**: Monitor lambs 3-8 weeks old
    - **Footrot**: Wet conditions increase risk

    ## Internal Parasite Management for Virginia

    ### Primary Threat: Barber Pole Worm

    Haemonchus contortus is your biggest concern. This blood-sucking
    parasite causes:
    - Anemia (pale mucous membranes)
    - Bottle jaw (fluid under chin)
    - Sudden death in heavy infections

    ### Recommended Control Strategy

    1. **FAMACHA scoring every 2-3 weeks**
       - Score 1-2: No treatment needed
       - Score 3: Watch closely
       - Score 4-5: Treat immediately

    2. **Strategic deworming**
       - Treat only animals that need it (selective treatment)
       - Avoid treating the whole flock (preserves refugia)

    3. **Pasture management**
       - Rotate pastures (minimum 60-day rest)
       - Avoid grazing below 4 inches
       - Consider mixed species grazing

    4. **Genetic selection**
       - Select for parasite resistance (FEC trait if available)
       - Cull animals requiring frequent treatment

    ### When to Consult a Veterinarian

    - Animals not responding to treatment
    - Sudden deaths in the flock
    - Before choosing dewormers (resistance testing)
```

---

### Seasonal Calendar Planning

**What it does:** Provides guidance on timing management tasks throughout the year based on your region and production calendar.

**When to use it:**
- Planning breeding dates for desired lambing time
- Creating a seasonal management calendar
- Timing shearing, vaccinations, and other routine tasks

**How to ask:**

> "Ask the Shepherd about calendar: I want March lambs. When should I put rams in?"

Or:

> "Help me plan my breeding and lambing calendar for the midwest."

**What it considers:**
- Your target lambing dates
- Regional climate and typical lambing times
- Task timing and dependencies
- Seasonal feed availability

**Example:**

```
You: Ask the Shepherd about calendar: I want to lamb in early March
     in Ohio. Help me plan backward to know when to do everything.

AI: ## Context

    **Region**: Midwest (Ohio)
    **Target Lambing**: Early March
    **Task Focus**: Breeding calendar

    ## Planning Backward from March Lambing

    Sheep gestation is approximately 147 days (5 months).
    For March 1 lambing, work backward:

    ### Critical Dates

    | Event | Timing | Notes |
    |-------|--------|-------|
    | Lambing begins | March 1 | Have jugs ready, monitor ewes |
    | Rams out | January 15 | End of breeding window |
    | Rams in | October 1 | Start of breeding season |
    | Flush ewes | September 15 | 2 weeks before breeding |
    | Ram fertility check | August 15 | 6 weeks before breeding |

    ### Pre-Breeding Tasks (August - September)

    1. **6 weeks before rams in**
       - Breeding soundness exam for rams
       - Condition score ewes, sort into feeding groups
       - Vaccinate ewes for abortive diseases

    2. **2-3 weeks before rams in**
       - Begin flushing thin ewes (improved nutrition)
       - Trim feet if needed
       - Deworm if FAMACHA indicates need

    3. **1 week before rams in**
       - Mark rams for breeding activity monitoring
       - Final check of fences and facilities

    ### During Breeding (October - January)

    - Check ram marking activity daily first 2 weeks
    - Replace worn marking crayons
    - Consider pregnancy scanning at 45-60 days

    ### Pre-Lambing Tasks (February)

    - Set up lambing jugs
    - Stock lambing supplies
    - Begin increased nutrition (late gestation ration)
    - Vaccinate for clostridial diseases (4 weeks pre-lambing)

    ## Regional Considerations for Ohio

    - Cold-weather lambing: prepare for wind chill, heat lamps
    - Barn lambing preferred over pasture in March
    - Watch for frozen water sources
```

---

### Economics and Profitability

**What it does:** Provides guidance on costs, profitability, marketing, and the economics of sheep production.

**When to use it:**
- Evaluating whether an investment is worthwhile
- Understanding your costs per ewe or per lamb
- Making marketing decisions
- ROI calculations for genetics or equipment

**How to ask:**

> "Ask the Shepherd about economics: Is a $2,500 ram worth it for my 50-ewe flock?"

Or:

> "Help me understand my breakeven price for market lambs."

**What it considers:**
- Flock size economics (small, medium, large)
- Market focus (direct, auction, breeding stock)
- Cost templates for various expenses
- Revenue potential from different markets

**Example:**

```
You: Ask the Shepherd about economics: I'm thinking about buying a
     $3,000 registered ram. Is that worth it for my 40-ewe flock?

AI: ## Context

    **Flock Size**: Medium (40 ewes)
    **Market Focus**: (please specify if known)

    ## Ram Investment Analysis

    ### Cost Breakdown

    **Initial Investment**: $3,000
    **Expected Service Life**: 4-5 breeding seasons
    **Cost per Season**: $600-750
    **Cost per Breeding**: $15-19 per ewe bred

    ### Value Calculation

    The ram adds value through:

    1. **Improved lamb performance**
       - If his lambs average 5 lbs heavier at market
       - At $2.50/lb: 5 lbs x $2.50 = $12.50 extra per lamb
       - With 40 ewes x 1.5 lambs = 60 market lambs
       - Annual extra value: 60 x $12.50 = $750

    2. **Replacement ewe quality**
       - Better genetics in future breeding stock
       - Compounding returns over generations

    ### Break-Even Analysis

    | Scenario | Extra Value Needed per Lamb |
    |----------|----------------------------|
    | 4-year service life | $12.50 per lamb |
    | 3-year service life | $16.67 per lamb |
    | 2-year service life | $25.00 per lamb |

    ### My Assessment

    **For a 40-ewe flock, a $3,000 ram is a significant investment.**

    It makes sense if:
    - The ram has proven progeny data (not just high EBVs)
    - You are keeping replacement ewe lambs
    - The ram is dramatically better than alternatives
    - You can use him for 4+ seasons

    Consider alternatives:
    - Leasing a top ram for breeding season
    - AI to an elite sire
    - A $1,500-2,000 ram with solid (not elite) EBVs

    ### Risk Factors

    - Ram injury or death before payback period
    - EBVs do not guarantee phenotype
    - Market price fluctuations
```

---

## Real-World Scenarios

These examples show complete conversations for common situations sheep farmers face.

### Scenario 1: Improving My Flock's Growth Rate

**The situation:** You want your lambs to grow faster and reach market weight sooner.

**Starting the conversation:**

> "I want to improve my flock's growth rate. My lambs are taking too long to reach market weight. Where do I start?"

**How the conversation unfolds:**

```
You: I want to improve my flock's growth rate. My lambs are taking
     too long to reach market weight. Where do I start?

AI: I can help you create a plan to improve growth rate. Let me
    gather some information and provide specific recommendations.

    First, let me check if you have animals in NSIP so we can
    look at current genetic levels. What is your flock ID prefix?

You: 6332

AI: I found 45 animals in your flock. Let me analyze the current
    growth trait levels.

    ## Current Flock Status

    | Trait | Flock Average | Breed Average | Your Position |
    |-------|---------------|---------------|---------------|
    | WWT | +2.1 | +2.5 | Slightly below |
    | PWWT | +3.5 | +4.2 | Below average |
    | YWT | +5.0 | +5.8 | Below average |

    Your flock is running about 15% below breed average for growth
    traits. This is good news - there is clear room for improvement
    through genetics.

    ## Recommended Strategy

    **Short-term (This Breeding Season)**

    1. Identify your top growth rams already in the flock
       - [Lists top 3 rams by PWWT from your flock]

    2. Consider purchasing or leasing a ram with:
       - PWWT above +7.0
       - Good accuracy (above 60%)
       - Proven progeny if possible

    **Medium-term (1-3 Generations)**

    3. Cull ewes with offspring consistently below average
    4. Keep replacement ewe lambs only from fast-growing dams
    5. Expect improvement of +0.5 to +0.8 units per generation

    Would you like me to:
    - Search for rams with high growth EBVs for sale?
    - Calculate selection index scores for your current rams?
    - Create a trait improvement timeline?
```

---

### Scenario 2: Planning Matings for Next Season

**The situation:** Breeding season is coming up and you need to decide which rams to use on which ewes.

**Starting the conversation:**

> "Help me plan my matings for this fall. I have 2 rams and 30 ewes."

**How the conversation unfolds:**

```
You: Help me plan my matings for this fall. I have 2 rams and
     30 ewes.

AI: I'll help you create an optimized mating plan. I need to
    gather the LPN IDs and understand your goals.

    Let's start with your rams. What are their LPN IDs?

You: Ram 1 is 6332-001, Ram 2 is 6332-002

AI: Found both rams. Let me show you their profiles:

    | Ram | PWWT | NLW | YEMD | Strengths |
    |-----|------|-----|------|-----------|
    | 6332-001 | +7.5 | +0.05 | +1.8 | Growth + carcass |
    | 6332-002 | +4.2 | +0.18 | +0.9 | Maternal traits |

    Now, what are your ewe LPN IDs? You can list them or provide
    your flock prefix if all 30 ewes share it.

You: They all have prefix 6332. I want market lambs but I'm also
     keeping some ewe lambs for replacements.

AI: Since you have mixed goals (market lambs AND replacements),
    I recommend a split strategy:

    ## Mating Plan Recommendation

    ### Ram 6332-001 (Growth Ram)
    **Assign to**: Older ewes (4+ years) not producing replacements
    **Ewe count**: 12-15 ewes
    **Rationale**: Maximize growth for market lambs

    ### Ram 6332-002 (Balanced Ram)
    **Assign to**: Younger ewes (2-3 years) for replacement stock
    **Ewe count**: 15-18 ewes
    **Rationale**: Ewe lambs from these matings will have better
    maternal genetics

    ### Inbreeding Check

    I checked for common ancestors between each ram and your ewes.

    - 6332-001: 2 ewes share a common grandsire (COI would be 3.1%)
    - 6332-002: No common ancestors in 4 generations

    **Recommendation**: Mate the 2 related ewes to 6332-002 instead.

    Would you like me to provide specific ewe assignments for each ram?

You: Yes, please assign the ewes

AI: [Provides detailed table with each ewe, her assigned ram,
    projected offspring EBVs, and inbreeding coefficient]
```

---

### Scenario 3: Analyzing My Ram's Offspring Performance

**The situation:** You have been using a ram for two years and want to know if his lambs are performing as expected.

**Starting the conversation:**

> "Evaluate my herd sire 6332-001. I've used him for two years and want to know if he's doing what his EBVs promised."

**How the conversation unfolds:**

```
You: Evaluate my herd sire 6332-001. I've used him for two years
     and want to know if he's doing what his EBVs promised.

AI: I'll generate a progeny report to see how his offspring are
    performing compared to his predicted EBVs.

    ## Progeny Report: 6332-001

    **Sire**: 6332-001 (Big Sky Katahdin)
    **Breed**: Katahdin
    **Total Progeny in NSIP**: 42
    **Ram Lambs**: 19 | **Ewe Lambs**: 23

    ### Sire's EBVs (His Genetic Predictions)

    | Trait | His EBV | Accuracy |
    |-------|---------|----------|
    | BWT | +0.3 | 85% |
    | WWT | +5.2 | 82% |
    | PWWT | +7.5 | 80% |
    | NLW | +0.05 | 65% |

    ### How His Offspring Are Actually Performing

    | Trait | Sire EBV | Offspring Avg | % of Prediction |
    |-------|----------|---------------|-----------------|
    | BWT | +0.3 | +0.28 | 93% |
    | WWT | +5.2 | +4.8 | 92% |
    | PWWT | +7.5 | +7.1 | 95% |
    | NLW | +0.05 | +0.04 | 80% |

    ### Assessment

    **Good news: This ram is breeding true to his EBVs.**

    - His offspring are averaging 90-95% of his predicted values
    - Consistency is good (small range between best and worst offspring)
    - The slight shortfall is normal (genetics are predictions, not guarantees)

    ### Should You Keep Using Him?

    **Yes, if:**
    - Growth is your priority (his offspring are excellent for PWWT)
    - You are not keeping many replacement ewe lambs from him

    **Consider alternatives if:**
    - You want to improve maternal traits (NLW +0.05 is average)
    - You are seeing more inbreeding as his daughters enter the flock

    Would you like me to check inbreeding with your current ewes?
```

---

### Scenario 4: Regional Health Concerns

**The situation:** You are new to sheep in your area and want to know what health challenges to prepare for.

**Starting the conversation:**

> "What health issues should I watch for with sheep in Alabama? I'm just getting started."

**How the conversation unfolds:**

```
You: What health issues should I watch for with sheep in Alabama?
     I'm just getting started.

AI: Welcome to sheep production! Alabama falls in the Southeast
    region, which has specific health challenges due to the warm,
    humid climate.

    ## Top Health Challenges for Alabama

    ### 1. Internal Parasites (Your Biggest Challenge)

    The Southeast has the most severe parasite pressure in the US
    due to extended warm seasons.

    **Primary threats:**
    - Barber pole worm (Haemonchus contortus) - can kill quickly
    - Brown stomach worm
    - Bankrupt worm

    **What to do:**
    - Learn FAMACHA scoring immediately
    - Rotate pastures with 60+ day rest periods
    - Consider hair sheep breeds (more resistant)
    - Do NOT deworm on a schedule - selective treatment only

    ### 2. Heat Stress

    **Signs to watch:**
    - Rapid breathing, open-mouth panting
    - Reduced feed intake
    - Seeking shade constantly

    **Prevention:**
    - Provide shade and fresh water
    - Shear wool breeds before summer
    - Avoid working sheep in heat of day

    ### 3. Footrot

    High humidity creates ideal conditions for footrot.

    **Prevention:**
    - Keep feet dry when possible
    - Trim hooves regularly
    - Footbath during outbreaks
    - Cull chronic cases

    ### 4. Coccidiosis (Young Lambs)

    **Watch for:**
    - Lambs 3-8 weeks old
    - Bloody or mucus-y diarrhea
    - Poor growth in seemingly healthy lambs

    ## Vaccination Program for Alabama

    | Vaccine | When | Notes |
    |---------|------|-------|
    | CDT | Pre-lambing (4 weeks) | Protects ewes and lambs |
    | CDT | Lambs at 4-6 weeks | First dose |
    | CDT | Lambs at 8-10 weeks | Booster |

    Consider also:
    - Campylobacter/Chlamydia if abortion history
    - Rabies (skunks common in Alabama)

    Would you like more detail on any of these topics?
```

---

### Scenario 5: Should I Buy This Ram?

**The situation:** You are at a sale and considering purchasing a ram. You want a quick evaluation.

**Starting the conversation:**

> "I'm looking at a ram for sale. LPN ID is 6402-2024-ABC. Is he worth $2,000 for my terminal lamb operation?"

**How the conversation unfolds:**

```
You: I'm looking at a ram for sale. LPN ID is 6402-2024-ABC.
     Is he worth $2,000 for my terminal lamb operation?

AI: Let me look him up and give you a quick evaluation.

    ## Ram Evaluation: 6402-2024-ABC

    **Breed**: Suffolk
    **Age**: 2 years old
    **Farm**: Mountain View Farm

    ### His EBVs

    | Trait | Value | Breed Rank | Assessment |
    |-------|-------|------------|------------|
    | BWT | +0.8 | Top 40% | Average |
    | WWT | +6.2 | Top 20% | Good |
    | PWWT | +9.5 | Top 15% | Very Good |
    | YEMD | +2.1 | Top 10% | Excellent |
    | YFAT | +0.3 | Top 50% | Average |

    ### For Terminal Production

    **Strengths:**
    - Excellent post-weaning growth (+9.5)
    - Outstanding muscle depth (+2.1 YEMD)
    - Will sire fast-growing, meaty lambs

    **Concerns:**
    - BWT +0.8 is higher than ideal (larger birth weights)
    - May want to avoid on maiden ewes
    - Accuracy is 68% (good but could improve with more progeny)

    ### Price Assessment

    For $2,000:
    - Top 15% genetics for growth = reasonable value
    - Compare to AI costs: ~$35/ewe, so 57 ewes to break even
    - Consider how many ewes you will breed

    ### My Recommendation

    **Buy if:**
    - You have 40+ ewes
    - Terminal lamb sales are your focus
    - Your ewes are mature (not maidens)

    **Pass if:**
    - You need a maternal ram
    - Most of your ewes are young
    - You have fewer than 30 ewes (consider AI instead)

    Would you like me to compare him to other rams on the sale list?
```

---

### Scenario 6: Understanding My Flock Report

**The situation:** You received your NSIP flock report and do not understand what the numbers mean.

**Starting the conversation:**

> "I just got my NSIP report back. Can you help me understand what my ram's numbers mean? His report shows: BWT 0.4, WWT 3.8, PWWT 5.2, MWWT 1.5, NLW 0.08"

**How the conversation unfolds:**

```
You: I just got my NSIP report back. Can you help me understand
     what my ram's numbers mean? His report shows: BWT 0.4,
     WWT 3.8, PWWT 5.2, MWWT 1.5, NLW 0.08

AI: I would be happy to explain each of these values and what they
    mean for your breeding program.

    ## Your Ram's EBV Breakdown

    ### BWT (Birth Weight): +0.4

    **What it means**: His lambs are predicted to be born 0.4 lbs
    heavier than breed average.

    **Is this good?**
    - Slightly above average (neutral to mildly concerning)
    - Lower is generally better (easier lambing)
    - Watch carefully with maiden ewes

    ---

    ### WWT (Weaning Weight): +3.8

    **What it means**: His lambs are predicted to weigh 3.8 lbs
    more than breed average at weaning.

    **Is this good?**
    - Yes! This is above breed average
    - Faster-growing lambs reach market weight sooner
    - Good for commercial lamb production

    ---

    ### PWWT (Post-Weaning Weight): +5.2

    **What it means**: His lambs are predicted to weigh 5.2 lbs
    more than breed average at ~200 days.

    **Is this good?**
    - Yes! Solid above-average growth
    - Important for market lamb production
    - This ram should produce lambs that finish well

    ---

    ### MWWT (Maternal Weaning Weight): +1.5

    **What it means**: Daughters of this ram are predicted to wean
    lambs 1.5 lbs heavier than breed average (due to better
    mothering - more milk, better care).

    **Is this good?**
    - Above average maternal ability
    - His daughters should make good mothers
    - Important if you are keeping replacement ewe lambs

    ---

    ### NLW (Number of Lambs Weaned): +0.08

    **What it means**: Daughters of this ram are predicted to wean
    0.08 more lambs per year than breed average.

    **Is this good?**
    - Slightly above average
    - Over 100 ewes, that is 8 extra lambs weaned per year
    - Combined with MWWT, suggests decent maternal genetics

    ---

    ## Overall Assessment

    **Your ram's profile:** Growth-focused with acceptable maternal

    | Purpose | Suitability |
    |---------|-------------|
    | Terminal (market lambs only) | Very Good |
    | Maternal (replacement ewes) | Average |
    | Balanced (both purposes) | Good |

    **Bottom line**: This is a solid, above-average ram. Use
    confidently for market lamb production. If keeping his daughters
    as replacements, they should perform adequately but will not be
    exceptional mothers.

    Would you like me to compare these values to specific breeding goals?
```

---

## Quick Reference

### Which Prompt Should I Use?

| I Want To... | Use This Prompt |
|--------------|-----------------|
| Compare several animals' EBVs | `ebv_analyzer` |
| See my whole flock at a glance | `flock_dashboard` |
| Check if a sire's offspring are performing | `progeny_report` |
| Rank animals by overall merit | `selection_index` |
| See an animal's pedigree | `ancestry` |
| Check inbreeding for a mating | `inbreeding` |
| Plan breeding pairs (with help) | `guided_mating_plan` |
| Create a multi-generation improvement plan | `guided_trait_improvement` |
| Get personalized breeding advice | `guided_breeding_recommendations` |
| Import my flock from a spreadsheet | `guided_flock_import` |
| Ask any sheep question | `shepherd_consult` |
| Get genetics/breeding advice | `shepherd_breeding` |
| Get health/nutrition advice | `shepherd_health` |
| Plan seasonal tasks | `shepherd_calendar` |
| Understand costs and profitability | `shepherd_economics` |

### Common Trait Abbreviations

| Trait | Full Name | Higher is Better? |
|-------|-----------|-------------------|
| BWT | Birth Weight | No (lower = easier lambing) |
| WWT | Weaning Weight | Yes |
| PWWT | Post-Weaning Weight | Yes |
| MWWT | Maternal Weaning Weight | Yes |
| NLB | Number Lambs Born | Yes |
| NLW | Number Lambs Weaned | Yes |
| YEMD | Yearling Eye Muscle Depth | Yes |
| YFAT | Yearling Fat Depth | Moderate is ideal |

### NSIP Regions

| Region | States |
|--------|--------|
| Northeast | ME, NH, VT, MA, RI, CT, NY, NJ, PA |
| Southeast | MD, DE, VA, WV, NC, SC, GA, FL, AL, MS, TN, KY |
| Midwest | OH, IN, IL, MI, WI, MN, IA, MO, ND, SD, NE, KS |
| Southwest | TX, OK, AR, LA, AZ, NM |
| Mountain | MT, WY, CO, UT, ID, NV |
| Pacific | WA, OR, CA, AK, HI |

---

## See Also

- [Getting Started Guide](/docs/getting-started-guide.md) - Installation and setup
- [MCP Prompts Technical Reference](/docs/mcp-prompts.md) - Developer documentation
- [Shepherd Agent Documentation](/docs/shepherd-agent.md) - AI advisor details
- [NSIP Skills Documentation](/docs/nsip-skills.md) - Breeding analysis tools

---

*This guide was created for sheep farmers and breeders who want practical help using AI-assisted breeding analysis. No programming experience required.*

*Last Updated: December 2025*
