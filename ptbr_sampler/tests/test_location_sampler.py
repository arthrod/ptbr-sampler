"""Tests for the BrazilianLocationSampler class."""

import pytest

from ptbr_sampler.location_sampler import BrazilianLocationSampler
from ptbr_sampler.time_period import TimePeriod


@pytest.fixture
def mock_location_data():
    return {
        'common_names_percentage': {
            period.value: {'names': {'TEST': {'percentage': 1.0}}, 'total': 1}
            for period in TimePeriod
        },
        'states': {
            'São Paulo': {
                'state_abbr': 'SP',
                'population_percentage': 0.6,
            },
            'Rio de Janeiro': {
                'state_abbr': 'RJ',
                'population_percentage': 0.4,
            },
        },
        'cities': {
            'São Paulo': {
                'city_uf': 'SP',
                'population_percentage_state': 0.5,
                'cep_starts': '01000-000',
                'cep_ends': '05999-999',
                'cep_starts_two': '08000-000',
                'cep_ends_two': '08499-999',
            },
            'Campinas': {
                'city_uf': 'SP',
                'population_percentage_state': 0.5,
                'cep_starts': '13000-000',
                'cep_ends': '13139-999',
            },
            'Rio de Janeiro': {
                'city_uf': 'RJ',
                'population_percentage_state': 1.0,
                'cep_starts': '20000-000',
                'cep_ends': '23799-999',
            },
        },
    }


def test_location_sampler_initialization(mock_location_data) -> None:
    """Test sampler initialization."""
    sampler = BrazilianLocationSampler(mock_location_data)
    assert sampler.data == mock_location_data
    assert len(sampler.state_weights) == 2
    assert len(sampler.city_weights_by_state) == 2


def test_get_state(mock_location_data) -> None:
    """Test state generation."""
    sampler = BrazilianLocationSampler(mock_location_data)
    state_name, state_abbr = sampler.get_state()
    assert state_name in ['São Paulo', 'Rio de Janeiro']
    assert state_abbr in ['SP', 'RJ']


def test_get_city(mock_location_data) -> None:
    """Test city generation."""
    sampler = BrazilianLocationSampler(mock_location_data)

    # Test with specific state
    city_name, state_abbr = sampler.get_city('SP')
    assert city_name in ['São Paulo', 'Campinas']
    assert state_abbr == 'SP'

    # Test with random state
    city_name, state_abbr = sampler.get_city()
    assert city_name in ['São Paulo', 'Campinas', 'Rio de Janeiro']
    assert state_abbr in ['SP', 'RJ']


def test_get_state_and_city(mock_location_data) -> None:
    """Test combined state and city generation."""
    sampler = BrazilianLocationSampler(mock_location_data)
    state_name, state_abbr, city_name = sampler.get_state_and_city()
    assert state_name in ['São Paulo', 'Rio de Janeiro']
    assert state_abbr in ['SP', 'RJ']
    assert city_name in ['São Paulo', 'Campinas', 'Rio de Janeiro']


def test_cep_formatting(mock_location_data) -> None:
    """Test CEP formatting."""
    sampler = BrazilianLocationSampler(mock_location_data)

    # Test with dash
    cep = sampler._format_cep(12345678)
    assert len(cep) == 9
    assert cep[5] == '-'

    # Test without dash
    cep = sampler._format_cep(12345678, with_dash=False)
    assert len(cep) == 8
    assert '-' not in cep


def test_random_cep_generation(mock_location_data) -> None:
    """Test random CEP generation for cities."""
    sampler = BrazilianLocationSampler(mock_location_data)

    # Test regular city
    cep = sampler._get_random_cep_for_city('Campinas')
    assert 13000000 <= cep <= 13139999

    # Test city with two ranges
    cep = sampler._get_random_cep_for_city('São Paulo')
    assert (1000000 <= cep <= 5999999) or (8000000 <= cep <= 8499999)


def test_full_location_format(mock_location_data) -> None:
    """Test location string formatting."""
    sampler = BrazilianLocationSampler(mock_location_data)

    # Test basic format
    location = sampler.format_full_location('São Paulo', 'São Paulo', 'SP')
    assert 'São Paulo, São Paulo (SP)' in location
    assert len(location.split(',')) >= 2  # Should have city, state, and CEP

    # Test without parentheses
    location = sampler.format_full_location('São Paulo', 'São Paulo', 'SP', no_parenthesis=True)
    assert 'São Paulo, São Paulo SP' in location
    assert '(' not in location
    assert ')' not in location


def test_random_location_options(mock_location_data) -> None:
    """Test random location generation with various options."""
    sampler = BrazilianLocationSampler(mock_location_data)

    # Test city only
    location = sampler.get_random_location(city_only=True)
    assert location in ['São Paulo', 'Campinas', 'Rio de Janeiro']

    # Test state abbreviation only
    location = sampler.get_random_location(state_abbr_only=True)
    assert location in ['SP', 'RJ']

    # Test state full name only
    location = sampler.get_random_location(state_full_only=True)
    assert location in ['São Paulo', 'Rio de Janeiro']

    # Test CEP only
    location = sampler.get_random_location(only_cep=True)
    assert len(location) == 9
    assert '-' in location

    # Test CEP without dash
    location = sampler.get_random_location(only_cep=True, cep_without_dash=True)
    assert len(location) == 8
    assert '-' not in location
