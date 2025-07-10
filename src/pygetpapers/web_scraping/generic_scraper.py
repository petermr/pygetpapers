"""
Generic Web Scraper for Pygetpapers

This module provides the core generic web scraper that orchestrates the entire
scraping process using configuration-based components. It handles HTTP requests,
HTML parsing, data extraction, and transformation.
"""

import logging
from typing import Any, Dict, List, Optional, Union
from urllib.parse import quote_plus, urljoin, urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config_parser import ScrapingConfigParser
from .data_transformer import DataTransformer
from .html_parser import ConfigurableHTMLParser

logger = logging.getLogger(__name__)


class GenericWebScraper:
    """
    Generic web scraper that uses configuration-based components.

    This class orchestrates the entire scraping process:
    1. Load configuration for the repository
    2. Make HTTP requests with proper rate limiting
    3. Parse HTML using configurable selectors
    4. Extract and transform data
    5. Handle pagination and errors
    """

    def __init__(self, config_parser: Optional[ScrapingConfigParser] = None):
        """
        Initialize the generic web scraper.

        Args:
            config_parser: Configuration parser instance
        """
        self.config_parser = config_parser or ScrapingConfigParser()
        self.html_parser = ConfigurableHTMLParser()
        self.data_transformer = DataTransformer()
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """
        Create a requests session with retry logic and proper headers.

        Returns:
            Configured requests session
        """
        session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Set default headers
        session.headers.update(
            {
                "User-Agent": "pygetpapers-web-scraper/1.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
            }
        )

        return session

    def search_papers(
        self,
        repo_name: str,
        query: str,
        max_results: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Search for papers using the specified repository.

        Args:
            repo_name: Name of the repository to search
            query: Search query string
            max_results: Maximum number of results to return
            filters: Additional filters to apply

        Returns:
            Dictionary with search results and metadata
        """
        # Load repository configuration
        config = self.config_parser.load_repository_config(repo_name)
        if not config:
            raise ValueError(f"Repository configuration not found: {repo_name}")

        # Validate configuration
        errors = self.config_parser.validate_config(config)
        if errors:
            raise ValueError(f"Configuration errors for {repo_name}: {errors}")

        # Check if repository is enabled
        if not config.get("enabled", False):
            raise ValueError(f"Repository {repo_name} is not enabled")

        # Initialize results
        results = {
            "repository": repo_name,
            "query": query,
            "papers": [],
            "metadata": {
                "total_results": 0,
                "pages_scraped": 0,
                "errors": [],
                "warnings": [],
            },
        }

        try:
            # Build search URL
            search_url = self._build_search_url(config, query, filters)
            logger.info(f"Searching {repo_name} with URL: {search_url}")

            # Start scraping
            current_page = 1
            total_papers = 0

            while True:
                # Check if we've reached the maximum results
                if max_results and total_papers >= max_results:
                    break

                # Make request
                page_url = self._build_page_url(search_url, current_page, config)
                html_content = self._make_request(page_url, config)

                if not html_content:
                    logger.warning(f"No content received for page {current_page}")
                    break

                # Parse HTML
                soup = self.html_parser.parse_html(html_content)

                # Find results container
                results_container = self.html_parser.find_results_container(
                    soup, config["selectors"]["results_container"]
                )

                if not results_container:
                    logger.warning(f"No results container found on page {current_page}")
                    break

                # Extract paper elements
                paper_elements = self.html_parser.find_paper_elements(
                    results_container, config["selectors"]["paper_entry"]
                )

                if not paper_elements:
                    logger.info(f"No more papers found on page {current_page}")
                    break

                # Extract data from each paper
                page_papers = []
                for paper_element in paper_elements:
                    try:
                        paper_data = self._extract_paper_data(paper_element, config)
                        if paper_data:
                            page_papers.append(paper_data)
                            total_papers += 1

                            # Check if we've reached the maximum results
                            if max_results and total_papers >= max_results:
                                break
                    except Exception as e:
                        error_msg = f"Error extracting paper data: {e}"
                        logger.error(error_msg)
                        results["metadata"]["errors"].append(error_msg)

                results["papers"].extend(page_papers)
                results["metadata"]["pages_scraped"] = current_page

                # Check for pagination
                if not self._has_next_page(soup, config):
                    break

                current_page += 1

                # Rate limiting
                self._rate_limit(config)

            # Update metadata
            results["metadata"]["total_results"] = len(results["papers"])

            logger.info(f"Scraped {len(results['papers'])} papers from {repo_name}")

        except Exception as e:
            error_msg = f"Error during scraping: {e}"
            logger.error(error_msg)
            results["metadata"]["errors"].append(error_msg)

        return results

    def _build_search_url(
        self,
        config: Dict[str, Any],
        query: str,
        filters: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Build the search URL with query and filters.

        Args:
            config: Repository configuration
            query: Search query
            filters: Additional filters

        Returns:
            Complete search URL
        """
        search_url = config["search_url"]

        # Encode query based on configuration
        encoding = config.get("search", {}).get("encoding", "url_encode")
        if encoding == "url_encode":
            encoded_query = quote_plus(query)
        elif encoding == "double_encode":
            encoded_query = quote_plus(quote_plus(query))
        else:
            encoded_query = query

        # Replace query placeholder
        search_url = search_url.replace("{query}", encoded_query)

        # Add filters if provided
        if filters and "filters" in config:
            for filter_name, filter_value in filters.items():
                if filter_name in config["filters"]:
                    placeholder = f"{{{filter_name}}}"
                    if placeholder in search_url:
                        search_url = search_url.replace(placeholder, str(filter_value))

        # Ensure absolute URL
        if not search_url.startswith(("http://", "https://")):
            search_url = urljoin(config["base_url"], search_url)

        return search_url

    def _build_page_url(self, base_url: str, page: int, config: Dict[str, Any]) -> str:
        """
        Build URL for a specific page.

        Args:
            base_url: Base search URL
            page: Page number
            config: Repository configuration

        Returns:
            Page URL
        """
        if page == 1:
            return base_url

        # Check if pagination is configured
        if "pagination" not in config:
            return base_url

        pagination_config = config["pagination"]

        # Try different pagination strategies
        if "page_parameter" in pagination_config:
            # Add page parameter to URL
            import urllib.parse

            parsed = urllib.parse.urlparse(base_url)
            params = urllib.parse.parse_qs(parsed.query)
            params[pagination_config["page_parameter"]] = [str(page)]
            new_query = urllib.parse.urlencode(params, doseq=True)
            return urllib.parse.urlunparse(
                (
                    parsed.scheme,
                    parsed.netloc,
                    parsed.path,
                    parsed.params,
                    new_query,
                    parsed.fragment,
                )
            )
        elif "page_pattern" in pagination_config:
            # Replace page pattern in URL
            pattern = pagination_config["page_pattern"]
            return base_url.replace(pattern, str(page))
        else:
            # Default: append page number
            separator = "&" if "?" in base_url else "?"
            return f"{base_url}{separator}page={page}"

    def _make_request(self, url: str, config: Dict[str, Any]) -> Optional[str]:
        """
        Make HTTP request with proper error handling and rate limiting.

        Args:
            url: URL to request
            config: Repository configuration

        Returns:
            HTML content or None if request failed
        """
        try:
            # Set custom headers if configured
            if "user_agent" in config:
                self.session.headers["User-Agent"] = config["user_agent"]

            # Make request
            timeout = config.get("timeout", 30)
            response = self.session.get(url, timeout=timeout)

            # Check response
            response.raise_for_status()

            # Check content type
            content_type = response.headers.get("content-type", "").lower()
            if (
                "text/html" not in content_type
                and "application/xhtml" not in content_type
            ):
                logger.warning(f"Unexpected content type: {content_type}")

            return response.text

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            return None

    def _extract_paper_data(
        self, paper_element, config: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Extract paper data from an HTML element.

        Args:
            paper_element: BeautifulSoup element containing paper data
            config: Repository configuration

        Returns:
            Dictionary with paper data or None if extraction failed
        """
        try:
            # Extract basic fields
            paper_data = {}
            selectors = config["selectors"]

            # Extract required fields
            for field_name, selector_config in selectors.items():
                if field_name in ["results_container", "paper_entry"]:
                    continue  # Skip container selectors

                value = self.html_parser.extract_field(paper_element, selector_config)
                if value:
                    paper_data[field_name] = value

            # Apply transformations
            if "transformations" in config:
                paper_data = self.data_transformer.transform_data(
                    paper_data, config["transformations"]
                )

            # Validate required fields
            required_fields = config.get("output", {}).get("required_fields", [])
            for field in required_fields:
                if field not in paper_data or not paper_data[field]:
                    logger.debug(f"Missing required field: {field}")
                    return None

            # Add metadata
            paper_data["_source"] = config.get("name", "Unknown")
            paper_data["_scraped_at"] = time.strftime("%Y-%m-%d %H:%M:%S")

            return paper_data

        except Exception as e:
            logger.error(f"Error extracting paper data: {e}")
            return None

    def _has_next_page(self, soup, config: Dict[str, Any]) -> bool:
        """
        Check if there's a next page available.

        Args:
            soup: BeautifulSoup object of current page
            config: Repository configuration

        Returns:
            True if next page is available, False otherwise
        """
        if "pagination" not in config:
            return False

        pagination_config = config["pagination"]

        # Check for next button
        if "next_button" in pagination_config:
            next_selector = pagination_config["next_button"]
            next_element = self.html_parser._find_element(soup, next_selector)
            if next_element:
                return True

        # Check for page numbers
        if "page_numbers" in pagination_config:
            page_selector = pagination_config["page_numbers"]
            page_elements = self.html_parser._find_elements(soup, page_selector)

            # Look for next page number
            current_page = 1  # This should be extracted from current page
            for element in page_elements:
                try:
                    page_num = int(element.get_text().strip())
                    if page_num > current_page:
                        return True
                except ValueError:
                    continue

        return False

    def _rate_limit(self, config: Dict[str, Any]):
        """
        Apply rate limiting based on configuration.

        Args:
            config: Repository configuration
        """
        rate_limit = config.get("rate_limit", 2.0)
        if rate_limit > 0:
            time.sleep(rate_limit)

    def save_results(
        self, results: Dict[str, Any], output_dir: str, format: str = "json"
    ) -> str:
        """
        Save search results to files.

        Args:
            results: Search results dictionary
            output_dir: Output directory path
            format: Output format ('json', 'csv', 'xml')

        Returns:
            Path to the saved file
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        if format == "json":
            return self._save_json(results, output_path)
        elif format == "csv":
            return self._save_csv(results, output_path)
        elif format == "xml":
            return self._save_xml(results, output_path)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _save_json(self, results: Dict[str, Any], output_path: Path) -> str:
        """Save results as JSON file."""
        filename = f"{results['repository']}_results.json"
        filepath = output_path / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        logger.info(f"Results saved to: {filepath}")
        return str(filepath)

    def _save_csv(self, results: Dict[str, Any], output_path: Path) -> str:
        """Save results as CSV file."""
        import pandas as pd

        filename = f"{results['repository']}_results.csv"
        filepath = output_path / filename

        # Convert papers to DataFrame
        papers_df = pd.DataFrame(results["papers"])

        # Add metadata as additional columns
        for key, value in results["metadata"].items():
            if isinstance(value, (str, int, float)):
                papers_df[f"metadata_{key}"] = value

        papers_df.to_csv(filepath, index=False, encoding="utf-8")

        logger.info(f"Results saved to: {filepath}")
        return str(filepath)

    def _save_xml(self, results: Dict[str, Any], output_path: Path) -> str:
        """Save results as XML file."""
        filename = f"{results['repository']}_results.xml"
        filepath = output_path / filename

        # Create XML structure
        import xml.etree.ElementTree as ET

        root = ET.Element("search_results")
        root.set("repository", results["repository"])
        root.set("query", results["query"])
        root.set("total_results", str(results["metadata"]["total_results"]))

        # Add papers
        papers_elem = ET.SubElement(root, "papers")
        for paper in results["papers"]:
            paper_elem = ET.SubElement(papers_elem, "paper")
            for key, value in paper.items():
                if not key.startswith("_"):
                    field_elem = ET.SubElement(paper_elem, key)
                    field_elem.text = str(value)

        # Add metadata
        metadata_elem = ET.SubElement(root, "metadata")
        for key, value in results["metadata"].items():
            meta_elem = ET.SubElement(metadata_elem, key)
            meta_elem.text = str(value)

        # Write XML file
        tree = ET.ElementTree(root)
        tree.write(filepath, encoding="utf-8", xml_declaration=True)

        logger.info(f"Results saved to: {filepath}")
        return str(filepath)

    def get_repository_info(self, repo_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a repository.

        Args:
            repo_name: Name of the repository

        Returns:
            Repository information dictionary or None if not found
        """
        return self.config_parser.get_repository_info(repo_name)

    def list_available_repositories(self) -> List[str]:
        """
        Get list of available repositories.

        Returns:
            List of repository names
        """
        return self.config_parser.get_available_repositories()

    def validate_repository(self, repo_name: str) -> List[str]:
        """
        Validate repository configuration.

        Args:
            repo_name: Name of the repository

        Returns:
            List of validation errors
        """
        config = self.config_parser.load_repository_config(repo_name)
        if not config:
            return [f"Repository configuration not found: {repo_name}"]

        return self.config_parser.validate_config(config)
