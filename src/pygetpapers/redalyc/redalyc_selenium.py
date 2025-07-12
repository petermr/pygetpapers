"""
Selenium-based Redalyc scraper for dynamic search functionality.

This module provides browser automation capabilities for Redalyc,
allowing us to interact with the AngularJS search interface.
"""

import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

from pygetpapers.abstract_repository import AbstractRepository
from pygetpapers.download_tools import DownloadTools
from pygetpapers.metadata_extractor import MetadataExtractor
from pygetpapers.file_utils import FileUtils


class RedalycSelenium(AbstractRepository):
    """Redalyc repository implementation using Selenium for dynamic content."""

    def __init__(self, headless: bool = True):
        super().__init__("redalyc_selenium", {
            "repository_name": "redalyc_selenium",
            "api_client": {"type": "requests"},  # Use requests to satisfy AbstractRepository
            "response_structure": {"total_results": "total_hits", "items": "total_json_output"},
            "content_types": ["html", "pdf", "xml"],
            "paper_key": "url",
            "xml2html_supported": False,
            "xml2html_converters": []
        })
        self.download_tools = DownloadTools("redalyc_selenium")
        # Add these two lines for search compatibility
        self.base_url = "https://redalyc.org"
        self.search_url = "https://redalyc.org/redalyc/search"
        self.headless = headless
        self.driver = None
        self.wait_timeout = 10
        
        # Initialize browser
        try:
            self._init_driver()
        except Exception as e:
            logging.error(f"Failed to initialize WebDriver: {e}")
            # Don't raise here, let the class be created but mark driver as None
            self.driver = None

    def _init_driver(self):
        """Initialize the Chrome WebDriver."""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
        
        # Additional options for stability
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=pygetpapers/2.0 (https://github.com/pygetpapers/pygetpapers)")
        
        # Disable images and CSS for faster loading
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--disable-css")
        
        # Initialize driver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        logging.info("Selenium WebDriver initialized successfully")

    def _wait_for_element(self, by: By, value: str, timeout: int = None) -> Optional[Any]:
        """Wait for an element to be present on the page."""
        if timeout is None:
            timeout = self.wait_timeout
            
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.presence_of_element_located((by, value)))
            return element
        except TimeoutException:
            logging.warning(f"Element not found: {by}={value}")
            return None

    def _wait_for_elements(self, by: By, value: str, timeout: int = None) -> List[Any]:
        """Wait for elements to be present on the page."""
        if timeout is None:
            timeout = self.wait_timeout
            
        try:
            wait = WebDriverWait(self.driver, timeout)
            elements = wait.until(EC.presence_of_all_elements_located((by, value)))
            return elements
        except TimeoutException:
            logging.warning(f"Elements not found: {by}={value}")
            return []

    def search_articles(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for articles on Redalyc using Selenium.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of article metadata dictionaries
        """
        logging.info(f"Searching Redalyc with Selenium for: {query}")
        
        try:
            # Navigate to Redalyc homepage
            self.driver.get(self.base_url)
            logging.info("Loaded Redalyc homepage")
            
            # Wait for page to load
            time.sleep(2)
            
            # Find and fill the search input
            search_input = self._wait_for_element(By.ID, "input-articulo")
            if not search_input:
                logging.error("Search input not found")
                return []
            
            # Clear and fill search input
            search_input.clear()
            search_input.send_keys(query)
            logging.info(f"Entered search query: {query}")
            
            # Submit search (press Enter)
            search_input.send_keys(Keys.RETURN)
            logging.info("Submitted search")
            
            # Wait for search results to load
            time.sleep(3)
            
            # Extract article links from current page
            article_links = self._extract_article_links_from_page()
            logging.info(f"Found {len(article_links)} article links from search")
            
            # Limit results
            article_links = article_links[:max_results]
            
            # Extract metadata for each article
            articles = []
            for link in article_links:
                # Navigate to the article page to extract metadata
                try:
                    self.driver.get(link)
                    time.sleep(2)
                    metadata = self._extract_article_metadata_from_page(link)
                    if metadata:
                        articles.append(metadata)
                        logging.info(f"Extracted metadata for: {metadata.get('title', 'Unknown title')}")
                except Exception as e:
                    logging.warning(f"Failed to extract metadata from {link}: {e}")
                    # Create basic metadata with URL
                    articles.append({
                        'url': link,
                        'title': 'Unknown title',
                        'authors': [],
                        'abstract': '',
                        'journal': '',
                        'year': '',
                        'doi': '',
                        'keywords': [],
                        'language': '',
                        'pdf_url': '',
                        'xml_url': ''
                    })
            
            return articles
            
        except Exception as e:
            logging.error(f"Error during Selenium search: {e}")
            return []

    def _extract_article_links_from_page(self) -> List[str]:
        """Extract article links from the current page."""
        article_links = []
        
        try:
            # Look for article links with various selectors
            selectors = [
                'a[href*="/articulo.oa"]',
                'a[href*="/journal/"]',
                '.result-item a',
                '.article-link',
                'a[href*="id="]'
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        href = element.get_attribute('href')
                        if href and href not in article_links:
                            # Filter out non-article links
                            if self._is_valid_article_link(href):
                                article_links.append(href)
                except Exception as e:
                    logging.debug(f"Selector {selector} failed: {e}")
                    continue
            
            logging.info(f"Extracted {len(article_links)} article links")
            return article_links
            
        except Exception as e:
            logging.error(f"Error extracting article links: {e}")
            return []
    
    def _is_valid_article_link(self, href: str) -> bool:
        """Check if a link is a valid article link."""
        # Must be a Redalyc article link
        if not href.startswith('https://www.redalyc.org/articulo.oa'):
            return False
        
        # Must have an ID parameter
        if 'id=' not in href:
            return False
        
        # Filter out sharing links
        if 'facebook.com' in href or 'twitter.com' in href or 'linkedin.com' in href:
            return False
        
        # Filter out citation/export links
        if 'comocitar' in href or 'exportarcita' in href:
            return False
        
        return True

    def _extract_article_metadata_from_page(self, article_url: str) -> Optional[Dict[str, Any]]:
        """Extract metadata from an article page using Selenium."""
        if not self.driver:
            logging.error("WebDriver not initialized")
            return None

        try:
            # Navigate to article page
            self.driver.get(article_url)
            time.sleep(2)
            
            # Get page source for metadata extraction
            page_source = self.driver.page_source
            
            # Use the centralized metadata extractor
            metadata = MetadataExtractor.extract_all_metadata(page_source, article_url)
            
            return metadata
            
        except Exception as e:
            logging.error(f"Error extracting metadata from {article_url}: {e}")
            return None

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
        Main method to search and download articles from Redalyc using Selenium.
        
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
        logging.info("Starting Redalyc Selenium search and download")
        
        # Search for articles
        articles = self.search_articles(query, cutoff_size)
        
        if not articles:
            logging.warning("No articles found for the given query")
            return {
                'new_results': {'total_hits': 0, 'total_json_output': []},
                'updated_dict': {}
            }
        
        # Convert list to dictionary format expected by _make_metadata_json_files_for_paper
        # Use article IDs as keys instead of URLs for cleaner directory names
        articles_with_ids = []
        for article in articles:
            # Extract article ID from URL
            url = article.get('url', '')
            article_id = None
            if url and 'redalyc.org/articulo.oa?id=' in url:
                import re
                match = re.search(r'id=(\d+)', url)
                if match:
                    article_id = match.group(1)
            
            if article_id:
                article['article_id'] = article_id
                articles_with_ids.append(article)
            else:
                # Fallback to using URL hash
                article['article_id'] = str(hash(url))
                articles_with_ids.append(article)
        
        articles_dict = self.download_tools._make_dict_from_list(articles_with_ids, paper_key='article_id')
        
        # Add download status keys
        for paper in articles_dict:
            self.download_tools._add_download_status_keys(paper, articles_dict)
        
        # Prepare results structure
        results = {
            'new_results': {
                'total_hits': len(articles),
                'total_json_output': articles_dict
            },
            'updated_dict': {}
        }
        
        # Download articles if requested
        if makehtml or makexml:
            import os
            output_dir = os.getcwd()
            for article in articles:
                self._download_article_selenium(article['url'], output_dir)
        
        # Generate CSV if requested
        if makecsv:
            self.download_tools.handle_creation_of_csv_html_xml(
                makecsv, makehtml, makexml, articles, "redalyc_selenium_result"
            )
        
        # Generate XML output for better Unicode handling
        if makexml:
            self._generate_xml_output(articles_dict, "redalyc_selenium_result")
        
        logging.info(f"Redalyc Selenium search completed. Found {len(articles)} articles.")
        return results
    
    def _generate_xml_output(self, articles_dict: Dict[str, Any], base_filename: str) -> None:
        """Generate XML output for better Unicode handling."""
        try:
            # Create combined metadata for XML output
            combined_metadata = {
                "repository": "redalyc_selenium",
                "total_articles": len(articles_dict),
                "articles": articles_dict
            }
            
            # Use FileUtils to write XML
            import os
            output_dir = os.getcwd()
            xml_file = Path(output_dir) / f"{base_filename}s.xml"
            
            if FileUtils.write_xml_data(combined_metadata, xml_file, root_name="redalyc_articles"):
                logging.info(f"Generated XML output: {xml_file}")
            else:
                logging.error("Failed to generate XML output")
            
        except Exception as e:
            logging.error(f"Error generating XML output: {e}")

    def _download_article_selenium(self, article_url: str, output_dir: str) -> bool:
        """
        Download a single article using Selenium.
        
        Args:
            article_url: URL of the article to download
            output_dir: Directory to save the downloaded files
            
        Returns:
            True if download was successful, False otherwise
        """
        try:
            logging.info(f"Downloading article with Selenium: {article_url}")
            
            # Navigate to article page
            self.driver.get(article_url)
            time.sleep(2)
            
            # Get page source
            html_content = self.driver.page_source
            
            # Extract metadata
            metadata = self._extract_article_metadata_from_page(article_url)
            if not metadata:
                return False
            
            # Use FileUtils for file operations
            article_id = FileUtils.generate_article_id(metadata, article_url)
            article_dir = Path(output_dir) / article_id
            FileUtils.create_directory(article_dir)
            
            # Save files using FileUtils
            saved_files = FileUtils.save_article_files(
                metadata=metadata,
                output_dir=article_dir,
                html_content=html_content
            )
            
            # Download PDF if available
            if metadata.get('pdf_url'):
                try:
                    self.driver.get(metadata['pdf_url'])
                    time.sleep(2)
                    pdf_file = article_dir / "fulltext.pdf"
                    with open(pdf_file, 'wb') as f:
                        f.write(self.driver.page_source.encode('utf-8'))
                    logging.info(f"Downloaded PDF: {pdf_file}")
                except Exception as e:
                    logging.warning(f"Failed to download PDF: {e}")
            
            logging.info(f"Successfully downloaded article to: {article_dir}")
            return True
            
        except Exception as e:
            logging.error(f"Error downloading article {article_url}: {e}")
            return False

    def _generate_article_id(self, metadata: Dict[str, Any]) -> str:
        """Generate a unique identifier for an article."""
        import re
        
        # Extract Redalyc article ID from URL
        url = metadata.get('url', '')
        if url and 'redalyc.org/articulo.oa?id=' in url:
            # Extract the ID from URL like https://www.redalyc.org/articulo.oa?id=66914279011
            match = re.search(r'id=(\d+)', url)
            if match:
                article_id = match.group(1)
                return f"REDALYC_{article_id}"
        
        # Try to use DOI as fallback
        if metadata.get('doi'):
            return f"REDALYC_{metadata['doi'].replace('/', '_')}"
        
        # Use title as fallback
        if metadata.get('title'):
            # Clean title for filename
            title = re.sub(r'[^\w\s-]', '', metadata['title'])
            title = re.sub(r'[-\s]+', '-', title)
            return f"REDALYC_{title[:30]}"  # Limit length
        
        # Use URL hash as last resort
        return f"REDALYC_{str(hash(metadata.get('url', '')))}"

    def close(self):
        """Close the WebDriver."""
        if self.driver:
            self.driver.quit()
            logging.info("WebDriver closed")

    def __del__(self):
        """Cleanup when object is destroyed."""
        try:
            self.close()
        except:
            pass  # Ignore errors during cleanup

    # Implement required methods from AbstractRepository
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
            result_dict['new_results'],
            updated_dict=result_dict['updated_dict'],
            paper_key='article_id',
            name_of_file='redalyc_selenium_result',
        )

    def noexecute(self, query_namespace: Dict[str, Any]) -> None:
        """Execute search without downloading files."""
        query = query_namespace["query"]
        logging.info(f"Searching Redalyc with Selenium for: {query}")
        
        try:
            # Navigate to search page
            self.driver.get(self.search_url)
            time.sleep(2)
            
            # Try to find and fill search box using the correct selector
            search_box = self._wait_for_element(By.NAME, "input-articulo", timeout=5)
            if search_box:
                search_box.clear()
                search_box.send_keys(query)
                
                # Find and click the search button
                search_button = self._wait_for_element(By.ID, "boton-buscar-articulo", timeout=5)
                if search_button:
                    search_button.click()
                    time.sleep(3)
                else:
                    # Fallback to pressing Enter
                    search_box.send_keys(Keys.RETURN)
                    time.sleep(3)
                
                # Check if we're on a results page
                current_url = self.driver.current_url
                if "search" in current_url.lower() or "buscar" in current_url.lower():
                    # Count results from search results page
                    article_links = self._extract_article_links_from_page()
                    total_hits = len(article_links)
                    logging.info(f"Search successful, found {total_hits} results")
                else:
                    # Fallback to homepage count
                    logging.warning("Search submission may have failed, falling back to homepage count")
                    self.driver.get(self.base_url)
                    time.sleep(2)
                    article_links = self._extract_article_links_from_page()
                    total_hits = len(article_links)
            else:
                # Fallback to homepage count
                logging.warning("Could not find search box, falling back to homepage count")
                self.driver.get(self.base_url)
                time.sleep(2)
                article_links = self._extract_article_links_from_page()
                total_hits = len(article_links)
                
        except Exception as e:
            logging.error(f"Error during Selenium search: {e}")
            total_hits = 0
        
        logging.info(f"Total number of hits for the query are {total_hits}")

    def apipaperdownload(self, query_namespace: Dict[str, Any]) -> None:
        """Download papers via Selenium."""
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
            result_dict['new_results'],
            updated_dict=result_dict['updated_dict'],
            paper_key='article_id',
            name_of_file='redalyc_selenium_result',
        ) 