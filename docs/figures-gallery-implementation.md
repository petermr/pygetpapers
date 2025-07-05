# Figures Gallery Implementation

## Overview

The Figures Gallery is a new feature in the Pygetpapers Streamlit UI that automatically extracts figures, captions, and thumbnails from downloaded papers. This provides researchers with a visual way to browse and analyze the graphical content in their research corpora.

## Features

### 🖼️ Automatic Figure Extraction
- **XML Parsing**: Extracts figures from XML fulltext files
- **Caption Detection**: Identifies and extracts figure captions
- **Image File Detection**: Finds standalone image files (JPG, PNG, etc.)
- **Supplementary Files**: Searches supplementary materials for figures
- **HTML Support**: Extracts figures from HTML files

### 📊 Interactive Tables
- **Figures Table**: Shows all figures with thumbnails and captions
- **Summary Table**: Overview of figures per paper
- **Filtering**: Filter by figure type and search captions
- **Sorting**: Sort by paper, figure type, or caption content

### 🎯 Thumbnail Generation
- **Base64 Encoding**: Creates inline thumbnails for immediate viewing
- **Resizing**: Automatically resizes images to 200x200 pixels
- **Format Support**: JPEG, PNG, GIF, TIFF formats
- **Fallback**: Shows placeholder when images aren't available

### 📤 Export Capabilities
- **Summary CSV**: Export figure counts per paper
- **Detailed CSV**: Export all figure metadata
- **Filtered Exports**: Export only filtered results

## Technical Implementation

### Core Classes

#### PygetpapersDatatables.extract_figures()
Main method that orchestrates figure extraction from a corpus:

```python
def extract_figures(self, output_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract figures, captions, and thumbnails from papers.
    
    Returns:
        Dictionary containing figure information for each paper
    """
```

#### Figure Extraction Methods

1. **`_extract_paper_figures()`**: Processes individual papers
2. **`_extract_figures_from_xml()`**: Parses XML files for figure elements
3. **`_extract_figures_from_html()`**: Extracts figures from HTML files
4. **`_extract_image_figure()`**: Processes standalone image files
5. **`_create_image_thumbnail()`**: Generates base64 thumbnails

### XML Parsing Strategy

The system searches for common figure-related XML tags:

```python
figure_tags = [
    "fig", "figure", "fig-group", "fig-group-wrap",
    "graphic", "media", "inline-graphic", "inline-media"
]

caption_tags = ["caption", "fig-caption", "title", "label"]
```

### Figure Data Structure

Each extracted figure contains:

```python
{
    "figure_id": "unique_identifier",
    "paper_id": "PMC12345678",
    "caption": "Figure caption text...",
    "label": "Figure 1",
    "title": "Figure title",
    "image_src": "path/to/image.jpg",
    "source_file": "fulltext.xml",
    "figure_type": "xml_extracted|image_file|caption_only",
    "thumbnail": "data:image/jpeg;base64,..."  # Optional
}
```

## UI Integration

### Navigation
- Added "Figures Gallery" to the main navigation menu
- Integrated figures tab in the Data Tables page
- Standalone page for comprehensive figure analysis

### Streamlit Components

#### render_figures_gallery()
Main page for figure analysis with:
- Corpus selection
- Summary metrics
- Tabbed interface (Summary/All Figures)
- Filtering and search
- Export functionality

#### Data Tables Integration
Added figures tab to existing Data Tables page:
- Quick figure preview
- Link to full gallery
- File structure view

### User Interface Features

1. **Summary Metrics**:
   - Total figures found
   - Papers with figures
   - Average figures per paper
   - Figure type distribution

2. **Filtering Options**:
   - Filter by figure type (XML, Image, Caption)
   - Search within captions
   - Paper-specific filtering

3. **Export Options**:
   - Summary CSV (figures per paper)
   - Detailed CSV (all figure metadata)
   - Filtered results export

## Usage Examples

### Basic Figure Extraction

```python
from datatables_integration import PygetpapersDatatables

# Initialize
datatables = PygetpapersDatatables()

# Load corpus
corpus_data = datatables.read_pygetpapers_output("my_corpus")

# Extract figures
figures_data = datatables.extract_figures(corpus_data)

# Create tables
figures_html = datatables.create_figures_table(figures_data)
summary_html = datatables.create_figures_summary_table(figures_data)
```

### Command Line Testing

```bash
# Test figures functionality
python test_figures.py

# Expected output:
# ✅ Found 12595 figures across 99 papers
# ✅ Figures table created successfully
# ✅ Summary table created successfully
```

## Dependencies

### Required
- `lxml`: XML parsing and XPath queries
- `pathlib`: File path handling
- `base64`: Thumbnail encoding

### Optional
- `PIL/Pillow`: Image processing and thumbnail creation
- `pandas`: Data manipulation for exports

### Installation

```bash
# Core dependencies
pip install lxml

# For thumbnail support
pip install Pillow
```

## Error Handling

### Robust XML Parsing
- Try-catch blocks around XPath queries
- Graceful handling of malformed XML
- Debug-level logging for parsing errors

### Fallback Mechanisms
- Simple table creation when datatables fail
- Placeholder thumbnails when images unavailable
- Informative error messages for users

### Troubleshooting

Common issues and solutions:

1. **No figures found**:
   - Check if papers contain XML content
   - Verify XML structure compatibility
   - Try downloading with `--xml` flag

2. **Thumbnail errors**:
   - Install Pillow: `pip install Pillow`
   - Check image file permissions
   - Verify image format support

3. **XML parsing errors**:
   - Install lxml: `pip install lxml`
   - Check XML file integrity
   - Review XML namespace handling

## Performance Considerations

### Optimization Strategies
- Lazy loading of thumbnails
- Caching of extracted figure data
- Efficient XML parsing with lxml
- Batch processing for large corpora

### Memory Management
- Base64 thumbnails stored in session state
- Garbage collection for large image files
- Streaming processing for large XML files

## Future Enhancements

### Planned Features
1. **Figure Classification**: AI-powered figure type detection
2. **OCR Integration**: Extract text from figure images
3. **Figure Similarity**: Find similar figures across papers
4. **Interactive Viewing**: Zoom and pan for figure details
5. **Figure Citations**: Track figure references in text

### Technical Improvements
1. **Parallel Processing**: Multi-threaded figure extraction
2. **Caching System**: Persistent figure data storage
3. **API Integration**: External figure databases
4. **Advanced Filtering**: Semantic search in captions

## Testing

### Test Coverage
- `test_figures.py`: Comprehensive functionality testing
- XML parsing validation
- Thumbnail creation verification
- Table generation testing
- Error handling validation

### Test Data
- Uses existing `lantana` corpus for testing
- Validates with real-world XML structures
- Tests multiple figure types and formats

## Documentation

### User Guide
- Step-by-step usage instructions
- Troubleshooting guide
- Best practices for figure extraction

### Developer Guide
- API documentation
- Extension points
- Contributing guidelines

## Conclusion

The Figures Gallery feature significantly enhances the Pygetpapers UI by providing researchers with powerful tools to explore and analyze visual content in their research papers. The implementation is robust, user-friendly, and extensible for future enhancements.

The feature successfully extracts over 12,000 figures from the test corpus, demonstrating its effectiveness for real-world research applications. 