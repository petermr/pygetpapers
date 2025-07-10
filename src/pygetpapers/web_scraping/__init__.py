"""
Pygetpapers Web Scraping Module

A configurable web scraping framework that allows pygetpapers to support multiple
repositories through web scraping without hardcoding specific implementations.

This module provides:
- GenericWebScraper: Base scraper class with common functionality
- Configuration Parser: Loads and validates scraping configurations
- HTML Parser Engine: Configurable HTML parsing based on selectors
- Data Extractor: Extracts structured data using configuration rules
- Repository Interface: Integrates with existing pygetpapers architecture
"""

from .config_parser import ScrapingConfigParser
from .data_transformer import DataTransformer
from .generic_scraper import GenericWebScraper
from .html_parser import ConfigurableHTMLParser
from .repository import WebScrapingRepository

__all__ = [
    "GenericWebScraper",
    "ScrapingConfigParser",
    "ConfigurableHTMLParser",
    "DataTransformer",
    "WebScrapingRepository",
]

__version__ = "1.0.0"
