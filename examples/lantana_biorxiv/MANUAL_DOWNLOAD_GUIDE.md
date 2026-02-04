# Manual PDF Download Guide

## Why Manual Downloads?

BioRxiv has implemented strict Cloudflare bot detection that blocks automated requests. However, manual access through a web browser works perfectly.

## How to Manually Download PDFs

### Step 1: Get the Paper List
Run the main analysis script to get the list of papers:
```bash
python -m examples.lantana_biorxiv.lantana_analysis
```

This will create `lantana_results.json` with all the paper information.

### Step 2: Download PDFs Manually

1. **Open your web browser**
2. **Go to BioRxiv**: https://www.biorxiv.org/
3. **Search for "Lantana"** or use the direct DOI links from the results
4. **Download each PDF** by clicking the PDF link on each paper page

### Step 3: Save PDFs with Correct Names

Save the PDFs in the `examples/lantana_biorxiv/pdfs/` directory with these naming conventions:

**Format**: `{DOI}.pdf`
- Replace `/` with `_` in the DOI
- Example: `10.1101_2023.11.10.566554.pdf`

**Current Papers to Download:**
- `10.1101_2023.11.10.566554.pdf` - Environmental fungi from cool and warm neighborhoods...

### Step 4: Update Results

After placing the PDFs in the directory, run:
```bash
python examples/lantana_biorxiv/manual_pdf_adder.py
```

This will:
- ✅ Detect the manually added PDFs
- ✅ Update the results file with PDF information
- ✅ Recalculate statistics
- ✅ Generate an updated report

## Alternative: Use Different Repositories

If BioRxiv continues to block access, consider using other repositories:

### Europe PMC
- ✅ Allows automated downloads
- ✅ Has many Lantana-related papers
- ✅ PDFs are freely available

### OpenAlex
- ✅ Open access focus
- ✅ Good metadata
- ✅ PDF downloads available

### Redalyc
- ✅ Spanish/Portuguese papers
- ✅ May have Lantana research
- ✅ Automated downloads work

## Next Steps

Once PDFs are available (either manually or from other repositories), we can proceed with:

1. **PDF Feature Analysis** - Using PDFPlumber to analyze:
   - Single column layout
   - Headers/footers
   - Lists and tables
   - Math equations and chemical formulae
   - And all other specified features

2. **Generate DataTables** - Create interactive HTML tables
3. **Complete Analysis Report** - Comprehensive feature analysis

## Troubleshooting

### If PDFs are too large (>25MB)
- The script will automatically skip them
- Consider downloading smaller versions if available

### If naming doesn't work
- Check the exact DOI format in `lantana_results.json`
- Ensure the filename matches exactly (with `_` instead of `/`)

### If no papers are found
- Try different search terms
- Use a different repository
- Check if BioRxiv is accessible from your location 