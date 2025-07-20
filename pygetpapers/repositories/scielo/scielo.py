"""
SciELO repository implementation for web scraping.

SciELO is a multilingual scientific repository focused on Latin America,
Spain, Portugal, and South Africa. This implementation uses web scraping
since SciELO doesn't provide a public REST API.
"""

import logging
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from pygetpapers.core.download_tools import DownloadTools
from pygetpapers.core.file_utils import FileUtils
from pygetpapers.core.repositoryinterface import RepositoryInterface


class SciELO(RepositoryInterface):
    """SciELO repository implementation using web scraping."""

    def __init__(self):
        """Initialize SciELO repository."""
        super().__init__()
        self.download_tools = DownloadTools("scielo")
        self.base_url = "https://scielo.org"
        self.search_url = "https://search.scielo.org"
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                ),
                "Accept": (
                    "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
                ),
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }
        )

        # Rate limiting
        self.request_delay = 2.0  # seconds between requests
        self.last_request_time = 0

    def _rate_limit(self):
        """Implement rate limiting to be respectful to SciELO's servers."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.request_delay:
            time.sleep(self.request_delay - time_since_last)
        self.last_request_time = time.time()

    def _make_request(
        self, url: str, params: Optional[Dict] = None
    ) -> Optional[requests.Response]:
        """Make a rate-limited request to SciELO."""
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

        # Look for article links - SciELO specific patterns
        link_selectors = [
            'a[href*="/scielo.php?script=sci_arttext"]',
            'a[href*="script=sci_arttext"]',
            'a[target="_blank"]',
        ]

        for selector in link_selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get("href")
                if href:
                    # Clean up the URL
                    if href.startswith("//"):
                        href = "https:" + href
                    elif href.startswith("/"):
                        href = urljoin(self.search_url, href)
                    elif not href.startswith("http"):
                        href = urljoin(self.search_url, href)
                    
                    # Only include article links (not PDF or other links)
                    if "script=sci_arttext" in href and href not in article_links:
                        article_links.append(href)

        return article_links

    def _extract_article_metadata(
        self, html_content: str, article_url: str
    ) -> Dict[str, Any]:
        """Extract metadata from an article page."""
        soup = BeautifulSoup(html_content, "html.parser")
        
        metadata = {
            "url": article_url,
            "title": None,
            "authors": [],
            "abstract": None,
            "journal": None,
            "year": None,
            "doi": None,
            "language": None,
            "keywords": [],
            "volume": None,
            "issue": None,
            "pages": None,
            "pdf_urls": [],
            "collection": None
        }

        # Extract title
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
                    metadata["title"] = title_text
                    break

        # Extract authors
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
                if author_text and len(author_text) > 2 and author_text not in metadata["authors"]:
                    # Clean up author text (remove ORCID links, etc.)
                    clean_author = re.sub(r'http://orcid\.org/\d{4}-\d{4}-\d{4}-\d{3}[0-9X]', '', author_text)
                    clean_author = re.sub(r'\d+', '', clean_author)  # Remove numbers
                    clean_author = clean_author.strip()
                    if clean_author and len(clean_author) > 2:
                        metadata["authors"].append(clean_author)

        # Extract abstract
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
                metadata["abstract"] = abstract_elem.get_text(strip=True)
                break

        # Extract journal
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
                metadata["journal"] = journal_elem.get_text(strip=True)
                break

        # Extract DOI
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
                    metadata["doi"] = doi_text
                    break

        # Extract keywords
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
                    metadata["keywords"].append(keyword_text)

        # Extract PDF URLs
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
                href = link.get("href")
                if href:
                    if not href.startswith("http"):
                        parsed_url = urlparse(article_url)
                        href = f"{parsed_url.scheme}://{parsed_url.netloc}{href}"
                    if href not in metadata["pdf_urls"]:
                        metadata["pdf_urls"].append(href)

        # Extract collection from URL
        parsed_url = urlparse(article_url)
        if parsed_url.netloc:
            metadata["collection"] = parsed_url.netloc

        return metadata

    def search_articles(
        self, query: str, max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for articles on SciELO.

        Args:
            query: Search query string
            max_results: Maximum number of results to return

        Returns:
            List of article metadata dictionaries
        """
        logging.info(f"Searching SciELO for: {query}")

        # Build search parameters
        search_params = {
            "q": query,
            "lang": "en",  # Prefer English
            "count": min(max_results, 20),  # SciELO limit
            "from": 0,
            "output": "site",
            "sort": "",
            "format": "summary"
        }

        response = self._make_request(self.search_url, search_params)
        if not response:
            logging.error("Failed to get search results from SciELO")
            return []

        # Extract article links from search results
        article_links = self._extract_article_links(response.text)
        logging.info(f"Found {len(article_links)} article links from search")

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
        article_dir = Path(output_dir) / article_id
        article_dir.mkdir(parents=True, exist_ok=True)

        # Save HTML content
        html_file = article_dir / f"{article_id}.html"
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(response.text)

        # Save metadata
        metadata_file = article_dir / f"{article_id}_metadata.json"
        with open(metadata_file, "w", encoding="utf-8") as f:
            import json
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        # Download PDFs if available
        for i, pdf_url in enumerate(metadata.get("pdf_urls", [])):
            try:
                pdf_response = self._make_request(pdf_url)
                if pdf_response and pdf_response.headers.get("content-type", "").startswith("application/pdf"):
                    pdf_file = article_dir / f"{article_id}_pdf_{i+1}.pdf"
                    with open(pdf_file, "wb") as f:
                        f.write(pdf_response.content)
                    logging.info(f"Downloaded PDF: {pdf_file}")
            except Exception as e:
                logging.warning(f"Failed to download PDF {pdf_url}: {e}")

        logging.info(f"Article downloaded to: {article_dir}")
        return True

    def scielo(
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
        Main SciELO search and download method.

        Args:
            query: Search query
            cutoff_size: Maximum number of results
            filter_dict: Optional filters
            update: Optional update parameters
            makecsv: Generate CSV output
            makexml: Generate XML output
            makehtml: Generate HTML output

        Returns:
            Dictionary with search results and metadata
        """
        logging.info(f"Starting SciELO search for: {query}")

        # Search for articles
        articles = self.search_articles(query, cutoff_size)

        # Prepare results
        results = {
            "query": query,
            "total_results": len(articles),
            "articles": articles,
            "search_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "repository": "scielo"
        }

        # Generate outputs if requested
        if makecsv:
            self._generate_csv_output(results, "scielo_results")
        
        if makexml:
            self._generate_xml_output(results, "scielo_results")
        
        if makehtml:
            self._generate_html_output(results, "scielo_results")

        logging.info(f"SciELO search completed. Found {len(articles)} articles.")
        return results

    def _generate_csv_output(self, results: Dict[str, Any], base_filename: str) -> None:
        """Generate CSV output from search results."""
        import csv
        
        csv_file = Path(f"{base_filename}.csv")
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            if results["articles"]:
                fieldnames = results["articles"][0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for article in results["articles"]:
                    writer.writerow(article)
        
        logging.info(f"CSV output saved to: {csv_file}")

    def _generate_xml_output(self, results: Dict[str, Any], base_filename: str) -> None:
        """Generate XML output from search results."""
        import xml.etree.ElementTree as ET
        
        root = ET.Element("scielo_results")
        root.set("query", results["query"])
        root.set("total_results", str(results["total_results"]))
        root.set("search_date", results["search_date"])
        
        for article in results["articles"]:
            article_elem = ET.SubElement(root, "article")
            for key, value in article.items():
                if isinstance(value, list):
                    for item in value:
                        item_elem = ET.SubElement(article_elem, key)
                        item_elem.text = str(item)
                else:
                    elem = ET.SubElement(article_elem, key)
                    elem.text = str(value) if value else ""
        
        tree = ET.ElementTree(root)
        xml_file = Path(f"{base_filename}.xml")
        tree.write(xml_file, encoding="utf-8", xml_declaration=True)
        
        logging.info(f"XML output saved to: {xml_file}")

    def _generate_html_output(self, results: Dict[str, Any], base_filename: str) -> None:
        """Generate HTML output from search results."""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>SciELO Search Results: {results['query']}</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .article {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; }}
        .title {{ font-size: 18px; font-weight: bold; color: #333; }}
        .authors {{ color: #666; margin: 5px 0; }}
        .abstract {{ margin: 10px 0; }}
        .metadata {{ font-size: 12px; color: #888; }}
    </style>
</head>
<body>
    <h1>SciELO Search Results</h1>
    <p><strong>Query:</strong> {results['query']}</p>
    <p><strong>Total Results:</strong> {results['total_results']}</p>
    <p><strong>Search Date:</strong> {results['search_date']}</p>
    
    <div class="results">
"""
        
        for article in results["articles"]:
            html_content += f"""
        <div class="article">
            <div class="title">{article.get('title', 'No title')}</div>
            <div class="authors">Authors: {', '.join(article.get('authors', []))}</div>
            <div class="abstract">{article.get('abstract', 'No abstract')}</div>
            <div class="metadata">
                Journal: {article.get('journal', 'Unknown')} | 
                DOI: {article.get('doi', 'No DOI')} | 
                Collection: {article.get('collection', 'Unknown')}
            </div>
        </div>
"""
        
        html_content += """
    </div>
</body>
</html>
"""
        
        html_file = Path(f"{base_filename}.html")
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        logging.info(f"HTML output saved to: {html_file}")

    def update(self, query_namespace: Dict[str, Any]) -> None:
        """Update from previous results."""
        logging.info("Update functionality not implemented for SciELO")

    def noexecute(self, query_namespace: Dict[str, Any]) -> None:
        """Search without downloading."""
        query = query_namespace.get("query", "")
        cutoff_size = query_namespace.get("limit", 10)
        
        articles = self.search_articles(query, cutoff_size)
        logging.info(f"Found {len(articles)} articles for query: {query}")

    def apipaperdownload(self, query_namespace: Dict[str, Any]) -> None:
        """Download papers from search results."""
        query = query_namespace.get("query", "")
        cutoff_size = query_namespace.get("limit", 10)
        output_dir = query_namespace.get("output", "scielo_downloads")
        
        # Search for articles
        articles = self.search_articles(query, cutoff_size)
        
        # Download each article
        for article in articles:
            article_url = article.get("url")
            if article_url:
                self.download_article(article_url, output_dir) 