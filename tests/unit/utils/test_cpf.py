"""
Tests for the CPF utility module.
"""
import pytest
import asyncio
from ptbr_sampler.utils.cpf import validate_cpf, generate_cpf


class TestCPF:
    """Test suite for CPF utility functions."""

    @pytest.mark.asyncio
    async def test_generate_cpf_format(self):
        """Test that generated CPF has correct format."""
        # Generate a CPF
        cpf = await asyncio.to_thread(generate_cpf)
        
        # Test the format - should be 11 digits, might have punctuation
        clean_cpf = ''.join(c for c in cpf if c.isdigit())
        assert len(clean_cpf) == 11, f"Generated CPF '{cpf}' does not have 11 digits"
    
    @pytest.mark.asyncio
    async def test_generate_cpf_valid(self):
        """Test that generated CPF is valid according to validation algorithm."""
        # Generate a CPF
        cpf = await asyncio.to_thread(generate_cpf)
        
        # Test validation
        is_valid = await asyncio.to_thread(validate_cpf, cpf)
        assert is_valid, f"Generated CPF '{cpf}' is not valid"
    
    @pytest.mark.asyncio
    async def test_validate_cpf_valid(self):
        """Test valid CPF numbers."""
        # Some known valid CPF numbers
        valid_cpfs = [
            "529.982.247-25",
            "52998224725",
            "111.444.777-35",
            "11144477735"
        ]
        
        for cpf in valid_cpfs:
            is_valid = await asyncio.to_thread(validate_cpf, cpf)
            assert is_valid, f"CPF '{cpf}' should be valid"
    
    @pytest.mark.asyncio
    async def test_validate_cpf_invalid(self):
        """Test invalid CPF numbers."""
        # Some known invalid CPF numbers
        invalid_cpfs = [
            "111.111.111-11",  # Same digits
            "123.456.789-00",  # Random incorrect
            "000.000.000-00",  # All zeros
            "12345678900",     # Invalid check digits
            "123.456.789",     # Too short
            "123.456.789-0",   # Too short
            "abc.def.ghi-jk",  # Non-numeric
            "",                # Empty
            None,              # None
        ]
        
        for cpf in invalid_cpfs:
            is_valid = await asyncio.to_thread(validate_cpf, cpf)
            assert not is_valid, f"CPF '{cpf}' should be invalid"
    
    @pytest.mark.asyncio
    async def test_generate_cpf_unique(self):
        """Test that generated CPFs are unique."""
        # Generate multiple CPFs
        cpfs = [await asyncio.to_thread(generate_cpf) for _ in range(10)]
        
        # Check that all CPFs are unique
        unique_cpfs = set(cpfs)
        assert len(unique_cpfs) == len(cpfs), "Generated CPFs are not unique" 