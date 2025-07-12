"""
Redalyc repository module for pygetpapers.

This module provides web scraping functionality for Redalyc,
a multilingual scientific repository focused on Latin America,
Spain, and Portugal.
"""

from .redalyc import Redalyc
from .redalyc_selenium import RedalycSelenium

__all__ = ['Redalyc', 'RedalycSelenium'] 