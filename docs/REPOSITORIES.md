# Repository Output Capabilities Analysis

## Overview
This document provides a comprehensive analysis of the 8 repositories supported by pygetpapers, including their output capabilities, rate limits, and key limitations.

## Summary Table

| Repository | API Access | Web Scraping | Metadata | PDF | XML/JATS | HTML | Figures | Tables | Supplementary | Rate Limits | Key Limitations |
|------------|------------|--------------|----------|-----|----------|------|---------|--------|---------------|-------------|-----------------|
| **Europe PMC** | ✅ REST API | ❌ | ✅ Complete | ✅ Direct | ✅ JATS | ✅ Generated | ❌ | ❌ | ✅ ZIP/PDF/TXT | 1000/hr | Biomedical focus only |
| **BioRxiv** | ✅ Limited API | ✅ Advanced | ✅ Complete | ✅ Direct | ❌ | ✅ Direct | ❌ | ❌ | ❌ | 1000/hr API, 1/sec scraping | API: date-only queries |
| **arXiv** | ❌ Disabled | ❌ Disabled | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | N/A | Policy prohibits automated access |
| **Crossref** | ✅ REST API | ❌ | ✅ Complete | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | 500/hr | Metadata only, no full-text |
| **OpenAlex** | ✅ REST API | ❌ | ✅ Complete | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | 100,000/day | Metadata only, no full-text |
| **Redalyc** | ❌ | ✅ Advanced | ✅ Complete | ✅ Direct | ✅ Direct | ✅ Direct | ❌ | ❌ | ✅ PDF/TXT | 1/sec | Spanish/Portuguese focus |
| **SciELO** | ❌ | ✅ Advanced | ✅ Complete | ✅ Direct | ✅ Direct | ✅ Direct | ❌ | ❌ | ✅ PDF/TXT | 2/sec | Latin America focus |
| **UPSpace** | ✅ REST API | ❌ | ✅ Complete | ✅ Direct | ❌ | ❌ | ❌ | ❌ | ❌ | 1/sec | Institutional repository |

## Detailed Analysis by Repository

### 1. **Europe PMC** 
**Strengths:**
- Comprehensive REST API with 1000 requests/hour
- Full JATS XML support with HTML conversion
- Direct PDF downloads
- Rich metadata (PMID, PMCID, DOI, citations, references)
- Supplementary file support (ZIP, PDF, TXT)
- Biomedical focus with extensive coverage

**Limitations:**
- Biomedical/health sciences focus only
- No explicit figure/table extraction
- Requires specific query formats

### 2. **BioRxiv**
**Strengths:**
- Dual approach: API + advanced web scraping
- Direct HTML and PDF downloads
- Complete metadata extraction
- Supports both bioRxiv and medRxiv
- Rich content with full-text access

**Limitations:**
- API limited to date-based queries only
- Web scraping required for text searches
- No XML/JATS support
- No explicit figure/table extraction

### 3. **arXiv**
**Status: DISABLED**
- Completely disabled due to arXiv's policy against automated downloads
- No access to any content
- Policy prohibits scraping or bulk downloads

### 4. **Crossref**
**Strengths:**
- Comprehensive metadata API (500 requests/hour)
- Rich bibliographic data
- DOI-based access
- Multiple export formats (JSON, XML)

**Limitations:**
- Metadata only - no full-text content
- No PDF, XML, or HTML downloads
- No figure/table access
- No supplementary files

### 5. **OpenAlex**
**Strengths:**
- Very high rate limit (100,000 requests/day)
- Comprehensive metadata with citations
- Open access indicators
- Rich bibliographic relationships

**Limitations:**
- Metadata only - no full-text content
- No PDF, XML, or HTML downloads
- No figure/table access
- No supplementary files

### 6. **Redalyc**
**Strengths:**
- Advanced web scraping capabilities
- Direct PDF and XML downloads
- HTML content extraction
- Multilingual support (Spanish, Portuguese, English)
- Supplementary file support

**Limitations:**
- Web scraping only (no API)
- Rate limited to 1 request/second
- Latin American focus
- No explicit figure/table extraction

### 7. **SciELO**
**Strengths:**
- Advanced web scraping with encoding detection
- Direct PDF and XML downloads
- HTML content extraction
- Multilingual support
- Supplementary file support
- Latin American and African focus

**Limitations:**
- Web scraping only (no API)
- Rate limited to 2 requests/second
- Regional focus
- No explicit figure/table extraction

### 8. **UPSpace**
**Strengths:**
- Modern DSpace REST API
- Direct PDF downloads
- Rich metadata with SDG classifications
- Institutional repository with academic focus
- Clean JSON data structure

**Limitations:**
- No XML/JATS support
- No HTML generation
- No explicit figure/table extraction
- No supplementary files
- Institutional focus (University of Pretoria)

## Key Findings

### **Rate Limiting Considerations**
- **Most Generous**: OpenAlex (100,000/day)
- **Moderate**: Europe PMC (1000/hour), Crossref (500/hour)
- **Conservative**: BioRxiv (1000/hour API + 1/sec scraping), Redalyc (1/sec), UPSpace (1/sec)
- **Disabled**: arXiv

### **Content Access Patterns**
- **Full-Text Champions**: Europe PMC, BioRxiv, Redalyc, SciELO
- **Metadata Only**: Crossref, OpenAlex
- **Institutional**: UPSpace
- **Disabled**: arXiv

### **Repository-Specific Quirks**
1. **BioRxiv**: API vs web scraping dichotomy
2. **Europe PMC**: Biomedical focus with JATS support
3. **Redalyc/SciELO**: Regional focus with multilingual content
4. **UPSpace**: SDG classifications as unique feature
5. **Crossref/OpenAlex**: Rich metadata but no full-text
6. **arXiv**: Completely disabled due to policy

### **Recommended Usage Strategy**
- **For full-text research**: Europe PMC, BioRxiv, Redalyc, SciELO
- **For metadata analysis**: Crossref, OpenAlex
- **For institutional content**: UPSpace
- **Avoid**: arXiv (disabled)

## Maintenance Notes

**Last Updated**: January 2025

**Update Frequency**: This document should be updated when:
- New repositories are added
- Rate limits change
- API endpoints are modified
- Repository policies change
- New capabilities are implemented

**Information Sources**:
- Repository configuration files (`config.ini`)
- Implementation files (`*.py`)
- Repository documentation
- API documentation
- Testing results

---

*This analysis shows that pygetpapers provides access to a diverse range of repositories with different strengths and limitations, allowing users to choose the most appropriate source based on their specific research needs.* 