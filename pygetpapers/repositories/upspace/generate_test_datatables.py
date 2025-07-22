#!/usr/bin/env python3
"""
Generate test DataTables files for UPSpace.
This script creates DataTables HTML files in a visible location for inspection.
"""

from pathlib import Path

from pygetpapers.repositories.upspace.upspace import UPSpace


def generate_test_datatables():
    """Generate test DataTables files."""
    
    print("=" * 60)
    print("Generating Test DataTables for UPSpace")
    print("=" * 60)
    
    # Create output directory in the current location
    output_dir = Path(__file__).parent / "test_output"
    output_dir.mkdir(exist_ok=True)
    
    print(f"Output directory: {output_dir.absolute()}")
    
    # Initialize UPSpace
    upspace = UPSpace()
    upspace.output_dir = str(output_dir)
    
    # Search for articles
    print("\nSearching for articles...")
    articles = upspace.search_articles("sustainable development", max_results=5)
    
    if not articles:
        print("No articles found!")
        return
    
    print(f"Found {len(articles)} articles")
    
    # Generate DataTables
    print("\nGenerating DataTables...")
    upspace._create_upspace_datatables_html(articles)
    
    # Check what files were created
    print("\nFiles created:")
    for file_path in output_dir.iterdir():
        if file_path.is_file():
            print(f"  📄 {file_path.name} ({file_path.stat().st_size} bytes)")
        elif file_path.is_dir():
            print(f"  📁 {file_path.name}/")
    
    # Show DataTables file content preview
    datatables_file = output_dir / "upspace_datatables.html"
    if datatables_file.exists():
        print(f"\n📄 DataTables file preview (first 500 chars):")
        with open(datatables_file, 'r', encoding='utf-8') as f:
            content = f.read()
            print("-" * 60)
            print(content[:500] + "..." if len(content) > 500 else content)
            print("-" * 60)
    
    # Show index file content preview
    index_file = output_dir / "index.html"
    if index_file.exists():
        print(f"\n📄 Index file preview (first 300 chars):")
        with open(index_file, 'r', encoding='utf-8') as f:
            content = f.read()
            print("-" * 60)
            print(content[:300] + "..." if len(content) > 300 else content)
            print("-" * 60)
    
    print(f"\n✅ Test DataTables generated successfully!")
    print(f"📁 Files are located in: {output_dir.absolute()}")
    print(f"🌐 You can open {index_file.name} in your browser to view the results")


if __name__ == "__main__":
    generate_test_datatables() 