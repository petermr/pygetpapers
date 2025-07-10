"""
OpenAlex repository module for pygetpapers.
"""

from pygetpapers.config_loader import get_repository_config

from .openalex import OpenAlex

__all__ = ["OpenAlex"]
