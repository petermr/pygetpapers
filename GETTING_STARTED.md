# Pygetpapers Getting Started Guide

Welcome to pygetpapers! This guide will help you get started with downloading and managing scientific papers from various repositories.

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Repository Examples](#repository-examples)
4. [Output Formats](#output-formats)
5. [Advanced Features](#advanced-features)
6. [Troubleshooting](#troubleshooting)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Windows Installation

```bash
# Install Python from https://python.org if not already installed
# Open Command Prompt or PowerShell

# Clone the repository
git clone https://github.com/pygetpapers/pygetpapers.git
cd pygetpapers

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install pygetpapers
pip install -e .
```

### macOS Installation

```bash
# Install Python using Homebrew (if not already installed)
brew install python

# Clone the repository
git clone https://github.com/pygetpapers/pygetpapers.git
cd pygetpapers

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install pygetpapers
pip install -e .
```

### Linux/Unix Installation

```bash
# Install Python (Ubuntu/Debian)
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Or for CentOS/RHEL/Fedora
sudo yum install python3 python3-pip
# or
sudo dnf install python3 python3-pip

# Clone the repository
git clone https://github.com/pygetpapers/pygetpapers.git
cd pygetpapers

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install pygetpapers
pip install -e .
```

### Optional Dependencies

For enhanced functionality, install additional dependencies:

```bash
# For datatables support
pip install datatables-module

# For Selenium-based scraping (Redalyc)
pip install selenium webdriver-manager

# For enhanced HTML processing
pip install beautifulsoup4 lxml
```

## Quick Start

### Basic Usage

```bash
# Search for papers (default: Europe PMC)
pygetpapers --query "artificial intelligence" --limit 10

# Search with specific repository
pygetpapers --api europe_pmc --query "machine learning" --limit 10

# Generate CSV output
pygetpapers --api europe_pmc --query "bioinformatics" --limit 10 --makecsv

# Generate interactive datatables
pygetpapers --api europe_pmc --query "genomics" --limit 10 --datatables
```

### Output Location

By default, pygetpapers saves all output to `$HOME/pygetpapers/` with timestamped directories:

- **Windows**: `C:\Users\YourUsername\pygetpapers\`
- **macOS**: `/Users/YourUsername/pygetpapers/`
- **Linux**: `/home/YourUsername/pygetpapers/`

You can specify a custom output directory:

```bash
pygetpapers --query "climate change" --limit 10 --output /path/to/custom/directory
```

## Repository Examples

### 1. Europe PMC (Default)

Europe PMC provides access to life sciences literature.

```bash
# Basic search
pygetpapers --api europe_pmc --query "cancer immunotherapy" --limit 10

# Search with date range
pygetpapers --api europe_pmc --query "COVID-19" --startdate 2023-01-01 --enddate 2023-12-31 --limit 10

# Download full-text XML
pygetpapers --api europe_pmc --query "genomics" --limit 10 --xml

# Download PDFs (if available)
pygetpapers --api europe_pmc --query "bioinformatics" --limit 10 --pdf

# Generate CSV and datatables
pygetpapers --api europe_pmc --query "machine learning biology" --limit 10 --makecsv --datatables

# Search with synonyms
pygetpapers --api europe_pmc --query "DNA sequencing" --limit 10 --synonym
```

### 2. bioRxiv

Preprint server for biology research.

```bash
# Basic search
pygetpapers --api biorxiv --query "cancer research" --limit 10

# Search by date range
pygetpapers --api biorxiv --query "2023-01-01/2023-06-30" --limit 10

# Download full-text HTML
pygetpapers --api biorxiv --query "genomics" --limit 10 --makehtml

# Generate datatables
pygetpapers --api biorxiv --query "immunology" --limit 10 --datatables
```

### 3. medRxiv

Preprint server for medical research.

```bash
# Basic search
pygetpapers --api medrxiv --query "COVID-19 treatment" --limit 10

# Search by date
pygetpapers --api medrxiv --query "2023-07-01/2023-12-31" --limit 10

# Generate CSV output
pygetpapers --api medrxiv --query "vaccine development" --limit 10 --makecsv
```

### 4. Crossref

Academic publishing metadata.

```bash
# Basic search
pygetpapers --api crossref --query "artificial intelligence" --limit 10

# Search with filters
pygetpapers --api crossref --query "machine learning" --limit 10 --filter "type:journal-article"

# Generate datatables
pygetpapers --api crossref --query "data science" --limit 10 --datatables
```

### 5. OpenAlex

Academic knowledge graph.

```bash
# Basic search
pygetpapers --api openalex --query "climate change" --limit 10

# Generate CSV output
pygetpapers --api openalex --query "renewable energy" --limit 10 --makecsv

# Generate datatables
pygetpapers --api openalex --query "sustainability" --limit 10 --datatables
```

### 6. Redalyc (Selenium-based)

Latin American scientific journals.

```bash
# Basic search (requires Selenium)
pygetpapers --api redalyc_selenium --query "biodiversity" --limit 10

# Generate datatables
pygetpapers --api redalyc_selenium --query "conservation" --limit 10 --datatables

# Download HTML files
pygetpapers --api redalyc_selenium --query "ecology" --limit 10 --makehtml
```

## Output Formats

### 1. JSON Metadata

Default format containing paper metadata:

```bash
pygetpapers --api europe_pmc --query "bioinformatics" --limit 10
# Creates: eupmc_results.json
```

### 2. CSV Output

Comma-separated values for spreadsheet applications:

```bash
pygetpapers --api europe_pmc --query "genomics" --limit 10 --makecsv
# Creates: europe_pmc.csv
```

### 3. HTML Tables

Static HTML tables for web viewing:

```bash
pygetpapers --api europe_pmc --query "machine learning" --limit 10 --makehtml
# Creates: europe_pmc.html
```

### 4. Interactive Datatables

Advanced interactive HTML tables with search, sort, and pagination:

```bash
pygetpapers --api europe_pmc --query "artificial intelligence" --limit 10 --datatables
# Creates: datatables.html, datatables_papers.html, datatables_metadata.html, datatables_summary.html
```

### 5. Full-text Downloads

Download complete paper content:

```bash
# XML full-text (Europe PMC, bioRxiv, medRxiv)
pygetpapers --api europe_pmc --query "cancer research" --limit 10 --xml

# PDF downloads (where available)
pygetpapers --api europe_pmc --query "bioinformatics" --limit 10 --pdf

# Supplementary files (Europe PMC only)
pygetpapers --api europe_pmc --query "genomics" --limit 10 --supp
```

## Advanced Features

### Date Range Queries

```bash
# Search papers published between dates
pygetpapers --api europe_pmc --query "COVID-19" --startdate 2023-01-01 --enddate 2023-12-31 --limit 10

# Search bioRxiv preprints by date
pygetpapers --api biorxiv --query "2023-06-01/2023-12-31" --limit 10
```

### Term-based Queries

Create a file `terms.txt` with comma-separated terms:

```
machine learning, artificial intelligence, deep learning
```

```bash
# Search with OR logic between terms
pygetpapers --api europe_pmc --query "biology" --terms terms.txt --limit 10

# Exclude specific terms
pygetpapers --api europe_pmc --query "cancer" --notterms exclude_terms.txt --limit 10
```

### Update Existing Corpora

```bash
# Update existing search results
pygetpapers --api europe_pmc --query "bioinformatics" --limit 10 --update

# Restart failed downloads
pygetpapers --api europe_pmc --query "genomics" --limit 10 --restart
```

### HTML Processing

```bash
# Convert XML to HTML
pygetpapers --api europe_pmc --query "cancer" --limit 10 --xml --fulltext_html

# Process existing HTML files
pygetpapers --convert_html /path/to/corpus

# Enhance HTML with better structure
pygetpapers --enhance_html /path/to/corpus
```

### Logging and Debugging

```bash
# Set log level
pygetpapers --api europe_pmc --query "test" --limit 5 --loglevel debug

# Save logs to file
pygetpapers --api europe_pmc --query "test" --limit 5 --logfile search.log

# Check version
pygetpapers --version
```

## Troubleshooting

### Common Issues

#### 1. Import Errors

```bash
# If you get import errors, ensure you're in the virtual environment
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

#### 2. Selenium Issues (Redalyc)

```bash
# Install Chrome WebDriver
pip install webdriver-manager

# For headless operation, ensure Chrome is installed
# On Ubuntu/Debian:
sudo apt install chromium-browser

# On macOS:
brew install --cask google-chrome
```

#### 3. Permission Errors

```bash
# Ensure write permissions to output directory
chmod 755 ~/pygetpapers

# Or specify a different output directory
pygetpapers --query "test" --limit 5 --output /tmp/test_output
```

#### 4. Network Issues

```bash
# Use proxy if behind firewall
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080

# Or use different log level for debugging
pygetpapers --api europe_pmc --query "test" --limit 5 --loglevel debug
```

### Getting Help

```bash
# Show help
pygetpapers --help

# Show help for specific options
pygetpapers --help | grep -A 5 -B 5 "datatables"
```

### Example Workflows

#### Complete Research Workflow

```bash
# 1. Search for papers
pygetpapers --api europe_pmc --query "cancer immunotherapy" --limit 50 --makecsv

# 2. Generate interactive datatables
pygetpapers --api europe_pmc --query "cancer immunotherapy" --limit 50 --datatables

# 3. Download full-text XML
pygetpapers --api europe_pmc --query "cancer immunotherapy" --limit 50 --xml

# 4. Convert to HTML for easy reading
pygetpapers --convert_html ~/pygetpapers/2024_01_15_10_30_45
```

#### Literature Review Workflow

```bash
# 1. Search multiple repositories
pygetpapers --api europe_pmc --query "machine learning biology" --limit 20 --makecsv
pygetpapers --api biorxiv --query "machine learning biology" --limit 20 --makecsv
pygetpapers --api crossref --query "machine learning biology" --limit 20 --makecsv

# 2. Generate combined datatables
pygetpapers --api europe_pmc --query "machine learning biology" --limit 20 --datatables

# 3. Download full-text for selected papers
pygetpapers --api europe_pmc --query "machine learning biology" --limit 20 --xml --pdf
```

## Next Steps

1. **Explore the Documentation**: Check the `docs/` directory for detailed guides
2. **Try the Streamlit Interface**: Run `python run_streamlit.py` for a web-based interface
3. **Join the Community**: Visit the GitHub repository for issues and discussions
4. **Contribute**: Submit bug reports, feature requests, or code contributions

## Support

- **GitHub Issues**: https://github.com/pygetpapers/pygetpapers/issues
- **Documentation**: Check the `docs/` directory
- **Examples**: See the `examples/` directory for more usage examples

Happy paper downloading! 📚 