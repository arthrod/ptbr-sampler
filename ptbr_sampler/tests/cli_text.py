import pytest
from rich.table import Table

from ptbr_sampler.cli import create_results_table


def assert_table_row_content(table: Table, expected_rows: list[tuple[str, ...]]) -> None:
    """Helper function to assert table row content matches expected values."""
    actual_rows = []
    for row in table.rows:
        actual_rows.append(tuple(cell.plain for cell in row.cells))
    assert actual_rows == expected_rows, f'\nExpected: {expected_rows}\nGot: {actual_rows}'


@pytest.fixture
def sample_documents() -> list[dict[str, str]]:
    """Fixture providing sample documents for testing."""
    return [{'cpf': '123.456.789-00', 'pis': '123.4567.890-1', 'cnpj': '12.345.678/0001-90', 'cei': '12.345.67890.12'}]


def test_simple_name_formatting():
    """Test basic name formatting with single names."""
    results = ['São Paulo, São Paulo (SP), 01000-000, João Silva']
    table = create_results_table(results=results, title='Test Table', documents=None)
    expected_rows = [('1', 'João', 'Silva', 'São Paulo, São Paulo (SP), 01000-000')]
    assert_table_row_content(table, expected_rows)


def test_compound_first_names():
    """Test handling of compound first names."""
    results = ['São Paulo, São Paulo (SP), 01000-000, José Maria da Silva']
    table = create_results_table(results=results, title='Test Table', documents=None)
    expected_rows = [('1', 'José Maria', 'da Silva', 'São Paulo, São Paulo (SP), 01000-000')]
    assert_table_row_content(table, expected_rows)


def test_compound_surnames():
    """Test handling of compound surnames with various prefixes."""
    test_cases = [
        ('São Paulo, SP, Maria dos Santos Silva', ('1', 'Maria', 'dos Santos Silva', 'São Paulo, SP')),
        ('Rio de Janeiro, RJ, João da Costa e Silva', ('1', 'João', 'da Costa e Silva', 'Rio de Janeiro, RJ')),
        ('Salvador, BA, Pedro de Souza dos Santos', ('1', 'Pedro', 'de Souza dos Santos', 'Salvador, BA')),
    ]

    for result, expected in test_cases:
        table = create_results_table(results=[result], title='Test Table', documents=None)
        assert_table_row_content(table, [expected])


def test_middle_names():
    """Test handling of middle names with surnames."""
    test_cases = [
        ('São Paulo, SP, Maria Helena dos Santos', ('1', 'Maria Helena', 'dos Santos', 'São Paulo, SP')),
        ('Rio de Janeiro, RJ, João Pedro da Silva Santos', ('1', 'João Pedro', 'da Silva Santos', 'Rio de Janeiro, RJ')),
        ('Salvador, BA, Ana Clara de Souza e Silva', ('1', 'Ana Clara', 'de Souza e Silva', 'Salvador, BA')),
    ]

    for result, expected in test_cases:
        table = create_results_table(results=[result], title='Test Table', documents=None)
        assert_table_row_content(table, [expected])


def test_with_documents(sample_documents: list[dict[str, str]]):
    """Test table creation with document information."""
    results = ['São Paulo, SP, Maria da Silva']
    table = create_results_table(results=results, title='Test Table', documents=sample_documents)
    expected_rows = [
        (
            '1',
            'Maria',
            'da Silva',
            'São Paulo, SP',
            'CPF: 123.456.789-00\nPIS: 123.4567.890-1\nCNPJ: 12.345.678/0001-90\nCEI: 12.345.67890.12',
        )
    ]
    assert_table_row_content(table, expected_rows)


def test_only_location():
    """Test table creation with only location information."""
    results = ['São Paulo, São Paulo (SP), 01000-000']
    table = create_results_table(results=results, title='Test Table', only_location=True)
    expected_rows = [('1', 'São Paulo, São Paulo (SP), 01000-000')]
    assert_table_row_content(table, expected_rows)


def test_return_only_name():
    """Test table creation with only name information."""
    results = ['Maria Helena dos Santos Silva']
    table = create_results_table(results=results, title='Test Table', return_only_name=True)
    expected_rows = [('1', 'Maria Helena', 'dos Santos Silva')]
    assert_table_row_content(table, expected_rows)


def test_complex_names():
    """Test handling of complex Brazilian name patterns."""
    test_cases = [
        ('São Paulo, SP, Maria das Graças de Souza e Silva', ('1', 'Maria das Graças', 'de Souza e Silva', 'São Paulo, SP')),
        ("Rio de Janeiro, RJ, João d'Ávila dos Santos", ('1', 'João', "d'Ávila dos Santos", 'Rio de Janeiro, RJ')),
        ('Salvador, BA, Ana Maria da Costa e Silva de Souza', ('1', 'Ana Maria', 'da Costa e Silva de Souza', 'Salvador, BA')),
    ]

    for result, expected in test_cases:
        table = create_results_table(results=[result], title='Test Table', documents=None)
        assert_table_row_content(table, [expected])


def test_edge_cases():
    """Test edge cases and unusual name patterns."""
    test_cases = [
        # Single word name
        ('São Paulo, SP, Maria', ('1', 'Maria', '', 'São Paulo, SP')),
        # Multiple prefixes
        ('Rio de Janeiro, RJ, João da Silva dos Santos', ('1', 'João', 'da Silva dos Santos', 'Rio de Janeiro, RJ')),
        # Very long name
        (
            'Salvador, BA, Maria das Graças de Souza e Silva dos Santos da Costa',
            ('1', 'Maria das Graças', 'de Souza e Silva dos Santos da Costa', 'Salvador, BA'),
        ),
    ]

    for result, expected in test_cases:
        table = create_results_table(results=[result], title='Test Table', documents=None)
        assert_table_row_content(table, [expected])


def test_multiple_rows():
    """Test table creation with multiple rows of data."""
    results = ['São Paulo, SP, João da Silva', 'Rio de Janeiro, RJ, Maria dos Santos', 'Salvador, BA, Pedro de Souza']
    table = create_results_table(results=results, title='Test Table', documents=None)
    expected_rows = [
        ('1', 'João', 'da Silva', 'São Paulo, SP'),
        ('2', 'Maria', 'dos Santos', 'Rio de Janeiro, RJ'),
        ('3', 'Pedro', 'de Souza', 'Salvador, BA'),
    ]
    assert_table_row_content(table, expected_rows)


def test_special_characters():
    """Test handling of names with special characters and accents."""
    test_cases = [
        ('São Paulo, SP, João do Espírito Santo', ('1', 'João', 'do Espírito Santo', 'São Paulo, SP')),
        ("Rio de Janeiro, RJ, María José d'Ávila", ('1', 'María José', "d'Ávila", 'Rio de Janeiro, RJ')),
        ('Salvador, BA, João Baptista da Conceição', ('1', 'João Baptista', 'da Conceição', 'Salvador, BA')),
    ]

    for result, expected in test_cases:
        table = create_results_table(results=[result], title='Test Table', documents=None)
        assert_table_row_content(table, expected)
