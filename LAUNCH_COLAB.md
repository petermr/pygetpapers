# Launch Pygetpapers v2.0 in Google Colab

## Quick Start (3 Steps)

### 1. Open the Notebook
**Option A - Download & Upload (Recommended):**
1. **Download the notebook file:**
   - Go to this repository: https://github.com/pygetpapers/pygetpapers
   - Click on the file `pygetpapers_colab_demo.ipynb` in the file list
   - Click the "Download" button (or right-click → "Save link as...")
2. **Upload to Colab:**
   - Go to [Google Colab](https://colab.research.google.com/)
   - Click "File" → "Upload notebook"
   - Select the downloaded `pygetpapers_colab_demo.ipynb` file

**Option B - Manual Creation:**
1. Go to [Google Colab](https://colab.research.google.com/)
2. Create a new notebook
3. Copy the code from the cells in `pygetpapers_colab_demo.ipynb`

**Option C - GitHub (After Commit):**
```
https://colab.research.google.com/github/pygetpapers/pygetpapers/blob/main/pygetpapers_colab_demo.ipynb
```

### 2. Install Pygetpapers
Run the first code cell to install:
```python
!pip install git+https://github.com/pygetpapers/pygetpapers.git
```

### 3. Run Demos
Execute cells sequentially to see:
- 🌍 Climate change research across repositories
- 📄 PDF downloads from Europe PMC
- 📊 Interactive datatables
- 🔍 No-execute mode (count results)

## What You'll Get

✅ **5 repositories tested** (Europe PMC, Crossref, bioRxiv, medRxiv, OpenAlex)  
✅ **Climate change queries** (following project style guide)  
✅ **CSV metadata files** for analysis  
✅ **HTML datatables** for browsing  
✅ **PDF downloads** where available  

## Output Location
All files saved to: `/content/pygetpapers_output/`

## Customize
Change queries in any cell:
```python
query = "your topic"  # Replace with your research topic
limit = 10           # Number of papers to download
```

## Troubleshooting

**"Notebook not found" error?**
- Use Option A (Download & Upload) instead
- The GitHub link will work after the notebook is committed to the repository

**Can't find the notebook file?**
- Look for `pygetpapers_colab_demo.ipynb` in the main directory of the repository
- If not visible, the file may not be committed yet - use Option B instead

---

**Ready to research? Download the notebook and upload to Colab! 🚀** 