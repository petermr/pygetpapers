#!/usr/bin/env python3
"""
Test SciELO Article Page Structure

This script tests one of the discovered article URLs to understand
the structure of individual article pages.
"""

import requests
import time
from bs4 import BeautifulSoup
from pathlib import Path
import json

def test_article_page():
    """Test a specific SciELO article page."""
    
    # Test article URL from exploration
    article_url = "http://www.scielo.sa.cr/scielo.php?script=sci_arttext&pid=S2215-34702025000100067&lang=en"
    
    # Set up session with proper headers
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    })
    
    print(f"Testing article URL: {article_url}")
    
    # Make request
    response = session.get(article_url, timeout=30)
    print(f"Response status: {response.status_code}")
    
    if response.status_code == 200:
        # Save the response
        output_dir = Path('temp/scielo_exploration')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_dir / 'test_article_page.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"Saved article page to: {output_dir / 'test_article_page.html'}")
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract metadata
        metadata = extract_article_metadata(soup, article_url)
        print(f"Extracted metadata: {json.dumps(metadata, indent=2)}")
        
        # Find download links
        download_links = find_download_links(soup)
        print(f"Download links found: {len(download_links)}")
        for link_type, url in download_links:
            print(f"  {link_type}: {url}")
        
        # Save metadata
        with open(output_dir / 'test_article_metadata.json', 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        print(f"Saved metadata to: {output_dir / 'test_article_metadata.json'}")
        
        return metadata, download_links
    else:
        print(f"Failed to access article page: {response.status_code}")
        return None, []

def extract_article_metadata(soup, url):
    """Extract metadata from article page."""
    metadata = {
        'url': url,
        'title': None,
        'authors': [],
        'abstract': None,
        'journal': None,
        'year': None,
        'doi': None,
        'language': None,
        'keywords': [],
        'volume': None,
        'issue': None,
        'pages': None
    }
    
    # Title extraction - try multiple selectors
    title_selectors = [
        'h1.title',
        '.title',
        'h1',
        '.article-title',
        'title',
        '.documentTitle',
        '[class*="title"]'
    ]
    
    for selector in title_selectors:
        title_elem = soup.select_one(selector)
        if title_elem:
            title_text = title_elem.get_text(strip=True)
            if title_text and len(title_text) > 5:
                metadata['title'] = title_text
                break
    
    # Authors extraction
    author_selectors = [
        '.authors',
        '.author',
        '.byline',
        '[class*="author"]',
        '.contribGroup',
        '.contrib'
    ]
    
    for selector in author_selectors:
        author_elems = soup.select(selector)
        for elem in author_elems:
            author_text = elem.get_text(strip=True)
            if author_text and len(author_text) > 2 and author_text not in metadata['authors']:
                metadata['authors'].append(author_text)
    
    # Abstract extraction
    abstract_selectors = [
        '.abstract',
        '.resumo',
        '.summary',
        '[class*="abstract"]',
        '.abstractIn',
        '.abstractContent'
    ]
    
    for selector in abstract_selectors:
        abstract_elem = soup.select_one(selector)
        if abstract_elem:
            metadata['abstract'] = abstract_elem.get_text(strip=True)
            break
    
    # Journal extraction
    journal_selectors = [
        '.journal',
        '.periodical',
        '.publication',
        '[class*="journal"]',
        '.journalTitle',
        '.source'
    ]
    
    for selector in journal_selectors:
        journal_elem = soup.select_one(selector)
        if journal_elem:
            metadata['journal'] = journal_elem.get_text(strip=True)
            break
    
    # DOI extraction
    doi_selectors = [
        '[class*="doi"]',
        '.doi',
        'a[href*="doi.org"]',
        '[id*="doi"]'
    ]
    
    for selector in doi_selectors:
        doi_elem = soup.select_one(selector)
        if doi_elem:
            doi_text = doi_elem.get_text(strip=True)
            if 'doi' in doi_text.lower():
                metadata['doi'] = doi_text
                break
    
    # Keywords extraction
    keyword_selectors = [
        '.keywords',
        '.keyWords',
        '[class*="keyword"]',
        '.subject',
        '.descriptors'
    ]
    
    for selector in keyword_selectors:
        keyword_elems = soup.select(selector)
        for elem in keyword_elems:
            keyword_text = elem.get_text(strip=True)
            if keyword_text and len(keyword_text) > 2:
                metadata['keywords'].append(keyword_text)
    
    return metadata

def find_download_links(soup):
    """Find download links for PDF, HTML, XML."""
    download_links = []
    
    # Look for PDF links
    pdf_selectors = [
        'a[href*=".pdf"]',
        'a[href*="/pdf/"]',
        'a[href*="script=sci_pdf"]',
        '.pdf-link a',
        'a[title*="PDF"]',
        'a[href*="format=pdf"]'
    ]
    
    for selector in pdf_selectors:
        links = soup.select(selector)
        for link in links:
            href = link.get('href')
            if href:
                if not href.startswith('http'):
                    href = f"http://www.scielo.sa.cr{href}"
                download_links.append(('PDF', href))
    
    # Look for HTML links
    html_selectors = [
        'a[href*="format=html"]',
        'a[href*="/html/"]',
        '.html-link a',
        'a[title*="HTML"]',
        'a[href*="script=sci_arttext"]'
    ]
    
    for selector in html_selectors:
        links = soup.select(selector)
        for link in links:
            href = link.get('href')
            if href:
                if not href.startswith('http'):
                    href = f"http://www.scielo.sa.cr{href}"
                download_links.append(('HTML', href))
    
    # Look for XML links
    xml_selectors = [
        'a[href*=".xml"]',
        'a[href*="format=xml"]',
        '.xml-link a',
        'a[title*="XML"]'
    ]
    
    for selector in xml_selectors:
        links = soup.select(selector)
        for link in links:
            href = link.get('href')
            if href:
                if not href.startswith('http'):
                    href = f"http://www.scielo.sa.cr{href}"
                download_links.append(('XML', href))
    
    return download_links

if __name__ == "__main__":
    test_article_page() 