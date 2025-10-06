#!/usr/bin/env python3
"""
Basic usage examples for the NSIP API Client
"""

from nsip_client import NSIPClient


def main():
    """Demonstrate basic API usage"""

    # Initialize the client
    client = NSIPClient()

    print("=" * 70)
    print("NSIP API Client - Basic Usage Examples")
    print("=" * 70)
    print()

    # Example 1: Get database update date
    print("1. Database Last Updated:")
    print("-" * 70)
    update_info = client.get_date_last_updated()
    print(f"   Last update: {update_info}")
    print()

    # Example 2: List breed groups
    print("2. Available Breed Groups:")
    print("-" * 70)
    breed_groups = client.get_available_breed_groups()
    for group in breed_groups:
        print(f"   {group.id:2d} - {group.name}")
    print()

    # Example 3: Get animal details
    print("3. Animal Details:")
    print("-" * 70)
    lpn_id = "6401492020FLE249"
    animal = client.get_animal_details(lpn_id)
    print(f"   LPN ID: {animal.lpn_id}")
    print(f"   Breed: {animal.breed} ({animal.breed_group})")
    print(f"   DOB: {animal.date_of_birth}")
    print(f"   Gender: {animal.gender}")
    print(f"   Status: {animal.status}")
    print(f"   Sire: {animal.sire}")
    print(f"   Dam: {animal.dam}")
    print(f"   Total Progeny: {animal.total_progeny}")
    print()

    # Example 4: Display traits
    print("4. Animal Traits (EBVs):")
    print("-" * 70)
    print(f"   {'Trait':<15} {'Value':>10} {'Accuracy':>10}")
    print("   " + "-" * 40)
    for trait_name, trait in animal.traits.items():
        acc = f"{trait.accuracy}%" if trait.accuracy else "N/A"
        print(f"   {trait_name:<15} {trait.value:>10.3f} {acc:>10}")
    print()

    # Example 5: Get progeny
    print("5. Progeny Information:")
    print("-" * 70)
    progeny = client.get_progeny(lpn_id)
    print(f"   Total Progeny: {progeny.total_count}")
    print(f"   Showing: {len(progeny.animals)} animals")
    print()
    for offspring in progeny.animals[:5]:  # Show first 5
        print(f"   - {offspring.lpn_id} ({offspring.sex}) - DOB: {offspring.date_of_birth}")
    if len(progeny.animals) > 5:
        print(f"   ... and {len(progeny.animals) - 5} more")
    print()

    # Example 6: Contact information
    print("6. Contact Information:")
    print("-" * 70)
    if animal.contact_info:
        print(f"   Farm: {animal.contact_info.farm_name}")
        print(f"   Contact: {animal.contact_info.contact_name}")
        print(f"   Phone: {animal.contact_info.phone}")
        print(f"   Email: {animal.contact_info.email}")
    else:
        print("   No contact information available")
    print()

    # Example 7: Search for animals
    print("7. Search for Animals (Breed ID 486):")
    print("-" * 70)
    results = client.search_animals(breed_id=486, page_size=5)
    print(f"   Total animals found: {results.total_count}")
    print(f"   Showing page {results.page + 1} ({len(results.results)} results):")
    for result in results.results:
        print(f"   - {result.get('LpnId', 'N/A')}")
    print()

    # Example 8: Get trait ranges for a breed
    print("8. Trait Ranges for Breed 486:")
    print("-" * 70)
    ranges = client.get_trait_ranges_by_breed(486)
    print(f"   Available trait ranges: {len(ranges)} traits")
    # Display first few
    for trait_name, trait_range in list(ranges.items())[:3]:
        if isinstance(trait_range, dict):
            min_val = trait_range.get("min", "N/A")
            max_val = trait_range.get("max", "N/A")
            print(f"   {trait_name}: {min_val} to {max_val}")
    print()

    print("=" * 70)
    print("Examples completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
