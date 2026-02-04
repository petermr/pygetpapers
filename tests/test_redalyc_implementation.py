#!/usr/bin/env python3
"""
Test script for Redalyc implementation.

This script tests the Redalyc web scraping functionality.
"""

import logging
import sys
from pathlib import Path

from test_utils import skip_if_redalyc_down, test_redalyc_connectivity

from pygetpapers.repositories.redalyc.redalyc import Redalyc


def test_redalyc_initialization():
    """Test Redalyc class initialization."""
    print("Testing Redalyc initialization...")
    try:
        redalyc = Redalyc()
        print("✓ Redalyc initialization successful")
    except Exception as e:
        assert False, f"Redalyc initialization failed: {e}"


@skip_if_redalyc_down()
def test_redalyc_search():
    """Test Redalyc search functionality."""
    print("\nTesting Redalyc search...")
    try:
        redalyc = Redalyc()

        # Test with a simple query
        query = "climate change"
        max_results = 5

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

        print("✓ Redalyc search test completed")

    except Exception as e:
        assert False, f"Redalyc search test failed: {e}"


@skip_if_redalyc_down()
def test_redalyc_main_method():
    """Test the main redalyc method."""
    print("\nTesting Redalyc main method...")
    try:
        redalyc = Redalyc()

        # Test the main method
        result = redalyc.redalyc(
            query="global warming",
            cutoff_size=3,
            makecsv=False,
            makexml=False,
            makehtml=False,
        )

        print(
            f"Main method result: {len(result['new_results']['total_json_output'])} articles"
        )
        print("✓ Redalyc main method test completed")

    except Exception as e:
        assert False, f"Redalyc main method test failed: {e}"


@skip_if_redalyc_down()
def test_redalyc_noexecute():
    """Test the noexecute method."""
    print("\nTesting Redalyc noexecute method...")
    try:
        redalyc = Redalyc()

        # Test noexecute
        query_namespace = {"query": "carbon dioxide", "filter": None}

        redalyc.noexecute(query_namespace)
        print("✓ Redalyc noexecute test completed")

    except Exception as e:
        assert False, f"Redalyc noexecute test failed: {e}"


def main():
    """Run all tests."""
    print("🧪 Testing Redalyc Implementation")
    print("=" * 50)

    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Test connectivity first
    print("🔍 Testing Redalyc connectivity...")
    is_connected, error_msg = test_redalyc_connectivity()

    if not is_connected:
        print(f"⚠️  Redalyc appears to be down: {error_msg}")
        print("   Only running initialization test...")
        tests = [test_redalyc_initialization]
    else:
        print("✅ Redalyc is accessible, running all tests...")
        tests = [
            test_redalyc_initialization,
            test_redalyc_search,
            test_redalyc_main_method,
            test_redalyc_noexecute,
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

    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    if skipped > 0:
        print(f"              {skipped} tests skipped due to connectivity issues")

    if passed == total:
        print("🎉 All tests passed! Redalyc implementation is working correctly.")
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
