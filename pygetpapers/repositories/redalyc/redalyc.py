"""
Redalyc repository implementation for web scraping.

Redalyc is a multilingual scientific repository focused on Latin America,
Spain, and Portugal. This implementation uses web scraping since Redalyc
doesn't provide a public REST API.
"""

import logging
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from pygetpapers.core.download_tools import DownloadTools
from pygetpapers.core.file_utils import FileUtils
from pygetpapers.core.metadata_extractor import MetadataExtractor
from pygetpapers.core.repositoryinterface import RepositoryInterface


class Redalyc(RepositoryInterface):
    """Redalyc repository implementation using web scraping."""

    def __init__(self):
        """Initialize Redalyc repository."""
        super().__init__()
        self.download_tools = DownloadTools("redalyc")
        self.base_url = "https://redalyc.org"
        self.search_url = "https://redalyc.org/redalyc/search"
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "pygetpapers/2.0 " "(https://github.com/pygetpapers/pygetpapers)"
                ),
                "Accept": (
                    "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
                ),
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
            }
        )

        # Rate limiting
        self.request_delay = 1.0  # seconds between requests
        self.last_request_time = 0

    def _rate_limit(self):
        """Implement rate limiting to be respectful to Redalyc's servers."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.request_delay:
            time.sleep(self.request_delay - time_since_last)
        self.last_request_time = time.time()

    def _make_request(
        self, url: str, params: Optional[Dict] = None
    ) -> Optional[requests.Response]:
        """Make a rate-limited request to Redalyc."""
        self._rate_limit()
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logging.error(f"Request failed for {url}: {e}")
            return None

    def _extract_article_links(self, html_content: str) -> List[str]:
        """Extract article links from search results page."""
        soup = BeautifulSoup(html_content, "html.parser")
        article_links = []

        # Look for article links - this will need to be updated based on actual
        # HTML structure
        # Common patterns for article links
        link_selectors = [
            'a[href*="/articulo"]',
            'a[href*="/article"]',
            ".result-item a",
            ".article-link",
            'a[href*="id="]',
        ]

        for selector in link_selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get("href")
                if href:
                    full_url = urljoin(self.base_url, href)
                    if full_url not in article_links:
                        article_links.append(full_url)

        return article_links

    def _extract_article_metadata(
        self, html_content: str, article_url: str
    ) -> Dict[str, Any]:
        """Extract metadata from an article page."""
        # Use the centralized metadata extractor
        return MetadataExtractor.extract_all_metadata(html_content, article_url)

    def _scrape_homepage_articles(self, max_results: int = 10) -> List[str]:
        """
        Scrape article links from the Redalyc homepage.

        This is a fallback method when the search endpoint is not available.

        Args:
            max_results: Maximum number of article links to extract

        Returns:
            List of article URLs
        """
        logging.info("Scraping Redalyc homepage for article links")

        response = self._make_request(self.base_url)
        if not response:
            logging.error("Failed to get Redalyc homepage")
            return []

        # Extract article links from homepage
        article_links = self._extract_article_links(response.text)
        logging.info(f"Found {len(article_links)} article links on homepage")

        # Limit results
        return article_links[:max_results]

    def search_articles(
        self, query: str, max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for articles on Redalyc.

        Args:
            query: Search query string
            max_results: Maximum number of results to return

        Returns:
            List of article metadata dictionaries
        """
        logging.info(f"Searching Redalyc for: {query}")

        # Try the search endpoint first
        search_params = {"q": query, "t": "Art", "limit": max_results}  # Article type

        response = self._make_request(self.search_url, search_params)
        if response:
            # Extract article links from search results
            article_links = self._extract_article_links(response.text)
            logging.info(f"Found {len(article_links)} article links from search")
        else:
            logging.warning("Search endpoint failed, falling back to homepage scraping")
            # Fallback to homepage scraping
            article_links = self._scrape_homepage_articles(max_results)

        # Limit results
        article_links = article_links[:max_results]

        # Extract metadata for each article
        articles = []
        for link in article_links:
            article_response = self._make_request(link)
            if article_response:
                metadata = self._extract_article_metadata(article_response.text, link)
                articles.append(metadata)
                logging.info(
                    f"Extracted metadata for: {metadata.get('title', 'Unknown title')}"
                )

        return articles

    def download_article(self, article_url: str, output_dir: str) -> bool:
        """
        Download a single article and its associated files.

        Args:
            article_url: URL of the article to download
            output_dir: Directory to save the downloaded files

        Returns:
            True if download was successful, False otherwise
        """
        logging.info(f"Downloading article: {article_url}")

        # Get article page
        response = self._make_request(article_url)
        if not response:
            return False

        # Extract metadata
        metadata = self._extract_article_metadata(response.text, article_url)

        # Use FileUtils for file operations
        article_id = FileUtils.generate_article_id(metadata, article_url)
        article_dir = Path(output_dir, article_id)
        FileUtils.create_directory(article_dir)

        # Save files using FileUtils
        FileUtils.save_article_files(
            metadata=metadata, output_dir=article_dir, html_content=response.text
        )

        # Download PDF if available
        if metadata.get("pdf_url"):
            pdf_response = self._make_request(metadata["pdf_url"])
            if pdf_response:
                pdf_file = Path(article_dir, "fulltext.pdf")
                with open(pdf_file, "wb") as f:
                    f.write(pdf_response.content)
                logging.info(f"Downloaded PDF: {pdf_file}")

        # Download XML if available
        if metadata.get("xml_url"):
            xml_response = self._make_request(metadata["xml_url"])
            if xml_response:
                xml_file = Path(article_dir, "fulltext.xml")
                with open(xml_file, "w", encoding="utf-8") as f:
                    f.write(xml_response.text)
                logging.info(f"Downloaded XML: {xml_file}")

        logging.info(f"Successfully downloaded article to: {article_dir}")
        return True

    def _generate_article_id(self, metadata: Dict[str, Any]) -> str:
        """Generate a unique identifier for an article."""
        # Try to use DOI first
        if metadata.get("doi"):
            return metadata["doi"].replace("/", "_")

        # Use title as fallback
        if metadata.get("title"):
            # Clean title for filename
            title = re.sub(r"[^\w\s-]", "", metadata["title"])
            title = re.sub(r"[-\s]+", "-", title)
            return title[:50]  # Limit length

        # Use URL hash as last resort
        return str(hash(metadata.get("url", "")))

    def redalyc(
        self,
        query: str,
        cutoff_size: int,
        filter_dict: Optional[Dict] = None,
        update: Optional[Dict] = None,
        makecsv: bool = False,
        makexml: bool = False,
        makehtml: bool = False,
    ) -> Dict[str, Any]:
        """
        Main method to search and download articles from Redalyc.

        Args:
            query: Search query
            cutoff_size: Maximum number of articles to retrieve
            filter_dict: Optional filters (not used in current implementation)
            update: Optional update dictionary from previous run
            makecsv: Whether to generate CSV output
            makexml: Whether to download XML files
            makehtml: Whether to download HTML files

        Returns:
            Dictionary containing results and metadata
        """
        logging.info("Starting Redalyc search and download")

        # Search for articles
        articles = self.search_articles(query, cutoff_size)

        if not articles:
            logging.warning("No articles found for the given query")
            return {
                "new_results": {"total_hits": 0, "total_json_output": []},
                "updated_dict": {},
            }

        # Prepare results structure
        results = {
            "new_results": {"total_hits": len(articles), "total_json_output": articles},
            "updated_dict": {},
        }

        # Download articles if requested
        if makehtml or makexml:
            output_dir = self.download_tools.get_output_directory()
            for article in articles:
                self.download_article(article["url"], output_dir)

        # Generate CSV if requested
        if makecsv:
            self.download_tools.handle_creation_of_csv_html_xml(
                makecsv, makehtml, makexml, articles, "redalyc_result"
            )

        logging.info(f"Redalyc search completed. Found {len(articles)} articles.")
        return results

    def update(self, query_namespace: Dict[str, Any]) -> None:
        """Update search results from previous run."""
        logging.info("Reading old JSON metadata file")
        update_path = self.get_metadata_results_file()
        update = self.download_tools.readjsondata(update_path)

        result_dict = self.redalyc(
            query_namespace["query"],
            query_namespace["limit"],
            filter_dict=query_namespace.get("filter"),
            update=update,
            makecsv=query_namespace["makecsv"],
            makexml=query_namespace["xml"],
            makehtml=query_namespace["makehtml"],
        )

        self.download_tools._make_metadata_json_files_for_paper(
            result_dict["new_results"],
            updated_dict=result_dict["updated_dict"],
            paper_key="url",
            name_of_file="redalyc_result",
        )

    def noexecute(self, query_namespace: Dict[str, Any]) -> None:
        """Execute search without downloading files."""
        query = query_namespace["query"]
        logging.info(f"Searching Redalyc for: {query}")

        # Try search endpoint first
        search_params = {"q": query, "t": "Art", "limit": 10}

        response = self._make_request(self.search_url, search_params)
        if response:
            # If search works, count results from search
            article_links = self._extract_article_links(response.text)
            total_hits = len(article_links)
        else:
            # Fallback to homepage scraping for count only
            logging.warning(
                "Search endpoint failed, falling back to homepage scraping for count"
            )
            article_links = self._scrape_homepage_articles(max_results=100)
            total_hits = len(article_links)

        logging.info(f"Total number of hits for the query are {total_hits}")

    def apipaperdownload(self, query_namespace: Dict[str, Any]) -> None:
        """Download papers via API (web scraping in this case)."""
        result_dict = self.redalyc(
            query_namespace["query"],
            query_namespace["limit"],
            filter_dict=query_namespace.get("filter"),
            update=None,
            makecsv=query_namespace["makecsv"],
            makexml=query_namespace["xml"],
            makehtml=query_namespace["makehtml"],
        )

        self.download_tools._make_metadata_json_files_for_paper(
            result_dict["new_results"],
            updated_dict=result_dict["updated_dict"],
            paper_key="url",
            name_of_file="redalyc_result",
        )
