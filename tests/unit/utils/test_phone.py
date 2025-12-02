"""
Tests for the phone utility module.
"""
import pytest
import asyncio
import re
from ptbr_sampler.utils.phone import generate_phone_number, get_ddd_code, normalize_phone


class TestPhone:
    """Test suite for phone utility functions."""

    @pytest.mark.asyncio
    async def test_generate_phone_number_format(self):
        """Test that generated phone number has correct format."""
        # Generate a phone number
        phone = await asyncio.to_thread(generate_phone_number)
        
        # Test the format - should match the Brazilian phone pattern
        clean_phone = ''.join(c for c in phone if c.isdigit())
        
        # Brazilian phones should be 11 or 10 digits (with DDD)
        assert len(clean_phone) in [10, 11], f"Generated phone '{phone}' has incorrect length"
        
        # If formatted, should contain parentheses and hyphen
        if '(' in phone:
            assert re.match(r'^\(\d{2}\) \d{4,5}-\d{4}$', phone), f"Formatted phone '{phone}' has incorrect format"
    
    @pytest.mark.asyncio
    async def test_generate_phone_with_specific_ddd(self):
        """Test generating a phone number with a specific DDD."""
        # Test with some valid DDD codes
        valid_ddds = ["11", "21", "31", "41", "51"]
        
        for ddd in valid_ddds:
            phone = await asyncio.to_thread(generate_phone_number, ddd=ddd)
            
            # Extract DDD from phone
            clean_phone = ''.join(c for c in phone if c.isdigit())
            phone_ddd = clean_phone[:2]
            
            assert phone_ddd == ddd, f"Phone '{phone}' does not have the requested DDD '{ddd}'"
    
    @pytest.mark.asyncio
    async def test_generate_phone_mobile(self):
        """Test that mobile phone numbers have correct format with 9 as first digit."""
        # Generate a mobile phone
        phone = await asyncio.to_thread(generate_phone_number, mobile=True)
        
        # Mobile phones in Brazil start with 9 after the DDD
        clean_phone = ''.join(c for c in phone if c.isdigit())
        
        # Check if it's 11 digits (including DDD) and 9th position
        assert len(clean_phone) == 11, f"Mobile phone '{phone}' does not have 11 digits"
        assert clean_phone[2] == '9', f"Mobile phone '{phone}' does not start with 9 after DDD"
    
    @pytest.mark.asyncio
    async def test_generate_phone_landline(self):
        """Test that landline phone numbers have correct format without 9 as first digit."""
        # Generate a landline phone
        phone = await asyncio.to_thread(generate_phone_number, mobile=False)
        
        # Landlines in Brazil don't start with 9 after the DDD
        clean_phone = ''.join(c for c in phone if c.isdigit())
        
        # Check if it's 10 digits (including DDD)
        assert len(clean_phone) == 10, f"Landline phone '{phone}' does not have 10 digits"
        assert clean_phone[2] != '9', f"Landline phone '{phone}' incorrectly starts with 9 after DDD"
    
    @pytest.mark.asyncio
    async def test_get_ddd_code(self):
        """Test getting a valid DDD code."""
        # Get a DDD code
        ddd = await asyncio.to_thread(get_ddd_code)
        
        # Should be a 2-digit string
        assert isinstance(ddd, str), f"DDD '{ddd}' is not a string"
        assert len(ddd) == 2, f"DDD '{ddd}' is not 2 digits"
        assert ddd.isdigit(), f"DDD '{ddd}' is not numeric"
        
        # Should be a valid Brazilian DDD (between 11 and 99)
        ddd_int = int(ddd)
        assert 11 <= ddd_int <= 99, f"DDD '{ddd}' is not in valid Brazilian DDD range"
    
    @pytest.mark.asyncio
    async def test_normalize_phone(self):
        """Test normalizing different phone formats."""
        test_cases = [
            # Input, Expected Output
            ("(11) 98765-4321", "11987654321"),
            ("11 98765-4321", "11987654321"),
            ("11987654321", "11987654321"),
            ("98765-4321", "98765-4321"),  # No DDD
            ("+55 11 98765-4321", "11987654321"),  # With country code
            ("(11)98765-4321", "11987654321"),  # No space after parenthesis
            ("11.98765.4321", "11987654321"),  # Dots as separators
        ]
        
        for input_phone, expected in test_cases:
            result = await asyncio.to_thread(normalize_phone, input_phone)
            assert result == expected, f"Normalizing '{input_phone}' gave '{result}' instead of '{expected}'" 