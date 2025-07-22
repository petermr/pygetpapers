#!/usr/bin/env python3
"""
SciELO Site Exploration Script

This script manually explores SciELO's search interface to understand:
- URL patterns for articles and journals
- Available content types (HTML, PDF, XML)
- Search parameters and options
- Rate limiting and access patterns
- Language support and content availability

Usage:
    python temp/scielo_exploration.py
"""

import requests
import time
import json
from pathlib import Path
from urllib.parse import urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SciELOExplorer:
    """Manual explorer for SciELO's search interface."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }
        )

        # Base URLs
        self.base_urls = {
            "global": "https://scielo.org",
            "brazil": "https://www.scielo.br",
            "search": "https://search.scielo.org",
        }

        # Rate limiting
        self.request_delay = 2.0
        self.last_request_time = 0

        # Output directory
        self.output_dir = Path("temp/scielo_exploration")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _rate_limit(self):
        """Implement rate limiting."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.request_delay:
            time.sleep(self.request_delay - time_since_last)
        self.last_request_time = time.time()

    def _make_request(self, url, params=None, save_response=True, filename=None):
        """Make a rate-limited request and optionally save response."""
        self._rate_limit()

        try:
            logger.info(f"Requesting: {url}")
            response = self.session.get(url, params=params, timeout=30)
            logger.info(f"Response status: {response.status_code}")

            if save_response and response.status_code == 200:
                if filename is None:
                    # Generate filename from URL
                    parsed = urlparse(url)
                    filename = f"{parsed.netloc.replace('.', '_')}_{parsed.path.replace('/', '_')}.html"
                    if params:
                        filename = f"{filename.split('.')[0]}_{hash(str(params))}.html"

                filepath = self.output_dir / filename
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(response.text)
                logger.info(f"Saved response to: {filepath}")

            return response

        except Exception as e:
            logger.error(f"Request failed for {url}: {e}")
            return None

    def explore_homepage(self):
        """Explore the main SciELO homepage."""
        logger.info("=== Exploring SciELO Homepage ===")

        # Try global site
        response = self._make_request(
            self.base_urls["global"],
            save_response=True,
            filename="scielo_global_homepage.html",
        )

        if response and response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            # Find search forms
            search_forms = soup.find_all("form")
            logger.info(f"Found {len(search_forms)} forms on homepage")

            for i, form in enumerate(search_forms):
                logger.info(f"Form {i+1}:")
                logger.info(f"  Action: {form.get('action', 'N/A')}")
                logger.info(f"  Method: {form.get('method', 'N/A')}")

                # Find input fields
                inputs = form.find_all("input")
                for inp in inputs:
                    logger.info(
                        f"    Input: {inp.get('name', 'N/A')} = {inp.get('type', 'N/A')}"
                    )

        # Try Brazil site
        response = self._make_request(
            self.base_urls["brazil"],
            save_response=True,
            filename="scielo_brazil_homepage.html",
        )

        return response

    def explore_search_interface(self):
        """Explore the search interface."""
        logger.info("=== Exploring Search Interface ===")

        # Try direct search endpoint
        search_params = {
            "q": "climate change",
            "lang": "en",
            "count": "5",
            "from": "0",
            "output": "site",
            "sort": "",
            "format": "summary",
        }

        response = self._make_request(
            f"{self.base_urls['search']}/",
            params=search_params,
            save_response=True,
            filename="scielo_search_results.html",
        )

        if response:
            logger.info(f"Search response status: {response.status_code}")
            if response.status_code == 403:
                logger.warning("Search endpoint blocked automated requests")
            elif response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                self._analyze_search_results(soup)

        return response

    def _analyze_search_results(self, soup):
        """Analyze search results page structure."""
        logger.info("=== Analyzing Search Results Structure ===")

        # Look for article links
        article_links = []

        # Common patterns for article links
        link_selectors = [
            'a[href*="/scielo.php"]',
            'a[href*="/article"]',
            'a[href*="/pdf"]',
            ".result-item a",
            ".article-link",
            'a[href*="pid="]',
            'a[href*="script="]',
        ]

        for selector in link_selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get("href")
                if href:
                    full_url = urljoin(self.base_urls["search"], href)
                    if full_url not in article_links:
                        article_links.append(full_url)
                        logger.info(f"Found article link: {full_url}")

        logger.info(f"Total article links found: {len(article_links)}")

        # Look for pagination
        pagination = soup.find_all("a", href=True)
        pagination_links = [
            link["href"]
            for link in pagination
            if "page=" in link["href"] or "from=" in link["href"]
        ]
        logger.info(f"Pagination links found: {len(pagination_links)}")

        # Look for search parameters in forms
        forms = soup.find_all("form")
        for form in forms:
            inputs = form.find_all("input")
            for inp in inputs:
                name = inp.get("name")
                if name and name in [
                    "q",
                    "lang",
                    "count",
                    "from",
                    "output",
                    "sort",
                    "format",
                ]:
                    logger.info(f"Search parameter: {name} = {inp.get('value', 'N/A')}")

    def explore_article_page(self, article_url):
        """Explore a specific article page."""
        logger.info(f"=== Exploring Article Page: {article_url} ===")

        response = self._make_request(
            article_url, save_response=True, filename="scielo_article_page.html"
        )

        if response and response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract metadata
            metadata = self._extract_article_metadata(soup, article_url)
            logger.info(f"Extracted metadata: {json.dumps(metadata, indent=2)}")

            # Look for download links
            download_links = self._find_download_links(soup)
            logger.info(f"Download links found: {len(download_links)}")
            for link in download_links:
                logger.info(f"  Download: {link}")

            return metadata, download_links

        return None, []

    def _extract_article_metadata(self, soup, url):
        """Extract metadata from article page."""
        metadata = {
            "url": url,
            "title": None,
            "authors": [],
            "abstract": None,
            "journal": None,
            "year": None,
            "doi": None,
            "language": None,
        }

        # Title extraction
        title_selectors = ["h1.title", ".title", "h1", ".article-title", "title"]

        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                metadata["title"] = title_elem.get_text(strip=True)
                break

        # Authors extraction
        author_selectors = [".authors", ".author", ".byline", '[class*="author"]']

        for selector in author_selectors:
            author_elems = soup.select(selector)
            for elem in author_elems:
                author_text = elem.get_text(strip=True)
                if author_text and len(author_text) > 2:
                    metadata["authors"].append(author_text)

        # Abstract extraction
        abstract_selectors = [".abstract", ".resumo", ".summary", '[class*="abstract"]']

        for selector in abstract_selectors:
            abstract_elem = soup.select_one(selector)
            if abstract_elem:
                metadata["abstract"] = abstract_elem.get_text(strip=True)
                break

        # Journal extraction
        journal_selectors = [
            ".journal",
            ".periodical",
            ".publication",
            '[class*="journal"]',
        ]

        for selector in journal_selectors:
            journal_elem = soup.select_one(selector)
            if journal_elem:
                metadata["journal"] = journal_elem.get_text(strip=True)
                break

        return metadata

    def _find_download_links(self, soup):
        """Find download links for PDF, HTML, XML."""
        download_links = []

        # Look for PDF links
        pdf_selectors = [
            'a[href*=".pdf"]',
            'a[href*="/pdf/"]',
            'a[href*="format=pdf"]',
            ".pdf-link a",
            'a[title*="PDF"]',
        ]

        for selector in pdf_selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get("href")
                if href:
                    full_url = urljoin(self.base_urls["search"], href)
                    download_links.append(("PDF", full_url))

        # Look for HTML links
        html_selectors = [
            'a[href*="format=html"]',
            'a[href*="/html/"]',
            ".html-link a",
            'a[title*="HTML"]',
        ]

        for selector in html_selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get("href")
                if href:
                    full_url = urljoin(self.base_urls["search"], href)
                    download_links.append(("HTML", full_url))

        # Look for XML links
        xml_selectors = [
            'a[href*=".xml"]',
            'a[href*="format=xml"]',
            ".xml-link a",
            'a[title*="XML"]',
        ]

        for selector in xml_selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get("href")
                if href:
                    full_url = urljoin(self.base_urls["search"], href)
                    download_links.append(("XML", full_url))

        return download_links

    def generate_exploration_report(self):
        """Generate a comprehensive exploration report."""
        logger.info("=== Generating Exploration Report ===")

        report = {
            "exploration_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "base_urls": self.base_urls,
            "findings": {
                "search_interface": {
                    "status": "explored",
                    "blocking": "unknown",
                    "parameters": [
                        "q",
                        "lang",
                        "count",
                        "from",
                        "output",
                        "sort",
                        "format",
                    ],
                },
                "content_types": {
                    "html": "likely_available",
                    "pdf": "likely_available",
                    "xml": "unknown",
                },
                "rate_limiting": {
                    "implemented": True,
                    "delay_seconds": self.request_delay,
                },
                "language_support": {
                    "english": True,
                    "spanish": True,
                    "portuguese": True,
                },
            },
            "recommendations": [
                "Implement both basic and Selenium scrapers",
                "Use proper User-Agent and session management",
                "Implement rate limiting (2+ seconds between requests)",
                "Handle 403 Forbidden responses gracefully",
                "Extract metadata from article pages",
                "Support multiple content types (HTML, PDF)",
            ],
        }

        # Save report
        report_file = self.output_dir / "exploration_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Exploration report saved to: {report_file}")
        return report


def main():
    """Main exploration function."""
    logger.info("Starting SciELO site exploration...")

    explorer = SciELOExplorer()

    # Explore homepage
    explorer.explore_homepage()

    # Explore search interface
    explorer.explore_search_interface()

    # Generate report
    report = explorer.generate_exploration_report()

    logger.info("Exploration completed!")
    logger.info(f"Results saved to: {explorer.output_dir}")

    return report


if __name__ == "__main__":
    main()
