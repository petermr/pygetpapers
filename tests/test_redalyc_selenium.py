#!/usr/bin/env python3
"""
Test script for Redalyc Selenium implementation.

This script tests the Selenium-based Redalyc web scraping functionality.
Note: This requires Chrome browser and ChromeDriver to be installed.
"""

import logging
import sys
from pathlib import Path

from test_utils import skip_if_redalyc_down, test_redalyc_connectivity

from pygetpapers.repositories.redalyc.redalyc_selenium import RedalycSelenium


def test_redalyc_selenium_initialization():
    """Test RedalycSelenium class initialization."""
    print("Testing RedalycSelenium initialization...")
    try:
        redalyc = RedalycSelenium(headless=True)
        print("✓ RedalycSelenium initialization successful")
        redalyc.close()
    except Exception as e:
        assert False, f"RedalycSelenium initialization failed: {e}"


@skip_if_redalyc_down()
def test_redalyc_selenium_search():
    """Test RedalycSelenium search functionality."""
    print("\nTesting RedalycSelenium search...")
    try:
        redalyc = RedalycSelenium(headless=True)

        # Test with a simple query
        query = "climate change"
        max_results = 3

        print(f"Searching for: '{query}' (max {max_results} results)")
        articles = redalyc.search_articles(query, max_results)

        print(f"Found {len(articles)} articles")

        if articles:
            print("Sample article metadata:")
            article = articles[0]
            for key, value in article.items():
                if isinstance(value, list):
                    print(f"  {key}: {len(value)} items")
                else:
                    print(f"  {key}: {str(value)[:100]}...")

        redalyc.close()
        print("✓ RedalycSelenium search test completed")

    except Exception as e:
        if "redalyc" in locals():
            redalyc.close()
        assert False, f"RedalycSelenium search test failed: {e}"


@skip_if_redalyc_down()
def test_redalyc_selenium_main_method():
    """Test the main redalyc method with Selenium."""
    print("\nTesting RedalycSelenium main method...")
    try:
        redalyc = RedalycSelenium(headless=True)

        # Test the main method
        result = redalyc.redalyc(
            query="global warming",
            cutoff_size=2,
            makecsv=False,
            makexml=False,
            makehtml=False,
        )

        print(
            f"Main method result: {len(result['new_results']['total_json_output'])} articles"
        )

        redalyc.close()
        print("✓ RedalycSelenium main method test completed")

    except Exception as e:
        if "redalyc" in locals():
            redalyc.close()
        assert False, f"RedalycSelenium main method test failed: {e}"


@skip_if_redalyc_down()
def test_redalyc_selenium_noexecute():
    """Test the noexecute method with Selenium."""
    print("\nTesting RedalycSelenium noexecute method...")
    try:
        redalyc = RedalycSelenium(headless=True)

        # Test noexecute
        query_namespace = {"query": "carbon dioxide", "filter": None}

        redalyc.noexecute(query_namespace)

        redalyc.close()
        print("✓ RedalycSelenium noexecute test completed")

    except Exception as e:
        if "redalyc" in locals():
            redalyc.close()
        assert False, f"RedalycSelenium noexecute test failed: {e}"


def main():
    """Run all tests."""
    print("🧪 Testing Redalyc Selenium Implementation")
    print("=" * 60)

    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Test connectivity first
    print("🔍 Testing Redalyc connectivity...")
    is_connected, error_msg = test_redalyc_connectivity()

    if not is_connected:
        print(f"⚠️  Redalyc appears to be down: {error_msg}")
        print("   Only running initialization test...")
        tests = [test_redalyc_selenium_initialization]
    else:
        print("✅ Redalyc is accessible, running all tests...")
        tests = [
            test_redalyc_selenium_initialization,
            test_redalyc_selenium_search,
            test_redalyc_selenium_main_method,
            test_redalyc_selenium_noexecute,
        ]

    passed = 0
    total = len(tests)
    skipped = 0

    for test in tests:
        result = test()
        if result is True:
            passed += 1
        elif result is False:
            pass  # Already counted in total
        else:
            # Special case for skipped tests
            skipped += 1

    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    if skipped > 0:
        print(f"              {skipped} tests skipped due to connectivity issues")

    if passed == total:
        print(
            "🎉 All tests passed! Redalyc Selenium implementation is working correctly."
        )
    elif passed + skipped == total:
        print(
            "✅ All accessible tests passed! Some tests were skipped due to connectivity."
        )
    else:
        print("⚠️  Some tests failed. Check the implementation.")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
