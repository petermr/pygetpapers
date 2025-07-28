# Pygetpapers Repositories Summary

**Date:** July 28, 2025 (system date of generation)  
**Purpose:** Comprehensive overview of all pygetpapers repositories  
**Scope:** All 6 active repositories (biorxiv, europe_pmc, openalex, redalyc, scielo, upspace)

## Repository Overview

Pygetpapers supports 6 major scholarly repositories, each with unique capabilities and access methods. This document provides a comprehensive overview of all active repositories, their strengths, limitations, and use cases.

---

## Repository Comparison Matrix

| Repository | API Access | Web Scraping | Text Queries | Date Queries | PDF Downloads | XML Support | HTML Support | Rate Limits |
|------------|------------|--------------|--------------|--------------|---------------|-------------|--------------|-------------|
| **BioRxiv** | ✅ Limited | ✅ Advanced | ✅ Full | ✅ Full | ✅ Direct | ❌ | ✅ Direct | 1 req/sec |
| **Europe PMC** | ✅ Full | ❌ | ✅ Full | ✅ Full | ✅ Direct | ✅ JATS | ✅ Converted | 10 req/min |
| **OpenAlex** | ✅ Full | ❌ | ✅ Full | ✅ Full | ✅ Direct | ❌ | ❌ | 2 req/sec |
| **Redalyc** | ❌ | ✅ Selenium | ✅ Full | ❌ | ✅ Direct | ❌ | ✅ Direct | 1 req/sec |
| **SciELO** | ❌ | ✅ Advanced | ✅ Full | ❌ | ✅ Direct | ❌ | ✅ Direct | 1 req/sec |
| **UPSpace** | ✅ DSpace | ❌ | ✅ Full | ❌ | ✅ Direct | ❌ | ❌ | 5 req/min |

---

## 1. BioRxiv Repository

### Overview
BioRxiv is a preprint repository for biology that supports both API access and advanced web scraping for comprehensive content retrieval.

### Key Features
- **Dual Access**: API (date-only) + Web scraping (text queries)
- **Preprint Focus**: Early access to research before journal publication
- **Dual Repository**: Supports both bioRxiv and medRxiv
- **Direct Downloads**: HTML and PDF content available

### Strengths
- **Flexible Querying**: Combines API efficiency with scraping flexibility
- **Complete Metadata**: Rich metadata extraction
- **Direct Content**: Full HTML and PDF downloads
- **Rapid Updates**: Quick access to latest research

### Limitations
- **API Constraints**: Date-only queries via API
- **No XML/JATS**: No structured XML format support
- **Rate Limited**: 1 request/second for web scraping
- **No Supplementary Files**: No supplementary material access

### Best Use Cases
- Early research discovery
- Text-based searches in biology
- Preprint analysis
- Rapid literature review

---

## 2. Europe PMC Repository

### Overview
Europe PMC provides comprehensive access to biomedical literature with extensive secondary content and multiple file format support.

### Key Features
- **Full API Access**: Complete REST API with all features
- **Extensive Content**: XML, PDF, CSV, references, citations
- **JATS Support**: Structured XML format with conversion
- **Multiple Formats**: Rich secondary content support

### Strengths
- **Complete API**: Full-featured API with all capabilities
- **Rich Content**: Extensive secondary files and metadata
- **Structured Data**: JATS XML with HTML conversion
- **Comprehensive**: References, citations, supplementary files

### Limitations
- **Biomedical Focus**: Limited to biomedical literature
- **Complex Setup**: Requires JATS4R for XML conversion
- **Rate Limited**: 10 requests per minute
- **Large Files**: Some content can be very large

### Best Use Cases
- Biomedical research
- Systematic reviews
- Citation analysis
- Full-text analysis

---

## 3. OpenAlex Repository

### Overview
OpenAlex focuses on open access metadata with comprehensive citation data and PDF download capabilities.

### Key Features
- **Open Access Focus**: Comprehensive OA metadata
- **Citation Data**: Rich citation information
- **PDF Downloads**: Direct PDF access
- **Modern API**: RESTful API with pagination

### Strengths
- **Open Access**: Comprehensive OA literature coverage
- **Citation Data**: Rich citation and impact metrics
- **Modern API**: Well-designed REST API
- **Global Coverage**: Broad academic coverage

### Limitations
- **No XML/JATS**: No structured XML support
- **No HTML**: No HTML content
- **Rate Limited**: 2 requests per second
- **Metadata Focus**: Limited full-text content

### Best Use Cases
- Open access research
- Citation analysis
- Impact assessment
- Bibliometric studies

---

## 4. Redalyc Repository

### Overview
Redalyc provides access to Spanish and Portuguese language academic literature using advanced Selenium web scraping.

### Key Features
- **Selenium Scraping**: Advanced web scraping with browser automation
- **Multi-language**: Spanish and Portuguese content
- **Content Previews**: Rich content previews
- **Direct Downloads**: PDF and HTML content

### Strengths
- **Language Diversity**: Spanish/Portuguese language support
- **Rich Metadata**: Comprehensive metadata extraction
- **Content Previews**: Detailed content information
- **Direct Access**: PDF and HTML downloads

### Limitations
- **Web Scraping Only**: No API access
- **Language Limited**: Primarily Spanish/Portuguese
- **Rate Limited**: 1 request per second
- **Reliability Issues**: Web scraping may be unstable

### Best Use Cases
- Latin American research
- Spanish/Portuguese literature
- Regional studies
- Multi-language research

---

## 5. SciELO Repository

### Overview
SciELO uses advanced web scraping with multiple CSS selectors for robust metadata extraction from scientific literature.

### Key Features
- **Advanced Scraping**: Multiple CSS selector fallbacks
- **Multi-language**: Support for multiple languages
- **Collection-based**: Organized by collections
- **Robust Extraction**: Reliable metadata extraction

### Strengths
- **Robust Scraping**: Multiple fallback selectors
- **Multi-language**: Support for various languages
- **Collection Support**: Organized content structure
- **Reliable Extraction**: Stable metadata extraction

### Limitations
- **Web Scraping Only**: No API access
- **No Date Queries**: Limited to text-based searches
- **Rate Limited**: 1 request per second
- **No XML Support**: No structured data formats

### Best Use Cases
- Multi-language research
- Regional scientific literature
- Collection-based analysis
- Robust metadata extraction

---

## 6. UPSpace Repository

### Overview
UPSpace uses DSpace REST API with unique SDG (Sustainable Development Goals) classifications for institutional repository content.

### Key Features
- **DSpace API**: Institutional repository access
- **SDG Classifications**: Sustainable Development Goals metadata
- **Institutional Focus**: University repository content
- **Handle System**: DSpace handle identifiers

### Strengths
- **SDG Focus**: Unique SDG classifications
- **Institutional Content**: University repository access
- **Structured API**: DSpace REST API
- **Academic Focus**: Scholarly institutional content

### Limitations
- **Limited Scope**: Single institutional repository
- **No Date Queries**: Limited search capabilities
- **Rate Limited**: 5 requests per minute
- **No XML/HTML**: Limited content formats

### Best Use Cases
- SDG research
- Institutional repository analysis
- University research
- Academic content discovery



## Repository Selection Guide

### For Text-based Searches
1. **BioRxiv** - Biology preprints with advanced scraping
2. **Europe PMC** - Biomedical literature with full API
3. **OpenAlex** - Open access with citation data
4. **Redalyc** - Spanish/Portuguese literature
5. **SciELO** - Multi-language scientific literature

### For Date-based Searches
1. **Europe PMC** - Full date range support
2. **BioRxiv** - Date queries via API
3. **OpenAlex** - Date filtering available

### For Full-text Content
1. **Europe PMC** - JATS XML with HTML conversion
2. **BioRxiv** - Direct HTML and PDF
3. **Redalyc** - Direct PDF and HTML
4. **SciELO** - Direct PDF and HTML
5. **OpenAlex** - Direct PDF downloads

### For Citation Analysis
1. **OpenAlex** - Rich citation data
2. **Europe PMC** - Citation and reference data

### For Multi-language Research
1. **Redalyc** - Spanish and Portuguese
2. **SciELO** - Multiple languages
3. **Europe PMC** - Multi-language support

---

## Implementation Recommendations

### High-Volume Downloads
- Use **Europe PMC** for biomedical research
- Use **OpenAlex** for open access research

### Text-based Research
- Use **BioRxiv** for biology preprints
- Use **Redalyc** for Latin American research
- Use **SciELO** for multi-language studies

### Metadata Analysis
- Use **OpenAlex** for citation analysis
- Use **Europe PMC** for comprehensive metadata

### Full-text Analysis
- Use **Europe PMC** for structured XML
- Use **BioRxiv** for direct HTML
- Use **Redalyc/SciELO** for regional content

---

## Future Development

### Planned Enhancements
- **Repository-Specific Configurations**: Custom settings per repository
- **Advanced Filtering**: More sophisticated search capabilities
- **Content Conversion**: Enhanced format conversion
- **Performance Optimization**: Improved download speeds

### Integration Opportunities
- **Citation Networks**: Cross-repository citation analysis
- **Content Aggregation**: Unified search across repositories
- **Format Standardization**: Consistent output formats
- **Quality Metrics**: Content quality assessment

---

## Related Documentation
- [Repository Fields Schema](repository_fields_schema.md)
- [File Size Alerts](file-size-alerts.md)
- [Ignored Repositories](IGNORED_REPOSITORIES.md)
- [Repository Capabilities](REPOSITORIES.md)
- [Installation Guide](installation-and-deployment.md)
- [User Guide](user-guide.md) 