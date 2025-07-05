"""
Standalone Corpus Module

This module provides functionality for managing and analyzing document corpora.
Extracted from amilib for use in pygetpapers Streamlit UI and other projects.

Features:
- Hierarchical corpus management (directories and files)
- Search functionality across corpus files
- Query management and execution
- Results visualization and HTML generation
- Integration with pygetpapers output
- Datatables generation from corpus data
"""

from .corpus import AmiCorpus, AmiCorpusContainer
from .query import CorpusQuery
from .search import CorpusSearch

__version__ = "0.1.0"
__all__ = ["AmiCorpus", "AmiCorpusContainer", "CorpusQuery", "CorpusSearch"] 