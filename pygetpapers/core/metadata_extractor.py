"""
Metadata Extraction Utilities

This module provides common metadata extraction patterns that can be used
across different repository implementations to reduce code duplication.
"""

import logging
import re
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

try:
    from bs4 import BeautifulSoup, Tag

    BEAUTIFULSOUP_AVAILABLE = True
except ImportError:
    BEAUTIFULSOUP_AVAILABLE = False

logger = logging.getLogger(__name__)


class MetadataExtractor:
    """
    Static utility class for extracting metadata from HTML content.

    This class provides common patterns for extracting metadata fields
    that are used across multiple repository implementations.
    """

    # Common CSS selectors for different metadata fields
    TITLE_SELECTORS = [
        "h1",
        ".title",
        ".article-title",
        "title",
        ".titulo",
        ".titulo-articulo",
        ".paper-title",
        '[ng-bind*="title"]',
        '[ng-bind*="titulo"]',
        ".ng-binding",
    ]

    AUTHOR_SELECTORS = [
        ".authors",
        ".author",
        ".author-list",
        'span[class*="author"]',
        ".autores",
        ".autor",
        ".author-name",
        ".contrib-author",
    ]

    ABSTRACT_SELECTORS = [
        ".abstract",
        ".resumen",
        ".summary",
        'div[class*="abstract"]',
        ".abstract-text",
        ".resumen-texto",
        ".paper-abstract",
        ".summary",
        "span.summary",
        'div[class*="resumen"]',
        '[ng-bind*="resumen"]',
        '[ng-bind*="abstract"]',
    ]

    JOURNAL_SELECTORS = [
        ".journal",
        ".revista",
        ".publication",
        'span[class*="journal"]',
        ".journal-title",
        ".revista-titulo",
        ".publication-title",
    ]

    KEYWORD_SELECTORS = [
        ".keywords",
        ".palabras-clave",
        ".tags",
        'span[class*="keyword"]',
        ".subject-areas",
        ".categories",
    ]

    @staticmethod
    def extract_title(html_content: str, soup: Optional[BeautifulSoup] = None) -> str:
        """
        Extract title from HTML content using multiple strategies.

        Args:
            html_content: Raw HTML content
            soup: Optional BeautifulSoup object (will be created if not provided)

        Returns:
            Extracted title or empty string
        """
        if not BEAUTIFULSOUP_AVAILABLE:
            return MetadataExtractor._extract_title_from_text(html_content)

        if soup is None:
            soup = BeautifulSoup(html_content, "html.parser")

        # Try CSS selectors first
        for selector in MetadataExtractor.TITLE_SELECTORS:
            try:
                element = soup.select_one(selector)
                if element:
                    title = element.get_text(strip=True)
                    if title and len(title) > 5:
                        return title
            except Exception:
                continue

        # Fallback to text-based extraction
        return MetadataExtractor._extract_title_from_text(html_content)

    @staticmethod
    def _extract_title_from_text(text_content: str) -> str:
        """Extract title using regex patterns from text content."""
        # Remove HTML tags
        text_content = re.sub(r"<[^>]+>", "", text_content)
        text_content = re.sub(r"\s+", " ", text_content).strip()

        # Look for title patterns
        title_patterns = [
            r"([A-Z][A-Z\s\-\.,]{20,})",  # Long uppercase strings
            r"([A-Z][a-z\s\-\.,]{10,}(?:LIPPIA|LANTANA|VERBENACEAE)[a-z\s\-\.,]*)",  # Scientific titles
            r"([A-Z][a-z\s\-\.,]{15,})",  # Mixed case titles
        ]

        for pattern in title_patterns:
            matches = re.findall(pattern, text_content)
            for match in matches:
                title = match.strip()
                # Filter out common non-title text
                if (
                    len(title) > 10
                    and "redalyc" not in title.lower()
                    and "sistema" not in title.lower()
                    and "información" not in title.lower()
                    and "científica" not in title.lower()
                ):
                    return title

        return ""

    @staticmethod
    def extract_authors(
        html_content: str, soup: Optional[BeautifulSoup] = None
    ) -> List[str]:
        """
        Extract authors from HTML content.

        Args:
            html_content: Raw HTML content
            soup: Optional BeautifulSoup object

        Returns:
            List of author names
        """
        if not BEAUTIFULSOUP_AVAILABLE:
            return MetadataExtractor._extract_authors_from_text(html_content)

        if soup is None:
            soup = BeautifulSoup(html_content, "html.parser")

        # Try CSS selectors first
        for selector in MetadataExtractor.AUTHOR_SELECTORS:
            try:
                elements = soup.select(selector)
                if elements:
                    authors = []
                    for elem in elements:
                        author_text = elem.get_text(strip=True)
                        if author_text and len(author_text) > 2:
                            authors.append(author_text)
                    if authors:
                        return authors
            except Exception:
                continue

        # Fallback to text-based extraction
        return MetadataExtractor._extract_authors_from_text(html_content)

    @staticmethod
    def _extract_authors_from_text(text_content: str) -> List[str]:
        """Extract authors using regex patterns from text content."""
        author_patterns = [
            r"([A-Z][a-z]+ [A-Z]\. [A-Z][a-z]+)",  # First Last M. Last
            r"([A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+)",  # First Middle Last
            r"([A-Z][a-z]+ [A-Z]\. [A-Z]\. [A-Z][a-z]+)",  # First M. M. Last
            r"([A-Z][a-z]+ [A-Z][a-z]+)",  # First Last
        ]

        authors = []
        for pattern in author_patterns:
            matches = re.findall(pattern, text_content)
            for match in matches:
                author_text = match.strip()
                # Filter out common non-author text
                if (
                    len(author_text) > 5
                    and "redalyc" not in author_text.lower()
                    and "sistema" not in author_text.lower()
                    and "información" not in author_text.lower()
                    and "científica" not in author_text.lower()
                    and "darwiniana" not in author_text.lower()
                ):
                    authors.append(author_text)

        return list(set(authors))  # Remove duplicates

    @staticmethod
    def extract_abstract(
        html_content: str, soup: Optional[BeautifulSoup] = None
    ) -> str:
        """
        Extract abstract from HTML content.

        Args:
            html_content: Raw HTML content
            soup: Optional BeautifulSoup object

        Returns:
            Extracted abstract or empty string
        """
        if not BEAUTIFULSOUP_AVAILABLE:
            return MetadataExtractor._extract_abstract_from_text(html_content)

        if soup is None:
            soup = BeautifulSoup(html_content, "html.parser")

        # Try CSS selectors first
        for selector in MetadataExtractor.ABSTRACT_SELECTORS:
            try:
                element = soup.select_one(selector)
                if element:
                    abstract = element.get_text(strip=True)
                    if abstract and len(abstract) > 20:
                        return abstract
            except Exception:
                continue

        # Fallback to text-based extraction
        return MetadataExtractor._extract_abstract_from_text(html_content)

    @staticmethod
    def extract_redalyc_abstract_from_search_results(
        html_content: str, soup: Optional[BeautifulSoup] = None
    ) -> str:
        """
        Extract abstract from Redalyc search results page.

        This method specifically handles Redalyc's abstract toggle functionality
        where abstracts are stored in article.resumen and displayed via checkbox.

        Args:
            html_content: Raw HTML content from Redalyc search results
            soup: Optional BeautifulSoup object

        Returns:
            Extracted abstract or empty string
        """
        if not BEAUTIFULSOUP_AVAILABLE:
            return MetadataExtractor._extract_abstract_from_text(html_content)

        if soup is None:
            soup = BeautifulSoup(html_content, "html.parser")

        # Look for Redalyc-specific abstract patterns
        # 1. Check for summary spans that contain abstract text
        summary_spans = soup.find_all("span", class_="summary")
        for span in summary_spans:
            text = span.get_text(strip=True)
            if text and len(text) > 20:
                return text

        # 2. Look for article content that might contain abstract
        content_spans = soup.find_all("span", class_="article-contenido")
        for span in content_spans:
            text = span.get_text(strip=True)
            # Look for abstract indicators in the content
            if any(
                indicator in text.lower()
                for indicator in ["resumen:", "abstract:", "summary:"]
            ):
                # Extract text after the indicator
                for indicator in ["resumen:", "abstract:", "summary:"]:
                    if indicator in text.lower():
                        parts = text.split(indicator, 1)
                        if len(parts) > 1:
                            abstract = parts[1].strip()
                            if len(abstract) > 20:
                                return abstract

        # 3. Look for ng-bind attributes that might contain abstract data
        ng_bind_elements = soup.find_all(attrs={"ng-bind": True})
        for elem in ng_bind_elements:
            ng_bind = elem.get("ng-bind", "")
            if "resumen" in ng_bind or "abstract" in ng_bind:
                text = elem.get_text(strip=True)
                if text and len(text) > 20:
                    return text

        # 4. Look for abstract checkbox and try to extract from ng-click data
        resumen_checkboxes = soup.find_all("input", class_="check-resumen")
        for checkbox in resumen_checkboxes:
            ng_click = checkbox.get("ng-click", "")
            if "muestraResumen" in ng_click and "article.resumen" in ng_click:
                # The abstract data is in the AngularJS model, not directly in HTML
                # We need to look for any text that might be the abstract
                parent = checkbox.parent
                if parent:
                    # Look for any text that looks like an abstract
                    for text_elem in parent.find_all(text=True):
                        text = text_elem.strip()
                        if text and len(text) > 50 and not text.startswith("Resumen:"):
                            # This might be the abstract
                            return text

        # 5. Look for any text that looks like an abstract in the article content
        content_elem = soup.find("span", class_="article-contenido")
        if content_elem:
            text = content_elem.get_text(strip=True)
            # Look for patterns that indicate abstract content
            if len(text) > 100:
                # Split by common separators and look for abstract-like content
                parts = text.split(".")
                for part in parts:
                    part = part.strip()
                    if len(part) > 50 and any(
                        word in part.lower()
                        for word in [
                            "resumen",
                            "abstract",
                            "summary",
                            "como",
                            "se",
                            "los",
                            "las",
                        ]
                    ):
                        return part

        # Fallback to general abstract extraction
        return MetadataExtractor.extract_abstract(html_content, soup)

    @staticmethod
    def _extract_abstract_from_text(text_content: str) -> str:
        """Extract abstract using regex patterns from text content."""
        abstract_patterns = [
            r"Resumen[:\s]+([^.]{50,})",
            r"Abstract[:\s]+([^.]{50,})",
            r"Resumen[:\s]+([^<]{50,})",
            r"Abstract[:\s]+([^<]{50,})",
        ]

        for pattern in abstract_patterns:
            match = re.search(pattern, text_content, re.IGNORECASE | re.DOTALL)
            if match:
                abstract = match.group(1).strip()
                # Clean up HTML entities and tags
                abstract = re.sub(r"<[^>]+>", "", abstract)
                abstract = re.sub(r"&nbsp;", " ", abstract)
                abstract = re.sub(r"\s+", " ", abstract).strip()
                if len(abstract) > 20:
                    return abstract

        return ""

    @staticmethod
    def extract_journal(html_content: str, soup: Optional[BeautifulSoup] = None) -> str:
        """
        Extract journal name from HTML content.

        Args:
            html_content: Raw HTML content
            soup: Optional BeautifulSoup object

        Returns:
            Extracted journal name or empty string
        """
        if not BEAUTIFULSOUP_AVAILABLE:
            return MetadataExtractor._extract_journal_from_text(html_content)

        if soup is None:
            soup = BeautifulSoup(html_content, "html.parser")

        # Try CSS selectors first
        for selector in MetadataExtractor.JOURNAL_SELECTORS:
            try:
                element = soup.select_one(selector)
                if element:
                    journal = element.get_text(strip=True)
                    if journal and len(journal) > 2:
                        return journal
            except Exception:
                continue

        # Fallback to text-based extraction
        return MetadataExtractor._extract_journal_from_text(html_content)

    @staticmethod
    def _extract_journal_from_text(text_content: str) -> str:
        """Extract journal using regex patterns from text content."""
        journal_patterns = [
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+\d{4}",
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+\d{2,4}",
            r"(Darwiniana)\s+\d{4}",  # Specific journal name
            r"(Revista\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+&\nbsp;\d{4}",  # Handle HTML entities
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+\d{4},\s+\d+",  # Journal year, volume
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+\d{4}\s+\(\d+\)",  # Journal year (volume)
        ]

        for pattern in journal_patterns:
            match = re.search(pattern, text_content)
            if match:
                journal = match.group(1).strip()
                # Clean up HTML entities
                journal = re.sub(r"&nbsp;", " ", journal)
                journal = re.sub(r"\s+", " ", journal).strip()
                if journal and len(journal) > 2:
                    return journal

        return ""

    @staticmethod
    def extract_year(html_content: str) -> str:
        """
        Extract publication year from HTML content.

        Args:
            html_content: Raw HTML content

        Returns:
            Extracted year or empty string
        """
        year_pattern = r"\b(19|20)\d{2}\b"
        year_match = re.search(year_pattern, html_content)
        if year_match:
            return year_match.group()
        return ""

    @staticmethod
    def extract_doi(html_content: str) -> str:
        """
        Extract DOI from HTML content.

        Args:
            html_content: Raw HTML content

        Returns:
            Extracted DOI or empty string
        """
        doi_patterns = [
            r"10\.\d{4,}/[-._;()/:\w]+",
            r"DOI[:\s]+(10\.\d{4,}/[-._;()/:\w]+)",
            r"doi[:\s]+(10\.\d{4,}/[-._;()/:\w]+)",
        ]

        for pattern in doi_patterns:
            doi_match = re.search(pattern, html_content, re.IGNORECASE)
            if doi_match:
                doi = (
                    doi_match.group(1)
                    if len(doi_match.groups()) > 0
                    else doi_match.group(0)
                )
                return doi.strip()

        return ""

    @staticmethod
    def extract_language(
        html_content: str, soup: Optional[BeautifulSoup] = None
    ) -> str:
        """
        Extract language from HTML content.

        Args:
            html_content: Raw HTML content
            soup: Optional BeautifulSoup object

        Returns:
            Extracted language or empty string
        """
        if not BEAUTIFULSOUP_AVAILABLE:
            return MetadataExtractor._extract_language_from_text(html_content)

        if soup is None:
            soup = BeautifulSoup(html_content, "html.parser")

        # Try HTML lang attribute
        lang_elem = soup.find("html")
        if lang_elem and lang_elem.get("lang"):
            lang = lang_elem.get("lang")
            return MetadataExtractor._normalize_language(lang)

        # Fallback to text-based extraction
        return MetadataExtractor._extract_language_from_text(html_content)

    @staticmethod
    def _extract_language_from_text(text_content: str) -> str:
        """Extract language using regex patterns from text content."""
        language_patterns = [
            r"Idioma[:\s]+([A-Za-z]+)",
            r"Language[:\s]+([A-Za-z]+)",
            r'<html[^>]*lang="([^"]+)"',
            r'lang="([^"]+)"',
        ]

        for pattern in language_patterns:
            lang_match = re.search(pattern, text_content, re.IGNORECASE)
            if lang_match:
                lang = lang_match.group(1).strip()
                return MetadataExtractor._normalize_language(lang)

        return ""

    @staticmethod
    def _normalize_language(lang: str) -> str:
        """Normalize language codes to readable names."""
        lang = lang.lower()
        if lang in ["es", "spanish", "español"]:
            return "Spanish"
        elif lang in ["pt", "portuguese", "português"]:
            return "Portuguese"
        elif lang in ["en", "english"]:
            return "English"
        else:
            return lang

    @staticmethod
    def extract_keywords(
        html_content: str, soup: Optional[BeautifulSoup] = None
    ) -> List[str]:
        """
        Extract keywords from HTML content.

        Args:
            html_content: Raw HTML content
            soup: Optional BeautifulSoup object

        Returns:
            List of keywords
        """
        if not BEAUTIFULSOUP_AVAILABLE:
            return MetadataExtractor._extract_keywords_from_text(html_content)

        if soup is None:
            soup = BeautifulSoup(html_content, "html.parser")

        # Try CSS selectors first
        for selector in MetadataExtractor.KEYWORD_SELECTORS:
            try:
                elements = soup.select(selector)
                if elements:
                    keywords = []
                    for elem in elements:
                        keyword_text = elem.get_text(strip=True)
                        if keyword_text:
                            keywords.extend(
                                [
                                    kw.strip()
                                    for kw in keyword_text.split(",")
                                    if kw.strip()
                                ]
                            )
                    if keywords:
                        return keywords
            except Exception:
                continue

        # Fallback to text-based extraction
        return MetadataExtractor._extract_keywords_from_text(html_content)

    @staticmethod
    def _extract_keywords_from_text(text_content: str) -> List[str]:
        """Extract keywords using regex patterns from text content."""
        keyword_patterns = [
            r"Palabras\s+clave[:\s]+([^.]{10,})",
            r"Keywords[:\s]+([^.]{10,})",
            r"Palavras-chave[:\s]+([^.]{10,})",
        ]

        for pattern in keyword_patterns:
            keyword_match = re.search(pattern, text_content, re.IGNORECASE)
            if keyword_match:
                keywords_text = keyword_match.group(1).strip()
                # Clean up and split keywords
                keywords_text = re.sub(r"<[^>]+>", "", keywords_text)
                keywords_text = re.sub(r"&nbsp;", " ", keywords_text)
                keywords = [
                    kw.strip() for kw in re.split(r"[,;]", keywords_text) if kw.strip()
                ]
                if keywords:
                    return keywords

        return []

    @staticmethod
    def extract_links(
        html_content: str, soup: Optional[BeautifulSoup] = None, base_url: str = ""
    ) -> Dict[str, str]:
        """
        Extract download links from HTML content.

        Args:
            html_content: Raw HTML content
            soup: Optional BeautifulSoup object
            base_url: Base URL for resolving relative links

        Returns:
            Dictionary with 'pdf_url', 'xml_url', 'html_url', 'epub_url', and 'mobile_url' keys
        """
        links = {
            "pdf_url": "",
            "xml_url": "",
            "html_url": "",
            "epub_url": "",
            "mobile_url": "",
        }

        if not BEAUTIFULSOUP_AVAILABLE:
            return links

        if soup is None:
            soup = BeautifulSoup(html_content, "html.parser")

        try:
            for link in soup.find_all("a", href=True):
                href = link.get("href", "").lower()
                link_text = link.get_text(strip=True).lower()
                full_href = link.get("href", "")

                # Look for PDF links
                if ("pdf" in href or "pdf" in link_text) and not links["pdf_url"]:
                    if full_href and full_href.startswith("http"):
                        links["pdf_url"] = full_href
                    elif base_url and full_href:
                        links["pdf_url"] = urljoin(base_url, full_href)

                # Look for XML links
                elif (
                    "xml" in href
                    or "xml" in link_text
                    or "jats" in href
                    or "jats" in link_text
                ) and not links["xml_url"]:
                    # Include XML links when found (different repositories may have them)
                    if full_href and full_href.startswith("http"):
                        links["xml_url"] = full_href
                    elif base_url and full_href:
                        links["xml_url"] = urljoin(base_url, full_href)

                # Look for HTML links
                elif ("html" in href or "html" in link_text) and not links["html_url"]:
                    if full_href and full_href.startswith("http"):
                        links["html_url"] = full_href
                    elif base_url and full_href:
                        links["html_url"] = urljoin(base_url, full_href)

                # Look for ePUB links
                elif ("epub" in href or "epub" in link_text) and not links["epub_url"]:
                    if full_href and full_href.startswith("http"):
                        links["epub_url"] = full_href
                    elif base_url and full_href:
                        links["epub_url"] = urljoin(base_url, full_href)

                # Look for mobile links
                elif ("mobile" in href or "mobile" in link_text) and not links[
                    "mobile_url"
                ]:
                    if full_href and full_href.startswith("http"):
                        links["mobile_url"] = full_href
                    elif base_url and full_href:
                        links["mobile_url"] = urljoin(base_url, full_href)

                # Look for repository-specific download links
                elif "articulo.oa" in href and not links["pdf_url"]:
                    # For Redalyc, this is typically a PDF link
                    if base_url and full_href:
                        links["pdf_url"] = urljoin(base_url, full_href)
                    elif full_href.startswith("http"):
                        links["pdf_url"] = full_href

        except Exception as e:
            logger.debug(f"Error extracting links: {e}")

        return links

    @staticmethod
    def extract_all_metadata(html_content: str, url: str = "") -> Dict[str, Any]:
        """
        Extract all metadata fields from HTML content.

        Args:
            html_content: Raw HTML content
            url: Article URL for link extraction

        Returns:
            Dictionary with all extracted metadata
        """
        soup = (
            BeautifulSoup(html_content, "html.parser")
            if BEAUTIFULSOUP_AVAILABLE
            else None
        )

        metadata = {
            "url": url,
            "title": MetadataExtractor.extract_title(html_content, soup),
            "authors": MetadataExtractor.extract_authors(html_content, soup),
            "abstract": MetadataExtractor.extract_abstract(html_content, soup),
            "journal": MetadataExtractor.extract_journal(html_content, soup),
            "year": MetadataExtractor.extract_year(html_content),
            "doi": MetadataExtractor.extract_doi(html_content),
            "keywords": MetadataExtractor.extract_keywords(html_content, soup),
            "language": MetadataExtractor.extract_language(html_content, soup),
            "pdf_url": "",
            "xml_url": "",
            "html_url": "",
            "epub_url": "",
            "mobile_url": "",
        }

        # Extract links
        links = MetadataExtractor.extract_links(html_content, soup, url)
        metadata.update(links)

        return metadata
