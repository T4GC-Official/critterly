import pandas as pd
import json
import argparse
import re
import numpy as np

# Helper function to split and clean species names
def split_species(species_str):
    if pd.isna(species_str):
        return []
    return [species.strip().lower() for species in re.split(r',|\band\b', species_str) if species.strip()]

# Helper function to safely strip strings and handle non-strings
def safe_strip(value):
    return str(value).strip() if pd.notna(value) else ""

# Main function to convert Excel to JSON with species and NGO autocomplete
def excel_to_json_with_autocomplete(sanctuaries_path, output_path):
    # Load the Excel file
    df = pd.read_excel(sanctuaries_path, sheet_name='Sheet1')

    # Clean up the data
    # 1. Replace NaN values with None (which becomes null in JSON)
    # 2. Drop empty rows
    df = df.replace({np.nan: None})
    df_cleaned = df.dropna(how='all').reset_index(drop=True)

    # Initialize dictionaries to hold unique species and NGOs, and their respective sanctuary mappings
    species_dict = {}
    ngo_dict = {}
    state_dict = {}

    # Create a list to hold the sanitized data
    sanitized_data = []

    # Iterate over the dataframe and process each row
    for index, row in df_cleaned.iterrows():
        # Sanitize species data
        species_list = split_species(row.get("Species Present", ""))
        for species in species_list:
            species_dict.setdefault(species, []).append(safe_strip(row.get("Sanctuary", "")))

        # Process NGO data and website
        ngos = row.get("NGO", "").split(",") if pd.notna(row.get("NGO")) else []
        ngo_websites = row.get("NGO Website", "").split(",") if pd.notna(row.get("NGO Website")) else []
        ngo_dict_cleaned = {ngo.strip(): ngo_websites[i].strip() if i < len(ngo_websites) else "" for i, ngo in enumerate(ngos)}

        # Map NGOs to sanctuaries
        for ngo in ngo_dict_cleaned.keys():
            ngo_dict.setdefault(ngo, []).append(safe_strip(row.get("Sanctuary", "")))

        # Process states
        state = safe_strip(row.get("State", ""))
        sanctuary = safe_strip(row.get("Sanctuary", ""))
        if state: 
            state_dict.setdefault(state, []).append(sanctuary)

        # Process websites, splitting on commas and stripping whitespace
        websites_list = [website.strip() for website in safe_strip(row.get("Websites", "")).split(",") if website.strip()]

        # Process safari availability
        safari_value = safe_strip(row.get("Safari Available or not", "")).lower() == 'yes'

        # Create the sanitized entry
        sanitized_entry = {
            "sanctuary": safe_strip(row.get("Sanctuary", "")),
            "area": row.get("Area (sq. Km.)", None),
            "species": species_list,
            "state": state,
            "district": safe_strip(row.get("District", "")),
            "population": row.get("Population Near By (approx.)", None),
            "safari": safari_value,
            "websites": websites_list,
            "ngo": ngo_dict_cleaned
        }

        # Append the sanitized entry to the list
        sanitized_data.append(sanitized_entry)

    # Prepare the final JSON structure
    final_output = {
        "sanctuaries_data": sanitized_data,
        "autocomplete_species": species_dict,
        "autocomplete_ngo": ngo_dict,
        "autocomplete_states": state_dict
    }

    # Write the JSON data to the output path
    with open(output_path, 'w') as json_file:
        json.dump(final_output, json_file, indent=4)

# Argument parsing and main function
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert Excel to JSON with species and NGO autocomplete')
    parser.add_argument('--sanctuaries_path', type=str, required=True, help='Path to the sanctuaries Excel file')
    parser.add_argument('--output_path', type=str, required=True, help='Path for the output JSON file')
    args = parser.parse_args()

    # Run the conversion function
    excel_to_json_with_autocomplete(args.sanctuaries_path, args.output_path)

