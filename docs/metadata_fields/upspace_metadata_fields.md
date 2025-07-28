# UPSpace Repository - Metadata Fields

**Date:** July 28, 2025 (system date of generation)  
**Repository:** upspace  
**Access Method:** DSpace REST API  
**Base URL:** https://repository.up.ac.za/

## Overview

UPSpace uses DSpace REST API with unique SDG (Sustainable Development Goals) classifications for institutional repository content. The repository provides access to University of Pretoria's scholarly output with specialized metadata.

## Primary Fields (Immediate Information)

Fields that are directly available from the repository's search API or basic metadata extraction.

### Core Metadata
```json
{
  "title": "string",
  "authors": ["string"],
  "abstract": "string",
  "year": "string",
  "publisher": "string",
  "type": "string",
  "handle_url": "string",
  "handle_id": "string",
  "doi": "string",
  "keywords": ["string"],
  "sdg_classifications": ["string"],
  "language": "string",
  "uuid": "string",
  "id": "integer"
}
```

### Field Descriptions

#### `title`
- **Type:** string
- **Description:** Full title of the publication
- **Source:** DSpace API response from dc.title field
- **Example:** "Machine learning applications in sustainable development: A case study"

#### `authors`
- **Type:** array of strings
- **Description:** List of author names
- **Source:** DSpace API response from dc.contributor.author field
- **Format:** "Given Names Surname"
- **Example:** ["Sarah Johnson", "Michael Brown", "Lisa Davis"]

#### `abstract`
- **Type:** string
- **Description:** Abstract text of the publication
- **Source:** DSpace API response from dc.description.abstract field
- **Length:** Variable, typically 100-500 words
- **Example:** "This study investigates the application of machine learning..."

#### `year`
- **Type:** string
- **Description:** Publication year
- **Source:** DSpace API response from dc.date.issued field
- **Format:** Four-digit year
- **Example:** "2023"

#### `publisher`
- **Type:** string
- **Description:** Publisher information
- **Source:** DSpace API response from dc.publisher field
- **Example:** "University of Pretoria"

#### `type`
- **Type:** string
- **Description:** Type of work
- **Source:** DSpace API response from dc.type field
- **Example:** "Thesis", "Article", "Conference Paper"

#### `handle_url`
- **Type:** string
- **Description:** DSpace handle URL
- **Source:** DSpace API response from handle field
- **Format:** "https://repository.up.ac.za/handle/XXXX/XXXX"
- **Example:** "https://repository.up.ac.za/handle/2263/12345"

#### `handle_id`
- **Type:** string
- **Description:** DSpace handle identifier
- **Source:** DSpace API response from handle field
- **Format:** "XXXX/XXXX"
- **Example:** "2263/12345"

#### `doi`
- **Type:** string
- **Description:** Digital Object Identifier
- **Source:** DSpace API response from dc.identifier.doi field
- **Format:** "10.XXXX/XXXXX"
- **Example:** "10.4102/sajim.v25i1.1234"

#### `keywords`
- **Type:** array of strings
- **Description:** Keywords or descriptors
- **Source:** DSpace API response from dc.subject field
- **Example:** ["machine learning", "sustainable development", "artificial intelligence"]

#### `sdg_classifications`
- **Type:** array of strings
- **Description:** Sustainable Development Goals classifications
- **Source:** DSpace API response from dc.subject.sdg field
- **Example:** ["SDG 3: Good Health and Well-being", "SDG 9: Industry, Innovation and Infrastructure"]

#### `language`
- **Type:** string
- **Description:** Language of the publication
- **Source:** DSpace API response from dc.language field
- **Example:** "en" (English)

#### `uuid`
- **Type:** string
- **Description:** DSpace UUID identifier
- **Source:** DSpace API response from uuid field
- **Format:** UUID format
- **Example:** "12345678-1234-1234-1234-123456789012"

#### `id`
- **Type:** integer
- **Description:** DSpace numeric identifier
- **Source:** DSpace API response from id field
- **Example:** 12345

## Secondary Fields (Further Requests)

Fields that require additional web scraping, file downloads, or extended API calls.

### Content Files
```json
{
  "fulltext.pdf": "file",
  "metadata.json": "file",
  "upspace_datatables.html": "file",
  "index.html": "file"
}
```

### Field Descriptions

#### `fulltext.pdf`
- **Type:** file
- **Description:** Full-text PDF version
- **Source:** Direct download from DSpace bitstreams
- **Size:** Variable, typically 1-10 MB
- **Format:** PDF document

#### `metadata.json`
- **Type:** file
- **Description:** Structured metadata in JSON format
- **Source:** Generated from DSpace API response
- **Size:** Small, typically 1-10KB
- **Format:** JSON file

#### `upspace_datatables.html`
- **Type:** file
- **Description:** DataTables HTML output
- **Source:** Generated from metadata using templates
- **Size:** Variable, typically 10-100KB
- **Format:** HTML document with DataTables

#### `index.html`
- **Type:** file
- **Description:** Index HTML file
- **Source:** Generated from metadata using templates
- **Size:** Variable, typically 10-100KB
- **Format:** HTML document

## Ignored Fields

Fields that are extracted but should be ignored for normal processing.

### Technical Fields
```json
{
  "uuid": "string",
  "id": "integer",
  "api_version": "string",
  "request_id": "string",
  "extracted_at": "datetime"
}
```

#### `uuid`
- **Source:** DSpace API response from uuid field
- **Type:** DSpace UUID identifier
- **Reason for Ignoring:** Internal DSpace system identifier with no research value

#### `id`
- **Source:** DSpace API response from id field
- **Type:** DSpace numeric identifier
- **Reason for Ignoring:** Internal DSpace system identifier with no research value

#### `api_version`
- **Source:** DSpace API response metadata
- **Type:** Technical API version information
- **Reason for Ignoring:** Technical metadata not relevant for content analysis

#### `request_id`
- **Source:** System-generated request tracking
- **Type:** Internal request tracking identifier
- **Reason for Ignoring:** Debugging/tracking field with no research value

#### `extracted_at`
- **Source:** System-generated during extraction
- **Type:** Processing timestamp
- **Reason for Ignoring:** Technical processing metadata not relevant for content analysis

## Data Quality Notes

### Field Availability
- **Always Available:** title, authors, handle_url, handle_id, uuid, id, extracted_at
- **Usually Available:** abstract, year, publisher, type, language
- **Sometimes Available:** doi, keywords, sdg_classifications
- **Conditional:** fulltext.pdf, metadata.json

### Reliability Factors
- **API Stability:** Very stable DSpace REST API
- **Rate Limiting:** 5 requests per minute
- **Institutional Focus:** University of Pretoria content
- **SDG Integration:** Unique SDG classifications

### Common Issues
- **Missing Content:** Some items lack full-text
- **Access Restrictions:** Some content may be restricted
- **Metadata Variations:** DSpace metadata may vary
- **PDF Availability:** Not all items have PDFs

## Usage Examples

### Basic API Search
```python
from pygetpapers.repositories.upspace import UPSpaceIntegration

# Initialize integration
upspace = UPSpaceIntegration()

# Search for papers
results = upspace.search_and_collect(
    query="machine learning",
    max_papers=10
)

# Access metadata
for paper in results["papers"]:
    print(f"Title: {paper['title']}")
    print(f"Authors: {', '.join(paper['authors'])}")
    print(f"Handle: {paper['handle_id']}")
    print(f"SDG Classifications: {', '.join(paper.get('sdg_classifications', []))}")
```

### Full Content Download
```python
# Download full content
for paper in results["papers"]:
    handle_id = paper["handle_id"]
    download_result = upspace.download_article_content(handle_id)
    
    if "error" not in download_result:
        print(f"Downloaded PDF: {download_result['pdf_file']}")
        print(f"Metadata: {download_result['metadata_file']}")
        print(f"DataTables: {download_result['datatables_file']}")
```

### SDG Analysis
```python
# Analyze SDG classifications
sdg_counts = {}
for paper in results["papers"]:
    sdgs = paper.get("sdg_classifications", [])
    for sdg in sdgs:
        sdg_counts[sdg] = sdg_counts.get(sdg, 0) + 1

for sdg, count in sdg_counts.items():
    print(f"{sdg}: {count} papers")
```

## Implementation Notes

### DSpace API Endpoints
- **Search:** `https://repository.up.ac.za/rest/api/core/items`
- **Item Details:** `https://repository.up.ac.za/rest/api/core/items/{uuid}`
- **Bitstreams:** `https://repository.up.ac.za/rest/api/core/items/{uuid}/bitstreams`
- **Collections:** `https://repository.up.ac.za/rest/api/core/collections`

### API Configuration
- **Authentication:** No authentication required for public content
- **Rate Limiting:** 5 requests per minute
- **Response Format:** JSON
- **Pagination:** Offset-based pagination

### Content Formats
- **PDF Access:** Direct PDF downloads from bitstreams
- **Metadata JSON:** Structured metadata export
- **DataTables HTML:** Interactive HTML tables
- **Index HTML:** Summary HTML pages

### SDG Classifications
- **SDG 1:** No Poverty
- **SDG 2:** Zero Hunger
- **SDG 3:** Good Health and Well-being
- **SDG 4:** Quality Education
- **SDG 5:** Gender Equality
- **SDG 6:** Clean Water and Sanitation
- **SDG 7:** Affordable and Clean Energy
- **SDG 8:** Decent Work and Economic Growth
- **SDG 9:** Industry, Innovation and Infrastructure
- **SDG 10:** Reduced Inequalities
- **SDG 11:** Sustainable Cities and Communities
- **SDG 12:** Responsible Consumption and Production
- **SDG 13:** Climate Action
- **SDG 14:** Life Below Water
- **SDG 15:** Life on Land
- **SDG 16:** Peace, Justice and Strong Institutions
- **SDG 17:** Partnerships for the Goals

## Related Documentation
- [Repository Summary](../repositories_summary.md)
- [File Size Alerts](../file-size-alerts.md)
- [Ignored Fields](../../pygetpapers/repositories/upspace/IGNORED_FIELDS.md)
- [UPSpace Integration](../../pygetpapers/repositories/upspace/upspace.py) 