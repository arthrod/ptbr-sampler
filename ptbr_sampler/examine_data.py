import json

# Load the files
with open('ptbr_sampler/data/locations_data_normalized.json', encoding='utf-8') as f:
    normalized_data = json.load(f)

with open('ptbr_sampler/data/cities_with_ceps.json', encoding='utf-8') as f:
    ceps_data = json.load(f)

# Print the top-level keys in each file
print('Top-level keys in normalized_data:', list(normalized_data.keys()))
print('Top-level keys in ceps_data:', list(ceps_data.keys()))

# Check if 'cities' exists in both
if 'cities' in normalized_data and 'cities' in ceps_data:
    print("\nBoth files have a 'cities' key")
    print(f'Number of cities in normalized data: {len(normalized_data["cities"])}')
    print(f'Number of cities in ceps data: {len(ceps_data["cities"])}')

    # Sample a few cities from normalized data
    print('\nSample cities from normalized data:')
    for i, (city_name, city_data) in enumerate(list(normalized_data['cities'].items())[:5]):
        print(f'{city_name} ({city_data.get("city_uf", "no UF")})')

    # Sample a few cities from ceps data
    print('\nSample cities from ceps data:')
    for i, (city_name, city_data) in enumerate(list(ceps_data['cities'].items())[:5]):
        print(f'{city_name} ({city_data.get("city_uf", "no UF")})')

    # Let's see if one city doesn't match directly
    print("\nTrying to match 'Acrelândia' from normalized data:")
    found = False
    for city_name, city_data in ceps_data['cities'].items():
        if city_name == 'Acrelândia' and city_data.get('city_uf') == 'AC':
            print(f'Found match: {city_name}')
            found = True
            break
    if not found:
        print("No match found for 'Acrelândia'")
else:
    print('\nThe structure of the files is different')
    if 'cities' in normalized_data:
        print("normalized_data has a 'cities' key")
    if 'cities' in ceps_data:
        print("ceps_data has a 'cities' key")

    # If cities_with_ceps.json doesn't have a 'cities' key, examine its structure
    if 'cities' not in ceps_data:
        print('\nExamining cities_with_ceps.json structure:')
        if len(ceps_data) > 0:
            print(f'Number of top-level keys: {len(ceps_data)}')
            print('Sample keys:', list(ceps_data.keys())[:5])

            # Check the first item to see its structure
            first_key = list(ceps_data.keys())[0]
            print(f"\nStructure of first item '{first_key}':")
            print(json.dumps(ceps_data[first_key], indent=2, ensure_ascii=False)[:500] + '...')

# Check if cities are formatted differently (e.g., case, accents)
print('\nLooking for possible format differences:')
normalized_first_city = list(normalized_data['cities'].keys())[0]
for city_key, city_data in list(ceps_data.items())[:100]:
    city_name = city_data.get('city_name', '')
    if normalized_first_city.lower() in city_name.lower() or city_name.lower() in normalized_first_city.lower():
        print(f"Possible match: '{normalized_first_city}' and '{city_name}' ({city_data.get('city_uf', 'no UF')})")
