# UPSpace Repository Implementation Summary

**Date:** July 22, 2024  
**Project:** pygetpapers UPSpace Integration  
**Status:** Complete Implementation with Testing

---

## 1. Project Overview

### Background
- **Repository:** UPSpace (University of Pretoria's DSpace repository)
- **API Type:** DSpace REST API (public, no authentication required)
- **Base URL:** https://repository.up.ac.za/server/api
- **Integration Goal:** Full search, metadata extraction, and file download capabilities

### Key Achievements
- ✅ Complete API integration with DSpace REST endpoints
- ✅ Metadata extraction with SDG classification support
- ✅ PDF file download functionality
- ✅ DataTables HTML generation with interactive interface
- ✅ Comprehensive test suite
- ✅ Error handling and rate limiting

---

## 2. API Discovery and Structure Analysis

### Initial Challenges
- **Date Format Issues:** Incorrect date handling in metadata extraction
- **API Response Structure:** Complex nested JSON structure requiring careful parsing
- **Bundle/Bitstream Navigation:** Multi-level API calls for file access

### API Structure Discovered
```json
{
  "_embedded": {
    "searchResult": {
      "_embedded": {
        "objects": [...]  // Search results
      }
    }
  }
}
```

### Key Endpoints Identified
- **Search:** `/discover/search/objects`
- **Item Details:** `/core/items/{uuid}`
- **Bundles:** `/core/items/{uuid}/bundles`
- **Bitstreams:** `/core/bundles/{uuid}/bitstreams`
- **File Download:** `/core/bitstreams/{uuid}/content`

---

## 3. Core Implementation Components

### 3.1 Main UPSpace Class (`upspace.py`)
```python
class UPSpace(AbstractRepository):
    def __init__(self):
        self.base_url = "https://repository.up.ac.za/server/api"
        self.search_url = "https://repository.up.ac.za/server/api/discover/search/objects"
```

### 3.2 Key Methods Implemented
- **`search_articles()`** - Search with pagination and result processing
- **`_extract_metadata()`** - Parse Dublin Core metadata fields
- **`download_article()`** - Download PDF and metadata files
- **`_create_upspace_datatables_html()`** - Generate interactive HTML tables

### 3.3 Metadata Fields Extracted
- `dc.title` - Article title
- `dc.contributor.author` - Authors (multiple)
- `dc.description.abstract` - Abstract
- `dc.date.issued` - Publication year
- `dc.publisher` - Publisher information
- `dc.description.sdg` - SDG classifications
- `dc.subject` - Keywords
- `dc.identifier.uri` - Handle URLs
- `dc.identifier.other` - DOI and other identifiers

---

## 4. SDG Classification System

### Implementation Details
- **SDG Field:** `dc.description.sdg`
- **Validation:** Ensures SDG numbers are 1-17
- **Display:** Color-coded badges in DataTables
- **CSS Classes:** `sdg-badge sdg-{number}`

### SDG Badge Styling
```css
.sdg-badge {
    display: inline-block;
    padding: 2px 6px;
    margin: 1px;
    border-radius: 3px;
    font-size: 11px;
    font-weight: bold;
    color: white;
}
```

### Example Output
- SDG-11: Sustainable Cities and Communities
- SDG-04: Quality Education
- Multiple SDGs per article supported

---

## 5. File Download System

### Download Process
1. **Article Directory Creation:** `{output_dir}/{article_id}/`
2. **Metadata Save:** `metadata.json` with full article data
3. **PDF Download:** `fulltext.pdf` (if available)
4. **Error Handling:** Graceful fallback if files unavailable

### File Structure
```
output_dir/
├── UPSPACE_2263_103497/
│   ├── metadata.json
│   └── fulltext.pdf
├── UPSPACE_2263_103496/
│   ├── metadata.json
│   └── fulltext.pdf
└── ...
```

### Bundle/Bitstream Navigation
- **ORIGINAL Bundle:** Contains primary PDF files
- **Bitstream Processing:** Filters for PDF files only
- **Download URLs:** Direct content access via UUID

---

## 6. DataTables Interface

### Features Implemented
- **Interactive Table:** Sortable columns, search, pagination
- **Responsive Design:** Mobile-friendly layout
- **SDG Badges:** Visual SDG classification display
- **File Links:** Local PDF and JSON file access
- **External Links:** Handle URLs and DOI links

### HTML Structure
```html
<table id="upspace-table" class="display">
    <thead>
        <tr>
            <th>ID</th>
            <th>Title</th>
            <th>Authors</th>
            <th>Year</th>
            <th>Abstract</th>
            <th>SDGs</th>
            <th>Keywords</th>
            <th>Identifiers</th>
            <th>Files</th>
        </tr>
    </thead>
    <tbody>
        <!-- Dynamic content -->
    </tbody>
</table>
```

### Styling Features
- **Professional Appearance:** Clean, academic design
- **Column Widths:** Optimized for content types
- **Color Scheme:** SDG color palette integration
- **Typography:** Readable fonts and spacing

---

## 7. Testing Framework

### Test Categories
1. **Unit Tests:** Individual method testing
2. **Integration Tests:** End-to-end workflow testing
3. **API Tests:** Real API call validation
4. **DataTables Tests:** HTML generation verification

### Test Files Created
- `test_upspace_search.py` - Search functionality tests
- `test_upspace_download.py` - File download tests
- `test_upspace_metadata.py` - Metadata extraction tests
- `test_upspace_datatables.py` - DataTables generation tests

### Test Implementation Script
- `test_implementation.py` - Comprehensive integration testing
- Real API calls with actual UPSpace data
- Validation of all major functionality

---

## 8. Error Handling and Robustness

### Rate Limiting
```python
time.sleep(0.5)  # 500ms delay between requests
```

### Error Recovery
- **Network Failures:** Retry logic with exponential backoff
- **JSON Parsing:** Graceful handling of malformed responses
- **File Operations:** Directory creation error handling
- **Missing Data:** Fallback values for optional fields

### Validation
- **SDG Numbers:** Range validation (1-17)
- **URL Formatting:** Proper URL construction
- **File Extensions:** PDF file detection
- **Metadata Completeness:** Required field checking

---

## 9. Security and Best Practices

### HTML Escaping
```python
import html
title = html.escape(article.get('title', 'No title'))
```

### Input Validation
- **Query Parameters:** Sanitized before API calls
- **File Paths:** Safe directory traversal
- **Metadata Fields:** XSS prevention

### API Usage
- **Public API:** No authentication required
- **Rate Limiting:** Respectful server usage
- **Error Logging:** Comprehensive error tracking

---

## 10. Results and Validation

### Successful Implementation
- ✅ **Search Functionality:** 5+ articles retrieved per query
- ✅ **Metadata Extraction:** All Dublin Core fields parsed
- ✅ **SDG Classification:** Proper badge display
- ✅ **File Downloads:** PDF and metadata files saved
- ✅ **DataTables Generation:** Interactive HTML interface
- ✅ **Error Handling:** Robust error recovery

### Sample Output
```
Found 5 articles for query: 'sustainable development'
✓ Article download completed
✓ DataTables HTML file created (18,573 bytes)
✓ Index HTML file created (6,591 bytes)
```

### Files Generated
- **DataTables HTML:** Interactive table with search/sort
- **Index HTML:** Overview page with navigation
- **Article Directories:** Organized file structure
- **Metadata JSON:** Complete article information

---

## Technical Specifications

### Dependencies
- `requests` - HTTP API calls
- `pathlib` - File path handling
- `json` - JSON parsing
- `html` - HTML escaping
- `time` - Rate limiting

### API Endpoints Used
- Search: `GET /discover/search/objects`
- Items: `GET /core/items/{uuid}`
- Bundles: `GET /core/items/{uuid}/bundles`
- Bitstreams: `GET /core/bundles/{uuid}/bitstreams`
- Content: `GET /core/bitstreams/{uuid}/content`

### File Formats Supported
- **Input:** JSON API responses
- **Output:** HTML, JSON, PDF
- **Metadata:** Dublin Core format

---

## Future Enhancements

### Potential Improvements
1. **Advanced Search:** Filter by date, author, SDG
2. **Bulk Downloads:** Multiple article processing
3. **Citation Export:** BibTeX, RIS formats
4. **Analytics Dashboard:** Usage statistics
5. **Caching:** Local result caching

### Integration Opportunities
- **Streamlit UI:** Web interface integration
- **CLI Tools:** Command-line interface
- **API Wrapper:** Simplified API access
- **Plugin System:** Extensible architecture

---

## Conclusion

The UPSpace repository integration represents a complete implementation of academic repository access, featuring:

- **Robust API Integration:** Full DSpace REST API support
- **Rich Metadata Extraction:** Comprehensive Dublin Core parsing
- **SDG Classification:** Visual sustainability goal display
- **Interactive Interface:** Professional DataTables implementation
- **Comprehensive Testing:** Thorough validation framework
- **Production Ready:** Error handling and security measures

This implementation provides a solid foundation for accessing and analyzing academic content from the University of Pretoria's institutional repository, with particular emphasis on sustainable development research and SDG classification. 