"""
Brazilian Name and Location Generator

This package provides tools for generating realistic Brazilian names and locations
based on population data and historical naming patterns.

Classes:
    TimePeriod: Enum for different historical time periods
    BrazilianNameSampler: Generator for Brazilian names
    BrazilianLocationSampler: Generator for Brazilian locations

The package requires JSON files containing population data and name statistics.
"""

from ptbr_sampler.br_location_class import BrazilianLocationSampler
from ptbr_sampler.br_name_class import BrazilianNameSampler, TimePeriod, NameComponents

# Define the top-level exports of the package
__all__ = [
    'TimePeriod', 
    'NameComponents',
    'BrazilianNameSampler', 
    'BrazilianLocationSampler'
]

__version__ = '1.0.0'

# Define functions to avoid circular imports
def get_cli():
    """
    Retrieve the CLI application and its main callable.
    
    Returns:
        tuple: (app, main) where `app` is the CLI application object and `main` is the callable that runs the CLI.
    """
    from ptbr_sampler.cli import app, main
    return app, main

def run_cli():
    """Run the CLI application directly."""
    app, main = get_cli()
    main()