"""
BioRxiv Web Scraper - Enhanced Implementation

This module provides a comprehensive web scraper for bioRxiv's search interface,
allowing text-based search functionality that complements the existing API-based
date-only search in pygetpapers.

The web search interface at https://www.biorxiv.org/search/ supports text queries
and returns results in a paginated format, unlike the API which only supports
date-based searches.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import parse_qs, quote_plus, urljoin, urlparse

import requests
from bs4 import BeautifulSoup
import re
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class BioRxivWebScraper:
    """
    Enhanced web scraper for bioRxiv's search interface.

    This provides text-based search functionality that complements the existing
    API-based date-only search in pygetpapers.
    """

    def __init__(self):
        self.base_url = "https://www.biorxiv.org"
        self.search_url = f"{self.base_url}/search"
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        )

    def search_papers(
        self,
        query: str,
        max_results: int = 100,
        subject_area: Optional[str] = None,
        article_type: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        results_per_page: int = 10,
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
            results_per_page: Number of results per page (10, 25, 50)

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
            params["subject_area"] = subject_area
        if article_type:
            params["article_type"] = article_type
        if date_from:
            params["date_from"] = date_from
        if date_to:
            params["date_to"] = date_to
        if results_per_page != 10:
            params["numresults"] = results_per_page

        try:
            response = self.session.get(search_url, params=params, timeout=30)
            response.raise_for_status()

            # Parse the search results page
            results = self._parse_search_results(response.text, max_results)

            # Add metadata
            results["search_query"] = query
            results["search_url"] = response.url
            results["total_found"] = len(results["papers"])
            results["search_timestamp"] = datetime.now().isoformat()

            logger.info(f"Found {len(results['papers'])} papers for query: {query}")
            return results

        except requests.RequestException as e:
            logger.error(f"Error searching bioRxiv: {e}")
            return {
                "error": str(e),
                "papers": [],
                "search_query": query,
                "total_found": 0,
            }

    def _parse_search_results(
        self, html_content: str, max_results: int
    ) -> Dict[str, Any]:
        """
        Parse the HTML search results page using the actual bioRxiv structure.

        Args:
            html_content: HTML content of the search results page
            max_results: Maximum number of results to parse

        Returns:
            Dictionary containing parsed papers and pagination info
        """
        soup = BeautifulSoup(html_content, "html.parser")
        papers = []

        # Find the search results container - bioRxiv uses specific classes
        results_list = soup.find("ul", class_="highwire-search-results-list")

        if results_list:
            # Find individual paper entries
            paper_elements = results_list.find_all(
                "li", class_=re.compile(r"search-result")
            )

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
            "papers": papers,
            "pagination": pagination,
            "parsed_at": datetime.now().isoformat(),
        }

    def _extract_paper_data(self, paper_elem) -> Optional[Dict[str, Any]]:
        """
        Extract paper data from a single paper element using bioRxiv's structure.

        Args:
            paper_elem: BeautifulSoup element containing paper data

        Returns:
            Dictionary with paper metadata or None if extraction fails
        """
        try:
            paper_data = {}

            # Find the citation container
            citation_elem = paper_elem.find("div", class_="highwire-article-citation")
            if not citation_elem:
                return None

            # Extract title
            title_elem = citation_elem.find("span", class_="highwire-cite-title")
            if title_elem:
                title_link = title_elem.find("a", class_="highwire-cite-linked-title")
                if title_link:
                    paper_data["title"] = title_link.get_text(strip=True)
                    paper_data["url"] = urljoin(
                        self.base_url, title_link.get("href", "")
                    )

            # Extract authors
            authors_elem = citation_elem.find("div", class_="highwire-cite-authors")
            if authors_elem:
                author_spans = authors_elem.find_all(
                    "span", class_="highwire-citation-author"
                )
                authors = []
                for author_span in author_spans:
                    given_names = author_span.find("span", class_="nlm-given-names")
                    surname = author_span.find("span", class_="nlm-surname")
                    if given_names and surname:
                        authors.append(
                            f"{given_names.get_text(strip=True)} {surname.get_text(strip=True)}"
                        )
                    elif given_names:
                        authors.append(given_names.get_text(strip=True))
                    elif surname:
                        authors.append(surname.get_text(strip=True))
                paper_data["authors"] = authors

            # Extract metadata
            metadata_elem = citation_elem.find("div", class_="highwire-cite-metadata")
            if metadata_elem:
                # Extract journal
                journal_elem = metadata_elem.find(
                    "span", class_="highwire-cite-metadata-journal"
                )
                if journal_elem:
                    paper_data["journal"] = journal_elem.get_text(strip=True)

                # Extract bioRxiv ID
                pages_elem = metadata_elem.find(
                    "span", class_="highwire-cite-metadata-pages"
                )
                if pages_elem:
                    paper_data["biorxiv_id"] = pages_elem.get_text(strip=True).rstrip(
                        ";"
                    )

                # Extract DOI
                doi_elem = metadata_elem.find(
                    "span", class_="highwire-cite-metadata-doi"
                )
                if doi_elem:
                    doi_text = doi_elem.get_text(strip=True)
                    doi_match = re.search(r"https://doi\.org/(.+)", doi_text)
                    if doi_match:
                        paper_data["doi"] = doi_match.group(1)

            # Extract data attributes for additional info
            if citation_elem.get("data-pisa"):
                paper_data["pisa_id"] = citation_elem.get("data-pisa")

            if citation_elem.get("data-apath"):
                paper_data["apath"] = citation_elem.get("data-apath")

            # Add extraction timestamp
            paper_data["extracted_at"] = datetime.now().isoformat()

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
            "current_page": 1,
            "total_pages": 1,
            "results_per_page": 10,
            "has_next": False,
            "has_previous": False,
            "next_url": None,
            "previous_url": None,
        }

        # Look for pagination elements
        pager_elem = soup.find("div", class_="pager-wrapper")

        if pager_elem:
            # Extract current page
            current_elem = pager_elem.find("li", class_="pager-current")
            if current_elem:
                try:
                    pagination["current_page"] = int(current_elem.get_text(strip=True))
                except ValueError:
                    pass

            # Check for next/previous links
            next_elem = pager_elem.find("li", class_="pager-next")
            if next_elem:
                next_link = next_elem.find("a")
                if next_link:
                    pagination["has_next"] = True
                    pagination["next_url"] = urljoin(
                        self.base_url, next_link.get("href", "")
                    )

            prev_elem = pager_elem.find("li", class_="pager-previous")
            if prev_elem:
                prev_link = prev_elem.find("a")
                if prev_link:
                    pagination["has_previous"] = True
                    pagination["previous_url"] = urljoin(
                        self.base_url, prev_link.get("href", "")
                    )

            # Extract total pages from the last page link
            last_elem = pager_elem.find("li", class_="pager-last")
            if last_elem:
                last_link = last_elem.find("a")
                if last_link:
                    try:
                        # Extract page number from URL or title
                        title = last_link.get("title", "")
                        page_match = re.search(r"page (\d+)", title)
                        if page_match:
                            pagination["total_pages"] = int(page_match.group(1))
                    except ValueError:
                        pass

        return pagination

    def get_next_page(self, current_url: str) -> Optional[str]:
        """
        Get the URL for the next page of results.

        Args:
            current_url: Current search results URL

        Returns:
            URL for the next page or None if no next page
        """
        try:
            response = self.session.get(current_url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            pagination = self._extract_pagination_info(soup)

            return pagination.get("next_url")

        except requests.RequestException as e:
            logger.error(f"Error getting next page: {e}")
            return None

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

            soup = BeautifulSoup(response.text, "html.parser")

            # Extract detailed information
            details = self._extract_paper_details(soup)
            if details:
                details["doi"] = doi
                details["url"] = paper_url
                details["extracted_at"] = datetime.now().isoformat()

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
            title_elem = soup.find(["h1", "h2"], class_=re.compile(r"title"))
            if title_elem:
                details["title"] = title_elem.get_text(strip=True)

            # Extract authors
            authors_elem = soup.find(["div", "section"], class_=re.compile(r"author"))
            if authors_elem:
                details["authors"] = authors_elem.get_text(strip=True)

            # Extract abstract
            abstract_elem = soup.find(
                ["div", "section"], class_=re.compile(r"abstract")
            )
            if abstract_elem:
                details["abstract"] = abstract_elem.get_text(strip=True)

            # Extract subject areas
            subjects_elem = soup.find(["div", "section"], class_=re.compile(r"subject"))
            if subjects_elem:
                details["subject_areas"] = [
                    s.strip() for s in subjects_elem.get_text().split(",")
                ]

            # Extract publication date
            date_elem = soup.find(["time", "span"], class_=re.compile(r"date"))
            if date_elem:
                details["publication_date"] = date_elem.get_text(strip=True)

            # Extract PDF link
            pdf_elem = soup.find("a", href=re.compile(r"\.pdf$"))
            if pdf_elem:
                details["pdf_url"] = urljoin(self.base_url, pdf_elem["href"])

            return details if details else None

        except Exception as e:
            logger.warning(f"Error extracting paper details: {e}")
            return None

    def download_paper_html(self, doi: str, output_dir: str) -> Optional[str]:
        """
        Download the HTML version of a paper.

        Args:
            doi: DOI of the paper
            output_dir: Directory to save the HTML file

        Returns:
            Path to the downloaded HTML file or None if failed
        """
        try:
            # Get the paper URL
            paper_url = f"{self.base_url}/content/{doi}"

            response = self.session.get(paper_url, timeout=30)
            response.raise_for_status()

            # Create output directory
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            # Save HTML file
            filename = f"{doi.replace('/', '_')}.html"
            file_path = output_path / filename

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(response.text)

            logger.info(f"Downloaded HTML for {doi} to {file_path}")
            return str(file_path)

        except Exception as e:
            logger.error(f"Error downloading HTML for {doi}: {e}")
            return None

    def save_results(
        self,
        results: Dict[str, Any],
        output_dir: str,
        filename: str = "biorxiv_search_results.json",
    ):
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
            with open(file_path, "w", encoding="utf-8") as f:
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
    results = scraper.search_papers(query, max_results=10, results_per_page=10)

    if "error" not in results:
        print(f"Found {len(results['papers'])} papers for query: '{query}'")

        for i, paper in enumerate(results["papers"], 1):
            print(f"\n{i}. {paper.get('title', 'No title')}")
            print(f"   DOI: {paper.get('doi', 'No DOI')}")
            print(f"   Authors: {', '.join(paper.get('authors', ['No authors']))}")
            print(f"   bioRxiv ID: {paper.get('biorxiv_id', 'No ID')}")
            print(f"   URL: {paper.get('url', 'No URL')}")

        # Save results
        scraper.save_results(results, "biorxiv_search_output")

        # Show pagination info
        pagination = results.get("pagination", {})
        print(
            f"\nPagination: Page {pagination.get('current_page', 1)} of {pagination.get('total_pages', 1)}"
        )
        if pagination.get("has_next"):
            print(f"Next page URL: {pagination.get('next_url')}")
    else:
        print(f"Error: {results['error']}")


if __name__ == "__main__":
    main()
