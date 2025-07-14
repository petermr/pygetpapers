# Pygetpapers Quick Reference

## Basic Commands

```bash
# Search papers (default: Europe PMC)
pygetpapers --query "your search term" --limit 10

# Specify repository
pygetpapers --api europe_pmc --query "search term" --limit 10

# Generate CSV output
pygetpapers --api europe_pmc --query "search term" --limit 10 --makecsv

# Generate interactive datatables
pygetpapers --api europe_pmc --query "search term" --limit 10 --datatables

# Download full-text XML
pygetpapers --api europe_pmc --query "search term" --limit 10 --xml

# Download PDFs (where available)
pygetpapers --api europe_pmc --query "search term" --limit 10 --pdf
```

## Available Repositories

| Repository | Command | Features |
|------------|---------|----------|
| Europe PMC | `--api europe_pmc` | XML, PDF, CSV, Datatables |
| bioRxiv | `--api biorxiv` | HTML, Date ranges |
| medRxiv | `--api medrxiv` | HTML, Date ranges |
| Crossref | `--api crossref` | Metadata, Filters |
| OpenAlex | `--api openalex` | Academic graph data |
| Redalyc | `--api redalyc_selenium` | Latin American journals |

## Output Formats

| Format | Flag | Description |
|--------|------|-------------|
| JSON | (default) | Metadata in JSON format |
| CSV | `--makecsv` | Spreadsheet-friendly format |
| HTML | `--makehtml` | Static HTML tables |
| Datatables | `--datatables` | Interactive HTML tables |
| XML | `--xml` | Full-text XML (where available) |
| PDF | `--pdf` | PDF downloads (where available) |

## Date Range Queries

```bash
# Europe PMC date range
pygetpapers --api europe_pmc --query "COVID-19" --startdate 2023-01-01 --enddate 2023-12-31 --limit 10

# bioRxiv/medRxiv date range
pygetpapers --api biorxiv --query "2023-06-01/2023-12-31" --limit 10
```

## Advanced Options

```bash
# Search with synonyms
pygetpapers --api europe_pmc --query "DNA sequencing" --limit 10 --synonym

# Use terms file (OR logic)
pygetpapers --api europe_pmc --query "biology" --terms terms.txt --limit 10

# Exclude terms
pygetpapers --api europe_pmc --query "cancer" --notterms exclude.txt --limit 10

# Update existing corpus
pygetpapers --api europe_pmc --query "bioinformatics" --limit 10 --update

# Restart failed downloads
pygetpapers --api europe_pmc --query "genomics" --limit 10 --restart

# Custom output directory
pygetpapers --api europe_pmc --query "test" --limit 10 --output /path/to/directory

# Set log level
pygetpapers --api europe_pmc --query "test" --limit 5 --loglevel debug

# Save logs to file
pygetpapers --api europe_pmc --query "test" --limit 5 --logfile search.log
```

## Repository-Specific Examples

### Europe PMC
```bash
# Basic search
pygetpapers --api europe_pmc --query "cancer immunotherapy" --limit 10

# Full workflow
pygetpapers --api europe_pmc --query "machine learning biology" --limit 20 --makecsv --datatables --xml
```

### bioRxiv
```bash
# Text search
pygetpapers --api biorxiv --query "genomics" --limit 10

# Date-based search
pygetpapers --api biorxiv --query "2023-01-01/2023-06-30" --limit 10
```

### Crossref
```bash
# Basic search
pygetpapers --api crossref --query "artificial intelligence" --limit 10

# With filters
pygetpapers --api crossref --query "machine learning" --limit 10 --filter "type:journal-article"
```

### OpenAlex
```bash
# Academic search
pygetpapers --api openalex --query "climate change" --limit 10

# Generate datatables
pygetpapers --api openalex --query "sustainability" --limit 10 --datatables
```

### Redalyc
```bash
# Latin American journals
pygetpapers --api redalyc_selenium --query "biodiversity" --limit 10

# Generate datatables
pygetpapers --api redalyc_selenium --query "conservation" --limit 10 --datatables
```

## Output Location

By default, all output goes to `$HOME/pygetpapers/` with timestamped directories:

- **Windows**: `C:\Users\YourUsername\pygetpapers\`
- **macOS**: `/Users/YourUsername/pygetpapers/`
- **Linux**: `/home/YourUsername/pygetpapers/`

## Common Workflows

### Quick Literature Review
```bash
# 1. Search and get overview
pygetpapers --api europe_pmc --query "your topic" --limit 50 --makecsv

# 2. Generate interactive tables
pygetpapers --api europe_pmc --query "your topic" --limit 50 --datatables

# 3. Download full-text for selected papers
pygetpapers --api europe_pmc --query "your topic" --limit 50 --xml
```

### Multi-Repository Search
```bash
# Search across multiple repositories
pygetpapers --api europe_pmc --query "topic" --limit 20 --makecsv
pygetpapers --api biorxiv --query "topic" --limit 20 --makecsv
pygetpapers --api crossref --query "topic" --limit 20 --makecsv
```

### Date-Restricted Search
```bash
# Recent papers only
pygetpapers --api europe_pmc --query "COVID-19" --startdate 2023-01-01 --enddate 2023-12-31 --limit 100 --makecsv
```

## Troubleshooting

```bash
# Check version
pygetpapers --version

# Show help
pygetpapers --help

# Debug mode
pygetpapers --api europe_pmc --query "test" --limit 5 --loglevel debug

# Test with small limit
pygetpapers --api europe_pmc --query "test" --limit 1 --noexecute
```

## File Structure

After running a search, you'll find:

```
~/pygetpapers/2024_01_15_10_30_45/
├── eupmc_results.json          # Metadata
├── europe_pmc.csv              # CSV output (if --makecsv)
├── europe_pmc.html             # HTML table (if --makehtml)
├── datatables.html             # Interactive tables (if --datatables)
├── datatables_papers.html      # Papers table
├── datatables_metadata.html    # Metadata table
├── datatables_summary.html     # Summary table
└── PMC123456/                  # Individual paper directories (if --xml)
    ├── fulltext.xml
    ├── fulltext.html
    └── metadata.json
``` 