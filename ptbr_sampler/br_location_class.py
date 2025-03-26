import json
import random
from pathlib import Path
from loguru import logger


class BrazilianLocationSampler:
    """Brazilian location sampling class for generating realistic location data."""

    def __init__(self, json_file_path: str | Path):
        """Initialize the sampler with population data from JSON files.

        Args:
            json_file_path: Path to main JSON file with population data

        Raises:
            ValueError: If required data is missing or invalid
            FileNotFoundError: If JSON files cannot be found
        """
        with Path(json_file_path).open(encoding='utf-8') as file:
            self.data = json.load(file)

        # Ensure we have required data
        if not self.data.get('cities') or not self.data.get('states'):
            raise ValueError("Missing 'cities' or 'states' data in JSON file")

        # Pre-calculate weights for more efficient sampling
        self._calculate_weights()

    def update_cities(self, cities_data: dict) -> None:
        """Update the cities data and recalculate weights.

        This method allows updating the cities data after initialization,
        which is useful when loading custom location data.

        Args:
            cities_data: Dictionary containing city data to update or add

        Raises:
            ValueError: If cities_data is not a valid dictionary
        """
        if not isinstance(cities_data, dict):
            raise ValueError('cities_data must be a dictionary')

        # Create a map to find existing cities by state and name
        existing_cities_map = {}
        for city_key, city_data in self.data['cities'].items():
            city_name = city_data.get('city_name')
            state_abbr = city_data.get('city_uf')
            
            if city_name and state_abbr:
                # Create a nested dictionary indexed by state then city name
                if state_abbr not in existing_cities_map:
                    existing_cities_map[state_abbr] = {}
                
                existing_cities_map[state_abbr][city_name] = {
                    'key': city_key,
                    'data': city_data
                }

        # Update the cities data with two-step matching
        if cities_data:
            for city_key, new_city_data in cities_data.items():
                city_name = new_city_data.get('city_name')
                state_abbr = new_city_data.get('city_uf')
                
                if not city_name or not state_abbr:
                    # Skip entries without required data
                    logger.warning(f"Skipping update for city with missing name or state: {city_key}")
                    continue
                
                # Two-step matching process:
                # 1. First check if we have any cities in this state
                # 2. Then check if the city name exists in that state
                if (state_abbr in existing_cities_map and 
                    city_name in existing_cities_map[state_abbr]):
                    
                    # We found a match by state and city name
                    existing_entry = existing_cities_map[state_abbr][city_name]
                    existing_key = existing_entry['key']
                    existing_data = existing_entry['data']
                    
                    # Update using the existing key to maintain state code formatting
                    self.data['cities'][existing_key] = new_city_data
                else:
                    # This is a new city or a city not found using our two-step process
                    self.data['cities'][city_key] = new_city_data

        # Recalculate weights to ensure proper sampling
        self._calculate_weights()

    def update_states(self, states_data: dict) -> None:
        """Update the states data and recalculate weights.

        This method allows updating the states data after initialization,
        which is useful when loading custom location data.

        Args:
            states_data: Dictionary containing state data to update or add

        Raises:
            ValueError: If states_data is not a valid dictionary
        """
        if not isinstance(states_data, dict):
            raise ValueError('states_data must be a dictionary')

        # Update the states data
        if states_data:
            self.data['states'].update(states_data)

        # Recalculate weights to ensure proper sampling
        self._calculate_weights()

    def _calculate_weights(self) -> None:
        """Pre-calculate weights for states and cities based on population percentages."""
        # Calculate state weights
        self.state_weights = []
        self.state_names = []

        for state_name, state_data in self.data['states'].items():
            self.state_names.append(state_name)
            self.state_weights.append(state_data['population_percentage'])

        # Normalize state weights to sum to 1
        total_weight = sum(self.state_weights)
        self.state_weights = [w / total_weight for w in self.state_weights]

        # Calculate city weights per state
        self.city_weights_by_state = {}
        self.city_names_by_state = {}
        self.city_data_by_name = {}

        for city_id, city_data in self.data['cities'].items():
            state = city_data['city_uf']
            
            # Get city_name, ensuring it's always set
            # This handles differences between city_id keys in different files
            if 'city_name' not in city_data:
                # Extract city name from city_id if it uses the format "CityName_StateCode"
                if '_' in city_id and city_id.split('_')[-1] == state:
                    city_name = city_id.split('_')[0]
                    city_data['city_name'] = city_name
                    logger.debug(f"Extracted city_name '{city_name}' from city_id '{city_id}'")
                else:
                    # Use the city_id as city_name if no better option
                    city_name = city_id
                    city_data['city_name'] = city_name
                    logger.debug(f"Using city_id '{city_id}' as city_name")
            else:
                city_name = city_data['city_name']

            if state not in self.city_weights_by_state:
                self.city_weights_by_state[state] = []
                self.city_names_by_state[state] = []

            self.city_names_by_state[state].append(city_name)
            self.city_weights_by_state[state].append(city_data['population_percentage_state'])
            
            # Always index by city_name for consistent lookup
            self.city_data_by_name[city_name] = city_data

        # Normalize city weights within each state
        for state in self.city_weights_by_state:
            total = sum(self.city_weights_by_state[state])
            if total > 0:
                self.city_weights_by_state[state] = [w / total for w in self.city_weights_by_state[state]]

    def get_state(self) -> tuple[str, str]:
        """Get a random state weighted by population percentage.

        Returns:
            Tuple of (state_name, state_abbreviation)
        """
        state_name = random.choices(self.state_names, weights=self.state_weights, k=1)[0]
        state_abbr = self.data['states'][state_name]['state_abbr']
        return state_name, state_abbr

    def get_city(self, state_abbr: str | None = None) -> tuple[str, str]:
        """Get a random city weighted by population percentage.

        Args:
            state_abbr: Optional state abbreviation to get city from specific state

        Returns:
            Tuple of (city_name, state_abbreviation)

        Raises:
            ValueError: If no cities found for given state
        """
        if state_abbr is None:
            _, state_abbr = self.get_state()

        city_name = random.choices(self.city_names_by_state[state_abbr], weights=self.city_weights_by_state[state_abbr], k=1)[0]

        return city_name, state_abbr

    def get_state_and_city(self) -> tuple[str, str, str]:
        """Get a random state and city combination weighted by population percentage.

        Returns:
            Tuple of (state_name, state_abbreviation, city_name)
        """
        state_name, state_abbr = self.get_state()
        city_name, _ = self.get_city(state_abbr)
        return state_name, state_abbr, city_name

    def _get_random_cep_for_city(self, city_name: str) -> str:
        """Generate random CEP from city's available CEPs or CEP range.

        Args:
            city_name: Name of city to get CEP for

        Returns:
            Random valid CEP from city's available CEPs or generated from range

        Raises:
            ValueError: If city not found or has no CEPs/CEP range
        """
        if city_name not in self.city_data_by_name:
            logger.error(f'City not found: {city_name}')
            raise ValueError(f'City not found: {city_name}')

        city_data = self.city_data_by_name[city_name]
        
        # Try using specific CEPs first
        if city_data.get('ceps') and len(city_data['ceps']) > 0:
            logger.debug(f"Using CEP from city {city_name}'s ceps list of {len(city_data['ceps'])} CEPs")
            return random.choice(city_data['ceps'])
        
        # Fall back to generating from CEP range if available
        if city_data.get('cep_range_begins') and city_data.get('cep_range_ends'):
            logger.debug(f"Using CEP range for city {city_name}: {city_data['cep_range_begins']} to {city_data['cep_range_ends']}")
            range_start = int(city_data['cep_range_begins'].replace('-', ''))
            range_end = int(city_data['cep_range_ends'].replace('-', ''))
            return str(random.randint(range_start, range_end))

    def _format_cep(self, cep: str, with_dash: bool = True) -> str:
        """Format CEP string with optional dash.

        Args:
            cep: Raw CEP string
            with_dash: Whether to include dash in formatted CEP

        Returns:
            Formatted CEP string
        """
        cep = cep.replace('-', '')
        return f'{cep[:5]}-{cep[5:]}' if with_dash else cep

    def format_full_location(
        self, city: str, state: str, state_abbr: str, include_cep: bool = True, cep_without_dash: bool = False, name: str | None = None
    ) -> str:
        """Format location information into a single string.

        Args:
            city: City name
            state: State name
            state_abbr: State abbreviation
            include_cep: Whether to include CEP
            cep_without_dash: Whether to format CEP without dash
            name: Optional address name

        Returns:
            Formatted location string
        """
        base = f'{city}, {state} ({state_abbr})'
        if not include_cep:
            return base

        # Get a random CEP for the city, prioritizing the ceps array
        cep = self._get_random_cep_for_city(city)
        
        # Format the CEP as needed
        formatted_cep = self._format_cep(cep, not cep_without_dash)
        
        # Add the CEP to the location string
        location_with_cep = f'{city} - {formatted_cep}, {state} ({state_abbr})'
        
        return location_with_cep

    def get_random_location(
        self,
        city_only: bool = False,
        state_abbr_only: bool = False,
        state_full_only: bool = False,
        only_cep: bool = False,
        cep_without_dash: bool = False,
    ) -> str:
        """Get a random location with various formatting options.

        Args:
            city_only: Return only city name
            state_abbr_only: Return only state abbreviation
            state_full_only: Return only full state name
            only_cep: Return only CEP
            cep_without_dash: Format CEP without dash

        Returns:
            Formatted location string according to specified options
        """
        if only_cep:
            city_name, _ = self.get_city()
            cep = self._get_random_cep_for_city(city_name)
            return self._format_cep(cep, not cep_without_dash)

        if state_abbr_only:
            return self.get_state()[1]

        if state_full_only:
            return self.get_state()[0]

        if city_only:
            return self.get_city()[0]

        state_name, state_abbr, city_name = self.get_state_and_city()
        return self.format_full_location(city_name, state_name, state_abbr, True, cep_without_dash)

    def get_city_data_by_name(self, city_name: str, state_abbr: str) -> dict:
        """Get city data using both city name and state abbreviation for reliable lookup.
        
        This method provides a more reliable way to lookup city data compared to
        directly accessing city_data_by_name, especially when there are cities with
        the same name in different states.
        
        Args:
            city_name: The name of the city to look up
            state_abbr: The state abbreviation 
            
        Returns:
            dict: The city data dictionary or an empty dict if not found
            
        Examples:
            >>> sampler = BrazilianLocationSampler('data/cities_with_ceps.json')
            >>> data = sampler.get_city_data_by_name('São Paulo', 'SP')
            >>> print(data.get('ddd'))
            11
        """
        logger.debug(f"Looking up city data for {city_name}, {state_abbr}")
        
        # If no state provided, just use the simple lookup (less reliable)
        if not state_abbr:
            return self.city_data_by_name.get(city_name, {})
        
        # First try the exact lookup with compound key (most reliable)
        city_key = f"{city_name}_{state_abbr}"
        if city_key in self.data['cities']:
            return self.data['cities'][city_key]
        
        # Next, try a more thorough search in self.data['cities']
        for city_id, city_data in self.data['cities'].items():
            if (city_data.get('city_name') == city_name and 
                city_data.get('city_uf') == state_abbr):
                return city_data
        
        # As a fallback, try the city_data_by_name but verify state matches
        if city_name in self.city_data_by_name:
            city_data = self.city_data_by_name[city_name]
            if city_data.get('city_uf') == state_abbr:
                return city_data
            
        # If everything fails, try a case-insensitive search (last resort)
        city_name_lower = city_name.lower()
        for city_id, city_data in self.data['cities'].items():
            if (city_data.get('city_name', '').lower() == city_name_lower and 
                city_data.get('city_uf') == state_abbr):
                return city_data
                
        # If still not found, return empty dict
        logger.warning(f"City data not found for {city_name}, {state_abbr}")
        return {}
