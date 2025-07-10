"""
Web Scraping Repository Interface for Pygetpapers

This module provides a repository interface that integrates the web scraping
framework with pygetpapers' existing repository system. It allows web scraping
repositories to be used alongside API-based repositories.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config_parser import ScrapingConfigParser
from .generic_scraper import GenericWebScraper

logger = logging.getLogger(__name__)


class WebScrapingRepository:
    """
    Repository interface that integrates web scraping with pygetpapers.

    This class provides a unified interface for web scraping repositories
    that can be used alongside existing API-based repositories in pygetpapers.
    """

    def __init__(
        self, repo_name: str, config_parser: Optional[ScrapingConfigParser] = None
    ):
        """
        Initialize the web scraping repository.

        Args:
            repo_name: Name of the repository
            config_parser: Configuration parser instance
        """
        self.repo_name = repo_name
        self.config_parser = config_parser or ScrapingConfigParser()
        self.scraper = GenericWebScraper(self.config_parser)

        # Load repository configuration
        self.config = self.config_parser.load_repository_config(repo_name)
        if not self.config:
            raise ValueError(f"Repository configuration not found: {repo_name}")

    def search(
        self,
        query: str,
        max_results: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
        output_dir: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Search for papers using web scraping.

        Args:
            query: Search query string
            max_results: Maximum number of results to return
            filters: Additional filters to apply
            output_dir: Directory to save results (optional)

        Returns:
            Dictionary with search results and metadata
        """
        try:
            # Perform search
            results = self.scraper.search_papers(
                self.repo_name, query, max_results, filters
            )

            # Save results if output directory is specified
            if output_dir:
                self._save_results(results, output_dir)

            return results

        except Exception as e:
            logger.error(f"Error searching {self.repo_name}: {e}")
            raise

    def _save_results(self, results: Dict[str, Any], output_dir: str):
        """
        Save search results to the output directory.

        Args:
            results: Search results dictionary
            output_dir: Output directory path
        """
        try:
            # Create output directory
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            # Save in multiple formats
            formats = ["json", "csv"]
            for format_type in formats:
                try:
                    self.scraper.save_results(results, output_dir, format_type)
                except Exception as e:
                    logger.warning(f"Error saving {format_type} format: {e}")

            # Create metadata file
            self._create_metadata_file(results, output_path)

        except Exception as e:
            logger.error(f"Error saving results: {e}")
            raise

    def _create_metadata_file(self, results: Dict[str, Any], output_path: Path):
        """
        Create a metadata file with search information.

        Args:
            results: Search results dictionary
            output_path: Output directory path
        """
        metadata = {
            "repository": self.repo_name,
            "query": results["query"],
            "total_results": results["metadata"]["total_results"],
            "pages_scraped": results["metadata"]["pages_scraped"],
            "scraped_at": results["metadata"].get("scraped_at", ""),
            "errors": results["metadata"]["errors"],
            "warnings": results["metadata"]["warnings"],
            "config": {
                "name": self.config.get("name", self.repo_name),
                "description": self.config.get("description", ""),
                "base_url": self.config.get("base_url", ""),
                "rate_limit": self.config.get("rate_limit", 2.0),
            },
        }

        import json

        metadata_file = output_path / f"{self.repo_name}_metadata.json"
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

    def get_info(self) -> Dict[str, Any]:
        """
        Get repository information.

        Returns:
            Dictionary with repository information
        """
        return {
            "name": self.config.get("name", self.repo_name),
            "description": self.config.get("description", ""),
            "type": "web_scraping",
            "base_url": self.config.get("base_url", ""),
            "enabled": self.config.get("enabled", False),
            "rate_limit": self.config.get("rate_limit", 2.0),
            "max_requests_per_minute": self.config.get("max_requests_per_minute", 30),
            "supported_filters": list(self.config.get("filters", {}).keys()),
            "output_formats": ["json", "csv", "xml"],
        }

    def validate_config(self) -> List[str]:
        """
        Validate repository configuration.

        Returns:
            List of validation errors
        """
        return self.config_parser.validate_config(self.config)

    def is_enabled(self) -> bool:
        """
        Check if the repository is enabled.

        Returns:
            True if repository is enabled, False otherwise
        """
        return self.config.get("enabled", False)

    def get_supported_filters(self) -> List[str]:
        """
        Get list of supported filters.

        Returns:
            List of supported filter names
        """
        return list(self.config.get("filters", {}).keys())

    def get_output_formats(self) -> List[str]:
        """
        Get list of supported output formats.

        Returns:
            List of supported output formats
        """
        return ["json", "csv", "xml"]


class WebScrapingRepositoryManager:
    """
    Manager for web scraping repositories.

    This class provides a centralized way to manage multiple web scraping
    repositories and integrate them with pygetpapers.
    """

    def __init__(self, config_parser: Optional[ScrapingConfigParser] = None):
        """
        Initialize the repository manager.

        Args:
            config_parser: Configuration parser instance
        """
        self.config_parser = config_parser or ScrapingConfigParser()
        self.repositories = {}
        self._load_repositories()

    def _load_repositories(self):
        """Load all available web scraping repositories."""
        available_repos = self.config_parser.get_available_repositories()

        for repo_name in available_repos:
            try:
                if self.config_parser.is_repository_enabled(repo_name):
                    repo = WebScrapingRepository(repo_name, self.config_parser)
                    self.repositories[repo_name] = repo
                    logger.info(f"Loaded web scraping repository: {repo_name}")
            except Exception as e:
                logger.error(f"Error loading repository {repo_name}: {e}")

    def get_repository(self, repo_name: str) -> Optional[WebScrapingRepository]:
        """
        Get a specific repository by name.

        Args:
            repo_name: Name of the repository

        Returns:
            Repository instance or None if not found
        """
        return self.repositories.get(repo_name)

    def list_repositories(self) -> List[str]:
        """
        Get list of available repository names.

        Returns:
            List of repository names
        """
        return list(self.repositories.keys())

    def get_repository_info(self, repo_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific repository.

        Args:
            repo_name: Name of the repository

        Returns:
            Repository information dictionary or None if not found
        """
        repo = self.get_repository(repo_name)
        if repo:
            return repo.get_info()
        return None

    def search_all_repositories(
        self,
        query: str,
        max_results: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
        output_dir: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Search all repositories and combine results.

        Args:
            query: Search query string
            max_results: Maximum number of results per repository
            filters: Additional filters to apply
            output_dir: Directory to save results (optional)

        Returns:
            Dictionary with combined search results
        """
        combined_results = {
            "query": query,
            "repositories_searched": [],
            "total_papers": 0,
            "papers_by_repository": {},
            "errors": [],
            "metadata": {},
        }

        for repo_name, repo in self.repositories.items():
            try:
                logger.info(f"Searching repository: {repo_name}")

                # Create repository-specific output directory
                repo_output_dir = None
                if output_dir:
                    repo_output_dir = os.path.join(output_dir, repo_name)

                # Perform search
                results = repo.search(query, max_results, filters, repo_output_dir)

                # Add to combined results
                combined_results["repositories_searched"].append(repo_name)
                combined_results["papers_by_repository"][repo_name] = results
                combined_results["total_papers"] += len(results["papers"])

                # Add errors
                if results["metadata"]["errors"]:
                    combined_results["errors"].extend(
                        [
                            f"{repo_name}: {error}"
                            for error in results["metadata"]["errors"]
                        ]
                    )

            except Exception as e:
                error_msg = f"Error searching {repo_name}: {e}"
                logger.error(error_msg)
                combined_results["errors"].append(error_msg)

        # Save combined results if output directory is specified
        if output_dir:
            self._save_combined_results(combined_results, output_dir)

        return combined_results

    def _save_combined_results(self, combined_results: Dict[str, Any], output_dir: str):
        """
        Save combined results from all repositories.

        Args:
            combined_results: Combined search results
            output_dir: Output directory path
        """
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            # Save combined results as JSON
            import json

            combined_file = output_path / "combined_results.json"
            with open(combined_file, "w", encoding="utf-8") as f:
                json.dump(combined_results, f, indent=2, ensure_ascii=False)

            # Create summary file
            self._create_summary_file(combined_results, output_path)

        except Exception as e:
            logger.error(f"Error saving combined results: {e}")

    def _create_summary_file(self, combined_results: Dict[str, Any], output_path: Path):
        """
        Create a summary file with search statistics.

        Args:
            combined_results: Combined search results
            output_path: Output directory path
        """
        summary = {
            "search_query": combined_results["query"],
            "repositories_searched": combined_results["repositories_searched"],
            "total_papers_found": combined_results["total_papers"],
            "papers_per_repository": {
                repo: len(results["papers"])
                for repo, results in combined_results["papers_by_repository"].items()
            },
            "errors_encountered": len(combined_results["errors"]),
            "search_timestamp": combined_results.get("metadata", {}).get(
                "timestamp", ""
            ),
        }

        import json

        summary_file = output_path / "search_summary.json"
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

    def validate_all_repositories(self) -> Dict[str, List[str]]:
        """
        Validate all repository configurations.

        Returns:
            Dictionary mapping repository names to validation errors
        """
        validation_results = {}

        for repo_name, repo in self.repositories.items():
            errors = repo.validate_config()
            if errors:
                validation_results[repo_name] = errors

        return validation_results

    def reload_repositories(self):
        """Reload all repository configurations."""
        self.repositories.clear()
        self._load_repositories()
        logger.info("Reloaded all web scraping repositories")

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about all repositories.

        Returns:
            Dictionary with repository statistics
        """
        stats = {
            "total_repositories": len(self.repositories),
            "enabled_repositories": sum(
                1 for repo in self.repositories.values() if repo.is_enabled()
            ),
            "repository_names": list(self.repositories.keys()),
            "validation_errors": self.validate_all_repositories(),
        }

        return stats
