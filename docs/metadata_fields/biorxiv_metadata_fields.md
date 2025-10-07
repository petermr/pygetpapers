# BioRxiv Repository - Metadata Fields

**Date:** July 28, 2025 (system date of generation)  
**Repository:** bioRxiv  
**Access Method:** API (date-only) + Web Scraping (text queries)  
**Base URL:** https://www.biorxiv.org/

## Overview

BioRxiv provides comprehensive metadata for biology preprints through both API access and advanced web scraping. The repository supports both bioRxiv and medRxiv content with rich metadata extraction.

## Primary Fields (Immediate Information)

Fields that are directly available from the repository's search API or basic metadata extraction.

### Core Metadata
```json
{
  "title": "string",
  "authors": ["string"],
  "doi": "string",
  "biorxiv_id": "string",
  "journal": "string",
  "publication_date": "string",
  "subject_areas": ["string"],
  "url": "string",
  "extracted_at": "datetime"
}
```

### Field Descriptions

#### `title`
- **Type:** string
- **Description:** Full title of the preprint
- **Source:** Web scraping from citation elements
- **Example:** "Environmental fungi from cool and warm neighborhoods in the urban heat island of Baltimore City show differences in thermal susceptibility and pigmentation"

#### `authors`
- **Type:** array of strings
- **Description:** List of author names
- **Source:** Web scraping from author elements
- **Format:** "Given Names Surname"
- **Example:** ["Daniel F. Q. Smith", "Madhura Kulkarni", "Alexa Bencomo"]

#### `doi`
- **Type:** string
- **Description:** Digital Object Identifier
- **Source:** Web scraping from DOI elements
- **Format:** "10.1101/XXXXXXXX"
- **Example:** "10.1101/2023.11.10.566554"

#### `biorxiv_id`
- **Type:** string
- **Description:** BioRxiv-specific identifier
- **Source:** Web scraping from metadata elements
- **Format:** "YYYY.MM.DD.XXXXXXX"
- **Example:** "2023.11.10.566554"

#### `journal`
- **Type:** string
- **Description:** Target journal for publication
- **Source:** Web scraping from metadata elements
- **Example:** "Nature"

#### `publication_date`
- **Type:** string
- **Description:** Date when preprint was posted
- **Source:** Web scraping from date elements
- **Format:** ISO date format
- **Example:** "2023-11-10"

#### `subject_areas`
- **Type:** array of strings
- **Description:** Subject area classifications
- **Source:** Web scraping from subject elements
- **Example:** ["Ecology", "Environmental Science"]

#### `url`
- **Type:** string
- **Description:** Direct URL to the preprint
- **Source:** Web scraping from title links
- **Format:** "https://www.biorxiv.org/content/10.1101/XXXXXXXX"
- **Example:** "https://www.biorxiv.org/content/10.1101/2023.11.10.566554"

#### `extracted_at`
- **Type:** datetime
- **Description:** Timestamp when metadata was extracted
- **Source:** System-generated during extraction
- **Format:** ISO datetime format
- **Example:** "2025-07-27T10:30:00.000Z"

## Secondary Fields (Further Requests)

Fields that require additional web scraping, file downloads, or extended API calls.

### Content Fields
```json
{
  "fulltext_html": "string (HTML content)",
  "pdf_url": "string",
  "file_size": "integer",
  "download_timestamp": "datetime",
  "jsondownloaded": "boolean"
}
```

### Field Descriptions

#### `fulltext_html`
- **Type:** string (HTML content)
- **Description:** Full HTML content of the preprint
- **Source:** Web scraping from full-text pages
- **Access:** Requires additional page request
- **Size:** Variable, typically 50KB-500KB

#### `pdf_url`
- **Type:** string
- **Description:** Direct URL to PDF version
- **Source:** Web scraping from PDF links
- **Format:** "https://www.biorxiv.org/content/10.1101/XXXXXXXX.full.pdf"
- **Example:** "https://www.biorxiv.org/content/10.1101/2023.11.10.566554.full.pdf"

#### `file_size`
- **Type:** integer
- **Description:** Size of downloaded content in bytes
- **Source:** Calculated after download
- **Example:** 102400

#### `download_timestamp`
- **Type:** datetime
- **Description:** When content was downloaded
- **Source:** System-generated during download
- **Format:** ISO datetime format
- **Example:** "2025-07-27T10:35:00.000Z"

#### `jsondownloaded`
- **Type:** boolean
- **Description:** Whether metadata was successfully downloaded
- **Source:** System-generated flag
- **Example:** true

## Ignored Fields

Fields that are extracted but should be ignored for normal processing.

### Internal System Fields
```json
{
  "pisa_id": "string",
  "apath": "string"
}
```

#### `pisa_id`
- **Source:** `data-pisa` HTML attribute
- **Type:** Internal system identifier
- **Reason for Ignoring:** Internal BioRxiv system identifier with no research value

#### `apath`
- **Source:** `data-apath` HTML attribute
- **Type:** Internal routing/path identifier
- **Reason for Ignoring:** Internal BioRxiv routing identifier with no research value

## Data Quality Notes

### Field Availability
- **Always Available:** title, authors, doi, biorxiv_id, extracted_at
- **Usually Available:** journal, publication_date, url
- **Sometimes Available:** subject_areas, pdf_url
- **Conditional:** fulltext_html, file_size, download_timestamp

### Reliability Factors
- **Web Scraping Stability:** Subject to website changes
- **Rate Limiting:** 1 request per second limit
- **Content Availability:** Some preprints may be removed or updated
- **Format Consistency:** HTML structure may vary

### Common Issues
- **Missing Authors:** Sometimes author information is incomplete
- **Delayed Updates:** Publication dates may not reflect latest versions
- **Broken Links:** PDF URLs may become invalid
- **Scraping Failures:** Website changes can break extraction

## Usage Examples

### Basic Metadata Extraction
```python
from pygetpapers.repositories.biorxiv import BioRxivIntegration

# Initialize scraper
biorxiv = BioRxivIntegration()

# Search for papers
results = biorxiv.search_and_collect(
    query="urban heat island",
    max_papers=10
)

# Access metadata
for paper in results["papers"]:
    print(f"Title: {paper['title']}")
    print(f"Authors: {', '.join(paper['authors'])}")
    print(f"DOI: {paper['doi']}")
    print(f"BioRxiv ID: {paper['biorxiv_id']}")
```

### Full Content Download
```python
# Download full content
for paper in results["papers"]:
    doi = paper["doi"]
    download_result = biorxiv.scraper.download_paper_full_content(doi)
    
    if "error" not in download_result:
        print(f"Downloaded: {download_result['landing_file']}")
        print(f"PDF URL: {download_result['pdf_url']}")
        print(f"File size: {download_result['landing_size_bytes']} bytes")
```

## Implementation Notes

### Repository Structure and Naming Conventions

#### Directory Structure
```
{user_repo_directory}/
├── datatables.html                    # Main DataTables interface
├── lantana_papers_data.json           # Paper metadata
└── pdfs/
    ├── {paper_id_1}/
    │   ├── fulltext.pdf               # Original PDF (manually downloaded)
    │   ├── fulltext.html              # Downloaded HTML content
    │   └── fulltext.pdf.html          # PDF converted to HTML (derived)
    ├── {paper_id_2}/
    │   ├── fulltext.pdf
    │   ├── fulltext.html
    │   └── fulltext.pdf.html
    └── ...
```

#### Naming Conventions
- **Repository Directory**: User-defined (e.g., `./examples/lantana_biorxiv/`)
- **Article Subdirectories**: Named by paper ID (e.g., `/292722/`, `/126490/`)
- **Content Files**: Reserved names indicating type and format:
  - `fulltext.pdf` - Original PDF content
  - `fulltext.html` - Downloaded HTML content
  - `fulltext.pdf.html` - PDF converted to HTML (derived content)
- **DataTables Location**: `{repo_directory}/datatables.html`

#### PDF Download Workflow
1. **DataTables Interface**: Located at `{repo_directory}/datatables.html`
2. **PDF Links**: Point to BioRxiv repository URLs
3. **Manual Download**: User clicks PDF cells and saves to `/{paper_id}/fulltext.pdf`
4. **Local Detection**: DataTables shows green "Local PDF" when file exists

### Web Scraping Selectors
- **Title:** `span.highwire-cite-title a.highwire-cite-linked-title`
- **Authors:** `div.highwire-cite-authors span.highwire-citation-author`
- **DOI:** `span.highwire-cite-metadata-doi`
- **Journal:** `span.highwire-cite-metadata-journal`
- **BioRxiv ID:** `span.highwire-cite-metadata-pages`

### API Limitations
- **Date-only Queries:** API supports date ranges only
- **No Text Search:** Text queries require web scraping
- **Rate Limits:** 1000 requests per hour for API
- **Limited Metadata:** API provides basic information only

### Web Scraping Advantages
- **Text Queries:** Full text search support
- **Rich Metadata:** Comprehensive field extraction
- **Content Access:** Direct HTML and PDF downloads
- **Flexible Search:** Multiple search parameters

## Related Documentation
- [Repository Summary](../repositories_summary.md)
- [File Size Alerts](../file-size-alerts.md)
- [Ignored Fields](../../pygetpapers/repositories/biorxiv/IGNORED_FIELDS.md)
- [Repository Capabilities](../../pygetpapers/repositories/biorxiv/REPOSITORY_CAPABILITIES.md) 