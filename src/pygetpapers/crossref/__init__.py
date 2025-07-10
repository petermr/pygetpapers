"""
Crossref repository module for pygetpapers.
"""

from pygetpapers.config_loader import get_repository_config

from .crossref import CrossRef

__all__ = ["CrossRef"]
