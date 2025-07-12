#!/usr/bin/env python3
"""
Test script for Redalyc implementation.

This script tests the Redalyc web scraping functionality.
"""

import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pygetpapers.redalyc import Redalyc


def test_redalyc_initialization():
    """Test Redalyc class initialization."""
    print("Testing Redalyc initialization...")
    try:
        redalyc = Redalyc()
        print("✓ Redalyc initialization successful")
        return True
    except Exception as e:
        print(f"✗ Redalyc initialization failed: {e}")
        return False


def test_redalyc_search():
    """Test Redalyc search functionality."""
    print("\nTesting Redalyc search...")
    try:
        redalyc = Redalyc()
        
        # Test with a simple query
        query = "machine learning"
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
        return True
        
    except Exception as e:
        print(f"✗ Redalyc search test failed: {e}")
        return False


def test_redalyc_main_method():
    """Test the main redalyc method."""
    print("\nTesting Redalyc main method...")
    try:
        redalyc = Redalyc()
        
        # Test the main method
        result = redalyc.redalyc(
            query="artificial intelligence",
            cutoff_size=3,
            makecsv=False,
            makexml=False,
            makehtml=False
        )
        
        print(f"Main method result: {len(result['new_results']['total_json_output'])} articles")
        print("✓ Redalyc main method test completed")
        return True
        
    except Exception as e:
        print(f"✗ Redalyc main method test failed: {e}")
        return False


def test_redalyc_noexecute():
    """Test the noexecute method."""
    print("\nTesting Redalyc noexecute method...")
    try:
        redalyc = Redalyc()
        
        # Test noexecute
        query_namespace = {
            "query": "data science",
            "filter": None
        }
        
        redalyc.noexecute(query_namespace)
        print("✓ Redalyc noexecute test completed")
        return True
        
    except Exception as e:
        print(f"✗ Redalyc noexecute test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🧪 Testing Redalyc Implementation")
    print("=" * 50)
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    tests = [
        test_redalyc_initialization,
        test_redalyc_search,
        test_redalyc_main_method,
        test_redalyc_noexecute,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Redalyc implementation is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the implementation.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 