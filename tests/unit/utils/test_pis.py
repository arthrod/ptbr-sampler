"""
Tests for the PIS utility module.
"""
import pytest
import asyncio
from ptbr_sampler.utils.pis import validate_pis, generate_pis


class TestPIS:
    """Test suite for PIS utility functions."""

    @pytest.mark.asyncio
    async def test_generate_pis_format(self):
        """Test that generated PIS has correct format."""
        # Generate a PIS
        pis = await asyncio.to_thread(generate_pis)
        
        # Test the format - should be 11 digits, might have punctuation
        clean_pis = ''.join(c for c in pis if c.isdigit())
        assert len(clean_pis) == 11, f"Generated PIS '{pis}' does not have 11 digits"
    
    @pytest.mark.asyncio
    async def test_generate_pis_valid(self):
        """Test that generated PIS is valid according to validation algorithm."""
        # Generate a PIS
        pis = await asyncio.to_thread(generate_pis)
        
        # Test validation
        is_valid = await asyncio.to_thread(validate_pis, pis)
        assert is_valid, f"Generated PIS '{pis}' is not valid"
    
    @pytest.mark.asyncio
    async def test_validate_pis_valid(self):
        """Test valid PIS numbers."""
        # Some known valid PIS numbers
        valid_pis_numbers = [
            "120.5352.512-8",
            "12053525128",
            "131.67654.21-8",
            "13167654218"
        ]
        
        for pis in valid_pis_numbers:
            is_valid = await asyncio.to_thread(validate_pis, pis)
            assert is_valid, f"PIS '{pis}' should be valid"
    
    @pytest.mark.asyncio
    async def test_validate_pis_invalid(self):
        """Test invalid PIS numbers."""
        # Some known invalid PIS numbers
        invalid_pis_numbers = [
            "111.1111.111-1",  # Same digits
            "123.4567.890-1",  # Random incorrect
            "000.0000.000-0",  # All zeros
            "120.5352.512-0",  # Invalid check digit
            "123.4567.890",    # Too short
            "abc.defg.hij-k",  # Non-numeric
            "",                # Empty
            None,              # None
        ]
        
        for pis in invalid_pis_numbers:
            is_valid = await asyncio.to_thread(validate_pis, pis)
            assert not is_valid, f"PIS '{pis}' should be invalid"
    
    @pytest.mark.asyncio
    async def test_generate_pis_unique(self):
        """Test that generated PIS numbers are unique."""
        # Generate multiple PIS numbers
        pis_numbers = [await asyncio.to_thread(generate_pis) for _ in range(10)]
        
        # Check that all PIS numbers are unique
        unique_pis = set(pis_numbers)
        assert len(unique_pis) == len(pis_numbers), "Generated PIS numbers are not unique"
        
    @pytest.mark.asyncio
    async def test_pis_formatting(self):
        """Test that generated PIS has proper formatting with punctuation."""
        # Generate a formatted PIS
        pis = await asyncio.to_thread(generate_pis, formatted=True)
        
        # Check formatting pattern: XXX.XXXX.XXX-X
        assert len(pis) == 14, f"Formatted PIS '{pis}' does not have 14 characters"
        assert pis[3] == '.', f"Incorrect format at position 3: {pis}"
        assert pis[8] == '.', f"Incorrect format at position 8: {pis}"
        assert pis[12] == '-', f"Incorrect format at position 12: {pis}"
        
        # Generate an unformatted PIS
        pis_unformatted = await asyncio.to_thread(generate_pis, formatted=False)
        assert len(pis_unformatted) == 11, f"Unformatted PIS '{pis_unformatted}' does not have 11 characters"
        assert '.' not in pis_unformatted, f"Unformatted PIS '{pis_unformatted}' should not contain dots"
        assert '-' not in pis_unformatted, f"Unformatted PIS '{pis_unformatted}' should not contain hyphens" 