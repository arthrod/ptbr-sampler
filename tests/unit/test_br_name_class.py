"""
Tests for the Brazilian name class module.
"""
import pytest
import asyncio
import json
import re
from datetime import datetime, date
from pathlib import Path

from ptbr_sampler.br_name_class import BRName


class TestBRName:
    """Test suite for the Brazilian name class."""

    @pytest.fixture(scope="class")
    async def br_name(self):
        """Fixture providing an instance of BRName."""
        name_obj = BRName()
        await name_obj.load_data()
        return name_obj
    
    @pytest.fixture(scope="class")
    def test_data_dir(self):
        """Fixture providing the test data directory."""
        data_dir = Path("tests/results")
        data_dir.mkdir(exist_ok=True, parents=True)
        return data_dir
    
    @pytest.mark.asyncio
    async def test_initialization(self, br_name):
        """Test the initialization of the BRName class."""
        # Check that the loaded data is not empty
        assert br_name.names_data, "Names data is empty"
        assert br_name.surnames_data, "Surnames data is empty"
        assert br_name.middle_names, "Middle names data is empty"
        
        # Check that the names data has both male and female names
        male_names = br_name.names_data["M"]
        female_names = br_name.names_data["F"]
        assert male_names, "Male names list is empty"
        assert female_names, "Female names list is empty"
    
    @pytest.mark.asyncio
    async def test_get_random_name(self, br_name):
        """Test getting a random name."""
        # Test with both genders
        for gender in ["M", "F"]:
            name = await br_name.get_random_name(gender)
            
            # Check that the name is a string
            assert isinstance(name, str), f"Name '{name}' is not a string"
            assert name, f"Name is empty"
            
            # Check gender-specific names (if the API follows Brazilian naming conventions)
            if gender == "M" and name.endswith(("a", "e")):
                # Some male names end with 'a' or 'e' in Portuguese, so this is not a strict rule
                pass
            elif gender == "F" and not name.endswith(("a", "e")):
                # Many female names end with 'a' or 'e' in Portuguese, but not all
                pass
    
    @pytest.mark.asyncio
    async def test_get_random_surname(self, br_name):
        """Test getting a random surname."""
        surname = await br_name.get_random_surname()
        
        # Check that the surname is a string
        assert isinstance(surname, str), f"Surname '{surname}' is not a string"
        assert surname, f"Surname is empty"
    
    @pytest.mark.asyncio
    async def test_get_random_middle_name(self, br_name):
        """Test getting a random middle name."""
        middle_name = await br_name.get_random_middle_name()
        
        # Check that the middle name is a string
        assert isinstance(middle_name, str), f"Middle name '{middle_name}' is not a string"
        assert middle_name, f"Middle name is empty"
    
    @pytest.mark.asyncio
    async def test_get_random_full_name(self, br_name):
        """Test getting a random full name."""
        # Test with both genders
        for gender in ["M", "F"]:
            full_name = await br_name.get_random_full_name(gender)
            
            # Check that the full name is a string
            assert isinstance(full_name, str), f"Full name '{full_name}' is not a string"
            assert full_name, f"Full name is empty"
            
            # Check that the full name has at least two parts (first and last name)
            name_parts = full_name.split()
            assert len(name_parts) >= 2, f"Full name '{full_name}' does not have at least a first and last name"
    
    @pytest.mark.asyncio
    async def test_get_random_full_name_with_middle(self, br_name):
        """Test getting a random full name with a middle name."""
        # Test with both genders
        for gender in ["M", "F"]:
            full_name = await br_name.get_random_full_name(gender, include_middle=True)
            
            # Check that the full name is a string
            assert isinstance(full_name, str), f"Full name '{full_name}' is not a string"
            assert full_name, f"Full name is empty"
            
            # Check that the full name has at least three parts (first, middle, and last name)
            name_parts = full_name.split()
            assert len(name_parts) >= 3, f"Full name '{full_name}' does not have at least first, middle, and last names"
    
    @pytest.mark.asyncio
    async def test_get_random_birthdate(self, br_name):
        """Test getting a random birthdate."""
        # Test with various age ranges
        age_ranges = [
            (0, 18),    # Children/teens
            (18, 30),   # Young adults
            (30, 50),   # Adults
            (50, 90)    # Seniors
        ]
        
        for min_age, max_age in age_ranges:
            birthdate_info = await br_name.get_random_birthdate(min_age, max_age)
            
            # Check that the birthdate_info has the expected fields
            assert "birthdate" in birthdate_info, "Birthdate info missing 'birthdate' field"
            assert "age" in birthdate_info, "Birthdate info missing 'age' field"
            
            # Check that the birthdate is a string
            birthdate = birthdate_info["birthdate"]
            assert isinstance(birthdate, str), f"Birthdate '{birthdate}' is not a string"
            
            # Check that the birthdate has the format 'YYYY-MM-DD'
            assert re.match(r'^\d{4}-\d{2}-\d{2}$', birthdate), f"Birthdate '{birthdate}' does not match format 'YYYY-MM-DD'"
            
            # Check that the age is within the specified range
            age = birthdate_info["age"]
            assert isinstance(age, int), f"Age '{age}' is not an integer"
            assert min_age <= age <= max_age, f"Age {age} not in range [{min_age}, {max_age}]"
            
            # Check that the birthdate and age are consistent
            birthdate_date = datetime.strptime(birthdate, "%Y-%m-%d").date()
            today = date.today()
            calculated_age = today.year - birthdate_date.year - ((today.month, today.day) < (birthdate_date.month, birthdate_date.day))
            assert calculated_age == age, f"Calculated age {calculated_age} does not match returned age {age}"
    
    @pytest.mark.asyncio
    async def test_get_random_person(self, br_name):
        """Test generating a random person."""
        # Test with both genders
        for gender in ["M", "F"]:
            person = await br_name.get_random_person(gender)
            
            # Check that the person has the expected fields
            assert "name" in person, "Person missing 'name' field"
            assert "gender" in person, "Person missing 'gender' field"
            assert "birthdate" in person, "Person missing 'birthdate' field"
            assert "age" in person, "Person missing 'age' field"
            assert "cpf" in person, "Person missing 'cpf' field"
            
            # Check that the gender matches the requested gender
            assert person["gender"] == gender, f"Person gender '{person['gender']}' does not match requested gender '{gender}'"
    
    @pytest.mark.asyncio
    async def test_get_random_person_with_age_range(self, br_name):
        """Test generating a random person with a specific age range."""
        # Test with specific age range
        min_age = 25
        max_age = 35
        
        person = await br_name.get_random_person("M", min_age, max_age)
        
        # Check that the age is within the specified range
        age = person["age"]
        assert min_age <= age <= max_age, f"Person age {age} not in range [{min_age}, {max_age}]" 