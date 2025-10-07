# Repository Fields Schema Documentation

**Date:** July 27, 2025 (system date of generation)  
**Purpose:** Document field output schemas for all 6 current pygetpapers repositories  
**Scope:** biorxiv, europe_pmc, openalex, redalyc, scielo, upspace

## Schema Categorization

### Primary Fields (Immediate Information)
Fields that are directly available from the repository's search API or basic metadata extraction.

### Secondary Fields (Further Requests)
Fields that require additional web scraping, file downloads, or extended API calls.

---

## 1. BioRxiv Repository

### Primary Fields
```json
{
  "title": "string",
  "authors": ["string"],
  "doi": "string",
  "biorxiv_id": "string",
  "journal": "string",
  "publication_date": "string",
  "subject_areas": ["string"],
  "url": "string",
  "extracted_at": "datetime",
  "pisa_id": "string",
  "apath": "string"
}
```

### Secondary Fields
```json
{
  "fulltext_html": "string (HTML content)",
  "pdf_url": "string",
  "file_size": "integer",
  "download_timestamp": "datetime",
  "jsondownloaded": "boolean"
}
```

### Repository Structure and Naming Conventions

#### Directory Structure
```
{user_repo_directory}/
├── datatables.html                    # Main DataTables interface
├── {repository}_papers_data.json      # Paper metadata
└── pdfs/
    ├── {paper_id_1}/
    │   ├── fulltext.pdf               # Original PDF (manually downloaded)
    │   ├── fulltext.html              # Downloaded HTML content
    │   └── fulltext.pdf.html          # PDF converted to HTML (derived)
    ├── {paper_id_2}/
    │   ├── fulltext.pdf
    │   ├── fulltext.html
    │   └── fulltext.pdf.html
    └── ...
```

#### Naming Conventions
- **Repository Directory**: User-defined (e.g., `./examples/lantana_biorxiv/`)
- **Article Subdirectories**: Named by paper ID (e.g., `/292722/`, `/126490/`)
- **Content Files**: Reserved names indicating type and format:
  - `fulltext.pdf` - Original PDF content
  - `fulltext.html` - Downloaded HTML content
  - `fulltext.pdf.html` - PDF converted to HTML (derived content)
- **DataTables Location**: `{repo_directory}/datatables.html`

#### PDF Download Workflow
1. **DataTables Interface**: Located at `{repo_directory}/datatables.html`
2. **PDF Links**: Point to BioRxiv repository URLs
3. **Manual Download**: User clicks PDF cells and saves to `/{paper_id}/fulltext.pdf`
4. **Local Detection**: DataTables shows green "Local PDF" when file exists

**Notes:** BioRxiv uses web scraping for full text extraction and PDF downloads. Due to Cloudflare protection, PDF downloads require manual intervention through the DataTables interface.

---

## 2. Europe PMC Repository

### Primary Fields
```json
{
  "title": "string",
  "authors": ["string"],
  "abstract": "string",
  "keywords": ["string"],
  "journal_title": "string",
  "pmcid": "string",
  "pmid": "string",
  "doi": "string",
  "publication_date": "string",
  "html_links": ["string"],
  "pdf_links": ["string"],
  "cursor_mark": "string"
}
```

### Secondary Fields
```json
{
  "fulltext.pdf": "file",
  "fulltext.xml": "file",
  "fulltext.xml.html": "file",
  "fulltext.csv": "file",
  "references": "file",
  "citations": "file",
  "supplementary_files": ["file"],
  "zip_files": "file",
  "pdfdownloaded": "boolean",
  "xmldownloaded": "boolean",
  "csvmade": "boolean",
  "htmldownloaded": "boolean"
}
```

**Notes:** Europe PMC provides extensive secondary content including XML, PDF, and supplementary files.

---

## 3. OpenAlex Repository

### Primary Fields
```json
{
  "title": "string",
  "authors": ["string"],
  "doi": "string",
  "publication_date": "string",
  "journal": "string",
  "abstract": "string",
  "keywords": ["string"],
  "best_oa_location": {
    "pdf_url": "string",
    "landing_page_url": "string"
  },
  "open_access": "boolean",
  "cited_by_count": "integer",
  "type": "string"
}
```

### Secondary Fields
```json
{
  "fulltext.pdf": "file",
  "pdfdownloaded": "boolean",
  "cursor_mark": "string",
  "total_results": "integer"
}
```

**Notes:** OpenAlex focuses on open access metadata with PDF download capabilities.

---

## 4. Redalyc Repository

### Primary Fields
```json
{
  "title": "string",
  "authors": ["string"],
  "abstract": "string",
  "journal": "string",
  "year": "string",
  "url": "string",
  "article_id": "string",
  "content_preview": "string",
  "pdf_url": "string",
  "language": "string",
  "keywords": ["string"],
  "volume": "string",
  "issue": "string",
  "pages": "string"
}
```

### Secondary Fields
```json
{
  "fulltext.html": "file",
  "fulltext.pdf": "file",
  "metadata.json": "file",
  "extracted_at": "datetime"
}
```

**Notes:** Redalyc uses Selenium web scraping for comprehensive metadata extraction.

---

## 5. SciELO Repository

### Primary Fields
```json
{
  "title": "string",
  "authors": ["string"],
  "abstract": "string",
  "journal": "string",
  "year": "string",
  "doi": "string",
  "language": "string",
  "keywords": ["string"],
  "volume": "string",
  "issue": "string",
  "pages": "string",
  "url": "string",
  "collection": "string",
  "pdf_urls": ["string"]
}
```

### Secondary Fields
```json
{
  "fulltext.html": "file",
  "fulltext.pdf": "file",
  "metadata.json": "file",
  "extracted_at": "datetime"
}
```

**Notes:** SciELO uses web scraping with multiple CSS selectors for robust metadata extraction.

---

## 6. UPSpace Repository

### Primary Fields
```json
{
  "title": "string",
  "authors": ["string"],
  "abstract": "string",
  "year": "string",
  "publisher": "string",
  "type": "string",
  "handle_url": "string",
  "handle_id": "string",
  "doi": "string",
  "keywords": ["string"],
  "sdg_classifications": ["string"],
  "language": "string",
  "uuid": "string",
  "id": "integer"
}
```

### Secondary Fields
```json
{
  "fulltext.pdf": "file",
  "metadata.json": "file",
  "upspace_datatables.html": "file",
  "index.html": "file"
}
```

**Notes:** UPSpace uses DSpace REST API with unique SDG (Sustainable Development Goals) classifications.

---

## Common Field Patterns

### Universal Primary Fields
All repositories provide these core fields:
- `title` (string)
- `authors` (array of strings)
- `doi` (string, when available)
- `year` or `publication_date` (string)
- `abstract` (string, when available)

### Universal Secondary Fields
Most repositories support:
- `fulltext.pdf` (file download)
- `metadata.json` (structured metadata)
- `fulltext.html` (HTML version, when available)

### Repository-Specific Features

#### BioRxiv
- Unique `biorxiv_id` field
- Subject area classifications
- Web scraping for full text

#### Europe PMC
- Extensive secondary content (XML, CSV, references, citations)
- Multiple file format support
- Cursor-based pagination

#### OpenAlex
- Open access focus
- Citation counts
- Best OA location metadata

#### Redalyc
- Spanish/Portuguese language support
- Content previews
- Selenium-based scraping

#### SciELO
- Multi-language support
- Collection-based organization
- Robust CSS selector fallbacks

#### UPSpace
- SDG (Sustainable Development Goals) classifications
- DSpace handle system
- Institutional repository focus

---

## Schema Validation Recommendations

### Required Fields for All Repositories
```json
{
  "title": "required",
  "authors": "required",
  "repository": "required",
  "extracted_at": "required"
}
```

### Optional but Common Fields
```json
{
  "doi": "optional",
  "abstract": "optional",
  "year": "optional",
  "journal": "optional",
  "keywords": "optional"
}
```

### File Output Standards
- Metadata files: `metadata.json`
- PDF files: `fulltext.pdf`
- HTML files: `fulltext.html`
- XML files: `fulltext.xml`

---

## Implementation Notes

### Field Extraction Methods
1. **API-based**: Europe PMC, OpenAlex, UPSpace
2. **Web scraping**: BioRxiv, Redalyc, SciELO
3. **Hybrid**: Some repositories combine API and scraping

### Data Quality Considerations
- Field availability varies by repository
- Some fields require additional API calls
- Web scraping may have reliability issues
- Rate limiting affects secondary field extraction

### Future Schema Evolution
- Standardize field names across repositories
- Implement consistent data types
- Add field validation and quality metrics
- Support for new repository types

---

## Related Documentation
- [Repository Summary](repositories_summary.md)
- [Ignored Repositories](IGNORED_REPOSITORIES.md)
- [File Size Alerts](file-size-alerts.md)

---

*This schema documentation will be updated as repositories evolve and new features are added.* 