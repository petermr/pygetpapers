#!/usr/bin/env python3
"""
Test Basic SciELO Implementation

This script tests the basic SciELO web scraper implementation
with climate change examples to verify functionality.
"""

import os
import sys
from pathlib import Path

import logging

from pygetpapers.repositories.scielo.scielo import SciELO

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_scielo_basic():
    """Test basic SciELO functionality."""

    logger.info("=== Testing Basic SciELO Implementation ===")

    # Initialize SciELO scraper
    scielo = SciELO()

    # Test 1: Basic search
    logger.info("Test 1: Basic search for 'climate change'")
    try:
        articles = scielo.search_articles("climate change", max_results=3)
        logger.info(f"✅ Found {len(articles)} articles")

        if articles:
            # Display first article details
            first_article = articles[0]
            logger.info(f"First article:")
            logger.info(f"  Title: {first_article.get('title', 'No title')}")
            logger.info(f"  Authors: {', '.join(first_article.get('authors', [])[:2])}")
            logger.info(f"  Collection: {first_article.get('collection', 'Unknown')}")
            logger.info(f"  DOI: {first_article.get('doi', 'No DOI')}")
            logger.info(f"  PDF URLs: {len(first_article.get('pdf_urls', []))}")
        else:
            logger.warning("❌ No articles found")

    except Exception as e:
        assert False, f"Test 1 failed: {e}"

    # Test 2: Main scielo method
    logger.info("Test 2: Main scielo method with CSV output")
    results = scielo.scielo(
        query="climate change", cutoff_size=2, makecsv=True, makehtml=True
    )
    assert isinstance(results, dict), "Results should be a dictionary"
    assert "total_results" in results, "Results should contain total_results"
    logger.info(
        f"✅ Main method completed. Found {results['total_results']} articles"
    )
    logger.info(f"✅ Generated CSV and HTML outputs")

    # Test 3: Noexecute method
    logger.info("Test 3: Noexecute method")
    query_namespace = {"query": "climate change", "limit": 2}
    assert hasattr(scielo, "noexecute"), "SciELO should have noexecute method"
    scielo.noexecute(query_namespace)
    logger.info("✅ Noexecute method completed")

    # Test 4: Article download
    logger.info("Test 4: Article download")
    if articles:
        # Download first article
        first_article_url = articles[0].get("url")
        if first_article_url:
            output_dir = "temp/scielo_test_downloads"
            assert hasattr(scielo, "download_article"), "SciELO should have download_article method"
            success = scielo.download_article(first_article_url, output_dir)
            if success:
                logger.info(f"✅ Article downloaded to {output_dir}")
            else:
                logger.warning("⚠️ Article download failed")
        else:
            logger.warning("⚠️ No article URL available for download test")
    else:
        logger.warning("⚠️ No articles available for download test")

    logger.info("=== All Basic Tests Completed ===")


def test_scielo_metadata_extraction():
    """Test metadata extraction from a known article."""

    logger.info("=== Testing Metadata Extraction ===")

    # Test with a known article URL from exploration
    test_url = "http://www.scielo.sa.cr/scielo.php?script=sci_arttext&pid=S2215-34702025000100067&lang=en"

    scielo = SciELO()

    try:
        # Get article page
        response = scielo._make_request(test_url)
        if response:
            # Extract metadata
            metadata = scielo._extract_article_metadata(response.text, test_url)

            logger.info("✅ Metadata extraction test completed")
            logger.info(f"  Title: {metadata.get('title', 'No title')[:100]}...")
            logger.info(f"  Authors: {len(metadata.get('authors', []))} authors found")
            logger.info(f"  Abstract: {len(metadata.get('abstract', ''))} characters")
            logger.info(f"  DOI: {metadata.get('doi', 'No DOI')}")
            logger.info(f"  PDF URLs: {len(metadata.get('pdf_urls', []))}")
            logger.info(f"  Collection: {metadata.get('collection', 'Unknown')}")
            
            assert metadata is not None, "Metadata should be extracted"
            assert isinstance(metadata, dict), "Metadata should be a dictionary"
        else:
            assert False, "Failed to get article page"

    except Exception as e:
        assert False, f"Metadata extraction test failed: {e}"


def main():
    """Main test function."""
    logger.info("Starting SciELO Basic Implementation Tests")

    # Test basic functionality
    basic_success = test_scielo_basic()

    # Test metadata extraction
    metadata_success = test_scielo_metadata_extraction()

    # Summary
    logger.info("=== Test Summary ===")
    logger.info(f"Basic functionality: {'✅ PASS' if basic_success else '❌ FAIL'}")
    logger.info(f"Metadata extraction: {'✅ PASS' if metadata_success else '❌ FAIL'}")

    if basic_success and metadata_success:
        logger.info("🎉 All tests passed! Basic SciELO implementation is working.")
        return True
    else:
        logger.error("❌ Some tests failed. Check implementation.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
