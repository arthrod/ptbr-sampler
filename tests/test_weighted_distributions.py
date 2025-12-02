#!/usr/bin/env python
"""
Test Weighted Distributions in ptbr_sampler

This module provides tests to verify that the random sampling functions
in ptbr_sampler use proper weighted distributions that match expected 
frequency distributions from the real-world Brazilian population.

It tests three key elements:
1. First names distribution
2. Surnames distribution 
3. Geographic (states) distribution

The results are visualized using Brazil's national colors (green and yellow)
and statistically analyzed with correlation coefficients.
"""

import asyncio
import json
from collections import Counter
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from loguru import logger
import pandas as pd
import seaborn as sns
import pytest

# Brazilian national colors (for plots)
BRAZIL_GREEN = '#009c3b'  # Green
BRAZIL_YELLOW = '#ffdf00'  # Yellow
BRAZIL_BLUE = '#002776'   # Blue (for text and accents)

# Import necessary samplers
from ptbr_sampler.br_name_class import BrazilianNameSampler, TimePeriod
from ptbr_sampler.br_location_class import BrazilianLocationSampler
from ptbr_sampler.sampler import sample


async def generate_test_samples(sample_size=5000):
    """Generate test samples without API calls for statistical analysis.
    
    Args:
        sample_size: Number of samples to generate (default: 5000)
        
    Returns:
        List of generated sample items
    """
    logger.info(f"Generating {sample_size} samples for statistical testing...")
    
    # Call the sampler without API calls (faster for testing)
    samples = await sample(
        qty=sample_size,
        make_api_call=False,  # No API calls
        all_data=True,        # Include all data fields
        batch_size=100,
        num_workers=100,
        # Specify correct data file paths
        json_path="ptbr_sampler/data/cities_with_ceps.json",
        names_path="ptbr_sampler/data/names_data.json",
        middle_names_path="ptbr_sampler/data/middle_names.json",
        surnames_path="ptbr_sampler/data/surnames_data.json",
        locations_path="ptbr_sampler/data/locations_data.json"
    )
    
    logger.info(f"Generated {len(samples)} samples successfully")
    return samples


def analyze_name_distribution(samples, top_n=20):
    """Analyze the distribution of first names and compare to expected weights.
    
    Args:
        samples: List of sample items to analyze
        top_n: Number of top names to analyze
        
    Returns:
        DataFrame with name distribution comparison
    """
    logger.info("Analyzing first name distribution...")
    
    # Count the frequency of first names
    first_names = Counter([item.name for item in samples])
    total_count = len(samples)
    
    # Calculate observed percentages
    observed_percentages = {name: count/total_count * 100 for name, count in first_names.items()}
    
    # Load expected weights from data file
    name_data_path = Path("ptbr_sampler/data/names_data.json")
    with name_data_path.open(encoding='utf-8') as f:
        name_data = json.load(f)
    
    # Get expected weights from the UNTIL_2010 period (most recent)
    expected_percentages = {}
    time_period = TimePeriod.UNTIL_2010.value  # 'ate2010'
    for name, info in name_data['common_names_percentage'][time_period]['names'].items():
        expected_percentages[name] = info['percentage'] * 100  # Multiply by 100 to get percentage
    
    # Create DataFrame for comparison (top_n most frequent)
    top_names = [name for name, _ in first_names.most_common(top_n)]
    comparison_data = []
    
    for name in top_names:
        comparison_data.append({
            'Name': name,
            'Observed (%)': observed_percentages.get(name, 0),
            'Expected (%)': expected_percentages.get(name, 0)
        })
    
    df = pd.DataFrame(comparison_data)
    return df


def analyze_surname_distribution(samples, top_n=20):
    """Analyze the distribution of surnames and compare to expected weights.
    
    Args:
        samples: List of sample items to analyze
        top_n: Number of top surnames to analyze
        
    Returns:
        DataFrame with surname distribution comparison
    """
    logger.info("Analyzing surname distribution...")
    
    # Extract all surname components for better analysis
    all_surnames = []
    
    # Common prefixes in Brazilian surnames
    prefixes = ['da', 'de', 'do', 'das', 'dos', 'e']
    
    for item in samples:
        if not item.surnames:
            continue
            
        # Split full surname into components
        surname_parts = item.surnames.split()
        
        # Process each part of the surname
        i = 0
        while i < len(surname_parts):
            # Check if current part is a prefix
            if i < len(surname_parts) - 1 and surname_parts[i].lower() in prefixes:
                # Combine prefix with the actual surname (e.g., "da Silva" -> "Silva")
                i += 1  # Skip the prefix
            
            # Add the actual surname component to our list
            if i < len(surname_parts):
                all_surnames.append(surname_parts[i])
            i += 1
    
    # Count frequency
    surname_counts = Counter(all_surnames)
    total_count = len(all_surnames)
    
    # Calculate observed percentages
    observed_percentages = {surname: count/total_count * 100 for surname, count in surname_counts.items()}
    
    # Load expected weights from data file
    surname_data_path = Path("ptbr_sampler/data/surnames_data.json")
    with surname_data_path.open(encoding='utf-8') as f:
        surname_data = json.load(f)
    
    # Get expected weights - values are already percentages, no need to multiply by 100
    expected_percentages = {}
    for surname, info in surname_data['surnames'].items():
        if surname != 'top_40':  # Skip the top_40 nested dictionary
            expected_percentages[surname] = info['percentage']  # Already a percentage
    
    # Create DataFrame for comparison (top_n most frequent)
    top_surnames = [surname for surname, _ in surname_counts.most_common(top_n)]
    comparison_data = []
    
    for surname in top_surnames:
        comparison_data.append({
            'Surname': surname,
            'Observed (%)': observed_percentages.get(surname, 0),
            'Expected (%)': expected_percentages.get(surname, 0)
        })
    
    df = pd.DataFrame(comparison_data)
    return df


def analyze_state_distribution(samples):
    """Analyze the distribution of states and compare to expected weights.
    
    Args:
        samples: List of sample items to analyze
        
    Returns:
        DataFrame with state distribution comparison
    """
    logger.info("Analyzing state distribution...")
    
    # Count frequency of states
    states = Counter([item.state for item in samples])
    total_count = len(samples)
    
    # Calculate observed percentages
    observed_percentages = {state: count/total_count * 100 for state, count in states.items()}
    
    # Load expected weights from data file
    location_data_path = Path("ptbr_sampler/data/locations_data.json")
    with location_data_path.open(encoding='utf-8') as f:
        location_data = json.load(f)
    
    # Get expected weights - need to multiply by 100 as they're stored as decimals (e.g., 0.08)
    expected_percentages = {}
    for state, info in location_data['states'].items():
        expected_percentages[state] = info['population_percentage'] * 100
    
    # Create DataFrame for comparison
    comparison_data = []
    
    for state in observed_percentages.keys():
        comparison_data.append({
            'State': state,
            'Observed (%)': observed_percentages.get(state, 0),
            'Expected (%)': expected_percentages.get(state, 0)
        })
    
    df = pd.DataFrame(comparison_data)
    return df.sort_values(by='Expected (%)', ascending=False)


def plot_comparison_brazil_colors(df, title, x_column, output_dir=None, figsize=(12, 8)):
    """Plot comparison between observed and expected percentages using Brazil's colors.
    
    Args:
        df: DataFrame with the distribution data
        title: Title for the plot
        x_column: Column to use for x-axis labels
        output_dir: Directory to save the plot (default: tests/results)
        figsize: Size of the figure (width, height) in inches
    
    Returns:
        Correlation coefficient between observed and expected values
    """
    plt.figure(figsize=figsize)
    plt.style.use('seaborn-v0_8-whitegrid')
    
    x = np.arange(len(df))
    width = 0.35
    
    # Use Brazilian flag colors (green and yellow)
    plt.bar(x - width/2, df['Observed (%)'], width, label='Observed', color=BRAZIL_GREEN, alpha=0.9)
    plt.bar(x + width/2, df['Expected (%)'], width, label='Expected', color=BRAZIL_YELLOW, alpha=0.9)
    
    plt.xlabel('Item', fontsize=12, color=BRAZIL_BLUE)
    plt.ylabel('Percentage (%)', fontsize=12, color=BRAZIL_BLUE)
    plt.title(title, fontsize=14, fontweight='bold', color=BRAZIL_BLUE)
    plt.xticks(x, df[x_column], rotation=45, ha='right', fontsize=10)
    plt.legend(frameon=True, facecolor='white', edgecolor=BRAZIL_BLUE)
    plt.grid(axis='y', alpha=0.3)
    
    # Calculate correlation
    correlation = df['Observed (%)'].corr(df['Expected (%)'])
    
    # Add correlation text with color based on strength
    if correlation > 0.9:
        corr_color = 'darkgreen'
    elif correlation > 0.7:
        corr_color = 'green'
    elif correlation > 0.5:
        corr_color = 'orange'
    else:
        corr_color = 'red'
        
    plt.figtext(0.5, 0.01, f"Correlation: {correlation:.4f}", 
                ha='center', fontsize=12, fontweight='bold', color=corr_color)
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.97])
    
    # Create output directory if it doesn't exist
    if output_dir is None:
        output_dir = Path("tests/results")
    else:
        output_dir = Path(output_dir)
        
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Save the plot
    filename = title.lower().replace(" ", "_") + ".png"
    plt.savefig(output_dir / filename, dpi=300)
    logger.info(f"Saved plot to {output_dir / filename}")
    
    return correlation


def create_summary_plot(correlations, output_dir=None):
    """Create a summary plot of all correlations.
    
    Args:
        correlations: Dictionary of correlation values
        output_dir: Directory to save the plot
    """
    categories = list(correlations.keys())
    values = [correlations[cat] for cat in categories]
    
    plt.figure(figsize=(10, 6))
    plt.style.use('seaborn-v0_8-whitegrid')
    
    # Create bars with conditional coloring
    colors = [BRAZIL_GREEN if v > 0.7 else BRAZIL_YELLOW for v in values]
    
    bars = plt.bar(categories, values, color=colors, alpha=0.85)
    
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., 1.002*height,
                f'{height:.4f}', ha='center', fontsize=11, fontweight='bold')
    
    plt.ylim(0, 1.1)
    plt.axhline(y=0.9, color='green', linestyle='--', alpha=0.7, label='Excellent (0.9+)')
    plt.axhline(y=0.7, color='orange', linestyle='--', alpha=0.7, label='Good (0.7+)')
    plt.axhline(y=0.5, color='red', linestyle='--', alpha=0.7, label='Adequate (0.5+)')
    
    plt.title('Weighted Distribution Correlation Summary', fontsize=14, fontweight='bold', color=BRAZIL_BLUE)
    plt.ylabel('Correlation Coefficient', fontsize=12, color=BRAZIL_BLUE)
    plt.grid(axis='y', alpha=0.3)
    plt.legend(frameon=True, facecolor='white', edgecolor=BRAZIL_BLUE)
    
    # Calculate average
    avg = sum(values) / len(values)
    avg_text = f"Average Correlation: {avg:.4f}"
    
    if avg > 0.9:
        status = "VERY WELL"
        color = 'darkgreen'
    elif avg > 0.7:
        status = "WELL"
        color = 'green'
    elif avg > 0.5:
        status = "ADEQUATELY"
        color = 'orange'
    else:
        status = "NEEDS IMPROVEMENT"
        color = 'red'
    
    plt.figtext(0.5, 0.01, f"{avg_text} - Weighting system is working {status}", 
                ha='center', fontsize=12, fontweight='bold', color=color)
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.97])
    
    # Create output directory if it doesn't exist
    if output_dir is None:
        output_dir = Path("tests/results")
    else:
        output_dir = Path(output_dir)
        
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Save the plot
    filename = "correlation_summary.png"
    plt.savefig(output_dir / filename, dpi=300)
    logger.info(f"Saved summary plot to {output_dir / filename}")


@pytest.mark.asyncio
async def test_weighted_distributions(sample_size=5000):
    """
    Test if the weighted distributions match expected percentages.
    
    This comprehensive test verifies that names, surnames, and geographic
    locations are being generated with proper weighted random selection
    that matches real-world frequency distributions.
    
    Args:
        sample_size: Number of samples to generate for testing
    """
    # Configure logger
    log_file = Path("tests/results/weighted_test.log")
    log_file.parent.mkdir(exist_ok=True, parents=True)
    
    logger.remove()
    logger.add(lambda msg: print(msg), level="INFO")
    logger.add(log_file, rotation="10 MB", level="DEBUG")
    
    # Generate test samples
    logger.info(f"Starting weighted distribution test with sample size of {sample_size}")
    samples = await generate_test_samples(sample_size)
    
    # Analyze distributions
    name_df = analyze_name_distribution(samples)
    surname_df = analyze_surname_distribution(samples)
    state_df = analyze_state_distribution(samples)
    
    # Save results to CSV
    output_dir = Path("tests/results")
    output_dir.mkdir(exist_ok=True, parents=True)
    
    name_df.to_csv(output_dir / "name_distribution.csv", index=False)
    surname_df.to_csv(output_dir / "surname_distribution.csv", index=False)
    state_df.to_csv(output_dir / "state_distribution.csv", index=False)
    
    # Plot comparisons with Brazil's colors
    name_corr = plot_comparison_brazil_colors(name_df, "First Name Distribution", "Name", output_dir)
    surname_corr = plot_comparison_brazil_colors(surname_df, "Surname Distribution", "Surname", output_dir)
    state_corr = plot_comparison_brazil_colors(state_df, "State Distribution", "State", output_dir)
    
    # Create summary dictionary
    correlations = {
        "First Names": name_corr,
        "Surnames": surname_corr,
        "States": state_corr
    }
    
    # Create summary plot
    create_summary_plot(correlations, output_dir)
    
    # Calculate average correlation
    avg_corr = sum(correlations.values()) / len(correlations)
    
    # Log results
    logger.info(f"Correlation between observed and expected frequencies:")
    logger.info(f"First Names: {name_corr:.4f}")
    logger.info(f"Surnames: {surname_corr:.4f}")
    logger.info(f"States: {state_corr:.4f}")
    logger.info(f"Average Correlation: {avg_corr:.4f}")
    
    if avg_corr > 0.9:
        logger.info("Weighting system is working VERY WELL")
    elif avg_corr > 0.7:
        logger.info("Weighting system is working WELL")
    elif avg_corr > 0.5:
        logger.info("Weighting system is working ADEQUATELY")
    else:
        logger.info("Weighting system needs IMPROVEMENT")
    
    # Assert tests pass with good correlation values
    assert name_corr > 0.7, f"Name distribution correlation ({name_corr:.4f}) is too low"
    assert surname_corr > 0.7, f"Surname distribution correlation ({surname_corr:.4f}) is too low"
    assert state_corr > 0.7, f"State distribution correlation ({state_corr:.4f}) is too low"
    assert avg_corr > 0.7, f"Average correlation ({avg_corr:.4f}) is too low"


if __name__ == "__main__":
    # Allow running as a script for manual testing
    asyncio.run(test_weighted_distributions()) 