# Doing Business Codebook

This module loads the World Bank's Doing Business dataset and methodology as Pydantic models. Includes the full methodology and data from the Doing Business website.

## Main Components

### DoingBusiness

The primary class that handles the loading and processing of Doing Business data. It has the following attributes:
- `metadata`: List of metadata for defining variables
- `methodology`: List of methodologies for each category in dataset, taken from the Doing Business website
- `data`: List of data rows containing country-specific information

On deletion, the class saves its contents to a series of JSON files.

### Row

Represents a single row of data from the Doing Business Excel file with attributes:
- `country_code`: ISO 3166-1 alpha-3 country code
- `economy`: Name of the economy (country or territory)
- `region`: Geographical region
- `income_group`: Income classification
- `year`: Year of the data
- `indicators`: Dictionary of indicator names and their values

### Metadata

Represents metadata for an indicator with attributes:
- `python_type`: The Python type of the indicator
- `topic`: The topic/category the indicator belongs to
- `indicator`: Brief definition/display name
- `long_def`: Detailed description of the indicator

### Methodology

Represents methodology for a Doing Business category with attributes:
- `yaml_file_path`: Path to the YAML file containing methodology details
- `name`: Name of the methodology
- `source`: Source URL
- `assumptions`: Dictionary of assumptions for indicators
- `units`: Dictionary of units used for indicators

## Data Processing

The module handles:
1. Loading and validation of Excel data files
2. Processing of methodology YAML files
3. Data type validation for indicators
4. Automatic saving of processed data to JSON files
5. Metadata management and storage

## File Structure

The module expects:
- An Excel file named "Historical-data---COMPLETE-dataset-with-scores.xlsx"
- Methodology YAML files in the 'methodology/categories' directory
- Creates and manages 'data' and 'metadata' directories for processed information

## Dependencies

- openpyxl: For Excel file processing
- pydantic: For data validation and settings management
- PyYAML: For reading methodology files
- Python standard libraries: os, pathlib, typing, hashlib

## Usage

The module is designed to be used as part of a larger system for analyzing business environment data. The main entry point is the `DoingBusiness` class, which automatically processes and validates data upon initialization.

```python
from market_agents.codebook.doing_business import DoingBusiness

# Initialize and load data
doing_business = DoingBusiness()

# Data is automatically processed and saved to JSON files
# Access processed data through the class attributes
metadata = doing_business.metadata
methodology = doing_business.methodology
data = doing_business.data
```

You can also load the data directly once the JSON files are generated. Here's an example:

```python
import json
from pathlib import Path

# Assuming the data directory is in the current working directory
data_dir = Path.cwd() / 'codebook' / 'data' /

# Load data for Afghanistan in 2020
afg_2020_file = data_dir / '2020' / 'AFG_2020.json'

with open(afg_2020_file, 'r') as f:
    afg_2020_data = json.load(f)

# Now you can access the data
print(f"Economy: {afg_2020_data['economy']}")
print(f"Region: {afg_2020_data['region']}")
print(f"Income Group: {afg_2020_data['income_group']}")

# Print some indicator values
for indicator, value in afg_2020_data['indicators'].items():
    print(f"{indicator}: {value}")
```
## Data Validation

The module includes robust validation:
- Indicator type checking against predefined INDICATOR_TYPES
- Required sheet validation in Excel files
- Data cleaning and conversion
- Validation of required fields in data rows

## Auto-saving Feature

The module automatically saves processed data:
- Each row of data is saved as a JSON file in the 'data' directory
- Metadata is saved with hashed identifiers in the 'metadata' directory
