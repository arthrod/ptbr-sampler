"""
Tests for the Brazilian location class module.
"""
import pytest
import asyncio
import json
from pathlib import Path

from ptbr_sampler.br_location_class import BRLocation


class TestBRLocation:
    """Test suite for the Brazilian location class."""

    @pytest.fixture(scope="class")
    async def br_location(self):
        """Fixture providing an instance of BRLocation."""
        location = BRLocation()
        await location.load_data()
        return location
    
    @pytest.fixture(scope="class")
    def test_data_dir(self):
        """Fixture providing the test data directory."""
        data_dir = Path("tests/results")
        data_dir.mkdir(exist_ok=True, parents=True)
        return data_dir
    
    @pytest.mark.asyncio
    async def test_initialization(self, br_location):
        """Test the initialization of the BRLocation class."""
        # Check that the loaded data is not empty
        assert br_location.locations_data, "Locations data is empty"
        assert br_location.cities_with_ceps, "Cities with CEPs data is empty"
        
        # Check that the weighted cities list is initialized
        assert br_location.weighted_cities, "Weighted cities list is empty"
    
    @pytest.mark.asyncio
    async def test_get_all_states(self, br_location):
        """Test getting all Brazilian states."""
        states = await br_location.get_all_states()
        
        # Brazil has 27 federal units (26 states + Federal District)
        assert len(states) == 27, f"Expected 27 states, got {len(states)}"
        
        # Check that common states are in the list
        common_states = ["SP", "RJ", "MG", "RS", "BA", "PR", "PE", "DF"]
        for state in common_states:
            assert state in states, f"Common state {state} not in list"
    
    @pytest.mark.asyncio
    async def test_get_cities_by_state(self, br_location):
        """Test getting cities by state."""
        # Test with a few states
        test_states = ["SP", "RJ", "MG", "RS"]
        
        for state in test_states:
            cities = await br_location.get_cities_by_state(state)
            
            # Check that we got some cities
            assert cities, f"No cities found for state {state}"
            
            # Check that all cities are in the right state
            for city_data in cities:
                assert city_data["state"] == state, f"City {city_data['city']} not in state {state}"
    
    @pytest.mark.asyncio
    async def test_get_random_city(self, br_location):
        """Test getting a random city."""
        # Get a random city
        city = await br_location.get_random_city()
        
        # Check that the city has the expected fields
        assert "city" in city, "City missing 'city' field"
        assert "state" in city, "City missing 'state' field"
        assert "ibge_code" in city, "City missing 'ibge_code' field"
    
    @pytest.mark.asyncio
    async def test_get_random_city_by_state(self, br_location):
        """Test getting a random city from a specific state."""
        # Test with a few states
        test_states = ["SP", "RJ", "MG", "RS"]
        
        for state in test_states:
            city = await br_location.get_random_city_by_state(state)
            
            # Check that the city is in the right state
            assert city["state"] == state, f"City {city['city']} not in state {state}"
    
    @pytest.mark.asyncio
    async def test_get_random_city_by_state_weighted(self, br_location):
        """Test getting a random city from a specific state with population weighting."""
        # Test with a few states
        test_states = ["SP", "RJ", "MG", "RS"]
        
        for state in test_states:
            city = await br_location.get_random_city_by_state(state, weighted=True)
            
            # Check that the city is in the right state
            assert city["state"] == state, f"City {city['city']} not in state {state}"
    
    @pytest.mark.asyncio
    async def test_get_random_address(self, br_location):
        """Test generating a random address."""
        # Generate a random address
        address = await br_location.get_random_address(state="SP", make_api_call=False)
        
        # Check address fields
        assert "street" in address, "Address missing 'street' field"
        assert "number" in address, "Address missing 'number' field"
        assert "district" in address, "Address missing 'district' field"
        assert "city" in address, "Address missing 'city' field"
        assert "state" in address, "Address missing 'state' field"
        assert "cep" in address, "Address missing 'cep' field"
        
        # Check that the address is in the right state
        assert address["state"] == "SP", f"Address not in state SP: {address}"
    
    @pytest.mark.asyncio
    async def test_get_random_full_location(self, br_location):
        """Test generating a random full location."""
        # Generate a random full location
        location = await br_location.get_random_full_location(make_api_call=False)
        
        # Check location fields
        assert "city" in location, "Location missing 'city' field"
        assert "state" in location, "Location missing 'state' field"
        assert "address" in location, "Location missing 'address' field"
        
        # Check address subfields
        address = location["address"]
        assert "street" in address, "Address missing 'street' field"
        assert "number" in address, "Address missing 'number' field"
        assert "district" in address, "Address missing 'district' field"
        assert "cep" in address, "Address missing 'cep' field"
    
    @pytest.mark.asyncio
    async def test_get_random_full_location_filtered(self, br_location):
        """Test generating a random full location with filters."""
        # Generate a random full location for a specific state and city
        state = "SP"
        city = "São Paulo"
        
        location = await br_location.get_random_full_location(
            state=state, 
            city=city,
            make_api_call=False
        )
        
        # Check that the location is in the right state and city
        assert location["state"] == state, f"Location not in state {state}: {location}"
        assert location["city"] == city, f"Location not in city {city}: {location}"
    
    @pytest.mark.asyncio
    async def test_get_city_data(self, br_location):
        """Test getting city data."""
        # Test with a few cities
        test_cities = [
            {"state": "SP", "city": "São Paulo"},
            {"state": "RJ", "city": "Rio de Janeiro"},
            {"state": "MG", "city": "Belo Horizonte"},
            {"state": "RS", "city": "Porto Alegre"}
        ]
        
        for test_city in test_cities:
            state = test_city["state"]
            city_name = test_city["city"]
            
            city_data = await br_location.get_city_data(state, city_name)
            
            # Check that we got the right city
            assert city_data["city"] == city_name, f"Got wrong city: {city_data['city']} instead of {city_name}"
            assert city_data["state"] == state, f"Got wrong state: {city_data['state']} instead of {state}" 