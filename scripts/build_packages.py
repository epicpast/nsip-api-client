#!/usr/bin/env python3
"""Build wheel and sdist for each package.

Usage:
    python scripts/build_packages.py
    python scripts/build_packages.py --client-only
    python scripts/build_packages.py --server-only

Builds are created in the packaging/<package>/dist/ directories
and copied to the root dist/ directory.
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

# Project root (parent of scripts/)
PROJECT_ROOT = Path(__file__).parent.parent
DIST_DIR = PROJECT_ROOT / "dist"

PACKAGES = {
    "client": PROJECT_ROOT / "packaging" / "nsip-client",
    "server": PROJECT_ROOT / "packaging" / "nsip-mcp-server",
}


def build_package(name: str, package_dir: Path) -> bool:
    """Build a single package."""
    print(f"\n{'='*60}")
    print(f"Building {name}...")
    print(f"{'='*60}")

    # Clean any existing dist in package dir
    pkg_dist = package_dir / "dist"
    if pkg_dist.exists():
        shutil.rmtree(pkg_dist)

    # Build using python -m build
    result = subprocess.run(
        [sys.executable, "-m", "build"],
        cwd=package_dir,
        capture_output=False,
    )

    if result.returncode != 0:
        print(f"ERROR: Failed to build {name}")
        return False

    # Copy artifacts to root dist/
    if pkg_dist.exists():
        for artifact in pkg_dist.iterdir():
            dest = DIST_DIR / artifact.name
            shutil.copy2(artifact, dest)
            print(f"  -> {dest.name}")

    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Build package distributions")
    parser.add_argument(
        "--client-only",
        action="store_true",
        help="Only build nsip-client",
    )
    parser.add_argument(
        "--server-only",
        action="store_true",
        help="Only build nsip-mcp-server",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean dist/ before building",
    )
    args = parser.parse_args()

    # Determine which packages to build
    if args.client_only:
        packages = {"client": PACKAGES["client"]}
    elif args.server_only:
        packages = {"server": PACKAGES["server"]}
    else:
        packages = PACKAGES

    # Clean dist directory
    if args.clean and DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
        print(f"Cleaned {DIST_DIR}")

    # Create dist directory
    DIST_DIR.mkdir(exist_ok=True)

    # Build each package
    success = True
    for name, package_dir in packages.items():
        if not build_package(name, package_dir):
            success = False

    # Summary
    print(f"\n{'='*60}")
    if success:
        print("BUILD SUCCESSFUL")
        print(f"\nArtifacts in {DIST_DIR}:")
        for artifact in sorted(DIST_DIR.iterdir()):
            size = artifact.stat().st_size
            print(f"  {artifact.name} ({size:,} bytes)")
    else:
        print("BUILD FAILED")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
