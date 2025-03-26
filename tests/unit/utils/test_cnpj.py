"""
Tests for the CNPJ utility module.
"""
import pytest
import asyncio
from ptbr_sampler.utils.cnpj import validate_cnpj, generate_cnpj


class TestCNPJ:
    """Test suite for CNPJ utility functions."""

    @pytest.mark.asyncio
    async def test_generate_cnpj_format(self):
        """Test that generated CNPJ has correct format."""
        # Generate a CNPJ
        cnpj = await asyncio.to_thread(generate_cnpj)
        
        # Test the format - should be 14 digits, might have punctuation
        clean_cnpj = ''.join(c for c in cnpj if c.isdigit())
        assert len(clean_cnpj) == 14, f"Generated CNPJ '{cnpj}' does not have 14 digits"
    
    @pytest.mark.asyncio
    async def test_generate_cnpj_valid(self):
        """Test that generated CNPJ is valid according to validation algorithm."""
        # Generate a CNPJ
        cnpj = await asyncio.to_thread(generate_cnpj)
        
        # Test validation
        is_valid = await asyncio.to_thread(validate_cnpj, cnpj)
        assert is_valid, f"Generated CNPJ '{cnpj}' is not valid"
    
    @pytest.mark.asyncio
    async def test_validate_cnpj_valid(self):
        """Test valid CNPJ numbers."""
        # Some known valid CNPJ numbers
        valid_cnpjs = [
            "11.444.777/0001-61",
            "11444777000161",
            "45.283.163/0001-67",
            "45283163000167"
        ]
        
        for cnpj in valid_cnpjs:
            is_valid = await asyncio.to_thread(validate_cnpj, cnpj)
            assert is_valid, f"CNPJ '{cnpj}' should be valid"
    
    @pytest.mark.asyncio
    async def test_validate_cnpj_invalid(self):
        """Test invalid CNPJ numbers."""
        # Some known invalid CNPJ numbers
        invalid_cnpjs = [
            "11.111.111/1111-11",  # Same digits
            "12.345.678/9012-34",  # Random incorrect
            "00.000.000/0000-00",  # All zeros
            "11.444.777/0001-00",  # Invalid check digits
            "12.345.678/9012",     # Too short
            "abc.def.ghi/jklm-no", # Non-numeric
            "",                    # Empty
            None,                  # None
        ]
        
        for cnpj in invalid_cnpjs:
            is_valid = await asyncio.to_thread(validate_cnpj, cnpj)
            assert not is_valid, f"CNPJ '{cnpj}' should be invalid"
    
    @pytest.mark.asyncio
    async def test_generate_cnpj_unique(self):
        """Test that generated CNPJs are unique."""
        # Generate multiple CNPJs
        cnpjs = [await asyncio.to_thread(generate_cnpj) for _ in range(10)]
        
        # Check that all CNPJs are unique
        unique_cnpjs = set(cnpjs)
        assert len(unique_cnpjs) == len(cnpjs), "Generated CNPJs are not unique"
        
    @pytest.mark.asyncio
    async def test_cnpj_formatting(self):
        """Test that generated CNPJ has proper formatting with punctuation."""
        # Generate a CNPJ
        cnpj = await asyncio.to_thread(generate_cnpj, formatted=True)
        
        # Check formatting pattern: XX.XXX.XXX/XXXX-XX
        assert len(cnpj) == 18, f"Formatted CNPJ '{cnpj}' does not have 18 characters"
        assert cnpj[2] == '.', f"Incorrect format at position 2: {cnpj}"
        assert cnpj[6] == '.', f"Incorrect format at position 6: {cnpj}"
        assert cnpj[10] == '/', f"Incorrect format at position 10: {cnpj}"
        assert cnpj[15] == '-', f"Incorrect format at position 15: {cnpj}" 