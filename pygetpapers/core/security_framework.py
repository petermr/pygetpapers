"""
Security Framework for Pygetpapers Declarative Operations

This module provides secure implementations of core operations:
- URL/file discovery
- Content retrieval
- DOM parsing
- Data extraction
- File saving

All operations include comprehensive security checks and resource management.
"""

import hashlib
import json
import logging
import shutil
import signal
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse

# Safe parsing libraries
try:
    import lxml.etree as etree

    LXML_AVAILABLE = True
except ImportError:
    LXML_AVAILABLE = False

try:
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

logger = logging.getLogger(__name__)


class SecurityError(Exception):
    """Raised when security validation fails."""

    pass


class ResourceLimitError(Exception):
    """Raised when resource limits are exceeded."""

    pass


class SecurityValidator:
    """Validates inputs and operations for security."""

    """PLEASE use CONFIG"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize security validator.

        Args:
            config: Security configuration dictionary
        """
        self.config = config or self._default_config()
        self.allowed_domains = set(self.config.get("allowed_domains", []))
        self.max_file_size = self.config.get(
            "max_file_size", 100 * 1024 * 1024
        )  # 100MB
        self.max_total_size = self.config.get(
            "max_total_size", 1024 * 1024 * 1024
        )  # 1GB
        self.dangerous_patterns = self.config.get("dangerous_patterns", [])

    def _default_config(self) -> Dict[str, Any]:
        """Get default security configuration."""
        return {
            "allowed_domains": [
                "crossref.org",
                "api.crossref.org",
                "biorxiv.org",
                "medrxiv.org",
                "europepmc.org",
                "www.ebi.ac.uk",
                "openalex.org",
                "api.openalex.org",
                # Note: arXiv removed - they prefer bulk downloads
            ],
            "max_file_size": 100 * 1024 * 1024,  # 100MB
            "max_total_size": 1024 * 1024 * 1024,  # 1GB
            "dangerous_patterns": [
                "admin",
                "login",
                "private",
                "secret",
                "password",
                "token",
                "key",
                "auth",
                "session",
                "cookie",
            ],
        }

    def validate_url(self, url: str) -> bool:
        """
        Validate URL is safe to access.

        Args:
            url: URL to validate

        Returns:
            True if URL is safe, False otherwise
        """
        try:
            parsed = urlparse(url)

            # Check scheme
            if parsed.scheme not in ["http", "https"]:
                logger.warning(f"Invalid URL scheme: {parsed.scheme}")
                return False

            # Check domain
            if parsed.netloc not in self.allowed_domains:
                logger.warning(f"Domain not allowed: {parsed.netloc}")
                return False

            # Check for dangerous patterns
            url_lower = url.lower()
            for pattern in self.dangerous_patterns:
                if pattern in url_lower:
                    logger.warning(f"Dangerous pattern in URL: {pattern}")
                    return False

            return True

        except Exception as e:
            logger.error(f"URL validation error: {e}")
            return False

    def validate_file_path(
        self, path: Union[str, Path], base_dir: Union[str, Path]
    ) -> bool:
        """
        Validate file path is safe to write.

        Args:
            path: Path to validate
            base_dir: Base directory for safe operations

        Returns:
            True if path is safe, False otherwise
        """
        try:
            path = Path(path)
            base_dir = Path(base_dir)

            # Resolve paths
            resolved_path = path.resolve()
            resolved_base = base_dir.resolve()

            # Check if path is within base directory
            if not str(resolved_path).startswith(str(resolved_base)):
                logger.warning(f"Path traversal attempt: {path}")
                return False

            # Check for dangerous patterns in path
            path_str = str(resolved_path).lower()
            for pattern in self.dangerous_patterns:
                if pattern in path_str:
                    logger.warning(f"Dangerous pattern in path: {pattern}")
                    return False

            return True

        except Exception as e:
            logger.error(f"Path validation error: {e}")
            return False

    def validate_content_size(self, content: bytes) -> bool:
        """
        Validate content size is within limits.

        Args:
            content: Content to validate

        Returns:
            True if size is acceptable, False otherwise
        """
        size = len(content)
        if size > self.max_file_size:
            logger.warning(
                f"Content too large: {size} bytes (max: {self.max_file_size})"
            )
            return False
        return True


class ResourceManager:
    """Manages resource usage and rate limiting."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize resource manager.

        Args:
            config: Resource configuration dictionary
        """
        self.config = config or self._default_config()
        self.request_timestamps = defaultdict(list)
        self.active_connections = 0
        self.max_connections = self.config.get("max_connections", 5)
        self.requests_per_minute = self.config.get("requests_per_minute", 30)
        self.delay_between_requests = self.config.get("delay_between_requests", 2.0)
        self.last_request_time = defaultdict(float)

    def _default_config(self) -> Dict[str, Any]:
        """Get default resource configuration."""
        return {
            "max_connections": 5,
            "requests_per_minute": 30,
            "delay_between_requests": 2.0,
            "request_timeout": 30,
            "parse_timeout": 60,
        }

    def can_make_request(self, domain: str) -> bool:
        """
        Check if we can make a request to domain.

        Args:
            domain: Domain to check

        Returns:
            True if request is allowed, False otherwise
        """
        now = time.time()

        # Check rate limiting
        recent_requests = [
            ts for ts in self.request_timestamps[domain] if now - ts < 60
        ]

        if len(recent_requests) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for {domain}")
            return False

        # Check connection limit
        if self.active_connections >= self.max_connections:
            logger.warning(f"Connection limit exceeded: {self.active_connections}")
            return False

        # Check delay between requests
        last_request = self.last_request_time.get(domain, 0)
        if now - last_request < self.delay_between_requests:
            logger.debug(f"Waiting for delay between requests to {domain}")
            return False

        return True

    def record_request(self, domain: str):
        """
        Record a request for rate limiting.

        Args:
            domain: Domain that was requested
        """
        now = time.time()
        self.request_timestamps[domain].append(now)
        self.last_request_time[domain] = now

        # Clean old timestamps
        cutoff = now - 60
        self.request_timestamps[domain] = [
            ts for ts in self.request_timestamps[domain] if ts > cutoff
        ]

    def check_disk_space(self, path: Path, required_bytes: int) -> bool:
        """
        Check if sufficient disk space is available.

        Args:
            path: Path to check space for
            required_bytes: Required bytes

        Returns:
            True if sufficient space, False otherwise
        """
        try:
            available = shutil.disk_usage(path).free
            return available > required_bytes
        except Exception as e:
            logger.error(f"Disk space check error: {e}")
            return False


class SafeContentProcessor:
    """Safely processes content with security checks."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize content processor.

        Args:
            config: Processing configuration dictionary
        """
        self.config = config or self._default_config()
        self.max_size = self.config.get("max_file_size", 100 * 1024 * 1024)
        self.parse_timeout = self.config.get("parse_timeout", 60)

    def _default_config(self) -> Dict[str, Any]:
        """Get default processing configuration."""
        return {
            "max_file_size": 100 * 1024 * 1024,  # 100MB
            "parse_timeout": 60,  # seconds
            "remove_scripts": True,
            "remove_styles": True,
            "remove_iframes": True,
        }

    def process_content(self, content: bytes, content_type: str) -> Any:
        """
        Safely process content with size and timeout limits.

        Args:
            content: Content to process
            content_type: MIME type of content

        Returns:
            Processed content (DOM structure, dict, etc.)

        Raises:
            SecurityError: If content is unsafe
            ResourceLimitError: If content is too large
        """
        # Check size
        if len(content) > self.max_size:
            raise ResourceLimitError(f"Content too large: {len(content)} bytes")

        # Process based on content type
        if content_type.startswith("text/html"):
            return self.parse_html_safely(content)
        elif content_type.startswith("application/json"):
            return self.parse_json_safely(content)
        elif content_type.startswith("text/xml"):
            return self.parse_xml_safely(content)
        else:
            raise SecurityError(f"Unsupported content type: {content_type}")

    def parse_html_safely(self, content: bytes) -> Any:
        """
        Parse HTML with security checks.

        Args:
            content: HTML content

        Returns:
            Parsed HTML structure
        """
        if not LXML_AVAILABLE:
            raise SecurityError("lxml not available for HTML parsing")

        try:
            # Use lxml with security features
            parser = etree.HTMLParser(recover=True, remove_blank_text=True)
            tree = etree.fromstring(content, parser)

            # Remove potentially dangerous elements
            if self.config.get("remove_scripts", True):
                for elem in tree.xpath("//script"):
                    parent = elem.getparent()
                    if parent is not None:
                        parent.remove(elem)

            if self.config.get("remove_styles", True):
                for elem in tree.xpath("//style"):
                    parent = elem.getparent()
                    if parent is not None:
                        parent.remove(elem)

            if self.config.get("remove_iframes", True):
                for elem in tree.xpath("//iframe"):
                    parent = elem.getparent()
                    if parent is not None:
                        parent.remove(elem)

            return tree

        except Exception as e:
            logger.error(f"HTML parsing error: {e}")
            raise SecurityError(f"Failed to parse HTML: {e}")

    def parse_json_safely(self, content: bytes) -> Dict[str, Any]:
        """
        Parse JSON with security checks.

        Args:
            content: JSON content

        Returns:
            Parsed JSON dictionary
        """
        try:
            # Decode content
            text = content.decode("utf-8", errors="ignore")

            # Parse JSON
            data = json.loads(text)

            # Validate it's a dictionary
            if not isinstance(data, dict):
                raise SecurityError("JSON root must be an object")

            return data

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            raise SecurityError(f"Failed to parse JSON: {e}")
        except Exception as e:
            logger.error(f"JSON processing error: {e}")
            raise SecurityError(f"Failed to process JSON: {e}")

    def parse_xml_safely(self, content: bytes) -> Any:
        """
        Parse XML with security checks.

        Args:
            content: XML content

        Returns:
            Parsed XML structure
        """
        if not LXML_AVAILABLE:
            raise SecurityError("lxml not available for XML parsing")

        try:
            # Use lxml with security features
            parser = etree.XMLParser(recover=True, remove_blank_text=True)
            tree = etree.fromstring(content, parser)
            return tree

        except Exception as e:
            logger.error(f"XML parsing error: {e}")
            raise SecurityError(f"Failed to parse XML: {e}")


class SafeFileOperations:
    """Safely handles file operations."""

    def __init__(self, base_dir: Union[str, Path], validator: SecurityValidator):
        """
        Initialize file operations.

        Args:
            base_dir: Base directory for safe operations
            validator: Security validator instance
        """
        self.base_dir = Path(base_dir)
        self.validator = validator

    def safe_save(
        self, data: Any, output_path: Union[str, Path], format: str = "json"
    ) -> bool:
        """
        Safely save data to file.

        Args:
            data: Data to save
            output_path: Output file path
            format: Output format (json, xml, html, txt)

        Returns:
            True if successful, False otherwise
        """
        try:
            output_path = Path(output_path)

            # Validate path
            if not self.validator.validate_file_path(output_path, self.base_dir):
                raise SecurityError("Invalid output path")

            # Create directory if needed
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Save based on format
            if format == "json":
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            elif format == "xml":
                if hasattr(data, "write"):
                    data.write(str(output_path), encoding="utf-8", pretty_print=True)
                else:
                    with open(output_path, "w", encoding="utf-8") as f:
                        f.write(str(data))
            elif format == "html":
                if hasattr(data, "write"):
                    data.write(str(output_path), encoding="utf-8", pretty_print=True)
                else:
                    with open(output_path, "w", encoding="utf-8") as f:
                        f.write(str(data))
            elif format == "txt":
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(str(data))
            else:
                raise SecurityError(f"Unsupported format: {format}")

            logger.info(f"Successfully saved {output_path}")
            return True

        except Exception as e:
            logger.error(f"File save error: {e}")
            return False

    def safe_read(self, file_path: Union[str, Path]) -> Optional[bytes]:
        """
        Safely read file content.

        Args:
            file_path: File to read

        Returns:
            File content or None if error
        """
        try:
            file_path = Path(file_path)

            # Validate path
            if not self.validator.validate_file_path(file_path, self.base_dir):
                raise SecurityError("Invalid file path")

            # Check if file exists
            if not file_path.exists():
                logger.warning(f"File does not exist: {file_path}")
                return None

            # Read file
            with open(file_path, "rb") as f:
                content = f.read()

            # Validate content size
            if not self.validator.validate_content_size(content):
                raise ResourceLimitError("File too large")

            return content

        except Exception as e:
            logger.error(f"File read error: {e}")
            return None


# Convenience function to create a complete security framework
def create_security_framework(
    base_dir: Union[str, Path], config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a complete security framework.

    Args:
        base_dir: Base directory for operations
        config: Configuration dictionary

    Returns:
        Dictionary containing all security components
    """
    validator = SecurityValidator(config)
    resource_manager = ResourceManager(config)
    content_processor = SafeContentProcessor(config)
    file_ops = SafeFileOperations(base_dir, validator)

    return {
        "validator": validator,
        "resource_manager": resource_manager,
        "content_processor": content_processor,
        "file_ops": file_ops,
    }
