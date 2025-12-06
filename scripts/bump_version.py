#!/usr/bin/env python3
"""Bump version for specified package(s) following semver.

Usage:
    python scripts/bump_version.py --package client --bump patch
    python scripts/bump_version.py --package server --bump patch
    python scripts/bump_version.py --package skills --bump patch
    python scripts/bump_version.py --package all --bump minor

For minor/major bumps, all packages are aligned to the same version.
For patch bumps, only the specified package is incremented.
"""

import argparse
import re
import sys
from pathlib import Path

# Project root (parent of scripts/)
PROJECT_ROOT = Path(__file__).parent.parent

# Package paths
CLIENT_INIT = PROJECT_ROOT / "src" / "nsip_client" / "__init__.py"
SERVER_INIT = PROJECT_ROOT / "src" / "nsip_mcp" / "__init__.py"
SKILLS_INIT = PROJECT_ROOT / "src" / "nsip_skills" / "__init__.py"
SERVER_PYPROJECT = PROJECT_ROOT / "packaging" / "nsip-mcp-server" / "pyproject.toml"
SKILLS_PYPROJECT = PROJECT_ROOT / "packaging" / "nsip-skills" / "pyproject.toml"

VERSION_PATTERN = re.compile(r'^__version__\s*=\s*["\'](\d+\.\d+\.\d+)["\']', re.MULTILINE)
# Match dependency format: "nsip-client>=1.3.0,<2.0.0"
DEPENDENCY_PATTERN = re.compile(r'("nsip-client>=)(\d+\.\d+\.\d+)(,<\d+\.\d+\.\d+")')


def read_version(init_path: Path) -> tuple[int, int, int]:
    """Read version from __init__.py file."""
    content = init_path.read_text()
    match = VERSION_PATTERN.search(content)
    if not match:
        raise ValueError(f"Could not find __version__ in {init_path}")
    parts = match.group(1).split(".")
    return int(parts[0]), int(parts[1]), int(parts[2])


def write_version(init_path: Path, major: int, minor: int, patch: int) -> None:
    """Write version to __init__.py file."""
    content = init_path.read_text()
    new_version = f'{major}.{minor}.{patch}'
    new_content = VERSION_PATTERN.sub(f'__version__ = "{new_version}"', content)
    init_path.write_text(new_content)
    print(f"Updated {init_path.name}: {new_version}")


def update_dependency(pyproject_path: Path, major: int, minor: int, patch: int) -> None:
    """Update nsip-client dependency pin in pyproject.toml."""
    content = pyproject_path.read_text()
    new_version = f"{major}.{minor}.{patch}"
    new_content = DEPENDENCY_PATTERN.sub(rf'\g<1>{new_version}\g<3>', content)
    if content != new_content:
        pyproject_path.write_text(new_content)
        print(f"Updated {pyproject_path.parent.name} dependency: nsip-client>={new_version}")


def bump_version(
    version: tuple[int, int, int], bump_type: str
) -> tuple[int, int, int]:
    """Increment version based on bump type."""
    major, minor, patch = version
    if bump_type == "major":
        return major + 1, 0, 0
    elif bump_type == "minor":
        return major, minor + 1, 0
    else:  # patch
        return major, minor, patch + 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Bump package version(s)")
    parser.add_argument(
        "--package",
        choices=["client", "server", "skills", "all"],
        required=True,
        help="Which package(s) to bump",
    )
    parser.add_argument(
        "--bump",
        choices=["patch", "minor", "major"],
        default="patch",
        help="Version component to bump (default: patch)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without making changes",
    )
    args = parser.parse_args()

    # For minor/major bumps, always bump all packages
    if args.bump in ("minor", "major") and args.package != "all":
        print(f"Note: {args.bump} bump requires aligning all packages")
        args.package = "all"

    # Read current versions
    client_version = read_version(CLIENT_INIT)
    server_version = read_version(SERVER_INIT)
    skills_version = read_version(SKILLS_INIT)

    print(f"Current client version: {'.'.join(map(str, client_version))}")
    print(f"Current server version: {'.'.join(map(str, server_version))}")
    print(f"Current skills version: {'.'.join(map(str, skills_version))}")

    # Calculate new versions
    if args.package == "client":
        new_client = bump_version(client_version, args.bump)
        new_server = server_version
        new_skills = skills_version
    elif args.package == "server":
        new_client = client_version
        new_server = bump_version(server_version, args.bump)
        new_skills = skills_version
    elif args.package == "skills":
        new_client = client_version
        new_server = server_version
        new_skills = bump_version(skills_version, args.bump)
    else:  # all
        # For aligned bumps, use the highest version as base
        base = max(client_version, server_version, skills_version)
        new_version = bump_version(base, args.bump)
        new_client = new_version
        new_server = new_version
        new_skills = new_version

    print(f"\nNew client version: {'.'.join(map(str, new_client))}")
    print(f"New server version: {'.'.join(map(str, new_server))}")
    print(f"New skills version: {'.'.join(map(str, new_skills))}")

    if args.dry_run:
        print("\n[DRY RUN] No changes made")
        return 0

    # Apply changes
    if new_client != client_version:
        write_version(CLIENT_INIT, *new_client)

    if new_server != server_version:
        write_version(SERVER_INIT, *new_server)

    if new_skills != skills_version:
        write_version(SKILLS_INIT, *new_skills)

    # Update dependencies on client if client version changed
    if new_client != client_version or args.bump in ("minor", "major"):
        update_dependency(SERVER_PYPROJECT, *new_client)
        update_dependency(SKILLS_PYPROJECT, *new_client)

    print("\nVersion bump complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
