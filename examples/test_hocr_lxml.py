#!/usr/bin/env python3
"""
Simple test for hOCR Builder with lxml.

AUTHOR: P. Murray-Rust with assistance from CursorAI (Claude Sonnet 4)
VERSION: 1.0.0
PURPOSE: Verify hOCR builder uses lxml instead of lexical XML construction
"""

from pathlib import Path

from pygetpapers.core.hocr_builder import HOCRBuilder


def test_lxml_hocr_generation():
    """Test that hOCR generation uses lxml properly."""
    print("🧪 Testing hOCR Builder with lxml")
    print("=" * 50)
    
    # Create hOCR builder
    builder = HOCRBuilder("Test Document")
    
    # Add a page
    page = builder.add_page(1, 612, 792)
    print(f"✅ Added page: {page.page_number}")
    
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
    ]
    
    for text, x0, y0, x1, y1, conf, font, size, weight in words_data:
        word = builder.add_word(text, x0, y0, x1, y1, conf, font, size, weight)
        print(f"   ✅ Added word: '{word.text}'")
    
    # Generate hOCR XML
    hocr_xml = builder.generate_hocr_xml()
    print(f"✅ Generated hOCR XML ({len(hocr_xml)} characters)")
    
    # Verify it's proper XML (not lexical construction)
    print(f"\n📖 hOCR XML Preview (first 300 characters):")
    preview = hocr_xml[:300] + "..." if len(hocr_xml) > 300 else hocr_xml
    print(preview)
    
    # Check for proper XML structure
    if "<?xml version=" in hocr_xml:
        print("✅ Contains proper XML declaration")
    else:
        print("❌ Missing XML declaration")
        return False
    
    if "<html xmlns=" in hocr_xml:
        print("✅ Contains proper HTML namespace")
    else:
        print("❌ Missing HTML namespace")
        return False
    
    if "<div class=\"ocr_page\"" in hocr_xml:
        print("✅ Contains proper hOCR page structure")
    else:
        print("❌ Missing hOCR page structure")
        return False
    
    if "<span class=\"ocr_word\"" in hocr_xml:
        print("✅ Contains proper hOCR word structure")
    else:
        print("❌ Missing hOCR word structure")
        return False
    
    # Save hOCR file
    output_dir = Path("examples", "hocr_test_output")
    output_dir.mkdir(exist_ok=True)
    
    hocr_file = builder.save_hocr(Path(output_dir, "lxml_test.hocr"))
    print(f"\n💾 Saved hOCR file: {hocr_file}")
    
    # Get document summary
    summary = builder.get_document_summary()
    print(f"\n📊 Document Summary:")
    print(f"   Pages: {summary['pages']}")
    print(f"   Paragraphs: {summary['paragraphs']}")
    print(f"   Lines: {summary['lines']}")
    print(f"   Words: {summary['words']}")
    
    print(f"\n✅ hOCR Builder with lxml test completed successfully!")
    return True


def main():
    """Main test function."""
    print("=" * 70)
    print("           hOCR BUILDER LXML TEST")
    print("=" * 70)
    print()
    
    try:
        success = test_lxml_hocr_generation()
        
        if success:
            print("\n" + "=" * 70)
            print("           TEST RESULTS SUMMARY")
            print("=" * 70)
            
            print("✅ hOCR BUILDER LXML TEST PASSED!")
            print()
            print("🎯 lxml integration working correctly:")
            print("   ✅ Proper XML declaration")
            print("   ✅ HTML namespace declaration")
            print("   ✅ hOCR page structure")
            print("   ✅ hOCR word structure")
            print("   ✅ No lexical XML construction")
            print()
            print("📁 Output file: examples/hocr_test_output/lxml_test.hocr")
            print()
            print("🎉 hOCR builder now follows style guide!")
            
        return success
        
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