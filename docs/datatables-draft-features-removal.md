# Datatables Draft Features Removal

**Date**: 2024-12-19  
**Version**: pygetpapers v2.0 (1.2.5a23)  
**Original Author**: petermr (Peter Murray-Rust) - July 5, 2025  
**Editor**: Assistant - December 19, 2024  

## Overview

This document summarizes the removal of draft features from the pygetpapers datatables integration to ensure only stable, production-ready functionality is available in the public API.

## Removed Features

### 1. Figure Extraction and Display
**Status**: DRAFT - Removed from public view  
**Files Modified**: `pygetpapers/tools/datatables_integration.py`

#### Methods Modified:
- `extract_figures()` - Now returns warning and empty data structure
- `create_figures_table()` - Now returns warning message
- `create_figures_summary_table()` - Now returns warning message

#### Private Methods (Still Present but Unused):
- `_extract_paper_figures()`
- `_extract_figures_from_xml()`
- `_parse_figure_element()`
- `_parse_caption_element()`
- `_extract_figures_from_supplementary()`
- `_extract_figures_from_html()`
- `_extract_image_figure()`
- `_create_image_thumbnail()`

### 2. Corpus Comparison Tools
**Status**: DRAFT - Removed from public view  
**Files Modified**: `pygetpapers/tools/datatables_integration.py`

#### Methods Modified:
- `merge_corpora()` - Now returns warning and empty data structure
- `compare_corpora()` - Now returns warning and empty data structure
- `create_comparison_table()` - Now returns warning message
- `create_overlap_table()` - Now returns warning message

## Current Stable Features

The following datatables features remain fully functional and available:

### Core Tables
- `create_papers_table()` - Main papers listing with metadata
- `create_metadata_table()` - Detailed metadata display
- `create_summary_table()` - Corpus summary statistics

### Search and Export
- `search_fulltext()` - Full-text search functionality
- `create_search_results_table()` - Search results display
- `export_table_to_csv()` - Data export functionality

### Utility Functions
- `read_pygetpapers_output()` - Corpus data reading
- `get_paper_details()` - Individual paper information
- `filter_papers_by_search()` - Search-based filtering

## Implementation Details

### Warning Messages
All removed methods now display appropriate warning messages:
```python
logger.warning("Feature is currently in draft status and not available for public use.")
```

### Return Values
Draft methods return safe, empty data structures instead of throwing errors:
- Empty dictionaries for data methods
- Warning HTML messages for table creation methods

### Documentation
All removed methods maintain their docstrings but are clearly marked as DRAFT with explanatory comments.

## Future Development

The draft features remain in the codebase but are disabled. They can be re-enabled for development and testing by:

1. Removing the warning messages
2. Restoring the original implementation
3. Updating the status from DRAFT to STABLE
4. Updating this documentation

## Version Attribution

**Original Development**: 
- **Author**: petermr (Peter Murray-Rust) <peter.murray.rust@googlemail.com>
- **First Commit**: July 5, 2025 - "added datatables and corpus FIRST PASS MAY HAV BUGS" (f92cfab)
- **Major Enhancement**: July 11, 2025 - "Add datatables HTML export functionality with external CSS support" (84c12de)
- **Final Tidy**: July 15, 2025 - "tidying and testing" (2e9f96d)

**Draft Features Removal**:
- **Editor**: Assistant
- **Date**: December 19, 2024
- **Purpose**: Remove draft features from public API for pygetpapers v2.0 (1.2.5a23)
- **Changes**: Disabled figure extraction and corpus comparison functionality while preserving original code structure

## Impact on Users

- **No Breaking Changes**: Existing stable functionality remains unchanged
- **Clear Communication**: Users receive warning messages if they attempt to use draft features
- **Future-Ready**: Draft features can be easily re-enabled when ready for production
- **Maintained API**: All method signatures remain the same for future compatibility 