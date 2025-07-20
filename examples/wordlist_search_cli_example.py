#!/usr/bin/env python3
"""
CLI Wordlist Search Example for Pygetpapers

This example demonstrates how to use the new CLI wordlist search functionality
to search datatables fields with specific words and flag papers with the highest hits.

AUTHOR: P. Murray-Rust with assistance from CursorAI (Claude Sonnet 4)
VERSION: 1.0.0
PURPOSE: Demonstrate CLI wordlist search functionality with climate examples
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Demonstrate CLI wordlist search functionality."""
    print("=" * 60)
    print("           Pygetpapers CLI Wordlist Search Example")
    print("=" * 60)
    print()

    # Example 1: Basic wordlist search in title only (default)
    print("📋 Example 1: Basic wordlist search in title only")
    print("Command: pygetpapers -q 'climate change AND adaptation' --api europe_pmc --limit 10 -x -p --fulltext_html --datatables --words 'climate' 'adaptation'")
    print()
    print("This will:")
    print("  - Search for 'climate change AND adaptation' papers")
    print("  - Download XML, PDF, and HTML files")
    print("  - Create datatables")
    print("  - Search for 'climate' and 'adaptation' in title field only")
    print("  - Flag papers with the highest hits")
    print()

    # Example 2: Search in multiple fields
    print("📋 Example 2: Search in multiple fields")
    print("Command: pygetpapers -q 'climate change AND adaptation' --api europe_pmc --limit 10 -x -p --fulltext_html --datatables --fields title abstract --words 'climate' 'adaptation' 'mitigation'")
    print()
    print("This will:")
    print("  - Search for 'climate change AND adaptation' papers")
    print("  - Download XML, PDF, and HTML files")
    print("  - Create datatables")
    print("  - Search for 'climate', 'adaptation', and 'mitigation' in title and abstract fields")
    print("  - Flag papers with the highest hits across both fields")
    print()

    # Example 3: Search in all available fields
    print("📋 Example 3: Search in all available fields")
    print("Command: pygetpapers -q 'climate change AND adaptation' --api europe_pmc --limit 10 -x -p --fulltext_html --datatables --fields title abstract authors journal keywords --words 'climate' 'adaptation' 'sustainability' 'carbon'")
    print()
    print("This will:")
    print("  - Search for 'climate change AND adaptation' papers")
    print("  - Download XML, PDF, and HTML files")
    print("  - Create datatables")
    print("  - Search for multiple climate terms in title, abstract, authors, journal, and keywords")
    print("  - Flag papers with the highest hits across all fields")
    print()

    # Example 4: Search with specific field combinations
    print("📋 Example 4: Search with specific field combinations")
    print("Command: pygetpapers -q 'climate change AND adaptation' --api europe_pmc --limit 10 -x -p --fulltext_html --datatables --fields abstract keywords --words 'daisy' 'bellis perennis'")
    print()
    print("This will:")
    print("  - Search for 'climate change AND adaptation' papers")
    print("  - Download XML, PDF, and HTML files")
    print("  - Create datatables")
    print("  - Search for 'daisy' and 'bellis perennis' in abstract and keywords only")
    print("  - Flag papers with the highest hits in these specific fields")
    print()

    # Available fields
    print("📋 Available search fields:")
    print("  - title: Paper title")
    print("  - abstract: Paper abstract")
    print("  - authors: Author names")
    print("  - journal: Journal name")
    print("  - keywords: Keywords/tags")
    print("  - doi: Digital Object Identifier")
    print("  - pmid: PubMed ID")
    print("  - pmcid: PubMed Central ID")
    print()

    # Output files
    print("📋 Output files created:")
    print("  - datatables.html: Combined datatables view")
    print("  - datatables_papers.html: Papers table with abstracts")
    print("  - datatables_metadata.html: Metadata information")
    print("  - datatables_summary.html: Summary statistics")
    print("  - wordlist_search_results.html: Wordlist search results (if --words provided)")
    print("  - wordlist_search_results.json: Search results in JSON format (if --words provided)")
    print()

    # Usage tips
    print("💡 Usage tips:")
    print("  - Use --fields to specify which fields to search (default: title)")
    print("  - Use --words to specify search terms")
    print("  - Search is case-insensitive by default")
    print("  - Papers are flagged if they have at least 1 hit (configurable)")
    print("  - Results are sorted by total hit count")
    print("  - Hit counts are stored for each term in each field")
    print()

    # Example execution
    print("🚀 To run an example:")
    print("1. Make sure you have pygetpapers installed")
    print("2. Run one of the commands above")
    print("3. Check the output directory for results")
    print("4. Open wordlist_search_results.html in your browser")
    print()

    # Note about abstracts
    print("📝 Note about abstracts:")
    print("  - Abstracts are now included in the main datatables papers table")
    print("  - If no abstract is available, 'No abstract available' is shown")
    print("  - Abstracts are truncated to 150 characters in the table")
    print("  - Full abstracts are available for searching")
    print()


if __name__ == "__main__":
    main() 