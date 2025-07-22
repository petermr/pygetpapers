# UPSpace Repository Site Exploration

**Date:** July 22, 2025  
**Repository:** University of Pretoria UPSpace  
**URL:** https://repository.up.ac.za  
**Technology:** DSpace 7.x with REST API

## 1. Site Structure Analysis

### 1.1 Repository Overview
- **Name:** University of Pretoria Repository
- **Site ID:** d6c94cc4-ad92-4dff-96d8-e5ce3913a31f
- **Total Items:** 85,228 (as of July 2025)
- **Technology Stack:** DSpace 7.x with Angular frontend
- **API Base:** https://repository.up.ac.za/server/api

### 1.2 Faculty/Collection Structure
The repository is organized into 9 faculties:
1. **Economic and Management Sciences**
2. **Education**
3. **Engineering, Built Environment and Information Technology**
4. **Gordon Institute of Business Science (GIBS)**
5. **Health Sciences**
6. **Humanities**
7. **Law**
8. **Natural and Agricultural Sciences**
9. **Theology**
10. **Veterinary Science**

### 1.3 Content Types
- **Theses and Dissertations**
- **Research Articles**
- **ETD Self Submissions**
- **UPSpace Workspace**
- **Special Collections** (Mapungubwe, Christine Seegers Biomedical Illustrations)

## 2. Search Interface Analysis

### 2.1 Search API Endpoints
- **Search Base:** `https://repository.up.ac.za/server/api/discover/search`
- **Search Objects:** `https://repository.up.ac.za/server/api/discover/search/objects`
- **Browse Endpoints:** `https://repository.up.ac.za/server/api/discover/browses`

### 2.2 Available Search Filters
1. **title** - Text search with operators: equals, notequals, authority, notauthority, contains, notcontains, query
2. **author** - Text search with facets
3. **upauthor** - UP author specific search
4. **supervisor** - Supervisor search
5. **postgraduate** - Postgraduate student search
6. **subject** - Hierarchical subject search
7. **dateIssued** - Date range search
8. **sdg** - Sustainable Development Goals
9. **department** - Department filter
10. **itemtype** - Item type filter
11. **has_content_in_original_bundle** - Content availability filter

### 2.3 Sort Options
- **score** (desc) - Relevance
- **dc.title** (asc) - Title alphabetical
- **dc.date.issued** (desc) - Publication date
- **dc.date.accessioned** (desc) - Accession date

### 2.4 Browse Options
- **dateissued** - Browse by date
- **author** - Browse by author
- **upauthor** - Browse by UP author
- **supervisor** - Browse by supervisor
- **postgraduate** - Browse by postgraduate
- **title** - Browse by title
- **subject** - Browse by subject

## 3. Metadata Structure Analysis

### 3.1 Core Dublin Core Fields
- **dc.title** - Article title
- **dc.contributor.author** - Author names
- **dc.contributor.email** - Author email addresses
- **dc.date.issued** - Publication date
- **dc.date.accessioned** - Repository accession date
- **dc.date.available** - Availability date
- **dc.description.abstract** - Abstract text
- **dc.description.department** - Department
- **dc.description.sdg** - Sustainable Development Goals
- **dc.description.uri** - External publication URL
- **dc.identifier.citation** - Citation information
- **dc.identifier.issn** - ISSN numbers
- **dc.identifier.other** - DOI and other identifiers
- **dc.identifier.uri** - Handle URL
- **dc.language.iso** - Language code
- **dc.publisher** - Publisher name
- **dc.rights** - Copyright information
- **dc.subject** - Subject keywords
- **dc.type** - Content type (Article, Thesis, etc.)

### 3.2 UP-Specific Fields
- **dc.contributor.upauthor** - UP author specific
- **dc.contributor.postgraduate** - Postgraduate student
- **dc.contributor.advisor** - Supervisor/advisor
- **dc.contributor.coadvisor** - Co-advisor
- **dc.description.librarian** - Librarian identifier

## 4. File Download Structure

### 4.1 Bundle Organization
- **ORIGINAL** - Main content bundle
- **THUMBNAIL** - Thumbnail images
- **LICENSE** - License files
- **TEXT** - Text versions

### 4.2 File Access Pattern
```
Item UUID → Bundles → Bitstreams → Content
```

**Example:**
- Item: `7a9505b6-50de-4325-9712-4e1c0a7c0f24`
- Bundle: `fe04c89b-8d2e-4e20-a3fc-7e625b1c0424` (ORIGINAL)
- Bitstream: `3d745952-930f-4a19-a2ef-9a7ae71013c6`
- File: `Manyuchi_Systems_2021.pdf`

### 4.3 File Download URLs
- **Content:** `https://repository.up.ac.za/server/api/core/bitstreams/{uuid}/content`
- **Metadata:** `https://repository.up.ac.za/server/api/core/bitstreams/{uuid}`
- **Format:** `https://repository.up.ac.za/server/api/core/bitstreams/{uuid}/format`

## 5. API Authentication and Access

### 5.1 Authentication Status
- **Public Access:** Yes, most content is publicly accessible
- **Authentication Required:** No for basic search and download
- **Registration Available:** Yes, via `epersonRegistration` feature

### 5.2 Rate Limiting
- **Request Delays:** Recommended 1-2 seconds between requests
- **API Limits:** Not explicitly documented
- **Caching:** 15-minute cache (900000ms) for API responses

## 6. Content Analysis

### 6.1 Recent Content Examples
1. **"Contested heritage(s) - the case(s) of the battle of blood river"** (2024)
   - Authors: Van der Merwe, Clinton David
   - Department: Humanities Education
   - SDG: SDG-11, SDG-04
   - DOI: 10.15170/MG.2024.19.02.07

2. **"Suburban transformation in post-apartheid South Africa"** (2024)
   - Authors: Sekonyela, Boniswa Kelebogile; Gregory, James J.; Rogerson, Jayne M.
   - Department: Geography, Geoinformatics and Meteorology
   - SDG: SDG-11

3. **"Multilocus sequence typing and antimicrobial susceptibility"** (2024)
   - Authors: Jashari, Besart; et al.
   - Department: Biochemistry, Genetics and Microbiology
   - SDG: SDG-03, SDG-02

### 6.2 Content Characteristics
- **Languages:** Primarily English, some Afrikaans
- **Geographic Focus:** South Africa, Africa
- **Research Areas:** Strong in health sciences, agriculture, social sciences
- **Publication Types:** Articles, theses, dissertations, reports

## 7. Implementation Considerations

### 7.1 Technical Advantages
- **RESTful API** - Well-structured, predictable endpoints
- **Rich Metadata** - Comprehensive Dublin Core fields
- **File Access** - Direct download URLs available
- **Search Flexibility** - Multiple filter and sort options
- **Pagination** - Built-in pagination support

### 7.2 Implementation Strategy
1. **Use REST API** - Avoid web scraping, use structured API
2. **Implement Pagination** - Handle large result sets
3. **Respect Rate Limits** - Add delays between requests
4. **Handle Metadata** - Extract rich metadata for DataTables
5. **File Downloads** - Use direct bitstream content URLs
6. **Error Handling** - Handle API errors gracefully

### 7.3 Unique Features to Leverage
- **SDG Classification** - Filter by Sustainable Development Goals
- **Department Filtering** - Faculty-specific searches
- **UP Author Identification** - University-specific author tracking
- **Handle URLs** - Persistent identifiers for articles
- **Citation Information** - Pre-formatted citations available

## 8. Conclusion

UPSpace provides an excellent foundation for repository integration with:
- **Comprehensive REST API** with rich search capabilities
- **Well-structured metadata** following Dublin Core standards
- **Direct file access** through bitstream endpoints
- **Academic focus** with faculty organization
- **South African research** emphasis

The repository is well-suited for integration into pygetpapers with proper API usage and rate limiting considerations. 