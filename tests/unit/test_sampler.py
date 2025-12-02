"""
Tests for the main sampler module.
"""
import pytest
import asyncio
import json
from pathlib import Path
from typing import Dict, List, Any

from ptbr_sampler.sampler import (
    sample, 
    generate_person, 
    generate_location,
    get_random_district,
    process_weights,
    calculate_city_population_percentile
)


class TestSampler:
    """Test suite for sampler module."""

    @pytest.fixture(scope="class")
    def data_paths(self):
        """
        Provide file paths to test data used by the sampler.
        
        Returns:
            paths (dict[str, str]): Mapping with keys:
                - "json_path": path to cities_with_ceps.json
                - "names_path": path to names_data.json
                - "middle_names_path": path to middle_names.json
                - "surnames_path": path to surnames_data.json
                - "locations_path": path to locations_data.json
        """
        return {
            "json_path": "ptbr_sampler/data/cities_with_ceps.json",
            "names_path": "ptbr_sampler/data/names_data.json",
            "middle_names_path": "ptbr_sampler/data/middle_names.json",
            "surnames_path": "ptbr_sampler/data/surnames_data.json",
            "locations_path": "ptbr_sampler/data/locations_data.json"
        }
    
    @pytest.mark.asyncio
    async def test_sample_basic(self, data_paths):
        """Test basic sampling functionality."""
        # Get a small sample
        samples = await sample(
            qty=5,
            make_api_call=False,
            **data_paths
        )
        
        # Check that we got the right number of samples
        assert len(samples) == 5, f"Expected 5 samples, got {len(samples)}"
        
        # Check that each sample has the expected structure
        for s in samples:
            assert "person" in s, "Sample missing 'person' field"
            assert "location" in s, "Sample missing 'location' field"
            
            # Check person fields
            person = s["person"]
            assert "name" in person, "Person missing 'name' field"
            assert "gender" in person, "Person missing 'gender' field"
            assert "birthdate" in person, "Person missing 'birthdate' field"
            assert "age" in person, "Person missing 'age' field"
            assert "cpf" in person, "Person missing 'cpf' field"
            
            # Check location fields
            location = s["location"]
            assert "city" in location, "Location missing 'city' field"
            assert "state" in location, "Location missing 'state' field"
            assert "address" in location, "Location missing 'address' field"
    
    @pytest.mark.asyncio
    async def test_sample_with_location_filter(self, data_paths):
        """Test sampling with location filter."""
        # Sample only from São Paulo state
        samples = await sample(
            qty=5,
            state="SP",
            make_api_call=False,
            **data_paths
        )
        
        # Check that all samples are from São Paulo state
        for s in samples:
            assert s["location"]["state"] == "SP", f"Sample not from SP: {s['location']}"
    
    @pytest.mark.asyncio
    async def test_sample_with_age_filter(self, data_paths):
        """Test sampling with age filter."""
        # Sample only people between 20 and 30 years old
        samples = await sample(
            qty=5,
            min_age=20,
            max_age=30,
            make_api_call=False,
            **data_paths
        )
        
        # Check that all samples have age within the specified range
        for s in samples:
            age = s["person"]["age"]
            assert 20 <= age <= 30, f"Age {age} not in range 20-30"
    
    @pytest.mark.asyncio
    async def test_sample_with_gender_filter(self, data_paths):
        """Test sampling with gender filter."""
        # Sample only female individuals
        samples = await sample(
            qty=5,
            gender="F",
            make_api_call=False,
            **data_paths
        )
        
        # Check that all samples are female
        for s in samples:
            assert s["person"]["gender"] == "F", f"Sample not female: {s['person']}"
        
        # Sample only male individuals
        samples = await sample(
            qty=5,
            gender="M",
            make_api_call=False,
            **data_paths
        )
        
        # Check that all samples are male
        for s in samples:
            assert s["person"]["gender"] == "M", f"Sample not male: {s['person']}"
    
    @pytest.mark.asyncio
    async def test_generate_person(self, data_paths):
        """Test person generation."""
        # Generate a person
        person = await generate_person(
            gender="M",
            min_age=25,
            max_age=35,
            names_path=data_paths["names_path"],
            surnames_path=data_paths["surnames_path"],
            middle_names_path=data_paths["middle_names_path"]
        )
        
        # Check person fields
        assert "name" in person, "Person missing 'name' field"
        assert "gender" in person, "Person missing 'gender' field"
        assert "birthdate" in person, "Person missing 'birthdate' field"
        assert "age" in person, "Person missing 'age' field"
        assert "cpf" in person, "Person missing 'cpf' field"
        
        # Check gender filter
        assert person["gender"] == "M", f"Person gender is not M: {person['gender']}"
        
        # Check age filter
        assert 25 <= person["age"] <= 35, f"Person age {person['age']} not in range 25-35"
    
    @pytest.mark.asyncio
    async def test_generate_location(self, data_paths):
        """Test location generation."""
        # Generate a location
        location = await generate_location(
            state=None,  # Any state
            city=None,   # Any city
            weighted=True,
            make_api_call=False,
            locations_path=data_paths["locations_path"],
            json_path=data_paths["json_path"]
        )
        
        # Check location fields
        assert "city" in location, "Location missing 'city' field"
        assert "state" in location, "Location missing 'state' field"
        assert "address" in location, "Location missing 'address' field"
        assert "street" in location["address"], "Address missing 'street' field"
        assert "number" in location["address"], "Address missing 'number' field"
        assert "district" in location["address"], "Address missing 'district' field"
        assert "cep" in location["address"], "Address missing 'cep' field"
    
    @pytest.mark.asyncio
    async def test_process_weights(self):
        """Test weight processing for weighted sampling."""
        # Test data with cities and populations
        data = [
            {"city": "São Paulo", "population": 12000000},
            {"city": "Rio de Janeiro", "population": 6000000},
            {"city": "Belo Horizonte", "population": 2500000},
            {"city": "Salvador", "population": 2900000},
            {"city": "Curitiba", "population": 1800000}
        ]
        
        # Process weights
        weighted_data = await asyncio.to_thread(process_weights, data)
        
        # Check that weights are properly calculated
        total_population = sum(city["population"] for city in data)
        
        for city in weighted_data:
            assert "weight" in city, f"City {city['city']} missing 'weight' field"
            expected_weight = city["population"] / total_population
            assert abs(city["weight"] - expected_weight) < 1e-10, f"Weight for {city['city']} incorrect"
        
        # Check that weights sum to 1.0
        total_weight = sum(city["weight"] for city in weighted_data)
        assert abs(total_weight - 1.0) < 1e-10, f"Total weight {total_weight} does not sum to 1.0"
    
    @pytest.mark.asyncio
    async def test_get_random_district(self):
        """Test getting random district names."""
        # Test with multiple calls
        districts = [await asyncio.to_thread(get_random_district) for _ in range(10)]
        
        # Check that all districts are strings
        for district in districts:
            assert isinstance(district, str), f"District '{district}' is not a string"
            assert len(district) > 0, f"District '{district}' is empty" 