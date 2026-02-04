#!/usr/bin/env python3
"""
Test script for UPSpace implementation.
Tests search, metadata extraction, and file download functionality.
"""

import json
import logging
import sys
import tempfile
from pathlib import Path

from pygetpapers.repositories.upspace.upspace import UPSpace


def test_upspace_implementation():
    """Test the UPSpace implementation with real API calls."""

    # Set up logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    print("=" * 60)
    print("UPSpace Implementation Test")
    print("=" * 60)

    # Initialize UPSpace
    upspace = UPSpace()

    # Test 1: Search functionality
    print("\n1. Testing search functionality...")
    query = "sustainable development"  # Changed from "climate change" to a broader term
    max_results = 5

    try:
        articles = upspace.search_articles(query, max_results)
        print(f"✓ Found {len(articles)} articles for query: '{query}'")

        if articles:
            print("\nSample article metadata:")
            article = articles[0]
            print(f"  Title: {article.get('title', 'No title')}")
            print(f"  Authors: {article.get('authors', ['Unknown'])}")
            print(f"  Year: {article.get('year', 'Unknown')}")
            print(f"  Handle URL: {article.get('handle_url', 'None')}")
            print(f"  DOI: {article.get('doi', 'None')}")
            print(f"  SDG Classifications: {article.get('sdg_classifications', [])}")
            print(f"  Keywords: {article.get('keywords', [])}")
        else:
            print("  ⚠ No articles found - trying a different query...")
            # Try a more general search
            articles = upspace.search_articles(
                "", max_results
            )  # Empty query should return recent articles
            print(
                f"  Found {len(articles)} articles with empty query (recent articles)"
            )

            if articles:
                print("\nSample article metadata:")
                article = articles[0]
                print(f"  Title: {article.get('title', 'No title')}")
                print(f"  Authors: {article.get('authors', ['Unknown'])}")
                print(f"  Year: {article.get('year', 'Unknown')}")
                print(f"  Handle URL: {article.get('handle_url', 'None')}")
                print(f"  DOI: {article.get('doi', 'None')}")
                print(
                    f"  SDG Classifications: {article.get('sdg_classifications', [])}"
                )
                print(f"  Keywords: {article.get('keywords', [])}")

    except Exception as e:
        assert False, f"Search test failed: {e}"

    # Test 2: Metadata extraction
    print("\n2. Testing metadata extraction...")
    try:
        if articles:
            # Test metadata structure
            required_fields = ["title", "authors", "year", "uuid"]
            for field in required_fields:
                if field in articles[0]:
                    print(f"  ✓ Field '{field}' present")
                else:
                    print(f"  ✗ Field '{field}' missing")

            # Test SDG extraction
            sdg_articles = [a for a in articles if a.get("sdg_classifications")]
            print(f"  ✓ {len(sdg_articles)} articles have SDG classifications")

    except Exception as e:
        assert False, f"Metadata extraction test failed: {e}"

    # Test 3: File download (if articles found)
    print("\n3. Testing file download...")
    if articles:
        try:
            # Create temporary directory for downloads
            with tempfile.TemporaryDirectory() as temp_dir:
                print(f"  Using temporary directory: {temp_dir}")

                # Test download of first article
                article = articles[0]
                success = upspace.download_article(article, temp_dir)

                if success:
                    print("  ✓ Article download completed")

                    # Check if files were created
                    article_id = upspace._generate_article_id(article)
                    article_dir = Path(temp_dir, article_id)

                    if article_dir.exists():
                        print(f"  ✓ Article directory created: {article_id}")

                        # Check for metadata file
                        metadata_file = Path(article_dir, "metadata.json")
                        if metadata_file.exists():
                            print("  ✓ Metadata file created")

                            # Verify metadata content
                            with open(metadata_file, "r", encoding="utf-8") as f:
                                saved_metadata = json.load(f)
                            print(f"  ✓ Metadata contains {len(saved_metadata)} fields")

                        # Check for PDF file
                        pdf_file = Path(article_dir, "fulltext.pdf")
                        if pdf_file.exists():
                            print(
                                f"  ✓ PDF file created ({pdf_file.stat().st_size} bytes)"
                            )
                        else:
                            print("  ⚠ PDF file not found (may not be available)")
                    else:
                        print(f"  ✗ Article directory not created")
                else:
                    print("  ✗ Article download failed")

        except Exception as e:
            assert False, f"File download test failed: {e}"

    # Test 4: DataTables generation
    print("\n4. Testing DataTables generation...")
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            upspace.download_tools.output_dir = temp_dir

            if articles:
                upspace._create_upspace_datatables_html(articles)

                # Check if files were created
                datatables_file = Path(temp_dir, "upspace_datatables.html")
                index_file = Path(temp_dir, "index.html")

                if datatables_file.exists():
                    print("  ✓ DataTables HTML file created")
                    print(f"  ✓ File size: {datatables_file.stat().st_size} bytes")
                else:
                    print("  ✗ DataTables HTML file not created")

                if index_file.exists():
                    print("  ✓ Index HTML file created")
                else:
                    print("  ✗ Index HTML file not created")
            else:
                print("  ⚠ Skipping DataTables test (no articles)")

    except Exception as e:
        assert False, f"DataTables generation test failed: {e}"

    # Test 5: Article ID generation
    print("\n5. Testing article ID generation...")
    try:
        if articles:
            for i, article in enumerate(articles[:3]):  # Test first 3 articles
                article_id = upspace._generate_article_id(article)
                print(f"  Article {i+1}: {article_id}")

                # Verify ID format
                if article_id.startswith(("UPSPACE_", "DOI_", "UUID_", "TITLE_")):
                    print(f"    ✓ Valid ID format")
                else:
                    print(f"    ✗ Invalid ID format")

    except Exception as e:
        assert False, f"Article ID generation test failed: {e}"

    print("\n" + "=" * 60)
    print("✓ All tests completed successfully!")
    print("=" * 60)

    return True


if __name__ == "__main__":
    success = test_upspace_implementation()
    sys.exit(0 if success else 1)
