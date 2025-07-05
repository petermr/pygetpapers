"""
Standalone Datatables Module

This module provides functionality for creating interactive HTML tables using jQuery DataTables.
Extracted from amilib for use in pygetpapers Streamlit UI and other projects.

Features:
- Create interactive HTML tables with sorting, searching, and pagination
- Support for multiple DataTable versions
- Column manipulation (extract, insert, modify)
- Modal popups for cell content display
- Scrollable content support
- JSON to HTML table conversion
"""

from .datatables import Datatables, DataTable
from .html_table import HtmlTable

__version__ = "0.1.0"
__all__ = ["Datatables", "DataTable", "HtmlTable"] 