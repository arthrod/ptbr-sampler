import json

# Define file paths
normalized_file = 'ptbr_sampler/data/locations_data.json'
ceps_file = 'ptbr_sampler/data/cities_with_ceps.json'
output_file = 'ptbr_sampler/data/cities_merged.json'

print(f'Reading normalized data from {normalized_file}...')
with open(normalized_file, encoding='utf-8') as f:
    normalized_data = json.load(f)

print(f'Reading cities with CEPs data from {ceps_file}...')
with open(ceps_file, encoding='utf-8') as f:
    ceps_data = json.load(f)

# Process the data
print('Merging city data...')
cities_matched = 0
cities_not_found = 0

for city_name, city_data in normalized_data['cities'].items():
    # We need both city_name and city_uf to match
    city_uf = city_data.get('city_uf')

    # Ensure we have city_name in the data
    if 'city_name' not in city_data:
        city_data['city_name'] = city_name

    # Try to find a match in the ceps_data
    matched = False

    # Loop through the cities in ceps_data
    for cep_city_key, cep_city_data in ceps_data['cities'].items():
        # Check if both city_name and city_uf match using the nested field values
        if cep_city_data.get('city_name') == city_name and cep_city_data.get('city_uf') == city_uf:
            # Match found! Copy the fields
            if 'ddd' in cep_city_data:
                city_data['ddd'] = cep_city_data['ddd']
            if 'ceps' in cep_city_data:
                city_data['ceps'] = cep_city_data['ceps']
            if 'aka' in cep_city_data:
                city_data['aka'] = cep_city_data['aka']

            cities_matched += 1
            matched = True
            break

    if not matched:
        cities_not_found += 1

# Save the updated data
print(f'Writing merged data to {output_file}...')
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(normalized_data, f, ensure_ascii=False, indent=2)

print(f'Done! Matched {cities_matched} cities.')
print(f'Could not find matching data for {cities_not_found} cities.')
print(f'Merged data saved to {output_file}')
