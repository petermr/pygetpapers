# hOCR Builder Implementation

## Overview

The hOCR Builder provides a unified approach for both PDF and image-to-text conversion using hOCR as the intermediate format. This creates a clean architecture that can later be transformed into semantic HTML with sections, lists, footnotes, etc.

## Architecture

### Design Philosophy

The proposed architecture follows a clean, maintainable design:

```
PDF Processing:
PDFPlumber → Heuristic Logic → SVG → hOCR Builder → hOCR Output

Image Processing:
Tesseract → hOCR Output → hOCR Builder → Enhanced hOCR

Unified Output:
hOCR → Semantic HTML (sections, lists, footnotes, etc.)
```

### Key Components

1. **PDFPlumber Integration**: Extracts primitives (characters, lines, curves, bitmaps)
2. **Heuristic Logic**: Builds complex objects (sentences, paragraphs, graphics)
3. **SVG Representation**: Final geometric representation
4. **hOCR Builder**: Creates standardized hOCR output
5. **Semantic HTML Converter**: Transforms hOCR to structured HTML

## Implementation

### Core hOCR Builder

The `HOCRBuilder` class in `pygetpapers/core/hocr_builder.py` provides:

- **Data Classes**: `HOCRCharacter`, `HOCRWord`, `HOCRLine`, `HOCRParagraph`, `HOCRPage`, `HOCRDocument`
- **Builder Pattern**: Fluent API for constructing hOCR documents
- **lxml Integration**: Proper XML construction (no lexical string building)
- **Export Functions**: Generate hOCR XML and save to files

### Key Features

#### 1. Proper XML Construction
- Uses `lxml.etree.ElementTree` for all XML generation
- No lexical string concatenation or f-string XML construction
- Follows style guide: "Never construct HTML or XML lexically"

#### 2. Comprehensive Data Model
```python
@dataclass
class HOCRWord:
    text: str
    x0: float
    y0: float
    x1: float
    y1: float
    confidence: float = 1.0
    font_family: Optional[str] = None
    font_size: Optional[float] = None
    font_weight: Optional[str] = None
    font_style: Optional[str] = None
    color: Optional[str] = None
    baseline: Optional[float] = None
```

#### 3. Builder API
```python
builder = HOCRBuilder("Document Title")
page = builder.add_page(1, 612, 792)
paragraph = builder.add_paragraph("heading")
line = builder.add_line()
word = builder.add_word("Climate", 50, 50, 100, 70, 0.95, "Arial", 12, "bold")
```

#### 4. Integration Functions
- `create_hocr_from_pdfplumber_data()`: Convert PDFPlumber output to hOCR
- `create_hocr_from_tesseract_data()`: Convert Tesseract output to hOCR

## Usage Examples

### Basic hOCR Creation
```python
from pygetpapers.core.hocr_builder import HOCRBuilder

builder = HOCRBuilder("Test Document")
page = builder.add_page(1, 612, 792)
paragraph = builder.add_paragraph("heading")
line = builder.add_line()
word = builder.add_word("Climate Change", 50, 50, 150, 70)

hocr_xml = builder.generate_hocr_xml()
builder.save_hocr("output.hocr")
```

### PDFPlumber Integration
```python
from pygetpapers.core.hocr_builder import create_hocr_from_pdfplumber_data

# PDFPlumber data structure
pdfplumber_data = [
    {
        'page_num': 1,
        'width': 612,
        'height': 792,
        'text_blocks': [
            {'text': 'Climate', 'x0': 50, 'y0': 50, 'x1': 100, 'y1': 70},
            {'text': 'Change', 'x0': 105, 'y0': 50, 'x1': 150, 'y1': 70},
        ]
    }
]

builder = create_hocr_from_pdfplumber_data(pdfplumber_data)
builder.save_hocr("pdf_output.hocr")
```

## Testing

### Test Files
- `examples/test_hocr_builder.py`: Comprehensive functionality tests
- `examples/test_hocr_lxml.py`: lxml integration verification

### Test Coverage
- Basic hOCR creation with pages, paragraphs, lines, words
- PDFPlumber data integration
- Advanced features (characters, images, graphics)
- Multiple paragraph types (heading, normal, list_item, footnote)
- Font properties (family, size, weight, style, color)
- Confidence scores and metadata
- SVG graphics support
- lxml XML generation (no lexical construction)

## Style Guide Compliance

### ✅ Follows Style Guide Rules
1. **No lexical XML construction**: Uses `lxml.etree.ElementTree`
2. **PDF parsing with PDFPlumber**: Leverages existing PDFPlumber integration
3. **XML parsing with lxml**: Proper XML handling
4. **Climate change examples**: Uses climate change content for testing
5. **Proper file naming**: Alphanumeric and underscores only

### ❌ Avoided Anti-patterns
- No string concatenation for XML/HTML
- No f-string XML construction
- No manual XML escaping
- No lexical HTML building

## Future Development

### Next Steps
1. **PDFPlumber Integration**: Connect with existing PDF processing pipeline
2. **Tesseract Integration**: Add image-to-text conversion support
3. **Semantic HTML Converter**: Create hOCR to structured HTML transformation
4. **Real PDF Testing**: Test with actual PDF documents
5. **Performance Optimization**: Optimize for large documents

### Semantic HTML Features
- Section detection and hierarchy
- List identification and formatting
- Footnote extraction and linking
- Table structure preservation
- Figure and caption handling
- Reference section formatting

## Files

### Core Implementation
- `pygetpapers/core/hocr_builder.py`: Main hOCR builder implementation

### Examples and Tests
- `examples/test_hocr_builder.py`: Comprehensive test suite
- `examples/test_hocr_lxml.py`: lxml integration test
- `examples/hocr_test_output/`: Generated test files

### Documentation
- `docs/hocr-builder-implementation.md`: This documentation

## Author

**AUTHOR**: P. Murray-Rust with assistance from CursorAI (Claude Sonnet 4)  
**VERSION**: 1.0.0  
**PURPOSE**: Create unified hOCR output format for PDF and image processing

---

*This implementation provides a solid foundation for unified PDF and image processing through hOCR, following clean design principles and style guide compliance.* 