"""
Tests for the CEI utility module.
"""
import pytest
import asyncio
from ptbr_sampler.utils.cei import validate_cei, generate_cei


class TestCEI:
    """Test suite for CEI utility functions."""

    @pytest.mark.asyncio
    async def test_generate_cei_format(self):
        """Test that generated CEI has correct format."""
        # Generate a CEI
        cei = await asyncio.to_thread(generate_cei)
        
        # Test the format - should be 12 digits
        clean_cei = ''.join(c for c in cei if c.isdigit())
        assert len(clean_cei) == 12, f"Generated CEI '{cei}' does not have 12 digits"
    
    @pytest.mark.asyncio
    async def test_generate_cei_valid(self):
        """Test that generated CEI is valid according to validation algorithm."""
        # Generate a CEI
        cei = await asyncio.to_thread(generate_cei)
        
        # Test validation
        is_valid = await asyncio.to_thread(validate_cei, cei)
        assert is_valid, f"Generated CEI '{cei}' is not valid"
    
    @pytest.mark.asyncio
    async def test_validate_cei_valid(self):
        """Test valid CEI numbers."""
        # Some example CEI numbers (these are examples, might need to be replaced with actual valid CEIs)
        valid_ceis = [
            "12.123.12345/12",
            "12123.12345/12",
            "12.123.12345/12"
        ]
        
        for cei in valid_ceis:
            is_valid = await asyncio.to_thread(validate_cei, cei)
            assert is_valid, f"CEI '{cei}' should be valid"
    
    @pytest.mark.asyncio
    async def test_validate_cei_invalid(self):
        """Test invalid CEI numbers."""
        # Some invalid CEI numbers
        invalid_ceis = [
            "11.111.11111/11",  # Same digits
            "12.345.67890/12",  # Random incorrect
            "00.000.00000/00",  # All zeros
            "12.123.12345/00",  # Incorrect check digit
            "12.123.12345",     # Too short
            "abc.def.ghijk/lm", # Non-numeric
            "",                 # Empty
            None,               # None
        ]
        
        for cei in invalid_ceis:
            is_valid = await asyncio.to_thread(validate_cei, cei)
            assert not is_valid, f"CEI '{cei}' should be invalid"
    
    @pytest.mark.asyncio
    async def test_generate_cei_unique(self):
        """Test that generated CEIs are unique."""
        # Generate multiple CEIs
        ceis = [await asyncio.to_thread(generate_cei) for _ in range(10)]
        
        # Check that all CEIs are unique
        unique_ceis = set(ceis)
        assert len(unique_ceis) == len(ceis), "Generated CEIs are not unique"
        
    @pytest.mark.asyncio
    async def test_cei_formatting(self):
        """Test that generated CEI has proper formatting with punctuation."""
        # Generate a formatted CEI
        cei = await asyncio.to_thread(generate_cei, formatted=True)
        
        # Check formatting pattern: XX.XXX.XXXXX/XX
        assert len(cei) == 14, f"Formatted CEI '{cei}' does not have 14 characters"
        assert cei[2] == '.', f"Incorrect format at position 2: {cei}"
        assert cei[6] == '.', f"Incorrect format at position 6: {cei}"
        assert cei[12] == '/', f"Incorrect format at position 12: {cei}"
        
        # Generate an unformatted CEI
        cei_unformatted = await asyncio.to_thread(generate_cei, formatted=False)
        assert len(cei_unformatted) == 12, f"Unformatted CEI '{cei_unformatted}' does not have 12 characters"
        assert '.' not in cei_unformatted, f"Unformatted CEI '{cei_unformatted}' should not contain dots"
        assert '/' not in cei_unformatted, f"Unformatted CEI '{cei_unformatted}' should not contain slashes" 