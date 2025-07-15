# Pygetpapers v2.0 Google Colab Demo

This document provides instructions for launching and using the pygetpapers v2.0 Google Colab notebook.

## Quick Start

### Option 1: Direct Launch (Recommended)

1. **Click the link below to open the notebook directly in Google Colab:**
   ```
   https://colab.research.google.com/github/pygetpapers/pygetpapers/blob/main/pygetpapers_colab_demo.ipynb
   ```

2. **If the above link doesn't work, use this alternative:**
   - Go to [Google Colab](https://colab.research.google.com/)
   - Click "File" → "Open notebook"
   - Select "GitHub" tab
   - Enter: `pygetpapers/pygetpapers`
   - Select `pygetpapers_colab_demo.ipynb`

### Option 2: Manual Upload

1. **Download the notebook:**
   - Download `pygetpapers_colab_demo.ipynb` from this repository
   
2. **Upload to Colab:**
   - Go to [Google Colab](https://colab.research.google.com/)
   - Click "File" → "Upload notebook"
   - Select the downloaded `.ipynb` file

## What the Notebook Demonstrates

### 🌍 Climate Change Research Queries
The notebook uses climate-related queries as per the project style guide:
- **Climate change** (Europe PMC)
- **Global warming** (Crossref)
- **Carbon dioxide** (bioRxiv)
- **Temperature** (medRxiv)
- **Greenhouse gas** (OpenAlex)
- **Atmospheric CO2** (PDF downloads)

### 📚 Repository Coverage
- **Europe PMC**: Biomedical and life sciences papers
- **Crossref**: Cross-disciplinary academic papers
- **bioRxiv**: Biology preprints
- **medRxiv**: Medicine preprints
- **OpenAlex**: Academic papers and citations

### 🛠️ Features Demonstrated
- ✅ Installation and setup
- ✅ Multi-repository searching
- ✅ PDF downloads (where available)
- ✅ CSV metadata export
- ✅ HTML datatables creation
- ✅ No-execute mode (count results without downloading)
- ✅ Batch processing

## Running the Notebook

### Prerequisites
- Google account (free)
- Internet connection
- No local installation required

### Step-by-Step Instructions

1. **Open the notebook** using one of the methods above

2. **Runtime Setup:**
   - Click "Runtime" → "Change runtime type"
   - Ensure "Python 3" is selected
   - GPU/TPU not required (CPU is sufficient)

3. **Run Installation Cell:**
   - Execute the first code cell to install pygetpapers
   - Wait for installation to complete (may take 1-2 minutes)

4. **Run Demo Cells:**
   - Execute cells sequentially to see different features
   - Each cell demonstrates a different repository or feature
   - Results are saved to `/content/pygetpapers_output/`

5. **View Results:**
   - Use Colab's file browser to explore downloaded files
   - Open HTML files in new tabs to view datatables
   - Download files to your local machine if needed

## Expected Outputs

### File Structure
```
/content/pygetpapers_output/
├── europe_pmc_climate/          # Climate change papers
│   ├── datatables.html         # Interactive table
│   ├── metadata.csv            # Paper metadata
│   └── index.html              # Summary page
├── crossref_global_warming/     # Global warming papers
├── biorxiv_carbon_dioxide/      # Carbon dioxide papers
├── medrxiv_temperature/         # Temperature papers
├── openalex_greenhouse_gas/     # Greenhouse gas papers
└── europe_pmc_pdfs/            # PDF downloads
    ├── *.pdf                   # Downloaded PDFs
    └── datatables.html         # Table with PDF links
```

### Sample Results
- **5-10 papers per repository** (configurable)
- **CSV files** with metadata (title, authors, DOI, etc.)
- **HTML datatables** for easy browsing
- **PDF files** where available (Europe PMC)
- **Summary statistics** for each search

## Customization

### Modify Queries
Change the search terms in any cell:
```python
query = "your search term"  # Replace with your topic
limit = 10                 # Number of papers to download
```

### Add New Repositories
Use different APIs:
```python
!pygetpapers --query "your query" --api europe_pmc --limit 5
!pygetpapers --query "your query" --api crossref --limit 5
!pygetpapers --query "your query" --api biorxiv --limit 5
```

### Download Formats
Choose what to download:
```python
# Metadata only
!pygetpapers --query "query" --makecsv --makehtml

# Include PDFs (where available)
!pygetpapers --query "query" --pdf --makecsv --datatables

# Full XML content
!pygetpapers --query "query" --xml --makecsv
```

## Troubleshooting

### Common Issues

1. **Installation fails:**
   - Check internet connection
   - Restart runtime: "Runtime" → "Restart runtime"
   - Try running installation cell again

2. **No results found:**
   - Try different search terms
   - Check if repository is accessible
   - Reduce limit to 1-2 papers for testing

3. **PDF downloads fail:**
   - PDFs are only available for Europe PMC and some OpenAlex papers
   - Other repositories don't provide PDF downloads

4. **Slow performance:**
   - Reduce `limit` parameter
   - Some repositories may be slow to respond
   - Check Colab's runtime status

### Getting Help

- **Repository Issues**: Check the [pygetpapers GitHub repository](https://github.com/pygetpapers/pygetpapers)
- **Colab Issues**: See [Google Colab documentation](https://colab.research.google.com/notebooks/basic_features_overview.ipynb)
- **Network Issues**: Try different repositories or check your internet connection

## Advanced Usage

### Batch Processing
Run multiple searches at once:
```python
queries = ["climate change", "global warming", "carbon dioxide"]
apis = ["europe_pmc", "crossref", "biorxiv"]

for api in apis:
    for query in queries:
        !pygetpapers --query "{query}" --api {api} --limit 3 --output /content/batch_output/{api}_{query.replace(' ', '_')}
```

### Data Analysis
Use the CSV files for further analysis:
```python
import pandas as pd

# Load metadata
df = pd.read_csv("/content/pygetpapers_output/europe_pmc_climate/metadata.csv")
print(f"Found {len(df)} papers")
print(df.head())
```

### Custom Datatables
Modify the datatables for your needs:
```python
# Create custom datatables with specific columns
!pygetpapers --query "your query" --datatables /content/custom_output --makecsv
```

## Contributing

If you find issues or want to improve the notebook:

1. **Fork the repository**
2. **Make your changes**
3. **Test in Colab**
4. **Submit a pull request**

## License

This notebook is part of the pygetpapers project and follows the same license terms.

---

**Happy researching! 🌍📚**

*For more information, visit: https://github.com/pygetpapers/pygetpapers* 