#!/usr/bin/env python3
"""
Advanced BioRxiv Web Scraper - Full Workflow Implementation

This module provides a comprehensive bioRxiv scraper that implements the full workflow:
1. Send a query and retrieve hit list with cursor/pagination
2. For each hit: download metadata, download HTML, provide PDF link
3. Handle pagination and cursor management
4. Batch processing capabilities
"""

import json
import logging
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional
from urllib.parse import quote_plus, urljoin

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class BioRxivAdvancedScraper:
    """
    Advanced bioRxiv web scraper with full workflow support.

    This scraper implements the complete workflow for bioRxiv paper collection:
    - Search with pagination support
    - Metadata extraction
    - HTML content downloading
    - PDF link extraction
    - Batch processing
    """

    def __init__(self, output_dir: str = "biorxiv_output", delay: float = 1.0):
        """
        Initialize the advanced scraper.

        Args:
            output_dir: Base output directory for downloads
            delay: Delay between requests in seconds
        """
        self.base_url = "https://www.biorxiv.org"
        self.search_url = f"{self.base_url}/search"
        self.output_dir = Path(output_dir)
        self.delay = delay

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Set up session
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        )

    def search_with_pagination(
        self,
        query: str,
        max_papers: int = 100,
        results_per_page: int = 25,
        start_page: int = 0,
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Search bioRxiv papers with automatic pagination handling.

        Args:
            query: Search query string
            max_papers: Maximum number of papers to retrieve
            results_per_page: Number of results per page (10, 25, 50)
            start_page: Starting page number (0-based)

        Yields:
            Dictionary containing paper data and pagination info
        """
        logger.info(f"Starting search for: {query} (max: {max_papers} papers)")

        papers_found = 0
        current_page = start_page

        while papers_found < max_papers:
            try:
                # Build search URL with pagination
                encoded_query = quote_plus(query)
                search_url = f"{self.search_url}/{encoded_query}"

                params = {"numresults": results_per_page}

                if current_page > 0:
                    params["page"] = current_page

                logger.info(f"Fetching page {current_page + 1}...")

                response = self.session.get(search_url, params=params, timeout=30)
                response.raise_for_status()

                # Parse results
                soup = BeautifulSoup(response.text, "html.parser")
                papers = self._parse_search_results(soup, max_papers - papers_found)

                if not papers:
                    logger.info("No more papers found")
                    break

                # Yield each paper with pagination info
                for paper in papers:
                    paper_data = {
                        "paper": paper,
                        "pagination": {
                            "current_page": current_page + 1,
                            "papers_found": papers_found + 1,
                            "search_url": response.url,
                            "query": query,
                        },
                    }

                    yield paper_data
                    papers_found += 1

                    if papers_found >= max_papers:
                        break

                # Check if there are more pages
                pagination = self._extract_pagination_info(soup)
                if not pagination.get("has_next"):
                    logger.info("No more pages available")
                    break

                current_page += 1

                # Respect rate limiting
                time.sleep(self.delay)

            except requests.RequestException as e:
                logger.error(f"Error fetching page {current_page + 1}: {e}")
                break
            except Exception as e:
                logger.error(f"Unexpected error on page {current_page + 1}: {e}")
                break

    def download_paper_full_content(
        self, doi: str, paper_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Download full content for a paper including landing page and full text.

        Args:
            doi: DOI of the paper
            paper_dir: Directory to save paper files (defaults to DOI-based directory)

        Returns:
            Dictionary with download results and metadata
        """
        try:
            # Create paper directory using the same encoding logic as pygetpapers
            # Remove https://doi.org/ prefix if present, then URL encode
            if paper_dir is None:
                if doi.startswith("https://doi.org/"):
                    doi_clean = doi.replace("https://doi.org/", "")
                else:
                    doi_clean = doi

                # Use the same encoding as pygetpapers download_tools.url_encode_id
                url_encoded_doi = doi_clean.replace("\\", "_").replace("/", "_")
                paper_dir = self.output_dir / url_encoded_doi
            else:
                paper_dir = Path(paper_dir)

            paper_dir.mkdir(parents=True, exist_ok=True)

            # Get paper URL
            paper_url = f"{self.base_url}/content/{doi}"

            logger.info(f"Downloading full content for {doi}")

            # Download landing page (abstract)
            response = self.session.get(paper_url, timeout=30)
            response.raise_for_status()

            # Save landing page HTML
            # Use the same encoding for file names
            if doi.startswith("https://doi.org/"):
                doi_clean = doi.replace("https://doi.org/", "")
            else:
                doi_clean = doi
            url_encoded_doi = doi_clean.replace("\\", "_").replace("/", "_")

            landing_file = paper_dir / "landing.html"
            with open(landing_file, "w", encoding="utf-8") as f:
                f.write(response.text)

            # Parse HTML to extract full text link and additional information
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract full text link
            fulltext_url = self._extract_fulltext_link(soup, doi)
            fulltext_file = None

            # Download full text if link found
            if fulltext_url:
                try:
                    logger.info(f"Downloading full text from {fulltext_url}")
                    fulltext_response = self.session.get(fulltext_url, timeout=30)
                    fulltext_response.raise_for_status()

                    fulltext_file = paper_dir / "fulltext.html"
                    with open(fulltext_file, "w", encoding="utf-8") as f:
                        f.write(fulltext_response.text)

                    logger.info(f"Successfully downloaded full text for {doi}")
                except Exception as e:
                    logger.warning(f"Failed to download full text for {doi}: {e}")
                    fulltext_file = None
            else:
                logger.warning(f"No full text link found for {doi}")

            # Extract PDF link
            pdf_url = self._extract_pdf_link(soup)

            # Extract additional metadata
            metadata = self._extract_paper_metadata(soup, doi)

            # Save metadata
            metadata_file = paper_dir / f"{url_encoded_doi}_metadata.json"
            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            result = {
                "doi": doi,
                "paper_url": paper_url,
                "landing_file": str(landing_file),
                "fulltext_file": str(fulltext_file) if fulltext_file else None,
                "metadata_file": str(metadata_file),
                "pdf_url": pdf_url,
                "fulltext_url": fulltext_url,
                "download_timestamp": datetime.now().isoformat(),
                "landing_size_bytes": landing_file.stat().st_size,
                "fulltext_size_bytes": fulltext_file.stat().st_size if fulltext_file else 0,
                "metadata": metadata,
            }

            logger.info(f"Successfully downloaded {doi} to {paper_dir}")
            return result

        except Exception as e:
            logger.error(f"Error downloading {doi}: {e}")
            return {
                "doi": doi,
                "error": str(e),
                "download_timestamp": datetime.now().isoformat(),
            }

    def _extract_pdf_link(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract PDF download link from paper page."""
        try:
            # Look for PDF links
            pdf_links = soup.find_all("a", href=re.compile(r"\.pdf$"))

            for link in pdf_links:
                href = link.get("href", "")
                if "full.pdf" in href or "biorxiv" in href:
                    return urljoin(self.base_url, href)

            # Fallback: look for any PDF link
            if pdf_links:
                return urljoin(self.base_url, pdf_links[0]["href"])

            return None

        except Exception as e:
            logger.warning(f"Error extracting PDF link: {e}")
            return None

    def _extract_fulltext_link(self, soup: BeautifulSoup, doi: str) -> Optional[str]:
        """Extract full text link from paper landing page."""
        try:
            # Look for the "Full Text" tab link
            # Based on the HTML structure provided, the full text link has:
            # - href containing ".full-text"
            # - text content "Full Text"
            # - class containing "panels-ajax-tab-tab"
            
            fulltext_links = soup.find_all("a", href=re.compile(r"\.full-text$"))
            
            for link in fulltext_links:
                # Check if this is the "Full Text" link
                if "Full Text" in link.get_text(strip=True):
                    href = link.get("href", "")
                    if href:
                        # Convert relative URL to absolute
                        return urljoin(self.base_url, href)
            
            # Alternative: look for any link with "full-text" in href and "Full Text" text
            for link in soup.find_all("a"):
                href = link.get("href", "")
                text = link.get_text(strip=True)
                if "full-text" in href and "Full Text" in text:
                    return urljoin(self.base_url, href)
            
            # Fallback: construct the full text URL based on DOI pattern
            # bioRxiv full text URLs follow pattern: /content/{doi}.full-text
            if "10.1101/" in doi:
                doi_clean = doi.replace("https://doi.org/", "")
                fulltext_url = f"{self.base_url}/content/{doi_clean}.full-text"
                logger.info(f"Constructed fallback full text URL: {fulltext_url}")
                return fulltext_url

            return None

        except Exception as e:
            logger.warning(f"Error extracting full text link: {e}")
            return None

    def _extract_paper_metadata(self, soup: BeautifulSoup, doi: str) -> Dict[str, Any]:
        """Extract comprehensive metadata from paper page."""
        metadata = {"doi": doi, "extracted_at": datetime.now().isoformat()}

        try:
            # Extract title
            title_elem = soup.find(["h1", "h2"], class_=re.compile(r"title"))
            if title_elem:
                metadata["title"] = title_elem.get_text(strip=True)

            # Extract authors
            authors_elem = soup.find(["div", "section"], class_=re.compile(r"author"))
            if authors_elem:
                metadata["authors"] = authors_elem.get_text(strip=True)

            # Extract abstract
            abstract_elem = soup.find(
                ["div", "section"], class_=re.compile(r"abstract")
            )
            if abstract_elem:
                metadata["abstract"] = abstract_elem.get_text(strip=True)

            # Extract subject areas
            subjects_elem = soup.find(["div", "section"], class_=re.compile(r"subject"))
            if subjects_elem:
                metadata["subject_areas"] = [
                    s.strip() for s in subjects_elem.get_text().split(",")
                ]

            # Extract publication date
            date_elem = soup.find(["time", "span"], class_=re.compile(r"date"))
            if date_elem:
                metadata["publication_date"] = date_elem.get_text(strip=True)

            # Extract bioRxiv ID
            id_match = re.search(r"10\.1101/(.+)", doi)
            if id_match:
                metadata["biorxiv_id"] = id_match.group(1)

        except Exception as e:
            logger.warning(f"Error extracting metadata: {e}")

        return metadata

    def _parse_search_results(
        self, soup: BeautifulSoup, max_results: int
    ) -> List[Dict[str, Any]]:
        """Parse search results from HTML."""
        papers = []

        results_list = soup.find("ul", class_="highwire-search-results-list")

        if results_list:
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

        return papers

    def _extract_paper_data(self, paper_elem) -> Optional[Dict[str, Any]]:
        """Extract paper data from search result element."""
        try:
            paper_data = {}

            citation_elem = paper_elem.find("div", class_="highwire-article-citation")
            if not citation_elem:
                return None

            # Extract title and URL
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
                journal_elem = metadata_elem.find(
                    "span", class_="highwire-cite-metadata-journal"
                )
                if journal_elem:
                    paper_data["journal"] = journal_elem.get_text(strip=True)

                pages_elem = metadata_elem.find(
                    "span", class_="highwire-cite-metadata-pages"
                )
                if pages_elem:
                    paper_data["biorxiv_id"] = pages_elem.get_text(strip=True).rstrip(
                        ";"
                    )

                doi_elem = metadata_elem.find(
                    "span", class_="highwire-cite-metadata-doi"
                )
                if doi_elem:
                    doi_text = doi_elem.get_text(strip=True)
                    doi_match = re.search(r"https://doi\.org/(.+)", doi_text)
                    if doi_match:
                        paper_data["doi"] = doi_match.group(1)

            # Extract data attributes
            if citation_elem.get("data-pisa"):
                paper_data["pisa_id"] = citation_elem.get("data-pisa")

            if citation_elem.get("data-apath"):
                paper_data["apath"] = citation_elem.get("data-apath")

            paper_data["extracted_at"] = datetime.now().isoformat()

            return paper_data if paper_data else None

        except Exception as e:
            logger.warning(f"Error extracting paper data: {e}")
            return None

    def _extract_pagination_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract pagination information."""
        pagination = {
            "current_page": 1,
            "total_pages": 1,
            "results_per_page": 10,
            "has_next": False,
            "has_previous": False,
            "next_url": None,
            "previous_url": None,
        }

        pager_elem = soup.find("div", class_="pager-wrapper")

        if pager_elem:
            current_elem = pager_elem.find("li", class_="pager-current")
            if current_elem:
                try:
                    pagination["current_page"] = int(current_elem.get_text(strip=True))
                except ValueError:
                    pass

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

            last_elem = pager_elem.find("li", class_="pager-last")
            if last_elem:
                last_link = last_elem.find("a")
                if last_link:
                    try:
                        title = last_link.get("title", "")
                        page_match = re.search(r"page (\d+)", title)
                        if page_match:
                            pagination["total_pages"] = int(page_match.group(1))
                    except ValueError:
                        pass

        return pagination

    def batch_download_papers(
        self, query: str, max_papers: int = 10, results_per_page: int = 25
    ) -> Dict[str, Any]:
        """
        Perform batch download of papers for a query.

        Args:
            query: Search query
            max_papers: Maximum number of papers to download
            results_per_page: Results per page

        Returns:
            Summary of batch download operation
        """
        logger.info(f"Starting batch download for query: {query}")

        batch_results = {
            "query": query,
            "max_papers": max_papers,
            "start_time": datetime.now().isoformat(),
            "papers_downloaded": [],
            "errors": [],
            "summary": {},
        }

        papers_downloaded = 0

        try:
            for paper_data in self.search_with_pagination(
                query, max_papers, results_per_page
            ):
                paper = paper_data["paper"]
                doi = paper.get("doi")

                if not doi:
                    logger.warning(
                        f"No DOI found for paper: {paper.get('title', 'Unknown')}"
                    )
                    continue

                logger.info(
                    f"Downloading paper {papers_downloaded + 1}/{max_papers}: {doi}"
                )

                # Download full content
                download_result = self.download_paper_full_content(doi)

                if "error" not in download_result:
                    batch_results["papers_downloaded"].append(download_result)
                    papers_downloaded += 1
                else:
                    batch_results["errors"].append(
                        {"doi": doi, "error": download_result["error"]}
                    )

                # Respect rate limiting
                time.sleep(self.delay)

                if papers_downloaded >= max_papers:
                    break

        except Exception as e:
            logger.error(f"Batch download error: {e}")
            batch_results["errors"].append({"type": "batch_error", "error": str(e)})

        # Create summary
        batch_results["end_time"] = datetime.now().isoformat()
        batch_results["summary"] = {
            "total_papers_downloaded": len(batch_results["papers_downloaded"]),
            "total_errors": len(batch_results["errors"]),
            "success_rate": (
                len(batch_results["papers_downloaded"]) / max_papers
                if max_papers > 0
                else 0
            ),
        }

        # Save batch results
        batch_file = (
            self.output_dir
            / f"batch_download_{query.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(batch_file, "w", encoding="utf-8") as f:
            json.dump(batch_results, f, indent=2, ensure_ascii=False)

        logger.info(f"Batch download completed. Results saved to: {batch_file}")
        logger.info(
            f"Summary: {batch_results['summary']['total_papers_downloaded']} papers downloaded, {batch_results['summary']['total_errors']} errors"
        )

        return batch_results


def main():
    """Example usage of the advanced bioRxiv scraper."""
    scraper = BioRxivAdvancedScraper(output_dir="biorxiv_advanced_output", delay=1.0)

    # Example: Download 5 papers for a query
    query = "urban heat island"
    results = scraper.batch_download_papers(query, max_papers=5, results_per_page=25)

    print("Batch download completed!")
    print(f"Papers downloaded: {results['summary']['total_papers_downloaded']}")
    print(f"Errors: {results['summary']['total_errors']}")
    print(f"Success rate: {results['summary']['success_rate']:.1%}")

    # Show downloaded papers
    for paper in results["papers_downloaded"]:
        print(f"\n- {paper['doi']}")
        print(f"  HTML: {paper['html_file']}")
        print(f"  PDF: {paper['pdf_url']}")
        print(f"  Size: {paper['file_size_bytes']:,} bytes")


if __name__ == "__main__":
    main()
