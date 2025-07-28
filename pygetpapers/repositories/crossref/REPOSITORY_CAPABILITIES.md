# Crossref Repository Capabilities

## Overview
Crossref is a comprehensive metadata repository that provides rich bibliographic data through a REST API. It focuses on metadata only, with no full-text content access.

## Capabilities Summary

| Feature | Status | Details |
|---------|--------|---------|
| **API Access** | ✅ REST API | Comprehensive REST API with 500 requests/hour |
| **Web Scraping** | ❌ | Not supported - API only |
| **Metadata** | ✅ Complete | Rich bibliographic metadata |
| **PDF Downloads** | ❌ | No full-text content access |
| **XML/JATS** | ❌ | No full-text content access |
| **HTML** | ❌ | No full-text content access |
| **Figures** | ❌ | No full-text content access |
| **Tables** | ❌ | No full-text content access |
| **Supplementary Files** | ❌ | No full-text content access |

## Strengths

### API Capabilities
- **Rate Limit**: 500 requests per hour
- **Base URL**: `https://api.crossref.org/`
- **Endpoints**: works, journals, funders
- **Date Format**: YYYY-MM-DD
- **Query Types**: Text search, date range, author search, journal search, subject search, DOI search

### Rich Metadata
- **Comprehensive Coverage**: Extensive bibliographic database
- **DOI-Based Access**: Direct DOI lookups
- **Multiple Export Formats**: JSON, XML, CSV
- **Publisher Information**: Rich publisher metadata
- **Type Classification**: Article type identification

### Bibliographic Data
- **Authors**: Complete author information
- **Journals**: Journal metadata and relationships
- **Citations**: Citation data where available
- **References**: Reference lists where available
- **Open Access**: Open access indicators

## Limitations

### Content Access
- **Metadata Only**: No full-text content access
- **No PDF Downloads**: Cannot download PDF files
- **No XML/JATS**: No structured full-text formats
- **No HTML**: No HTML content access

### Technical Constraints
- **No Web Scraping**: API-only access method
- **Rate Limited**: 500 requests per hour maximum
- **No Full-Text**: Limited to bibliographic data only

### Content Scope
- **No Figures/Tables**: No access to figures or tables
- **No Supplementary Files**: No supplementary material access
- **No Citations**: Limited citation information

## Usage Recommendations

### Best For
- **Bibliographic Research**: Comprehensive literature searches
- **DOI Resolution**: DOI-based metadata retrieval
- **Publisher Analysis**: Publisher and journal information
- **Open Access Studies**: Open access indicator analysis
- **Citation Analysis**: Where citation data is available

### Query Examples
```bash
# Basic search
pygetpapers --query "climate change adaptation" --api crossref --limit 50

# DOI lookup
pygetpapers --query "10.1038/nature12345" --api crossref --limit 1

# Date range search
pygetpapers --query "machine learning" --api crossref --startdate 2023-01-01 --enddate 2023-12-31 --limit 100

# Author search
pygetpapers --query "author:Smith J" --api crossref --limit 20
```

## Configuration

### Rate Limiting
- **Requests per hour**: 500
- **Delay between requests**: 2 seconds (recommended)
- **Timeout**: 30 seconds

### Supported Formats
- **Metadata**: JSON, XML, CSV
- **No Full Text**: No PDF, XML, or HTML content
- **No Supplementary**: No supplementary files

### Query Types
- **Text Search**: Full-text search across metadata
- **Date Range**: Publication date filtering
- **Author Search**: Author name searches
- **Journal Search**: Journal-specific searches
- **Subject Search**: Subject classification searches
- **DOI Search**: Direct DOI lookups

## Technical Implementation

### API Structure
- **Works Endpoint**: `https://api.crossref.org/works`
- **Journals Endpoint**: `https://api.crossref.org/journals`
- **Funders Endpoint**: `https://api.crossref.org/funders`
- **Response Format**: JSON with rich metadata

### Metadata Fields
- **DOI**: Digital Object Identifier
- **Title**: Article title
- **Authors**: Author information
- **Abstract**: Abstract text (where available)
- **Journal**: Journal information
- **Publication Date**: Publication date
- **Publisher**: Publisher information
- **Type**: Content type classification

## Maintenance Notes

**Last Updated**: January 2025

**Update Frequency**: Update when:
- API rate limits change
- New endpoints are added
- Metadata schema changes
- New capabilities are implemented

**Information Sources**:
- `config.ini` configuration file
- `crossref_new.py` implementation
- Crossref API documentation
- Testing results

## Alternative Approaches

### For Full-Text Access
- **Europe PMC**: For biomedical full-text
- **BioRxiv**: For biology preprints
- **Redalyc**: For Latin American content
- **SciELO**: For regional content

### For Comprehensive Research
- **OpenAlex**: For open access indicators
- **Europe PMC**: For biomedical content
- **BioRxiv**: For preprint access

---

*Crossref is the premier choice for comprehensive bibliographic metadata and DOI resolution, though it does not provide full-text content access.* 