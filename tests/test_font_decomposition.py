#!/usr/bin/env python3
"""
Test Font Decomposition Functionality.

AUTHOR: P. Murray-Rust with assistance from CursorAI (Claude Sonnet 4)
VERSION: 1.0.0
PURPOSE: Test font name decomposition and line coordinate preservation
"""

import os

# Add the pygetpapers directory to the path
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).parent.parent))

from pygetpapers.core.hocr_builder import (
    HOCRBuilder,
    create_hocr_from_pdfplumber_data,
    decompose_font_name,
)


class TestFontDecomposition(unittest.TestCase):
    """Test font name decomposition functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = Path(self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_font_decomposition_function(self):
        """Test the decompose_font_name function with various patterns."""

        # Test cases with expected results
        test_cases = [
            # (input_font_name, expected_family, expected_weight, expected_style)
            ("Arial-Bold", "Arial", "bold", "normal"),
            ("Times-Italic", "Times", "normal", "italic"),
            ("Helvetica-BoldItalic", "Helvetica", "bold", "italic"),
            ("Courier-Bold-Italic", "Courier", "bold", "italic"),
            ("Foo-B", "Foo", "bold", "normal"),
            ("Bar-I", "Bar", "normal", "italic"),
            ("Baz-BI", "Baz", "bold", "italic"),
            ("Qux-IB", "Qux", "bold", "italic"),
            ("PlainFont", "PlainFont", "normal", "normal"),
            ("", "Arial", "normal", "normal"),
            (None, "Arial", "normal", "normal"),
        ]

        for font_name, expected_family, expected_weight, expected_style in test_cases:
            with self.subTest(font_name=font_name):
                family, weight, style = decompose_font_name(font_name)
                self.assertEqual(family, expected_family)
                self.assertEqual(weight, expected_weight)
                self.assertEqual(style, expected_style)

    def test_add_word_with_font_name(self):
        """Test adding words with automatic font decomposition."""
        builder = HOCRBuilder("Font Decomposition Test")
        page = builder.add_page(1, 612, 792)
        paragraph = builder.add_paragraph()
        line = builder.add_line()

        # Add words with different font patterns
        word1 = builder.add_word_with_font_name(
            "Bold", 50, 50, 80, 70, font_name="Arial-Bold", font_size=12
        )

        word2 = builder.add_word_with_font_name(
            "Italic", 85, 50, 120, 70, font_name="Times-Italic", font_size=12
        )

        word3 = builder.add_word_with_font_name(
            "BoldItalic",
            125,
            50,
            180,
            70,
            font_name="Helvetica-BoldItalic",
            font_size=12,
        )

        # Verify font decomposition
        self.assertEqual(word1.font_family, "Arial")
        self.assertEqual(word1.font_weight, "bold")
        self.assertEqual(word1.font_style, "normal")

        self.assertEqual(word2.font_family, "Times")
        self.assertEqual(word2.font_weight, "normal")
        self.assertEqual(word2.font_style, "italic")

        self.assertEqual(word3.font_family, "Helvetica")
        self.assertEqual(word3.font_weight, "bold")
        self.assertEqual(word3.font_style, "italic")

    def test_line_coordinate_preservation(self):
        """Test that lines are preserved as spans with coordinates."""
        builder = HOCRBuilder("Line Coordinate Test")
        page = builder.add_page(1, 612, 792)
        paragraph = builder.add_paragraph()

        # Add multiple lines
        line1 = builder.add_line()
        builder.add_word("First", 50, 50, 90, 70)
        builder.add_word("line", 95, 50, 115, 70)

        line2 = builder.add_line()
        builder.add_word("Second", 50, 80, 110, 100)
        builder.add_word("line", 115, 80, 135, 100)

        # Generate XML
        hocr_xml = builder.generate_hocr_xml()

        # Verify line structure
        self.assertIn('<div class="pdf_par"', hocr_xml)
        self.assertIn('<span class="pdf_line"', hocr_xml)

        # Verify line coordinates are preserved
        self.assertIn('title="bbox 50 50 115 70"', hocr_xml)  # First line
        self.assertIn('title="bbox 50 80 135 100"', hocr_xml)  # Second line

        # Verify words are within lines
        self.assertIn("First", hocr_xml)
        self.assertIn("Second", hocr_xml)

    def test_pdfplumber_integration_with_font_decomposition(self):
        """Test PDFPlumber integration with font decomposition."""

        # Sample PDFPlumber data with various font patterns
        pdfplumber_data = [
            {
                "page_num": 1,
                "width": 612,
                "height": 792,
                "text_blocks": [
                    {
                        "text": "Bold",
                        "x0": 50,
                        "y0": 50,
                        "x1": 80,
                        "y1": 70,
                        "fontname": "Arial-Bold",
                        "size": 12,
                        "color": "#000000",
                    },
                    {
                        "text": "Italic",
                        "x0": 85,
                        "y0": 50,
                        "x1": 120,
                        "y1": 70,
                        "fontname": "Times-Italic",
                        "size": 12,
                        "color": "#000000",
                    },
                    {
                        "text": "BoldItalic",
                        "x0": 125,
                        "y0": 50,
                        "x1": 180,
                        "y1": 70,
                        "fontname": "Helvetica-BoldItalic",
                        "size": 12,
                        "color": "#000000",
                    },
                    {
                        "text": "Normal",
                        "x0": 50,
                        "y0": 80,
                        "x1": 100,
                        "y1": 100,
                        "fontname": "Arial",
                        "size": 12,
                        "color": "#000000",
                    },
                ],
            }
        ]

        # Create hOCR from PDFPlumber data
        builder = create_hocr_from_pdfplumber_data(pdfplumber_data)

        # Verify structure
        self.assertEqual(len(builder.document.pages), 1)
        page = builder.document.pages[0]
        self.assertEqual(len(page.paragraphs), 1)
        paragraph = page.paragraphs[0]
        self.assertEqual(
            len(paragraph.lines), 2
        )  # Two lines due to y-position grouping

        # Verify font decomposition in words
        words = []
        for line in paragraph.lines:
            words.extend(line.words)

        # Find words by text
        bold_word = next(w for w in words if w.text == "Bold")
        italic_word = next(w for w in words if w.text == "Italic")
        bolditalic_word = next(w for w in words if w.text == "BoldItalic")
        normal_word = next(w for w in words if w.text == "Normal")

        # Verify font decomposition
        self.assertEqual(bold_word.font_family, "Arial")
        self.assertEqual(bold_word.font_weight, "bold")
        self.assertEqual(bold_word.font_style, "normal")

        self.assertEqual(italic_word.font_family, "Times")
        self.assertEqual(italic_word.font_weight, "normal")
        self.assertEqual(italic_word.font_style, "italic")

        self.assertEqual(bolditalic_word.font_family, "Helvetica")
        self.assertEqual(bolditalic_word.font_weight, "bold")
        self.assertEqual(bolditalic_word.font_style, "italic")

        self.assertEqual(normal_word.font_family, "Arial")
        self.assertEqual(normal_word.font_weight, "normal")
        self.assertEqual(normal_word.font_style, "normal")

    def test_xml_output_with_font_decomposition(self):
        """Test XML output includes decomposed font information."""
        builder = HOCRBuilder("Font XML Test")
        page = builder.add_page(1, 612, 792)
        paragraph = builder.add_paragraph()
        line = builder.add_line()

        # Add word with font decomposition
        builder.add_word_with_font_name(
            "Test",
            50,
            50,
            80,
            70,
            font_name="Arial-Bold",
            font_size=12,
            color="#000000",
        )

        # Generate XML
        hocr_xml = builder.generate_hocr_xml()

        # Verify font information in XML (now using CSS style attributes)
        self.assertIn("font-family: &quot;Arial&quot;", hocr_xml)
        self.assertIn("font-weight: bold", hocr_xml)
        self.assertIn("font-style: normal", hocr_xml)
        self.assertIn("font-size: 12pt", hocr_xml)
        self.assertIn("fill: #000000", hocr_xml)

    def test_complex_font_patterns(self):
        """Test complex font naming patterns."""
        builder = HOCRBuilder("Complex Font Patterns")
        page = builder.add_page(1, 612, 792)
        paragraph = builder.add_paragraph()
        line = builder.add_line()

        # Test various font patterns
        patterns = [
            ("Arial-Bold", "Arial", "bold", "normal"),
            ("Times-Italic", "Times", "normal", "italic"),
            ("Helvetica-BoldItalic", "Helvetica", "bold", "italic"),
            ("Courier-Bold-Italic", "Courier", "bold", "italic"),
            ("Foo-B", "Foo", "bold", "normal"),
            ("Bar-I", "Bar", "normal", "italic"),
            ("Baz-BI", "Baz", "bold", "italic"),
            ("Qux-IB", "Qux", "bold", "italic"),
        ]

        for i, (
            font_name,
            expected_family,
            expected_weight,
            expected_style,
        ) in enumerate(patterns):
            word = builder.add_word_with_font_name(
                f"Word{i}",
                50 + i * 60,
                50,
                100 + i * 60,
                70,
                font_name=font_name,
                font_size=12,
            )

            self.assertEqual(word.font_family, expected_family)
            self.assertEqual(word.font_weight, expected_weight)
            self.assertEqual(word.font_style, expected_style)

    def test_line_span_structure(self):
        """Test that lines are properly structured as spans within paragraphs."""
        builder = HOCRBuilder("Line Span Structure")
        page = builder.add_page(1, 612, 792)
        paragraph = builder.add_paragraph()

        # Add multiple lines with different y positions
        line1 = builder.add_line()
        builder.add_word("Line", 50, 50, 80, 70)
        builder.add_word("one", 85, 50, 105, 70)

        line2 = builder.add_line()
        builder.add_word("Line", 50, 80, 80, 100)
        builder.add_word("two", 85, 80, 105, 100)

        # Generate XML
        hocr_xml = builder.generate_hocr_xml()

        # Verify paragraph structure
        self.assertIn('<div class="pdf_par"', hocr_xml)

        # Verify line spans within paragraph
        lines = hocr_xml.split("\n")
        line_spans = [line for line in lines if 'class="pdf_line"' in line]

        self.assertEqual(len(line_spans), 2)

        # Verify line coordinates
        self.assertIn('title="bbox 50 50 105 70"', hocr_xml)  # First line
        self.assertIn('title="bbox 50 80 105 100"', hocr_xml)  # Second line


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2)
