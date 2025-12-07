# Getting Started with NSIP Tools for AI Assistants

A plain-English guide for sheep farmers and breeders who want to use AI assistants to help with breeding decisions.

---

## Table of Contents

1. [What This Is and Why It Matters](#what-this-is-and-why-it-matters)
2. [Before You Begin](#before-you-begin)
3. [Installation for Claude Desktop](#installation-for-claude-desktop)
4. [Verifying Everything Works](#verifying-everything-works)
5. [What You Can Ask](#what-you-can-ask)
6. [Common Questions and Examples](#common-questions-and-examples)
7. [Troubleshooting](#troubleshooting)
8. [Glossary of Terms](#glossary-of-terms)
9. [Getting Help](#getting-help)

---

## What This Is and Why It Matters

### What is NSIP?

The **National Sheep Improvement Program (NSIP)** is a genetic evaluation program used by sheep breeders across the United States. If you participate in NSIP, your animals have **Estimated Breeding Values (EBVs)** that predict how their genetics will affect their offspring.

Think of EBVs like a genetic report card - they tell you what traits an animal is likely to pass on to their lambs: growth rate, birth weight, maternal ability, and more.

### What is this tool?

This tool connects AI assistants (like Claude) directly to NSIP's database of sheep genetics. Instead of manually looking up each animal on the NSIP website, you can simply ask your AI assistant questions like:

- "Look up the breeding values for my ram"
- "Compare these three ewes I'm considering buying"
- "What's the inbreeding risk if I breed these two animals?"
- "Help me plan my lambing season for March lambing"

### What is MCP?

**MCP (Model Context Protocol)** is the technology that allows AI assistants to access external data sources. You do not need to understand how it works - just think of it as the "bridge" that lets Claude (or other AI assistants) read your sheep's genetic data from NSIP.

### Who is this for?

This guide is written for sheep farmers and breeders who:

- Participate in NSIP or are considering it
- Want data-driven help with breeding decisions
- Are NOT programmers but are comfortable with basic computer tasks
- Want to use AI assistants more effectively for their operation

---

## Before You Begin

### What You Need

1. **A computer** (Windows, Mac, or Linux)
2. **Claude Desktop app** (free download from Anthropic)
3. **Your animals' LPN IDs** (the unique NSIP identification numbers for your sheep)

### Finding Your LPN IDs

Your LPN (Lot-Prefix-Number) IDs are the unique identifiers NSIP assigns to each animal. They look something like this: `6402382024NCS310`

You can find them:
- On your NSIP flock reports
- On the NSIP Search website (nsipsearch.nsip.org)
- In correspondence from your breed association

If you are not sure what your animals' LPN IDs are, contact your breed association or NSIP directly.

---

## Installation for Claude Desktop

Follow these steps to connect the NSIP tools to Claude Desktop. This is a one-time setup that takes about 10 minutes.

### Step 1: Download and Install Claude Desktop

If you do not already have Claude Desktop:

1. Go to [claude.ai/download](https://claude.ai/download)
2. Download the Claude Desktop application for your computer
3. Install it following the on-screen instructions
4. Open Claude Desktop and sign in (or create an account)

### Step 2: Install uv (The Easy Way to Run Python Tools)

**uv** is a modern tool that makes running Python programs simple - no complicated setup required. It handles everything automatically.

---

#### Installing uv on Mac

1. **Open Terminal**
   - Press `Cmd + Space` to open Spotlight
   - Type "Terminal" and press Enter

2. **Install uv** by copying and pasting this command:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Close and reopen Terminal** for the installation to take effect

4. **Verify it worked** by typing:
   ```bash
   uvx --version
   ```
   You should see a version number like `uv 0.5.x`

---

#### Installing uv on Windows

1. **Open PowerShell**
   - Press `Windows + X`
   - Click "Windows PowerShell" or "Terminal"

2. **Install uv** by copying and pasting this command:
   ```powershell
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

3. **Close and reopen PowerShell** for the installation to take effect

4. **Verify it worked** by typing:
   ```powershell
   uvx --version
   ```
   You should see a version number like `uv 0.5.x`

---

#### Troubleshooting uv Installation

**Mac - "command not found: uvx"**
- Close Terminal completely and reopen it
- Or run: `source ~/.zshrc` (or `source ~/.bashrc` if using bash)

**Windows - "uvx is not recognized"**
- Close PowerShell completely and reopen it
- Make sure you installed as Administrator if prompted

**Still not working?**
- Visit [docs.astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/) for detailed instructions
- Or ask Claude: "Help me install uv on my computer"

### Step 3: Configure Claude Desktop

Now you need to tell Claude Desktop how to find the NSIP tools. This is a simple configuration file edit.

---

#### On Mac

1. **Open Finder**

2. **Go to the Claude configuration folder:**
   - Click "Go" in the menu bar
   - Click "Go to Folder..."
   - Type: `~/Library/Application Support/Claude/`
   - Click "Go"

3. **Edit or create the configuration file:**
   - Look for a file called `claude_desktop_config.json`
   - If it exists, double-click to open it in TextEdit
   - If it does not exist, we'll create it in the next step

4. **Open TextEdit and create the file** (if needed):
   - Open TextEdit (search for it in Spotlight)
   - Go to Format → Make Plain Text
   - Copy the configuration below
   - Save as `claude_desktop_config.json` in the Claude folder

---

#### On Windows

1. **Open the Claude configuration folder:**
   - Press `Windows + R` to open Run
   - Type: `%APPDATA%\Claude\`
   - Press Enter

2. **Edit or create the configuration file:**
   - Look for a file called `claude_desktop_config.json`
   - If it exists, right-click and choose "Open with" → "Notepad"
   - If it does not exist, we'll create it in the next step

3. **Create the file** (if needed):
   - Right-click in the folder
   - Choose "New" → "Text Document"
   - Name it exactly: `claude_desktop_config.json`
   - (Make sure to remove the `.txt` extension if Windows adds one)
   - Open it with Notepad

---

#### The Configuration File

Copy and paste this entire block into your `claude_desktop_config.json` file:

```json
{
  "mcpServers": {
    "nsip": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/epicpast/nsip-api-client",
        "nsip-mcp-server"
      ]
    }
  }
}
```

**Important:**
- Make sure you copy the entire block including the curly braces `{ }`
- The file must be valid JSON - watch for missing commas or brackets
- Save the file after pasting

---

#### If You Already Have Other MCP Servers Configured

If your `claude_desktop_config.json` already has content, you need to add the NSIP server to the existing configuration. Your file might look like this:

```json
{
  "mcpServers": {
    "some-other-server": {
      "command": "some-command"
    },
    "nsip": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/epicpast/nsip-api-client",
        "nsip-mcp-server"
      ]
    }
  }
}
```

Notice the comma after the first server's closing brace. If you are not sure how to merge configurations, ask Claude for help!

### Step 4: Restart Claude Desktop

1. **Completely close Claude Desktop:**
   - Mac: Right-click the Claude icon in the Dock and choose "Quit"
   - Windows: Right-click Claude in the taskbar and choose "Close window"

2. **Reopen Claude Desktop**

3. **The NSIP tools should now be available!**

The first time you use the tools, uvx will automatically download everything needed. This may take 30-60 seconds on the first request.

---

## Verifying Everything Works

To make sure everything is set up correctly, try this simple test:

Open Claude Desktop and type:

> "Can you check when the NSIP database was last updated?"

If the tools are working, Claude will connect to NSIP and tell you the date. The response will look something like:

> "The NSIP database was last updated on 09/23/2025."

If you see an error message instead, jump to the [Troubleshooting](#troubleshooting) section.

---

## What You Can Ask

Once set up, you can ask Claude to help with many aspects of sheep breeding. Here are the main categories:

### Looking Up Individual Animals

Ask Claude to retrieve breeding values, pedigree information, or offspring records for any animal in the NSIP database.

**Examples:**
- "Look up the animal with LPN ID 6402382024NCS310"
- "What are the breeding values for my ram?"
- "Show me the pedigree for this ewe"
- "How many offspring does this sire have?"

### Comparing Animals

When evaluating purchase candidates or selecting breeding stock, ask Claude to compare multiple animals side-by-side.

**Examples:**
- "Compare these three rams I'm considering buying"
- "Which of these ewes has the best maternal traits?"
- "Rank these animals by weaning weight EBV"

### Breeding and Genetics Advice

The built-in "Shepherd" advisor can help you understand genetics and make breeding decisions.

**Examples:**
- "What does a WWT EBV of 3.5 mean?"
- "How should I select for better lambing ease?"
- "What traits should I focus on for terminal production?"
- "Is inbreeding a concern if I breed these two animals?"

### Health and Nutrition Guidance

Get region-specific advice on keeping your flock healthy.

**Examples:**
- "What parasite control strategies work best in the Southeast?"
- "How should I feed my ewes during late gestation?"
- "What vaccinations do my sheep need?"

### Seasonal Planning

Get help planning your breeding calendar and management schedule.

**Examples:**
- "I want lambs in March - when should I put the ram in?"
- "Help me plan my lambing season"
- "What tasks should I complete before breeding season?"

### Economic Analysis

Get help with the business side of your operation.

**Examples:**
- "Is this $2000 ram worth the investment?"
- "What's my breakeven price per lamb?"
- "How can I improve my operation's profitability?"

---

## Common Questions and Examples

Here are some real-world scenarios showing how to use the NSIP tools with Claude.

### Scenario 1: Evaluating a Ram for Purchase

You are at a sale and considering buying a ram. You want to know his genetic merit.

**Ask Claude:**
> "Look up the complete profile for LPN ID 6402382023ABC456. I'm considering buying this ram for terminal production. What are his strengths and weaknesses?"

**Claude will provide:**
- The ram's breeding values for growth, carcass, and other traits
- His pedigree (sire and dam)
- Number of offspring and their performance
- An assessment of whether he fits your production goals

### Scenario 2: Planning a Mating

You want to breed a specific ram to one of your ewes but are concerned about inbreeding.

**Ask Claude:**
> "I want to breed my ram (LPN 6402382022RAM001) to my ewe (LPN 6402382021EWE005). Can you check if they share any common ancestors and what the inbreeding would be for the offspring?"

**Claude will provide:**
- Whether the animals share ancestors
- The projected inbreeding coefficient
- A recommendation on whether to proceed

### Scenario 3: Understanding Your Flock

You want an overview of your flock's genetic strengths and weaknesses.

**Ask Claude:**
> "I have a flock of Katahdin ewes focused on market lamb production. Here are my top 5 ewes' LPN IDs: [list them]. Can you summarize their breeding values and tell me what traits I should focus on improving?"

**Claude will provide:**
- A comparison of your ewes' EBVs
- Identification of flock-wide strengths
- Specific recommendations for improvement

### Scenario 4: Regional Management Advice

You are new to sheep production in your area and want location-specific guidance.

**Ask Claude:**
> "I'm starting a sheep operation in Georgia. What are the biggest health challenges I should prepare for, and what does a typical production calendar look like for the Southeast?"

**Claude will provide:**
- Region-specific disease and parasite concerns
- Recommended management calendar
- Climate considerations for your area

### Scenario 5: Interpreting Breeding Values

You received your flock's latest EBV report but are not sure what the numbers mean.

**Ask Claude:**
> "My ram's report shows: BWT 0.25, WWT 4.5, MWWT 2.1, NLW 0.15. Can you explain what each of these means and whether these are good values?"

**Claude will provide:**
- Plain-English explanations of each trait
- How your ram compares to breed average
- Practical implications for your flock

---

## Troubleshooting

### "The NSIP tools are not responding"

**Try these steps in order:**

1. **Restart Claude Desktop completely**
   - Mac: Right-click Claude in the Dock → Quit, then reopen
   - Windows: Right-click in taskbar → Close window, then reopen

2. **Check your internet connection**
   - The tools need to reach both GitHub (to download) and NSIP (for data)

3. **Verify uv is installed**
   - Open Terminal (Mac) or PowerShell (Windows)
   - Type `uvx --version` and press Enter
   - If you see an error, reinstall uv (see Step 2 above)

4. **Check the configuration file**
   - Make sure `claude_desktop_config.json` exists in the right location
   - Verify the JSON is valid (no missing commas or brackets)

5. **Test uvx directly**
   - In Terminal/PowerShell, run:
     ```
     uvx --from git+https://github.com/epicpast/nsip-api-client nsip-mcp-server --help
     ```
   - If this shows help text, uvx is working correctly

### "Animal not found"

This means the LPN ID you provided is not in the NSIP database.

**Common causes:**
- Typo in the LPN ID (check each character carefully)
- The animal is not enrolled in NSIP
- The animal was recently added and not yet in the public database

**Solution:** Double-check the LPN ID against your NSIP paperwork or search on the [NSIP Search website](https://nsipsearch.nsip.org).

### "Configuration file not found" or "Server not connecting"

**Check these things:**

1. **File location is correct:**
   - Mac: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. **File name is exactly right:**
   - Must be `claude_desktop_config.json` (not `.txt`)
   - Windows users: Make sure "Hide extensions for known file types" isn't hiding a `.txt` extension

3. **JSON is valid:**
   - All brackets `{ }` and `[ ]` are matched
   - Commas between items (but not after the last item)
   - Use a JSON validator like [jsonlint.com](https://jsonlint.com) if unsure

### "uvx: command not found" or "uvx is not recognized"

This means uv didn't install correctly or your terminal can't find it.

**On Mac:**
1. Close and reopen Terminal
2. Run: `source ~/.zshrc` (or `source ~/.bashrc`)
3. Try `uvx --version` again
4. If still not working, reinstall:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

**On Windows:**
1. Close and reopen PowerShell
2. Try `uvx --version` again
3. If still not working, reinstall:
   ```powershell
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

### First Request is Slow (30-60 seconds)

**This is normal!** The first time you use the NSIP tools after configuring them:

1. uvx downloads the NSIP package from GitHub
2. It installs all required dependencies
3. It starts the MCP server

This only happens once. After that, uvx caches everything, and future requests are fast (1-3 seconds).

**Subsequent slow requests** might mean:
- uvx updated the package (happens occasionally)
- Your computer restarted and cleared the cache
- You're looking up an animal with lots of progeny (large data)

### Data Seems Outdated

NSIP updates their database periodically (usually monthly). You can check when it was last updated by asking Claude:

> "When was the NSIP database last updated?"

The NSIP tools also cache results for 1 hour to improve speed. If you need fresh data for an animal you just looked up, wait an hour or restart Claude Desktop.

---

## Glossary of Terms

Understanding these terms will help you use the tools more effectively.

### Breeding Terms

| Term | What It Means |
|------|---------------|
| **EBV** | Estimated Breeding Value - a prediction of the genetic merit an animal will pass to offspring. Positive values are typically above breed average. |
| **Accuracy** | How reliable an EBV is (0-100%). Higher accuracy means more data supports the prediction. |
| **LPN ID** | Lot-Prefix-Number ID - the unique identifier for each animal in NSIP. Example: 6402382024NCS310 |
| **Pedigree** | An animal's family tree - its sire (father), dam (mother), and ancestors. |
| **Progeny** | An animal's offspring (lambs). |
| **Inbreeding Coefficient** | A percentage indicating how related an animal's parents are. Higher values mean more inbreeding. Below 6.25% is generally considered acceptable. |
| **Selection Index** | A single score that combines multiple EBVs based on economic importance. Makes it easier to rank animals for overall merit. |

### Common Trait Abbreviations

| Trait | What It Measures | Good Direction |
|-------|------------------|----------------|
| **BWT** | Birth Weight | Lower is better (easier lambing) |
| **WWT** | Weaning Weight | Higher is better (faster growth) |
| **PWWT** | Post-Weaning Weight | Higher is better |
| **MWWT** | Maternal Weaning Weight | Higher is better (better mothers) |
| **NLB** | Number of Lambs Born | Higher is better (more lambs) |
| **NLW** | Number of Lambs Weaned | Higher is better (lambs that survive) |
| **YEMD** | Yearling Eye Muscle Depth | Higher is better (more meat) |
| **YFAT** | Yearling Fat Depth | Moderate is ideal |

### Technical Terms

| Term | What It Means |
|------|---------------|
| **uv / uvx** | A modern Python package runner. uvx runs Python tools without complicated installation - it handles everything automatically. Think of it like an app store for Python tools. |
| **MCP** | Model Context Protocol - the technology that lets AI assistants access external data. You do not need to understand this to use the tools. |
| **API** | Application Programming Interface - how computer programs talk to each other. The NSIP tools use the NSIP API to get your data. |
| **Cache** | Temporary storage. The tools remember recent lookups for one hour so repeated requests are faster. |
| **JSON** | JavaScript Object Notation - a text format used for configuration files. The Claude Desktop config file uses JSON format. |

### Production Types

| Term | Focus |
|------|-------|
| **Terminal** | Producing market lambs for meat. Emphasizes growth and carcass traits. |
| **Maternal** | Producing replacement ewes. Emphasizes reproduction and mothering ability. |
| **Range** | Balanced production for extensive/pastoral systems. |
| **Hair** | Production with hair sheep breeds (Katahdin, St. Croix, etc.). |

### NSIP Regions

The Shepherd advisor provides region-specific guidance. Here are the regions:

| Region | States Included |
|--------|-----------------|
| **Northeast** | ME, NH, VT, MA, RI, CT, NY, NJ, PA |
| **Southeast** | MD, DE, VA, WV, NC, SC, GA, FL, AL, MS, TN, KY |
| **Midwest** | OH, IN, IL, MI, WI, MN, IA, MO, ND, SD, NE, KS |
| **Southwest** | TX, OK, AR, LA, AZ, NM |
| **Mountain** | MT, WY, CO, UT, ID, NV |
| **Pacific** | WA, OR, CA, AK, HI |

When asking for advice, mention your state or region for more relevant recommendations.

---

## Getting Help

### If the tools are not working:

1. Check the [Troubleshooting](#troubleshooting) section above
2. Ask Claude directly: "The NSIP tools don't seem to be working. Can you help me troubleshoot?"
3. Restart Claude Desktop and try again

### If you need help understanding results:

Just ask Claude to explain! For example:
- "Can you explain what these breeding values mean in simpler terms?"
- "I don't understand the inbreeding report. Can you break it down?"
- "What does this mean for my breeding program?"

### For NSIP account questions:

If you have questions about your NSIP membership, data submission, or account:
- Contact NSIP directly at [nsip.org](https://nsip.org)
- Reach out to your breed association

### For questions about this tool:

For technical issues or feature requests, visit the project repository on GitHub.

---

## Quick Reference Card

Keep this handy for common tasks:

| What You Want to Do | What to Ask Claude |
|--------------------|--------------------|
| Look up an animal | "Look up LPN ID [your ID]" |
| Compare animals | "Compare these animals: [list IDs]" |
| Check inbreeding | "What's the inbreeding if I breed [ram ID] to [ewe ID]?" |
| Get breeding advice | "I'm raising [breed] for [terminal/maternal]. What traits should I focus on?" |
| Plan lambing | "I want to lamb in [month]. When should breeding start?" |
| Understand a trait | "What does [trait abbreviation] mean?" |
| Get regional advice | "What are the main sheep health concerns in [your state]?" |

---

*This guide was created for sheep farmers and breeders new to using AI assistants with NSIP data. No programming experience required.*

*Last Updated: December 2025*
