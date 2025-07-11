# Pygetpapers 2.0 Guide

## Overview

Pygetpapers 2.0 is a comprehensive tool for downloading and analyzing scientific papers from multiple repositories. This guide covers the enhanced functionality for **Europe PMC** and **bioRxiv**, which have agreed to host these tools and are thoroughly tested.

## Project Structure

```
pygetpapers/
├── src/
│   ├── pygetpapers/           # Core pygetpapers functionality
│   │   ├── europe_pmc/        # Europe PMC repository support
│   │   ├── biorxiv/           # bioRxiv repository support
│   │   ├── datatables_integration.py  # Interactive HTML tables
│   │   └── pygetpapers.py     # Main CLI interface
│   ├── streamlit_app.py       # Streamlit web interface
│   └── run_streamlit.py       # Streamlit launcher
├── tests/                     # Test suite
├── docs/                      # Documentation
├── requirements.txt           # Python dependencies
└── pyproject.toml            # Project configuration
```

## Key Features

### ✅ **Europe PMC Support**
- **API Integration**: Full Europe PMC API support
- **Text Queries**: Advanced text-based search
- **Date Ranges**: Date-based filtering
- **Multiple Formats**: XML, HTML, PDF downloads
- **Metadata Extraction**: Comprehensive paper metadata
- **Batch Processing**: Efficient bulk downloads

### ✅ **BioRxiv Support**
- **Web Scraper**: Advanced text-based search (complements API)
- **API Integration**: Date-based searches via API
- **Full Content**: Downloads both landing page and full text
- **HTML Content**: Complete article content in HTML format
- **PDF Links**: Direct links to PDF versions
- **Metadata**: Rich paper metadata extraction

### ✅ **Enhanced Features**
- **Interactive Datatables**: HTML tables with search, pagination, sorting
- **Streamlit UI**: Modern web interface
- **External CSS**: Maintainable styling
- **Batch Processing**: Efficient bulk operations
- **Error Handling**: Robust error recovery
- **Rate Limiting**: Respectful API usage

## Installation

### Prerequisites
- Python 3.9+
- pip package manager

### Install pygetpapers
```bash
# Clone the repository
git clone https://github.com/your-repo/pygetpapers.git
cd pygetpapers

# Install in development mode
pip install -e .

# Install dependencies
pip install -r requirements.txt
```

## Command Line Usage

### Basic Commands

#### 1. **Europe PMC Search**
```bash
# Text-based search
pygetpapers --api europepmc --query "urban heat island" --limit 10

# Date-based search
pygetpapers --api europepmc --query "2023-01-01/2023-12-31" --limit 50

# With specific output formats
pygetpapers --api europepmc --query "climate change" --limit 20 --makehtml --makexml
```

#### 2. **BioRxiv Search**
```bash
# Text-based search (uses web scraper)
pygetpapers --api biorxiv --query "urban heat island" --limit 10

# Date-based search (uses API)
pygetpapers --api biorxiv --query "2023-01-01/2023-12-31" --limit 50

# Download with full content
pygetpapers --api biorxiv --query "climate adaptation" --limit 5 --makehtml
```

### Advanced Options

#### **Output Formats**
```bash
# Generate HTML tables
pygetpapers --api europepmc --query "your query" --makehtml

# Generate CSV files
pygetpapers --api biorxiv --query "your query" --makecsv

# Generate XML files
pygetpapers --api europepmc --query "your query" --xml

# Generate interactive datatables
pygetpapers --api europepmc --query "your query" --datatables
```

#### **Output Directory**
```bash
# Specify custom output directory
pygetpapers --api europepmc --query "your query" --output ./my_papers

# Use default directory (current working directory)
pygetpapers --api biorxiv --query "your query"
```

### Command Line Examples

#### **Europe PMC Examples**
```bash
# Search for recent climate change papers
pygetpapers --api europepmc --query "climate change" --limit 20 --makehtml

# Search by date range
pygetpapers --api europepmc --query "2023-06-01/2023-12-31" --limit 100

# Search with specific terms
pygetpapers --api europepmc --query "urban heat island adaptation" --limit 15 --makecsv

# Generate interactive datatables
pygetpapers --api europepmc --query "biodiversity conservation" --limit 25 --datatables
```

#### **BioRxiv Examples**
```bash
# Search for recent preprints
pygetpapers --api biorxiv --query "machine learning biology" --limit 10

# Search by date (API mode)
pygetpapers --api biorxiv --query "2023-01-01/2023-06-30" --limit 50

# Text search with full content download
pygetpapers --api biorxiv --query "cancer immunotherapy" --limit 5 --makehtml

# Generate interactive datatables
pygetpapers --api biorxiv --query "genomics" --limit 20 --datatables
```

## Streamlit Web Interface

### Launching Streamlit
```bash
# Method 1: Use the launcher script
python run_streamlit.py

# Method 2: Direct streamlit command
streamlit run streamlit_app.py

# Method 3: With custom port
streamlit run streamlit_app.py --server.port 8501
```

### Streamlit Features

#### **1. Search Interface**
- **Repository Selection**: Choose between Europe PMC and bioRxiv
- **Query Input**: Text-based search with autocomplete
- **Advanced Options**: Date ranges, result limits, output formats
- **Real-time Validation**: Query validation and suggestions

#### **2. Results Display**
- **Interactive Tables**: Sortable, searchable results
- **Paper Details**: Click to view full paper information
- **Download Options**: Direct download links
- **Progress Tracking**: Real-time download progress

#### **3. Data Export**
- **CSV Export**: Download results as CSV files
- **HTML Tables**: Generate interactive HTML tables
- **Datatables**: Advanced interactive tables with features
- **Metadata Export**: Complete paper metadata

### Streamlit Usage Examples

#### **Basic Search**
1. Open Streamlit interface
2. Select repository (Europe PMC or bioRxiv)
3. Enter search query
4. Set result limit
5. Click "Search Papers"
6. View results in interactive table

#### **Advanced Search**
1. Select repository
2. Enter complex query
3. Set date range (if applicable)
4. Choose output formats
5. Configure advanced options
6. Execute search
7. Export results

## Output Structure

### **Europe PMC Output**
```
output_directory/
├── europe_pmc_results.json      # Search results metadata
├── europe_pmc_results.csv       # CSV export (if requested)
├── PMC12345678/                 # Individual paper directory
│   ├── fulltext.xml            # Full text in XML format
│   ├── fulltext.html           # Full text in HTML format
│   ├── fulltext.pdf            # PDF file (if available)
│   └── metadata.json           # Paper metadata
├── PMC87654321/
│   ├── fulltext.xml
│   ├── fulltext.html
│   └── metadata.json
└── datatables/                  # Interactive tables (if requested)
    ├── datatables_index.html
    ├── papers_datatable.html
    ├── metadata_datatable.html
    └── datatables.css
```

### **BioRxiv Output**
```
output_directory/
├── biorxiv_results.json         # Search results metadata
├── biorxiv_results.csv          # CSV export (if requested)
├── 10.1101_2023.11.10.566554/   # Individual paper directory
│   ├── landing.html            # Abstract and metadata page
│   ├── fulltext.html           # Complete article content
│   ├── pdf_url.txt             # PDF download link
│   └── metadata.json           # Paper metadata
├── 10.1101_2023.06.01.543268/
│   ├── landing.html
│   ├── fulltext.html
│   └── metadata.json
└── datatables/                  # Interactive tables (if requested)
    ├── datatables_index.html
    ├── papers_datatable.html
    ├── metadata_datatable.html
    └── datatables.css
```

## Interactive Datatables

### **Features**
- **Search**: Real-time search across all columns
- **Pagination**: Navigate through large result sets
- **Sorting**: Sort by any column
- **Responsive**: Works on mobile and desktop
- **Export**: Download filtered/sorted data

### **Generated Files**
- `datatables_index.html`: Main index page with links
- `papers_datatable.html`: Interactive papers table
- `metadata_datatable.html`: Metadata overview table
- `datatables.css`: Styling (can be external or inline)

### **Usage**
```bash
# Generate datatables for Europe PMC
pygetpapers --api europepmc --query "your query" --datatables

# Generate datatables for bioRxiv
pygetpapers --api biorxiv --query "your query" --datatables
```

## Configuration

### **Repository Configuration**
Each repository has its own configuration file:
- `src/pygetpapers/europe_pmc/config.ini`
- `src/pygetpapers/biorxiv/config.ini`

### **Rate Limiting**
- **Europe PMC**: 1000 requests per hour
- **BioRxiv**: 1 request per second (web scraper)
- **BioRxiv API**: 1000 requests per hour

### **Output Formats**
- **Europe PMC**: XML, HTML, PDF
- **BioRxiv**: HTML (landing + fulltext), PDF links

## Testing

### **Test Commands**
```bash
# Run all tests
pytest tests/

# Run specific repository tests
pytest tests/test_europe_pmc.py
pytest tests/test_biorxiv.py

# Run CI tests
python tests/test_ci.py

# Run style checks
black .
isort .
flake8 src/
```

### **Test Coverage**
- **Europe PMC**: API integration, text queries, date ranges
- **BioRxiv**: Web scraper, API integration, full content download
- **Datatables**: HTML generation, interactive features
- **Streamlit**: UI functionality, search interface

## Troubleshooting

### **Common Issues**

#### **1. Rate Limiting**
```
Error: Too many requests
Solution: Wait and retry, or reduce request frequency
```

#### **2. Network Issues**
```
Error: Connection timeout
Solution: Check internet connection, try again
```

#### **3. File Permissions**
```
Error: Permission denied
Solution: Check directory permissions, use different output location
```

#### **4. Query Syntax**
```
Error: Invalid query format
Solution: Use simple text queries, avoid special characters
```

### **Debug Mode**
```bash
# Enable debug logging
pygetpapers --api europepmc --query "test" --debug

# Verbose output
pygetpapers --api biorxiv --query "test" --verbose
```

## Best Practices

### **1. Query Optimization**
- Use specific, targeted queries
- Avoid overly broad searches
- Use date ranges to limit results
- Combine terms for better precision

### **2. Resource Management**
- Set reasonable result limits
- Use batch processing for large datasets
- Monitor disk space usage
- Clean up temporary files

### **3. Rate Limiting**
- Respect API rate limits
- Use delays between requests
- Implement retry logic
- Monitor request counts

### **4. Data Organization**
- Use descriptive output directories
- Maintain consistent naming conventions
- Keep metadata files organized
- Regular backup of important data

## API Reference

### **Command Line Options**
```bash
--api              # Repository (europepmc, biorxiv)
--query            # Search query
--limit            # Maximum results
--output           # Output directory
--makehtml         # Generate HTML files
--makecsv          # Generate CSV files
--xml              # Generate XML files
--datatables       # Generate interactive tables
--debug            # Enable debug mode
--verbose          # Verbose output
```

### **Python API**
```python
from pygetpapers import Pygetpapers

# Initialize
pygetpapers = Pygetpapers()

# Search Europe PMC
results = pygetpapers.europepmc("your query", limit=10)

# Search bioRxiv
results = pygetpapers.biorxiv("your query", limit=10)

# Generate datatables
pygetpapers.create_datatables(results)
```

## Support and Contributing

### **Getting Help**
- Check the documentation in `docs/`
- Review test examples in `tests/`
- Open an issue on GitHub
- Check existing issues for solutions

### **Contributing**
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run style checks
6. Submit a pull request

### **Testing Your Changes**
```bash
# Run style checks
black .
isort .
flake8 src/

# Run tests
pytest tests/

# Test specific functionality
python -m pytest tests/test_europe_pmc.py -v
python -m pytest tests/test_biorxiv.py -v
```

## Version History

### **v2.0.0 (Current)**
- Enhanced Europe PMC support
- Advanced bioRxiv web scraper
- Interactive datatables
- Streamlit web interface
- External CSS support
- Comprehensive testing

### **Key Improvements**
- Full text download for bioRxiv
- Interactive HTML tables
- Modern web interface
- Better error handling
- Enhanced metadata extraction
- Rate limiting improvements

---

**Note**: This guide covers Europe PMC and bioRxiv repositories, which have been thoroughly tested and are officially supported. Other repositories may have different capabilities and limitations. 