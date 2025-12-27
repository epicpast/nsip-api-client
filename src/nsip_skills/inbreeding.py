"""
Inbreeding coefficient calculation module.

Calculate pedigree-based inbreeding coefficients using Wright's path method.
"""

from __future__ import annotations

import logging
from collections import Counter
from dataclasses import dataclass
from typing import Any

from nsip_skills.common.data_models import (
    InbreedingResult,
    PedigreeNode,
    PedigreeTree,
    RiskLevel,
)
from nsip_skills.common.formatters import format_inbreeding_result
from nsip_skills.common.nsip_wrapper import CachedNSIPClient

logger = logging.getLogger(__name__)

# Alias for backwards compatibility with test API
format_inbreeding_report = format_inbreeding_result


@dataclass
class AncestorPath:
    """A path through the pedigree to a common ancestor."""

    ancestor_lpn: str
    sire_path_length: int  # Steps from subject to ancestor via sire
    dam_path_length: int  # Steps from subject to ancestor via dam
    ancestor_inbreeding: float  # FA - inbreeding coefficient of the ancestor

    @property
    def contribution(self) -> float:
        """Calculate this path's contribution to inbreeding coefficient."""
        # Wright's formula: (1/2)^(n1+n2+1) × (1 + FA)
        exponent = self.sire_path_length + self.dam_path_length + 1
        return (0.5**exponent) * (1 + self.ancestor_inbreeding)


def build_pedigree_tree(
    lpn_id: str,
    generations: int = 4,
    client: CachedNSIPClient | None = None,
) -> PedigreeTree:
    """
    Build a pedigree tree by recursively fetching lineage.

    Args:
        lpn_id: The subject animal's LPN ID
        generations: Number of generations to trace (default: 4)
        client: Optional pre-configured client

    Returns:
        PedigreeTree with ancestors up to specified generations
    """
    should_close = client is None
    if client is None:
        client = CachedNSIPClient()

    try:
        # Fetch initial lineage
        lineage = client.get_lineage(lpn_id)

        # Build subject node
        subject_node = PedigreeNode(
            lpn_id=lpn_id,
            generation=0,
        )
        if lineage.subject:
            subject_node.name = lineage.subject.lpn_id
            subject_node.gender = lineage.subject.sex
            subject_node.date_of_birth = lineage.subject.date_of_birth
            subject_node.status = lineage.subject.status
            subject_node.farm_name = lineage.subject.farm_name
            subject_node.us_index = lineage.subject.us_index

        tree = PedigreeTree(
            subject=subject_node,
            max_generations=generations,
        )

        # Build parent nodes
        if lineage.sire:
            tree.sire = PedigreeNode(
                lpn_id=lineage.sire.lpn_id,
                gender="Male",
                date_of_birth=lineage.sire.date_of_birth,
                status=lineage.sire.status,
                farm_name=lineage.sire.farm_name,
                us_index=lineage.sire.us_index,
                generation=1,
            )

        if lineage.dam:
            tree.dam = PedigreeNode(
                lpn_id=lineage.dam.lpn_id,
                gender="Female",
                date_of_birth=lineage.dam.date_of_birth,
                status=lineage.dam.status,
                farm_name=lineage.dam.farm_name,
                us_index=lineage.dam.us_index,
                generation=1,
            )

        # Recursively fetch grandparents and beyond if generations > 1
        if generations > 1:
            _fetch_ancestors_recursive(tree, client, generations)

        # Identify common ancestors
        tree.common_ancestors = find_common_ancestors(tree)

        return tree

    finally:
        if should_close and client:
            client.close()


def _store_ancestor_node(tree: PedigreeTree, path: str, node: PedigreeNode) -> None:
    """Store an ancestor node at the appropriate tree location."""
    grandparent_paths = {"ss": "sire_sire", "sd": "sire_dam", "ds": "dam_sire", "dd": "dam_dam"}
    if path in grandparent_paths:
        setattr(tree, grandparent_paths[path], node)
    else:
        tree.extended[path] = node


def _create_ancestor_node(lineage_animal: Any, gender: str, generation: int) -> PedigreeNode | None:
    """Create a PedigreeNode from a lineage animal."""
    if not lineage_animal:
        return None
    return PedigreeNode(
        lpn_id=lineage_animal.lpn_id,
        gender=gender,
        date_of_birth=lineage_animal.date_of_birth,
        status=lineage_animal.status,
        farm_name=lineage_animal.farm_name,
        us_index=lineage_animal.us_index,
        generation=generation,
    )


def _fetch_ancestors_recursive(
    tree: PedigreeTree,
    client: CachedNSIPClient,
    max_gen: int,
    current_path: str = "",
    current_gen: int = 1,
) -> None:
    """Recursively fetch ancestors and add to tree."""
    if current_gen >= max_gen:
        return

    nodes_to_expand = _get_nodes_to_expand(tree, current_path)

    for path, parent_node in nodes_to_expand:
        _expand_parent_node(tree, client, max_gen, path, parent_node, current_gen)


def _get_nodes_to_expand(tree: PedigreeTree, current_path: str) -> list[tuple[str, PedigreeNode]]:
    """Get list of parent nodes to expand."""
    if current_path == "":
        nodes = []
        if tree.sire:
            nodes.append(("s", tree.sire))
        if tree.dam:
            nodes.append(("d", tree.dam))
        return nodes
    node = tree.get_ancestor(current_path)
    return [(current_path, node)] if node else []


def _expand_parent_node(
    tree: PedigreeTree,
    client: CachedNSIPClient,
    max_gen: int,
    path: str,
    parent_node: PedigreeNode,
    current_gen: int,
) -> None:
    """Expand a single parent node by fetching its ancestors."""
    try:
        lineage = client.get_lineage(parent_node.lpn_id)
        next_gen = current_gen + 1

        # Add sire of this parent
        sire_node = _create_ancestor_node(lineage.sire, "Male", next_gen)
        if sire_node:
            sire_path = path + "s"
            _store_ancestor_node(tree, sire_path, sire_node)
            if next_gen < max_gen:
                _fetch_ancestors_recursive(tree, client, max_gen, sire_path, next_gen)

        # Add dam of this parent
        dam_node = _create_ancestor_node(lineage.dam, "Female", next_gen)
        if dam_node:
            dam_path = path + "d"
            _store_ancestor_node(tree, dam_path, dam_node)
            if next_gen < max_gen:
                _fetch_ancestors_recursive(tree, client, max_gen, dam_path, next_gen)

    except Exception as e:
        # Log warning for silent failures instead of silently ignoring
        logger.debug(f"Could not fetch lineage for {parent_node.lpn_id}: {e}")


def find_common_ancestors(tree: PedigreeTree) -> list[str]:
    """Find ancestors that appear multiple times in the pedigree.

    Uses Counter for O(n) duplicate detection instead of O(n²) nested loops.
    """
    # Count occurrences of each ancestor LPN ID in O(n)
    ancestor_counts = Counter(ancestor.lpn_id for ancestor in tree.all_ancestors())

    # Return those appearing more than once, preserving insertion order
    return [lpn_id for lpn_id, count in ancestor_counts.items() if count > 1]


def trace_paths_to_ancestor(
    tree: PedigreeTree,
    ancestor_lpn: str,
    side: str,  # "s"/"sire" for sire side, "d"/"dam" for dam side
) -> list[int]:
    """Find all path lengths from subject to ancestor on one side."""
    # Normalize side parameter to short form
    if side.lower() in ("sire", "s"):
        side = "s"
    elif side.lower() in ("dam", "d"):
        side = "d"
    else:
        raise ValueError(f"Invalid side '{side}', expected 'sire'/'s' or 'dam'/'d'")

    paths = []

    def search(path: str, depth: int):
        node = tree.get_ancestor(path)
        if node is None:
            return
        if node.lpn_id == ancestor_lpn:
            paths.append(depth)
            return
        # Continue searching both branches
        search(path + "s", depth + 1)
        search(path + "d", depth + 1)

    search(side, 1)
    return paths


def calculate_path_contribution(
    path_length_sire: int,
    path_length_dam: int,
    ancestor_inbreeding: float = 0.0,
) -> float:
    """
    Calculate a single path's contribution to inbreeding coefficient.

    Uses Wright's formula: (1/2)^(n1+n2+1) × (1 + FA)

    Args:
        path_length_sire: Steps from subject to ancestor via sire
        path_length_dam: Steps from subject to ancestor via dam
        ancestor_inbreeding: Inbreeding coefficient of the ancestor (FA)

    Returns:
        Path contribution to inbreeding coefficient
    """
    exponent = path_length_sire + path_length_dam + 1
    return (0.5**exponent) * (1 + ancestor_inbreeding)


def calculate_inbreeding(
    lpn_id: str,
    generations: int = 4,
    client: CachedNSIPClient | None = None,
) -> InbreedingResult:
    """
    Calculate inbreeding coefficient for an animal.

    Uses Wright's path coefficient method:
    F = Σ[(1/2)^(n1+n2+1) × (1 + FA)]

    Where:
    - n1 = path length from subject to common ancestor via sire
    - n2 = path length from subject to common ancestor via dam
    - FA = inbreeding coefficient of the common ancestor

    Args:
        lpn_id: Animal's LPN ID
        generations: Generations to analyze (default: 4)
        client: Optional pre-configured client

    Returns:
        InbreedingResult with coefficient and risk level
    """
    should_close = client is None
    if client is None:
        client = CachedNSIPClient()

    try:
        # Build pedigree tree
        tree = build_pedigree_tree(lpn_id, generations=generations, client=client)

        # Find common ancestors and calculate contributions
        paths: list[AncestorPath] = []
        common_ancestors: list[dict[str, Any]] = []

        # Cache path results to avoid redundant tree traversals
        # This memoization reduces path lookups from O(2*ancestors) to O(ancestors)
        path_cache: dict[tuple[str, str], list[int]] = {}

        def get_paths(ancestor: str, side: str) -> list[int]:
            key = (ancestor, side)
            if key not in path_cache:
                path_cache[key] = trace_paths_to_ancestor(tree, ancestor, side)
            return path_cache[key]

        for ancestor_lpn in tree.common_ancestors:
            # Find paths to this ancestor from each side (with caching)
            sire_paths = get_paths(ancestor_lpn, "s")
            dam_paths = get_paths(ancestor_lpn, "d")

            if sire_paths and dam_paths:
                # For simplicity, assume ancestor's inbreeding is 0
                # (would need deeper pedigree analysis for true FA)
                fa = 0.0

                # Calculate contribution inline to avoid O(n²) filtering later
                ancestor_contribution = 0.0
                for n1 in sire_paths:
                    for n2 in dam_paths:
                        path = AncestorPath(
                            ancestor_lpn=ancestor_lpn,
                            sire_path_length=n1,
                            dam_path_length=n2,
                            ancestor_inbreeding=fa,
                        )
                        paths.append(path)
                        ancestor_contribution += path.contribution

                common_ancestors.append(
                    {
                        "lpn_id": ancestor_lpn,
                        "contribution": ancestor_contribution * 100,  # As percentage
                        "path_count": len(sire_paths) * len(dam_paths),
                    }
                )

        # Sum all path contributions
        coefficient = sum(p.contribution for p in paths)

        return InbreedingResult(
            lpn_id=lpn_id,
            coefficient=coefficient,
            risk_level=RiskLevel.from_coefficient(coefficient),
            common_ancestors=[ca["lpn_id"] for ca in common_ancestors],
            paths=[
                {
                    "ancestor": p.ancestor_lpn,
                    "sire_path": p.sire_path_length,
                    "dam_path": p.dam_path_length,
                    "contribution": p.contribution * 100,
                }
                for p in paths
            ],
            generations_analyzed=generations,
            pedigree=tree,
        )

    finally:
        if should_close and client:
            client.close()


def calculate_projected_offspring_inbreeding(
    sire_lpn: str,
    dam_lpn: str,
    generations: int = 4,
    client: CachedNSIPClient | None = None,
    lineage_cache: dict[str, Any] | None = None,
) -> InbreedingResult:
    """
    Calculate projected inbreeding coefficient for offspring of a mating.

    This creates a virtual pedigree combining sire and dam lineages
    and calculates what the offspring's inbreeding would be.

    Args:
        sire_lpn: Sire's LPN ID
        dam_lpn: Dam's LPN ID
        generations: Generations to analyze
        client: Optional pre-configured client
        lineage_cache: Optional pre-fetched lineage data to avoid N+1 queries.
                       If provided, reduces API calls significantly when called
                       in a loop (e.g., for mating optimization).

    Returns:
        InbreedingResult with projected coefficient
    """
    should_close = client is None
    if client is None:
        client = CachedNSIPClient()

    try:
        # Build pedigree trees for both parents.
        # The lineage_cache parameter is kept for API compatibility but caching now
        # happens at the CachedNSIPClient level. Pre-fetching lineages upstream
        # (e.g., in mating_optimizer) populates the client's internal cache,
        # which build_pedigree_tree will use automatically.
        _ = lineage_cache  # Acknowledge parameter for documentation/compatibility
        sire_tree = build_pedigree_tree(sire_lpn, generations=generations - 1, client=client)
        dam_tree = build_pedigree_tree(dam_lpn, generations=generations - 1, client=client)

        # Collect all ancestors from both trees
        sire_ancestors = {a.lpn_id: a for a in sire_tree.all_ancestors()}
        dam_ancestors = {a.lpn_id: a for a in dam_tree.all_ancestors()}

        # Include the parents themselves
        sire_ancestors[sire_lpn] = sire_tree.subject
        dam_ancestors[dam_lpn] = dam_tree.subject

        # Find common ancestors between the two lineages
        common = set(sire_ancestors.keys()) & set(dam_ancestors.keys())

        paths: list[AncestorPath] = []
        common_ancestors: list[str] = []

        for ancestor_lpn in common:
            # Path through sire = 1 + path in sire's tree to ancestor
            # Path through dam = 1 + path in dam's tree to ancestor
            sire_gen = sire_ancestors[ancestor_lpn].generation + 1
            dam_gen = dam_ancestors[ancestor_lpn].generation + 1

            path = AncestorPath(
                ancestor_lpn=ancestor_lpn,
                sire_path_length=sire_gen,
                dam_path_length=dam_gen,
                ancestor_inbreeding=0.0,
            )
            paths.append(path)

            common_ancestors.append(ancestor_lpn)

        coefficient = sum(p.contribution for p in paths)

        return InbreedingResult(
            lpn_id=f"{sire_lpn} x {dam_lpn} (projected)",
            coefficient=coefficient,
            risk_level=RiskLevel.from_coefficient(coefficient),
            common_ancestors=common_ancestors,
            paths=[
                {
                    "ancestor": p.ancestor_lpn,
                    "sire_path": p.sire_path_length,
                    "dam_path": p.dam_path_length,
                    "contribution": p.contribution * 100,
                }
                for p in paths
            ],
            generations_analyzed=generations,
        )

    finally:
        if should_close and client:
            client.close()


def main():
    """Command-line interface for inbreeding calculation."""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Calculate inbreeding coefficients")
    parser.add_argument("lpn_id", help="Animal LPN ID")
    parser.add_argument("--generations", "-g", type=int, default=4, help="Generations to trace")
    parser.add_argument("--mating", "-m", help="Dam LPN ID for projected offspring calculation")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if args.mating:
        result = calculate_projected_offspring_inbreeding(
            sire_lpn=args.lpn_id,
            dam_lpn=args.mating,
            generations=args.generations,
        )
    else:
        result = calculate_inbreeding(
            lpn_id=args.lpn_id,
            generations=args.generations,
        )

    if args.json:
        print(json.dumps(result.to_dict(), indent=2, default=str))
    else:
        print(format_inbreeding_result(result))

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
