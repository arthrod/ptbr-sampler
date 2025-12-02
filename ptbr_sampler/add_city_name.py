import json

# Define file paths
input_file = 'ptbr_sampler/data/locations_data_normalized.json'
output_file = 'ptbr_sampler/data/locations_data_updated.json'

# Read the JSON file
print(f'Reading data from {input_file}...')
with open(input_file, encoding='utf-8') as f:
    data = json.load(f)

# Process the data - add city_name to each city
print('Processing city data...')
cities_count = 0
if 'cities' in data:
    for city_name, city_data in data['cities'].items():
        # Add the city_name field to the city data
        city_data['city_name'] = city_name
        cities_count += 1

# Save the updated data
print(f'Writing updated data to {output_file}...')
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'Done! Added city_name field to {cities_count} cities.')
print(f'Updated data saved to {output_file}')
