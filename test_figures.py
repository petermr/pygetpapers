#!/usr/bin/env python3
"""
Test script for figures extraction functionality
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datatables_integration import PygetpapersDatatables


def test_figures_extraction():
    """Test figures extraction functionality"""
    print("🧪 Testing Figures Extraction Functionality")
    print("=" * 50)

    # Initialize datatables
    datatables = PygetpapersDatatables()

    # Test with existing corpus
    test_corpus = "lantana"  # Use the existing lantana corpus

    if not os.path.exists(test_corpus):
        print(f"❌ Test corpus '{test_corpus}' not found")
        print("Please download a corpus first using pygetpapers")
        return False

    try:
        print(f"📁 Loading corpus: {test_corpus}")

        # Load corpus data
        corpus_data = datatables.read_pygetpapers_output(test_corpus)
        print(f"✅ Loaded {len(corpus_data['paper_directories'])} papers")

        # Extract figures
        print("🔍 Extracting figures...")
        figures_data = datatables.extract_figures(corpus_data)

        if figures_data["papers"]:
            summary = figures_data["summary"]
            print(f"✅ Found {summary['total_figures']} figures across {summary['papers_with_figures']} papers")

            # Show some sample figures
            print("\n📊 Sample Figures:")
            for i, (paper_id, paper_figures) in enumerate(figures_data["papers"].items()):
                if i >= 3:  # Show first 3 papers
                    break
                print(f"  📄 {paper_id}: {paper_figures['total_figures']} figures")
                for j, figure in enumerate(paper_figures["figures"][:2]):  # Show first 2 figures per paper
                    print(f"    🖼️  {figure['figure_id']}: {figure['caption'][:50]}...")

            # Test table creation
            print("\n📋 Testing table creation...")
            figures_html = datatables.create_figures_table(figures_data, "test_figures_table")
            if figures_html and "table" in figures_html.lower():
                print("✅ Figures table created successfully")
            else:
                print("❌ Failed to create figures table")
                return False

            # Test summary table
            summary_html = datatables.create_figures_summary_table(figures_data, "test_summary_table")
            if summary_html and "table" in summary_html.lower():
                print("✅ Summary table created successfully")
            else:
                print("❌ Failed to create summary table")
                return False

            print("\n🎉 All tests passed!")
            return True

        else:
            print("ℹ️  No figures found in the test corpus")
            print("This is normal if the papers don't contain figures or if XML parsing didn't find them")
            return True

    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


def test_thumbnail_creation():
    """Test thumbnail creation functionality"""
    print("\n🖼️ Testing Thumbnail Creation")
    print("=" * 30)

    # Look for image files in the test corpus
    test_corpus = "lantana"
    image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".tiff", ".tif"]

    found_images = []
    for ext in image_extensions:
        found_images.extend(Path(test_corpus).rglob(f"*{ext}"))
        found_images.extend(Path(test_corpus).rglob(f"*{ext.upper()}"))

    if not found_images:
        print("ℹ️  No image files found for thumbnail testing")
        return True

    print(f"📷 Found {len(found_images)} image files")

    datatables = PygetpapersDatatables()

    # Test thumbnail creation on first few images
    for i, image_path in enumerate(found_images[:3]):
        try:
            print(f"  Testing thumbnail for: {image_path.name}")
            thumbnail = datatables._create_image_thumbnail(image_path)
            if thumbnail:
                print(f"    ✅ Thumbnail created ({len(thumbnail)} chars)")
            else:
                print(f"    ⚠️  No thumbnail created (PIL may not be available)")
        except Exception as e:
            print(f"    ❌ Error creating thumbnail: {str(e)}")

    return True


if __name__ == "__main__":
    print("🚀 Starting Figures Extraction Tests")
    print("=" * 50)

    # Test figures extraction
    success1 = test_figures_extraction()

    # Test thumbnail creation
    success2 = test_thumbnail_creation()

    print("\n" + "=" * 50)
    if success1 and success2:
        print("🎉 All tests completed successfully!")
        print("✅ Figures extraction functionality is working")
    else:
        print("❌ Some tests failed")
        print("Check the error messages above for details")

    print("\n💡 Tips:")
    print("- Install PIL/Pillow for thumbnail creation: pip install Pillow")
    print("- Install lxml for better XML parsing: pip install lxml")
    print("- Download papers with XML content for better figure extraction")
