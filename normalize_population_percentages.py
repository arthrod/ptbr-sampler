#!/usr/bin/env python3
import json
import secrets


def normalize_population_data(
    input_file='src/data/locations_data.json',
    ceps_file='src/data/cities_with_ceps.json',
    output_file='src/data/locations_data_normalized.json',
):
    """
    Recalculate population percentages in locations_data.json

    This script:
    1. Loads the existing locations_data.json
    2. Calculates total population across all cities
    3. Recalculates population_percentage_total for each city
    4. Calculates state populations by summing cities within each state
    5. Recalculates population_percentage_state for each city
    6. Imports CEP data from cities_with_ceps.json
    7. Selects a random CEP from a weighted-selected city
    8. Writes the normalized data to a new file
    """
    # Load the data
    with open(input_file, encoding='utf-8') as f:
        data = json.load(f)

    # Load the cities with CEP data
    try:
        with open(ceps_file, encoding='utf-8') as f:
            cities_with_cep_data = json.load(f)
        print(f'Successfully loaded CEP data from {ceps_file}')
    except FileNotFoundError:
        print(f'Warning: CEP data file {ceps_file} not found. Using existing CEP ranges instead.')
        cities_with_cep_data = {}

    # Calculate total population from cities
    city_data = data.get('cities', {})
    total_population = 0
    for city_id, city in city_data.items():
        if 'city_population' in city:
            total_population += city['city_population']

    print(f'Total population from all cities: {total_population}')

    # Calculate state populations by summing city populations
    state_populations = {}
    for city_id, city in city_data.items():
        state = city.get('city_uf')
        if state and 'city_population' in city:
            state_populations[state] = state_populations.get(state, 0) + city['city_population']

    # Update state totals in the states dictionary
    for state_name, state_data in data.get('states', {}).items():
        state_abbr = state_data.get('state_abbr')
        if state_abbr in state_populations:
            state_data['state_population'] = state_populations[state_abbr]

    # Calculate and update percentages for each city
    for city_id, city in city_data.items():
        if 'city_population' in city and city['city_population'] > 0:
            # Calculate percentage of total population
            city['population_percentage_total'] = city['city_population'] / total_population

            # Calculate percentage of state population
            state = city.get('city_uf')
            if state and state in state_populations and state_populations[state] > 0:
                city['population_percentage_state'] = city['city_population'] / state_populations[state]

    # Calculate and update percentages for each state
    for state_name, state_data in data.get('states', {}).items():
        if 'state_population' in state_data and state_data['state_population'] > 0:
            state_data['population_percentage'] = state_data['state_population'] / total_population

    # Check what CEP fields exist in the first few cities
    print('\nSample CEP fields in data:')
    sample_cities = list(city_data.items())[:5]
    for city_id, city in sample_cities:
        cep_fields = {k: v for k, v in city.items() if 'cep' in k.lower()}
        if cep_fields:
            print(f'{city_id}: {cep_fields}')

    # Step 1: Weighted selection of a city based on population
    cities_with_ceps = []
    weights = []

    # If we have the cities_with_cep_data, use it
    if cities_with_cep_data:
        # Print a sample of the CEP data to understand its structure
        sample_city = next(iter(cities_with_cep_data.items())) if cities_with_cep_data else None
        if sample_city:
            print(f'\nSample city from cities_with_ceps.json: {sample_city[0]}')
            if 'ceps' in sample_city[1]:
                print(f"Sample 'ceps' field: {sample_city[1]['ceps'][:3]}...")
            else:
                print(f'Sample city data structure: {sample_city[1].keys()}')

        # Import CEPs from cities_with_ceps.json
        for city_id, city_cep_data in cities_with_cep_data.items():
            if city_id in city_data and 'ceps' in city_cep_data:
                # Add the ceps data to our main dataset
                city_data[city_id]['ceps'] = city_cep_data['ceps']

                # Add to our selection list if it has ceps and population data
                if city_data[city_id].get('city_population', 0) > 0:
                    cities_with_ceps.append((city_id, city_data[city_id]))
                    weights.append(city_data[city_id]['city_population'])
    else:
        # Fallback to using CEP ranges if no CEP data file
        for city_id, city in city_data.items():
            # Check for various CEP fields and create a ceps list/range if needed
            cep_begin = city.get('cep_range_begins') or city.get('cep_starts')
            cep_end = city.get('cep_range_ends') or city.get('cep_ends')

            if cep_begin and cep_end:
                # For simplicity, just use the begin and end values as our CEPs
                city['ceps'] = [cep_begin, cep_end]

            # Now add to our selection list if it has ceps and population data
            if city.get('ceps') and city.get('city_population', 0) > 0:
                cities_with_ceps.append((city_id, city))
                weights.append(city['city_population'])

    print(f'\nFinding a city using weighted selection from {len(cities_with_ceps)} cities with CEP data...')

    if cities_with_ceps:
        # Select a city weighted by population
        selected_city_id, selected_city = secrets.SystemRandom().choices(cities_with_ceps, weights=weights, k=1)[0]

        # Step 2: Randomly pick a CEP from the selected city
        ceps_data = selected_city['ceps']
        if isinstance(ceps_data, list) and ceps_data:
            print(f'Selected city has {len(ceps_data)} CEPs in a list')
            random_cep = secrets.choice(ceps_data)
        elif isinstance(ceps_data, dict) and ceps_data:
            print(f'Selected city has {len(ceps_data)} CEPs in a dictionary')
            random_cep = secrets.choice(list(ceps_data.values()))
        else:
            print('Selected city has a single CEP')
            random_cep = ceps_data

        # Store the selected information
        data['selected_city'] = selected_city_id
        data['selected_city_cep'] = random_cep

        print('\nWeighted Selection Result:')
        print(f'Selected city: {selected_city_id} ({selected_city.get("city_uf", "")})')
        print(f'Population: {selected_city.get("city_population", 0)}')
        print(f'Selected CEP: {random_cep}')
    else:
        print('No cities with CEP data found!')

    # Write the updated data to a new file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f'\nNormalized data written to {output_file}')

    # Validate percentages
    state_percentage_sum = sum(state['population_percentage'] for state in data['states'].values() if 'population_percentage' in state)
    city_percentage_sum = sum(
        city['population_percentage_total'] for city in data['cities'].values() if 'population_percentage_total' in city
    )

    print(f'Sum of all state percentages: {state_percentage_sum}')
    print(f'Sum of all city percentages: {city_percentage_sum}')
    print('Both should be very close to 1.0')

    return data


if __name__ == '__main__':
    normalize_population_data()
