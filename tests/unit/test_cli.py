"""
Tests for the CLI module.
"""
import pytest
import asyncio
import json
import os
from pathlib import Path
from typing import List, Dict, Any
import tempfile

from ptbr_sampler.cli import (
    write_jsonl,
    read_jsonl,
    validate_output,
    process_config
)


class TestCLI:
    """Test suite for the CLI module functions."""

    @pytest.fixture(scope="class")
    def test_data_dir(self):
        """Fixture providing the test data directory."""
        data_dir = Path("tests/results")
        data_dir.mkdir(exist_ok=True, parents=True)
        return data_dir
    
    @pytest.fixture
    def sample_data(self):
        """Fixture providing sample data for testing."""
        return [
            {
                "person": {
                    "name": "João Silva",
                    "gender": "M",
                    "birthdate": "1985-03-15",
                    "age": 38,
                    "cpf": "123.456.789-00"
                },
                "location": {
                    "city": "São Paulo",
                    "state": "SP",
                    "address": {
                        "street": "Avenida Paulista",
                        "number": "1000",
                        "district": "Bela Vista",
                        "cep": "01310-100"
                    }
                }
            },
            {
                "person": {
                    "name": "Maria Santos",
                    "gender": "F",
                    "birthdate": "1990-07-22",
                    "age": 33,
                    "cpf": "987.654.321-00"
                },
                "location": {
                    "city": "Rio de Janeiro",
                    "state": "RJ",
                    "address": {
                        "street": "Avenida Atlântica",
                        "number": "500",
                        "district": "Copacabana",
                        "cep": "22010-000"
                    }
                }
            }
        ]
    
    @pytest.mark.asyncio
    async def test_write_and_read_jsonl(self, test_data_dir, sample_data):
        """Test writing and reading JSONL files."""
        # Create a temporary file path
        temp_file = test_data_dir / "test_write_read.jsonl"
        
        # Write the sample data to the file
        await asyncio.to_thread(write_jsonl, sample_data, temp_file)
        
        # Check that the file exists
        assert temp_file.exists(), f"Output file {temp_file} was not created"
        
        # Read the data back
        read_data = await asyncio.to_thread(read_jsonl, temp_file)
        
        # Check that the read data matches the original data
        assert len(read_data) == len(sample_data), f"Read data length {len(read_data)} doesn't match original length {len(sample_data)}"
        assert read_data == sample_data, "Read data doesn't match original data"
        
        # Clean up the temporary file
        temp_file.unlink()
    
    @pytest.mark.asyncio
    async def test_validate_output(self, sample_data):
        """Test output validation."""
        # Valid data should pass validation
        is_valid = await asyncio.to_thread(validate_output, sample_data)
        assert is_valid, "Valid data failed validation"
        
        # Invalid data (missing required fields) should fail validation
        invalid_data = [
            {
                "person": {
                    "name": "João Silva",
                    # Missing gender
                    "birthdate": "1985-03-15",
                    "age": 38,
                    "cpf": "123.456.789-00"
                },
                "location": {
                    "city": "São Paulo",
                    "state": "SP",
                    # Missing address
                }
            }
        ]
        
        is_valid = await asyncio.to_thread(validate_output, invalid_data)
        assert not is_valid, "Invalid data passed validation"
    
    @pytest.mark.asyncio
    async def test_process_config(self):
        """Test config processing."""
        # Create a temporary config file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
            config = {
                "qty": 10,
                "state": "SP",
                "gender": "F",
                "min_age": 20,
                "max_age": 40,
                "make_api_call": False,
                "output_file": "test_output.jsonl"
            }
            json.dump(config, temp_file)
            temp_file_path = temp_file.name
        
        # Process the config
        config_args = await asyncio.to_thread(process_config, temp_file_path)
        
        # Check that the config was processed correctly
        assert config_args["qty"] == 10, f"Processed qty {config_args['qty']} doesn't match config"
        assert config_args["state"] == "SP", f"Processed state {config_args['state']} doesn't match config"
        assert config_args["gender"] == "F", f"Processed gender {config_args['gender']} doesn't match config"
        assert config_args["min_age"] == 20, f"Processed min_age {config_args['min_age']} doesn't match config"
        assert config_args["max_age"] == 40, f"Processed max_age {config_args['max_age']} doesn't match config"
        assert config_args["make_api_call"] is False, f"Processed make_api_call {config_args['make_api_call']} doesn't match config"
        assert config_args["output_file"] == "test_output.jsonl", f"Processed output_file {config_args['output_file']} doesn't match config"
        
        # Clean up the temporary file
        os.unlink(temp_file_path) 