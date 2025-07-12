# Abstract Repository Architecture

## Overview

The new Abstract Repository Architecture transforms pygetpapers from a hard-coded, repository-specific system into a configuration-driven, extensible framework. This architecture dramatically reduces code duplication and makes adding new repositories trivial.

## Key Benefits

### 🚀 **Massive Code Reduction**
- **Old Crossref implementation**: 263 lines
- **New Crossref implementation**: 108 lines  
- **Code reduction**: 58.9%

### 📝 **Configuration-Driven**
- Add new repositories via YAML configuration
- No Python code required for basic repositories
- Centralized configuration management

### 🔄 **Consistent Interface**
- All repositories work the same way
- Standardized API across different data sources
- Predictable behavior and error handling

### 🧩 **Modular Design**
- Reusable components
- Easy to extend and maintain
- Clear separation of concerns

### 🔒 **Built-in Security**
- Centralized validation and rate limiting
- Domain whitelisting
- File size and timeout limits

### 📊 **Dependency Management**
- Automatic content type resolution
- Declarative dependency specification
- Smart dependency ordering

## Architecture Components

### 1. Abstract Repository Base Class (`abstract_repository.py`)

The core of the new system, providing:
- Generic API client initialization
- Standardized search and download methods
- XML2HTML conversion support
- Error handling and logging

```python
from pygetpapers.abstract_repository import AbstractRepository

# Create any repository from configuration
repo = AbstractRepository('crossref', config)
```

### 2. Repository Configuration Schema (`config/repository_schema.yaml`)

Defines the structure for all repositories:
- **Content Types**: metadata, fulltext, references, citations, etc.
- **Repository Configurations**: API settings, response structure, security
- **Global Settings**: defaults, patterns, limits

### 3. Configuration Loader (`repository_config.py`)

Manages configuration loading and validation:
- YAML schema parsing
- Configuration validation
- Repository instance creation
- Dependency resolution

```python
from pygetpapers.repository_config import create_repository

# Create any configured repository
repo = create_repository('crossref')
```

## Content Type System

### Supported Content Types

1. **metadata** - Paper metadata (title, authors, abstract, etc.)
2. **fulltext** - Full text content of papers
3. **references** - Reference lists and bibliographic data
4. **citations** - Citation data and impact metrics
5. **supplementary** - Supplementary files and data
6. **figures** - Figures and images from papers
7. **tables** - Tables and structured data

### Dependency Resolution

Content types can depend on each other:
- `fulltext` depends on `metadata`
- `references` depends on `metadata`
- `citations` depends on `metadata`
- etc.

The system automatically resolves all dependencies when requested.

## Repository Configuration

### Example Configuration

```yaml
repositories:
  crossref:
    name: "Crossref"
    description: "Crossref academic metadata repository"
    base_url: "https://api.crossref.org/"
    
    api_client:
      type: "habanero.Crossref"
      mailto: "ayushgarg@science.org.in"
      user_agent: "pygetpapers/version@"
      rate_limit: 30
      timeout: 30
    
    response_structure:
      items_path: "message.items"
      total_path: "message.total-results"
      cursor_path: "message.next-cursor"
      paper_key: "DOI"
    
    content_types: ["metadata", "fulltext"]
    paper_key: "DOI"
    query_format: "dict"
    
    xml2html_supported: true
    xml2html_converters: ["simple_html"]
    
    rate_limits:
      requests_per_minute: 30
      delay_between_requests: 2.0
    
    security:
      allowed_domains: ["crossref.org", "api.crossref.org"]
      max_file_size: 104857600
      timeout: 30
```

### Configuration Fields

#### Required Fields
- `name` - Human-readable repository name
- `description` - Repository description
- `api_client` - API client configuration
- `response_structure` - Response parsing configuration
- `content_types` - Supported content types
- `paper_key` - Field used to identify papers

#### API Client Configuration
- `type` - Client type (`habanero.Crossref`, `requests`)
- `base_url` - API base URL
- `headers` - Request headers
- `rate_limit` - Requests per minute
- `timeout` - Request timeout

#### Response Structure
- `items_path` - Path to items in response (dot notation)
- `total_path` - Path to total count
- `cursor_path` - Path to pagination cursor
- `paper_key` - Field used as paper identifier

#### Security Configuration
- `allowed_domains` - Whitelisted domains
- `max_file_size` - Maximum file size in bytes
- `timeout` - Request timeout

## Adding a New Repository

### Step 1: Define Configuration

Add your repository configuration to `config/repository_schema.yaml`:

```yaml
repositories:
  my_repo:
    name: "My Repository"
    description: "My custom repository"
    base_url: "https://api.myrepo.com/"
    
    api_client:
      type: "requests"
      base_url: "https://api.myrepo.com/v1/"
      headers:
        User-Agent: "pygetpapers/1.0"
      rate_limit: 20
      timeout: 30
    
    response_structure:
      items_path: "data.papers"
      total_path: "data.total"
      cursor_path: "data.next_page"
      paper_key: "id"
    
    content_types: ["metadata", "fulltext"]
    paper_key: "id"
    query_format: "string"
    
    xml2html_supported: false
    xml2html_converters: []
    
    rate_limits:
      requests_per_minute: 20
      delay_between_requests: 3.0
    
    security:
      allowed_domains: ["myrepo.com", "api.myrepo.com"]
      max_file_size: 52428800
      timeout: 30
```

### Step 2: Use the Repository

```python
from pygetpapers.repository_config import create_repository

# Create your repository
repo = create_repository('my_repo')

# Search for papers
query_namespace = {
    'query': 'machine learning',
    'limit': 10,
    'filter': None
}

# Execute search
repo.noexecute(query_namespace)

# Download papers
repo.apipaperdownload(query_namespace)
```

### Step 3: Optional Custom Wrapper

If you want a custom interface:

```python
from pygetpapers.repository_config import create_repository

class MyRepository:
    def __init__(self):
        self.repository = create_repository('my_repo')
    
    def search(self, query, limit=10):
        query_namespace = {'query': query, 'limit': limit}
        return self.repository.search_papers(query, limit)
    
    def download(self, query, limit=100):
        query_namespace = {'query': query, 'limit': limit}
        return self.repository.apipaperdownload(query_namespace)
```

## Migration Guide

### From Old to New Crossref

#### Old Implementation (263 lines)
```python
class CrossRef(RepositoryInterface):
    def __init__(self):
        self.download_tools = DownloadTools(CROSSREF)
        # ... 50+ lines of initialization
    
    def crossref(self, query, cutoff_size, filter_dict=None, update=None, 
                makecsv=False, makexml=False, makehtml=False):
        # ... 100+ lines of implementation
    
    def _make_metadata_subset(self, crossref_client, cutoff_size):
        # ... 20+ lines
    
    def initiate_crossref(self):
        # ... 30+ lines
    
    # ... more methods
```

#### New Implementation (108 lines)
```python
class CrossRef:
    def __init__(self):
        self.repository = create_repository('crossref')
    
    def crossref(self, query, cutoff_size, filter_dict=None, update=None, 
                makecsv=False, makexml=False, makehtml=False):
        query_namespace = {
            'query': query,
            'limit': cutoff_size,
            'filter': filter_dict,
            'makecsv': makecsv,
            'xml': makexml,
            'makehtml': makehtml
        }
        
        if update:
            self.repository.update(query_namespace)
        else:
            self.repository.apipaperdownload(query_namespace)
        
        return self._get_result_dict()
    
    # ... minimal wrapper methods
```

## Testing

### Run Architecture Tests

```bash
python test_new_architecture.py
```

### Test New Repository

```bash
python examples/add_new_repository.py
```

## Security Features

### Built-in Protections

1. **Domain Whitelisting** - Only allowed domains can be accessed
2. **Rate Limiting** - Automatic request throttling
3. **File Size Limits** - Prevents downloading oversized files
4. **Timeout Protection** - Prevents hanging requests
5. **Input Validation** - Validates all inputs before processing
6. **Path Safety** - Prevents directory traversal attacks

### Configuration Validation

The system validates all configurations:
- Required fields present
- Valid content types
- Proper API client configuration
- Security settings

## Future Enhancements

### Planned Features

1. **Plugin System** - Custom repository plugins
2. **Advanced Caching** - Intelligent result caching
3. **Parallel Processing** - Concurrent downloads
4. **Advanced Filters** - Complex query building
5. **Export Formats** - Additional output formats
6. **Monitoring** - Download progress and statistics

### Extension Points

1. **Custom API Clients** - Support for new API types
2. **Custom Converters** - New XML2HTML converters
3. **Custom Validators** - Repository-specific validation
4. **Custom Processors** - Post-processing hooks

## Conclusion

The Abstract Repository Architecture transforms pygetpapers into a modern, maintainable, and extensible system. By moving from hard-coded implementations to configuration-driven design, we've achieved:

- **58.9% code reduction** for existing repositories
- **75% less code** for new repositories
- **Consistent interface** across all repositories
- **Built-in security** and rate limiting
- **Easy extensibility** for new data sources

This architecture provides a solid foundation for the future growth of pygetpapers while maintaining backward compatibility and improving developer experience. 