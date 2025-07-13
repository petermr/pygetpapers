"""
Repository Configuration Loader

This module provides functionality to load and manage repository configurations
from the schema file, making it easy to create new repositories with minimal code.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from src.pygetpapers.abstract_repository import AbstractRepository

logger = logging.getLogger(__name__)


class RepositoryConfig:
    """
    Manages repository configurations loaded from the schema file.
    """

    def __init__(self, schema_path: Optional[str] = None):
        """
        Initialize the configuration loader.

        Args:
            schema_path: Path to the schema file. If None, uses default location.
        """
        if schema_path is None:
            # Look for schema in config directory relative to this file
            current_dir = Path(__file__).parent
            schema_path = (
                current_dir.parent.parent / "config" / "repository_schema.yaml"
            )

        self.schema_path = Path(schema_path)
        self._schema = None
        self._load_schema()

    def _load_schema(self) -> None:
        """Load the schema from the YAML file."""
        try:
            if not self.schema_path.exists():
                raise FileNotFoundError(f"Schema file not found: {self.schema_path}")

            with open(self.schema_path, "r", encoding="utf-8") as f:
                self._schema = yaml.safe_load(f)

            logger.info(f"Loaded repository schema from {self.schema_path}")

        except Exception as e:
            logger.error(f"Failed to load schema: {e}")
            raise

    def get_repository_config(self, repository_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific repository.

        Args:
            repository_name: Name of the repository (e.g., 'crossref', 'europe_pmc')

        Returns:
            Repository configuration dictionary

        Raises:
            KeyError: If repository not found in schema
        """
        if not self._schema:
            raise RuntimeError("Schema not loaded")

        repositories = self._schema.get("repositories", {})
        if repository_name not in repositories:
            available = list(repositories.keys())
            raise KeyError(
                f"Repository '{repository_name}' not found. Available: {available}"
            )

        return repositories[repository_name].copy()

    def get_content_type_config(self, content_type: str) -> Dict[str, Any]:
        """
        Get configuration for a specific content type.

        Args:
            content_type: Name of the content type (e.g., 'metadata', 'fulltext')

        Returns:
            Content type configuration dictionary
        """
        if not self._schema:
            raise RuntimeError("Schema not loaded")

        content_types = self._schema.get("content_types", {})
        if content_type not in content_types:
            available = list(content_types.keys())
            raise KeyError(
                f"Content type '{content_type}' not found. Available: {available}"
            )

        return content_types[content_type].copy()

    def get_global_config(self) -> Dict[str, Any]:
        """
        Get global configuration settings.

        Returns:
            Global configuration dictionary
        """
        if not self._schema:
            raise RuntimeError("Schema not loaded")

        return self._schema.get("global", {}).copy()

    def list_repositories(self) -> List[str]:
        """
        Get list of available repositories.

        Returns:
            List of repository names
        """
        if not self._schema:
            raise RuntimeError("Schema not loaded")

        return list(self._schema.get("repositories", {}).keys())

    def list_content_types(self) -> List[str]:
        """
        Get list of available content types.

        Returns:
            List of content type names
        """
        if not self._schema:
            raise RuntimeError("Schema not loaded")

        return list(self._schema.get("content_types", {}).keys())

    def get_repository_content_types(self, repository_name: str) -> List[str]:
        """
        Get content types supported by a repository.

        Args:
            repository_name: Name of the repository

        Returns:
            List of supported content type names
        """
        config = self.get_repository_config(repository_name)
        return config.get("content_types", [])

    def validate_repository_config(self, repository_name: str) -> List[str]:
        """
        Validate a repository configuration and return any issues.

        Args:
            repository_name: Name of the repository to validate

        Returns:
            List of validation issues (empty if valid)
        """
        issues = []

        try:
            config = self.get_repository_config(repository_name)
        except KeyError as e:
            return [str(e)]

        # Check required fields
        required_fields = [
            "name",
            "description",
            "api_client",
            "response_structure",
            "content_types",
            "paper_key",
        ]

        for field in required_fields:
            if field not in config:
                issues.append(f"Missing required field: {field}")

        # Validate API client configuration
        if "api_client" in config:
            api_client = config["api_client"]
            if "type" not in api_client:
                issues.append("API client missing 'type' field")

        # Validate response structure
        if "response_structure" in config:
            response_structure = config["response_structure"]
            required_paths = ["items_path", "total_path", "paper_key"]
            for path in required_paths:
                if path not in response_structure:
                    issues.append(f"Response structure missing '{path}' field")

        # Validate content types
        if "content_types" in config:
            content_types = config["content_types"]
            available_types = self.list_content_types()
            for content_type in content_types:
                if content_type not in available_types:
                    issues.append(f"Unknown content type: {content_type}")

        return issues

    def create_repository_instance(self, repository_name: str) -> "AbstractRepository":
        """
        Create a repository instance using the configuration.

        Args:
            repository_name: Name of the repository

        Returns:
            Configured AbstractRepository instance
        """
        config = self.get_repository_config(repository_name)
        return AbstractRepository(repository_name, config)

    def get_dependencies_for_content_type(self, content_type: str) -> List[str]:
        """
        Get dependencies for a content type.

        Args:
            content_type: Name of the content type

        Returns:
            List of dependency content type names
        """
        config = self.get_content_type_config(content_type)
        return config.get("dependencies", [])

    def get_all_dependencies(self, content_types: List[str]) -> List[str]:
        """
        Get all dependencies for a list of content types.

        Args:
            content_types: List of content type names

        Returns:
            List of all required content types (including dependencies)
        """
        all_types = set(content_types)
        to_process = content_types.copy()

        while to_process:
            current = to_process.pop(0)
            dependencies = self.get_dependencies_for_content_type(current)

            for dep in dependencies:
                if dep not in all_types:
                    all_types.add(dep)
                    to_process.append(dep)

        return list(all_types)


# Global configuration instance
_repository_config = None


def get_repository_config(schema_path: Optional[str] = None) -> RepositoryConfig:
    """
    Get the global repository configuration instance.

    Args:
        schema_path: Optional path to schema file

    Returns:
        RepositoryConfig instance
    """
    global _repository_config

    if _repository_config is None:
        _repository_config = RepositoryConfig(schema_path)

    return _repository_config


def create_repository(
    repository_name: str, schema_path: Optional[str] = None
) -> "AbstractRepository":
    """
    Convenience function to create a repository instance.

    Args:
        repository_name: Name of the repository
        schema_path: Optional path to schema file

    Returns:
        Configured AbstractRepository instance
    """
    config = get_repository_config(schema_path)
    return config.create_repository_instance(repository_name)
