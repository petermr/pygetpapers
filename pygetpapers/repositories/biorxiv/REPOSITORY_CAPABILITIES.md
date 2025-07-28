# BioRxiv Repository Capabilities

## Overview
BioRxiv is a preprint repository for biology that supports both API access and advanced web scraping for comprehensive content retrieval.

## Capabilities Summary

| Feature | Status | Details |
|---------|--------|---------|
| **API Access** | ✅ Limited API | API with 1000 requests/hour (date-only queries) |
| **Web Scraping** | ✅ Advanced | Advanced web scraping with 1 request/second |
| **Metadata** | ✅ Complete | Complete metadata extraction |
| **PDF Downloads** | ✅ Direct | Direct PDF downloads available |
| **XML/JATS** | ❌ | No XML/JATS support |
| **HTML** | ✅ Direct | Direct HTML downloads |
| **Figures** | ❌ | No explicit figure extraction |
| **Tables** | ❌ | No explicit table extraction |
| **Supplementary Files** | ❌ | No supplementary file support |

## Strengths

### Dual Access Approach
- **API Access**: 1000 requests per hour for date-based queries
- **Web Scraping**: Advanced scraping for text-based searches
- **Flexible Querying**: Combines API efficiency with scraping flexibility

### Content Access
- **Direct HTML Downloads**: Full HTML content available
- **Direct PDF Downloads**: PDF files available for download
- **Complete Metadata**: Rich metadata extraction
- **Dual Repository Support**: Both bioRxiv and medRxiv

### Preprint Focus
- **Early Access**: Access to preprints before journal publication
- **Rapid Updates**: Quick access to latest research
- **Open Access**: All content is freely available

## Limitations

### API Constraints
- **Date-Only Queries**: API limited to date-based searches only
- **No Text Search**: Text queries require web scraping
- **Limited Metadata**: API provides basic metadata only

### Technical Constraints
- **No XML/JATS**: No structured XML format support
- **No Figures/Tables**: No explicit extraction of figures or tables
- **No Supplementary Files**: No supplementary material access
- **Rate Limited**: 1 request/second for web scraping

### Content Scope
- **Biology Focus**: Limited to biological sciences
- **Preprint Only**: No peer-reviewed journal content
- **No Citations**: Limited citation information

## Usage Recommendations

### Best For
- **Preprint Research**: Early access to biological research
- **Text-Based Searches**: Complex query requirements
- **Rapid Literature Review**: Quick access to latest findings
- **Dual Repository Analysis**: Combined bioRxiv/medRxiv searches

### Query Examples
```bash
# Date-based search (API)
pygetpapers --query "" --api biorxiv --startdate 2024-01-01 --enddate 2024-12-31 --limit 50 -p

# Text-based search (web scraping)
pygetpapers --query "climate change adaptation" --api biorxiv --limit 20 -p

# Combined approach
pygetpapers --query "cancer immunotherapy" --api biorxiv --startdate 2023-01-01 --enddate 2023-12-31 --limit 100 -p
```

## Configuration

### Rate Limiting
- **API Requests per hour**: 1000
- **Web Scraping**: 1 request per second
- **Delay between requests**: 1 second (scraping)
- **Timeout**: 30 seconds

### Supported Formats
- **Metadata**: JSON, CSV
- **Full Text**: HTML, PDF
- **No XML**: No structured XML format
- **No Supplementary**: No supplementary files

## Technical Implementation

### API Approach
- **Base URL**: `https://api.biorxiv.org/details/`
- **Endpoints**: biorxiv, medrxiv
- **Date Format**: YYYY-MM-DD
- **Query Types**: Date range only

### Web Scraping Approach
- **Base URL**: `https://www.biorxiv.org/`
- **Search URL**: `https://www.biorxiv.org/search/`
- **Pagination**: Supported
- **Max Papers per Page**: 25
- **User Agent**: Mozilla/5.0 (compatible; pygetpapers/1.0)

## Maintenance Notes

**Last Updated**: January 2025

**Update Frequency**: Update when:
- API rate limits change
- Web scraping patterns change
- New capabilities are implemented
- Repository policies change

**Information Sources**:
- `config.ini` configuration file
- `biorxiv_advanced_scraper.py` implementation
- BioRxiv API documentation
- Web scraping testing results

---

*BioRxiv provides flexible access to preprint literature through its dual API/web scraping approach, making it ideal for early access to biological research.* 