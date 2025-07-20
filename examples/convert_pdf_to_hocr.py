#!/usr/bin/env python3
"""
Convert PDF to hOCR Format.

AUTHOR: P. Murray-Rust with assistance from CursorAI (Claude Sonnet 4)
VERSION: 1.0.0
PURPOSE: Convert PDF files to hOCR format using PDFPlumber extraction
"""

import sys
import pdfplumber
from pathlib import Path
from typing import List, Dict, Any

# Add the pygetpapers directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pygetpapers.core.hocr_builder import create_hocr_from_pdfplumber_data


def extract_pdf_data(pdf_path: Path) -> List[Dict[str, Any]]:
    """
    Extract data from PDF using PDFPlumber.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        List of page data dictionaries
    """
    print(f"📄 Extracting data from: {pdf_path}")
    
    pages_data = []
    
    with pdfplumber.open(pdf_path) as pdf:
        print(f"📊 PDF has {len(pdf.pages)} pages")
        
        for page_num, page in enumerate(pdf.pages, 1):
            print(f"  Processing page {page_num}...")
            
            # Extract text blocks with font information
            text_blocks = []
            
            # Extract text with font information
            chars = page.chars
            if chars:
                # Group characters by font and position to create text blocks
                current_block = None
                
                for char in chars:
                    text = char.get('text', '')
                    x0 = char.get('x0', 0)
                    y0 = char.get('y0', 0)
                    x1 = char.get('x1', 0)
                    y1 = char.get('y1', 0)
                    fontname = char.get('fontname', 'Arial')
                    size = char.get('size', 12)
                    color = char.get('non_stroking_color', '#000000')
                    
                    # Convert color tuple to hex if needed
                    if isinstance(color, tuple):
                        color = f"#{int(color[0]*255):02x}{int(color[1]*255):02x}{int(color[2]*255):02x}"
                    
                    # Check if this character belongs to the current block
                    if (current_block and 
                        abs(char.get('y0', 0) - current_block['y0']) < 5 and  # Same line
                        abs(char.get('x0', 0) - current_block['x1']) < 20 and  # Close horizontally
                        char.get('fontname') == current_block['fontname'] and  # Same font
                        char.get('size') == current_block['size']):  # Same size
                        
                        # Extend current block
                        current_block['text'] += text
                        current_block['x1'] = x1
                        current_block['y1'] = max(current_block['y1'], y1)
                    else:
                        # Start new block
                        if current_block:
                            text_blocks.append(current_block)
                        
                        current_block = {
                            'text': text,
                            'x0': x0,
                            'y0': y0,
                            'x1': x1,
                            'y1': y1,
                            'fontname': fontname,
                            'size': size,
                            'color': color
                        }
                
                # Add the last block
                if current_block:
                    text_blocks.append(current_block)
            
            # Extract images
            images = []
            for image in page.images:
                images.append({
                    'x0': image.get('x0', 0),
                    'y0': image.get('y0', 0),
                    'x1': image.get('x1', 0),
                    'y1': image.get('y1', 0),
                    'alt_text': f"Image on page {page_num}"
                })
            
            # Extract graphics
            graphics = []
            for graphic in page.edges + page.rects + page.curves:
                graphics.append({
                    'type': graphic.get('object_type', 'unknown'),
                    'x0': graphic.get('x0', 0),
                    'y0': graphic.get('y0', 0),
                    'x1': graphic.get('x1', 0),
                    'y1': graphic.get('y1', 0),
                    'fill': graphic.get('fill', '#ffffff'),
                    'stroke': graphic.get('stroke', '#000000')
                })
            
            # Create page data
            page_data = {
                'page_num': page_num,
                'width': page.width,
                'height': page.height,
                'text_blocks': text_blocks,
                'images': images,
                'graphics': graphics
            }
            
            pages_data.append(page_data)
            print(f"    Extracted {len(text_blocks)} text blocks, {len(images)} images, {len(graphics)} graphics")
    
    return pages_data


def convert_pdf_to_hocr(pdf_path: Path, output_path: Path = None) -> Path:
    """
    Convert PDF to hOCR format.
    
    Args:
        pdf_path: Path to input PDF file
        output_path: Path for output hOCR file (optional)
        
    Returns:
        Path to the generated hOCR file
    """
    if not output_path:
        output_path = pdf_path.with_suffix('.hocr')
    
    print(f"🔄 Converting {pdf_path.name} to hOCR format...")
    
    # Extract PDF data
    pdf_data = extract_pdf_data(pdf_path)
    
    if not pdf_data:
        raise ValueError("No data extracted from PDF")
    
    # Create hOCR from PDF data
    print("🏗️  Building hOCR document...")
    builder = create_hocr_from_pdfplumber_data(pdf_data)
    
    # Save hOCR file
    print(f"💾 Saving hOCR to: {output_path}")
    saved_file = builder.save_hocr(output_path)
    
    # Print summary
    summary = builder.get_document_summary()
    print(f"\n✅ Conversion completed!")
    print(f"📊 Document Summary:")
    print(f"   Pages: {summary['pages']}")
    print(f"   Paragraphs: {summary['paragraphs']}")
    print(f"   Lines: {summary['lines']}")
    print(f"   Words: {summary['words']}")
    print(f"   Images: {summary['images']}")
    print(f"   Graphics: {summary['graphics']}")
    
    return saved_file


def main():
    """Main conversion function."""
    # Input PDF file
    pdf_file = Path("examples/86214152006.pdf")
    
    if not pdf_file.exists():
        print(f"❌ PDF file not found: {pdf_file}")
        return False
    
    try:
        # Convert PDF to hOCR
        output_file = convert_pdf_to_hocr(pdf_file)
        
        print(f"\n🎉 Successfully converted {pdf_file.name} to hOCR format!")
        print(f"📁 Output file: {output_file}")
        print(f"📏 File size: {output_file.stat().st_size:,} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ Error converting PDF: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 