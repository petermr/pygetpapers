# Corpus Module

A standalone Python module for managing and analyzing document corpora. Extracted from the AmiLib project for use in pygetpapers Streamlit UI and other projects.

## Features

- Hierarchical corpus management (directories and files)
- Search functionality across corpus files
- Query management and execution
- Results visualization and HTML generation
- Integration with pygetpapers output
- DataTables generation from corpus data
- Support for multiple document formats

## Installation

```bash
pip install corpus-module
```

## Quick Start

```python
from corpus_module import AmiCorpus, AmiCorpusContainer

# Create a new corpus
corpus = AmiCorpus(
    topdir="my_documents",
    globstr="**/*.html",
    make_descendants=True,
    mkdir=True
)

# Create a container for a specific document type
reports = corpus.create_corpus_container(
    "reports", 
    bib_type="report", 
    mkdir=True
)

# Create a document
doc = reports.create_document(
    "analysis.html", 
    text="<html><body><h1>Analysis Report</h1></body></html>"
)

# List files in corpus
files = corpus.list_files("**/*.html")
print(f"Found {len(files)} HTML files")
```

## Search Functionality

```python
from corpus_module import CorpusQuery, CorpusSearch

# Create a query
query = CorpusQuery(
    query_id="climate_search",
    phrases=["climate change", "global warming", "carbon emissions"],
    outfile="results.html"
)

# Search corpus files
infiles = corpus.list_files("**/*.html")
results = CorpusSearch.search_files_with_phrases_write_results(
    infiles=infiles,
    phrases=query.phrases,
    outfile=query.outfile,
    debug=True
)
```

## DataTables Integration

```python
# Create DataTables from corpus
corpus.make_datatables(
    indir="my_documents",
    outdir="output",
    outfile_h="corpus_table.html"
)

# Create DataTables with filenames
corpus.create_datatables_html_with_filenames(
    html_glob="**/*.html",
    labels=["File", "Type", "Size"],
    table_id="corpus_files",
    outpath="files_table.html"
)
```

## Query Management

```python
# Create multiple queries
climate_query = corpus.get_or_create_corpus_query(
    query_id="climate",
    phrases=["climate", "temperature", "weather"]
)

energy_query = corpus.get_or_create_corpus_query(
    query_id="energy",
    phrases=["energy", "power", "electricity"]
)

# Run multiple queries
results = corpus.search_files_with_queries([
    "climate",
    "energy"
], debug=True)

# Process results
for query_id, html_result in results.items():
    print(f"Query {query_id} found results")
    # Save or process HTML result
```

## Advanced Usage

### Hierarchical Corpus Structure

```python
# Create a complex corpus structure
corpus = AmiCorpus("research_papers", mkdir=True)

# Create year-based containers
for year in ["2020", "2021", "2022"]:
    year_container = corpus.create_corpus_container(year, bib_type="year", mkdir=True)
    
    # Create subject containers within each year
    for subject in ["climate", "energy", "health"]:
        subject_container = year_container.create_corpus_container(
            subject, 
            bib_type="subject", 
            mkdir=True
        )
        
        # Add documents
        subject_container.create_document(
            f"paper_{subject}_{year}.html",
            text=f"<html><body><h1>{subject} research from {year}</h1></body></html>"
        )
```

### Custom Search with XPath

```python
# Search with custom XPath for paragraph elements
results = CorpusSearch.search_files_with_phrases_write_results(
    infiles=corpus.list_files("**/*.html"),
    phrases=["methane", "emissions"],
    para_xpath="//p[@class='content']",  # Custom XPath
    outfile="methane_results.html"
)
```

### Integration with pygetpapers

```python
# After running pygetpapers, create DataTables from results
import json
from pathlib import Path

# Assuming pygetpapers created a directory with results
pygetpapers_dir = Path("pygetpapers_output")

# Create DataTables from pygetpapers JSON results
if (pygetpapers_dir / "eupmc_result.json").exists():
    AmiCorpus.make_datatables(
        indir=pygetpapers_dir,
        outdir=pygetpapers_dir,
        outfile_h="search_results_table.html"
    )
```

## Streamlit Integration

```python
import streamlit as st
from corpus_module import AmiCorpus
import lxml.etree as ET

# Create corpus
corpus = AmiCorpus("documents", globstr="**/*.html")

# Create DataTable
htmlx, tbody = corpus.create_datatables_html_with_filenames(
    html_glob="**/*.html",
    labels=["File", "Type"],
    table_id="corpus_files"
)

# Display in Streamlit
st.components.v1.html(
    ET.tostring(htmlx, encoding='unicode'),
    height=600
)
```

## Configuration

The module supports various configuration options:

```python
# Create corpus with specific options
corpus = AmiCorpus(
    topdir="documents",
    globstr="**/*.{html,pdf,txt}",  # Multiple file types
    make_descendants=True,  # Create containers for all subdirectories
    mkdir=True,  # Create directories if they don't exist
    eupmc=True  # Enable EuropePMC specific features
)
```

## Dependencies

- **lxml**: XML/HTML processing
- **datatables-module**: For DataTables generation
- **pathlib**: Path manipulation (Python standard library)
- **json**: JSON processing (Python standard library)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

This module was extracted from the [AmiLib](https://github.com/amilib/amilib) project and adapted for standalone use. 