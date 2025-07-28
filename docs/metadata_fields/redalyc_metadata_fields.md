# Redalyc Repository - Metadata Fields

**Date:** July 28, 2025 (system date of generation)  
**Repository:** redalyc  
**Access Method:** Selenium Web Scraping  
**Base URL:** https://www.redalyc.org/

## Overview

Redalyc provides access to Spanish and Portuguese language academic literature using advanced Selenium web scraping. The repository offers rich metadata extraction and direct content downloads for Latin American research.

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
  "url": "string",
  "article_id": "string",
  "content_preview": "string",
  "pdf_url": "string",
  "language": "string",
  "keywords": ["string"],
  "volume": "string",
  "issue": "string",
  "pages": "string"
}
```

### Field Descriptions

#### `title`
- **Type:** string
- **Description:** Full title of the publication
- **Source:** Selenium scraping from title elements
- **Example:** "Aplicación de machine learning en el descubrimiento de fármacos: Una revisión comprehensiva"

#### `authors`
- **Type:** array of strings
- **Description:** List of author names
- **Source:** Selenium scraping from author elements
- **Format:** "Given Names Surname"
- **Example:** ["Juan Pérez", "María García", "Carlos López"]

#### `abstract`
- **Type:** string
- **Description:** Abstract text of the publication
- **Source:** Selenium scraping from abstract elements
- **Length:** Variable, typically 100-500 words
- **Example:** "Este estudio investiga la aplicación de machine learning..."

#### `journal`
- **Type:** string
- **Description:** Journal or publication name
- **Source:** Selenium scraping from journal elements
- **Example:** "Revista Latinoamericana de Ciencias"

#### `year`
- **Type:** string
- **Description:** Publication year
- **Source:** Selenium scraping from date elements
- **Format:** Four-digit year
- **Example:** "2023"

#### `url`
- **Type:** string
- **Description:** Direct URL to the article
- **Source:** Selenium scraping from article links
- **Format:** "https://www.redalyc.org/journal/XXXX/article/XXXX"
- **Example:** "https://www.redalyc.org/journal/1234/article/5678"

#### `article_id`
- **Type:** string
- **Description:** Redalyc-specific article identifier
- **Source:** Selenium scraping from URL or metadata
- **Example:** "12345678"

#### `content_preview`
- **Type:** string
- **Description:** Preview of article content
- **Source:** Selenium scraping from preview elements
- **Length:** Variable, typically 50-200 words
- **Example:** "Resumen del contenido del artículo..."

#### `pdf_url`
- **Type:** string
- **Description:** Direct URL to PDF version
- **Source:** Selenium scraping from PDF links
- **Format:** "https://www.redalyc.org/journal/XXXX/article/XXXX/pdf"
- **Example:** "https://www.redalyc.org/journal/1234/article/5678/pdf"

#### `language`
- **Type:** string
- **Description:** Language of the publication
- **Source:** Selenium scraping from language elements
- **Example:** "es" (Spanish) or "pt" (Portuguese)

#### `keywords`
- **Type:** array of strings
- **Description:** Keywords or descriptors
- **Source:** Selenium scraping from keyword elements
- **Example:** ["machine learning", "descubrimiento de fármacos", "inteligencia artificial"]

#### `volume`
- **Type:** string
- **Description:** Journal volume number
- **Source:** Selenium scraping from volume elements
- **Example:** "15"

#### `issue`
- **Type:** string
- **Description:** Journal issue number
- **Source:** Selenium scraping from issue elements
- **Example:** "2"

#### `pages`
- **Type:** string
- **Description:** Page range
- **Source:** Selenium scraping from page elements
- **Example:** "123-145"

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
- **Source:** Selenium scraping from full-text pages
- **Size:** Variable, typically 100KB-1MB
- **Format:** HTML document

#### `fulltext.pdf`
- **Type:** file
- **Description:** Full-text PDF version
- **Source:** Direct download from pdf_url
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
  "selenium_session_id": "string",
  "scraping_timestamp": "datetime",
  "request_id": "string"
}
```

#### `extracted_at`
- **Source:** System-generated during extraction
- **Type:** Processing timestamp
- **Reason for Ignoring:** Technical processing metadata not relevant for content analysis

#### `selenium_session_id`
- **Source:** Selenium browser session
- **Type:** Selenium session identifier
- **Reason for Ignoring:** Technical browser session data with no research value

#### `scraping_timestamp`
- **Source:** System-generated during scraping
- **Type:** Technical timestamp
- **Reason for Ignoring:** Technical scraping metadata not relevant for content analysis

#### `request_id`
- **Source:** System-generated request tracking
- **Type:** Internal request tracking identifier
- **Reason for Ignoring:** Debugging/tracking field with no research value

## Data Quality Notes

### Field Availability
- **Always Available:** title, authors, url, article_id, extracted_at
- **Usually Available:** abstract, journal, year, language
- **Sometimes Available:** keywords, volume, issue, pages, pdf_url
- **Conditional:** fulltext.html, fulltext.pdf, content_preview

### Reliability Factors
- **Web Scraping Stability:** Subject to website changes
- **Rate Limiting:** 1 request per second
- **Language Support:** Spanish and Portuguese content
- **Content Consistency:** Variable HTML structure

### Common Issues
- **Missing Content:** Some articles lack full-text
- **Language Variations:** Mixed language content
- **Scraping Failures:** Website changes can break extraction
- **PDF Availability:** Not all articles have PDFs

## Usage Examples

### Basic Web Scraping
```python
from pygetpapers.repositories.redalyc import RedalycSelenium

# Initialize scraper
redalyc = RedalycSelenium()

# Search for papers
results = redalyc.search_and_collect(
    query="machine learning",
    max_papers=10
)

# Access metadata
for paper in results["papers"]:
    print(f"Title: {paper['title']}")
    print(f"Authors: {', '.join(paper['authors'])}")
    print(f"Journal: {paper['journal']}")
    print(f"Year: {paper['year']}")
    print(f"Language: {paper['language']}")
```

### Full Content Download
```python
# Download full content
for paper in results["papers"]:
    article_id = paper["article_id"]
    download_result = redalyc.download_article_content(article_id)
    
    if "error" not in download_result:
        print(f"Downloaded HTML: {download_result['html_file']}")
        print(f"Downloaded PDF: {download_result['pdf_file']}")
        print(f"Metadata: {download_result['metadata_file']}")
```

### Language Analysis
```python
# Analyze language distribution
languages = {}
for paper in results["papers"]:
    lang = paper.get("language", "unknown")
    languages[lang] = languages.get(lang, 0) + 1

for lang, count in languages.items():
    print(f"{lang}: {count} papers")
```

## Implementation Notes

### Selenium Scraping Selectors
- **Title:** `h1.article-title` or `div.title`
- **Authors:** `div.authors span.author`
- **Abstract:** `div.abstract` or `div.resumen`
- **Journal:** `div.journal-name`
- **Keywords:** `div.keywords span.keyword`
- **PDF Link:** `a.pdf-link` or `a[href*="pdf"]`

### Web Scraping Configuration
- **Browser:** Chrome/Firefox with Selenium
- **Wait Times:** Dynamic waits for content loading
- **Retry Logic:** Automatic retry for failed requests
- **Error Handling:** Graceful handling of scraping failures

### Rate Limiting
- **Request Rate:** 1 request per second
- **Session Management:** Browser session reuse
- **Timeout Handling:** Configurable timeouts
- **Error Recovery:** Automatic retry mechanisms

### Content Formats
- **HTML Content:** Direct HTML extraction
- **PDF Downloads:** Direct PDF file downloads
- **Metadata JSON:** Structured metadata export
- **Language Detection:** Automatic language identification

## Related Documentation
- [Repository Summary](../repositories_summary.md)
- [File Size Alerts](../file-size-alerts.md)
- [Ignored Fields](../../pygetpapers/repositories/redalyc/IGNORED_FIELDS.md)
- [Selenium Integration](../../pygetpapers/repositories/redalyc/redalyc_selenium.py) 