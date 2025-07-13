"""
Abstract Repository Base Class

This module provides a generic repository implementation that can be configured
for different APIs through configuration files, reducing the need for
repository-specific code.
"""

import logging
import os
from typing import Any, Dict, List, Optional

from src.pygetpapers.download_tools import DownloadTools
from src.pygetpapers.repositoryinterface import RepositoryInterface

logger = logging.getLogger(__name__)


class AbstractRepository(RepositoryInterface):
    """
    Abstract repository implementation that handles common functionality
    across different repositories through configuration.
    """

    def __init__(self, repository_name: str, config: Dict[str, Any]):
        """
        Initialize the abstract repository.

        Args:
            repository_name: Name of the repository (e.g., 'crossref', 'europe_pmc')
            config: Repository configuration dictionary
        """
        # Initialize parent class (RepositoryInterface)
        super().__init__()

        self.repository_name = repository_name
        self.config = config
        self.download_tools = DownloadTools(repository_name)

        # Load configuration
        self.api_client_config = config.get("api_client", {})
        self.response_structure = config.get("response_structure", {})
        self.content_types = config.get("content_types", [])
        self.paper_key = config.get("paper_key", "id")

        # Initialize API client
        self.api_client = self._init_api_client()

        # XML2HTML support
        self.xml2html_supported = self._get_config_bool("xml2html_supported", False)
        self.xml2html_converters = self._get_config_list("xml2html_converters", [])

    def _get_config_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean configuration value."""
        value = self.config.get(key, default)
        if isinstance(value, str):
            return value.lower() in ("true", "yes", "1", "on")
        return bool(value)

    def _get_config_list(self, key: str, default: List[str] = None) -> List[str]:
        """Get list configuration value."""
        if default is None:
            default = []
        value = self.config.get(key, default)
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value if isinstance(value, list) else default

    def _init_api_client(self) -> Any:
        """Initialize the API client based on configuration."""
        client_config = self.api_client_config
        client_type = client_config.get("type", "requests")

        if client_type == "habanero.Crossref":
            from habanero import Crossref

            client = Crossref()
            # Apply Crossref-specific settings
            if "mailto" in client_config:
                Crossref(mailto=client_config["mailto"])
            if "user_agent" in client_config:
                version = self.download_tools.get_version()
                Crossref(ua_string=f"{client_config['user_agent']}{version}")
            return client
        elif client_type == "requests":
            import requests

            return requests.Session()
        else:
            raise ValueError(f"Unsupported API client type: {client_type}")

    def supports_xml2html(self) -> bool:
        """Check if this repository supports XML to HTML conversion."""
        return self.xml2html_supported

    def get_xml2html_converters(self) -> List[str]:
        """Get list of available XML to HTML converters for this repository."""
        return self.xml2html_converters

    def convert_xml_to_html(
        self, xml_file_path: str, identifier_for_paper: str
    ) -> bool:
        """Convert XML file to HTML using available converters."""
        if not self.supports_xml2html():
            return False

        try:
            from pygetpapers.core.simple_html_converter import SimpleHTMLConverter

            converter = SimpleHTMLConverter()
            html_file_path = xml_file_path.replace(".xml", ".xml.html")

            success, result = converter.convert_xml_to_html(
                xml_file_path, html_file_path
            )

            if success:
                msg = "Converted XML to HTML for %s"
                logger.info(msg, identifier_for_paper)
                return True
            else:
                msg = "Failed to convert XML to HTML for %s: %s"
                logger.warning(msg, identifier_for_paper, result)

        except Exception as e:
            msg = "Error converting XML to HTML for %s: %s"
            logger.error(msg, identifier_for_paper, e)

        return False

    def search_papers(
        self,
        query: str,
        limit: int,
        filters: Optional[Dict] = None,
        cursor: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generic paper search method that works with any configured repository.

        Args:
            query: Search query
            limit: Maximum number of results
            filters: Optional filters
            cursor: Optional cursor for pagination

        Returns:
            Dictionary with search results
        """
        # Build query based on repository configuration
        query_format = self.api_client_config.get("query_format", "string")

        if query_format == "dict":
            # Crossref-style: query={query}
            query_params = {query: query}
        else:
            # Europe PMC-style: query string
            query_params = query

        # Execute search
        response = self._execute_search(query_params, limit, filters, cursor)

        # Parse response using configured structure
        return self._parse_response(response, limit)

    def _execute_search(
        self,
        query: Any,
        limit: int,
        filters: Optional[Dict] = None,
        cursor: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute the search based on repository configuration."""
        client_type = self.api_client_config.get("type", "requests")

        if client_type == "habanero.Crossref":
            # Crossref-specific search
            return self.api_client.works(
                query=query, filter=filters, cursor_max=limit, cursor=cursor or "*"
            )
        elif client_type == "requests":
            # Generic HTTP API search
            return self._http_search(query, limit, filters, cursor)
        else:
            raise ValueError(f"Unsupported client type: {client_type}")

    def _http_search(
        self,
        query: str,
        limit: int,
        filters: Optional[Dict] = None,
        cursor: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute HTTP-based search."""
        # This would be implemented for repositories like Europe PMC
        # For now, raise NotImplementedError
        raise NotImplementedError("HTTP search not yet implemented")

    def _parse_response(self, response: Dict[str, Any], limit: int) -> Dict[str, Any]:
        """Parse response using configured structure."""
        structure = self.response_structure

        # Extract items
        items_path = structure.get("items_path", "items")
        items = self._get_nested_value(response, items_path, [])
        items = items[:limit] if items else []

        # Extract total count
        total_path = structure.get("total_path", "total")
        total_count = self._get_nested_value(response, total_path, 0)

        # Extract cursor for pagination
        cursor_path = structure.get("cursor_path", "cursor")
        cursor_mark = self._get_nested_value(response, cursor_path, None)

        # Convert to standard format
        metadata_dict = self.download_tools._make_dict_from_list(items, self.paper_key)

        # Add download status keys
        for paper in metadata_dict:
            self.download_tools._add_download_status_keys(paper, metadata_dict)

        # Create result dictionary
        result_dict = self.download_tools._adds_new_results_to_metadata_dictionary(
            cursor_mark, metadata_dict, total_count, None
        )

        return result_dict

    def _get_nested_value(
        self, data: Dict[str, Any], path: str, default: Any = None
    ) -> Any:
        """Get nested value from dictionary using dot notation."""
        keys = path.split(".")
        current = data

        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default

        return current

    def noexecute(self, query_namespace: Dict[str, Any]) -> None:
        """Execute search without downloading files."""
        query = query_namespace.get("query", "")
        filters = query_namespace.get("filter")
        limit = query_namespace.get("limit", 10)

        result_dict = self.search_papers(query, limit, filters)
        total_hits = result_dict["new_results"]["total_hits"]

        logger.info(f"Total number of hits for the query are {total_hits}")

    def apipaperdownload(self, query_namespace: Dict[str, Any]) -> None:
        """Download papers from the repository."""
        query = query_namespace.get("query", "")
        filters = query_namespace.get("filter")
        limit = query_namespace.get("limit", 100)
        makecsv = query_namespace.get("makecsv", False)
        makexml = query_namespace.get("xml", False)
        makehtml = query_namespace.get("makehtml", False)

        result_dict = self.search_papers(query, limit, filters)

        # Generate output files
        metadata_dict = result_dict["new_results"]["total_json_output"]
        file_name = f"{self.repository_name}_result"

        self.download_tools.handle_creation_of_csv_html_xml(
            makecsv, makehtml, makexml, metadata_dict, file_name
        )

        # Save individual paper metadata
        self.download_tools._make_metadata_json_files_for_paper(
            result_dict["new_results"],
            updated_dict=result_dict["updated_dict"],
            paper_key=self.paper_key,
            name_of_file=file_name,
        )

    def update(self, query_namespace: Dict[str, Any]) -> None:
        """Update existing corpus with new results."""
        # Read existing metadata
        update_path = self.get_metadata_results_file()
        os.chdir(os.path.dirname(update_path))
        update = self.download_tools.readjsondata(update_path)

        # Execute search with cursor from previous run
        query = query_namespace.get("query", "")
        filters = query_namespace.get("filter")
        limit = query_namespace.get("limit", 100)
        cursor = update.get("cursor_mark") if update else None

        result_dict = self.search_papers(query, limit, filters, cursor)

        # Save updated metadata
        file_name = f"{self.repository_name}_result"
        self.download_tools._make_metadata_json_files_for_paper(
            result_dict["new_results"],
            updated_dict=result_dict["updated_dict"],
            paper_key=self.paper_key,
            name_of_file=file_name,
        )

    def get_metadata_results_file(self) -> str:
        """Get the path to the metadata results file."""
        return self.download_tools.get_metadata_results_file()
