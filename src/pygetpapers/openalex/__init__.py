"""
OpenAlex repository module for pygetpapers.
"""

from .openalex import OpenAlex
from pygetpapers.config_loader import get_repository_config

__all__ = ["OpenAlex"]
