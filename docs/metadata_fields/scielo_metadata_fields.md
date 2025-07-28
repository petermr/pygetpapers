# SciELO Repository - Metadata Fields

**Date:** July 28, 2025 (system date of generation)  
**Repository:** scielo  
**Access Method:** Advanced Web Scraping  
**Base URL:** https://scielo.org/

## Overview

SciELO uses advanced web scraping with multiple CSS selectors for robust metadata extraction from scientific literature. The repository supports multiple languages and provides comprehensive content access.

## Primary Fields (Immediate Information)

Fields that are directly available from the repository's search API or basic metadata extraction.

### Core Metadata
```json
{
  "title": "string",
  "authors": ["string"],
  "abstract": "string",
  "journal": "string",
  "year": "string",
  "doi": "string",
  "language": "string",
  "keywords": ["string"],
  "volume": "string",
  "issue": "string",
  "pages": "string",
  "url": "string",
  "collection": "string",
  "pdf_urls": ["string"]
}
```

### Field Descriptions

#### `title`
- **Type:** string
- **Description:** Full title of the publication
- **Source:** Web scraping from title elements
- **Example:** "Machine learning applications in scientific research: A comprehensive analysis"

#### `authors`
- **Type:** array of strings
- **Description:** List of author names
- **Source:** Web scraping from author elements
- **Format:** "Given Names Surname"
- **Example:** ["Ana Silva", "João Santos", "Maria Costa"]

#### `abstract`
- **Type:** string
- **Description:** Abstract text of the publication
- **Source:** Web scraping from abstract elements
- **Length:** Variable, typically 100-500 words
- **Example:** "Este estudo investiga as aplicações de machine learning..."

#### `journal`
- **Type:** string
- **Description:** Journal or publication name
- **Source:** Web scraping from journal elements
- **Example:** "Revista Brasileira de Ciências"

#### `year`
- **Type:** string
- **Description:** Publication year
- **Source:** Web scraping from date elements
- **Format:** Four-digit year
- **Example:** "2023"

#### `doi`
- **Type:** string
- **Description:** Digital Object Identifier
- **Source:** Web scraping from DOI elements
- **Format:** "10.XXXX/XXXXX"
- **Example:** "10.1590/S0102-311X2023000100001"

#### `language`
- **Type:** string
- **Description:** Language of the publication
- **Source:** Web scraping from language elements
- **Example:** "en" (English), "es" (Spanish), "pt" (Portuguese)

#### `keywords`
- **Type:** array of strings
- **Description:** Keywords or descriptors
- **Source:** Web scraping from keyword elements
- **Example:** ["machine learning", "scientific research", "artificial intelligence"]

#### `volume`
- **Type:** string
- **Description:** Journal volume number
- **Source:** Web scraping from volume elements
- **Example:** "15"

#### `issue`
- **Type:** string
- **Description:** Journal issue number
- **Source:** Web scraping from issue elements
- **Example:** "2"

#### `pages`
- **Type:** string
- **Description:** Page range
- **Source:** Web scraping from page elements
- **Example:** "123-145"

#### `url`
- **Type:** string
- **Description:** Direct URL to the article
- **Source:** Web scraping from article links
- **Format:** "https://scielo.org/XXXX/XXXX"
- **Example:** "https://scielo.org/abc/2023.v15n2/"

#### `collection`
- **Type:** string
- **Description:** SciELO collection identifier
- **Source:** Web scraping from collection elements
- **Example:** "Brazil", "Argentina", "Mexico"

#### `pdf_urls`
- **Type:** array of strings
- **Description:** URLs to PDF versions
- **Source:** Web scraping from PDF links
- **Format:** Array of PDF URLs
- **Example:** ["https://scielo.org/pdf/abc/v15n2/001.pdf"]

## Secondary Fields (Further Requests)

Fields that require additional web scraping, file downloads, or extended API calls.

### Content Files
```json
{
  "fulltext.html": "file",
  "fulltext.pdf": "file",
  "metadata.json": "file",
  "extracted_at": "datetime"
}
```

### Field Descriptions

#### `fulltext.html`
- **Type:** file
- **Description:** Full HTML content of the article
- **Source:** Web scraping from full-text pages
- **Size:** Variable, typically 100KB-1MB
- **Format:** HTML document

#### `fulltext.pdf`
- **Type:** file
- **Description:** Full-text PDF version
- **Source:** Direct download from pdf_urls
- **Size:** Variable, typically 1-10 MB
- **Format:** PDF document

#### `metadata.json`
- **Type:** file
- **Description:** Structured metadata in JSON format
- **Source:** Generated from scraped metadata
- **Size:** Small, typically 1-10KB
- **Format:** JSON file

#### `extracted_at`
- **Type:** datetime
- **Description:** Timestamp when metadata was extracted
- **Source:** System-generated during extraction
- **Format:** ISO datetime format
- **Example:** "2025-07-28T11:30:00.000Z"

## Ignored Fields

Fields that are extracted but should be ignored for normal processing.

### Technical Fields
```json
{
  "extracted_at": "datetime",
  "scraping_timestamp": "datetime",
  "request_id": "string",
  "session_id": "string"
}
```

#### `extracted_at`
- **Source:** System-generated during extraction
- **Type:** Processing timestamp
- **Reason for Ignoring:** Technical processing metadata not relevant for content analysis

#### `scraping_timestamp`
- **Source:** System-generated during scraping
- **Type:** Technical timestamp
- **Reason for Ignoring:** Technical scraping metadata not relevant for content analysis

#### `request_id`
- **Source:** System-generated request tracking
- **Type:** Internal request tracking identifier
- **Reason for Ignoring:** Debugging/tracking field with no research value

#### `session_id`
- **Source:** Web scraping session
- **Type:** Session identifier
- **Reason for Ignoring:** Technical session data with no research value

## Data Quality Notes

### Field Availability
- **Always Available:** title, authors, url, collection, extracted_at
- **Usually Available:** abstract, journal, year, language
- **Sometimes Available:** doi, keywords, volume, issue, pages, pdf_urls
- **Conditional:** fulltext.html, fulltext.pdf

### Reliability Factors
- **Web Scraping Stability:** Subject to website changes
- **Rate Limiting:** 1 request per second
- **Multi-language Support:** Multiple languages supported
- **Collection-based:** Organized by collections

### Common Issues
- **Missing Content:** Some articles lack full-text
- **Language Variations:** Mixed language content
- **Scraping Failures:** Website changes can break extraction
- **PDF Availability:** Not all articles have PDFs

## Usage Examples

### Basic Web Scraping
```python
from pygetpapers.repositories.scielo import ScieloIntegration

# Initialize scraper
scielo = ScieloIntegration()

# Search for papers
results = scielo.search_and_collect(
    query="machine learning",
    max_papers=10
)

# Access metadata
for paper in results["papers"]:
    print(f"Title: {paper['title']}")
    print(f"Authors: {', '.join(paper['authors'])}")
    print(f"Journal: {paper['journal']}")
    print(f"Collection: {paper['collection']}")
    print(f"Language: {paper['language']}")
```

### Full Content Download
```python
# Download full content
for paper in results["papers"]:
    url = paper["url"]
    download_result = scielo.download_article_content(url)
    
    if "error" not in download_result:
        print(f"Downloaded HTML: {download_result['html_file']}")
        print(f"Downloaded PDF: {download_result['pdf_file']}")
        print(f"Metadata: {download_result['metadata_file']}")
```

### Collection Analysis
```python
# Analyze collection distribution
collections = {}
for paper in results["papers"]:
    collection = paper.get("collection", "unknown")
    collections[collection] = collections.get(collection, 0) + 1

for collection, count in collections.items():
    print(f"{collection}: {count} papers")
```

## Implementation Notes

### Web Scraping Selectors
- **Title:** Multiple selectors with fallbacks
- **Authors:** `div.authors span.author`
- **Abstract:** `div.abstract` or `div.resumen`
- **Journal:** `div.journal-name`
- **Keywords:** `div.keywords span.keyword`
- **PDF Links:** `a.pdf-link` or `a[href*="pdf"]`

### Advanced Scraping Features
- **Multiple Selectors:** Fallback selectors for robustness
- **Collection Support:** Different selectors per collection
- **Language Detection:** Automatic language identification
- **Error Recovery:** Graceful handling of scraping failures

### Rate Limiting
- **Request Rate:** 1 request per second
- **Session Management:** Efficient session reuse
- **Timeout Handling:** Configurable timeouts
- **Error Recovery:** Automatic retry mechanisms

### Content Formats
- **HTML Content:** Direct HTML extraction
- **PDF Downloads:** Direct PDF file downloads
- **Metadata JSON:** Structured metadata export
- **Multi-language:** Support for multiple languages

## Related Documentation
- [Repository Summary](../repositories_summary.md)
- [File Size Alerts](../file-size-alerts.md)
- [Ignored Fields](../../pygetpapers/repositories/scielo/IGNORED_FIELDS.md)
- [SciELO Integration](../../pygetpapers/repositories/scielo/scielo.py) 