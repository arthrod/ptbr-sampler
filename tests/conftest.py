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
    """
    Create and ensure the test output directory "tests/results" exists and return its Path.
    
    Returns:
        Path: Path object for the created or existing "tests/results" directory.
    """
    output_dir = Path("tests/results")
    output_dir.mkdir(exist_ok=True, parents=True)
    return output_dir


@pytest.fixture(scope="session")
def data_paths():
    """
    Provide paths to JSON data files used by the sampler.
    
    Returns:
        dict: Mapping of data identifiers to their relative file paths:
            - "json_path": "ptbr_sampler/data/cities_with_ceps.json"
            - "names_path": "ptbr_sampler/data/names_data.json"
            - "middle_names_path": "ptbr_sampler/data/middle_names.json"
            - "surnames_path": "ptbr_sampler/data/surnames_data.json"
            - "locations_path": "ptbr_sampler/data/locations_data.json"
    """
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
    """
    Configure and return the test logger.
    
    Sets the logger to write INFO-level messages to the console and DEBUG-level messages to a rotating file named `test.log` inside `test_output_dir`; existing handlers are removed.
    
    Parameters:
        test_output_dir (Path): Directory where `test.log` will be created.
    
    Returns:
        logger: The configured logger instance.
    """
    log_path = test_output_dir / "test.log"
    
    # Remove all existing handlers
    logger.remove()
    
    # Add console and file handlers
    logger.add(lambda msg: print(msg), level="INFO")
    logger.add(log_path, rotation="10 MB", level="DEBUG")
    
    return logger


@pytest.fixture(scope="session")
def name_data(data_paths):
    """
    Load and return name data from the JSON file specified in `data_paths`.
    
    Parameters:
        data_paths (dict): Mapping containing a `names_path` key with the filesystem path to the names JSON file.
    
    Returns:
        Parsed JSON content (usually a list or dict) from the names file.
    """
    with open(data_paths["names_path"], "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def surname_data(data_paths):
    """
    Load surname data from the configured surnames JSON file.
    
    Parameters:
        data_paths (dict): Mapping of data file paths; expects a `surnames_path` key pointing to the surnames JSON file.
    
    Returns:
        The parsed JSON content from the surnames file.
    """
    with open(data_paths["surnames_path"], "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def location_data(data_paths):
    """
    Load and return JSON-parsed location data from the path specified in `data_paths`.
    
    Parameters:
        data_paths (dict): Mapping that must include the key `"locations_path"` pointing to the locations JSON file path (str or Path).
    
    Returns:
        location_data (Any): The parsed JSON data from the locations file (typically a dict or list).
    """
    with open(data_paths["locations_path"], "r", encoding="utf-8") as f:
        return json.load(f)


# This allows us to use async fixtures with pytest
@pytest.fixture(scope="session")
def event_loop():
    """
    Provide a dedicated asyncio event loop for the test session.
    
    The returned event loop is created fresh and will be closed after the session's tests complete.
    
    Returns:
        loop (asyncio.AbstractEventLoop): Event loop created for the session; closed after use.
    """
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close() 