# Europe PMC Repository - Metadata Fields

**Date:** July 28, 2025 (system date of generation)  
**Repository:** europe_pmc  
**Access Method:** Full REST API  
**Base URL:** https://www.ebi.ac.uk/europepmc/webservices/rest/

## Overview

Europe PMC provides comprehensive access to biomedical literature with extensive secondary content and multiple file format support. The repository offers the richest metadata and content options among all pygetpapers repositories.

## Primary Fields (Immediate Information)

Fields that are directly available from the repository's search API or basic metadata extraction.

### Core Metadata
```json
{
  "title": "string",
  "authors": ["string"],
  "abstract": "string",
  "keywords": ["string"],
  "journal_title": "string",
  "pmcid": "string",
  "pmid": "string",
  "doi": "string",
  "publication_date": "string",
  "html_links": ["string"],
  "pdf_links": ["string"],
  "cursor_mark": "string"
}
```

### Field Descriptions

#### `title`
- **Type:** string
- **Description:** Full title of the publication
- **Source:** API response from search results
- **Example:** "Machine learning approaches for drug discovery: methods and applications"

#### `authors`
- **Type:** array of strings
- **Description:** List of author names
- **Source:** API response from author fields
- **Format:** "Surname, Given Names"
- **Example:** ["Smith, John", "Doe, Jane", "Johnson, Robert"]

#### `abstract`
- **Type:** string
- **Description:** Abstract text of the publication
- **Source:** API response from abstract field
- **Length:** Variable, typically 100-500 words
- **Example:** "This study investigates the application of machine learning..."

#### `keywords`
- **Type:** array of strings
- **Description:** Keywords or MeSH terms
- **Source:** API response from keyword fields
- **Example:** ["machine learning", "drug discovery", "artificial intelligence"]

#### `journal_title`
- **Type:** string
- **Description:** Full journal title
- **Source:** API response from journal field
- **Example:** "Nature Biotechnology"

#### `pmcid`
- **Type:** string
- **Description:** PubMed Central identifier
- **Source:** API response from pmcid field
- **Format:** "PMCXXXXXXXX"
- **Example:** "PMC12345678"

#### `pmid`
- **Type:** string
- **Description:** PubMed identifier
- **Source:** API response from pmid field
- **Format:** Numeric identifier
- **Example:** "12345678"

#### `doi`
- **Type:** string
- **Description:** Digital Object Identifier
- **Source:** API response from doi field
- **Format:** "10.XXXX/XXXXX"
- **Example:** "10.1038/nbt.1234"

#### `publication_date`
- **Type:** string
- **Description:** Publication date
- **Source:** API response from date fields
- **Format:** ISO date format
- **Example:** "2023-01-15"

#### `html_links`
- **Type:** array of strings
- **Description:** URLs to HTML versions
- **Source:** API response from link fields
- **Example:** ["https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12345678/"]

#### `pdf_links`
- **Type:** array of strings
- **Description:** URLs to PDF versions
- **Source:** API response from link fields
- **Example:** ["https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12345678/pdf/"]

#### `cursor_mark`
- **Type:** string
- **Description:** Pagination cursor for API requests
- **Source:** API response pagination metadata
- **Purpose:** Used for pagination in large result sets
- **Example:** "*"

## Secondary Fields (Further Requests)

Fields that require additional web scraping, file downloads, or extended API calls.

### Content Files
```json
{
  "fulltext.pdf": "file",
  "fulltext.xml": "file",
  "fulltext.xml.html": "file",
  "fulltext.csv": "file",
  "references": "file",
  "citations": "file",
  "supplementary_files": ["file"],
  "zip_files": "file"
}
```

### Status Flags
```json
{
  "pdfdownloaded": "boolean",
  "xmldownloaded": "boolean",
  "csvmade": "boolean",
  "htmldownloaded": "boolean"
}
```

### Field Descriptions

#### `fulltext.pdf`
- **Type:** file
- **Description:** Full-text PDF version
- **Source:** Direct download from PDF links
- **Size:** Variable, typically 1-10 MB
- **Format:** PDF document

#### `fulltext.xml`
- **Type:** file
- **Description:** JATS XML version
- **Source:** API endpoint for XML content
- **Size:** Variable, typically 100KB-2MB
- **Format:** JATS XML

#### `fulltext.xml.html`
- **Type:** file
- **Description:** HTML converted from XML
- **Source:** JATS4R conversion process
- **Size:** Variable, typically 200KB-3MB
- **Format:** HTML document

#### `fulltext.csv`
- **Type:** file
- **Description:** CSV export of metadata
- **Source:** Generated from metadata
- **Size:** Small, typically 1-10KB
- **Format:** CSV file

#### `references`
- **Type:** file
- **Description:** Reference list in XML format
- **Source:** API endpoint for references
- **Size:** Variable, typically 10-100KB
- **Format:** XML document

#### `citations`
- **Type:** file
- **Description:** Citation data in XML format
- **Source:** API endpoint for citations
- **Size:** Variable, typically 10-100KB
- **Format:** XML document

#### `supplementary_files`
- **Type:** array of files
- **Description:** Supplementary material files
- **Source:** API endpoint for supplementary files
- **Size:** Variable, can be very large
- **Format:** Various (PDF, images, data files)

#### `zip_files`
- **Type:** file
- **Description:** Zipped supplementary content
- **Source:** FTP endpoint for bulk downloads
- **Size:** Variable, can be very large
- **Format:** ZIP archive

#### `pdfdownloaded`
- **Type:** boolean
- **Description:** Whether PDF was successfully downloaded
- **Source:** System-generated flag
- **Example:** true

#### `xmldownloaded`
- **Type:** boolean
- **Description:** Whether XML was successfully downloaded
- **Source:** System-generated flag
- **Example:** true

#### `csvmade`
- **Type:** boolean
- **Description:** Whether CSV was successfully generated
- **Source:** System-generated flag
- **Example:** true

#### `htmldownloaded`
- **Type:** boolean
- **Description:** Whether HTML was successfully converted
- **Source:** System-generated flag
- **Example:** true

## Ignored Fields

Fields that are extracted but should be ignored for normal processing.

### Technical Fields
```json
{
  "cursor_mark": "string",
  "request_id": "string",
  "api_version": "string"
}
```

#### `cursor_mark`
- **Source:** API response pagination metadata
- **Type:** Internal pagination identifier
- **Reason for Ignoring:** Technical pagination field with no research value

#### `request_id`
- **Source:** API response headers or metadata
- **Type:** Internal request tracking identifier
- **Reason for Ignoring:** Debugging/tracking field with no research value

#### `api_version`
- **Source:** API response metadata
- **Type:** Technical API version information
- **Reason for Ignoring:** Technical metadata not relevant for content analysis

## Data Quality Notes

### Field Availability
- **Always Available:** title, authors, pmcid, pmid, publication_date
- **Usually Available:** abstract, journal_title, doi, html_links, pdf_links
- **Sometimes Available:** keywords, references, citations
- **Conditional:** supplementary_files, zip_files

### Reliability Factors
- **API Stability:** Very stable REST API
- **Rate Limiting:** 10 requests per minute
- **Content Consistency:** Well-structured data
- **Format Standards:** JATS XML compliance

### Common Issues
- **Large Files:** Supplementary files can be very large
- **Missing Content:** Some articles lack full-text
- **Format Variations:** XML structure may vary
- **Access Restrictions:** Some content may be restricted

## Usage Examples

### Basic API Search
```python
from pygetpapers.core.download_tools import DownloadTools

# Initialize download tools
tools = DownloadTools("europe_pmc")

# Search for papers
results = tools.post_query(
    url="https://www.ebi.ac.uk/europepmc/webservices/rest/searchPOST",
    data={"query": "machine learning drug discovery", "resultType": "core"}
)

# Access metadata
for paper in results["resultList"]["result"]:
    print(f"Title: {paper['title']}")
    print(f"Authors: {paper.get('authorString', 'N/A')}")
    print(f"PMCID: {paper.get('pmcid', 'N/A')}")
    print(f"DOI: {paper.get('doi', 'N/A')}")
```

### Full Content Download
```python
# Download XML content
xml_content = tools.get_request_endpoint_for_xml("PMC12345678")

# Download references
refs_content = tools.get_request_endpoint_for_references("PMC12345678", "PMC")

# Download citations
citations_content = tools.get_request_endpoint_for_citations("PMC12345678", "PMC")

# Download supplementary files
tools.getsupplementaryfiles("PMC12345678", "output_dir")
```

### JATS XML to HTML Conversion
```python
# Convert XML to HTML using JATS4R
from pygetpapers.tools.jats4r_integration import Jats4rIntegration

jats4r = Jats4rIntegration()
html_content = jats4r.convert_xml_to_html("fulltext.xml")
```

## Implementation Notes

### API Endpoints
- **Search:** `https://www.ebi.ac.uk/europepmc/webservices/rest/searchPOST`
- **XML:** `https://www.ebi.ac.uk/europepmc/webservices/rest/{identifier}/fullTextXML`
- **References:** `https://www.ebi.ac.uk/europepmc/webservices/rest/{identifier}/references`
- **Citations:** `https://www.ebi.ac.uk/europepmc/webservices/rest/{identifier}/citations`
- **Supplementary:** `https://www.ebi.ac.uk/europepmc/webservices/rest/{identifier}/supplementaryFiles`

### Rate Limiting
- **Search API:** 10 requests per minute
- **Content API:** 10 requests per minute
- **FTP Downloads:** No specific limit but bandwidth dependent

### Content Formats
- **JATS XML:** Structured XML following JATS standard
- **HTML Conversion:** JATS4R tool for XML to HTML conversion
- **PDF Access:** Direct PDF downloads available
- **Supplementary Files:** Various formats supported

### Pagination
- **Cursor-based:** Uses cursor_mark for pagination
- **Large Results:** Supports large result sets efficiently
- **Resume Capability:** Can resume interrupted downloads

## Related Documentation
- [Repository Summary](../repositories_summary.md)
- [File Size Alerts](../file-size-alerts.md)
- [JATS4R Integration](../../pygetpapers/tools/jats4r_integration.py)
- [Ignored Fields](../../pygetpapers/repositories/europe_pmc/IGNORED_FIELDS.md) 