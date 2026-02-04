#!/usr/bin/env python3
"""
Test hOCR Builder with real Tesseract output.

AUTHOR: P. Murray-Rust with assistance from CursorAI (Claude Sonnet 4)
VERSION: 1.0.0
PURPOSE: Demonstrate hOCR builder with real Tesseract output
"""

import sys
from pathlib import Path

from pygetpapers.core.hocr_builder import HOCRBuilder


def test_real_tesseract_output():
    """Test hOCR builder with real Tesseract output data."""

    # Create hOCR builder
    builder = HOCRBuilder("Redalyc Search Results")

    # Add page based on the real Tesseract output dimensions
    page = builder.add_page(1, 3456, 1778)

    # Add content areas based on the real Tesseract output
    # Search filters area
    paragraph1 = builder.add_paragraph("carea")
    line1 = builder.add_line()
    builder.add_word("Filtros", 82, 534, 164, 559, 0.92)
    builder.add_word("de", 173, 534, 204, 559, 0.93)
    builder.add_word("bisqueda", 214, 534, 344, 565, 0.52)

    # Year filter area
    paragraph2 = builder.add_paragraph("carea")
    line2 = builder.add_line()
    builder.add_word("Año:", 303, 628, 352, 649, 0.37)

    line3 = builder.add_line()
    builder.add_word("@", 157, 665, 179, 687, 0.26)
    builder.add_word("2025", 189, 671, 244, 690, 0.92)

    line4 = builder.add_line()
    builder.add_word("@", 157, 704, 179, 726, 0.23)
    builder.add_word("2024", 189, 710, 245, 729, 0.90)

    # Language filter area
    paragraph3 = builder.add_paragraph("carea")
    line5 = builder.add_line()
    builder.add_word("Idioma:", 289, 956, 368, 977, 0.96)

    line6 = builder.add_line()
    builder.add_word("@", 157, 993, 179, 1015, 0.70)
    builder.add_word("Español", 189, 998, 272, 1023, 0.54)

    # Search term
    paragraph4 = builder.add_paragraph("carea")
    line7 = builder.add_line()
    builder.add_word("Lantana", 699, 553, 787, 572, 0.96)

    # Title
    paragraph5 = builder.add_paragraph("carea")
    line8 = builder.add_line()
    builder.add_word("Sistema", 1910, 38, 2052, 69, 0.96)
    builder.add_word("de", 2063, 37, 2104, 69, 0.93)
    builder.add_word("Información", 2117, 36, 2323, 69, 0.61)
    builder.add_word("Científica", 2337, 37, 2497, 69, 0.91)
    builder.add_word("Redalyc", 2509, 37, 2643, 78, 0.92)

    # Add image area
    builder.add_image(0, 486, 664, 1778, alt_text="Main content area")

    # Generate and save hOCR
    output_file = Path(
        "examples/redalyc_abstract_analysis/redalyc_search_hocr_output.hocr"
    )
    saved_file = builder.save_hocr(output_file)

    print(f"✅ hOCR generated and saved to: {saved_file}")

    # Get document summary
    summary = builder.get_document_summary()
    print(f"\n📊 Document Summary:")
    print(f"   Title: {summary['title']}")
    print(f"   Pages: {summary['pages']}")
    print(f"   Paragraphs: {summary['paragraphs']}")
    print(f"   Lines: {summary['lines']}")
    print(f"   Words: {summary['words']}")
    print(f"   Images: {summary['images']}")

    # Show sample of generated XML
    hocr_xml = builder.generate_hocr_xml()
    print(f"\n📄 Sample hOCR XML (first 500 characters):")
    print(hocr_xml[:500] + "..." if len(hocr_xml) > 500 else hocr_xml)

    return builder


if __name__ == "__main__":
    test_real_tesseract_output()
