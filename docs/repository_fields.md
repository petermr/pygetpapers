# Repository Fields Discussion and Implementation

**Date:** July 28, 2025 (system date of generation)  
**Purpose:** Document the discussion and implementation of repository field management in pygetpapers  
**Scope:** Field analysis, ignored fields documentation, file size alerts, and repository deprecation

## Overview

This document captures the comprehensive discussion and implementation work done to improve repository field management in pygetpapers. The work included analyzing field meanings, creating ignored fields documentation, implementing file size alerts, and managing repository deprecation.

---

## 1. BioRxiv Field Analysis

### Initial Question: pisa_id and apath Fields

**User Query:** "in biorxiv what do pisa_id and apath mean?"

### Investigation Process

The investigation involved examining the BioRxiv web scraper code to understand the origin and purpose of these fields.

#### Code Analysis
```python
# From pygetpapers/repositories/biorxiv/biorxiv_web_scraper.py
# In the _extract_paper_data method:

if citation_elem.get("data-pisa"):
    paper_data["pisa_id"] = citation_elem.get("data-pisa")
if citation_elem.get("data-apath"):
    paper_data["apath"] = citation_elem.get("data-apath")
```

#### Findings

**pisa_id:**
- **Source:** HTML `data-pisa` attribute on citation elements
- **Type:** Internal BioRxiv system identifier
- **Purpose:** Internal system routing and identification
- **Research Value:** None - purely technical implementation detail

**apath:**
- **Source:** HTML `data-apath` attribute on citation elements  
- **Type:** Internal routing/path identifier
- **Purpose:** Internal BioRxiv system routing
- **Research Value:** None - purely technical implementation detail

### Conclusion

Both `pisa_id` and `apath` are internal BioRxiv system identifiers extracted from HTML data attributes. They serve no research purpose and should be ignored during normal processing.

---

## 2. Ignored Fields Documentation

### User Request
"Please ignore pisa_id and apath in future. Please add a file for each repository of IGNORED_FIELDS"

### Implementation

Created individual `IGNORED_FIELDS.md` files for each repository to document fields that should be ignored during processing.

#### Files Created

1. **`pygetpapers/repositories/biorxiv/IGNORED_FIELDS.md`**
   - `pisa_id`: Internal system identifier from `data-pisa` HTML attribute
   - `apath`: Internal routing identifier from `data-apath` HTML attribute

2. **`pygetpapers/repositories/europe_pmc/IGNORED_FIELDS.md`**
   - `cursor_mark`: Internal pagination identifier
   - `request_id`: Internal request tracking identifier
   - `api_version`: Technical API version information

3. **`pygetpapers/repositories/openalex/IGNORED_FIELDS.md`**
   - `cursor_mark`: Internal pagination identifier
   - `total_results`: Search result count
   - `api_version`: Technical API version information
   - `request_id`: Internal request tracking identifier

4. **`pygetpapers/repositories/redalyc/IGNORED_FIELDS.md`**
   - `extracted_at`: Processing timestamp
   - `selenium_session_id`: Selenium session identifier
   - `scraping_timestamp`: Technical scraping timestamp
   - `request_id`: Internal request tracking identifier

5. **`pygetpapers/repositories/scielo/IGNORED_FIELDS.md`**
   - `extracted_at`: Processing timestamp
   - `scraping_timestamp`: Technical scraping timestamp
   - `request_id`: Internal request tracking identifier
   - `session_id`: Session identifier

6. **`pygetpapers/repositories/upspace/IGNORED_FIELDS.md`**
   - `uuid`: DSpace UUID identifier
   - `id`: DSpace numeric identifier
   - `api_version`: Technical API version information
   - `request_id`: Internal request tracking identifier
   - `extracted_at`: Processing timestamp

### Benefits
- **Clear Documentation:** Each repository has explicit documentation of ignored fields
- **Consistent Processing:** Developers know which fields to filter out
- **Research Focus:** Ensures only research-relevant fields are processed
- **Maintainability:** Centralized documentation of technical vs. research fields

---

## 3. File Size Alert Implementation

### User Request
"STYLE: Please alert users to any file downloads where the size is greater than 100 MBytes"

### Implementation Components

#### 1. Configuration Management
**File:** `pygetpapers/core/file_size_config.py`

```python
DEFAULT_CONFIG = {
    "file_size_alert_threshold_mb": 100,
    "file_size_warning_threshold_mb": 50,
    "enable_file_size_alerts": True,
    "show_ui_warnings": True,
    "log_large_files": True,
    "alert_message_template": "🚨 LARGE FILE ALERT: {file_name} is {size_mb:.1f} MB (exceeds {threshold_mb} MB threshold)",
    "warning_message_template": "⚠️  This large file may take significant time to download and consume substantial disk space."
}
```

**Features:**
- Configurable thresholds via environment variables
- Multiple alert channels (console, UI, logging)
- Customizable message templates
- Granular control over alert behavior

#### 2. Utility Functions
**File:** `pygetpapers/core/file_utils.py`

Added static methods:
- `check_file_size_alert()`: Performs size check and logging
- `format_file_size()`: Formats file sizes for display

#### 3. Download Integration
**File:** `pygetpapers/core/download_tools.py`

Integrated file size checks in:
- `queries_the_url_and_writes_response_to_destination()`: General file downloads
- `getsupplementaryfiles()`: Supplementary/zip file downloads

#### 4. Streamlit UI Integration
**File:** `pygetpapers/streamlit_app.py`

Added alerts in:
- **File Browser:** Shows 🚨 icon and warning for large files
- **File Details:** Displays warning message for selected large files
- **Progress Display:** Shows summary of large files detected during download

### Alert Channels

1. **Console Logging:** Warning messages in terminal output
2. **Streamlit UI:** Visual alerts with icons and warning messages
3. **Progress Tracking:** Real-time detection and counting of large files
4. **File Browser:** Visual indicators in file listings

### Configuration Options

- **Environment Variables:** Override default settings
- **Programmatic Configuration:** Modify settings in code
- **Threshold Customization:** Adjust alert and warning thresholds
- **Channel Control:** Enable/disable specific alert channels

---

## 4. Repository Deprecation

### User Request
"STYLE: Please create IGNORED_REPOSITORIES and put arXiv and CrossRef in there. After that we ignore all repos in this list"

### Implementation

#### 1. Created IGNORED_REPOSITORIES.md
**File:** `docs/IGNORED_REPOSITORIES.md`

**arXiv Repository:**
- **Reason:** Deprecated in favor of more comprehensive alternatives
- **Alternative:** BioRxiv for preprints, Europe PMC for published content
- **Technical Issues:** Limited metadata, no structured XML, basic API

**CrossRef Repository:**
- **Reason:** Metadata-only repository with no full-text access
- **Alternative:** OpenAlex for comprehensive metadata and citation data
- **Technical Issues:** No full-text content, limited research value

#### 2. Documentation Updates

**Updated Files:**
- `docs/repositories_summary.md`: Removed arXiv and CrossRef, updated scope to 6 repositories
- `docs/repository_fields_schema.md`: Removed references to ignored repositories
- Deleted: `docs/metadata_fields/arxiv_metadata_fields.md`
- Deleted: `docs/metadata_fields/crossref_metadata_fields.md`

**Changes Made:**
- Updated repository count from 8 to 6
- Removed arXiv and CrossRef from comparison matrix
- Updated selection guides and recommendations
- Added references to IGNORED_REPOSITORIES.md

### Current Active Repositories

1. **BioRxiv** - Biology preprints with dual access
2. **Europe PMC** - Biomedical literature with JATS XML
3. **OpenAlex** - Open access with citation data
4. **Redalyc** - Spanish/Portuguese literature
5. **SciELO** - Multi-language scientific literature
6. **UPSpace** - Institutional repository with SDG classifications

---

## 5. Comprehensive Documentation

### Repository Summary
**File:** `docs/repositories_summary.md`

Created comprehensive overview including:
- Repository comparison matrix
- Detailed descriptions of each repository
- Strengths, limitations, and use cases
- Selection guide for different research needs
- Implementation recommendations

### Individual Repository Documentation
**Directory:** `docs/metadata_fields/`

Created detailed metadata field documentation for each active repository:
- `biorxiv_metadata_fields.md`
- `europe_pmc_metadata_fields.md`
- `openalex_metadata_fields.md`
- `redalyc_metadata_fields.md`
- `scielo_metadata_fields.md`
- `upspace_metadata_fields.md`

Each file includes:
- Field descriptions with types and examples
- Data quality notes
- Usage examples with code snippets
- Implementation notes
- Related documentation links

### File Size Alerts Documentation
**File:** `docs/file-size-alerts.md`

Comprehensive guide covering:
- Feature overview and benefits
- Configuration options
- Usage examples
- Implementation details
- Best practices and troubleshooting

---

## 6. Technical Implementation Details

### File Size Alert Flow

1. **Download Trigger:** File download initiated in `download_tools.py`
2. **Size Check:** `FileUtils.check_file_size_alert()` called with file size
3. **Configuration:** `file_size_config.py` provides threshold and settings
4. **Alert Generation:** Warning messages generated and logged
5. **UI Update:** Streamlit app displays alerts in relevant sections
6. **Progress Tracking:** Large file count tracked in progress data

### Ignored Fields Management

1. **Documentation:** Each repository has `IGNORED_FIELDS.md`
2. **Field Identification:** Technical vs. research fields clearly documented
3. **Processing:** Fields can be filtered during data processing
4. **Maintenance:** Centralized documentation for easy updates

### Repository Deprecation Process

1. **Documentation:** Create `IGNORED_REPOSITORIES.md`
2. **Code Cleanup:** Remove repository-specific code
3. **Documentation Updates:** Update all references
4. **User Communication:** Provide migration guidance

---

## 7. Benefits and Impact

### Improved User Experience
- **Clear Alerts:** Users are warned about large file downloads
- **Better Guidance:** Clear documentation on which repositories to use
- **Reduced Confusion:** Eliminated deprecated repositories from documentation

### Enhanced Maintainability
- **Centralized Configuration:** File size alerts are easily configurable
- **Documented Fields:** Clear understanding of which fields to ignore
- **Structured Documentation:** Comprehensive and organized repository information

### Research Focus
- **Quality Content:** Focus on repositories with full-text access
- **Relevant Fields:** Filter out technical implementation details
- **Better Alternatives:** Guide users to more comprehensive repositories

---

## 8. Future Considerations

### Potential Enhancements
- **Field Validation:** Implement automatic filtering of ignored fields
- **Repository Monitoring:** Track usage and performance of active repositories
- **Configuration UI:** Add Streamlit interface for file size alert configuration
- **Advanced Alerts:** Implement predictive alerts based on file type and size

### Maintenance Tasks
- **Regular Reviews:** Periodically review ignored fields and repositories
- **Documentation Updates:** Keep documentation current with repository changes
- **User Feedback:** Collect feedback on alert effectiveness and configuration
- **Performance Monitoring:** Track impact of file size alerts on user experience

---

## Related Documentation

- [Repository Summary](repositories_summary.md)
- [Repository Fields Schema](repository_fields_schema.md)
- [Ignored Repositories](IGNORED_REPOSITORIES.md)
- [File Size Alerts](file-size-alerts.md)
- [Individual Repository Documentation](metadata_fields/)

---

*This document captures the comprehensive discussion and implementation work done to improve repository field management in pygetpapers. The work demonstrates a systematic approach to understanding, documenting, and improving the system's functionality.* 