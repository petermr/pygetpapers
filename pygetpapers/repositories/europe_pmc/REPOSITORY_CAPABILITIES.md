# Europe PMC Repository Capabilities

## Overview
Europe PMC is a comprehensive biomedical repository that provides access to life sciences literature through a REST API.

## Capabilities Summary

| Feature | Status | Details |
|---------|--------|---------|
| **API Access** | ✅ REST API | Comprehensive REST API with 1000 requests/hour |
| **Web Scraping** | ❌ | Not supported - API only |
| **Metadata** | ✅ Complete | Rich metadata including PMID, PMCID, DOI, citations, references |
| **PDF Downloads** | ✅ Direct | Direct PDF downloads available |
| **XML/JATS** | ✅ JATS | Full JATS XML support with HTML conversion |
| **HTML** | ✅ Generated | HTML generated from XML using converters |
| **Figures** | ❌ | No explicit figure extraction |
| **Tables** | ❌ | No explicit table extraction |
| **Supplementary Files** | ✅ ZIP/PDF/TXT | Supplementary file support |

## Strengths

### API Capabilities
- **Rate Limit**: 1000 requests per hour
- **Endpoints**: search, fetch, citations
- **Date Format**: YYYY-MM-DD
- **Query Types**: Text search, date range, author search, journal search, subject search, citations

### Content Access
- **Full JATS XML Support**: Complete XML downloads with HTML conversion
- **Direct PDF Downloads**: PDF files available for download
- **Rich Metadata**: Comprehensive bibliographic information
- **Supplementary Files**: Support for ZIP, PDF, and TXT supplementary materials

### Biomedical Focus
- **Extensive Coverage**: Comprehensive biomedical and life sciences literature
- **PubMed Integration**: Seamless integration with PubMed data
- **Professional Standards**: Uses industry-standard JATS format

## Limitations

### Content Scope
- **Biomedical Focus Only**: Limited to health sciences and life sciences
- **No Figures/Tables**: No explicit extraction of figures or tables
- **Query Format Requirements**: Requires specific query formats

### Technical Constraints
- **No Web Scraping**: API-only access method
- **Rate Limited**: 1000 requests per hour maximum
- **No Direct HTML**: HTML must be generated from XML

## Usage Recommendations

### Best For
- **Biomedical Research**: Primary literature in health sciences
- **Full-Text Analysis**: Complete article content with metadata
- **Systematic Reviews**: Comprehensive literature searches
- **Citation Analysis**: Rich citation and reference data

### Query Examples
```bash
# Basic search
pygetpapers --query "climate change AND adaptation" --api europe_pmc --limit 10 -x -p --fulltext_html

# Date range search
pygetpapers --query "cancer immunotherapy" --api europe_pmc --startdate 2023-01-01 --enddate 2023-12-31 --limit 50 -x

# Author search
pygetpapers --query "author:Smith J" --api europe_pmc --limit 20 -x -p
```

## Configuration

### Rate Limiting
- **Requests per hour**: 1000
- **Delay between requests**: 6 seconds (recommended)
- **Timeout**: 30 seconds

### Supported Formats
- **Metadata**: JSON, CSV, XML
- **Full Text**: XML (JATS), PDF
- **HTML**: Generated from XML
- **Supplementary**: ZIP, PDF, TXT

## Maintenance Notes

**Last Updated**: January 2025

**Update Frequency**: Update when:
- API rate limits change
- New endpoints are added
- Content policies change
- New capabilities are implemented

**Information Sources**:
- `config.ini` configuration file
- `europe_pmc.py` implementation
- Europe PMC API documentation
- Testing results

---

*Europe PMC is the premier choice for biomedical research with its comprehensive API, rich metadata, and full-text access capabilities.* 