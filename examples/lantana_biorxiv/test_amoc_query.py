#!/usr/bin/env python3
"""
Test AMOC Query - Step by Step PDF URL Analysis

This script queries BioRxiv for "amoc" and downloads the HTML page of the first result
to understand the correct PDF URL structure.

Author: AI Assistant
Date: July 28, 2025 (system date of generation)
"""

import requests
import time
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

def query_biorxiv_amoc():
    """Query BioRxiv for 'amoc' and get the first result"""
    print("🔍 Querying BioRxiv for 'amoc'...")
    
    # Create session with realistic headers
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    })
    
    # Search URL
    search_url = f"https://www.biorxiv.org/search/{quote_plus('amoc')}"
    print(f"🌐 Searching: {search_url}")
    
    try:
        # Add delay to be respectful
        time.sleep(2)
        
        # Make the search request
        response = session.get(search_url, timeout=30)
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Search successful!")
            
            # Parse the search results
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for paper elements
            paper_elements = soup.find_all('div', class_='highwire-cite')
            print(f"📄 Found {len(paper_elements)} paper elements")
            
            if paper_elements:
                # Get the first paper
                first_paper = paper_elements[0]
                
                # Extract paper information
                title_elem = first_paper.find('a', class_='highwire-cite-title')
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    paper_url = title_elem.get('href', '')
                    
                    print(f"\n📋 First Paper Found:")
                    print(f"   Title: {title}")
                    print(f"   URL: {paper_url}")
                    
                    # Extract DOI from URL
                    if paper_url:
                        doi = paper_url.split('/')[-1]
                        full_doi = f"10.1101/{doi}"
                        print(f"   DOI: {full_doi}")
                        
                        # Download the paper's HTML page
                        download_paper_page(session, full_doi, title)
                    else:
                        print("❌ No paper URL found")
                else:
                    print("❌ No title element found")
            else:
                print("❌ No paper elements found")
                
        else:
            print(f"❌ Search failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error during search: {e}")

def download_paper_page(session, doi, title):
    """Download the HTML page of a specific paper"""
    print(f"\n📥 Downloading paper page for: {doi}")
    
    # Construct paper URL
    paper_url = f"https://www.biorxiv.org/content/{doi}"
    print(f"🌐 Paper URL: {paper_url}")
    
    try:
        # Add delay
        time.sleep(2)
        
        # Download the paper page
        response = session.get(paper_url, timeout=30)
        print(f"📊 Paper page response: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Paper page downloaded successfully!")
            
            # Save the HTML
            output_dir = Path("examples/lantana_biorxiv/amoc_test")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            html_file = output_dir / f"{doi.replace('/', '_')}_page.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            print(f"💾 HTML saved to: {html_file}")
            
            # Analyze the HTML for PDF links
            analyze_pdf_links(response.text, doi)
            
        else:
            print(f"❌ Failed to download paper page: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error downloading paper page: {e}")

def analyze_pdf_links(html_content, doi):
    """Analyze the HTML content for PDF links"""
    print(f"\n🔍 Analyzing PDF links in HTML...")
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Look for all PDF links
    pdf_links = soup.find_all("a", href=lambda href: href and ".pdf" in href)
    print(f"📄 Found {len(pdf_links)} PDF links:")
    
    for i, link in enumerate(pdf_links, 1):
        href = link.get("href", "")
        text = link.get_text(strip=True)
        print(f"   {i}. Text: '{text}' | Href: '{href}'")
    
    # Look for specific PDF patterns
    print(f"\n🔍 Looking for specific PDF patterns...")
    
    # Pattern 1: full.pdf
    full_pdf_links = soup.find_all("a", href=lambda href: href and "full.pdf" in href)
    print(f"   Full PDF links: {len(full_pdf_links)}")
    for link in full_pdf_links:
        print(f"     - {link.get('href', '')}")
    
    # Pattern 2: biorxiv in URL
    biorxiv_pdf_links = soup.find_all("a", href=lambda href: href and "biorxiv" in href and ".pdf" in href)
    print(f"   BioRxiv PDF links: {len(biorxiv_pdf_links)}")
    for link in biorxiv_pdf_links:
        print(f"     - {link.get('href', '')}")
    
    # Pattern 3: Any PDF link
    all_pdf_links = soup.find_all("a", href=lambda href: href and ".pdf" in href)
    print(f"   All PDF links: {len(all_pdf_links)}")
    for link in all_pdf_links:
        href = link.get("href", "")
        if href.startswith("/"):
            full_url = f"https://www.biorxiv.org{href}"
        elif href.startswith("http"):
            full_url = href
        else:
            full_url = f"https://www.biorxiv.org/{href}"
        print(f"     - {full_url}")

def main():
    """Main function"""
    print("🚀 Testing AMOC Query - Step by Step Analysis")
    print("=" * 50)
    
    query_biorxiv_amoc()
    
    print("\n" + "=" * 50)
    print("✅ Analysis Complete!")

if __name__ == "__main__":
    main() 