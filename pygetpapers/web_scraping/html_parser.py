"""
Configurable HTML Parser for Web Scraping Framework

This module provides a flexible HTML parser that uses configuration-based
selectors to extract structured data from HTML content. It supports multiple
selector strategies and fallback mechanisms for robust data extraction.
"""

import logging
import re
from typing import Any, Dict, List, Optional, Union

try:
    from bs4 import BeautifulSoup, Tag

    BEAUTIFULSOUP_AVAILABLE = True
except ImportError:
    BEAUTIFULSOUP_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("BeautifulSoup not available. HTML parsing will be limited.")

logger = logging.getLogger(__name__)


class ConfigurableHTMLParser:
    """
    HTML parser that uses configuration-based selectors.

    Supports multiple selector strategies:
    - CSS selectors
    - XPath expressions
    - Text-based matching
    - Attribute-based selection
    """

    def __init__(self):
        """Initialize the HTML parser."""
        if not BEAUTIFULSOUP_AVAILABLE:
            raise ImportError(
                "BeautifulSoup is required for HTML parsing. Install with: pip install beautifulsoup4"
            )

    def parse_html(self, html_content: str) -> BeautifulSoup:
        """
        Parse HTML content into a BeautifulSoup object.

        Args:
            html_content: HTML content string

        Returns:
            BeautifulSoup object
        """
        try:
            return BeautifulSoup(html_content, "html.parser")
        except Exception as e:
            logger.error(f"Error parsing HTML: {e}")
            raise

    def extract_field(
        self, element: Union[BeautifulSoup, Tag], selector_config: str
    ) -> Optional[str]:
        """
        Extract field using configured selector with fallbacks.

        Args:
            element: BeautifulSoup element to search within
            selector_config: Comma-separated list of selectors to try

        Returns:
            Extracted text or None if not found
        """
        if not selector_config:
            return None

        # Split selectors by comma and try each one
        selectors = [s.strip() for s in selector_config.split(",") if s.strip()]

        for selector in selectors:
            try:
                result = self._extract_with_selector(element, selector)
                if result:
                    return result
            except Exception as e:
                logger.debug(f"Selector '{selector}' failed: {e}")
                continue

        return None

    def _extract_with_selector(
        self, element: Union[BeautifulSoup, Tag], selector: str
    ) -> Optional[str]:
        """
        Extract text using a single selector.

        Args:
            element: BeautifulSoup element to search within
            selector: CSS selector or special selector

        Returns:
            Extracted text or None if not found
        """
        # Handle special selectors
        if selector.startswith("text:"):
            # Text-based matching
            return self._extract_text_match(element, selector[5:])
        elif selector.startswith("attr:"):
            # Attribute-based selection
            return self._extract_attribute(element, selector[5:])
        elif selector.startswith("contains:"):
            # Contains text matching
            return self._extract_contains(element, selector[9:])
        else:
            # CSS selector
            return self._extract_css_selector(element, selector)

    def _extract_css_selector(
        self, element: Union[BeautifulSoup, Tag], selector: str
    ) -> Optional[str]:
        """
        Extract text using CSS selector.

        Args:
            element: BeautifulSoup element to search within
            selector: CSS selector

        Returns:
            Extracted text or None if not found
        """
        try:
            found_elements = element.select(selector)
            if found_elements:
                # Get text from the first matching element
                text = found_elements[0].get_text(strip=True)
                return text if text else None
        except Exception as e:
            logger.debug(f"CSS selector '{selector}' failed: {e}")

        return None

    def _extract_text_match(
        self, element: Union[BeautifulSoup, Tag], pattern: str
    ) -> Optional[str]:
        """
        Extract text using pattern matching.

        Args:
            element: BeautifulSoup element to search within
            pattern: Text pattern to match

        Returns:
            Matched text or None if not found
        """
        try:
            # Find elements containing the pattern
            elements = element.find_all(text=re.compile(pattern, re.IGNORECASE))
            if elements:
                return elements[0].strip()
        except Exception as e:
            logger.debug(f"Text pattern '{pattern}' failed: {e}")

        return None

    def _extract_attribute(
        self, element: Union[BeautifulSoup, Tag], attr_selector: str
    ) -> Optional[str]:
        """
        Extract attribute value.

        Args:
            element: BeautifulSoup element to search within
            attr_selector: Attribute selector (e.g., "a[href]")

        Returns:
            Attribute value or None if not found
        """
        try:
            # Parse attribute selector (e.g., "a[href]")
            match = re.match(r"(\w+)\[(\w+)\]", attr_selector)
            if match:
                tag_name, attr_name = match.groups()
                elements = element.find_all(tag_name)
                for elem in elements:
                    if elem.has_attr(attr_name):
                        return elem[attr_name]
        except Exception as e:
            logger.debug(f"Attribute selector '{attr_selector}' failed: {e}")

        return None

    def _extract_contains(
        self, element: Union[BeautifulSoup, Tag], text: str
    ) -> Optional[str]:
        """
        Extract text from elements containing specific text.

        Args:
            element: BeautifulSoup element to search within
            text: Text to search for

        Returns:
            Extracted text or None if not found
        """
        try:
            # Find elements containing the text
            elements = element.find_all(text=re.compile(re.escape(text), re.IGNORECASE))
            if elements:
                # Get the parent element's text
                parent = elements[0].parent
                if parent:
                    return parent.get_text(strip=True)
        except Exception as e:
            logger.debug(f"Contains selector '{text}' failed: {e}")

        return None

    def extract_multiple_fields(
        self, element: Union[BeautifulSoup, Tag], selectors: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Extract multiple fields using configured selectors.

        Args:
            element: BeautifulSoup element to search within
            selectors: Dictionary mapping field names to selector configurations

        Returns:
            Dictionary with extracted field values
        """
        results = {}

        for field_name, selector_config in selectors.items():
            try:
                value = self.extract_field(element, selector_config)
                if value:
                    results[field_name] = value
            except Exception as e:
                logger.debug(f"Error extracting field '{field_name}': {e}")
                continue

        return results

    def find_results_container(
        self, soup: BeautifulSoup, selector_config: str
    ) -> Optional[Tag]:
        """
        Find the container element that holds search results.

        Args:
            soup: BeautifulSoup object of the page
            selector_config: Selector configuration for results container

        Returns:
            Results container element or None if not found
        """
        return self._find_element(soup, selector_config)

    def find_paper_elements(self, container: Tag, selector_config: str) -> List[Tag]:
        """
        Find individual paper elements within the results container.

        Args:
            container: Results container element
            selector_config: Selector configuration for paper elements

        Returns:
            List of paper elements
        """
        return self._find_elements(container, selector_config)

    def _find_element(
        self, element: Union[BeautifulSoup, Tag], selector_config: str
    ) -> Optional[Tag]:
        """
        Find a single element using selector configuration.

        Args:
            element: Element to search within
            selector_config: Comma-separated list of selectors

        Returns:
            Found element or None
        """
        selectors = [s.strip() for s in selector_config.split(",") if s.strip()]

        for selector in selectors:
            try:
                found = element.select_one(selector)
                if found:
                    return found
            except Exception as e:
                logger.debug(f"Selector '{selector}' failed: {e}")
                continue

        return None

    def _find_elements(
        self, element: Union[BeautifulSoup, Tag], selector_config: str
    ) -> List[Tag]:
        """
        Find multiple elements using selector configuration.

        Args:
            element: Element to search within
            selector_config: Comma-separated list of selectors

        Returns:
            List of found elements
        """
        selectors = [s.strip() for s in selector_config.split(",") if s.strip()]

        for selector in selectors:
            try:
                found = element.select(selector)
                if found:
                    return found
            except Exception as e:
                logger.debug(f"Selector '{selector}' failed: {e}")
                continue

        return []

    def extract_pagination_info(
        self, soup: BeautifulSoup, pagination_config: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Extract pagination information from the page.

        Args:
            soup: BeautifulSoup object of the page
            pagination_config: Pagination configuration dictionary

        Returns:
            Dictionary with pagination information
        """
        pagination_info = {
            "current_page": 1,
            "total_pages": 1,
            "has_next": False,
            "has_previous": False,
            "results_per_page": 20,
        }

        # Extract current page
        if "current_page" in pagination_config:
            current_selector = pagination_config["current_page"]
            current_text = self.extract_field(soup, current_selector)
            if current_text:
                try:
                    pagination_info["current_page"] = int(current_text)
                except ValueError:
                    pass

        # Check for next button
        if "next_button" in pagination_config:
            next_selector = pagination_config["next_button"]
            next_element = self._find_element(soup, next_selector)
            pagination_info["has_next"] = next_element is not None

        # Check for previous button
        if "previous_button" in pagination_config:
            prev_selector = pagination_config["previous_button"]
            prev_element = self._find_element(soup, prev_selector)
            pagination_info["has_previous"] = prev_element is not None

        # Extract results per page
        if "results_per_page" in pagination_config:
            try:
                pagination_info["results_per_page"] = int(
                    pagination_config["results_per_page"]
                )
            except ValueError:
                pass

        return pagination_info

    def extract_filters(
        self, soup: BeautifulSoup, filters_config: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Extract available filters from the page.

        Args:
            soup: BeautifulSoup object of the page
            filters_config: Filters configuration dictionary

        Returns:
            Dictionary with available filters
        """
        filters = {}

        for filter_name, selector_config in filters_config.items():
            try:
                # Try to find filter elements
                filter_elements = self._find_elements(soup, selector_config)
                if filter_elements:
                    filters[filter_name] = [
                        elem.get_text(strip=True) for elem in filter_elements
                    ]
            except Exception as e:
                logger.debug(f"Error extracting filter '{filter_name}': {e}")
                continue

        return filters

    def clean_text(self, text: str) -> str:
        """
        Clean extracted text by removing extra whitespace and normalizing.

        Args:
            text: Raw text to clean

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text.strip())

        # Remove common HTML entities
        text = text.replace("&nbsp;", " ")
        text = text.replace("&amp;", "&")
        text = text.replace("&lt;", "<")
        text = text.replace("&gt;", ">")
        text = text.replace("&quot;", '"')
        text = text.replace("&#39;", "'")

        return text

    def extract_links(
        self, element: Union[BeautifulSoup, Tag], selector: str
    ) -> List[Dict[str, str]]:
        """
        Extract links from elements.

        Args:
            element: Element to search within
            selector: CSS selector for link elements

        Returns:
            List of dictionaries with link text and URL
        """
        links = []

        try:
            link_elements = element.select(selector)
            for link_elem in link_elements:
                href = link_elem.get("href", "")
                text = link_elem.get_text(strip=True)
                if href and text:
                    links.append({"text": text, "url": href})
        except Exception as e:
            logger.debug(f"Error extracting links: {e}")

        return links

    def extract_table_data(
        self, element: Union[BeautifulSoup, Tag], table_selector: str
    ) -> List[Dict[str, str]]:
        """
        Extract data from HTML tables.

        Args:
            element: Element to search within
            table_selector: CSS selector for table elements

        Returns:
            List of dictionaries with table row data
        """
        table_data = []

        try:
            tables = element.select(table_selector)
            for table in tables:
                # Extract headers
                headers = []
                header_row = table.find("thead")
                if header_row:
                    header_cells = header_row.find_all(["th", "td"])
                    headers = [cell.get_text(strip=True) for cell in header_cells]

                # Extract rows
                rows = table.find_all("tr")
                for row in rows:
                    # Skip header row
                    if row.find("th"):
                        continue

                    cells = row.find_all("td")
                    if cells:
                        row_data = {}
                        for i, cell in enumerate(cells):
                            if i < len(headers):
                                row_data[headers[i]] = cell.get_text(strip=True)
                            else:
                                row_data[f"column_{i}"] = cell.get_text(strip=True)
                        table_data.append(row_data)
        except Exception as e:
            logger.debug(f"Error extracting table data: {e}")

        return table_data

    def validate_selector(self, selector: str) -> bool:
        """
        Validate if a selector is syntactically correct.

        Args:
            selector: CSS selector to validate

        Returns:
            True if selector is valid, False otherwise
        """
        try:
            # Basic CSS selector validation
            if selector.startswith(("text:", "attr:", "contains:")):
                return True

            # Test with a minimal HTML document
            test_html = "<html><body><div></div></body></html>"
            soup = BeautifulSoup(test_html, "html.parser")
            soup.select(selector)
            return True
        except Exception:
            return False
