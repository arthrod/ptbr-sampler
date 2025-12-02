"""
Tests for the general utility module.
"""
import pytest
import asyncio
import re
from ptbr_sampler.utils.util import clean_id, pad_id


class TestUtil:
    """Test suite for general utility functions."""

    @pytest.mark.asyncio
    async def test_clean_id(self):
        """Test cleaning identifiers by removing non-numeric characters."""
        test_cases = [
            # Input, Expected Output
            ("123-456-789", "123456789"),
            ("123.456.789", "123456789"),
            ("abc123def456", "123456"),
            ("", ""),  # Empty string
            (12345, "12345"),  # Integer input
        ]
        
        for input_val, expected in test_cases:
            result = await asyncio.to_thread(clean_id, input_val)
            assert result == expected, f"Cleaning '{input_val}' gave '{result}' instead of '{expected}'"
    
    @pytest.mark.asyncio
    async def test_pad_id(self):
        """Test padding identifiers with leading zeros."""
        test_cases = [
            # Input, Format, Expected Output
            ("123", "%011d", "00000000123"),
            (456, "%09d", "000000456"),
            ("", "%05d", "00000"),  # Empty string should be treated as 0
            ("abc123", "%08d", "00000123"),  # Non-numeric chars should be removed
        ]
        
        for input_val, fmt, expected in test_cases:
            result = await asyncio.to_thread(pad_id, input_val, fmt)
            assert result == expected, f"Padding '{input_val}' with format '{fmt}' gave '{result}' instead of '{expected}'" 