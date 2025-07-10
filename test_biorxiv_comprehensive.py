#!/usr/bin/env python3
"""
Comprehensive test script for the bioRxiv web scraper.

This script demonstrates all the functionality of the BioRxivWebScraper:
1. Basic search functionality
2. Pagination handling
3. Downloading individual paper HTML
4. Saving results to files
"""

import json
import logging
from pathlib import Path
from biorxiv_web_scraper import BioRxivWebScraper

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_basic_search():
    """Test basic search functionality."""
    print("=" * 60)
    print("TEST 1: Basic Search Functionality")
    print("=" * 60)
    
    scraper = BioRxivWebScraper()
    
    # Test search with different parameters
    query = "urban heat island"
    results = scraper.search_papers(
        query=query,
        max_results=5,
        results_per_page=10
    )
    
    if 'error' not in results:
        print(f"✅ Search successful!")
        print(f"   Query: {query}")
        print(f"   Found: {len(results['papers'])} papers")
        print(f"   Total pages: {results['pagination']['total_pages']}")
        
        # Display first few results
        for i, paper in enumerate(results['papers'][:3], 1):
            print(f"\n   {i}. {paper['title'][:80]}...")
            print(f"      DOI: {paper['doi']}")
            print(f"      Authors: {', '.join(paper['authors'][:3])}{'...' if len(paper['authors']) > 3 else ''}")
        
        return results
    else:
        print(f"❌ Search failed: {results['error']}")
        return None

def test_pagination():
    """Test pagination functionality."""
    print("\n" + "=" * 60)
    print("TEST 2: Pagination Functionality")
    print("=" * 60)
    
    scraper = BioRxivWebScraper()
    
    # Get first page
    query = "urban heat island"
    results = scraper.search_papers(query, max_results=10, results_per_page=10)
    
    if 'error' not in results:
        pagination = results['pagination']
        print(f"✅ First page loaded successfully!")
        print(f"   Current page: {pagination['current_page']}")
        print(f"   Total pages: {pagination['total_pages']}")
        print(f"   Has next: {pagination['has_next']}")
        
        # Try to get next page
        if pagination['has_next']:
            print(f"\n   Getting next page...")
            next_url = pagination['next_url']
            
            # Parse the next page
            next_results = scraper.search_papers(query, max_results=10, results_per_page=10)
            
            if 'error' not in next_results:
                print(f"✅ Next page loaded successfully!")
                print(f"   Next page papers: {len(next_results['papers'])}")
                
                # Show first paper from next page
                if next_results['papers']:
                    first_paper = next_results['papers'][0]
                    print(f"   First paper: {first_paper['title'][:80]}...")
            else:
                print(f"❌ Failed to load next page: {next_results['error']}")
        else:
            print(f"   No next page available")
        
        return results
    else:
        print(f"❌ Pagination test failed: {results['error']}")
        return None

def test_paper_download():
    """Test downloading individual paper HTML."""
    print("\n" + "=" * 60)
    print("TEST 3: Paper HTML Download")
    print("=" * 60)
    
    scraper = BioRxivWebScraper()
    
    # Get a sample paper
    query = "urban heat island"
    results = scraper.search_papers(query, max_results=1)
    
    if 'error' not in results and results['papers']:
        paper = results['papers'][0]
        doi = paper['doi']
        
        print(f"✅ Testing download for paper:")
        print(f"   Title: {paper['title']}")
        print(f"   DOI: {doi}")
        
        # Download HTML
        output_dir = "biorxiv_downloads"
        html_path = scraper.download_paper_html(doi, output_dir)
        
        if html_path:
            print(f"✅ HTML downloaded successfully!")
            print(f"   Path: {html_path}")
            
            # Check file size
            file_size = Path(html_path).stat().st_size
            print(f"   File size: {file_size:,} bytes")
            
            return html_path
        else:
            print(f"❌ HTML download failed")
            return None
    else:
        print(f"❌ No papers found for download test")
        return None

def test_paper_details():
    """Test getting detailed paper information."""
    print("\n" + "=" * 60)
    print("TEST 4: Paper Details Extraction")
    print("=" * 60)
    
    scraper = BioRxivWebScraper()
    
    # Test with a known DOI
    test_doi = "10.1101/2023.11.10.566554"
    
    print(f"✅ Getting details for DOI: {test_doi}")
    
    details = scraper.get_paper_details(test_doi)
    
    if details:
        print(f"✅ Paper details extracted successfully!")
        print(f"   Title: {details.get('title', 'No title')}")
        print(f"   Authors: {details.get('authors', 'No authors')}")
        print(f"   Abstract: {details.get('abstract', 'No abstract')[:100]}...")
        print(f"   PDF URL: {details.get('pdf_url', 'No PDF')}")
        
        return details
    else:
        print(f"❌ Failed to get paper details")
        return None

def test_save_and_load():
    """Test saving and loading results."""
    print("\n" + "=" * 60)
    print("TEST 5: Save and Load Results")
    print("=" * 60)
    
    scraper = BioRxivWebScraper()
    
    # Perform search
    query = "urban heat island"
    results = scraper.search_papers(query, max_results=3)
    
    if 'error' not in results:
        # Save results
        output_dir = "biorxiv_test_output"
        saved_path = scraper.save_results(results, output_dir, "test_results.json")
        
        if saved_path:
            print(f"✅ Results saved to: {saved_path}")
            
            # Load and verify
            try:
                with open(saved_path, 'r', encoding='utf-8') as f:
                    loaded_results = json.load(f)
                
                print(f"✅ Results loaded successfully!")
                print(f"   Papers in saved file: {len(loaded_results['papers'])}")
                print(f"   Search query: {loaded_results['search_query']}")
                
                return saved_path
            except Exception as e:
                print(f"❌ Failed to load saved results: {e}")
                return None
        else:
            print(f"❌ Failed to save results")
            return None
    else:
        print(f"❌ Search failed: {results['error']}")
        return None

def test_different_queries():
    """Test different search queries."""
    print("\n" + "=" * 60)
    print("TEST 6: Different Search Queries")
    print("=" * 60)
    
    scraper = BioRxivWebScraper()
    
    test_queries = [
        "urban heat island",
        "climate change",
        "machine learning",
        "covid-19"
    ]
    
    results_summary = {}
    
    for query in test_queries:
        print(f"\n   Testing query: '{query}'")
        
        results = scraper.search_papers(query, max_results=5)
        
        if 'error' not in results:
            count = len(results['papers'])
            total_pages = results['pagination']['total_pages']
            print(f"   ✅ Found {count} papers, {total_pages} total pages")
            results_summary[query] = {
                'papers_found': count,
                'total_pages': total_pages
            }
        else:
            print(f"   ❌ Failed: {results['error']}")
            results_summary[query] = {'error': results['error']}
    
    print(f"\n📊 Summary:")
    for query, summary in results_summary.items():
        if 'error' not in summary:
            print(f"   '{query}': {summary['papers_found']} papers, {summary['total_pages']} pages")
        else:
            print(f"   '{query}': ERROR - {summary['error']}")
    
    return results_summary

def main():
    """Run all tests."""
    print("🧪 BioRxiv Web Scraper - Comprehensive Test Suite")
    print("=" * 60)
    
    # Create output directories
    Path("biorxiv_test_output").mkdir(exist_ok=True)
    Path("biorxiv_downloads").mkdir(exist_ok=True)
    
    # Run tests
    test_results = {}
    
    try:
        test_results['basic_search'] = test_basic_search()
        test_results['pagination'] = test_pagination()
        test_results['paper_download'] = test_paper_download()
        test_results['paper_details'] = test_paper_details()
        test_results['save_load'] = test_save_and_load()
        test_results['different_queries'] = test_different_queries()
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS COMPLETED!")
        print("=" * 60)
        
        # Summary
        successful_tests = sum(1 for result in test_results.values() if result is not None)
        total_tests = len(test_results)
        
        print(f"✅ Successful tests: {successful_tests}/{total_tests}")
        
        if successful_tests == total_tests:
            print("🎯 All tests passed! The bioRxiv scraper is working correctly.")
        else:
            print("⚠️  Some tests failed. Check the output above for details.")
        
    except Exception as e:
        print(f"❌ Test suite failed with error: {e}")
        logger.exception("Test suite error")

if __name__ == "__main__":
    main() 