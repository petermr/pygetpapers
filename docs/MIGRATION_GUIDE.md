# Migration Guide: From Pygetpapers CLI to Streamlit UI

## Overview

This guide helps you transition from using the pygetpapers command-line interface (CLI) to the new Streamlit web interface.

## Quick Comparison

| Feature | CLI Command | Streamlit UI |
|---------|-------------|--------------|
| Basic search | `pygetpapers -q "query"` | Enter query in search box |
| Limit results | `pygetpapers -k 10` | Set "Maximum Results" to 10 |
| Download XML | `pygetpapers --xml` | Check "Download XML" box |
| Download PDF | `pygetpapers --pdf` | Check "Download PDF" box |
| Date range | `pygetpapers --startdate 2020-01-01 --enddate 2023-12-31` | Use date pickers |
| Output directory | `pygetpapers -o "my_output"` | Set "Output Directory" (auto-generated as `{repo_name}_{timestamp}`) |

## Step-by-Step Migration

### 1. Starting the Application

**CLI:**
```bash
pygetpapers -q "your query"
```

**Streamlit:**
```bash
python run_streamlit.py
```
Then open your browser to `http://localhost:8502`

### 2. Basic Search

**CLI:**
```bash
pygetpapers -q "machine learning" -k 10
```

**Streamlit:**
1. Enter "machine learning" in the search query box
2. Set "Maximum Results" to 10
3. Click "Search and Download"

### 3. Advanced Search with Options

**CLI:**
```bash
pygetpapers -q "artificial intelligence" -k 50 --xml --pdf --makecsv -o "ai_papers"
```

**Streamlit:**
1. Enter "artificial intelligence" in the search query box
2. Set "Maximum Results" to 50
3. Check "Download XML"
4. Check "Download PDF"
5. Check "Generate CSV Metadata"
6. Output directory will auto-generate as "europe_pmc_20250121_143022" (or customize)
7. Click "Search and Download"

### 4. Date-Range Search

**CLI:**
```bash
pygetpapers -q "COVID-19" --startdate 2020-01-01 --enddate 2023-12-31
```

**Streamlit:**
1. Enter "COVID-19" in the search query box
2. Set "Start Date" to 2020-01-01
3. Set "End Date" to 2023-12-31
4. Click "Search and Download"

### 5. Complex Boolean Queries

**CLI:**
```bash
pygetpapers -q "(machine learning OR artificial intelligence) AND (healthcare OR medicine)"
```

**Streamlit:**
1. Use the "Query Builder" page for complex queries
2. Add multiple query parts with AND/OR operators
3. Or enter the full query directly in the search box

## Key Differences

### Advantages of Streamlit UI:
- **Visual Interface**: No need to remember command syntax
- **Real-time Feedback**: See results immediately
- **Corpus Management**: Built-in tools to manage multiple corpora
- **Data Tables**: Interactive tables for viewing results
- **Figures Gallery**: Extract and view figures from papers
- **Fulltext Search**: Search within downloaded papers
- **Settings**: Persistent configuration

### When to Use CLI:
- **Automation**: Scripts and batch processing
- **Server Environments**: Headless servers without GUI
- **Quick One-off Searches**: Simple queries you know by heart

## Output Location

**CLI:** Files are saved to the specified output directory
**Streamlit:** Same location, but you can browse and manage corpora through the UI

## Tips for New Users

1. **Start Simple**: Begin with basic keyword searches
2. **Use Query Builder**: For complex queries, use the Query Builder page
3. **Check Repository Features**: Different repositories support different options
4. **Manage Corpora**: Use the Corpus Manager to organize your downloads
5. **Explore Data Tables**: View your results in interactive tables

## Troubleshooting

### Common Issues:

**"No results found"**
- Try simpler queries
- Check spelling
- Use broader terms

**"Repository not available"**
- Check internet connection
- Try a different repository
- Verify the repository is working

**"Download errors"**
- Reduce the result limit
- Check available disk space
- Verify file permissions

## Getting Help

- Use the "Help" page in the Streamlit UI
- Check the documentation in the `docs/` folder
- Review the README files for detailed information

## Next Steps

After migrating to the Streamlit UI, explore these features:
- **Corpus Comparison**: Compare multiple corpora
- **Fulltext Search**: Search within downloaded papers
- **Figures Gallery**: Extract and view figures
- **Data Tables**: Interactive data exploration 