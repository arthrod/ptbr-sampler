"""
Tests for the Brazilian RG class module.
"""
import pytest
import asyncio
import re
from pathlib import Path

from ptbr_sampler.br_rg_class import BrazilianRG


class TestBrazilianRG:
    """Test suite for the Brazilian RG class."""

    @pytest.fixture(scope="class")
    def br_rg(self):
        """
        Provide a pytest fixture that yields a fresh BrazilianRG instance for use in tests.
        
        Returns:
            BrazilianRG: A new BrazilianRG instance.
        """
        return BrazilianRG()
    
    @pytest.mark.asyncio
    async def test_generate_rg_basic(self, br_rg):
        """Test basic RG generation."""
        # Generate an RG without specifying a state
        rg = await asyncio.to_thread(br_rg.generate)
        
        # Check that the RG is a dict with rg and issuer keys when include_issuer=True (default)
        assert isinstance(rg, dict), f"RG '{rg}' is not a dictionary"
        assert "rg" in rg, f"RG info missing 'rg' key"
        assert "issuer" in rg, f"RG info missing 'issuer' key"
        
        # Extract the RG number
        rg_num = rg["rg"]
        
        # Check that the RG has the correct format (digits and possibly X, with optional formatting)
        # Remove formatting characters first
        clean_rg = ''.join(c for c in rg_num if c.isdigit() or c == 'X')
        assert len(clean_rg) >= 8, f"RG '{rg_num}' does not have at least 8 characters"
    
    @pytest.mark.asyncio
    async def test_generate_rg_by_state(self, br_rg):
        """Test RG generation for specific states."""
        # Test RG generation for various Brazilian states
        test_states = ["SP", "RJ", "MG", "RS", "BA", "PR"]
        
        for state in test_states:
            rg = await asyncio.to_thread(br_rg.generate, state=state, include_issuer=False)
            
            # Check that the RG is a string when include_issuer=False
            assert isinstance(rg, str), f"RG for state {state} '{rg}' is not a string"
            assert rg, f"RG for state {state} is empty"
            
            # Different states may have different RG formats, so we check the general pattern
            clean_rg = ''.join(c for c in rg if c.isdigit() or c == 'X')
            assert len(clean_rg) >= 8, f"RG for state {state} '{rg}' does not have at least 8 characters"
            
            # Some states have specific formats
            if state == "SP":
                # SP RGs often have 9 digits and a specific format
                clean_rg = ''.join(c for c in rg if c.isdigit())
                assert len(clean_rg) == 9, f"SP RG '{rg}' does not have 9 digits"
            elif state == "RJ":
                # RJ RGs have a specific format
                clean_rg = ''.join(c for c in rg if c.isdigit())
                assert len(clean_rg) >= 8, f"RJ RG '{rg}' does not have at least 8 digits"
    
    @pytest.mark.asyncio
    async def test_generate_rg_with_issuer(self, br_rg):
        """Test RG generation with issuing agency."""
        # Generate an RG with issuing agency
        rg_info = await asyncio.to_thread(br_rg.generate, include_issuer=True)
        
        # The result should be a dictionary with 'rg' and 'issuer' keys
        assert isinstance(rg_info, dict), f"RG info '{rg_info}' is not a dictionary"
        assert "rg" in rg_info, f"RG info missing 'rg' key"
        assert "issuer" in rg_info, f"RG info missing 'issuer' key"
        
        # Check that the RG and issuer are strings
        assert isinstance(rg_info["rg"], str), f"RG '{rg_info['rg']}' is not a string"
        assert isinstance(rg_info["issuer"], str), f"Issuer '{rg_info['issuer']}' is not a string"
        
        # Common issuing agencies in Brazil
        common_issuers = ["SSP", "SESP", "DETRAN", "IFP", "PCMG", "SSPDS", "IGP"]
        assert any(issuer in rg_info["issuer"] for issuer in common_issuers), f"Issuer '{rg_info['issuer']}' is not a common Brazilian issuing agency"
    
    @pytest.mark.asyncio
    async def test_generate_multiple_rgs(self, br_rg):
        """Test generating multiple RGs to ensure uniqueness."""
        # Generate multiple RGs
        rgs = [await asyncio.to_thread(br_rg.generate, include_issuer=False) for _ in range(10)]
        
        # Check that all RGs are unique
        unique_rgs = set(rgs)
        assert len(unique_rgs) == len(rgs), f"Generated RGs are not unique: {rgs}"
    
    @pytest.mark.asyncio
    async def test_state_specific_issuer(self, br_rg):
        """Test that RGs are generated with the correct state-specific issuer."""
        # Test with specific states
        test_cases = [
            {"state": "SP", "expected_issuer_part": "SSP-SP"},
            {"state": "RJ", "expected_issuer_part": "DETRAN-RJ"},
            {"state": "MG", "expected_issuer_part": "PCMG"}
        ]
        
        for case in test_cases:
            state = case["state"]
            expected_issuer_part = case["expected_issuer_part"]
            
            rg_info = await asyncio.to_thread(br_rg.generate, state=state, include_issuer=True)
            
            # Check that the issuer contains the expected state-specific part
            assert expected_issuer_part in rg_info["issuer"], f"Issuer '{rg_info['issuer']}' for state {state} does not contain '{expected_issuer_part}'" 