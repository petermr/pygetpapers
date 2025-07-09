# Generic Web Scraping Framework - Implementation Complete

## Overview

A configurable web scraping framework that allows pygetpapers to support multiple repositories through web scraping without hardcoding specific implementations. This framework is driven by configuration files that define how to scrape different repository websites.

## ✅ Implementation Status

The generic web scraping framework has been **fully implemented** and is ready for use. All core components are complete and functional.

## Architecture

### Core Components

1. **✅ GenericWebScraper**: Base scraper class with common functionality
2. **✅ ScrapingConfigParser**: Loads and validates scraping configurations
3. **✅ ConfigurableHTMLParser**: Configurable HTML parsing based on selectors
4. **✅ DataTransformer**: Extracts structured data using configuration rules
5. **✅ WebScrapingRepository**: Integrates with existing pygetpapers architecture

### Configuration-Driven Design

The framework uses INI configuration files to define scraping behavior:

```ini
[biorxiv_web]
name = BioRxiv Web Search
base_url = https://www.biorxiv.org
search_url = https://www.biorxiv.org/search/{query}
enabled = true
rate_limit = 2.0

[biorxiv_web.selectors]
results_container = div.search-results, main, div.content
paper_entry = article, div.search-result, div.paper
title = h1.title, h2.title, h3.title, a.title
authors = div.authors, span.author, div.author-list
doi = a[href*="doi.org"], span.doi, div.doi

[biorxiv_web.transformations]
title = strip_whitespace, remove_html_tags
authors = strip_whitespace, normalize_author_name
publication_date = parse_date
doi = normalize_doi
```

## Key Features

### ✅ Configuration Management
- **Multiple config sources**: System-wide, user, local, and environment-specific
- **Validation**: Comprehensive configuration validation with error reporting
- **Templates**: Auto-generated configuration templates for new repositories
- **Hot reloading**: Dynamic configuration updates without restart

### ✅ Flexible HTML Parsing
- **Multiple selector strategies**: CSS selectors, XPath, text matching, attributes
- **Fallback mechanisms**: Multiple selectors per field for robustness
- **Special selectors**: `text:`, `attr:`, `contains:` for advanced extraction
- **Error handling**: Graceful degradation when selectors fail

### ✅ Data Transformation Pipeline
- **Built-in transformations**: 25+ transformation functions
- **Text processing**: Cleaning, normalization, case conversion
- **Date parsing**: Multiple format support with fallbacks
- **URL normalization**: DOI, domain, and path extraction
- **Custom transformations**: User-defined transformation functions

### ✅ Robust HTTP Handling
- **Rate limiting**: Configurable delays between requests
- **Retry logic**: Exponential backoff with configurable limits
- **Session management**: Persistent connections with proper headers
- **Error recovery**: Continue scraping despite individual failures

### ✅ Repository Integration
- **Unified interface**: Compatible with existing pygetpapers repositories
- **Manager class**: Centralized management of multiple repositories
- **Batch operations**: Search across multiple repositories simultaneously
- **Output formats**: JSON, CSV, XML with metadata

## Usage Examples

### Basic Usage

```python
from pygetpapers.web_scraping import WebScrapingRepositoryManager

# Initialize manager
manager = WebScrapingRepositoryManager()

# Search all repositories
results = manager.search_all_repositories(
    query="urban heat island",
    max_results=20,
    output_dir="./output"
)
```

### Single Repository

```python
from pygetpapers.web_scraping import GenericWebScraper

# Initialize scraper
scraper = GenericWebScraper()

# Search specific repository
results = scraper.search_papers(
    repo_name='biorxiv_web',
    query='climate change',
    max_results=10
)
```

### Configuration Management

```python
from pygetpapers.web_scraping import ScrapingConfigParser

# Load and validate configuration
config_parser = ScrapingConfigParser()
config = config_parser.load_repository_config('biorxiv_web')
errors = config_parser.validate_config(config)

# Create new configuration template
template = config_parser.create_configuration_template('new_repo')
```

## Supported Repositories

### ✅ BioRxiv Web Search
- **URL**: `https://www.biorxiv.org/search/{query}`
- **Features**: Text queries, pagination, metadata extraction
- **Status**: Fully configured and tested

### ✅ MedRxiv Web Search
- **URL**: `https://www.medrxiv.org/search/{query}`
- **Features**: Text queries, pagination, metadata extraction
- **Status**: Fully configured and tested

### 🔄 arXiv Web Search
- **URL**: `https://arxiv.org/search/?query={query}`
- **Features**: Text queries, advanced filters, pagination
- **Status**: Configured but disabled by default

### 🔄 Custom Repositories
- **Template**: Available for any website
- **Configuration**: User-defined selectors and transformations
- **Status**: Ready for implementation

## Configuration File Structure

```
scraping_config.ini
├── [repositories] - List of available repositories
├── [biorxiv_web] - Repository settings
├── [biorxiv_web.search] - Search parameters
├── [biorxiv_web.selectors] - HTML selectors
├── [biorxiv_web.pagination] - Pagination selectors
├── [biorxiv_web.filters] - Available filters
├── [biorxiv_web.transformations] - Data transformations
├── [biorxiv_web.error_handling] - Error handling settings
├── [biorxiv_web.output] - Output configuration
└── [global] - Global settings
```

## Built-in Transformations

### Text Transformations
- `strip_whitespace` - Remove leading/trailing whitespace
- `remove_html_tags` - Strip HTML tags
- `normalize_whitespace` - Normalize whitespace characters
- `lowercase` / `uppercase` / `title_case` - Case conversion
- `remove_special_chars` - Remove non-alphanumeric characters

### Date Transformations
- `parse_date` - Parse various date formats to ISO
- `format_date` - Format dates to specific format
- `extract_year` / `extract_month` / `extract_day` - Extract date components

### URL Transformations
- `normalize_url` - Add protocol if missing
- `extract_domain` / `extract_path` - Extract URL components
- `normalize_doi` - Normalize DOI format

### Data Type Transformations
- `to_int` / `to_float` / `to_bool` / `to_string` - Type conversion
- `split_by_comma` / `split_by_semicolon` - List operations
- `unique_items` - Remove duplicates

### Author Transformations
- `normalize_author_name` - Handle "Last, First" format
- `extract_first_name` / `extract_last_name` - Name components
- `extract_initials` - Extract author initials

## Error Handling

### Robust Error Recovery
- **Individual paper failures**: Continue scraping other papers
- **Page failures**: Retry with exponential backoff
- **Selector failures**: Try fallback selectors
- **Network issues**: Automatic retry with configurable limits

### Comprehensive Logging
- **Structured logging**: Different levels for different components
- **Error tracking**: Detailed error messages with context
- **Performance monitoring**: Request timing and success rates
- **Debug information**: Detailed selector matching information

## Performance Features

### Rate Limiting
- **Configurable delays**: Per-repository rate limiting
- **Request tracking**: Monitor requests per minute
- **Respectful scraping**: Respect robots.txt and site policies

### Caching
- **Session persistence**: Reuse HTTP connections
- **Result caching**: Cache parsed results (configurable)
- **Configuration caching**: Cache parsed configurations

### Parallel Processing
- **Concurrent requests**: Configurable concurrency limits
- **Repository parallelism**: Search multiple repositories simultaneously
- **Resource management**: Memory and CPU optimization

## Integration with Pygetpapers

### Repository Interface
The framework provides a unified interface that integrates seamlessly with pygetpapers:

```python
# Use like any other pygetpapers repository
from pygetpapers.web_scraping import WebScrapingRepository

repo = WebScrapingRepository('biorxiv_web')
results = repo.search('urban heat island', max_results=20)
```

### Output Compatibility
- **JSON format**: Compatible with existing pygetpapers output
- **CSV export**: Standard tabular format
- **XML output**: Structured data format
- **Metadata files**: Search information and statistics

### CLI Integration
The framework can be easily integrated into pygetpapers' command-line interface:

```bash
# Future CLI commands
pygetpapers --repository biorxiv_web --query "urban heat island"
pygetpapers --repository medrxiv_web --query "COVID-19" --max-results 50
```

## Future Enhancements

### Planned Features
- **JavaScript rendering**: Support for dynamic content
- **Image extraction**: Download and process figures
- **Full-text extraction**: Extract complete paper content
- **Citation analysis**: Extract and analyze references
- **Advanced filters**: Date ranges, subject areas, authors

### Extensibility
- **Plugin system**: Custom transformation functions
- **API integration**: Hybrid scraping + API approaches
- **Machine learning**: Intelligent selector optimization
- **Community configurations**: Shared repository configurations

## Testing and Validation

### Configuration Validation
- **Syntax checking**: Validate INI file format
- **Selector testing**: Test selectors against sample pages
- **Transformation validation**: Verify transformation functions
- **Integration testing**: End-to-end workflow testing

### Error Scenarios
- **Network failures**: Test retry and recovery mechanisms
- **Page structure changes**: Test fallback selector mechanisms
- **Rate limiting**: Test respect for site policies
- **Large result sets**: Test pagination and memory usage

## Documentation and Examples

### Complete Documentation
- **API reference**: Full class and method documentation
- **Configuration guide**: Detailed configuration examples
- **Troubleshooting**: Common issues and solutions
- **Best practices**: Recommended usage patterns

### Example Scripts
- **Basic usage**: Simple search examples
- **Advanced features**: Complex configuration examples
- **Integration examples**: Pygetpapers integration
- **Custom repositories**: Building new repository configurations

## Conclusion

The Generic Web Scraping Framework provides a powerful, flexible, and maintainable solution for adding web scraping capabilities to pygetpapers. Its configuration-driven approach makes it easy to add new repositories without code changes, while its robust error handling and comprehensive feature set ensure reliable operation.

The framework is ready for production use and can be easily extended to support additional repositories and features as needed. 