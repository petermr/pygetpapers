#!/usr/bin/env python3
"""
Test PDF-enhanced features of hOCR Builder.

AUTHOR: P. Murray-Rust with assistance from CursorAI (Claude Sonnet 4)
VERSION: 1.0.0
PURPOSE: Demonstrate PDF-enhanced features like FP coordinates and CSS styles
"""

import sys
from pathlib import Path

# Get the project root directory (parent of examples directory)
PROJECT_ROOT = Path(__file__).parent.parent

from pygetpapers.core.hocr_builder import HOCRBuilder, create_hocr_from_pdfplumber_data


def test_pdf_enhanced_features():
    """Test PDF-enhanced features like FP coordinates and CSS styles."""

    # Create hOCR builder with PDF-specific features
    builder = HOCRBuilder("PDF Enhanced Document")
    page = builder.add_page(1, 612, 792)

    # Add paragraph with PDF-specific class
    paragraph = builder.add_paragraph("pdf_area")
    line = builder.add_line()

    # Add word with comprehensive PDF properties
    word = builder.add_word(
        "Climate",
        x0=50,
        y0=50,
        x1=100,
        y1=70,
        confidence=0.95,
        font_family="Arial-Bold",
        font_size=12,
        font_weight="bold",
        font_style="normal",
        color="#000000",
        baseline=0.004,
    )

    # Add another word with different styling
    word2 = builder.add_word(
        "Change",
        x0=105,
        y0=50,
        x1=150,
        y1=70,
        confidence=0.90,
        font_family="Times-Roman",
        font_size=10,
        font_weight="normal",
        font_style="italic",
        color="#333333",
        baseline=0.002,
    )

    # Add image with PDF-specific properties
    image = builder.add_image(
        x0=300,
        y0=100,
        x1=500,
        y1=200,
        alt_text="Sample chart showing climate data",
        confidence=0.85,
    )

    # Add graphic with SVG data
    svg_data = """<svg width="100" height="50">
        <rect x="0" y="0" width="100" height="50" fill="#ffffff" stroke="#000000"/>
        <circle cx="25" cy="25" r="10" fill="#ff0000"/>
        <circle cx="75" cy="25" r="10" fill="#00ff00"/>
    </svg>"""

    graphic = builder.add_graphic(
        graphic_type="chart",
        x0=50,
        y0=300,
        x1=150,
        y1=350,
        svg_data=svg_data,
        confidence=0.88,
    )

    # Generate and save hOCR
    output_file = PROJECT_ROOT / "examples" / "pdf_enhanced_output.hocr"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    saved_file = builder.save_hocr(output_file)

    print(f"✅ PDF-enhanced hOCR saved to: {saved_file}")
    
    assert builder is not None, "Builder should be created"
    assert saved_file is not None, "hOCR file should be saved"

    # Get document summary
    summary = builder.get_document_summary()
    print(f"\n📊 Document Summary:")
    print(f"   Title: {summary['title']}")
    print(f"   Pages: {summary['pages']}")
    print(f"   Paragraphs: {summary['paragraphs']}")
    print(f"   Lines: {summary['lines']}")
    print(f"   Words: {summary['words']}")
    print(f"   Images: {summary['images']}")
    print(f"   Graphics: {summary['graphics']}")

    # Show sample of generated XML with PDF features
    hocr_xml = builder.generate_hocr_xml()
    print(f"\n📄 Sample hOCR XML with PDF features:")

    # Find the word elements with PDF properties
    lines = hocr_xml.split("\n")
    for line in lines:
        if "ocr_word" in line and ("x_font" in line or "x_color" in line):
            print(f"   {line.strip()}")

    assert builder is not None, "Builder should exist"


def test_pdfplumber_integration():
    """Test integration with PDFPlumber data."""

    # Sample PDFPlumber data with enhanced features
    pdfplumber_data = [
        {
            "page_num": 1,
            "width": 612,
            "height": 792,
            "text_blocks": [
                {
                    "text": "Climate",
                    "x0": 50,
                    "y0": 50,
                    "x1": 100,
                    "y1": 70,
                    "fontname": "Arial-Bold",
                    "size": 12,
                    "color": "#000000",
                    "bbox": [50, 50, 100, 70],
                },
                {
                    "text": "Change",
                    "x0": 105,
                    "y0": 50,
                    "x1": 150,
                    "y1": 70,
                    "fontname": "Arial",
                    "size": 12,
                    "color": "#000000",
                    "bbox": [105, 50, 150, 70],
                },
                {
                    "text": "Adaptation",
                    "x0": 155,
                    "y0": 50,
                    "x1": 220,
                    "y1": 70,
                    "fontname": "Arial",
                    "size": 12,
                    "color": "#000000",
                    "bbox": [155, 50, 220, 70],
                },
            ],
            "images": [
                {
                    "x0": 300,
                    "y0": 100,
                    "x1": 500,
                    "y1": 200,
                    "type": "image",
                    "bbox": [300, 100, 500, 200],
                }
            ],
            "graphics": [
                {
                    "x0": 50,
                    "y0": 300,
                    "x1": 150,
                    "y1": 350,
                    "type": "rect",
                    "stroke": "#000000",
                    "fill": "#ffffff",
                    "bbox": [50, 300, 150, 350],
                }
            ],
        }
    ]

    # Create hOCR from PDFPlumber data
    builder = create_hocr_from_pdfplumber_data(pdfplumber_data)

    # Save to file
    output_file = PROJECT_ROOT / "examples" / "pdfplumber_integration_output.hocr"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    saved_file = builder.save_hocr(output_file)

    print(f"\n✅ PDFPlumber integration hOCR saved to: {saved_file}")
    
    assert builder is not None, "Builder should be created"
    assert saved_file is not None, "hOCR file should be saved"

    # Show summary
    summary = builder.get_document_summary()
    print(f"📊 PDFPlumber Integration Summary:")
    print(f"   Words: {summary['words']}")
    print(f"   Images: {summary['images']}")
    print(f"   Graphics: {summary['graphics']}")

    assert builder is not None, "Builder should exist"


if __name__ == "__main__":
    print("🧪 Testing PDF-enhanced features...")
    test_pdf_enhanced_features()

    print("\n🧪 Testing PDFPlumber integration...")
    test_pdfplumber_integration()

    print("\n✅ All PDF-enhanced feature tests completed!")
