"""
BioRxiv Web Scraper - Proof of Concept

This module demonstrates how bioRxiv's web-based search interface could be scraped
to provide text-based search functionality, complementing the existing API-based
date-only search in pygetpapers.

The web search interface at https://www.biorxiv.org/search/ supports text queries
and returns results in a paginated format, unlike the API which only supports
date-based searches.
"""

import json
import logging
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote_plus, urljoin

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class BioRxivWebScraper:
    """
    Web scraper for bioRxiv's search interface.
    
    This provides text-based search functionality that complements the existing
    API-based date-only search in pygetpapers.
    """

    def __init__(self):
        self.base_url = "https://www.biorxiv.org"
        self.search_url = f"{self.base_url}/search"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def search_papers(
        self, 
        query: str, 
        max_results: int = 100,
        subject_area: Optional[str] = None,
        article_type: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search bioRxiv papers using the web interface.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            subject_area: Filter by subject area (e.g., "Ecology", "Neuroscience")
            article_type: Filter by article type (e.g., "Research Article", "Review")
            date_from: Start date in YYYY-MM-DD format
            date_to: End date in YYYY-MM-DD format
            
        Returns:
            Dictionary containing search results and metadata
        """
        logger.info(f"Searching bioRxiv for: {query}")
        
        # Build search URL
        encoded_query = quote_plus(query)
        search_url = f"{self.search_url}/{encoded_query}"
        
        # Add filters if provided
        params = {}
        if subject_area:
            params['subject_area'] = subject_area
        if article_type:
            params['article_type'] = article_type
        if date_from:
            params['date_from'] = date_from
        if date_to:
            params['date_to'] = date_to
            
        try:
            response = self.session.get(search_url, params=params, timeout=30)
            response.raise_for_status()
            
            # Parse the search results page
            results = self._parse_search_results(response.text, max_results)
            
            # Add metadata
            results['search_query'] = query
            results['search_url'] = response.url
            results['total_found'] = len(results['papers'])
            results['search_timestamp'] = datetime.now().isoformat()
            
            logger.info(f"Found {len(results['papers'])} papers for query: {query}")
            return results
            
        except requests.RequestException as e:
            logger.error(f"Error searching bioRxiv: {e}")
            return {
                'error': str(e),
                'papers': [],
                'search_query': query,
                'total_found': 0
            }

    def _parse_search_results(self, html_content: str, max_results: int) -> Dict[str, Any]:
        """
        Parse the HTML search results page.
        
        Args:
            html_content: HTML content of the search results page
            max_results: Maximum number of results to parse
            
        Returns:
            Dictionary containing parsed papers and pagination info
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        papers = []
        
        # Find the search results container
        # Note: This is a proof-of-concept - the actual selectors would need to be
        # determined by inspecting the bioRxiv search results page structure
        results_container = soup.find('div', class_='search-results') or soup.find('div', id='search-results')
        
        if not results_container:
            # Fallback: look for common patterns
            results_container = soup.find('main') or soup.find('div', class_='content')
        
        if results_container:
            # Look for individual paper entries
            # These selectors are examples and would need to be updated based on actual page structure
            paper_elements = results_container.find_all(['article', 'div'], class_=re.compile(r'paper|result|entry'))
            
            for i, paper_elem in enumerate(paper_elements[:max_results]):
                try:
                    paper_data = self._extract_paper_data(paper_elem)
                    if paper_data:
                        papers.append(paper_data)
                except Exception as e:
                    logger.warning(f"Error parsing paper {i}: {e}")
                    continue
        
        # Extract pagination information
        pagination = self._extract_pagination_info(soup)
        
        return {
            'papers': papers,
            'pagination': pagination,
            'parsed_at': datetime.now().isoformat()
        }

    def _extract_paper_data(self, paper_elem) -> Optional[Dict[str, Any]]:
        """
        Extract paper data from a single paper element.
        
        Args:
            paper_elem: BeautifulSoup element containing paper data
            
        Returns:
            Dictionary with paper metadata or None if extraction fails
        """
        try:
            # These selectors are examples and would need to be updated based on actual page structure
            paper_data = {}
            
            # Extract title
            title_elem = paper_elem.find(['h1', 'h2', 'h3'], class_=re.compile(r'title'))
            if title_elem:
                paper_data['title'] = title_elem.get_text(strip=True)
            
            # Extract DOI
            doi_elem = paper_elem.find('a', href=re.compile(r'doi\.org'))
            if doi_elem:
                doi_match = re.search(r'doi\.org/(.+)', doi_elem['href'])
                if doi_match:
                    paper_data['doi'] = doi_match.group(1)
            
            # Extract authors
            authors_elem = paper_elem.find(['div', 'span'], class_=re.compile(r'author'))
            if authors_elem:
                paper_data['authors'] = authors_elem.get_text(strip=True)
            
            # Extract publication date
            date_elem = paper_elem.find(['time', 'span'], class_=re.compile(r'date'))
            if date_elem:
                paper_data['publication_date'] = date_elem.get_text(strip=True)
            
            # Extract abstract (if available)
            abstract_elem = paper_elem.find(['div', 'p'], class_=re.compile(r'abstract'))
            if abstract_elem:
                paper_data['abstract'] = abstract_elem.get_text(strip=True)
            
            # Extract subject area
            subject_elem = paper_elem.find(['span', 'div'], class_=re.compile(r'subject|category'))
            if subject_elem:
                paper_data['subject_area'] = subject_elem.get_text(strip=True)
            
            # Extract article type
            type_elem = paper_elem.find(['span', 'div'], class_=re.compile(r'type|article-type'))
            if type_elem:
                paper_data['article_type'] = type_elem.get_text(strip=True)
            
            # Extract bioRxiv ID
            id_elem = paper_elem.find(['span', 'div'], class_=re.compile(r'id|biorxiv-id'))
            if id_elem:
                paper_data['biorxiv_id'] = id_elem.get_text(strip=True)
            
            # Add extraction timestamp
            paper_data['extracted_at'] = datetime.now().isoformat()
            
            return paper_data if paper_data else None
            
        except Exception as e:
            logger.warning(f"Error extracting paper data: {e}")
            return None

    def _extract_pagination_info(self, soup) -> Dict[str, Any]:
        """
        Extract pagination information from the search results page.
        
        Args:
            soup: BeautifulSoup object of the page
            
        Returns:
            Dictionary with pagination information
        """
        pagination = {
            'current_page': 1,
            'total_pages': 1,
            'results_per_page': 20,
            'has_next': False,
            'has_previous': False
        }
        
        # Look for pagination elements
        # These selectors are examples and would need to be updated based on actual page structure
        pagination_elem = soup.find(['nav', 'div'], class_=re.compile(r'pagination'))
        
        if pagination_elem:
            # Extract current page
            current_elem = pagination_elem.find(['span', 'a'], class_=re.compile(r'current|active'))
            if current_elem:
                try:
                    pagination['current_page'] = int(current_elem.get_text(strip=True))
                except ValueError:
                    pass
            
            # Check for next/previous links
            next_elem = pagination_elem.find('a', class_=re.compile(r'next'))
            if next_elem:
                pagination['has_next'] = True
            
            prev_elem = pagination_elem.find('a', class_=re.compile(r'previous|prev'))
            if prev_elem:
                pagination['has_previous'] = True
        
        return pagination

    def get_paper_details(self, doi: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information for a specific paper by DOI.
        
        Args:
            doi: DOI of the paper
            
        Returns:
            Dictionary with detailed paper information or None if not found
        """
        try:
            # Construct the paper URL
            paper_url = f"{self.base_url}/content/{doi}"
            
            response = self.session.get(paper_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract detailed information
            details = self._extract_paper_details(soup)
            if details:
                details['doi'] = doi
                details['url'] = paper_url
                details['extracted_at'] = datetime.now().isoformat()
            
            return details
            
        except requests.RequestException as e:
            logger.error(f"Error getting paper details for {doi}: {e}")
            return None

    def _extract_paper_details(self, soup) -> Optional[Dict[str, Any]]:
        """
        Extract detailed paper information from the paper page.
        
        Args:
            soup: BeautifulSoup object of the paper page
            
        Returns:
            Dictionary with detailed paper information
        """
        try:
            details = {}
            
            # Extract title
            title_elem = soup.find(['h1', 'h2'], class_=re.compile(r'title'))
            if title_elem:
                details['title'] = title_elem.get_text(strip=True)
            
            # Extract authors
            authors_elem = soup.find(['div', 'section'], class_=re.compile(r'author'))
            if authors_elem:
                details['authors'] = authors_elem.get_text(strip=True)
            
            # Extract abstract
            abstract_elem = soup.find(['div', 'section'], class_=re.compile(r'abstract'))
            if abstract_elem:
                details['abstract'] = abstract_elem.get_text(strip=True)
            
            # Extract subject areas
            subjects_elem = soup.find(['div', 'section'], class_=re.compile(r'subject'))
            if subjects_elem:
                details['subject_areas'] = [s.strip() for s in subjects_elem.get_text().split(',')]
            
            # Extract publication date
            date_elem = soup.find(['time', 'span'], class_=re.compile(r'date'))
            if date_elem:
                details['publication_date'] = date_elem.get_text(strip=True)
            
            # Extract PDF link
            pdf_elem = soup.find('a', href=re.compile(r'\.pdf$'))
            if pdf_elem:
                details['pdf_url'] = urljoin(self.base_url, pdf_elem['href'])
            
            return details if details else None
            
        except Exception as e:
            logger.warning(f"Error extracting paper details: {e}")
            return None

    def save_results(self, results: Dict[str, Any], output_dir: str, filename: str = "biorxiv_search_results.json"):
        """
        Save search results to a JSON file.
        
        Args:
            results: Search results dictionary
            output_dir: Output directory path
            filename: Output filename
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        file_path = output_path / filename
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Results saved to: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Error saving results: {e}")
            return None


def main():
    """
    Example usage of the BioRxivWebScraper.
    """
    scraper = BioRxivWebScraper()
    
    # Example search
    query = "urban heat island"
    results = scraper.search_papers(query, max_results=10)
    
    if 'error' not in results:
        print(f"Found {len(results['papers'])} papers for query: '{query}'")
        
        for i, paper in enumerate(results['papers'], 1):
            print(f"\n{i}. {paper.get('title', 'No title')}")
            print(f"   DOI: {paper.get('doi', 'No DOI')}")
            print(f"   Authors: {paper.get('authors', 'No authors')}")
            print(f"   Date: {paper.get('publication_date', 'No date')}")
        
        # Save results
        scraper.save_results(results, "biorxiv_search_output")
    else:
        print(f"Error: {results['error']}")


if __name__ == "__main__":
    main() 