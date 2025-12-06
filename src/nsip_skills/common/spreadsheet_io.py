"""
Spreadsheet I/O utilities for NSIP skills.

Supports reading and writing CSV, Excel (.xlsx), and Google Sheets.
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from nsip_skills.common.data_models import FlockRecord


@dataclass
class SpreadsheetData:
    """Container for spreadsheet data with metadata."""

    rows: list[dict[str, Any]]
    source: str  # File path or URL
    source_type: str  # "csv", "excel", "gsheets"
    sheet_name: str | None = None
    column_mapping: dict[str, str] | None = None  # Original -> normalized names


# Column name variations to normalize
LPN_ID_COLUMNS = ["lpn_id", "lpnid", "lpn", "id", "animal_id", "animalid", "nsip_id"]
LOCAL_ID_COLUMNS = ["local_id", "localid", "tag", "ear_tag", "name", "animal_name"]
NOTES_COLUMNS = ["notes", "note", "comments", "comment", "remarks"]
GROUP_COLUMNS = ["group", "pen", "pasture", "lot", "category"]


def normalize_column_name(name: str) -> str:
    """Normalize column name to lowercase with underscores."""
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def find_lpn_column(columns: list[str]) -> str | None:
    """Find the LPN ID column from a list of column names."""
    normalized = {normalize_column_name(c): c for c in columns}
    for candidate in LPN_ID_COLUMNS:
        if candidate in normalized:
            return normalized[candidate]
    return None


def detect_column_mapping(columns: list[str]) -> dict[str, str]:
    """
    Detect which columns map to which fields.

    Returns dict of original_name -> field_name.
    """
    mapping = {}
    normalized = {normalize_column_name(c): c for c in columns}

    # Find LPN ID column
    for candidate in LPN_ID_COLUMNS:
        if candidate in normalized:
            mapping[normalized[candidate]] = "lpn_id"
            break

    # Find local ID column
    for candidate in LOCAL_ID_COLUMNS:
        if candidate in normalized:
            mapping[normalized[candidate]] = "local_id"
            break

    # Find notes column
    for candidate in NOTES_COLUMNS:
        if candidate in normalized:
            mapping[normalized[candidate]] = "notes"
            break

    # Find group column
    for candidate in GROUP_COLUMNS:
        if candidate in normalized:
            mapping[normalized[candidate]] = "group"
            break

    return mapping


def read_csv(path: str | Path) -> SpreadsheetData:
    """Read a CSV file."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")

    rows = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames or []
        for row in reader:
            rows.append(dict(row))

    return SpreadsheetData(
        rows=rows,
        source=str(path),
        source_type="csv",
        column_mapping=detect_column_mapping(list(columns)),
    )


def read_excel(path: str | Path, sheet_name: str | int = 0) -> SpreadsheetData:
    """
    Read an Excel file.

    Args:
        path: Path to .xlsx file
        sheet_name: Sheet name or 0-indexed position (default: first sheet)
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError(
            "pandas and openpyxl required for Excel support: pip install pandas openpyxl"
        )

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Excel file not found: {path}")

    df = pd.read_excel(path, sheet_name=sheet_name)
    columns = list(df.columns)
    rows = df.to_dict("records")

    return SpreadsheetData(
        rows=rows,
        source=str(path),
        source_type="excel",
        sheet_name=str(sheet_name) if isinstance(sheet_name, str) else None,
        column_mapping=detect_column_mapping(columns),
    )


def read_google_sheets(url: str, sheet_name: str | None = None) -> SpreadsheetData:
    """
    Read a Google Sheets document.

    Requires gspread library and Google Cloud credentials configured.

    Args:
        url: Google Sheets URL
        sheet_name: Specific sheet name (default: first sheet)
    """
    try:
        import gspread
    except ImportError:
        raise ImportError("gspread required for Google Sheets support: pip install gspread")

    # Extract sheet ID from URL
    match = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", url)
    if not match:
        raise ValueError(f"Invalid Google Sheets URL: {url}")

    sheet_id = match.group(1)

    # Connect and fetch data
    gc = gspread.service_account()  # Uses default credentials
    spreadsheet = gc.open_by_key(sheet_id)

    if sheet_name:
        worksheet = spreadsheet.worksheet(sheet_name)
    else:
        worksheet = spreadsheet.sheet1

    records = worksheet.get_all_records()
    columns = list(records[0].keys()) if records else []

    return SpreadsheetData(
        rows=records,
        source=url,
        source_type="gsheets",
        sheet_name=worksheet.title,
        column_mapping=detect_column_mapping(columns),
    )


def read_spreadsheet(
    source: str | Path,
    sheet_name: str | int | None = None,
) -> SpreadsheetData:
    """
    Read a spreadsheet from file or URL.

    Automatically detects format from extension or URL pattern.

    Args:
        source: File path or Google Sheets URL
        sheet_name: Sheet name for multi-sheet files (Excel/GSheets)

    Returns:
        SpreadsheetData with rows and metadata
    """
    source_str = str(source)

    # Check if it's a Google Sheets URL
    if "docs.google.com/spreadsheets" in source_str:
        return read_google_sheets(
            source_str, sheet_name=sheet_name if isinstance(sheet_name, str) else None
        )

    # Handle file
    path = Path(source)
    suffix = path.suffix.lower()

    if suffix == ".csv":
        return read_csv(path)
    elif suffix in (".xlsx", ".xls"):
        return read_excel(path, sheet_name=sheet_name if sheet_name is not None else 0)
    else:
        # Try to infer from content
        if path.exists():
            with open(path, "rb") as f:
                header = f.read(4)
            if header[:2] == b"PK":  # ZIP signature (xlsx)
                return read_excel(path, sheet_name=sheet_name if sheet_name is not None else 0)
        # Default to CSV
        return read_csv(path)


def extract_flock_records(data: SpreadsheetData) -> list[FlockRecord]:
    """
    Extract FlockRecord objects from spreadsheet data.

    Uses column mapping to identify fields.

    Returns:
        List of FlockRecord objects
    """
    records = []
    mapping = data.column_mapping or {}

    # Reverse mapping: field_name -> original_column_name
    field_to_column = {v: k for k, v in mapping.items()}

    lpn_column = field_to_column.get("lpn_id")
    if not lpn_column:
        # Try to find it manually
        if data.rows:
            lpn_column = find_lpn_column(list(data.rows[0].keys()))

    if not lpn_column:
        raise ValueError("Could not identify LPN ID column in spreadsheet")

    local_id_column = field_to_column.get("local_id")
    notes_column = field_to_column.get("notes")
    group_column = field_to_column.get("group")

    for i, row in enumerate(data.rows, 1):
        lpn_id = row.get(lpn_column)
        if not lpn_id or not str(lpn_id).strip():
            continue  # Skip empty rows

        records.append(
            FlockRecord(
                lpn_id=str(lpn_id).strip(),
                local_id=(
                    str(row.get(local_id_column, "")).strip() or None if local_id_column else None
                ),
                notes=str(row.get(notes_column, "")).strip() or None if notes_column else None,
                group=str(row.get(group_column, "")).strip() or None if group_column else None,
                row_number=i,
            )
        )

    return records


def write_csv(
    records: list[dict[str, Any]],
    path: str | Path,
    columns: list[str] | None = None,
) -> None:
    """
    Write records to a CSV file.

    Args:
        records: List of dicts to write
        path: Output file path
        columns: Column order (default: keys from first record)
    """
    if not records:
        return

    path = Path(path)

    # Get all possible columns from records, filtering to requested if specified
    all_keys: set[str] = set()
    for record in records:
        all_keys.update(record.keys())

    if columns:
        # Filter to only columns that exist in at least one record
        columns = [c for c in columns if c in all_keys]
    else:
        columns = list(records[0].keys())

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)


def write_excel(
    records: list[dict[str, Any]],
    path: str | Path,
    sheet_name: str = "Sheet1",
    columns: list[str] | None = None,
) -> None:
    """
    Write records to an Excel file.

    Args:
        records: List of dicts to write
        path: Output file path
        sheet_name: Name for the worksheet
        columns: Column order (default: keys from first record)
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError(
            "pandas and openpyxl required for Excel support: pip install pandas openpyxl"
        )

    if not records:
        return

    path = Path(path)
    df = pd.DataFrame(records)

    # Filter columns to only those that exist in the data
    if columns:
        existing_columns = [c for c in columns if c in df.columns]
        df = df[existing_columns]

    df.to_excel(path, sheet_name=sheet_name, index=False)


def write_spreadsheet(
    records: list[dict[str, Any]],
    path: str | Path,
    format: str = "auto",
    sheet_name: str = "Sheet1",
    columns: list[str] | None = None,
) -> None:
    """
    Write records to a spreadsheet file.

    Args:
        records: List of dicts to write
        path: Output file path
        format: "csv", "excel", or "auto" (detect from extension)
        sheet_name: Sheet name for Excel files
        columns: Column order
    """
    path = Path(path)

    if format == "auto":
        suffix = path.suffix.lower()
        if suffix in (".xlsx", ".xls"):
            format = "excel"
        else:
            format = "csv"

    if format == "excel":
        write_excel(records, path, sheet_name=sheet_name, columns=columns)
    else:
        write_csv(records, path, columns=columns)
