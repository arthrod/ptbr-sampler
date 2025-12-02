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
        """
        Create and return the test data directory Path, ensuring it exists.
        
        Returns:
            Path: Path to the created or existing 'tests/results' directory.
        """
        data_dir = Path("tests/results")
        data_dir.mkdir(exist_ok=True, parents=True)
        return data_dir
    
    @pytest.fixture
    def sample_data(self):
        """
        Sample dataset of two person/location records used by tests.
        
        Each item is a dictionary with two top-level keys: `person` and `location`. The `person`
        dictionary includes `name`, `gender`, `birthdate`, `age`, and `cpf`. The `location`
        dictionary includes `city`, `state`, and an `address` dictionary with `street`,
        `number`, `district`, and `cep`.
        
        Returns:
            list: Two dictionaries representing sample people and their locations.
        """
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
        """
        Verify that write_jsonl writes a list of records to a JSONL file and that read_jsonl reads them back unchanged.
        
        Parameters:
            test_data_dir (Path): Directory in which a temporary JSONL file will be created.
            sample_data (list[dict]): List of records to write and read back.
        
        Description:
            Creates a temporary JSONL file inside `test_data_dir`, writes `sample_data` using `write_jsonl`,
            asserts the file was created, reads the file back using `read_jsonl`, and asserts the read data
            matches `sample_data`. The temporary file is removed at the end of the test.
        """
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