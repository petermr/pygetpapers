# Europe PMC Repository - Ignored Fields

**Date:** July 27, 2025  
**Purpose:** Document fields that should be ignored in Europe PMC repository processing  
**Repository:** europe_pmc

## Overview
This document lists fields that are extracted during API calls or processing but should be ignored for normal processing and analysis. These fields are typically internal system identifiers, debugging information, or technical metadata that don't provide meaningful content for research purposes.

## Ignored Fields

### `cursor_mark`
- **Source**: API response pagination metadata
- **Type**: Internal pagination identifier
- **Reason for Ignoring**: Technical pagination field with no research value
- **Usage**: Used internally for API pagination but not needed in final output

### `request_id` (if present)
- **Source**: API response headers or metadata
- **Type**: Internal request tracking identifier
- **Reason for Ignoring**: Debugging/tracking field with no research value

### `api_version` (if present)
- **Source**: API response metadata
- **Type**: Technical API version information
- **Reason for Ignoring**: Technical metadata not relevant for content analysis

## Implementation Notes

### Current Status
- `cursor_mark` is currently included in primary fields schema
- No specific filtering mechanism exists for these fields
- Fields may vary depending on API version and response format

### Recommended Actions
1. **Filtering**: Add logic to exclude technical fields from final output
2. **Documentation**: Update schema documentation to mark these as ignored
3. **Configuration**: Add configuration option to control field filtering

### Code Locations
- Primary API response processing in `europe_pmc.py`
- Pagination handling logic

## Future Considerations
- Monitor for additional technical fields that should be ignored
- Consider creating a standardized ignored fields configuration system
- Evaluate whether these fields should be completely removed from extraction or just filtered from output 