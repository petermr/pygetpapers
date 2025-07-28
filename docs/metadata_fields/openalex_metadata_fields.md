# OpenAlex Repository - Metadata Fields

**Date:** July 28, 2025 (system date of generation)  
**Repository:** openalex  
**Access Method:** Full REST API  
**Base URL:** https://api.openalex.org/

## Overview

OpenAlex focuses on open access metadata with comprehensive citation data and PDF download capabilities. The repository provides rich bibliometric information and modern API access to scholarly literature.

## Primary Fields (Immediate Information)

Fields that are directly available from the repository's search API or basic metadata extraction.

### Core Metadata
```json
{
  "title": "string",
  "authors": ["string"],
  "doi": "string",
  "publication_date": "string",
  "journal": "string",
  "abstract": "string",
  "keywords": ["string"],
  "best_oa_location": {
    "pdf_url": "string",
    "landing_page_url": "string"
  },
  "open_access": "boolean",
  "cited_by_count": "integer",
  "type": "string"
}
```

### Field Descriptions

#### `title`
- **Type:** string
- **Description:** Full title of the publication
- **Source:** API response from title field
- **Example:** "Machine learning applications in drug discovery: A comprehensive review"

#### `authors`
- **Type:** array of strings
- **Description:** List of author names
- **Source:** API response from authors array
- **Format:** "Given Names Surname"
- **Example:** ["John Smith", "Jane Doe", "Robert Johnson"]

#### `doi`
- **Type:** string
- **Description:** Digital Object Identifier
- **Source:** API response from doi field
- **Format:** "10.XXXX/XXXXX"
- **Example:** "10.1038/s41586-023-12345-6"

#### `publication_date`
- **Type:** string
- **Description:** Publication date
- **Source:** API response from publication_date field
- **Format:** ISO date format
- **Example:** "2023-01-15"

#### `journal`
- **Type:** string
- **Description:** Journal or venue name
- **Source:** API response from primary_location field
- **Example:** "Nature"

#### `abstract`
- **Type:** string
- **Description:** Abstract text of the publication
- **Source:** API response from abstract_inverted_index field
- **Length:** Variable, typically 100-500 words
- **Example:** "This comprehensive review examines the application of machine learning..."

#### `keywords`
- **Type:** array of strings
- **Description:** Keywords or concepts
- **Source:** API response from concepts array
- **Example:** ["machine learning", "drug discovery", "artificial intelligence"]

#### `best_oa_location`
- **Type:** object
- **Description:** Best open access location information
- **Source:** API response from best_oa_location field
- **Structure:**
  - `pdf_url`: Direct URL to PDF
  - `landing_page_url`: URL to landing page

#### `open_access`
- **Type:** boolean
- **Description:** Whether the work is open access
- **Source:** API response from open_access field
- **Example:** true

#### `cited_by_count`
- **Type:** integer
- **Description:** Number of citations
- **Source:** API response from cited_by_count field
- **Example:** 150

#### `type`
- **Type:** string
- **Description:** Type of work
- **Source:** API response from type field
- **Example:** "journal-article"

## Secondary Fields (Further Requests)

Fields that require additional web scraping, file downloads, or extended API calls.

### Content Files
```json
{
  "fulltext.pdf": "file",
  "pdfdownloaded": "boolean",
  "cursor_mark": "string",
  "total_results": "integer"
}
```

### Field Descriptions

#### `fulltext.pdf`
- **Type:** file
- **Description:** Full-text PDF version
- **Source:** Direct download from best_oa_location.pdf_url
- **Size:** Variable, typically 1-10 MB
- **Format:** PDF document

#### `pdfdownloaded`
- **Type:** boolean
- **Description:** Whether PDF was successfully downloaded
- **Source:** System-generated flag
- **Example:** true

#### `cursor_mark`
- **Type:** string
- **Description:** Pagination cursor for API requests
- **Source:** API response pagination metadata
- **Purpose:** Used for pagination in large result sets
- **Example:** "*"

#### `total_results`
- **Type:** integer
- **Description:** Total number of results for the query
- **Source:** API response metadata
- **Example:** 1250

## Ignored Fields

Fields that are extracted but should be ignored for normal processing.

### Technical Fields
```json
{
  "cursor_mark": "string",
  "total_results": "integer",
  "api_version": "string",
  "request_id": "string"
}
```

#### `cursor_mark`
- **Source:** API response pagination metadata
- **Type:** Internal pagination identifier
- **Reason for Ignoring:** Technical pagination field with no research value

#### `total_results`
- **Source:** API response metadata
- **Type:** Search result count
- **Reason for Ignoring:** Technical search metadata not relevant for content analysis

#### `api_version`
- **Source:** API response metadata
- **Type:** Technical API version information
- **Reason for Ignoring:** Technical metadata not relevant for content analysis

#### `request_id`
- **Source:** API response headers or metadata
- **Type:** Internal request tracking identifier
- **Reason for Ignoring:** Debugging/tracking field with no research value

## Data Quality Notes

### Field Availability
- **Always Available:** title, authors, doi, publication_date, type
- **Usually Available:** journal, open_access, cited_by_count
- **Sometimes Available:** abstract, keywords, best_oa_location
- **Conditional:** fulltext.pdf, pdfdownloaded

### Reliability Factors
- **API Stability:** Very stable REST API
- **Rate Limiting:** 2 requests per second
- **Content Consistency:** Well-structured data
- **Open Access Focus:** Comprehensive OA coverage

### Common Issues
- **Missing Abstracts:** Some works lack abstract text
- **PDF Availability:** Not all works have accessible PDFs
- **Citation Delays:** Citation counts may be delayed
- **Access Restrictions:** Some content may be restricted

## Usage Examples

### Basic API Search
```python
from pygetpapers.core.download_tools import DownloadTools

# Initialize download tools
tools = DownloadTools("openalex")

# Search for papers
results = tools.post_query(
    url="https://api.openalex.org/works",
    data={"search": "machine learning drug discovery", "per_page": 25}
)

# Access metadata
for work in results["results"]:
    print(f"Title: {work['title']}")
    print(f"Authors: {[author['author']['display_name'] for author in work['authorships']]}")
    print(f"DOI: {work.get('doi', 'N/A')}")
    print(f"Citations: {work.get('cited_by_count', 0)}")
```

### Full Content Download
```python
# Download PDF content
for work in results["results"]:
    if work.get("best_oa_location", {}).get("pdf_url"):
        pdf_url = work["best_oa_location"]["pdf_url"]
        pdf_content = tools.queries_the_url_and_writes_response_to_destination(
            pdf_url, f"output/{work['id'].split('/')[-1]}.pdf"
        )
        print(f"Downloaded PDF for {work['title']}")
```

### Citation Analysis
```python
# Analyze citation data
for work in results["results"]:
    cited_by_count = work.get("cited_by_count", 0)
    if cited_by_count > 100:
        print(f"Highly cited: {work['title']} ({cited_by_count} citations)")
```

## Implementation Notes

### API Endpoints
- **Works Search:** `https://api.openalex.org/works`
- **Work Details:** `https://api.openalex.org/works/{id}`
- **Authors:** `https://api.openalex.org/authors`
- **Venues:** `https://api.openalex.org/venues`
- **Concepts:** `https://api.openalex.org/concepts`

### Rate Limiting
- **API Requests:** 2 requests per second
- **Bulk Downloads:** No specific limit but bandwidth dependent
- **Pagination:** Cursor-based pagination supported

### Content Formats
- **JSON API:** RESTful JSON API
- **PDF Access:** Direct PDF downloads when available
- **Metadata:** Rich structured metadata
- **Citations:** Comprehensive citation data

### Pagination
- **Cursor-based:** Uses cursor_mark for pagination
- **Large Results:** Supports large result sets efficiently
- **Resume Capability:** Can resume interrupted downloads

## Related Documentation
- [Repository Summary](../repositories_summary.md)
- [File Size Alerts](../file-size-alerts.md)
- [Ignored Fields](../../pygetpapers/repositories/openalex/IGNORED_FIELDS.md) 