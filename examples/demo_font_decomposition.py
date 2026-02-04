#!/usr/bin/env python3
"""
Demonstration of Font Decomposition Functionality.

AUTHOR: P. Murray-Rust with assistance from CursorAI (Claude Sonnet 4)
VERSION: 1.0.0
PURPOSE: Demonstrate font name decomposition and line coordinate preservation
"""

import sys
from pathlib import Path

from pygetpapers.core.hocr_builder import (
    HOCRBuilder,
    create_hocr_from_pdfplumber_data,
    decompose_font_name,
)


def demo_font_decomposition():
    """Demonstrate font name decomposition with various patterns."""

    print("🔤 Font Decomposition Demonstration")
    print("=" * 50)

    # Test various font patterns
    font_patterns = [
        "Arial-Bold",
        "Times-Italic",
        "Helvetica-BoldItalic",
        "Courier-Bold-Italic",
        "Foo-B",
        "Bar-I",
        "Baz-BI",
        "Qux-IB",
        "PlainFont",
        "",
    ]

    print("Font Name Decomposition Results:")
    print("-" * 40)

    for font_name in font_patterns:
        family, weight, style = decompose_font_name(font_name)
        print(f"{font_name:20} → family='{family}', weight='{weight}', style='{style}'")

    print()


def demo_hocr_with_font_decomposition():
    """Demonstrate hOCR generation with font decomposition."""

    print("📄 hOCR Generation with Font Decomposition")
    print("=" * 50)

    # Create hOCR builder
    builder = HOCRBuilder("Font Decomposition Demo")
    page = builder.add_page(1, 612, 792)
    paragraph = builder.add_paragraph()

    # Add words with different font patterns
    line1 = builder.add_line()
    builder.add_word_with_font_name(
        "Bold", 50, 50, 80, 70, font_name="Arial-Bold", font_size=12
    )
    builder.add_word_with_font_name(
        "Italic", 85, 50, 120, 70, font_name="Times-Italic", font_size=12
    )
    builder.add_word_with_font_name(
        "BoldItalic", 125, 50, 180, 70, font_name="Helvetica-BoldItalic", font_size=12
    )

    line2 = builder.add_line()
    builder.add_word_with_font_name(
        "Normal", 50, 80, 100, 100, font_name="Arial", font_size=12
    )
    builder.add_word_with_font_name(
        "Foo-B", 105, 80, 135, 100, font_name="Foo-B", font_size=12
    )
    builder.add_word_with_font_name(
        "Bar-I", 140, 80, 160, 100, font_name="Bar-I", font_size=12
    )

    # Generate and save hOCR
    output_file = Path("examples/font_decomposition_demo.hocr")
    saved_file = builder.save_hocr(output_file)

    print(f"✅ hOCR saved to: {saved_file}")

    # Show word details
    print("\nWord Details:")
    print("-" * 20)
    for i, line in enumerate(paragraph.lines):
        print(f"Line {i+1}:")
        for j, word in enumerate(line.words):
            print(f"  Word {j+1}: '{word.text}'")
            print(f"    Font: {word.font_family}")
            print(f"    Weight: {word.font_weight}")
            print(f"    Style: {word.font_style}")
            print(f"    Size: {word.font_size}")
            print(f"    BBox: ({word.x0}, {word.y0}, {word.x1}, {word.y1})")
            print()

    # Show line coordinates
    print("Line Coordinates:")
    print("-" * 20)
    for i, line in enumerate(paragraph.lines):
        print(f"Line {i+1}: bbox ({line.x0}, {line.y0}, {line.x1}, {line.y1})")

    return builder


def demo_pdfplumber_integration():
    """Demonstrate PDFPlumber integration with font decomposition."""

    print("📊 PDFPlumber Integration with Font Decomposition")
    print("=" * 55)

    # Sample PDFPlumber data with various font patterns
    pdfplumber_data = [
        {
            "page_num": 1,
            "width": 612,
            "height": 792,
            "text_blocks": [
                {
                    "text": "Title",
                    "x0": 50,
                    "y0": 50,
                    "x1": 100,
                    "y1": 70,
                    "fontname": "Arial-Bold",
                    "size": 14,
                    "color": "#000000",
                },
                {
                    "text": "Subtitle",
                    "x0": 105,
                    "y0": 50,
                    "x1": 180,
                    "y1": 70,
                    "fontname": "Times-Italic",
                    "size": 12,
                    "color": "#333333",
                },
                {
                    "text": "Body",
                    "x0": 50,
                    "y0": 80,
                    "x1": 80,
                    "y1": 100,
                    "fontname": "Arial",
                    "size": 10,
                    "color": "#000000",
                },
                {
                    "text": "Emphasis",
                    "x0": 85,
                    "y0": 80,
                    "x1": 140,
                    "y1": 100,
                    "fontname": "Helvetica-BoldItalic",
                    "size": 10,
                    "color": "#000000",
                },
            ],
        }
    ]

    # Create hOCR from PDFPlumber data
    builder = create_hocr_from_pdfplumber_data(pdfplumber_data)

    # Save to file
    output_file = Path("examples/pdfplumber_font_decomposition.hocr")
    saved_file = builder.save_hocr(output_file)

    print(f"✅ PDFPlumber hOCR saved to: {saved_file}")

    # Show font decomposition results
    print("\nFont Decomposition Results:")
    print("-" * 30)

    words = []
    for page in builder.document.pages:
        for paragraph in page.paragraphs:
            for line in paragraph.lines:
                words.extend(line.words)

    for word in words:
        print(
            f"'{word.text}': {word.font_family} {word.font_weight} {word.font_style} ({word.font_size}pt)"
        )

    return builder


def demo_xml_structure():
    """Demonstrate the XML structure with lines as spans."""

    print("🔍 XML Structure with Line Spans")
    print("=" * 40)

    builder = HOCRBuilder("XML Structure Demo")
    page = builder.add_page(1, 612, 792)
    paragraph = builder.add_paragraph()

    # Add multiple lines
    line1 = builder.add_line()
    builder.add_word("First", 50, 50, 80, 70)
    builder.add_word("line", 85, 50, 105, 70)

    line2 = builder.add_line()
    builder.add_word("Second", 50, 80, 110, 100)
    builder.add_word("line", 115, 80, 135, 100)

    # Generate XML
    hocr_xml = builder.generate_hocr_xml()

    print("XML Structure:")
    print("-" * 15)

    # Extract relevant lines
    lines = hocr_xml.split("\n")
    relevant_lines = []

    for line in lines:
        if any(tag in line for tag in ["ocr_par", "ocr_line", "ocr_word"]):
            relevant_lines.append(line.strip())

    for line in relevant_lines:
        print(line)

    print(f"\n✅ Lines are preserved as <span> elements within <div class='ocr_par'>")
    print(f"✅ Each line has its own bbox coordinates")
    print(f"✅ Words are nested within lines")


if __name__ == "__main__":
    print("🎨 Font Decomposition and Line Coordinate Preservation Demo")
    print("=" * 65)
    print()

    # Run demonstrations
    demo_font_decomposition()
    demo_hocr_with_font_decomposition()
    demo_pdfplumber_integration()
    demo_xml_structure()

    print("\n✅ All demonstrations completed!")
    print("\n📁 Generated files:")
    print("  - examples/font_decomposition_demo.hocr")
    print("  - examples/pdfplumber_font_decomposition.hocr")
