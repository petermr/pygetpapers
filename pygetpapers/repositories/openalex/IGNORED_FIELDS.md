# OpenAlex Repository - Ignored Fields

**Date:** July 27, 2025  
**Purpose:** Document fields that should be ignored in OpenAlex repository processing  
**Repository:** openalex

## Overview
This document lists fields that are extracted during API calls or processing but should be ignored for normal processing and analysis. These fields are typically internal system identifiers, debugging information, or technical metadata that don't provide meaningful content for research purposes.

## Ignored Fields

### `cursor_mark`
- **Source**: API response pagination metadata
- **Type**: Internal pagination identifier
- **Reason for Ignoring**: Technical pagination field with no research value
- **Usage**: Used internally for API pagination but not needed in final output

### `total_results`
- **Source**: API response metadata
- **Type**: Search result count
- **Reason for Ignoring**: Technical metadata not relevant for individual paper analysis
- **Usage**: Useful for pagination but not needed in paper metadata

### `api_version` (if present)
- **Source**: API response metadata
- **Type**: Technical API version information
- **Reason for Ignoring**: Technical metadata not relevant for content analysis

### `request_id` (if present)
- **Source**: API response headers or metadata
- **Type**: Internal request tracking identifier
- **Reason for Ignoring**: Debugging/tracking field with no research value

## Implementation Notes

### Current Status
- `cursor_mark` and `total_results` are currently included in schema documentation
- No specific filtering mechanism exists for these fields
- Fields may vary depending on API version and response format

### Recommended Actions
1. **Filtering**: Add logic to exclude technical fields from final output
2. **Documentation**: Update schema documentation to mark these as ignored
3. **Configuration**: Add configuration option to control field filtering

### Code Locations
- Primary API response processing in `openalex.py`
- Pagination handling logic

## Future Considerations
- Monitor for additional technical fields that should be ignored
- Consider creating a standardized ignored fields configuration system
- Evaluate whether these fields should be completely removed from extraction or just filtered from output 