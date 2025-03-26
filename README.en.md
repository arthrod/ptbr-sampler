# 🇧🇷 Brazilian Realistic Data Generator

Generate names, addresses, CPFs, CNPJs, and other Brazilian documents that are **proportional to actual population distribution** and based **exclusively on existing, verified data**. Every generated name exists in Brazilian historical records, and locations are sampled proportionally to each region's population.

*Leia aqui em Português: [Português](README.md)*

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Key Features

- 📍 **Location Generation**: Realistic Brazilian addresses with population-weighted sampling
- 👤 **Name Generation**: Historically accurate Brazilian names with period-specific sampling
- 📄 **Document Generation**: Valid Brazilian documents (CPF, RG, PIS, CNPJ, CEI)
- 🎯 **Statistical Accuracy**: Based on real demographic data and historical statistics
- 🔧 **Flexible Output**: Structured data in various formats (CLI, Python dictionaries, API-ready)
- ⚡ **High Performance**: Efficient sampling with pre-calculated weights
- 🧪 **Thoroughly Tested**: Comprehensive test suite for reliability

## 🚀 Perfect For

- 🏢 **Enterprise Applications**: Generate realistic test data for Brazilian market applications
- 🧪 **Testing**: Create diverse datasets for thorough application testing
- 📊 **Data Science**: Generate statistically accurate samples for analysis and modeling
- 🎓 **Education**: Learn about Brazilian document formats and validation rules
- 🔄 **API Development**: Ready-to-use structured data for API responses

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/your-username/ptbr-sampler.git
cd ptbr-sampler

# Install dependencies (recommended to use a virtual environment)
uv sync
```

## 🎯 Quick Start

### Command Line Interface

```bash
# Generate a complete profile (name, location, documents)
uv run ptbr_sampler.cli sample --qty 1

# Generate specific documents only
uv run ptbr_sampler.cli sample --only-cpf --only-rg --qty 3
```

### All CLI Options

#### Basic Options
```bash
--qty, -q                  Number of samples to generate (default: 1)
--all, -a                  Include all possible data in the generated samples
--save-to-jsonl, -sj       Save generated samples to a JSONL file
--append, -ap              Append to JSONL file instead of overwriting (default: True)
--batch, -b                Maximum samples per batch before saving (processes large requests in smaller chunks) (default: 50)
--batch-size, -bs          Number of items to process in each batch (default: 100)
--workers, -w              Number of workers to use for API calls (default: 100)
--easy, -e                 Easy mode with integer qty (enables API calls, all data, and auto-saves)
```

#### Location Options
```bash
--city-only, -c            Return only city names
--state-abbr-only, -sa     Return only state abbreviations
--state-full-only, -sf     Return only full state names
--only-cep, -oc            Return only CEP (postal code)
--cep-without-dash, -nd    Return CEP without dash
--make-api-call, -mac      Make API calls to retrieve real CEP data instead of generating synthetic address data
```

#### Name Options
```bash
--time-period, -t          Time period for name sampling (default: UNTIL_2010)
--return-only-name, -rn    Return only the name without location
--name-raw, -r             Return names in raw format (all caps)
--only-surname, -s         Return only surname
--top-40, -t40             Use only top 40 surnames
--one-surname, -os         Return only one surname instead of two
--always-middle, -am       Always include a middle name
--only-middle, -om         Return only middle name
```

#### Document Options
```bash
--only-document, -od       Return only documents
--always-cpf, -ac          Always include CPF (default: True)
--always-pis, -ap          Always include PIS
--always-cnpj, -acn        Always include CNPJ
--always-cei, -ace         Always include CEI
--always-rg, -ar           Always include RG (default: True)
--always-phone, -aph       Always include phone number (default: True)
--only-cpf, -ocpf          Return only CPF
--only-pis, -op            Return only PIS
--only-cnpj, -ocn          Return only CNPJ
--only-cei, -oce           Return only CEI
--only-rg, -or             Return only RG
--only-fone, -of           Return only phone number
--include-issuer, -ii      Include issuer in RG (default: True)
```

#### Data Source Options
```bash
--json-path, -j            Path to the cities and CEPs data JSON file (default: ptbr_sampler/data/cities_with_ceps.json)
--names-path, -np          Path to the first names data JSON file (default: ptbr_sampler/data/names_data.json)
--middle-names-path, -mnp  Path to the middle names JSON file (default: ptbr_sampler/data/middle_names.json)
--surnames-path, -sp       Path to the surnames JSON file (default: ptbr_sampler/data/surnames_data.json)
--locations-path, -lp      Path to the locations data JSON file (default: ptbr_sampler/data/locations_data.json)
```

### Python API

```python
from ptbr_sampler.br_location_class import BrazilianLocationSampler
from ptbr_sampler.br_name_class import BrazilianNameSampler, TimePeriod
from ptbr_sampler.document_sampler import DocumentSampler

# Initialize samplers
location_sampler = BrazilianLocationSampler("data/cities_with_ceps.json")
name_sampler = BrazilianNameSampler("data/names_data.json",
                                   middle_names_path="data/middle_names.json")
doc_sampler = DocumentSampler()

# Generate data
state_name, state_abbr, city_name = location_sampler.get_state_and_city()
name_components = name_sampler.get_random_name(
    time_period=TimePeriod.UNTIL_2010,
    return_components=True
)

# Get formatted output
result = {
    "name": name_components.first_name,
    "middle_name": name_components.middle_name,
    "surnames": name_components.surname,
    "city": city_name,
    "state": state_name,
    "state_abbr": state_abbr,
    "cep": location_sampler.format_full_location(
        city_name, state_name, state_abbr
    ).split(',')[-1].strip(),
    "cpf": doc_sampler.generate_cpf(),
    "rg": doc_sampler.generate_rg(state_abbr)
}
```

## 🎛️ Features In-Depth

### Location Generation
- Population-weighted selection of states and cities
- Realistic CEP (postal code) generation
- Flexible output formatting
- Support for specific region filtering

### Name Generation
- Historical period-based sampling
- Support for full names, middle names, and surnames
- Case formatting options (title case, uppercase)
- Top 40 surnames list option

### Document Generation
- CPF (Brazilian Individual Taxpayer ID)
- RG (Brazilian ID Card) with state-specific formats
- PIS (Social Integration Program Number)
- CNPJ (Brazilian Company ID)
- CEI (Employer Registration Number)

### Data Output
- Structured dictionary format
- CLI with rich formatting
- Batch generation support
- Customizable output fields

## 📊 Available Datasets

The project uses several carefully prepared datasets to ensure the generation of statistically accurate and realistic data:

### 🏙️ Location Data
- **cities_with_ceps.json** (27MB): Contains detailed information about Brazilian cities, including:
  - City name
  - State (full name and abbreviation)
  - Population
  - Associated postal code ranges
  - Geographic information
  - Data used for population-weighted sampling

- **locations_data.json** (19MB): Expanded dataset with additional location information:
  - Neighborhoods
  - Street names
  - Specific postal codes
  - Complementary information for generating complete addresses

### 👤 Name Data
- **names_data.json** (17MB): Contains Brazilian first names organized by:
  - Historical frequency
  - Time period distribution (from 1930 to 2010)
  - Popularity data for realistic sampling
  
- **middle_names.json** (141KB): Collection of common Brazilian middle names:
  - Names traditionally used as middle names
  - Relative frequencies
  
- **surnames_data.json** (5.5MB): Database of Brazilian surnames:
  - Most common surnames
  - Frequencies and distributions
  - Compound surnames
  - Rules for prefixes (de, da, dos, etc.)

All datasets were compiled from official data and historical records, ensuring high statistical fidelity for generating Brazilian personal data.

## 🏗️ Project Structure

```plaintext
src
├── br_location_class.py         # Location sampling
├── br_name_class.py             # Name sampling
├── br_rg_class.py              # RG generation
├── cli.py                      # Command-line interface
├── document_sampler.py         # Document generation
├── __init__.py                 # Package initialization
└── utils/                      # Utility functions
    ├── cpf.py                  # CPF handling
    ├── pis.py                  # PIS handling
    ├── cnpj.py                 # CNPJ handling
    ├── cei.py                  # CEI handling
    ├── util.py                 # Helper functions
    └── __init__.py
```

## 🧪 Testing

Comprehensive test suite covering all components:

```bash
uv run pytest
```

## 📚 Requirements

- Python 3.9+
- Dependencies:
  - Typer (CLI framework)
  - Rich (Terminal formatting)
  - pytest (Testing)

## 📖 Documentation

Detailed documentation for all features and components:

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Main Features](#main-features)
- [Command Line Interface](#command-line-interface)
- [Data Output](#data-output)
- [Available Datasets](#available-datasets)
- [Testing and Validation](#testing)
- [Installation and Dependencies](#installation)
- [Usage Examples](#quick-start)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
