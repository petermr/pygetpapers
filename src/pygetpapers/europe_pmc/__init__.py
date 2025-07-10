"""
Europe PMC repository module for pygetpapers.
"""

from pygetpapers.config_loader import get_repository_config

from .europe_pmc import EuropePmc

__all__ = ["EuropePmc"]


class EuropePMC:
    def __init__(self):
        self.config = get_repository_config("europe_pmc")

    def has_capability(self, capability: str) -> bool:
        return self.config.get_capability(capability)
