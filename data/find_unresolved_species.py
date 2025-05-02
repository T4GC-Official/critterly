"""Find species in sanctuaries_data.json that don't resolve to a category.

Usage: 
    python3 find_unresolved_species.py --sanctuaries_path ./sanctuaries_data.json
"""
import json
import argparse

# Predefined animal buckets
animal_buckets = {
    "snake": ["indian rock python", "king cobra", "python", "cobra"],
    "gaur": ["indian gaur", "gaur"],
    "deer": ["sambar", "barking deer", "mouse deer"],
    "bear": ["sloth bear"],
    "vulture": ["indian vulture"],
    "squirrel": ["indian giant squirrel", "giant squirrel"],
    "leopard": ["leopard", "snow leopard", "clouded leopard"],
    "elephant": ["asian elephant"],
    "tiger": ["bengal tiger", "tiger"],
    "panda": ["red panda"],
    "gibbon": ["hoolock gibbon"],
    "langur": ["golden langur"],
    "parakeet": ["malabar parakeet"],
    "pigeon": ["nicobar pigeon", "green imperial pigeon"],
    "wild boar": ["wild boar"],
    "lion": ["lion"]
}

# Reverse mapping of species to final bucket
species_to_bucket = {}
for bucket, species_list in animal_buckets.items():
    for species in species_list:
        species_to_bucket[species.lower()] = bucket

# Function to find unresolved species
def find_unresolved_species(input_json_path):
    # Load sanctuary data
    with open(input_json_path, 'r') as file:
        sanctuaries_data = json.load(file)

    unresolved_species = set()

    # Iterate through the sanctuaries and species
    for sanctuary in sanctuaries_data['sanctuaries_data']:
        for species in sanctuary.get("species", []):
            species_lower = species.lower()
            if species_lower not in species_to_bucket:
                unresolved_species.add(species)
    
    return list(unresolved_species)

# Main function to parse command-line argument
def main():
    parser = argparse.ArgumentParser(description="Find unresolved species from a sanctuaries JSON file.")
    parser.add_argument("--sanctuaries_path", type=str, required=True, help="Path to the sanctuaries JSON file")

    args = parser.parse_args()

    # Run the unresolved species check
    unresolved = find_unresolved_species(args.sanctuaries_path)
    if unresolved:
        print("Unresolved species (not in any predefined bucket):")
        for species in unresolved:
            print(species)
    else:
        print("All species are resolved into predefined buckets.")

if __name__ == "__main__":
    main()
