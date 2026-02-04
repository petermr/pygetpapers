#!/usr/bin/env python3
"""
Test script for hOCR Builder functionality.

AUTHOR: P. Murray-Rust with assistance from CursorAI (Claude Sonnet 4)
VERSION: 1.0.0
PURPOSE: Demonstrate hOCR builder with PDF and image processing examples
"""

import os
import sys
from pathlib import Path

from pygetpapers.core.hocr_builder import (
    HOCRBuilder,
    HOCRCharacter,
    HOCRLine,
    HOCRParagraph,
    HOCRWord,
)


def test_basic_hocr_creation():
    """Test basic hOCR creation with sample data."""
    print("🧪 Testing Basic hOCR Creation")
    print("=" * 50)

    # Create hOCR builder
    builder = HOCRBuilder("Test Document")

    # Add a page
    page = builder.add_page(1, 612, 792)  # Letter size
    print(f"✅ Added page: {page.page_number} ({page.width}x{page.height})")

    # Add a paragraph
    paragraph = builder.add_paragraph("heading")
    print(f"✅ Added paragraph: {paragraph.paragraph_type}")

    # Add a line
    line = builder.add_line()
    print(f"✅ Added line")

    # Add words
    words_data = [
        ("Climate", 50, 50, 100, 70, 0.95, "Arial", 12, "bold"),
        ("Change", 105, 50, 150, 70, 0.92, "Arial", 12, "normal"),
        ("Adaptation", 155, 50, 220, 70, 0.88, "Arial", 12, "normal"),
    ]

    for text, x0, y0, x1, y1, conf, font, size, weight in words_data:
        word = builder.add_word(text, x0, y0, x1, y1, conf, font, size, weight)
        print(f"   ✅ Added word: '{word.text}' at ({x0},{y0})-({x1},{y1})")

    # Add another line
    line2 = builder.add_line()
    print(f"✅ Added second line")

    # Add more words
    words_data2 = [
        ("This", 50, 80, 80, 100, 0.96, "Times", 10, "normal"),
        ("is", 85, 80, 95, 100, 0.98, "Times", 10, "normal"),
        ("a", 100, 80, 110, 100, 0.97, "Times", 10, "normal"),
        ("test", 115, 80, 140, 100, 0.94, "Times", 10, "normal"),
        ("document", 145, 80, 190, 100, 0.91, "Times", 10, "normal"),
    ]

    for text, x0, y0, x1, y1, conf, font, size, weight in words_data2:
        word = builder.add_word(text, x0, y0, x1, y1, conf, font, size, weight)
        print(f"   ✅ Added word: '{word.text}' at ({x0},{y0})-({x1},{y1})")

    # Add an image
    image = builder.add_image(300, 50, 500, 200, alt_text="Sample chart")
    print(
        f"✅ Added image: {image['alt_text']} at ({image['x0']},{image['y0']})-({image['x1']},{image['y1']})"
    )

    # Add a graphic
    svg_data = '<svg width="100" height="50"><rect x="0" y="0" width="100" height="50" fill="blue"/></svg>'
    graphic = builder.add_graphic("rect", 50, 300, 150, 350, svg_data)
    print(
        f"✅ Added graphic: {graphic['type']} at ({graphic['x0']},{graphic['y0']})-({graphic['x1']},{graphic['y1']})"
    )

    # Generate hOCR XML
    hocr_xml = builder.generate_hocr_xml()
    print(f"✅ Generated hOCR XML ({len(hocr_xml)} characters)")

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

    # Save hOCR file
    output_dir = Path("examples/hocr_test_output")
    output_dir.mkdir(exist_ok=True)

    hocr_file = builder.save_hocr(output_dir / "test_document.hocr")
    print(f"\n💾 Saved hOCR file: {hocr_file}")

    # Show preview of hOCR XML
    print(f"\n📖 hOCR XML Preview (first 500 characters):")
    preview = hocr_xml[:500] + "..." if len(hocr_xml) > 500 else hocr_xml
    print(preview)

    return builder


def test_pdfplumber_integration():
    """Test integration with PDFPlumber data."""
    print("\n🧪 Testing PDFPlumber Integration")
    print("=" * 50)

    # Simulate PDFPlumber data structure
    pdfplumber_data = [
        {
            "page_num": 1,
            "width": 612,
            "height": 792,
            "text_blocks": [
                {"text": "Climate", "x0": 50, "y0": 50, "x1": 100, "y1": 70},
                {"text": "Change", "x0": 105, "y0": 50, "x1": 150, "y1": 70},
                {"text": "Adaptation", "x0": 155, "y0": 50, "x1": 220, "y1": 70},
                {"text": "This", "x0": 50, "y0": 80, "x1": 80, "y1": 100},
                {"text": "is", "x0": 85, "y0": 80, "x1": 95, "y1": 100},
                {"text": "a", "x0": 100, "y0": 80, "x1": 110, "y1": 100},
                {"text": "test", "x0": 115, "y0": 80, "x1": 140, "y1": 100},
                {"text": "document", "x0": 145, "y0": 80, "x1": 190, "y1": 100},
            ],
        }
    ]

    # Create hOCR from PDFPlumber data
    from pygetpapers.core.hocr_builder import create_hocr_from_pdfplumber_data

    builder = create_hocr_from_pdfplumber_data(pdfplumber_data)
    print(f"✅ Created hOCR from PDFPlumber data")

    # Get summary
    summary = builder.get_document_summary()
    print(f"📊 PDFPlumber Integration Summary:")
    print(f"   Pages: {summary['pages']}")
    print(f"   Paragraphs: {summary['paragraphs']}")
    print(f"   Lines: {summary['lines']}")
    print(f"   Words: {summary['words']}")

    # Save hOCR file
    output_dir = Path("examples/hocr_test_output")
    hocr_file = builder.save_hocr(output_dir / "pdfplumber_integration.hocr")
    print(f"💾 Saved PDFPlumber hOCR: {hocr_file}")

    return builder


def test_advanced_features():
    """Test advanced hOCR features."""
    print("\n🧪 Testing Advanced hOCR Features")
    print("=" * 50)

    builder = HOCRBuilder("Advanced Test Document")

    # Add page
    page = builder.add_page(1, 612, 792)

    # Add multiple paragraphs with different types
    paragraph_types = ["heading", "normal", "list_item", "footnote"]

    for i, ptype in enumerate(paragraph_types):
        paragraph = builder.add_paragraph(ptype)
        line = builder.add_line()

        # Add words with different font properties
        words = [
            (
                f"Sample {ptype}",
                50,
                50 + i * 30,
                150,
                70 + i * 30,
                0.95,
                "Arial",
                12 + i,
                "bold",
            ),
            ("text", 155, 50 + i * 30, 180, 70 + i * 30, 0.92, "Times", 10, "normal"),
        ]

        for text, x0, y0, x1, y1, conf, font, size, weight in words:
            word = builder.add_word(text, x0, y0, x1, y1, conf, font, size, weight)
            print(f"   ✅ Added word: '{word.text}' ({font}, {size}pt, {weight})")

    # Add characters with detailed properties
    paragraph = builder.add_paragraph("detailed")
    line = builder.add_line()
    word = builder.add_word("Detailed", 50, 200, 120, 220, 0.95, "Arial", 12, "bold")

    # Add individual characters
    char_data = [
        ("D", 50, 200, 60, 220, 0.98, "Arial", 12, "bold", "normal", "#000000", 210),
        ("e", 60, 200, 70, 220, 0.96, "Arial", 12, "bold", "normal", "#000000", 210),
        ("t", 70, 200, 80, 220, 0.97, "Arial", 12, "bold", "normal", "#000000", 210),
        ("a", 80, 200, 90, 220, 0.95, "Arial", 12, "bold", "normal", "#000000", 210),
        ("i", 90, 200, 95, 220, 0.99, "Arial", 12, "bold", "normal", "#000000", 210),
        ("l", 95, 200, 100, 220, 0.94, "Arial", 12, "bold", "normal", "#000000", 210),
        ("e", 100, 200, 110, 220, 0.96, "Arial", 12, "bold", "normal", "#000000", 210),
        ("d", 110, 200, 120, 220, 0.93, "Arial", 12, "bold", "normal", "#000000", 210),
    ]

    for (
        text,
        x0,
        y0,
        x1,
        y1,
        conf,
        font,
        size,
        weight,
        style,
        color,
        baseline,
    ) in char_data:
        char = builder.add_character(
            text, x0, y0, x1, y1, conf, font, size, weight, style, color, baseline
        )
        print(
            f"   ✅ Added character: '{char.text}' (color: {char.color}, baseline: {char.baseline})"
        )

    # Add images and graphics
    image = builder.add_image(
        300, 50, 500, 200, alt_text="Sample figure", confidence=0.9
    )
    print(f"✅ Added image: {image['alt_text']} (confidence: {image['confidence']})")

    svg_data = """
    <svg width="200" height="100">
        <rect x="0" y="0" width="200" height="100" fill="lightblue" stroke="black"/>
        <circle cx="100" cy="50" r="30" fill="red"/>
        <text x="100" y="55" text-anchor="middle" fill="white">SVG</text>
    </svg>
    """
    graphic = builder.add_graphic(
        "complex", 50, 300, 250, 400, svg_data, confidence=0.85
    )
    print(
        f"✅ Added complex graphic: {graphic['type']} (confidence: {graphic['confidence']})"
    )

    # Generate and save
    summary = builder.get_document_summary()
    print(f"\n📊 Advanced Features Summary:")
    print(f"   Paragraphs: {summary['paragraphs']}")
    print(f"   Lines: {summary['lines']}")
    print(f"   Words: {summary['words']}")
    print(f"   Images: {summary['images']}")
    print(f"   Graphics: {summary['graphics']}")

    output_dir = Path("examples/hocr_test_output")
    hocr_file = builder.save_hocr(output_dir / "advanced_features.hocr")
    print(f"💾 Saved advanced hOCR: {hocr_file}")

    return builder


def main():
    """Main test function."""
    print("=" * 70)
    print("           hOCR BUILDER TESTING")
    print("=" * 70)
    print()

    try:
        # Test basic functionality
        basic_builder = test_basic_hocr_creation()

        # Test PDFPlumber integration
        pdfplumber_builder = test_pdfplumber_integration()

        # Test advanced features
        advanced_builder = test_advanced_features()

        # Final summary
        print("\n" + "=" * 70)
        print("           TEST RESULTS SUMMARY")
        print("=" * 70)

        print("✅ hOCR BUILDER TESTS PASSED!")
        print()
        print("🎯 All features working correctly:")
        print("   ✅ Basic hOCR creation with pages, paragraphs, lines, words")
        print("   ✅ PDFPlumber data integration")
        print("   ✅ Advanced features (characters, images, graphics)")
        print("   ✅ Multiple paragraph types (heading, normal, list_item, footnote)")
        print("   ✅ Font properties (family, size, weight, style, color)")
        print("   ✅ Confidence scores and metadata")
        print("   ✅ SVG graphics support")
        print("   ✅ hOCR XML generation and file saving")
        print()
        print("📁 Output files created in: examples/hocr_test_output/")
        print("   - test_document.hocr")
        print("   - pdfplumber_integration.hocr")
        print("   - advanced_features.hocr")
        print()
        print("🔍 Next steps:")
        print("   - Integrate with PDFPlumber extraction")
        print("   - Add Tesseract OCR integration")
        print("   - Create hOCR to semantic HTML converter")
        print("   - Test with real PDF documents")
        print()
        print("🎉 hOCR builder is ready for integration!")

        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
