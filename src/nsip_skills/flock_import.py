"""
Flock import and enrichment module.

Import animal data from spreadsheets and enrich with NSIP API data.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from nsip_skills.common.data_models import (
    AnimalAnalysis,
    EnrichedFlockRecord,
    TraitProfile,
    TraitValue,
)
from nsip_skills.common.formatters import format_validation_report
from nsip_skills.common.nsip_wrapper import CachedNSIPClient
from nsip_skills.common.spreadsheet_io import (
    extract_flock_records,
    read_spreadsheet,
    write_spreadsheet,
)


@dataclass
class ImportResult:
    """Result of a flock import operation."""

    total_records: int = 0
    successful: int = 0
    not_found: list[str] = field(default_factory=list)
    errors: dict[str, str] = field(default_factory=dict)
    enriched_records: list[EnrichedFlockRecord] = field(default_factory=list)
    source_file: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_records": self.total_records,
            "successful": self.successful,
            "not_found": self.not_found,
            "errors": self.errors,
            "enriched_records": [r.to_dict() for r in self.enriched_records],
            "source_file": self.source_file,
        }


def import_flock(
    source: str | Path,
    sheet_name: str | int | None = None,
    include_lineage: bool = False,
    include_progeny: bool = False,
    client: CachedNSIPClient | None = None,
) -> ImportResult:
    """
    Import a flock from a spreadsheet and enrich with NSIP data.

    Args:
        source: Path to spreadsheet file or Google Sheets URL
        sheet_name: Sheet name for multi-sheet files
        include_lineage: Also fetch lineage data for each animal
        include_progeny: Also fetch progeny data for each animal
        client: Optional pre-configured client (created if not provided)

    Returns:
        ImportResult with enriched records and validation info

    Example:
        result = import_flock("my_flock.csv")
        print(f"Imported {result.successful}/{result.total_records} animals")
    """
    # Read spreadsheet
    data = read_spreadsheet(source, sheet_name=sheet_name)
    records = extract_flock_records(data)

    result = ImportResult(
        total_records=len(records),
        source_file=str(source),
    )

    if not records:
        return result

    # Create client if not provided
    should_close = client is None
    if client is None:
        client = CachedNSIPClient()

    try:
        # Fetch NSIP data for each record
        lpn_ids = [r.lpn_id for r in records]
        fetched = client.batch_get_animals(
            lpn_ids,
            include_lineage=include_lineage,
            include_progeny=include_progeny,
            on_error="skip",
        )

        for record in records:
            fetch_data = fetched.get(record.lpn_id, {})

            if "error" in fetch_data:
                error_msg = fetch_data["error"]
                if "Not found" in error_msg:
                    result.not_found.append(record.lpn_id)
                else:
                    result.errors[record.lpn_id] = error_msg
                result.enriched_records.append(
                    EnrichedFlockRecord(
                        local=record,
                        fetch_error=error_msg,
                    )
                )
            else:
                # Build AnimalAnalysis from fetched data
                details = fetch_data.get("details")
                analysis = None

                if details:
                    # Build trait profile
                    trait_profile = TraitProfile(
                        lpn_id=record.lpn_id,
                        breed=details.breed,
                    )
                    for trait_name, trait_obj in details.traits.items():
                        trait_profile.traits[trait_name] = TraitValue(
                            name=trait_name,
                            value=trait_obj.value,
                            accuracy=trait_obj.accuracy,
                        )

                    analysis = AnimalAnalysis(
                        lpn_id=record.lpn_id,
                        breed=details.breed,
                        breed_id=None,  # Not directly available
                        gender=details.gender,
                        date_of_birth=details.date_of_birth,
                        status=details.status,
                        sire_lpn=details.sire,
                        dam_lpn=details.dam,
                        trait_profile=trait_profile,
                        progeny_count=details.total_progeny,
                    )
                    result.successful += 1

                result.enriched_records.append(
                    EnrichedFlockRecord(
                        local=record,
                        nsip_details=analysis,
                    )
                )

    finally:
        if should_close and client:
            client.close()

    return result


def export_enriched_flock(
    result: ImportResult,
    output_path: str | Path,
    format: str = "auto",
    include_traits: list[str] | None = None,
) -> None:
    """
    Export enriched flock data to a spreadsheet.

    Args:
        result: ImportResult from import_flock()
        output_path: Path for output file
        format: "csv", "excel", or "auto"
        include_traits: Specific traits to include (None = all)
    """
    default_traits = ["BWT", "WWT", "PWWT", "YEMD", "YFAT", "NLB", "NLW"]
    traits = include_traits or default_traits

    rows: list[dict[str, Any]] = []
    for enriched in result.enriched_records:
        row: dict[str, Any] = {
            "lpn_id": enriched.local.lpn_id,
            "local_id": enriched.local.local_id or "",
            "group": enriched.local.group or "",
            "notes": enriched.local.notes or "",
        }

        if enriched.nsip_details:
            details = enriched.nsip_details
            row.update(
                {
                    "breed": details.breed or "",
                    "gender": details.gender or "",
                    "date_of_birth": details.date_of_birth or "",
                    "status": details.status or "",
                    "sire": details.sire_lpn or "",
                    "dam": details.dam_lpn or "",
                    "progeny_count": details.progeny_count or 0,
                }
            )

            # Add trait values
            if details.trait_profile:
                for trait in traits:
                    tv = details.trait_profile.traits.get(trait)
                    row[trait] = tv.value if tv else ""
                    row[f"{trait}_acc"] = tv.accuracy if tv and tv.accuracy else ""
        else:
            row["fetch_error"] = enriched.fetch_error or "Unknown error"

        rows.append(row)

    # Define column order
    columns = [
        "lpn_id",
        "local_id",
        "group",
        "notes",
        "breed",
        "gender",
        "date_of_birth",
        "status",
        "sire",
        "dam",
        "progeny_count",
    ]
    for trait in traits:
        columns.extend([trait, f"{trait}_acc"])
    columns.append("fetch_error")

    write_spreadsheet(rows, output_path, format=format, columns=columns)


def generate_import_report(result: ImportResult) -> str:
    """Generate a human-readable import report."""
    valid_ids = [r.local.lpn_id for r in result.enriched_records if r.nsip_details]
    return format_validation_report(
        valid=valid_ids,
        not_found=result.not_found,
        errors=result.errors,
    )


# CLI interface for standalone script execution
def main():
    """Command-line interface for flock import."""
    import argparse

    parser = argparse.ArgumentParser(description="Import and enrich flock data from NSIP")
    parser.add_argument("source", help="Path to spreadsheet or Google Sheets URL")
    parser.add_argument("-o", "--output", help="Output file path (default: enriched_<source>)")
    parser.add_argument("--sheet", help="Sheet name for multi-sheet files")
    parser.add_argument("--lineage", action="store_true", help="Include lineage data")
    parser.add_argument("--progeny", action="store_true", help="Include progeny data")
    parser.add_argument("--format", choices=["csv", "excel", "auto"], default="auto")
    parser.add_argument("--json", action="store_true", help="Output as JSON instead")

    args = parser.parse_args()

    result = import_flock(
        source=args.source,
        sheet_name=args.sheet,
        include_lineage=args.lineage,
        include_progeny=args.progeny,
    )

    print(generate_import_report(result))

    if args.json:
        print(json.dumps(result.to_dict(), indent=2, default=str))
    elif args.output or not args.json:
        output_path = args.output or f"enriched_{Path(args.source).stem}.csv"
        export_enriched_flock(result, output_path, format=args.format)
        print(f"\nExported to: {output_path}")

    return 0 if result.successful == result.total_records else 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
