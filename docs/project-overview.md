# Pygetpapers Streamlit UI Enhancement Project

## Project Overview

### What is pygetpapers?

Pygetpapers is a Python tool designed to assist text miners and researchers in accessing scholarly publications. It provides a command-line interface to search and download research papers from various open-access repositories using their RESTful APIs.

### Key Features of pygetpapers

- **Multi-repository support**: Searches across Europe PMC, arXiv, Crossref, bioRxiv, medRxiv, and OpenAlex
- **Flexible query system**: Supports complex Boolean queries with nested quoting
- **Multiple output formats**: Downloads full-text XML, PDF, supplementary files, references, and citations
- **Metadata management**: Saves metadata in JSON, CSV, and HTML formats
- **Corpus management**: Creates and manages CProject directory structures for text mining
- **Date range filtering**: Supports date-based queries for time-sensitive research
- **Term-based queries**: Allows querying using term lists from files

### Current Architecture

The pygetpapers project follows a modular architecture:

```
pygetpapers/
├── pygetpapers.py          # Main CLI interface
├── download_tools.py       # Core download functionality
├── repository/             # Repository-specific implementations
│   ├── europe_pmc.py
│   ├── arxiv.py
│   ├── crossref.py
│   ├── openalex.py
│   ├── rxiv.py

├── config.ini             # Repository configuration
└── extensions.py          # Extension functionality
```

### Streamlit UI Enhancement Goals

The Streamlit UI enhancement aims to:

1. **Improve accessibility**: Provide a user-friendly web interface for new users who may not be comfortable with command-line tools
2. **Complex query building**: Enable creation of complex Boolean queries with visual query builders and nested quoting support
3. **Corpus management**: Provide visual tools for managing downloaded papers as a corpus
4. **Enhanced user experience**: Offer real-time feedback, progress tracking, and result visualization
5. **Preserve CLI functionality**: Maintain all existing CLI capabilities while adding web interface

### Target Users

- **Researchers**: Who need to quickly search and download papers for literature reviews
- **Text miners**: Who require systematic paper collection for analysis
- **Students**: Learning about research paper discovery and collection
- **Librarians**: Assisting researchers with systematic literature searches

### Technical Requirements

- **Backend**: Leverage existing pygetpapers CLI functionality
- **Frontend**: Streamlit web application
- **Query Builder**: Visual interface for complex Boolean queries
- **Corpus Viewer**: Display and manage downloaded papers
- **Progress Tracking**: Real-time download progress and status
- **Export Options**: Multiple format support for results

### Success Metrics

- Reduced learning curve for new users
- Increased adoption of complex query features
- Improved user satisfaction with paper discovery process
- Maintained performance and reliability of existing CLI

## Repository Support Matrix

| Repository | Query Support | Date Range | PDF Download | XML Download | References | Citations | Supplementary Files |
|------------|---------------|------------|--------------|--------------|------------|-----------|-------------------|
| Europe PMC | ✅ Full | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| arXiv | ✅ Full | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Crossref | ✅ Full | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| OpenAlex | ✅ Full | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| bioRxiv | ❌ (Date only) | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| medRxiv | ❌ (Date only) | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |


## Query Format Examples

### Simple Queries
- `"artificial intelligence"`
- `"machine learning" AND "deep learning"`

### Complex Boolean Queries
- `"(LICENSE:'cc by' OR LICENSE:'cc-by') AND METHODS:'transcriptome assembly'"`
- `"cancer" AND ("treatment" OR "therapy") AND NOT "review"`

### Date Range Queries
- `"covid-19" AND FIRST_PDATE:[2020-01-01 TO 2023-12-31]`

### Field-Specific Queries
- `AUTH:"Smith J" AND TITLE:"machine learning"`
- `ABSTRACT:"neural networks" AND JOURNAL:"Nature"` 