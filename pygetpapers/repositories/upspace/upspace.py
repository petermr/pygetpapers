"""
UPSpace repository implementation for DSpace REST API.

UPSpace is the University of Pretoria's institutional repository built on DSpace.
This implementation uses the DSpace REST API for search and file downloads.
"""

import json
import logging
import re
import time
import html
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from pygetpapers.core.download_tools import DownloadTools
from pygetpapers.core.file_utils import FileUtils
from pygetpapers.core.metadata_extractor import MetadataExtractor
from pygetpapers.core.repositoryinterface import RepositoryInterface


class UPSpace(RepositoryInterface):
    """UPSpace repository implementation using DSpace REST API."""

    def __init__(self):
        """Initialize UPSpace repository."""
        super().__init__()
        self.download_tools = DownloadTools("upspace")
        self.output_dir = "."  # Default output directory
        self.base_url = "https://repository.up.ac.za/server/api"
        self.search_url = "https://repository.up.ac.za/server/api/discover/search/objects"
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "pygetpapers/2.0 " "(https://github.com/pygetpapers/pygetpapers)"
                ),
                "Accept": "application/json",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
            }
        )

        # Rate limiting
        self.request_delay = 1.0  # seconds between requests
        self.last_request_time = 0

        # SDG Classification mappings
        self.sdg_mappings = {
            "SDG-01": "No Poverty",
            "SDG-02": "Zero Hunger",
            "SDG-03": "Good Health and Well-being",
            "SDG-04": "Quality Education",
            "SDG-05": "Gender Equality",
            "SDG-06": "Clean Water and Sanitation",
            "SDG-07": "Affordable and Clean Energy",
            "SDG-08": "Decent Work and Economic Growth",
            "SDG-09": "Industry, Innovation and Infrastructure",
            "SDG-10": "Reduced Inequalities",
            "SDG-11": "Sustainable Cities and Communities",
            "SDG-12": "Responsible Consumption and Production",
            "SDG-13": "Climate Action",
            "SDG-14": "Life Below Water",
            "SDG-15": "Life on Land",
            "SDG-16": "Peace, Justice and Strong Institutions",
            "SDG-17": "Partnerships for the Goals"
        }

    def _rate_limit(self):
        """Implement rate limiting between requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.request_delay:
            sleep_time = self.request_delay - time_since_last
            time.sleep(sleep_time)
        self.last_request_time = time.time()

    def _make_request(self, url: str, params: Optional[Dict[str, Any]] = None) -> Optional[requests.Response]:
        """Make a rate-limited request to the UPSpace API."""
        self._rate_limit()
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed for {url}: {e}")
            return None

    def _extract_metadata(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata from DSpace item JSON response."""
        metadata = {}
        
        # Extract basic fields
        metadata["title"] = self._extract_field(item_data, "dc.title")
        metadata["authors"] = self._extract_field(item_data, "dc.contributor.author", multiple=True)
        metadata["abstract"] = self._extract_field(item_data, "dc.description.abstract")
        metadata["year"] = self._extract_field(item_data, "dc.date.issued")
        metadata["publisher"] = self._extract_field(item_data, "dc.publisher")
        metadata["type"] = self._extract_field(item_data, "dc.type")
        
        # Extract identifiers
        handle_url = self._extract_field(item_data, "dc.identifier.uri")
        if handle_url:
            metadata["handle_url"] = handle_url
            # Extract handle ID for article ID generation
            handle_match = re.search(r'handle\.net/(\d+/\d+)', handle_url)
            if handle_match:
                metadata["handle_id"] = handle_match.group(1)
        
        doi = self._extract_field(item_data, "dc.identifier.other")
        if doi and doi.startswith("10."):
            metadata["doi"] = doi
        
        # Extract subjects/keywords
        subjects = self._extract_field(item_data, "dc.subject", multiple=True)
        metadata["keywords"] = subjects if subjects else []
        
        # Extract SDG classifications
        sdg_data = self._extract_field(item_data, "dc.description.sdg", multiple=True)
        sdg_classifications = []
        if sdg_data:
            for sdg in sdg_data:
                # Extract SDG number and description
                match = re.search(r'SDG-(\d+):\s*(.+)', sdg)
                if match:
                    sdg_num = match.group(1)
                    sdg_desc = match.group(2).strip()
                    sdg_classifications.append(f"SDG-{sdg_num}: {sdg_desc}")
        
        metadata["sdg_classifications"] = sdg_classifications
        
        # Extract language
        language = self._extract_field(item_data, "dc.language.iso")
        metadata["language"] = language if language else "en"
        
        # Extract item UUID for API calls
        metadata["uuid"] = item_data.get("uuid")
        metadata["id"] = item_data.get("id")
        
        return metadata

    def _extract_field(self, item_data: Dict[str, Any], field_name: str, multiple: bool = False) -> Any:
        """Extract a field from DSpace metadata structure."""
        metadata = item_data.get("metadata", {})
        field_data = metadata.get(field_name, [])
        
        if not field_data:
            return [] if multiple else None
        
        if multiple:
            return [item.get("value", "") for item in field_data if item.get("value")]
        else:
            return field_data[0].get("value") if field_data else None

    def _generate_article_id(self, article: Dict[str, Any]) -> str:
        """Generate a unique article ID for file naming."""
        # Prefer Handle ID over DOI for consistency
        if article.get("handle_id"):
            return f"UPSPACE_{article['handle_id'].replace('/', '_')}"
        elif article.get("doi"):
            # Clean DOI for filename
            doi_clean = re.sub(r'[^\w\-\.]', '_', article["doi"])
            return f"DOI_{doi_clean}"
        elif article.get("uuid"):
            return f"UUID_{article['uuid']}"
        else:
            # Fallback to title-based ID
            title = article.get("title", "Unknown")
            title_clean = re.sub(r'[^\w\-\.]', '_', title)[:50]
            return f"TITLE_{title_clean}"

    def _get_item_bundles(self, item_uuid: str) -> Optional[Dict[str, Any]]:
        """Get bundles for a specific item."""
        bundles_url = f"{self.base_url}/core/items/{item_uuid}/bundles"
        response = self._make_request(bundles_url)
        if response:
            return response.json()
        return None

    def _get_bundle_bitstreams(self, bundle_uuid: str) -> Optional[Dict[str, Any]]:
        """Get bitstreams for a specific bundle."""
        bitstreams_url = f"{self.base_url}/core/bundles/{bundle_uuid}/bitstreams"
        response = self._make_request(bitstreams_url)
        if response:
            return response.json()
        return None

    def _download_bitstream(self, bitstream_uuid: str, output_path: Path) -> bool:
        """Download a bitstream to the specified path."""
        content_url = f"{self.base_url}/core/bitstreams/{bitstream_uuid}/content"
        response = self._make_request(content_url)
        if response and response.status_code == 200:
            try:
                with open(output_path, "wb") as f:
                    f.write(response.content)
                return True
            except IOError as e:
                logging.error(f"Failed to save file {output_path}: {e}")
                return False
        return False

    def search_articles(self, query: str, max_results: int = 20) -> List[Dict[str, Any]]:
        """Search for articles using the UPSpace API."""
        logging.info(f"Searching UPSpace for: {query}")
        
        articles = []
        page = 0
        page_size = min(max_results, 20)  # API limit per page
        
        while len(articles) < max_results:
            params = {
                "dsoType": "ITEM",
                "sort": "dc.date.accessioned,DESC",
                "page": page,
                "size": page_size,
                "query": query
            }
            
            response = self._make_request(self.search_url, params)
            if not response:
                break
            
            try:
                data = response.json()
                
                # Extract search results from the correct path in the response
                search_results = []
                if '_embedded' in data and 'searchResult' in data['_embedded']:
                    search_result = data['_embedded']['searchResult']
                    if '_embedded' in search_result and 'objects' in search_result['_embedded']:
                        search_results = search_result['_embedded']['objects']
                
                if not search_results:
                    break
                
                # Process each search result
                for result in search_results:
                    if len(articles) >= max_results:
                        break
                    
                    # The item data is already embedded in the search result
                    if '_embedded' in result and 'indexableObject' in result['_embedded']:
                        item_data = result['_embedded']['indexableObject']
                        metadata = self._extract_metadata(item_data)
                        if metadata:
                            articles.append(metadata)
                
                page += 1
                
            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse search results JSON: {e}")
                break
        
        logging.info(f"Found {len(articles)} articles")
        return articles

    def download_article(self, article: Dict[str, Any], output_dir: str) -> bool:
        """Download an article and its metadata."""
        if not article.get("uuid"):
            logging.error("Article missing UUID")
            return False
        
        article_id = self._generate_article_id(article)
        article_dir = Path(output_dir, article_id)
        
        try:
            article_dir.mkdir(parents=True, exist_ok=True)
        except (OSError, IOError) as e:
            logging.error(f"Failed to create directory {article_dir}: {e}")
            return False
        
        logging.info(f"Downloading article: {article_id}")
        
        # Download metadata
        metadata_file = Path(article_dir, "metadata.json")
        try:
            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(article, f, indent=2, ensure_ascii=False)
        except IOError as e:
            logging.error(f"Failed to save metadata: {e}")
            return False
        
        # Download full text if available
        bundles_data = self._get_item_bundles(article["uuid"])
        if bundles_data and isinstance(bundles_data, dict):
            # Bundles are in _embedded.bundles, not page
            bundles = bundles_data.get("_embedded", {}).get("bundles", [])
            for bundle in bundles:
                if isinstance(bundle, dict) and bundle.get("name") == "ORIGINAL":
                    bundle_uuid = bundle.get("uuid")
                    if bundle_uuid:
                        bitstreams_data = self._get_bundle_bitstreams(bundle_uuid)
                        if bitstreams_data and isinstance(bitstreams_data, dict):
                            # Bitstreams are in _embedded.bitstreams, not page
                            bitstreams = bitstreams_data.get("_embedded", {}).get("bitstreams", [])
                            for bitstream in bitstreams:
                                if isinstance(bitstream, dict):
                                    filename = bitstream.get("name", "")
                                    if filename.lower().endswith('.pdf'):
                                        pdf_path = Path(article_dir, "fulltext.pdf")
                                        bitstream_uuid = bitstream.get("uuid")
                                        if bitstream_uuid and self._download_bitstream(bitstream_uuid, pdf_path):
                                            logging.info(f"Downloaded PDF: {pdf_path}")
                                            return True
        
        logging.warning(f"No PDF found for article: {article_id}")
        return True  # Return True even without PDF as metadata was saved

    def upspace(self, query: str, output_dir: str, max_results: int = 20, **kwargs) -> None:
        """Main method for UPSpace search and download."""
        logging.info(f"Starting UPSpace search for: {query}")
        
        # Set output directory
        self.output_dir = output_dir
        
        # Search for articles
        articles = self.search_articles(query, max_results)
        
        if not articles:
            logging.warning("No articles found")
            return
        
        # Download articles
        downloaded_count = 0
        for article in articles:
            if self.download_article(article, output_dir):
                downloaded_count += 1
        
        logging.info(f"Downloaded {downloaded_count} out of {len(articles)} articles")
        
        # Generate DataTables
        if articles:
            self._create_upspace_datatables_html(articles)

    def update(self, **kwargs) -> None:
        """Update functionality - not implemented for UPSpace."""
        logging.warning("Update functionality not implemented for UPSpace")

    def noexecute(self, **kwargs) -> None:
        """No-execute mode - not implemented for UPSpace."""
        logging.warning("No-execute mode not implemented for UPSpace")

    def apipaperdownload(self, **kwargs) -> None:
        """API paper download - not implemented for UPSpace."""
        logging.warning("API paper download not implemented for UPSpace")

    def supports_xml2html(self) -> bool:
        """Check if XML to HTML conversion is supported."""
        return False

    def get_xml2html_converters(self) -> List[str]:
        """Get available XML to HTML converters."""
        return []

    def _create_upspace_datatables_html(self, articles: List[Dict[str, Any]]) -> None:
        """Create DataTables HTML for UPSpace articles."""
        logging.info(f"Creating DataTables for {len(articles)} articles")

        # Read the template
        template_path = Path(Path(__file__).parent, "templates", "upspace_datatables.html")
        if not template_path.exists():
            logging.error(f"Template not found: {template_path}")
            return

        with open(template_path, "r", encoding="utf-8") as f:
            template_content = f.read()

        # Generate table rows
        table_rows = []
        for article in articles:
            article_id = self._generate_article_id(article)

            # Format authors
            authors = article.get("authors", [])
            authors_str = "; ".join(authors) if authors else "Unknown"

            # Format SDG badges
            sdg_badges = []
            for sdg in article.get("sdg_classifications", []):
                # Extract SDG number from "SDG-13: Climate Action"
                match = re.search(r'SDG-(\d+)', sdg)
                if match:
                    sdg_num = match.group(1)
                    sdg_badges.append(f'<span class="sdg-badge sdg-{sdg_num}">{sdg_num}</span>')

            sdg_html = " ".join(sdg_badges) if sdg_badges else "None"

            # Format keywords
            keywords = article.get("keywords", [])
            keywords_str = "; ".join(keywords) if keywords else "None"

            # Format identifiers
            identifiers = []
            if article.get("handle_url"):
                identifiers.append(f'<div class="handle-url">Handle: <a href="{article["handle_url"]}" target="_blank">{article["handle_url"]}</a></div>')
            if article.get("doi"):
                identifiers.append(f'<div class="doi-link">DOI: <a href="https://doi.org/{article["doi"]}" target="_blank">{article["doi"]}</a></div>')

            identifiers_html = "".join(identifiers) if identifiers else "None"

            # Format local files
            local_files = []
            pdf_path = Path(self.output_dir, article_id, "fulltext.pdf")
            if pdf_path.exists():
                local_files.append(f'<a href="{article_id}/fulltext.pdf" class="btn btn-success" target="_blank">PDF</a>')

            metadata_path = Path(self.output_dir, article_id, "metadata.json")
            if metadata_path.exists():
                local_files.append(f'<a href="{article_id}/metadata.json" class="btn btn-info" target="_blank">JSON</a>')

            local_files_html = " ".join(local_files) if local_files else "None"

            # Create table row
            row = f"""
                <tr>
                    <td>{html.escape(article_id)}</td>
                    <td>{html.escape(article.get('title', 'No title'))}</td>
                    <td class="authors-cell">{html.escape(authors_str)}</td>
                    <td>{html.escape(str(article.get('year', 'Unknown')))}</td>
                    <td class="abstract-cell">{html.escape(article.get('abstract') or 'No abstract')}</td>
                    <td class="sdg-cell">{sdg_html}</td>
                    <td class="keywords">{html.escape(keywords_str)}</td>
                    <td>{identifiers_html}</td>
                    <td class="url-cell">{local_files_html}</td>
                </tr>
            """
            table_rows.append(row)

        # Replace template placeholders
        html_content = template_content.replace("{{TABLE_ROWS}}", "\n".join(table_rows))
        html_content = html_content.replace("{{QUERY}}", "UPSpace Search")

        # Save DataTables HTML
        datatables_file = Path(self.output_dir, "upspace_datatables.html")
        with open(datatables_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        logging.info(f"DataTables saved to: {datatables_file}")

        # Create index file
        self._create_upspace_index_html(articles)

    def _create_upspace_index_html(self, articles: List[Dict[str, Any]]) -> None:
        """Create index HTML for UPSpace results."""
        logging.info("Creating UPSpace index HTML")

        # Read the template
        template_path = Path(Path(__file__).parent, "templates", "upspace_index.html")
        if not template_path.exists():
            logging.error(f"Template not found: {template_path}")
            return

        with open(template_path, "r", encoding="utf-8") as f:
            template_content = f.read()

        # Count SDG articles
        sdg_articles = sum(1 for article in articles if article.get("sdg_classifications"))

        # Replace template placeholders
        html_content = template_content.replace("{{TOTAL_ARTICLES}}", str(len(articles)))
        html_content = html_content.replace("{{DOWNLOADED_ARTICLES}}", str(len(articles)))
        html_content = html_content.replace("{{SDG_ARTICLES}}", str(sdg_articles))
        html_content = html_content.replace("{{QUERY}}", "UPSpace Search")

        # Save index HTML
        index_file = Path(self.output_dir, "index.html")
        with open(index_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        logging.info(f"Index HTML saved to: {index_file}") 