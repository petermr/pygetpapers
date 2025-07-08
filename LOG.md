# Pygetpapers Streamlit UI Development Log

## Latest Updates

### 2024-07-08: Automatic Corpus Detection
- **Added automatic corpus detection**: The app now automatically scans for existing pygetpapers output directories on startup
- **Smart directory recognition**: Detects corpora by looking for characteristic files (eupmc_results.json, europe_pmc.csv, etc.) and paper ID patterns (PMC, arXiv:, etc.)
- **Metadata extraction**: Automatically extracts corpus information including API type, paper count, creation date, and original query
- **Manual refresh**: Added "🔄 Refresh Corpus List" button to manually scan for newly downloaded corpora
- **Session state integration**: Auto-detected corpora are seamlessly integrated into the existing corpus management system
- **Cross-version support**: Feature implemented in both main and no-dependencies Streamlit apps

### 2024-07-08: Progress Display Improvements
- **Complete tqdm filtering**: Completely removed tqdm progress bars from both stdout and stderr output display
- **Clean output display**: Filtered output now shows only meaningful information without redundant progress bars
- **Meaningful activity display**: Enhanced recent activity section to show only meaningful output lines
- **Smart filtering**: Automatically filters out debug messages, timestamps, and other noise
- **Better color coding**: Improved visual feedback with color-coded messages (green for success, red for errors, etc.)
- **Fallback indicators**: Added fallback messages when no meaningful output is available
- **Cross-version support**: Applied filtering to both main and no-dependencies Streamlit apps

### 2024-07-08: Quick Stats Fix
- **Fixed stats updating**: Quick stats now properly update when papers are downloaded
- **Auto-detection stats**: Stats are updated when existing corpora are auto-detected on startup
- **Accurate paper counts**: Corpus entries now use actual downloaded papers instead of requested limit
- **Debug information**: Added debug output to show stats updates for troubleshooting
- **Cross-version support**: Applied fixes to both main and no-dependencies Streamlit apps

### 2024-07-08: Comprehensive HTML Management System & Naming Convention
- **Multi-source HTML support**: Support for HTML from multiple sources with clear naming convention
- **HTML file types**: 
  - `fulltext.raw.html` (provided by publisher/repo)
  - `fulltext.xml.html` (converted from XML using JATS4R or Simple HTML Converter)
  - `fulltext.pdf.html` (converted from PDF)
  - `fulltext.doc.html` (converted from DOC)
  - `html_with_ids.html` (cleaned and enhanced for analysis)
- **JATS4R integration**: XML to HTML conversion with automatic setup and batch processing
- **PDF/DOC conversion**: Multiple converter support (pdfplumber, PyMuPDF, pandoc, etc.)
- **HTML enhancement**: Automatic creation of enhanced HTML with section IDs and cleaned structure
- **CLI commands**:
  - `--fulltext_html`: Convert XML to HTML during download
  - `--convert_html`: Retrospective XML to HTML conversion
  - `--process_html`: Process all HTML files in corpus (convert PDFs/DOCs, create enhanced versions)
  - `--enhance_html`: Create enhanced HTML from existing HTML files
- **Priority system**: Enhanced > XML > Raw > PDF > DOC (best HTML selection)
- **Naming convention**: HTML files are named with their source type (e.g., `fulltext.xml.html` for XML conversions)
- **Data tables integration**: Updated to show all HTML file types and enhanced HTML status
- **Cross-version support**: Full functionality in main app, placeholder in no-dependencies version

### 2024-07-08: Download Safety Measures
- **Enhanced validation**: Added comprehensive validation to compare requested vs actual papers downloaded
- **Safety limits**: Implemented hard limits (max 200 papers) and warnings (above 100 papers) in the UI
- **Debug output**: Added detailed command execution logging for troubleshooting
- **Error handling**: Improved error messages and warnings for limit violations
- **Cross-version support**: All safety measures implemented in both Streamlit app versions

### 2024-07-08: Progress Tracking Enhancement
- **Real-time progress**: Implemented live progress tracking with subprocess output capture
- **Dynamic progress bar**: Beautiful gradient progress bar with animated emojis and color transitions
- **File type counters**: Real-time counters for JSON, XML, PDF, and supplementary files
- **Operation indicators**: Dynamic operation emojis (🔍 Searching, 📥 Downloading, 💾 Writing)
- **Recent activity display**: Color-coded recent output with styled containers
- **Cross-version support**: Progress tracking implemented in both main and no-dependencies apps

### 2024-07-08: Repository Naming and Paper Count Improvements
- **Repository naming**: Now uses directory names as default repository names for better identification
- **Paper count distinction**: Clear distinction between downloaded papers and total available papers in repository
- **Download progress tracking**: Shows download percentage (e.g., "50 / 100 papers" with 50% progress)
- **Enhanced statistics**: Separate metrics for downloaded vs total available papers
- **Multiple instance management**: Improved run script to handle port conflicts and manage multiple Streamlit instances
- **Cross-version support**: All improvements implemented in both main and no-dependencies versions

### 2024-07-07: Streamlit UI Development
- **Initial implementation**: Created comprehensive Streamlit web interface for pygetpapers
- **Repository support**: Full support for Europe PMC, arXiv, Crossref, OpenAlex, bioRxiv, medRxiv, Rxivist
- **Query builder**: Advanced query builder with Boolean operators and field-specific search
- **Corpus management**: Complete corpus management with statistics and visualization
- **Data tables**: Interactive HTML tables with datatables integration
- **Figures gallery**: Automatic figure extraction and thumbnail generation
- **Fulltext search**: Advanced search within paper content
- **Corpus comparison**: Multi-corpus comparison and overlap analysis
- **Export functionality**: CSV export and data visualization
- **Settings and help**: Comprehensive settings and help documentation

### 2024-07-07: CI/CD and Import Fixes
- **Fixed import errors**: Resolved subprocess path issues and sys.path hacks
- **CI configuration**: Added pytest-cov installation and proper test configuration
- **Test fixes**: Fixed Arxiv API usage and zip file handling tests
- **Formatting**: Applied Black formatting to test files
- **Streamlit CI**: Added syntax checking without server startup to prevent hanging
- **CLI availability**: Fixed CLI command availability in CI environment

## Technical Details

### Progress Tracking Implementation
- Uses `subprocess.Popen` with real-time output capture
- Parses progress information from pygetpapers output
- Updates Streamlit components with `placeholder.empty()` for smooth animations
- Handles both tqdm progress bars and custom output parsing
- Implements graceful error handling and timeout management

### Corpus Detection Algorithm
- Scans current directory for pygetpapers output patterns
- Identifies characteristic files (eupmc_results.json, europe_pmc.csv, etc.)
- Recognizes paper ID patterns (PMC, arXiv:, doi_)
- Extracts metadata from JSON files when available
- Parses timestamps from directory names for creation dates
- Integrates seamlessly with existing session state management

### Safety Measures
- Validates actual vs requested paper counts
- Implements UI limits (100 warning, 200 hard stop)
- Provides detailed debug output for troubleshooting
- Shows clear error messages for limit violations
- Maintains user control while preventing accidental large downloads

## Migration Guide

### For Existing Users
1. **Automatic Detection**: Existing corpora will be automatically detected on next app startup
2. **Manual Refresh**: Use "🔄 Refresh Corpus List" button to detect new downloads
3. **Progress Tracking**: New downloads will show enhanced progress display
4. **Safety Limits**: Be aware of new download limits (max 200 papers)

### For New Users
1. **Installation**: Follow standard pygetpapers installation
2. **Streamlit Setup**: Install Streamlit and run `streamlit run streamlit_app.py`
3. **First Use**: Download papers through the web interface
4. **Corpus Management**: Use the Corpus Manager to view and analyze downloads

## Future Enhancements

### Planned Features
- **Batch operations**: Select multiple papers for bulk operations
- **Advanced filtering**: Filter papers by date, journal, author, etc.
- **Citation export**: Export citations in various formats (BibTeX, EndNote, etc.)
- **Collaborative features**: Share corpora and queries with other users
- **Advanced analytics**: More sophisticated corpus analysis and visualization
- **API integration**: Direct integration with external analysis tools

### Technical Improvements
- **Performance optimization**: Faster corpus scanning and data loading
- **Memory management**: Better handling of large corpora
- **Caching**: Implement intelligent caching for frequently accessed data
- **Offline mode**: Support for offline corpus analysis
- **Mobile optimization**: Better mobile device support

## Team Feedback - [Date]

### Issues to Address:

1. **Documentation Issues:**
   - ❌ Remove `# noqa` comments from instructions - team doesn't understand them
   - ❌ Need clear migration guide from CLI to Streamlit

2. **UI/UX Improvements:**
   - ❌ Highlight the query box for better visibility
   - ❌ Reduce default paper downloading from current limit to 10
   - ❌ Create version without external dependencies (no plotly requirement)
   - ❌ Add visual progress indicators for downloads

3. **Functionality Issues:**
   - ❌ Plot doesn't show numbers of papers and years
   - ❌ Datatables show journal name as "Unknown" 
   - ❌ Figures facility needs significant work (deferred)
   - ❌ Clarify where corpus is created/stored

4. **Future Enhancements:**
   - ❌ Add filters based on metadata (journal name, authors)
   - ❌ Add filters based on fulltext content

## Implementation Status:

### Completed ✅
- Fixed Arxiv API bug (`Search.get()` → `list(Search.results())`)
- Fixed zip test to be realistic
- Fixed Streamlit blocking in CI
- Fixed CLI availability with `pip install -e .`
- Fixed Black formatting issues
- All 23 tests passing with 64% coverage
- CI/CD pipeline working
- ✅ Reduced default limit to 10 papers
- ✅ Highlighted query box with prominent styling
- ✅ Created migration guide (MIGRATION_GUIDE.md)
- ✅ Created no-dependencies version (streamlit_app_no_deps.py)
- ✅ Added real-time progress tracking for downloads

### In Progress 🔄
- Fixing journal name display issue
- Investigating plot functionality

### Pending ⏳
- Remove `# noqa` comments from instructions
- Fix plot to show numbers of papers and years
- Fix journal name display in datatables
- Document corpus location clearly
- Plan filter implementation
- Figures facility improvements (deferred)

## Technical Notes:
- Current default limit: ✅ Reduced to 10 papers
- Plotly dependency: ✅ Created no-deps version without plotly
- Corpus location: ✅ Files saved to `{repo_name}_{timestamp}` in current directory (e.g., `europe_pmc_20250121_143022`)
- Journal name issue: ✅ Fixed - was looking for `journalTitle` but should look for `journalInfo.journal.title`
- Query box: ✅ Highlighted with prominent styling and help text
- Progress tracking: ✅ Real-time progress indicators showing:
  - Current operation (Searching, Downloading, Writing)
  - Overall progress bar with paper count
  - File type counters (JSON, XML, PDF, Supplementary)
  - Recent output lines
  - Works in both main and no-dependencies versions

## Next Steps:
1. Remove `# noqa` comments
2. Create migration guide
3. Highlight query box
4. Reduce default limit to 10
5. Create no-dependencies version
6. Add progress tracking for downloads
7. Fix plot functionality
8. Fix journal name display
9. Document corpus location
10. Plan filter implementation 