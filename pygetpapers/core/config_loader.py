"""
Configuration loader for pygetpapers repositories.

This module provides utilities to load and manage configuration files
for different repository subpackages.
"""

import configparser
from pathlib import Path
from typing import Any, Dict


class RepositoryConfig:
    """Configuration class for repository settings."""

    def __init__(self, repository_name: str):
        """Initialize configuration for a repository.

        Args:
            repository_name: Name of the repository (e.g., 'biorxiv', 'europe_pmc')
        """
        self.repository_name = repository_name
        self.config = configparser.ConfigParser()
        self._load_config()

    def _load_config(self):
        """Load configuration from the repository's config.ini file."""
        config_path = Path(Path(__file__).parent, self.repository_name, "config.ini")

        if config_path.exists():
            self.config.read(config_path)
        else:
            # Create default configuration if file doesn't exist
            self._create_default_config()

    def _create_default_config(self):
        """Create a default configuration for repositories without config files."""
        self.config.add_section("repository")
        self.config.set("repository", "name", self.repository_name.title())
        self.config.set(
            "repository", "description", f"{self.repository_name.title()} repository"
        )

        self.config.add_section("capabilities")
        self.config.set("capabilities", "api", "true")
        self.config.set("capabilities", "web_scraper", "false")
        self.config.set("capabilities", "date_queries", "true")
        self.config.set("capabilities", "text_queries", "true")
        self.config.set("capabilities", "fulltext_download", "false")
        self.config.set("capabilities", "metadata_export", "true")
        self.config.set("capabilities", "csv_export", "true")

    def get_capability(self, capability: str) -> bool:
        """Check if a repository has a specific capability.

        Args:
            capability: Name of the capability to check

        Returns:
            True if the capability is available, False otherwise
        """
        if not self.config.has_section("capabilities"):
            return False

        return self.config.getboolean("capabilities", capability, fallback=False)

    def get_setting(self, section: str, key: str, default: Any = None) -> Any:
        """Get a setting from a specific section.

        Args:
            section: Configuration section name
            key: Setting key name
            default: Default value if setting not found

        Returns:
            The setting value or default
        """
        if not self.config.has_section(section):
            return default

        return self.config.get(section, key, fallback=default)

    def get_boolean_setting(
        self, section: str, key: str, default: bool = False
    ) -> bool:
        """Get a boolean setting from a specific section.

        Args:
            section: Configuration section name
            key: Setting key name
            default: Default value if setting not found

        Returns:
            The boolean setting value or default
        """
        if not self.config.has_section(section):
            return default

        return self.config.getboolean(section, key, fallback=default)

    def get_supported_formats(self) -> list:
        """Get list of supported download formats.

        Returns:
            List of supported format names
        """
        formats_str = self.get_setting("download", "supported_formats", "")
        return [f.strip() for f in formats_str.split(",") if f.strip()]

    def get_metadata_fields(self) -> list:
        """Get list of available metadata fields.

        Returns:
            List of metadata field names
        """
        if not self.config.has_section("metadata_fields"):
            return []

        fields = []
        for key in self.config["metadata_fields"]:
            if self.config.getboolean("metadata_fields", key, fallback=False):
                fields.append(key)

        return fields

    def supports_query_type(self, query_type: str) -> bool:
        """Check if repository supports a specific query type.

        Args:
            query_type: Type of query to check

        Returns:
            True if query type is supported, False otherwise
        """
        return self.get_boolean_setting("query_types", query_type, default=False)

    def get_api_info(self) -> Dict[str, Any]:
        """Get API information for the repository.

        Returns:
            Dictionary with API information
        """
        if not self.config.has_section("api"):
            return {}

        return {
            "base_url": self.get_setting("api", "base_url", ""),
            "endpoints": self.get_setting("api", "endpoints", ""),
            "rate_limit": self.get_setting("api", "rate_limit", ""),
            "date_format": self.get_setting("api", "date_format", ""),
        }


def get_repository_config(repository_name: str) -> RepositoryConfig:
    """Get configuration for a specific repository.

    Args:
        repository_name: Name of the repository

    Returns:
        RepositoryConfig object for the repository
    """
    return RepositoryConfig(repository_name)


def list_available_repositories() -> list:
    """List all available repositories with configuration files.

    Returns:
        List of repository names that have configuration files
    """
    config_dir = Path(__file__).parent
    repositories = []

    for item in config_dir.iterdir():
        if item.is_dir() and (item / "config.ini").exists():
            repositories.append(item.name)

    return repositories


def get_repository_capabilities(repository_name: str) -> Dict[str, bool]:
    """Get all capabilities for a repository.

    Args:
        repository_name: Name of the repository

    Returns:
        Dictionary mapping capability names to boolean values
    """
    config = get_repository_config(repository_name)
    capabilities = {}

    if config.config.has_section("capabilities"):
        for key in config.config["capabilities"]:
            capabilities[key] = config.config.getboolean("capabilities", key)

    return capabilities
