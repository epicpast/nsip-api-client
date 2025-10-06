#!/usr/bin/env python3
"""
Advanced search examples using the NSIP API Client
"""

from nsip_client import NSIPClient, SearchCriteria


def search_by_criteria():
    """Example: Search with multiple criteria"""
    client = NSIPClient()

    print("Advanced Search Example")
    print("=" * 70)
    print()

    # Create search criteria
    criteria = SearchCriteria(
        breed_id=486,
        gender="Female",
        status="CURRENT",
        born_after="2020-01-01",
        born_before="2020-12-31",
    )

    print("Search Criteria:")
    print(f"  Breed ID: {criteria.breed_id}")
    print(f"  Gender: {criteria.gender}")
    print(f"  Status: {criteria.status}")
    print(f"  Born After: {criteria.born_after}")
    print(f"  Born Before: {criteria.born_before}")
    print()

    # Perform search
    results = client.search_animals(
        breed_id=criteria.breed_id, search_criteria=criteria, page_size=10
    )

    print(f"Results: Found {results.total_count} animals")
    print()

    for i, animal in enumerate(results.results, 1):
        print(f"{i}. {animal.get('LpnId', 'N/A')}")


def paginate_results():
    """Example: Paginate through search results"""
    client = NSIPClient()

    print("\nPagination Example")
    print("=" * 70)
    print()

    breed_id = 486
    page_size = 15
    max_pages = 3  # Limit for demo

    for page in range(max_pages):
        results = client.search_animals(breed_id=breed_id, page=page, page_size=page_size)

        print(f"Page {page + 1}/{(results.total_count + page_size - 1) // page_size}")
        print(f"Showing {len(results.results)} of {results.total_count} total")
        print()

        for animal in results.results[:3]:  # Show first 3 per page
            print(f"  - {animal.get('LpnId', 'N/A')}")

        if len(results.results) > 3:
            print(f"  ... and {len(results.results) - 3} more on this page")
        print()


def get_complete_family_tree():
    """Example: Get complete animal profile with family tree"""
    client = NSIPClient()

    print("Complete Family Profile Example")
    print("=" * 70)
    print()

    lpn_id = "6401492020FLE249"

    # Get all information
    profile = client.search_by_lpn(lpn_id)

    # Display details
    details = profile["details"]
    print(f"Animal: {details.lpn_id}")
    print(f"Breed: {details.breed}")
    print()

    # Display pedigree
    print("Pedigree:")
    print(f"  Sire: {details.sire or 'Unknown'}")
    print(f"  Dam: {details.dam or 'Unknown'}")
    print()

    # Display progeny
    progeny = profile["progeny"]
    print(f"Progeny: {progeny.total_count} offspring")
    for offspring in progeny.animals[:5]:
        print(f"  - {offspring.lpn_id} ({offspring.sex})")
    print()

    # Display top traits
    print("Top Traits:")
    sorted_traits = sorted(details.traits.items(), key=lambda x: abs(x[1].value), reverse=True)[:5]
    for trait_name, trait in sorted_traits:
        print(f"  {trait_name}: {trait.value:.3f} ({trait.accuracy}% accuracy)")


def search_high_performers():
    """Example: Find high-performing animals"""
    client = NSIPClient()

    print("\nHigh Performers Search Example")
    print("=" * 70)
    print()

    # Search for animals and filter for high index values
    results = client.search_animals(breed_id=486, page_size=50)

    print(f"Analyzing {len(results.results)} animals...")
    print()

    # Note: You would need to get details for each to filter by specific traits
    # This is a simplified example
    print("Top 5 animals by LPN ID (detailed analysis would require fetching each):")
    for i, animal in enumerate(results.results[:5], 1):
        print(f"{i}. {animal.get('LpnId', 'N/A')}")


def compare_animals():
    """Example: Compare two animals"""
    client = NSIPClient()

    print("\nAnimal Comparison Example")
    print("=" * 70)
    print()

    lpn_ids = ["6401492020FLE249", "6401492019FLE124"]
    animals = [client.get_animal_details(lpn) for lpn in lpn_ids]

    print(f"{'Trait':<15} {animals[0].lpn_id:>20} {animals[1].lpn_id:>20}")
    print("-" * 60)

    # Find common traits
    common_traits = set(animals[0].traits.keys()) & set(animals[1].traits.keys())

    for trait_name in sorted(common_traits):
        val1 = animals[0].traits[trait_name].value
        val2 = animals[1].traits[trait_name].value
        print(f"{trait_name:<15} {val1:>20.3f} {val2:>20.3f}")


def main():
    """Run all examples"""
    try:
        search_by_criteria()
        print("\n" * 2)

        paginate_results()
        print("\n" * 2)

        get_complete_family_tree()
        print("\n" * 2)

        search_high_performers()
        print("\n" * 2)

        compare_animals()

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
