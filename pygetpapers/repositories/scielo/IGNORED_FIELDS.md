# SciELO Repository - Ignored Fields

**Date:** July 27, 2025  
**Purpose:** Document fields that should be ignored in SciELO repository processing  
**Repository:** scielo

## Overview
This document lists fields that are extracted during web scraping or processing but should be ignored for normal processing and analysis. These fields are typically internal system identifiers, debugging information, or technical metadata that don't provide meaningful content for research purposes.

## Ignored Fields

### `extracted_at`
- **Source**: Timestamp added during extraction process
- **Type**: Processing metadata
- **Reason for Ignoring**: Technical processing timestamp with no research value
- **Usage**: Useful for debugging extraction issues but not needed in final output

### `scraping_timestamp` (if present)
- **Source**: Web scraping process
- **Type**: Technical timestamp
- **Reason for Ignoring**: Technical metadata not relevant for content analysis

### `request_id` (if present)
- **Source**: HTTP request headers or metadata
- **Type**: Internal request tracking identifier
- **Reason for Ignoring**: Debugging/tracking field with no research value

### `session_id` (if present)
- **Source**: Web scraping session
- **Type**: Internal session identifier
- **Reason for Ignoring**: Technical session tracking with no research value

## Implementation Notes

### Current Status
- `extracted_at` is currently included in secondary fields schema
- No specific filtering mechanism exists for these fields
- Fields may vary depending on scraping method and response format

### Recommended Actions
1. **Filtering**: Add logic to exclude technical fields from final output
2. **Documentation**: Update schema documentation to mark these as ignored
3. **Configuration**: Add configuration option to control field filtering

### Code Locations
- Primary web scraping processing in `scielo.py`
- Web scraping session handling logic

## Future Considerations
- Monitor for additional technical fields that should be ignored
- Consider creating a standardized ignored fields configuration system
- Evaluate whether these fields should be completely removed from extraction or just filtered from output 