---
description: Import and enrich flock data from spreadsheets with NSIP breeding values
allowed-tools: Bash(uv run:*)
---

# /nsip:flock-import

Import and enrich flock data from a spreadsheet with NSIP breeding values.

## Usage

```
/nsip:flock-import <spreadsheet_path> [--output <output_path>]
```

## Arguments

- `spreadsheet_path`: Path to CSV, Excel (.xlsx), or Google Sheets URL
- `--output`: Optional output path for enriched data (default: enriched_<input>)

## Process

1. Parse the input spreadsheet to extract LPN IDs
2. Validate all LPN IDs against NSIP database
3. Fetch complete EBV data, lineage, and status for each animal
4. Merge local data (name, tag, notes) with NSIP data
5. Generate enriched output spreadsheet
6. Create validation report showing any missing/invalid entries

## Example

```bash
# Import from CSV
uv run python -m nsip_skills.flock_import flock.csv

# Import from Excel with custom output
uv run python -m nsip_skills.flock_import flock.xlsx --output enriched_flock.xlsx

# Import and include lineage
uv run python -m nsip_skills.flock_import flock.csv --include-lineage
```

## Required Columns

The input spreadsheet must have a column named one of:
- `LPN_ID`, `lpn_id`, `LPN`, `lpn`

Optional columns that will be preserved:
- `Name`, `name`
- `Tag`, `tag`
- `Notes`, `notes`

## Output

The enriched spreadsheet adds:
- All EBV traits (BWT, WWT, PWWT, YFAT, YEMD, NLW, etc.)
- Accuracy values for each trait
- Breed, gender, date of birth, status
- Sire LPN, Dam LPN (if --include-lineage)
- Validation status

$ARGUMENTS
