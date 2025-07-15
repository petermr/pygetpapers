# Rxivist Repository Retirement Summary

## Overview

This document summarizes the retirement of the Rxivist repository from pygetpapers v2.0. The Rxivist API was deprecated and removed from the codebase to simplify the repository architecture and focus on more actively maintained and reliable data sources.

## Retirement Date

**Date**: December 2024  
**Version**: pygetpapers v2.0  
**Reason**: API deprecation and maintenance simplification

## What Was Removed

### 1. Core Implementation Files
- **`pygetpapers/repositories/biorxiv/rxivist.py`** - Complete Rxivist implementation
  - Rxivist class implementation
  - API integration with rxivist.org
  - Metadata-only search functionality
  - Pagination and cursor handling

### 2. Configuration
- **`pygetpapers/core/config.ini`** - Removed entire [rxivist] section
  - API endpoint configuration
  - Feature support flags
  - Class and library name mappings

### 3. Main Application Code
- **`pygetpapers/pygetpapers.py`** - Updated to remove rxivist support
  - Removed RXIVIST constant
  - Updated module path handling logic
  - Updated help text and API list
  - Removed rxivist from special case handling

### 4. Streamlit UI
- **`pygetpapers/streamlit_app.py`** - Removed rxivist from UI
  - Removed from repository selection dropdown
  - Removed from feature matrix
  - Removed from help documentation table

### 5. Documentation Updates
- **`docs/README.md`** - Removed rxivist section and references
- **`docs/project-overview.md`** - Updated repository support matrix
- **`docs/implementation-summary.md`** - Updated feature comparison
- **`docs/user-guide.md`** - Removed rxivist from repository list
- **`docs/streamlit-ui-implementation.md`** - Updated UI documentation
- **`docs/chat-log-streamlit-ui-development.md`** - Updated development logs
- **`docs/LOG.md`** - Updated changelog references
- **`docs/biorxiv-web-scraping-analysis.md`** - Updated alternative approaches
- **`pygetpapers/repositories/biorxiv/rxiv.py`** - Updated class documentation

## Impact Assessment

### ✅ No Breaking Changes
- All other repositories continue to work normally
- No changes to core pygetpapers functionality
- CLI interface remains stable
- Streamlit UI continues to function

### ✅ Improved Architecture
- Simplified repository management
- Reduced maintenance burden
- Cleaner codebase structure
- More focused feature set

### ✅ Better User Experience
- Clearer repository options
- Reduced confusion about deprecated APIs
- More reliable data sources
- Better documentation

## Alternative Solutions

### For bioRxiv/medRxiv Text Search
Users who previously relied on Rxivist for text-based searches of bioRxiv/medRxiv content now have better alternatives:

1. **bioRxiv Web Scraper** (Recommended)
   - Full text search capabilities
   - HTML content download
   - Metadata extraction
   - Integrated into pygetpapers workflow

2. **Direct bioRxiv/medRxiv APIs**
   - Date-based searches
   - Metadata retrieval
   - DOI-based access

3. **Europe PMC**
   - Comprehensive biomedical literature
   - Full text search
   - Multiple output formats

## Testing Results

### ✅ Retirement Verification
```bash
# Rxivist API now returns "API not supported yet" error
python -m pygetpapers.pygetpapers --api rxivist -q "test" -k 5
# Result: PygetpapersError: API not supported yet

# Other repositories continue to work
python -m pygetpapers.pygetpapers --api biorxiv -q "2024-01-01/2024-01-31" -k 5 -n
# Result: Total number of hits for the query are 4569

python -m pygetpapers.pygetpapers --api europe_pmc -q "artificial intelligence" -k 5 -n
# Result: Total number of hits for the query are 296722
```

### ✅ Help Text Updated
```bash
python -m pygetpapers.pygetpapers --help
# Shows: API to search [europe_pmc, crossref,arxiv,biorxiv,medrxiv,openalex]
# (rxivist removed from list)
```

## Migration Guide

### For Existing Users

1. **Replace Rxivist with bioRxiv Web Scraper**
   ```bash
   # Old: pygetpapers --api rxivist -q "biomedicine" -k 10
   # New: Use bioRxiv with text queries (web scraper)
   pygetpapers --api biorxiv -q "biomedicine" -k 10
   ```

2. **For Comprehensive Biomedical Search**
   ```bash
   # Use Europe PMC for broad biomedical literature
   pygetpapers --api europe_pmc -q "biomedicine" -k 10
   ```

3. **For Specific Preprint Searches**
   ```bash
   # Use bioRxiv or medRxiv directly
   pygetpapers --api biorxiv -q "2024-01-01/2024-12-31" -k 10
   pygetpapers --api medrxiv -q "2024-01-01/2024-12-31" -k 10
   ```

## Future Considerations

### Potential Enhancements
1. **Enhanced bioRxiv Web Scraper**
   - Improved text search capabilities
   - Better metadata extraction
   - Faster processing

2. **Additional Repository Support**
   - PubMed Central
   - arXiv (if policy changes)
   - Other preprint servers

3. **Advanced Search Features**
   - Semantic search
   - Citation network analysis
   - Content similarity matching

## Conclusion

The retirement of Rxivist from pygetpapers v2.0 represents a positive step toward a more maintainable and reliable codebase. Users now have access to better alternatives that provide more comprehensive functionality and improved reliability.

The migration path is clear, and the impact on existing workflows is minimal while providing significant benefits in terms of code maintainability and user experience.

---

**Note**: This retirement aligns with pygetpapers' commitment to providing high-quality, reliable access to academic literature through actively maintained and well-documented APIs. 