"""Tests for the BrazilianNameSampler class."""

import pytest

from ptbr_sampler.name_sampler import SURNAME_PREFIXES, BrazilianNameSampler
from ptbr_sampler.time_period import TimePeriod


@pytest.fixture
def mock_data():
    return {
        'common_names_percentage': {
            'ate1930': {'names': {'MARIA': {'percentage': 0.5}}, 'total': 100},
            'ate1940': {'names': {'JOSE': {'percentage': 0.5}}, 'total': 100},
            'ate1950': {'names': {'JOAO': {'percentage': 0.5}}, 'total': 100},
            'ate1960': {'names': {'ANA': {'percentage': 0.5}}, 'total': 100},
            'ate1970': {'names': {'ANTONIO': {'percentage': 0.5}}, 'total': 100},
            'ate1980': {'names': {'PEDRO': {'percentage': 0.5}}, 'total': 100},
            'ate1990': {'names': {'PAULO': {'percentage': 0.5}}, 'total': 100},
            'ate2000': {'names': {'LUCAS': {'percentage': 0.5}}, 'total': 100},
            'ate2010': {'names': {'MIGUEL': {'percentage': 0.5}}, 'total': 100},
        },
        'surnames': {
            'SILVA': {'percentage': 0.3},
            'SANTOS': {'percentage': 0.2},
            'top_40': {
                'SILVA': {'percentage': 0.5},
                'SANTOS': {'percentage': 0.5},
            },
        },
    }


def test_name_sampler_initialization(mock_data) -> None:
    """Test that sampler initializes correctly with valid data."""
    sampler = BrazilianNameSampler(mock_data)
    assert sampler.name_data is not None
    assert sampler.surname_data is not None
    assert sampler.top_40_surnames is not None


def test_name_sampler_invalid_path() -> None:
    """Test that sampler raises error with invalid file path."""
    with pytest.raises(FileNotFoundError):
        BrazilianNameSampler('invalid_path.json')


def test_name_sampler_missing_data() -> None:
    """Test validation of missing data."""
    with pytest.raises(ValueError, match="Missing 'common_names_percentage' data"):
        BrazilianNameSampler({})

    with pytest.raises(ValueError, match="Missing 'surnames' data"):
        BrazilianNameSampler({'common_names_percentage': {}})


def test_validate_data_structure(mock_data) -> None:
    """Test data structure validation."""
    sampler = BrazilianNameSampler(mock_data)
    sampler._validate_data()  # Should not raise

    # Test invalid period data
    invalid_data = mock_data.copy()
    invalid_data['common_names_percentage']['ate1930'] = {}
    with pytest.raises(ValueError, match='Invalid data structure for period ate1930'):
        BrazilianNameSampler(invalid_data)


def test_apply_prefix() -> None:
    """Test surname prefix application."""
    sampler = BrazilianNameSampler(
        {
            'common_names_percentage': {
                period.value: {'names': {}, 'total': 0}
                for period in TimePeriod
            },
            'surnames': {},
        }
    )

    # Test with known prefix
    for surname, (prefix, _) in SURNAME_PREFIXES.items():
        result = sampler._apply_prefix(surname.title())
        assert result in [f'{prefix} {surname.title()}', surname.title()]

    # Test with unknown surname
    result = sampler._apply_prefix('Unknown')
    assert result == 'Unknown'


def test_random_name_generation(mock_data) -> None:
    """Test basic name generation."""
    sampler = BrazilianNameSampler(mock_data)
    name = sampler.get_random_name()
    assert isinstance(name, str)
    assert len(name) > 0
    assert name.istitle()  # Should be title case by default


def test_random_name_with_period(test_data) -> None:
    """Test name generation for specific time period."""
    sampler = BrazilianNameSampler(test_data)
    name = sampler.get_random_name(time_period=TimePeriod.UNTIL_2010)
    assert isinstance(name, str)
    assert len(name) > 0


def test_random_surname(test_data) -> None:
    """Test surname generation."""
    sampler = BrazilianNameSampler(test_data)
    surname = sampler.get_random_surname()
    assert isinstance(surname, str)
    assert len(surname) > 0
    assert ' ' in surname  # Should have two surnames by default


def test_single_surname(test_data) -> None:
    """Test single surname generation."""
    sampler = BrazilianNameSampler(test_data)
    surname = sampler.get_random_surname(with_only_one_surname=True)
    assert isinstance(surname, str)
    assert len(surname) > 0


def test_top_40_surname(test_data) -> None:
    """Test top 40 surname generation."""
    sampler = BrazilianNameSampler(test_data)
    surname = sampler.get_random_surname(top_40=True)
    assert isinstance(surname, str)
    assert len(surname) > 0


def test_raw_name_format(test_data) -> None:
    """Test raw name format."""
    sampler = BrazilianNameSampler(test_data)
    name = sampler.get_random_name(raw=True)
    assert name.isupper()
