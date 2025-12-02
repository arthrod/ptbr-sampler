"""
Pytest configuration file with common fixtures for the ptbr-sampler test suite.
"""

import pytest
import asyncio
from pathlib import Path
import json
from loguru import logger


@pytest.fixture(scope="session")
def test_output_dir():
    """Fixture providing the test output directory."""
    output_dir = Path("tests/results")
    output_dir.mkdir(exist_ok=True, parents=True)
    return output_dir


@pytest.fixture(scope="session")
def data_paths():
    """Fixture providing the paths to the data files used by the sampler."""
    return {
        "json_path": "ptbr_sampler/data/cities_with_ceps.json",
        "names_path": "ptbr_sampler/data/names_data.json",
        "middle_names_path": "ptbr_sampler/data/middle_names.json",
        "surnames_path": "ptbr_sampler/data/surnames_data.json",
        "locations_path": "ptbr_sampler/data/locations_data.json"
    }


@pytest.fixture(scope="session")
def brazil_colors():
    """Fixture providing the Brazilian flag colors for visualization."""
    return {
        "green": "#009c3b",
        "yellow": "#ffdf00",
        "blue": "#002776"
    }


@pytest.fixture
def configure_logger(test_output_dir):
    """Configure logger for tests."""
    log_path = test_output_dir / "test.log"
    
    # Remove all existing handlers
    logger.remove()
    
    # Add console and file handlers
    logger.add(lambda msg: print(msg), level="INFO")
    logger.add(log_path, rotation="10 MB", level="DEBUG")
    
    return logger


@pytest.fixture(scope="session")
def name_data(data_paths):
    """Load name data from JSON file."""
    with open(data_paths["names_path"], "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def surname_data(data_paths):
    """Load surname data from JSON file."""
    with open(data_paths["surnames_path"], "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def location_data(data_paths):
    """Load location data from JSON file."""
    with open(data_paths["locations_path"], "r", encoding="utf-8") as f:
        return json.load(f)


# This allows us to use async fixtures with pytest
@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the entire test session."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close() 