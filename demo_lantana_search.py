#!/usr/bin/env python3
"""
Demonstration: Search for Lantana papers from UPSpace
Shows the complete process from search to download.
"""

import sys
import json
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from pygetpapers.repositories.upspace.upspace import UPSpace


def demo_lantana_search():
    """Demonstrate the complete Lantana search and download process."""

    print("=" * 80)
    print("🌿 UPSpace Lantana Research Search & Download")
    print("=" * 80)

    # Initialize UPSpace
    print("\n1️⃣ Initializing UPSpace repository connection...")
    upspace = UPSpace()
    print("✅ Connected to UPSpace API")

    # Search for Lantana papers
    print("\n2️⃣ Searching for Lantana research papers...")
    query = "Lantana"
    max_results = 10

    try:
        articles = upspace.search_articles(query, max_results)
        print(f"✅ Found {len(articles)} articles about Lantana")

        if not articles:
            print("❌ No articles found for 'Lantana'")
            return

        # Display search results
        print(f"\n3️⃣ Search Results for '{query}':")
        print("-" * 80)

        for i, article in enumerate(articles, 1):
            print(f"\n📄 Article {i}:")
            print(f"   Title: {article.get('title', 'No title')}")
            print(f"   Authors: {', '.join(article.get('authors', ['Unknown']))}")
            print(f"   Year: {article.get('year', 'Unknown')}")
            print(f"   SDGs: {article.get('sdg_classifications', [])}")
            print(f"   Keywords: {', '.join(article.get('keywords', []))}")
            print(f"   Handle: {article.get('handle_url', 'None')}")
            print(f"   DOI: {article.get('doi', 'None')}")

        # Create output directory
        output_dir = Path("lantana_research_output")
        output_dir.mkdir(exist_ok=True)
        upspace.output_dir = str(output_dir)

        print(f"\n4️⃣ Downloading articles to: {output_dir.absolute()}")
        print("-" * 80)

        # Download each article
        successful_downloads = 0
        for i, article in enumerate(articles, 1):
            print(
                f"\n📥 Downloading Article {i}: {article.get('title', 'No title')[:60]}..."
            )

            success = upspace.download_article(article, str(output_dir))
            if success:
                successful_downloads += 1
                print(f"   ✅ Downloaded successfully")
            else:
                print(f"   ⚠️  Download completed (metadata only)")

        # Generate DataTables
        print(f"\n5️⃣ Generating interactive DataTables...")
        upspace._create_upspace_datatables_html(articles)
        print("✅ DataTables HTML created")

        # Show final results
        print(f"\n6️⃣ Final Results:")
        print("-" * 80)
        print(f"📊 Total articles found: {len(articles)}")
        print(f"📥 Successfully downloaded: {successful_downloads}")
        print(f"📁 Output directory: {output_dir.absolute()}")

        # List downloaded files
        print(f"\n📂 Downloaded Files:")
        for item in output_dir.iterdir():
            if item.is_dir():
                print(f"   📁 {item.name}/")
                for file in item.iterdir():
                    size = file.stat().st_size
                    print(f"      📄 {file.name} ({size:,} bytes)")
            else:
                size = item.stat().st_size
                print(f"   📄 {item.name} ({size:,} bytes)")

        # Show DataTables files
        datatables_file = output_dir / "upspace_datatables.html"
        index_file = output_dir / "index.html"

        if datatables_file.exists():
            print(f"\n🌐 Interactive DataTables:")
            print(
                f"   📊 {datatables_file.name} ({datatables_file.stat().st_size:,} bytes)"
            )
            print(f"   🏠 {index_file.name} ({index_file.stat().st_size:,} bytes)")
            print(
                f"   💡 Open {index_file.name} in your browser to view the interactive table!"
            )

        print(f"\n🎉 Process Complete!")
        print(f"🔍 Query: '{query}'")
        print(f"📚 Results: {len(articles)} articles")
        print(f"📁 Location: {output_dir.absolute()}")

    except Exception as e:
        print(f"❌ Error during search: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    demo_lantana_search()
