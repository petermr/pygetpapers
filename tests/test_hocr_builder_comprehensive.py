#!/usr/bin/env python3
"""
Comprehensive tests for hOCR Builder functionality.

AUTHOR: P. Murray-Rust with assistance from CursorAI (Claude Sonnet 4)
VERSION: 1.0.0
PURPOSE: Test hOCR builder with Tesseract and PDF output formats
"""

import unittest
import tempfile
import os
from pathlib import Path
from typing import Dict, List, Any

# Add the pygetpapers directory to the path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from pygetpapers.core.hocr_builder import (
    HOCRBuilder, HOCRCharacter, HOCRWord, HOCRLine, 
    HOCRParagraph, HOCRPage, HOCRDocument,
    create_hocr_from_pdfplumber_data, create_hocr_from_tesseract_data
)


class TestHOCRBuilderComprehensive(unittest.TestCase):
    """Comprehensive tests for hOCR Builder functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = Path(self.temp_dir)
        
        # Sample Tesseract hOCR data based on real output
        self.tesseract_hocr_data = {
            'pages': [
                {
                    'page_number': 1,
                    'width': 3456,
                    'height': 1778,
                    'areas': [
                        {
                            'id': 'block_1_1',
                            'bbox': [82, 534, 344, 565],
                            'class': 'ocr_carea',
                            'paragraphs': [
                                {
                                    'id': 'par_1_1',
                                    'lang': 'eng',
                                    'bbox': [82, 534, 344, 565],
                                    'lines': [
                                        {
                                            'id': 'line_1_1',
                                            'bbox': [82, 534, 344, 565],
                                            'baseline': [0.004, -7],
                                            'x_size': 31,
                                            'x_descenders': 6,
                                            'x_ascenders': 7,
                                            'class': 'ocr_textfloat',
                                            'words': [
                                                {
                                                    'id': 'word_1_1',
                                                    'text': 'Filtros',
                                                    'bbox': [82, 534, 164, 559],
                                                    'confidence': 92
                                                },
                                                {
                                                    'id': 'word_1_2',
                                                    'text': 'de',
                                                    'bbox': [173, 534, 204, 559],
                                                    'confidence': 93
                                                },
                                                {
                                                    'id': 'word_1_3',
                                                    'text': 'bisqueda',
                                                    'bbox': [214, 534, 344, 565],
                                                    'confidence': 52
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
                    ],
                    'images': [
                        {
                            'id': 'block_1_6',
                            'bbox': [0, 486, 664, 1778],
                            'class': 'ocr_photo'
                        }
                    ]
                }
            ]
        }
        
        # Sample PDFPlumber data with enhanced features
        self.pdfplumber_data = [
            {
                'page_num': 1,
                'width': 612,
                'height': 792,
                'text_blocks': [
                    {
                        'text': 'Climate',
                        'x0': 50, 'y0': 50, 'x1': 100, 'y1': 70,
                        'fontname': 'Arial-Bold',
                        'size': 12,
                        'color': '#000000',
                        'bbox': [50, 50, 100, 70]
                    },
                    {
                        'text': 'Change',
                        'x0': 105, 'y0': 50, 'x1': 150, 'y1': 70,
                        'fontname': 'Arial',
                        'size': 12,
                        'color': '#000000',
                        'bbox': [105, 50, 150, 70]
                    },
                    {
                        'text': 'Adaptation',
                        'x0': 155, 'y0': 50, 'x1': 220, 'y1': 70,
                        'fontname': 'Arial',
                        'size': 12,
                        'color': '#000000',
                        'bbox': [155, 50, 220, 70]
                    }
                ],
                'images': [
                    {
                        'x0': 300, 'y0': 100, 'x1': 500, 'y1': 200,
                        'type': 'image',
                        'bbox': [300, 100, 500, 200]
                    }
                ],
                'graphics': [
                    {
                        'x0': 50, 'y0': 300, 'x1': 150, 'y1': 350,
                        'type': 'rect',
                        'stroke': '#000000',
                        'fill': '#ffffff',
                        'bbox': [50, 300, 150, 350]
                    }
                ]
            }
        ]

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_basic_hocr_creation(self):
        """Test basic hOCR creation with proper structure."""
        builder = HOCRBuilder("Test Document")
        
        # Add page
        page = builder.add_page(1, 612, 792)
        self.assertEqual(page.page_number, 1)
        self.assertEqual(page.width, 612)
        self.assertEqual(page.height, 792)
        
        # Add paragraph
        paragraph = builder.add_paragraph("heading")
        self.assertEqual(paragraph.paragraph_type, "heading")
        
        # Add line
        line = builder.add_line()
        self.assertIsInstance(line, HOCRLine)
        
        # Add word
        word = builder.add_word("Climate", 50, 50, 100, 70, 0.95, "Arial", 12, "bold")
        self.assertEqual(word.text, "Climate")
        self.assertEqual(word.x0, 50)
        self.assertEqual(word.y0, 50)
        self.assertEqual(word.x1, 100)
        self.assertEqual(word.y1, 70)
        self.assertEqual(word.confidence, 0.95)
        self.assertEqual(word.font_family, "Arial")
        self.assertEqual(word.font_size, 12)
        self.assertEqual(word.font_weight, "bold")

    def test_hocr_xml_generation(self):
        """Test hOCR XML generation with proper structure."""
        builder = HOCRBuilder("Test Document")
        
        # Create simple document
        page = builder.add_page(1, 612, 792)
        paragraph = builder.add_paragraph("heading")
        line = builder.add_line()
        word = builder.add_word("Climate", 50, 50, 100, 70, 0.95, "Arial", 12, "bold")
        
        # Generate XML
        hocr_xml = builder.generate_hocr_xml()
        
        # Verify XML structure
        self.assertIn('<?xml version="1.0" encoding="UTF-8"?>', hocr_xml)
        self.assertIn('<html xmlns="http://www.w3.org/1999/xhtml"', hocr_xml)
        self.assertIn('<meta name="ocr-system" content="pygetpapers hOCR Builder"', hocr_xml)
        self.assertIn('<div class="ocr_page"', hocr_xml)
        self.assertIn('<div class="ocr_par"', hocr_xml)
        self.assertIn('<span class="ocr_line"', hocr_xml)
        self.assertIn('<span class="ocr_word"', hocr_xml)
        self.assertIn('Climate', hocr_xml)

    def test_tesseract_data_parsing(self):
        """Test parsing Tesseract hOCR data."""
        # Create hOCR from Tesseract data
        builder = create_hocr_from_tesseract_data(self.tesseract_hocr_data)
        
        # Verify structure
        self.assertEqual(len(builder.document.pages), 1)
        page = builder.document.pages[0]
        self.assertEqual(page.page_number, 1)
        self.assertEqual(page.width, 3456)
        self.assertEqual(page.height, 1778)
        
        # Verify content
        self.assertEqual(len(page.paragraphs), 1)
        paragraph = page.paragraphs[0]
        self.assertEqual(len(paragraph.lines), 1)
        line = paragraph.lines[0]
        self.assertEqual(len(line.words), 3)
        
        # Verify words
        words = line.words
        self.assertEqual(words[0].text, "Filtros")
        self.assertEqual(words[0].confidence, 0.92)
        self.assertEqual(words[1].text, "de")
        self.assertEqual(words[1].confidence, 0.93)
        self.assertEqual(words[2].text, "bisqueda")
        self.assertEqual(words[2].confidence, 0.52)

    def test_pdfplumber_data_parsing(self):
        """Test parsing PDFPlumber data with enhanced features."""
        # Create hOCR from PDFPlumber data
        builder = create_hocr_from_pdfplumber_data(self.pdfplumber_data)
        
        # Verify structure
        self.assertEqual(len(builder.document.pages), 1)
        page = builder.document.pages[0]
        self.assertEqual(page.page_number, 1)
        self.assertEqual(page.width, 612)
        self.assertEqual(page.height, 792)
        
        # Verify text content
        self.assertEqual(len(page.paragraphs), 1)
        paragraph = page.paragraphs[0]
        self.assertEqual(len(paragraph.lines), 1)
        line = paragraph.lines[0]
        self.assertEqual(len(line.words), 3)
        
        # Verify words with font information
        words = line.words
        self.assertEqual(words[0].text, "Climate")
        self.assertEqual(words[0].font_family, "Arial")  # Decomposed from "Arial-Bold"
        self.assertEqual(words[0].font_size, 12)
        self.assertEqual(words[0].font_weight, "bold")
        
        self.assertEqual(words[1].text, "Change")
        self.assertEqual(words[1].font_family, "Arial")
        self.assertEqual(words[1].font_size, 12)
        self.assertEqual(words[1].font_weight, "normal")
        
        self.assertEqual(words[2].text, "Adaptation")
        self.assertEqual(words[2].font_family, "Arial")
        self.assertEqual(words[2].font_size, 12)

    def test_pdf_specific_features(self):
        """Test PDF-specific features like FP coordinates and CSS styles."""
        builder = HOCRBuilder("PDF Document")
        page = builder.add_page(1, 612, 792)
        
        # Add paragraph with PDF-specific class
        paragraph = builder.add_paragraph("pdf_area")
        self.assertEqual(paragraph.paragraph_type, "pdf_area")
        
        # Add line with baseline information
        line = builder.add_line()
        line.baseline = 0.004
        
        # Add word with detailed font properties
        word = builder.add_word(
            "Climate", 50, 50, 100, 70, 0.95,
            font_family="Arial-Bold",
            font_size=12,
            font_weight="bold",
            font_style="normal",
            color="#000000",
            baseline=0.004
        )
        
        # Generate XML and verify PDF-specific features
        hocr_xml = builder.generate_hocr_xml()
        
        # Check for PDF-specific attributes
        self.assertIn('class="ocr_par"', hocr_xml)
        self.assertIn('baseline', hocr_xml)
        self.assertIn('x_font', hocr_xml)
        self.assertIn('x_fsize', hocr_xml)
        self.assertIn('x_fweight', hocr_xml)
        self.assertIn('x_color', hocr_xml)

    def test_image_and_graphic_handling(self):
        """Test handling of images and graphics."""
        builder = HOCRBuilder("Document with Images")
        page = builder.add_page(1, 612, 792)
        
        # Add image
        image = builder.add_image(
            x0=300, y0=100, x1=500, y1=200,
            alt_text="Sample chart",
            confidence=0.9
        )
        
        # Add graphic with SVG
        svg_data = '<svg width="100" height="50"><rect x="0" y="0" width="100" height="50" fill="blue"/></svg>'
        graphic = builder.add_graphic(
            graphic_type="rect",
            x0=50, y0=300, x1=150, y1=350,
            svg_data=svg_data,
            confidence=0.85
        )
        
        # Verify structure
        self.assertEqual(len(page.images), 1)
        self.assertEqual(len(page.graphics), 1)
        
        # Verify image properties
        self.assertEqual(image['x0'], 300)
        self.assertEqual(image['y0'], 100)
        self.assertEqual(image['x1'], 500)
        self.assertEqual(image['y1'], 200)
        self.assertEqual(image['alt_text'], "Sample chart")
        self.assertEqual(image['confidence'], 0.9)
        
        # Verify graphic properties
        self.assertEqual(graphic['type'], "rect")
        self.assertEqual(graphic['x0'], 50)
        self.assertEqual(graphic['y0'], 300)
        self.assertEqual(graphic['x1'], 150)
        self.assertEqual(graphic['y1'], 350)
        self.assertIn('svg', graphic['svg_data'])

    def test_confidence_scores(self):
        """Test confidence score handling."""
        builder = HOCRBuilder("Confidence Test")
        page = builder.add_page(1, 612, 792)
        paragraph = builder.add_paragraph()
        line = builder.add_line()
        
        # Add words with different confidence scores
        word1 = builder.add_word("High", 50, 50, 80, 70, confidence=0.95)
        word2 = builder.add_word("Medium", 85, 50, 130, 70, confidence=0.75)
        word3 = builder.add_word("Low", 135, 50, 160, 70, confidence=0.45)
        
        # Generate XML and verify confidence attributes
        hocr_xml = builder.generate_hocr_xml()
        
        # Check that confidence scores are properly encoded
        self.assertIn('x_wconf 95', hocr_xml)
        self.assertIn('x_wconf 75', hocr_xml)
        self.assertIn('x_wconf 45', hocr_xml)

    def test_multiple_paragraph_types(self):
        """Test different paragraph types."""
        builder = HOCRBuilder("Multiple Paragraph Types")
        page = builder.add_page(1, 612, 792)
        
        # Add different paragraph types
        heading = builder.add_paragraph("heading")
        normal = builder.add_paragraph("normal")
        list_item = builder.add_paragraph("list_item")
        footnote = builder.add_paragraph("footnote")
        
        # Add content to each
        for paragraph in [heading, normal, list_item, footnote]:
            line = builder.add_line()
            builder.add_word("Test", 50, 50, 80, 70)
        
        # Verify paragraph types
        self.assertEqual(page.paragraphs[0].paragraph_type, "heading")
        self.assertEqual(page.paragraphs[1].paragraph_type, "normal")
        self.assertEqual(page.paragraphs[2].paragraph_type, "list_item")
        self.assertEqual(page.paragraphs[3].paragraph_type, "footnote")

    def test_character_level_details(self):
        """Test character-level detail handling."""
        builder = HOCRBuilder("Character Details")
        page = builder.add_page(1, 612, 792)
        paragraph = builder.add_paragraph()
        line = builder.add_line()
        word = builder.add_word("Test", 50, 50, 80, 70)
        
        # Add individual characters
        char1 = builder.add_character("T", 50, 50, 60, 70, 0.98, "Arial", 12, "bold", "normal", "#000000", 65)
        char2 = builder.add_character("e", 60, 50, 70, 70, 0.96, "Arial", 12, "bold", "normal", "#000000", 65)
        char3 = builder.add_character("s", 70, 50, 75, 70, 0.97, "Arial", 12, "bold", "normal", "#000000", 65)
        char4 = builder.add_character("t", 75, 50, 80, 70, 0.95, "Arial", 12, "bold", "normal", "#000000", 65)
        
        # Verify character properties
        self.assertEqual(char1.text, "T")
        self.assertEqual(char1.confidence, 0.98)
        self.assertEqual(char1.font_family, "Arial")
        self.assertEqual(char1.font_size, 12)
        self.assertEqual(char1.font_weight, "bold")
        self.assertEqual(char1.color, "#000000")
        self.assertEqual(char1.baseline, 65)

    def test_file_saving(self):
        """Test saving hOCR files."""
        builder = HOCRBuilder("Save Test")
        page = builder.add_page(1, 612, 792)
        paragraph = builder.add_paragraph()
        line = builder.add_line()
        builder.add_word("Test", 50, 50, 80, 70)
        
        # Save file
        output_file = self.output_dir / "test_output.hocr"
        saved_file = builder.save_hocr(output_file)
        
        # Verify file was created
        self.assertTrue(saved_file.exists())
        self.assertTrue(saved_file.stat().st_size > 0)
        
        # Verify file content
        with open(saved_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('<?xml version="1.0"', content)
            self.assertIn('<html xmlns="http://www.w3.org/1999/xhtml"', content)
            self.assertIn('Test', content)

    def test_document_summary(self):
        """Test document summary generation."""
        builder = HOCRBuilder("Summary Test")
        
        # Add multiple pages with content
        for page_num in range(1, 4):
            page = builder.add_page(page_num, 612, 792)
            paragraph = builder.add_paragraph()
            line = builder.add_line()
            builder.add_word(f"Page{page_num}", 50, 50, 100, 70)
            
            # Add image to first page
            if page_num == 1:
                builder.add_image(300, 100, 500, 200, alt_text="Test image")
        
        # Get summary
        summary = builder.get_document_summary()
        
        # Verify summary
        self.assertEqual(summary['title'], "Summary Test")
        self.assertEqual(summary['pages'], 3)
        self.assertEqual(summary['paragraphs'], 3)
        self.assertEqual(summary['lines'], 3)
        self.assertEqual(summary['words'], 3)
        self.assertEqual(summary['images'], 1)
        self.assertEqual(summary['graphics'], 0)

    def test_real_tesseract_format_compatibility(self):
        """Test compatibility with real Tesseract hOCR format."""
        # Create hOCR that matches Tesseract format
        builder = HOCRBuilder("Tesseract Compatible")
        page = builder.add_page(1, 3456, 1778)
        
        # Add carea (content area)
        paragraph = builder.add_paragraph("carea")
        line = builder.add_line()
        
        # Add words with Tesseract-style properties
        word1 = builder.add_word("Filtros", 82, 534, 164, 559, 0.92)
        word2 = builder.add_word("de", 173, 534, 204, 559, 0.93)
        word3 = builder.add_word("bisqueda", 214, 534, 344, 565, 0.52)
        
        # Generate XML
        hocr_xml = builder.generate_hocr_xml()
        
        # Verify Tesseract compatibility
        self.assertIn('bbox 0 0 3456 1778', hocr_xml)
        self.assertIn('x_wconf 92', hocr_xml)
        self.assertIn('x_wconf 93', hocr_xml)
        self.assertIn('x_wconf 52', hocr_xml)
        self.assertIn('Filtros', hocr_xml)
        self.assertIn('de', hocr_xml)
        self.assertIn('bisqueda', hocr_xml)

    def test_pdf_enhanced_features(self):
        """Test PDF-enhanced features like FP coordinates and CSS styles."""
        builder = HOCRBuilder("PDF Enhanced")
        page = builder.add_page(1, 612, 792)
        
        # Add paragraph with PDF-specific styling
        paragraph = builder.add_paragraph("pdf_area")
        line = builder.add_line()
        
        # Add word with comprehensive PDF properties
        word = builder.add_word(
            "Climate",
            x0=50, y0=50, x1=100, y1=70,
            confidence=0.95,
            font_family="Arial-Bold",
            font_size=12,
            font_weight="bold",
            font_style="normal",
            color="#000000",
            baseline=0.004
        )
        
        # Generate XML
        hocr_xml = builder.generate_hocr_xml()
        
        # Verify PDF-specific features
        self.assertIn('bbox 50 50 100 70', hocr_xml)
        self.assertIn('x_wconf 95', hocr_xml)
        self.assertIn('x_font &quot;Arial-Bold&quot;', hocr_xml)
        self.assertIn('x_fsize 12', hocr_xml)
        self.assertIn('x_fweight &quot;bold&quot;', hocr_xml)
        self.assertIn('x_fstyle &quot;normal&quot;', hocr_xml)
        self.assertIn('x_color &quot;#000000&quot;', hocr_xml)
        self.assertIn('baseline 0.004', hocr_xml)


def create_hocr_from_tesseract_data(tesseract_data: Dict) -> HOCRBuilder:
    """
    Create hOCR from Tesseract data structure.
    
    Args:
        tesseract_data: Dictionary with Tesseract hOCR structure
        
    Returns:
        HOCRBuilder instance with populated data
    """
    builder = HOCRBuilder("Tesseract Document")
    
    for page_data in tesseract_data['pages']:
        page = builder.add_page(
            page_data['page_number'],
            page_data['width'],
            page_data['height']
        )
        
        # Process content areas
        for area in page_data.get('areas', []):
            for paragraph_data in area.get('paragraphs', []):
                paragraph = builder.add_paragraph()
                
                for line_data in paragraph_data.get('lines', []):
                    line = builder.add_line()
                    
                    for word_data in line_data.get('words', []):
                        builder.add_word(
                            text=word_data['text'],
                            x0=word_data['bbox'][0],
                            y0=word_data['bbox'][1],
                            x1=word_data['bbox'][2],
                            y1=word_data['bbox'][3],
                            confidence=word_data.get('confidence', 100) / 100.0
                        )
        
        # Process images
        for image_data in page_data.get('images', []):
            builder.add_image(
                x0=image_data['bbox'][0],
                y0=image_data['bbox'][1],
                x1=image_data['bbox'][2],
                y1=image_data['bbox'][3]
            )
    
    return builder


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2) 