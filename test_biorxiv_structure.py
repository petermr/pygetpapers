#!/usr/bin/env python3
"""
Test script to analyze bioRxiv website structure and understand the search interface.
"""

import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import quote_plus


def analyze_biorxiv_structure():
    """Analyze the bioRxiv search page structure."""

    # Set up session
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    )

    # Test the search URL structure
    base_url = "https://www.biorxiv.org"

    # Try different search URL patterns
    search_patterns = [
        f"{base_url}/search",
        f"{base_url}/search/",
        f"{base_url}/search?q=",
        f"{base_url}/search?query=",
        f"{base_url}/search?search=",
    ]

    print("Testing bioRxiv search URL patterns...")

    for pattern in search_patterns:
        try:
            print(f"\nTrying: {pattern}")
            response = session.get(pattern, timeout=10)
            print(f"Status: {response.status_code}")
            print(f"URL: {response.url}")

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")

                # Look for search form
                search_form = soup.find("form")
                if search_form:
                    print(
                        f"Found search form: {search_form.get('action', 'No action')}"
                    )
                    print(f"Method: {search_form.get('method', 'No method')}")

                # Look for search input
                search_input = soup.find("input", {"type": "search"}) or soup.find(
                    "input", {"name": re.compile(r"q|query|search")}
                )
                if search_input:
                    print(f"Found search input: {search_input.get('name', 'No name')}")

                # Look for results container
                results_containers = soup.find_all(
                    ["div", "section", "main"],
                    class_=re.compile(r"result|search|paper|article"),
                )
                print(f"Found {len(results_containers)} potential results containers")

                # Save the HTML for inspection
                with open(
                    f"biorxiv_search_page_{pattern.split('/')[-1]}.html",
                    "w",
                    encoding="utf-8",
                ) as f:
                    f.write(response.text)
                print(
                    f"Saved HTML to biorxiv_search_page_{pattern.split('/')[-1]}.html"
                )

        except Exception as e:
            print(f"Error: {e}")

    # Try a specific search query
    print("\n" + "=" * 50)
    print("Testing with a specific search query...")

    query = "urban heat island"
    encoded_query = quote_plus(query)

    # Try different search URL patterns with query
    search_urls = [
        f"{base_url}/search/{encoded_query}",
        f"{base_url}/search?q={encoded_query}",
        f"{base_url}/search?query={encoded_query}",
        f"{base_url}/search?search={encoded_query}",
    ]

    for url in search_urls:
        try:
            print(f"\nTrying search URL: {url}")
            response = session.get(url, timeout=10)
            print(f"Status: {response.status_code}")
            print(f"Final URL: {response.url}")

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")

                # Look for paper entries
                paper_elements = soup.find_all(
                    ["article", "div", "section"],
                    class_=re.compile(r"paper|result|entry|article"),
                )
                print(f"Found {len(paper_elements)} potential paper elements")

                # Look for titles
                titles = soup.find_all(
                    ["h1", "h2", "h3", "h4"], class_=re.compile(r"title")
                )
                print(f"Found {len(titles)} potential title elements")

                # Look for DOIs
                doi_links = soup.find_all("a", href=re.compile(r"doi\.org"))
                print(f"Found {len(doi_links)} DOI links")

                # Look for pagination
                pagination = soup.find_all(
                    ["nav", "div"], class_=re.compile(r"pagination|page")
                )
                print(f"Found {len(pagination)} pagination elements")

                # Save the HTML for inspection
                filename = f"biorxiv_search_results_{url.split('/')[-1].replace('?', '_').replace('=', '_')}.html"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(response.text)
                print(f"Saved HTML to {filename}")

                # Try to extract some basic info
                if paper_elements:
                    print("\nSample paper elements found:")
                    for i, elem in enumerate(paper_elements[:3]):
                        print(f"\nPaper {i+1}:")
                        print(f"  Classes: {elem.get('class', [])}")
                        print(f"  ID: {elem.get('id', 'No ID')}")
                        print(f"  Text preview: {elem.get_text()[:200]}...")

        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    import re

    analyze_biorxiv_structure()
