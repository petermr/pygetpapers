# OpenAlex Repository Capabilities

## Overview
OpenAlex is a comprehensive metadata repository that provides rich bibliographic data with open access indicators through a REST API. It offers very generous rate limits but focuses on metadata only.

## Capabilities Summary

| Feature | Status | Details |
|---------|--------|---------|
| **API Access** | ✅ REST API | Comprehensive REST API with 100,000 requests/day |
| **Web Scraping** | ❌ | Not supported - API only |
| **Metadata** | ✅ Complete | Rich bibliographic metadata with citations |
| **PDF Downloads** | ❌ | No full-text content access |
| **XML/JATS** | ❌ | No full-text content access |
| **HTML** | ❌ | No full-text content access |
| **Figures** | ❌ | No full-text content access |
| **Tables** | ❌ | No full-text content access |
| **Supplementary Files** | ❌ | No full-text content access |

## Strengths

### API Capabilities
- **Rate Limit**: 100,000 requests per day (very generous)
- **Base URL**: `https://api.openalex.org/`
- **Endpoints**: works, authors, venues, institutions
- **Date Format**: YYYY-MM-DD
- **Query Types**: Text search, date range, author search, journal search, subject search, institution search

### Rich Metadata
- **Comprehensive Coverage**: Extensive bibliographic database
- **Open Access Indicators**: Clear open access status
- **Citation Data**: Rich citation information
- **Author Profiles**: Detailed author information
- **Institution Data**: Institutional affiliations

### Bibliographic Relationships
- **Work Relationships**: Connections between works
- **Author Networks**: Author collaboration networks
- **Venue Information**: Journal and conference data
- **Institution Networks**: Institutional collaboration patterns
- **Subject Classifications**: Detailed subject categorization

## Limitations

### Content Access
- **Metadata Only**: No full-text content access
- **No PDF Downloads**: Cannot download PDF files
- **No XML/JATS**: No structured full-text formats
- **No HTML**: No HTML content access

### Technical Constraints
- **No Web Scraping**: API-only access method
- **No Full-Text**: Limited to bibliographic data only
- **No Figures/Tables**: No access to figures or tables

### Content Scope
- **No Supplementary Files**: No supplementary material access
- **No Direct Content**: No direct access to article content
- **Metadata Focus**: Primarily bibliographic relationships

## Usage Recommendations

### Best For
- **Open Access Research**: Open access indicator analysis
- **Citation Analysis**: Comprehensive citation data
- **Author Networks**: Author collaboration studies
- **Institutional Analysis**: Institutional research patterns
- **Large-Scale Studies**: High-volume metadata analysis

### Query Examples
```bash
# Basic search
pygetpapers --query "climate change adaptation" --api openalex --limit 100

# Open access search
pygetpapers --query "machine learning" --api openalex --limit 500

# Date range search
pygetpapers --query "artificial intelligence" --api openalex --startdate 2023-01-01 --enddate 2023-12-31 --limit 1000

# Author search
pygetpapers --query "author:Smith J" --api openalex --limit 50
```

## Configuration

### Rate Limiting
- **Requests per day**: 100,000 (very generous)
- **Delay between requests**: Minimal (due to high limits)
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
- **Institution Search**: Institutional searches

## Technical Implementation

### API Structure
- **Works Endpoint**: `https://api.openalex.org/works`
- **Authors Endpoint**: `https://api.openalex.org/authors`
- **Venues Endpoint**: `https://api.openalex.org/venues`
- **Institutions Endpoint**: `https://api.openalex.org/institutions`
- **Response Format**: JSON with rich relationships

### Metadata Fields
- **OpenAlex ID**: Unique identifier
- **DOI**: Digital Object Identifier
- **Title**: Article title
- **Authors**: Author information with affiliations
- **Abstract**: Abstract text (where available)
- **Journal**: Journal information
- **Publication Date**: Publication date
- **Citations**: Citation count and data
- **Open Access**: Open access status

## Unique Features

### Open Access Indicators
- **Clear Status**: Explicit open access indicators
- **License Information**: Open access license details
- **Access Type**: Type of open access (gold, green, etc.)
- **Repository Information**: Repository hosting details

### Citation Data
- **Citation Counts**: Comprehensive citation information
- **Citation Networks**: Citation relationship data
- **Impact Metrics**: Various impact indicators
- **Temporal Analysis**: Citation patterns over time

### Author Networks
- **Collaboration Patterns**: Author collaboration networks
- **Institutional Affiliations**: Author institutional data
- **Research Areas**: Author research specialization
- **Publication History**: Author publication patterns

## Maintenance Notes

**Last Updated**: January 2025

**Update Frequency**: Update when:
- API rate limits change
- New endpoints are added
- Metadata schema changes
- New capabilities are implemented

**Information Sources**:
- `config.ini` configuration file
- `openalex.py` implementation
- OpenAlex API documentation
- Testing results

## Alternative Approaches

### For Full-Text Access
- **Europe PMC**: For biomedical full-text
- **BioRxiv**: For biology preprints
- **Redalyc**: For Latin American content
- **SciELO**: For regional content

### For Comprehensive Research
- **Crossref**: For general bibliographic data
- **Europe PMC**: For biomedical content
- **BioRxiv**: For preprint access

---

*OpenAlex is ideal for large-scale bibliographic analysis and open access research, offering the most generous rate limits among all repositories.* 