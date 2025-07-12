# Redalyc Implementation Summary

## Overview

This document summarizes the implementation of Redalyc repository support in pygetpapers. Redalyc is a multilingual scientific repository focused on Latin America, Spain, and Portugal, with content in Spanish, English, and Portuguese.

## Implementation Approaches

### 1. Basic Web Scraper (`Redalyc`)

**File:** `src/pygetpapers/redalyc/redalyc.py`

**Features:**
- Simple HTTP requests-based scraping
- Fallback to homepage scraping when search endpoint fails
- Rate limiting and respectful crawling
- Extracts article metadata from individual pages
- Supports HTML, PDF, and XML downloads

**Usage:**
```python
from pygetpapers.redalyc import Redalyc

redalyc = Redalyc()
articles = redalyc.search_articles("machine learning", max_results=10)
```

**Configuration:** `src/pygetpapers/config.ini` section `[redalyc]`

### 2. Selenium-Based Scraper (`RedalycSelenium`)

**File:** `src/pygetpapers/redalyc/redalyc_selenium.py`

**Features:**
- Full browser automation using Selenium
- Interacts with AngularJS search interface
- Handles dynamic content loading
- More robust search functionality
- Foundation for other Selenium-based tasks

**Usage:**
```python
from pygetpapers.redalyc import RedalycSelenium

redalyc = RedalycSelenium(headless=True)
articles = redalyc.search_articles("machine learning", max_results=10)
redalyc.close()  # Important: close the browser
```

**Configuration:** `src/pygetpapers/config.ini` section `[redalyc_selenium]`

## URL Patterns Discovered

### Article URLs
- **Direct article:** `https://www.redalyc.org/articulo.oa?id={article_id}`
- **Journal article:** `https://www.redalyc.org/journal/{journal_id}/{article_id}/`

### Example Article IDs
- `14075366011`
- `41375362006`
- `123075329002`

## Metadata Extraction

Both implementations extract the following metadata:

- **Title:** Article title
- **Authors:** List of authors
- **Abstract:** Article abstract/summary
- **Journal:** Journal name
- **Year:** Publication year
- **DOI:** Digital Object Identifier
- **Keywords:** Article keywords
- **Language:** Content language
- **PDF URL:** Link to PDF version
- **XML URL:** Link to XML version

## Configuration

### Basic Scraper Configuration
```ini
[redalyc]
query_url = https://redalyc.org/redalyc/search
request_delay = 1.0
request_timeout = 30
max_results = 100
supported_languages = es,en,pt
xml2html_supported = false
```

### Selenium Configuration
```ini
[redalyc_selenium]
query_url = https://redalyc.org/redalyc/search
headless = true
wait_timeout = 10
request_delay = 2.0
max_results = 100
```

## Dependencies

### Basic Scraper
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `lxml` - XML parsing

### Selenium Scraper
- `selenium` - Browser automation
- `webdriver-manager` - ChromeDriver management
- Chrome browser (automatically managed)

## Testing

### Basic Scraper Test
```bash
python test_redalyc_implementation.py
```

### Selenium Scraper Test
```bash
python test_redalyc_selenium.py
```

## Search Functionality

### Basic Scraper
1. Attempts to use search endpoint (`/redalyc/search`)
2. Falls back to homepage scraping if search fails
3. Extracts article links from HTML
4. Visits each article page to extract metadata

### Selenium Scraper
1. Loads Redalyc homepage
2. Finds search input field (`#input-articulo`)
3. Enters search query and submits
4. Waits for results to load
5. Extracts article links from dynamic content
6. Visits each article page to extract metadata

## Error Handling

### Basic Scraper
- Graceful fallback from search to homepage scraping
- Rate limiting to respect server resources
- Timeout handling for requests
- Logging of errors and warnings

### Selenium Scraper
- WebDriver initialization error handling
- Element not found exceptions
- Timeout handling for page loads
- Automatic browser cleanup

## Performance Considerations

### Basic Scraper
- **Pros:** Fast, lightweight, no browser overhead
- **Cons:** Limited by static HTML, may miss dynamic content

### Selenium Scraper
- **Pros:** Full JavaScript support, robust search
- **Cons:** Slower, requires more resources, browser dependency

## Future Enhancements

1. **Search Result Pagination:** Implement pagination for large result sets
2. **Advanced Filters:** Support for date ranges, journal filters, etc.
3. **Bulk Downloads:** Optimize for downloading large numbers of articles
4. **Caching:** Implement result caching to avoid repeated requests
5. **Parallel Processing:** Use multiple threads/processes for faster scraping

## Integration with pygetpapers

Both implementations follow the pygetpapers repository interface:

- `search_articles()` - Search for articles
- `redalyc()` - Main search and download method
- `noexecute()` - Search without downloading
- `apipaperdownload()` - Download papers
- `update()` - Update from previous results

## Security and Ethics

- **Rate Limiting:** Both implementations include delays between requests
- **User Agent:** Proper identification in requests
- **Robots.txt:** Respect for website crawling policies
- **Error Handling:** Graceful handling of server errors

## Troubleshooting

### Common Issues

1. **ChromeDriver not found:** Install Chrome browser or use webdriver-manager
2. **Search endpoint 404:** Normal behavior, falls back to homepage scraping
3. **No results found:** Check network connection and Redalyc availability
4. **Selenium timeout:** Increase `wait_timeout` in configuration

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Conclusion

The Redalyc implementation provides two complementary approaches:

1. **Basic scraper** for simple, fast article extraction
2. **Selenium scraper** for robust, dynamic content handling

Both implementations successfully integrate with the pygetpapers framework and provide a solid foundation for accessing Redalyc's multilingual scientific content. 