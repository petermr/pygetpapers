"""
Configuration Parser for Web Scraping Framework

This module handles loading, parsing, and validating scraping configurations
from INI files. It supports multiple configuration sources and provides
validation to ensure configurations are complete and correct.
"""

import configparser
import logging
import os
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class ScrapingConfigParser:
    """
    Parse and validate scraping configurations from INI files.

    Supports loading configurations from multiple sources:
    - System-wide configuration
    - User configuration
    - Local configuration
    - Environment-specific configuration
    """

    def __init__(self, config_paths: Optional[List[str]] = None):
        """
        Initialize the configuration parser.

        Args:
            config_paths: List of configuration file paths to load
        """
        self.config_paths = config_paths or self._get_default_config_paths()
        self.config = configparser.ConfigParser()
        self._load_configurations()

    def _get_default_config_paths(self) -> List[str]:
        """
        Get default configuration file paths.

        Returns:
            List of configuration file paths in order of precedence
        """
        configs = []

        # System-wide configuration
        system_config = "/etc/pygetpapers/scraping_config.ini"
        if os.path.exists(system_config):
            configs.append(system_config)

        # User configuration
        user_config = os.path.expanduser("~/.pygetpapers/scraping_config.ini")
        if os.path.exists(user_config):
            configs.append(user_config)

        # Local configuration
        local_config = "./scraping_config.ini"
        if os.path.exists(local_config):
            configs.append(local_config)

        # Environment-specific configuration
        env_config = os.getenv("PYGETPAPERS_SCRAPING_CONFIG")
        if env_config and os.path.exists(env_config):
            configs.append(env_config)

        return configs

    def _load_configurations(self):
        """Load and merge configurations from all sources."""
        if not self.config_paths:
            logger.warning("No configuration files found")
            return

        # Load all configuration files
        for config_path in self.config_paths:
            try:
                if os.path.exists(config_path):
                    self.config.read(config_path, encoding="utf-8")
                    logger.info(f"Loaded configuration from: {config_path}")
                else:
                    logger.debug(f"Configuration file not found: {config_path}")
            except Exception as e:
                logger.error(f"Error loading configuration from {config_path}: {e}")

    def get_available_repositories(self) -> List[str]:
        """
        Get list of available web scraping repositories.

        Returns:
            List of repository names
        """
        if "repositories" in self.config and "available" in self.config["repositories"]:
            repos = self.config["repositories"]["available"].split(",")
            return [repo.strip() for repo in repos if repo.strip()]
        return []

    def load_repository_config(self, repo_name: str) -> Optional[Dict[str, Any]]:
        """
        Load configuration for a specific repository.

        Args:
            repo_name: Name of the repository

        Returns:
            Dictionary with repository configuration or None if not found
        """
        if not self.config.has_section(repo_name):
            logger.warning(f"Repository configuration not found: {repo_name}")
            return None

        config = {}

        # Load basic repository settings
        basic_fields = [
            "name",
            "description",
            "base_url",
            "search_url",
            "enabled",
            "rate_limit",
            "max_requests_per_minute",
            "user_agent",
            "respect_robots_txt",
            "timeout",
            "max_retries",
        ]

        for field in basic_fields:
            if self.config.has_option(repo_name, field):
                value = self.config.get(repo_name, field)
                # Convert boolean strings
                if field == "enabled" or field == "respect_robots_txt":
                    config[field] = value.lower() in ("true", "yes", "1", "on")
                # Convert numeric values
                elif field in [
                    "rate_limit",
                    "max_requests_per_minute",
                    "timeout",
                    "max_retries",
                ]:
                    try:
                        config[field] = float(value) if "." in value else int(value)
                    except ValueError:
                        config[field] = value
                else:
                    config[field] = value

        # Load subsections
        subsections = [
            "search",
            "selectors",
            "pagination",
            "filters",
            "transformations",
            "error_handling",
            "output",
        ]

        for subsection in subsections:
            section_name = f"{repo_name}.{subsection}"
            if self.config.has_section(section_name):
                config[subsection] = dict(self.config[section_name])

        # Load global settings
        config["global"] = self._load_global_config()

        return config

    def _load_global_config(self) -> Dict[str, Any]:
        """
        Load global configuration settings.

        Returns:
            Dictionary with global configuration
        """
        global_config = {}

        if self.config.has_section("global"):
            for key, value in self.config["global"].items():
                # Convert boolean strings
                if value.lower() in ("true", "false"):
                    global_config[key] = value.lower() == "true"
                # Convert numeric values
                elif key in [
                    "default_rate_limit",
                    "default_timeout",
                    "default_max_retries",
                    "cache_duration",
                    "max_concurrent_requests",
                ]:
                    try:
                        global_config[key] = (
                            float(value) if "." in value else int(value)
                        )
                    except ValueError:
                        global_config[key] = value
                else:
                    global_config[key] = value

        # Load global transformations
        if self.config.has_section("global.transformations"):
            global_config["transformations"] = dict(
                self.config["global.transformations"]
            )

        # Load global error handling
        if self.config.has_section("global.error_handling"):
            global_config["error_handling"] = dict(self.config["global.error_handling"])

        return global_config

    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """
        Validate repository configuration and return errors.

        Args:
            config: Repository configuration dictionary

        Returns:
            List of validation error messages
        """
        errors = []

        # Check required fields
        required_fields = ["base_url", "search_url"]
        for field in required_fields:
            if field not in config:
                errors.append(f"Missing required field: {field}")

        # Check selectors
        if "selectors" in config:
            required_selectors = ["results_container", "paper_entry", "title"]
            for selector in required_selectors:
                if selector not in config["selectors"]:
                    errors.append(f"Missing required selector: {selector}")
        else:
            errors.append("Missing required section: selectors")

        # Validate URLs
        if "base_url" in config:
            if not config["base_url"].startswith(("http://", "https://")):
                errors.append("base_url must be a valid HTTP/HTTPS URL")

        if "search_url" in config:
            if "{query}" not in config["search_url"]:
                errors.append("search_url must contain {query} placeholder")

        # Validate numeric fields
        numeric_fields = [
            "rate_limit",
            "max_requests_per_minute",
            "timeout",
            "max_retries",
        ]
        for field in numeric_fields:
            if field in config and not isinstance(config[field], (int, float)):
                errors.append(f"{field} must be a number")

        # Validate boolean fields
        boolean_fields = ["enabled", "respect_robots_txt"]
        for field in boolean_fields:
            if field in config and not isinstance(config[field], bool):
                errors.append(f"{field} must be a boolean")

        return errors

    def is_repository_enabled(self, repo_name: str) -> bool:
        """
        Check if a repository is enabled.

        Args:
            repo_name: Name of the repository

        Returns:
            True if repository is enabled, False otherwise
        """
        config = self.load_repository_config(repo_name)
        if not config:
            return False

        return config.get("enabled", False)

    def get_repository_info(self, repo_name: str) -> Optional[Dict[str, Any]]:
        """
        Get basic repository information.

        Args:
            repo_name: Name of the repository

        Returns:
            Dictionary with repository information or None if not found
        """
        config = self.load_repository_config(repo_name)
        if not config:
            return None

        return {
            "name": config.get("name", repo_name),
            "description": config.get("description", ""),
            "enabled": config.get("enabled", False),
            "base_url": config.get("base_url", ""),
            "rate_limit": config.get("rate_limit", 2.0),
            "max_requests_per_minute": config.get("max_requests_per_minute", 30),
        }

    def get_selector(self, config: Dict[str, Any], field: str) -> Optional[str]:
        """
        Get the best selector for a field with fallbacks.

        Args:
            config: Repository configuration
            field: Field name to get selector for

        Returns:
            Selector string or None if not found
        """
        if "selectors" not in config:
            return None

        selectors = config["selectors"]
        if field not in selectors:
            return None

        # Return the first selector (fallbacks are handled by the HTML parser)
        selector_list = selectors[field].split(",")
        return selector_list[0].strip() if selector_list else None

    def get_all_selectors(self, config: Dict[str, Any], field: str) -> List[str]:
        """
        Get all selectors for a field (including fallbacks).

        Args:
            config: Repository configuration
            field: Field name to get selectors for

        Returns:
            List of selector strings
        """
        if "selectors" not in config:
            return []

        selectors = config["selectors"]
        if field not in selectors:
            return []

        # Split by comma and strip whitespace
        selector_list = selectors[field].split(",")
        return [selector.strip() for selector in selector_list if selector.strip()]

    def get_transformations(self, config: Dict[str, Any], field: str) -> List[str]:
        """
        Get transformation rules for a field.

        Args:
            config: Repository configuration
            field: Field name to get transformations for

        Returns:
            List of transformation rule names
        """
        if "transformations" not in config:
            return []

        transformations = config["transformations"]
        if field not in transformations:
            return []

        # Split by comma and strip whitespace
        transform_list = transformations[field].split(",")
        return [transform.strip() for transform in transform_list if transform.strip()]

    def create_configuration_template(self, repo_name: str) -> str:
        """
        Create a configuration template for a new repository.

        Args:
            repo_name: Name of the new repository

        Returns:
            Configuration template string
        """
        template = f"""[{repo_name}]
name = {repo_name.title()} Web Search
description = Web-based search for {repo_name} papers
base_url = https://example.com
search_url = https://example.com/search/{{query}}
enabled = false
rate_limit = 2.0
max_requests_per_minute = 30
user_agent = pygetpapers-web-scraper/1.0
respect_robots_txt = true
timeout = 30
max_retries = 3

[{repo_name}.search]
method = GET
query_parameter = query
encoding = url_encode
pagination = true
results_per_page = 20

[{repo_name}.selectors]
results_container = div.results, main, div.content
paper_entry = article, div.paper, div.result
title = h1.title, h2.title, h3.title, a.title
authors = div.authors, span.author, div.author-list
doi = a[href*="doi.org"], span.doi, div.doi
publication_date = time.date, span.date, div.date

[{repo_name}.pagination]
container = nav.pagination, div.pagination
next_button = a.next, a[rel="next"]
previous_button = a.previous, a[rel="prev"]
current_page = span.current, .current
page_numbers = a.page, .page-link

[{repo_name}.filters]
subject_area = false
article_type = false
date_range = false
author = false

[{repo_name}.transformations]
title = strip_whitespace, remove_html_tags
authors = strip_whitespace
publication_date = parse_date
doi = normalize_doi

[{repo_name}.error_handling]
max_retries = 3
retry_delay = 5.0
exponential_backoff = true
skip_failed_papers = true
log_errors = true
continue_on_error = true

[{repo_name}.output]
format = pygetpapers_json
metadata_fields = title, authors, doi, publication_date
required_fields = title
optional_fields = authors, doi, publication_date
output_encoding = utf-8
"""
        return template

    def save_configuration(self, config: Dict[str, Any], filepath: str):
        """
        Save configuration to a file.

        Args:
            config: Configuration dictionary
            filepath: Path to save the configuration file
        """
        try:
            # Create directory if it doesn't exist
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)

            # Convert back to configparser format and save
            config_parser = configparser.ConfigParser()

            # Add repositories section
            config_parser.add_section("repositories")
            config_parser.set(
                "repositories",
                "available",
                ", ".join(self.get_available_repositories()),
            )

            # Add repository sections
            for repo_name, repo_config in config.items():
                if isinstance(repo_config, dict):
                    config_parser.add_section(repo_name)
                    for key, value in repo_config.items():
                        if isinstance(value, dict):
                            # Handle subsections
                            for subkey, subvalue in value.items():
                                config_parser.set(
                                    f"{repo_name}.{key}", subkey, str(subvalue)
                                )
                        else:
                            config_parser.set(repo_name, key, str(value))

            with open(filepath, "w", encoding="utf-8") as f:
                config_parser.write(f)

            logger.info(f"Configuration saved to: {filepath}")

        except Exception as e:
            logger.error(f"Error saving configuration to {filepath}: {e}")
            raise
