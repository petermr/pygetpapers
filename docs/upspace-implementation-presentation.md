# UPSpace Repository Implementation
## Presentation Slides

---

## Slide 1: Project Overview
### UPSpace Integration for pygetpapers

**Date:** July 22, 2024  
**Repository:** University of Pretoria's DSpace  
**API:** Public REST API (no authentication required)

**Key Achievements:**
- ✅ Complete DSpace REST API integration
- ✅ SDG classification system
- ✅ Interactive DataTables interface
- ✅ Comprehensive testing framework
- ✅ Production-ready error handling

---

## Slide 2: Technical Architecture
### API Structure and Endpoints

**Base URL:** `https://repository.up.ac.za/server/api`

**Key Endpoints:**
- **Search:** `/discover/search/objects`
- **Items:** `/core/items/{uuid}`
- **Bundles:** `/core/items/{uuid}/bundles`
- **Bitstreams:** `/core/bundles/{uuid}/bitstreams`
- **Download:** `/core/bitstreams/{uuid}/content`

**Response Structure:**
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

---

## Slide 3: Core Implementation
### Main Components

**UPSpace Class Features:**
- `search_articles()` - Paginated search with result processing
- `_extract_metadata()` - Dublin Core metadata parsing
- `download_article()` - PDF and metadata file downloads
- `_create_upspace_datatables_html()` - Interactive HTML generation

**Metadata Fields Extracted:**
- Title, Authors, Abstract, Year
- Publisher, Keywords, Identifiers
- **SDG Classifications** (Sustainable Development Goals)
- Handle URLs and DOIs

---

## Slide 4: SDG Classification System
### Sustainable Development Goals Integration

**Implementation Details:**
- **Field:** `dc.description.sdg`
- **Validation:** SDG numbers 1-17
- **Display:** Color-coded badges in DataTables
- **CSS:** `sdg-badge sdg-{number}` classes

**Example Output:**
- SDG-11: Sustainable Cities and Communities
- SDG-04: Quality Education
- Multiple SDGs per article supported

**Visual Impact:**
- Professional academic appearance
- Easy identification of sustainability research
- Color-coded SDG palette

---

## Slide 5: File Download System
### Complete Article Retrieval

**Download Process:**
1. Create article directory: `{output_dir}/{article_id}/`
2. Save metadata: `metadata.json`
3. Download PDF: `fulltext.pdf` (if available)
4. Error handling for missing files

**File Structure:**
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

**Bundle Navigation:**
- ORIGINAL bundle contains primary PDFs
- Bitstream filtering for PDF files only
- Direct content access via UUID

---

## Slide 6: DataTables Interface
### Interactive HTML Generation

**Features Implemented:**
- **Interactive Table:** Sortable columns, search, pagination
- **Responsive Design:** Mobile-friendly layout
- **SDG Badges:** Visual classification display
- **File Links:** Local PDF and JSON access
- **External Links:** Handle URLs and DOIs

**HTML Structure:**
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
</table>
```

---

## Slide 7: Testing Framework
### Comprehensive Validation

**Test Categories:**
1. **Unit Tests:** Individual method testing
2. **Integration Tests:** End-to-end workflows
3. **API Tests:** Real API call validation
4. **DataTables Tests:** HTML generation verification

**Test Files Created:**
- `test_upspace_search.py` - Search functionality
- `test_upspace_download.py` - File downloads
- `test_upspace_metadata.py` - Metadata extraction
- `test_upspace_datatables.py` - HTML generation
- `test_implementation.py` - Integration testing

**Validation Results:**
- ✅ 5+ articles retrieved per search
- ✅ All metadata fields parsed correctly
- ✅ SDG badges display properly
- ✅ Files download successfully
- ✅ DataTables generate correctly

---

## Slide 8: Error Handling & Security
### Production-Ready Implementation

**Rate Limiting:**
```python
time.sleep(0.5)  # 500ms delay between requests
```

**Error Recovery:**
- Network failures with retry logic
- JSON parsing error handling
- File operation error recovery
- Missing data fallback values

**Security Measures:**
- **HTML Escaping:** XSS prevention
- **Input Validation:** Query sanitization
- **File Path Safety:** Directory traversal prevention
- **API Usage:** Respectful rate limiting

**Validation:**
- SDG number range checking (1-17)
- URL format validation
- File extension verification
- Metadata completeness checking

---

## Slide 9: Results & Performance
### Successful Implementation

**Sample Output:**
```
Found 5 articles for query: 'sustainable development'
✓ Article download completed
✓ DataTables HTML file created (18,573 bytes)
✓ Index HTML file created (6,591 bytes)
```

**Files Generated:**
- **DataTables HTML:** Interactive table with search/sort
- **Index HTML:** Overview page with navigation
- **Article Directories:** Organized file structure
- **Metadata JSON:** Complete article information

**Performance Metrics:**
- Search response time: < 2 seconds
- File download: Successful for available PDFs
- HTML generation: < 1 second
- Memory usage: Efficient for large result sets

---

## Slide 10: Future Enhancements
### Roadmap and Opportunities

**Potential Improvements:**
1. **Advanced Search:** Filter by date, author, SDG
2. **Bulk Downloads:** Multiple article processing
3. **Citation Export:** BibTeX, RIS formats
4. **Analytics Dashboard:** Usage statistics
5. **Caching:** Local result caching

**Integration Opportunities:**
- **Streamlit UI:** Web interface integration
- **CLI Tools:** Command-line interface
- **API Wrapper:** Simplified API access
- **Plugin System:** Extensible architecture

**Technical Debt:**
- Code documentation improvements
- Performance optimization
- Additional error scenarios
- Extended metadata support

---

## Conclusion

**Key Success Factors:**
- **Robust API Integration:** Full DSpace REST API support
- **Rich Metadata Extraction:** Comprehensive Dublin Core parsing
- **SDG Classification:** Visual sustainability goal display
- **Interactive Interface:** Professional DataTables implementation
- **Comprehensive Testing:** Thorough validation framework
- **Production Ready:** Error handling and security measures

**Impact:**
This implementation provides a solid foundation for accessing and analyzing academic content from the University of Pretoria's institutional repository, with particular emphasis on sustainable development research and SDG classification. 