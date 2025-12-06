"""
Command-line interface for NSIP client
"""

import argparse
import json
import sys

from .client import NSIPClient
from .exceptions import NSIPError


def main(args: list | None = None) -> int:
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="NSIP Search API Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("--version", action="store_true", help="Show version and exit")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search for an animal")
    search_parser.add_argument("lpn_id", help="LPN ID to search for")
    search_parser.add_argument(
        "--full", action="store_true", help="Get full profile (details, lineage, progeny)"
    )

    # List breed groups
    subparsers.add_parser("breeds", help="List available breed groups")

    # Search animals
    find_parser = subparsers.add_parser("find", help="Search for animals")
    find_parser.add_argument("--breed-id", type=int, help="Filter by breed ID")
    find_parser.add_argument("--page", type=int, default=0, help="Page number (0-indexed)")
    find_parser.add_argument("--page-size", type=int, default=15, help="Results per page")

    # Parse arguments
    parsed_args = parser.parse_args(args)

    if parsed_args.version:
        from . import __version__

        print(f"nsip-client version {__version__}")
        return 0

    if not parsed_args.command:
        parser.print_help()
        return 1

    try:
        client = NSIPClient()

        if parsed_args.command == "search":
            if parsed_args.full:
                result = client.search_by_lpn(parsed_args.lpn_id)
                print(
                    json.dumps(
                        {
                            "details": result["details"].raw_data,
                            "lineage": result["lineage"].raw_data,
                            "progeny": {
                                "total_count": result["progeny"].total_count,
                                "animals": [
                                    {"lpn_id": a.lpn_id, "sex": a.sex, "dob": a.date_of_birth}
                                    for a in result["progeny"].animals
                                ],
                            },
                        },
                        indent=2,
                    )
                )
            else:
                details = client.get_animal_details(parsed_args.lpn_id)
                print(json.dumps(details.raw_data, indent=2))

        elif parsed_args.command == "breeds":
            groups = client.get_available_breed_groups()
            for group in groups:
                print(f"{group.id}: {group.name}")

        elif parsed_args.command == "find":
            results = client.search_animals(
                breed_id=parsed_args.breed_id,
                page=parsed_args.page,
                page_size=parsed_args.page_size,
            )
            print(f"Total results: {results.total_count}")
            print(f"Page {results.page + 1} ({len(results.results)} results):")
            for animal in results.results:
                print(f"  {animal.get('LpnId', 'N/A')}")

        return 0

    except NSIPError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
