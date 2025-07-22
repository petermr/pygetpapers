# UPSpace HTML Structure Analysis

## Overview
UPSpace (University of Pretoria Repository) uses a modern DSpace 7.x installation with a JavaScript-heavy frontend and RESTful API backend.

## Key Findings

### 1. API Endpoints Discovered
- **Base API**: `https://repository.up.ac.za/server/api`
- **Search API**: `https://repository.up.ac.za/server/api/discover/search/objects`
- **Items API**: `https://repository.up.ac.za/server/api/core/items/{uuid}`
- **Bundles API**: `https://repository.up.ac.za/server/api/core/items/{uuid}/bundles`
- **Bitstreams API**: `https://repository.up.ac.za/server/api/core/bitstreams/{uuid}/content`

### 2. Frontend Structure
- **Main Page**: `https://repository.up.ac.za/discover` (JavaScript SPA)
- **Search Interface**: Angular-based with REST API calls
- **Content Loading**: Dynamic via JavaScript, not server-side rendered

### 3. Data Structure Analysis

#### Search Results Structure
```json
{
  "type": {"value": "discovery-objects"},
  "page": [
    {
      "type": {"value": "searchresult"},
      "hitHighlights": {},
      "_links": {
        "indexableObject": {
          "href": "https://repository.up.ac.za/server/api/core/items/{uuid}"
        }
      }
    }
  ],
  "pageInfo": {
    "elementsPerPage": 5,
    "totalElements": 85228,
    "totalPages": 17046,
    "currentPage": 1
  }
}
```

#### Item Metadata Structure
```json
{
  "handle": "2263/103497",
  "lastModified": "2025-07-21T20:07:36.762Z",
  "isArchived": true,
  "isDiscoverable": true,
  "isWithdrawn": false,
  "_name": "Article Title",
  "metadata": {
    "dc.title": [{"value": "Article Title", "language": "en_ZA"}],
    "dc.contributor.author": [{"value": "Author Name", "language": "en_ZA"}],
    "dc.description.abstract": [{"value": "Abstract text", "language": "en_ZA"}],
    "dc.date.issued": [{"value": "2024", "language": "en_ZA"}],
    "dc.description.sdg": [
      {"value": "SDG-11: Sustainable cities and communities", "language": "en_ZA"},
      {"value": "SDG-04: Quality Education", "language": "en_ZA"}
    ],
    "dc.identifier.uri": [{"value": "http://hdl.handle.net/2263/103497", "language": "en_ZA"}],
    "dc.identifier.other": [{"value": "10.15170/MG.2024.19.02.07", "language": "en_ZA"}],
    "dc.subject": [{"value": "Subject keyword", "language": "en_ZA"}],
    "dc.publisher": [{"value": "Publisher Name", "language": "en_ZA"}],
    "dc.type": [{"value": "Article", "language": "en_ZA"}]
  }
}
```

### 4. Key Metadata Fields for Web Scraping

#### Essential Fields
- **Title**: `dc.title`
- **Authors**: `dc.contributor.author`
- **Abstract**: `dc.description.abstract`
- **Year**: `dc.date.issued`
- **Handle URL**: `dc.identifier.uri`
- **DOI**: `dc.identifier.other`
- **Subjects/Keywords**: `dc.subject`
- **Publisher**: `dc.publisher`
- **Type**: `dc.type`

#### SDG Classifications
- **Field**: `dc.description.sdg`
- **Format**: "SDG-XX: Description" (e.g., "SDG-11: Sustainable cities and communities")
- **Multiple values**: Articles can have multiple SDG classifications

### 5. File Download Structure

#### Bundles API Response
```json
{
  "type": {"value": "paginated-list"},
  "page": [
    {
      "name": "ORIGINAL",
      "type": "bundle",
      "_links": {
        "bitstreams": {
          "href": "https://repository.up.ac.za/server/api/core/bundles/{uuid}/bitstreams"
        }
      }
    }
  ]
}
```

#### Bitstreams API Response
```json
{
  "type": {"value": "paginated-list"},
  "page": [
    {
      "name": "document.pdf",
      "type": "bitstream",
      "sizeBytes": 1234567,
      "bundleName": "ORIGINAL",
      "_links": {
        "content": {
          "href": "https://repository.up.ac.za/server/api/core/bitstreams/{uuid}/content"
        }
      }
    }
  ]
}
```

### 6. Search Parameters

#### Available Search Filters
- **Title**: `title`
- **Author**: `author`, `upauthor`
- **Subject**: `subject`
- **Date Issued**: `dateIssued`
- **SDG**: `sdg`
- **Department**: `department`
- **Item Type**: `itemtype`

#### Search URL Structure
```
https://repository.up.ac.za/server/api/discover/search/objects?
  dsoType=ITEM&
  sort=dc.date.accessioned,DESC&
  page=0&
  size=20&
  query=search+terms
```

### 7. Rate Limiting Considerations
- API appears to support standard HTTP requests
- No immediate authentication required for public data
- Recommended delay: 1-2 seconds between requests

### 8. Implementation Strategy

#### Web Scraping Approach
1. **Search**: Use REST API endpoint for search results
2. **Metadata**: Extract from JSON responses
3. **File Downloads**: Follow bundle → bitstream → content chain
4. **SDG Processing**: Parse `dc.description.sdg` field
5. **Error Handling**: Implement retry logic for failed requests

#### Advantages of API Approach
- Structured JSON data (no HTML parsing needed)
- Reliable data extraction
- Better performance than HTML scraping
- Consistent data format

#### Implementation Notes
- Use `requests` library for API calls
- Parse JSON responses directly
- Handle pagination for large result sets
- Implement proper error handling and retries
- Extract SDG classifications from metadata
- Generate clean article IDs from Handle URLs

## Conclusion
UPSpace provides a well-structured REST API that can be used directly for data extraction, eliminating the need for complex HTML parsing. The API provides all necessary metadata including SDG classifications, making it ideal for the pygetpapers implementation. 