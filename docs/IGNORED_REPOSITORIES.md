# Ignored Repositories

**Date:** July 28, 2025 (system date of generation)  
**Purpose:** Document repositories that should be ignored in pygetpapers  
**Scope:** Repositories that are deprecated, problematic, or no longer supported

## Overview

This document lists repositories that should be ignored in pygetpapers. These repositories may be deprecated, have technical issues, or are no longer actively maintained.

## Ignored Repositories

### 1. arXiv Repository

**Repository:** arxiv  
**Reason for Ignoring:** Deprecated in favor of more comprehensive alternatives  
**Status:** No longer actively maintained  
**Alternative:** Use BioRxiv for preprints or Europe PMC for published content

**Technical Issues:**
- Limited metadata compared to other repositories
- No structured XML support
- Basic API functionality
- Limited content formats

**Impact:** Removing arXiv reduces complexity and focuses on more feature-rich repositories.

### 2. CrossRef Repository

**Repository:** crossref  
**Reason for Ignoring:** Metadata-only repository with no full-text access  
**Status:** Limited utility for content analysis  
**Alternative:** Use OpenAlex for comprehensive metadata and citation data

**Technical Issues:**
- No full-text content access
- Metadata-only functionality
- Limited research value for content analysis
- Redundant with other metadata sources

**Impact:** Removing CrossRef simplifies the repository landscape and focuses on content-rich sources.

## Implementation Notes

### Repository Removal Process
1. **Documentation Updates:** Update all documentation to exclude ignored repositories
2. **Code Cleanup:** Remove repository-specific code and configurations
3. **Testing Updates:** Update tests to exclude ignored repositories
4. **User Communication:** Inform users about repository deprecation

### Migration Guidance
- **From arXiv:** Use BioRxiv for biology preprints, Europe PMC for published content
- **From CrossRef:** Use OpenAlex for comprehensive metadata and citation analysis

### Future Considerations
- Monitor for new repositories that may replace ignored ones
- Consider re-evaluating ignored repositories if they improve significantly
- Maintain documentation for historical reference

## Related Documentation
- [Repository Summary](repositories_summary.md)
- [Repository Fields Schema](repository_fields_schema.md)
- [File Size Alerts](file-size-alerts.md) 