# PTBr-Sampler Test Suite

This directory contains tests for the `ptbr-sampler` package, ensuring the quality and correctness of the generated Brazilian sample data.

## Tests Overview

### Weighted Distribution Tests

The `test_weighted_distributions.py` script verifies that random sampling functions use proper weighted distributions that match real-world Brazilian population statistics. This is critical for generating realistic sample data.

The test analyzes three key distributions:

1. **First Names Distribution**: Validates that first names are sampled according to their frequency in the Brazilian population
2. **Surnames Distribution**: Ensures surnames appear with frequencies matching actual surname distribution in Brazil
3. **Geographic (States) Distribution**: Confirms that states are sampled proportionally to their population size

#### Visualization

The test produces beautiful visualizations using Brazil's national colors (green and yellow):

- Individual charts for each distribution type
- A summary chart showing correlation coefficients
- Correlation metrics with color-coded evaluation

#### How to Run

```bash
# Run via pytest
pytest tests/test_weighted_distributions.py -v

# Run directly (alternative)
uv run python tests/test_weighted_distributions.py
```

#### Interpreting Results

Results are saved to `tests/results/` and include:
- CSV files with detailed distribution data
- High-resolution plots of the distribution comparisons
- A log file with detailed test information

The test calculates correlation coefficients between expected and observed distributions:

| Correlation | Interpretation |
|-------------|----------------|
| > 0.9       | Excellent - System is working VERY WELL |
| > 0.7       | Good - System is working WELL |
| > 0.5       | Adequate - System is working ADEQUATELY |
| ≤ 0.5       | Poor - System needs IMPROVEMENT |

## Other Tests

(Other test descriptions can be added here as the test suite expands)

## Adding New Tests

When adding new tests, please follow these guidelines:

1. Use meaningful filenames with a `test_` prefix
2. Provide detailed docstrings explaining the test purpose
3. Include assertions that verify the expected behavior
4. For visual tests, use the Brazilian color scheme:
   - Green: `#009c3b`
   - Yellow: `#ffdf00`
   - Blue (accents): `#002776` 