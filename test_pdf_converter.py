#!/usr/bin/env python3
"""
Test script for the PDF to HTML Converter

This script downloads a simple PDF and tests the converter functionality.
"""

import requests
from pathlib import Path
from pdf_to_html_converter import PDFToHTMLConverter


def download_test_pdf():
    """Download a simple test PDF from a public source."""
    print("📥 Downloading test PDF...")
    
    # Use a simple PDF from a public source
    # This is a sample PDF from the US government
    url = "https://www.irs.gov/pub/irs-pdf/fw4.pdf"
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        pdf_path = Path("test_document.pdf")
        with open(pdf_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✅ Test PDF downloaded: {pdf_path}")
        return pdf_path
        
    except Exception as e:
        print(f"❌ Failed to download test PDF: {e}")
        return None


def test_converter():
    """Test the PDF converter with the preprint PDF."""
    print("\n🧪 Testing PDF to HTML Converter")
    print("=" * 50)
    
    # Use the preprint PDF from tests/data
    pdf_path = Path("tests/data/2025.07.06.662788v1.full.pdf")
    
    if not pdf_path.exists():
        print(f"❌ Preprint PDF not found: {pdf_path}")
        return
    
    # Create converter
    converter = PDFToHTMLConverter(output_dir="test_output")
    
    try:
        # Convert PDF to HTML
        print(f"\n📄 Converting: {pdf_path}")
        html_path = converter.convert_pdf_to_html(pdf_path, "Test Document")
        
        print(f"✅ Conversion successful!")
        print(f"📄 Input PDF: {pdf_path}")
        print(f"🌐 Output HTML: {html_path}")
        
        # Show file sizes
        pdf_size = pdf_path.stat().st_size / 1024
        html_size = html_path.stat().st_size / 1024
        print(f"📊 PDF size: {pdf_size:.1f} KB")
        print(f"📊 HTML size: {html_size:.1f} KB")
        
        # Show a preview of the HTML content
        print(f"\n📖 HTML Preview (first 500 characters):")
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
            preview = content[:500] + "..." if len(content) > 500 else content
            print(preview)
        
        print(f"\n🎉 Test completed successfully!")
        print(f"📁 Check the output in: {converter.output_dir}")
        
    except Exception as e:
        print(f"❌ Conversion failed: {e}")
        import traceback
        traceback.print_exc()


def test_with_local_pdf():
    """Test with a local PDF if available."""
    print("\n🔍 Looking for local PDF files...")
    
    # Check for common PDF files
    possible_pdfs = [
        "example.pdf",
        "test.pdf", 
        "document.pdf",
        "sample.pdf"
    ]
    
    for pdf_name in possible_pdfs:
        pdf_path = Path(pdf_name)
        if pdf_path.exists():
            print(f"📄 Found local PDF: {pdf_path}")
            
            converter = PDFToHTMLConverter(output_dir="local_test_output")
            
            try:
                html_path = converter.convert_pdf_to_html(pdf_path, "Local Test Document")
                print(f"✅ Local conversion successful!")
                print(f"🌐 HTML output: {html_path}")
                return
            except Exception as e:
                print(f"❌ Local conversion failed: {e}")
    
    print("❌ No local PDF files found.")


if __name__ == "__main__":
    print("🚀 PDF to HTML Converter Test")
    print("=" * 50)
    
    # Test with local PDF first
    test_with_local_pdf()
    
    # Test with downloaded PDF
    test_converter() 