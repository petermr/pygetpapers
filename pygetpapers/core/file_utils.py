"""
File Operations Utilities

This module provides common file operations that can be used across
different repository implementations to reduce code duplication.
"""

import json
import logging
import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class FileUtils:
    """
    Static utility class for common file operations.

    This class provides common patterns for file operations that are used
    across multiple repository implementations.
    """

    @staticmethod
    def create_directory(path: Union[str, Path], exist_ok: bool = True) -> Path:
        """
        Create directory with proper error handling.

        Args:
            path: Directory path
            exist_ok: Whether to ignore existing directory

        Returns:
            Path object for the created directory
        """
        path = Path(path)
        try:
            path.mkdir(parents=True, exist_ok=exist_ok)
            return path
        except Exception as e:
            logger.error(f"Error creating directory {path}: {e}")
            raise

    @staticmethod
    def write_json_data(
        data: Dict[str, Any],
        file_path: Union[str, Path],
        encoding: str = "utf-8",
        indent: int = 2,
    ) -> bool:
        """
        Write data to JSON file with proper error handling.

        Args:
            data: Data to write
            file_path: Output file path
            encoding: File encoding
            indent: JSON indentation

        Returns:
            True if successful, False otherwise
        """
        file_path = Path(file_path)
        try:
            # Create parent directory if it doesn't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "w", encoding=encoding) as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Error writing JSON file {file_path}: {e}")
            return False

    @staticmethod
    def write_xml_data(
        data: Dict[str, Any],
        file_path: Union[str, Path],
        encoding: str = "utf-8",
        root_name: str = "metadata",
    ) -> bool:
        """
        Write data to XML file with proper formatting.

        Args:
            data: Data to write
            file_path: Output file path
            encoding: File encoding
            root_name: Root element name

        Returns:
            True if successful, False otherwise
        """
        file_path = Path(file_path)
        try:
            # Create parent directory if it doesn't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Create XML structure
            root = ET.Element(root_name)
            FileUtils._dict_to_xml(data, root)

            # Create tree and write with pretty formatting
            tree = ET.ElementTree(root)
            ET.indent(tree, space="  ")  # Pretty print

            with open(file_path, "w", encoding=encoding) as f:
                tree.write(f, encoding=encoding, xml_declaration=True)
            return True
        except Exception as e:
            logger.error(f"Error writing XML file {file_path}: {e}")
            return False

    @staticmethod
    def _dict_to_xml(data: Dict[str, Any], parent: ET.Element) -> None:
        """Convert dictionary to XML elements."""
        for key, value in data.items():
            # Clean key name for XML
            clean_key = re.sub(r"[^a-zA-Z0-9_]", "_", str(key))

            if isinstance(value, dict):
                child = ET.SubElement(parent, clean_key)
                FileUtils._dict_to_xml(value, child)
            elif isinstance(value, list):
                child = ET.SubElement(parent, clean_key)
                for item in value:
                    if isinstance(item, dict):
                        item_elem = ET.SubElement(child, "item")
                        FileUtils._dict_to_xml(item, item_elem)
                    else:
                        item_elem = ET.SubElement(child, "item")
                        item_elem.text = str(item)
            else:
                child = ET.SubElement(parent, clean_key)
                child.text = str(value) if value is not None else ""

    @staticmethod
    def write_html_content(
        content: str, file_path: Union[str, Path], encoding: str = "utf-8"
    ) -> bool:
        """
        Write HTML content to file.

        Args:
            content: HTML content to write
            file_path: Output file path
            encoding: File encoding

        Returns:
            True if successful, False otherwise
        """
        file_path = Path(file_path)
        try:
            # Create parent directory if it doesn't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "w", encoding=encoding) as f:
                f.write(content)
            return True
        except Exception as e:
            logger.error(f"Error writing HTML file {file_path}: {e}")
            return False

    @staticmethod
    def write_binary_content(content: bytes, file_path: Union[str, Path]) -> bool:
        """
        Write binary content to file.

        Args:
            content: Binary content to write
            file_path: Output file path

        Returns:
            True if successful, False otherwise
        """
        file_path = Path(file_path)
        try:
            # Create parent directory if it doesn't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "wb") as f:
                f.write(content)
            return True
        except Exception as e:
            logger.error(f"Error writing binary file {file_path}: {e}")
            return False

    @staticmethod
    def generate_article_id(
        metadata: Dict[str, Any], url: str = "", prefix: str = ""
    ) -> str:
        """
        Generate a unique article ID from metadata or URL.

        Args:
            metadata: Article metadata
            url: Article URL
            prefix: Optional prefix for the ID

        Returns:
            Generated article ID
        """
        # Try to extract ID from URL first
        if url:
            # Extract ID from Redalyc URLs
            redalyc_match = re.search(r"articulo\.oa\?id=(\d+)", url)
            if redalyc_match:
                return f"{prefix}REDALYC_{redalyc_match.group(1)}"

            # Extract ID from other repository URLs
            id_match = re.search(r"/(\d+)(?:[/?]|$)", url)
            if id_match:
                return f"{prefix}{id_match.group(1)}"

        # Try to use DOI
        if metadata.get("doi"):
            doi_clean = re.sub(r"[^\w\-]", "_", metadata["doi"])
            return f"{prefix}{doi_clean}"

        # Try to use title (first few words)
        if metadata.get("title"):
            title_clean = re.sub(r"[^\w\s]", "", metadata["title"])
            title_words = title_clean.split()[:3]
            if title_words:
                return f"{prefix}{'_'.join(title_words)}"

        # Fallback to hash of URL or timestamp
        import hashlib

        if url:
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            return f"{prefix}hash_{url_hash}"
        else:
            import time

            timestamp = int(time.time())
            return f"{prefix}timestamp_{timestamp}"

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename for safe file system usage.

        Args:
            filename: Original filename

        Returns:
            Sanitized filename
        """
        # Remove or replace problematic characters
        sanitized = re.sub(r'[<>:"/\\|?*]', "_", filename)
        sanitized = re.sub(r"\s+", "_", sanitized)
        sanitized = re.sub(r"_+", "_", sanitized)
        sanitized = sanitized.strip("_.")

        # Limit length
        if len(sanitized) > 200:
            sanitized = sanitized[:200]

        return sanitized

    @staticmethod
    def get_file_extension(content_type: str) -> str:
        """
        Get file extension from content type.

        Args:
            content_type: MIME content type

        Returns:
            File extension (with dot)
        """
        content_type_map = {
            "application/pdf": ".pdf",
            "application/xml": ".xml",
            "text/html": ".html",
            "text/xml": ".xml",
            "application/json": ".json",
            "text/plain": ".txt",
        }

        return content_type_map.get(content_type.lower(), ".txt")

    @staticmethod
    def save_article_files(
        metadata: Dict[str, Any],
        output_dir: Union[str, Path],
        html_content: str = "",
        pdf_content: bytes = b"",
        xml_content: str = "",
        epub_content: bytes = b"",
        encoding: str = "utf-8",
    ) -> Dict[str, str]:
        """
        Save all article files to the output directory.

        Args:
            metadata: Article metadata
            output_dir: Output directory
            html_content: HTML content to save
            pdf_content: PDF content to save
            xml_content: XML content to save
            epub_content: ePUB content to save
            encoding: File encoding

        Returns:
            Dictionary with saved file paths
        """
        output_dir = Path(output_dir)
        FileUtils.create_directory(output_dir)

        saved_files = {}

        # Generate article ID
        article_id = FileUtils.generate_article_id(metadata, metadata.get("url", ""))

        # Save metadata as JSON
        metadata_file = output_dir / f"{article_id}_metadata.json"
        if FileUtils.write_json_data(metadata, metadata_file, encoding):
            saved_files["metadata_json"] = str(metadata_file)

        # Save metadata as XML
        metadata_xml_file = output_dir / f"{article_id}_metadata.xml"
        if FileUtils.write_xml_data(metadata, metadata_xml_file, encoding):
            saved_files["metadata_xml"] = str(metadata_xml_file)

        # Save HTML content
        if html_content:
            html_file = output_dir / "fulltext.html"
            if FileUtils.write_html_content(html_content, html_file, encoding):
                saved_files["html"] = str(html_file)

        # Save PDF content
        if pdf_content:
            pdf_file = output_dir / "fulltext.pdf"
            if FileUtils.write_binary_content(pdf_content, pdf_file):
                saved_files["pdf"] = str(pdf_file)

        # Save XML content
        if xml_content:
            xml_file = output_dir / "fulltext.xml"
            if FileUtils.write_html_content(xml_content, xml_file, encoding):
                saved_files["xml"] = str(xml_file)

        # Save ePUB content
        if epub_content:
            epub_file = output_dir / "fulltext.epub"
            if FileUtils.write_binary_content(epub_content, epub_file):
                saved_files["epub"] = str(epub_file)

        return saved_files

    @staticmethod
    def read_json_data(
        file_path: Union[str, Path], encoding: str = "utf-8"
    ) -> Optional[Dict[str, Any]]:
        """
        Read JSON data from file.

        Args:
            file_path: Input file path
            encoding: File encoding

        Returns:
            Loaded data or None if failed
        """
        file_path = Path(file_path)
        try:
            with open(file_path, "r", encoding=encoding) as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading JSON file {file_path}: {e}")
            return None

    @staticmethod
    def read_text_file(
        file_path: Union[str, Path], encoding: str = "utf-8"
    ) -> Optional[str]:
        """
        Read text file content.

        Args:
            file_path: Input file path
            encoding: File encoding

        Returns:
            File content or None if failed
        """
        file_path = Path(file_path)
        try:
            with open(file_path, "r", encoding=encoding) as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading text file {file_path}: {e}")
            return None

    @staticmethod
    def read_binary_file(file_path: Union[str, Path]) -> Optional[bytes]:
        """
        Read binary file content.

        Args:
            file_path: Input file path

        Returns:
            File content or None if failed
        """
        file_path = Path(file_path)
        try:
            with open(file_path, "rb") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading binary file {file_path}: {e}")
            return None

    @staticmethod
    def file_exists(file_path: Union[str, Path]) -> bool:
        """
        Check if file exists.

        Args:
            file_path: File path to check

        Returns:
            True if file exists, False otherwise
        """
        return Path(file_path).exists()

    @staticmethod
    def get_file_size(file_path: Union[str, Path]) -> int:
        """
        Get file size in bytes.

        Args:
            file_path: File path

        Returns:
            File size in bytes, 0 if file doesn't exist
        """
        file_path = Path(file_path)
        try:
            return file_path.stat().st_size if file_path.exists() else 0
        except Exception:
            return 0

    @staticmethod
    def check_file_size_alert(file_size_bytes: int, file_name: str = "file", threshold_mb: int = None) -> bool:
        """
        Check if file size exceeds threshold and log appropriate alert.
        
        Args:
            file_size_bytes: File size in bytes
            file_name: Name of the file for logging
            threshold_mb: Size threshold in MB (uses config default if None)
            
        Returns:
            True if file size exceeds threshold, False otherwise
        """
        from pygetpapers.core.file_size_config import file_size_config
        
        # Use configuration if threshold not specified
        if threshold_mb is None:
            threshold_mb = file_size_config.get("file_size_alert_threshold_mb", 100)
        
        # Check if alerts are enabled
        if not file_size_config.is_alerts_enabled():
            return False
            
        threshold_bytes = threshold_mb * 1024 * 1024
        
        if file_size_bytes > threshold_bytes:
            size_mb = file_size_bytes / (1024 * 1024)
            
            # Use configured message template
            alert_template = file_size_config.get("alert_message_template")
            warning_template = file_size_config.get("warning_message_template")
            
            if file_size_config.should_log_large_files():
                logger.warning(alert_template.format(
                    file_name=file_name, 
                    size_mb=size_mb, 
                    threshold_mb=threshold_mb
                ))
                logger.warning(warning_template)
            
            return True
        return False

    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """
        Format file size in human-readable format.
        
        Args:
            size_bytes: File size in bytes
            
        Returns:
            Formatted size string (e.g., "1.5 MB", "750 KB")
        """
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
