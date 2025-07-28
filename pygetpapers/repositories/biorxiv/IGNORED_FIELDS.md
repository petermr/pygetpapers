# BioRxiv Repository - Ignored Fields

**Date:** July 27, 2025  
**Purpose:** Document fields that should be ignored in BioRxiv repository processing  
**Repository:** bioRxiv

## Overview
This document lists fields that are extracted during web scraping but should be ignored for normal processing and analysis. These fields are typically internal system identifiers or debugging information that don't provide meaningful content for research purposes.

## Ignored Fields

### `pisa_id`
- **Source**: `data-pisa` HTML attribute on citation elements
- **Type**: Internal system identifier
- **Reason for Ignoring**: Internal BioRxiv system identifier with no research value
- **Extraction Location**: `_extract_paper_data()` method in scraper files

### `apath`
- **Source**: `data-apath` HTML attribute on citation elements  
- **Type**: Internal routing/path identifier
- **Reason for Ignoring**: Internal BioRxiv routing identifier with no research value
- **Extraction Location**: `_extract_paper_data()` method in scraper files

## Implementation Notes

### Current Status
- These fields are currently extracted and stored in metadata
- They appear in the repository schema documentation
- No filtering mechanism currently exists to exclude them

### Recommended Actions
1. **Filtering**: Add logic to exclude these fields from final output
2. **Documentation**: Update schema documentation to mark these as ignored
3. **Configuration**: Add configuration option to control field filtering

### Code Locations
- `pygetpapers/repositories/biorxiv/biorxiv_web_scraper.py` (lines 234-238)
- `pygetpapers/repositories/biorxiv/biorxiv_advanced_scraper.py` (lines 455-459)

## Future Considerations
- Monitor for additional internal fields that should be ignored
- Consider creating a standardized ignored fields configuration system
- Evaluate whether these fields should be completely removed from extraction or just filtered from output 