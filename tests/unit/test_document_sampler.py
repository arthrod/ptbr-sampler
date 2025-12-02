"""
Tests for the document sampler module.
"""
import pytest
import asyncio
import json
from pathlib import Path

from ptbr_sampler.document_sampler import DocumentSampler


class TestDocumentSampler:
    """Test suite for the document sampler module."""

    @pytest.fixture(scope="class")
    def document_sampler(self):
        """Fixture providing an instance of DocumentSampler."""
        return DocumentSampler()
    
    @pytest.fixture(scope="class")
    def test_data_dir(self):
        """Fixture providing the test data directory."""
        data_dir = Path("tests/results")
        data_dir.mkdir(exist_ok=True, parents=True)
        return data_dir
    
    @pytest.mark.asyncio
    async def test_generate_cpf(self, document_sampler):
        """Test generating CPF document."""
        # Generate a CPF with formatting
        cpf_formatted = await asyncio.to_thread(document_sampler.generate_cpf, True)
        
        # Check format XXX.XXX.XXX-XX
        assert len(cpf_formatted) == 14, f"Formatted CPF '{cpf_formatted}' does not have 14 characters"
        assert cpf_formatted[3] == '.', f"Formatted CPF '{cpf_formatted}' has incorrect format at position 3"
        assert cpf_formatted[7] == '.', f"Formatted CPF '{cpf_formatted}' has incorrect format at position 7"
        assert cpf_formatted[11] == '-', f"Formatted CPF '{cpf_formatted}' has incorrect format at position 11"
        
        # Generate a CPF without formatting
        cpf_unformatted = await asyncio.to_thread(document_sampler.generate_cpf, False)
        
        # Check that it's just 11 digits
        assert len(cpf_unformatted) == 11, f"Unformatted CPF '{cpf_unformatted}' does not have 11 characters"
        assert cpf_unformatted.isdigit(), f"Unformatted CPF '{cpf_unformatted}' is not numeric"
    
    @pytest.mark.asyncio
    async def test_generate_cnpj(self, document_sampler):
        """Test generating CNPJ document."""
        # Generate a CNPJ with formatting
        cnpj_formatted = await asyncio.to_thread(document_sampler.generate_cnpj, True)
        
        # Check format XX.XXX.XXX/XXXX-XX
        assert len(cnpj_formatted) == 18, f"Formatted CNPJ '{cnpj_formatted}' does not have 18 characters"
        assert cnpj_formatted[2] == '.', f"Formatted CNPJ '{cnpj_formatted}' has incorrect format at position 2"
        assert cnpj_formatted[6] == '.', f"Formatted CNPJ '{cnpj_formatted}' has incorrect format at position 6"
        assert cnpj_formatted[10] == '/', f"Formatted CNPJ '{cnpj_formatted}' has incorrect format at position 10"
        assert cnpj_formatted[15] == '-', f"Formatted CNPJ '{cnpj_formatted}' has incorrect format at position 15"
        
        # Generate a CNPJ without formatting
        cnpj_unformatted = await asyncio.to_thread(document_sampler.generate_cnpj, False)
        
        # Check that it's just 14 digits
        assert len(cnpj_unformatted) == 14, f"Unformatted CNPJ '{cnpj_unformatted}' does not have 14 characters"
        assert cnpj_unformatted.isdigit(), f"Unformatted CNPJ '{cnpj_unformatted}' is not numeric"
    
    @pytest.mark.asyncio
    async def test_generate_pis(self, document_sampler):
        """Test generating PIS document."""
        # Generate a PIS with formatting
        pis_formatted = await asyncio.to_thread(document_sampler.generate_pis, True)
        
        # PIS format is XXX.XXXXX.XX-X
        assert len(pis_formatted) == 14, f"Formatted PIS '{pis_formatted}' does not have 14 characters"
        assert pis_formatted[3] == '.', f"Formatted PIS '{pis_formatted}' has incorrect format at position 3"
        assert pis_formatted[9] == '.', f"Formatted PIS '{pis_formatted}' has incorrect format at position 9"
        assert pis_formatted[12] == '-', f"Formatted PIS '{pis_formatted}' has incorrect format at position 12"
        
        # Generate a PIS without formatting
        pis_unformatted = await asyncio.to_thread(document_sampler.generate_pis, False)
        
        # Check that it's just 11 digits
        assert len(pis_unformatted) == 11, f"Unformatted PIS '{pis_unformatted}' does not have 11 characters"
        assert pis_unformatted.isdigit(), f"Unformatted PIS '{pis_unformatted}' is not numeric"
    
    @pytest.mark.asyncio
    async def test_generate_cei(self, document_sampler):
        """Test generating CEI document."""
        # Generate a CEI with formatting
        cei_formatted = await asyncio.to_thread(document_sampler.generate_cei, True)
        
        # CEI format is XX.XXX.XXXXX/XX
        assert len(cei_formatted) == 14, f"Formatted CEI '{cei_formatted}' does not have 14 characters"
        assert cei_formatted[2] == '.', f"Formatted CEI '{cei_formatted}' has incorrect format at position 2"
        assert cei_formatted[6] == '.', f"Formatted CEI '{cei_formatted}' has incorrect format at position 6"
        assert cei_formatted[12] == '/', f"Formatted CEI '{cei_formatted}' has incorrect format at position 12"
        
        # Generate a CEI without formatting
        cei_unformatted = await asyncio.to_thread(document_sampler.generate_cei, False)
        
        # Check that it's just 12 digits
        assert len(cei_unformatted) == 12, f"Unformatted CEI '{cei_unformatted}' does not have 12 characters"
        assert cei_unformatted.isdigit(), f"Unformatted CEI '{cei_unformatted}' is not numeric"
    
    @pytest.mark.asyncio
    async def test_generate_rg(self, document_sampler):
        """Test generating RG document."""
        # Generate an RG with issuer
        rg_with_issuer = await asyncio.to_thread(document_sampler.generate_rg, state="SP", include_issuer=True)
        
        # With issuer, it should return a dictionary
        assert isinstance(rg_with_issuer, dict), f"RG with issuer '{rg_with_issuer}' is not a dictionary"
        assert "rg" in rg_with_issuer, f"RG with issuer missing 'rg' key"
        assert "issuer" in rg_with_issuer, f"RG with issuer missing 'issuer' key"
        
        # Extract the RG number
        rg_number = rg_with_issuer["rg"]
        
        # Check that the RG has the right format (XX.XXX.XXX-X for SP)
        assert '.' in rg_number and '-' in rg_number, f"RG '{rg_number}' does not have SP format"
        
        # Generate an RG without issuer, only_rg=True
        rg_without_issuer = await asyncio.to_thread(document_sampler.generate_rg, state="SP", include_issuer=False, only_rg=True)
        
        # Without issuer and only_rg=True, it should return a string with just the number
        assert isinstance(rg_without_issuer, str), f"RG without issuer '{rg_without_issuer}' is not a string"
    
    @pytest.mark.asyncio
    async def test_generate_documents_uniqueness(self, document_sampler):
        """Test that generated documents are unique."""
        # Generate multiple documents
        cpfs = [await asyncio.to_thread(document_sampler.generate_cpf) for _ in range(10)]
        cnpjs = [await asyncio.to_thread(document_sampler.generate_cnpj) for _ in range(10)]
        pis_numbers = [await asyncio.to_thread(document_sampler.generate_pis) for _ in range(10)]
        
        # Check that all documents are unique
        assert len(set(cpfs)) == len(cpfs), "Generated CPFs are not unique"
        assert len(set(cnpjs)) == len(cnpjs), "Generated CNPJs are not unique"
        assert len(set(pis_numbers)) == len(pis_numbers), "Generated PIS numbers are not unique" 