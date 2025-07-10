"""
Data Transformer for Web Scraping Framework

This module provides data transformation capabilities for cleaning, normalizing,
and converting extracted data into the required format. It supports both
built-in transformations and custom transformation rules.
"""

import logging
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class DataTransformer:
    """
    Transform extracted data using configuration-based rules.

    Supports various transformation types:
    - Text cleaning and normalization
    - Date parsing and formatting
    - URL normalization
    - Data type conversion
    - Custom transformation functions
    """

    def __init__(self):
        """Initialize the data transformer with built-in transformations."""
        self.transformations = self._register_builtin_transformations()

    def _register_builtin_transformations(self) -> Dict[str, Callable]:
        """
        Register built-in transformation functions.

        Returns:
            Dictionary mapping transformation names to functions
        """
        return {
            # Text transformations
            "strip_whitespace": self._strip_whitespace,
            "remove_html_tags": self._remove_html_tags,
            "normalize_whitespace": self._normalize_whitespace,
            "remove_extra_spaces": self._remove_extra_spaces,
            "trim": self._trim,
            "lowercase": self._lowercase,
            "uppercase": self._uppercase,
            "capitalize": self._capitalize,
            "title_case": self._title_case,
            # Date transformations
            "parse_date": self._parse_date,
            "format_date": self._format_date,
            "extract_year": self._extract_year,
            "extract_month": self._extract_month,
            "extract_day": self._extract_day,
            # URL transformations
            "normalize_url": self._normalize_url,
            "extract_domain": self._extract_domain,
            "extract_path": self._extract_path,
            "normalize_doi": self._normalize_doi,
            # Data type transformations
            "to_int": self._to_int,
            "to_float": self._to_float,
            "to_bool": self._to_bool,
            "to_string": self._to_string,
            # Content transformations
            "extract_text": self._extract_text,
            "remove_special_chars": self._remove_special_chars,
            "normalize_unicode": self._normalize_unicode,
            "decode_html_entities": self._decode_html_entities,
            # List transformations
            "split_by_comma": self._split_by_comma,
            "split_by_semicolon": self._split_by_semicolon,
            "split_by_pipe": self._split_by_pipe,
            "join_list": self._join_list,
            "unique_items": self._unique_items,
            # Custom transformations
            "extract_first_name": self._extract_first_name,
            "extract_last_name": self._extract_last_name,
            "extract_initials": self._extract_initials,
            "normalize_author_name": self._normalize_author_name,
        }

    def transform_field(
        self,
        value: Any,
        transformations: List[str],
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Apply transformations to a field value.

        Args:
            value: Value to transform
            transformations: List of transformation names to apply
            params: Optional parameters for transformations

        Returns:
            Transformed value
        """
        if value is None:
            return None

        result = value

        for transform_name in transformations:
            try:
                if transform_name in self.transformations:
                    transform_func = self.transformations[transform_name]
                    result = transform_func(result, params or {})
                else:
                    logger.warning(f"Unknown transformation: {transform_name}")
            except Exception as e:
                logger.error(f"Error applying transformation '{transform_name}': {e}")
                continue

        return result

    def transform_data(
        self, data: Dict[str, Any], transformations_config: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """
        Transform multiple fields in a data dictionary.

        Args:
            data: Dictionary with field data
            transformations_config: Dictionary mapping field names to transformation lists

        Returns:
            Transformed data dictionary
        """
        transformed_data = {}

        for field_name, value in data.items():
            if field_name in transformations_config:
                transformations = transformations_config[field_name]
                transformed_value = self.transform_field(value, transformations)
                transformed_data[field_name] = transformed_value
            else:
                transformed_data[field_name] = value

        return transformed_data

    # Text transformations
    def _strip_whitespace(self, value: str, params: Dict[str, Any]) -> str:
        """Remove leading and trailing whitespace."""
        if isinstance(value, str):
            return value.strip()
        return value

    def _remove_html_tags(self, value: str, params: Dict[str, Any]) -> str:
        """Remove HTML tags from text."""
        if isinstance(value, str):
            # Simple HTML tag removal
            return re.sub(r"<[^>]+>", "", value)
        return value

    def _normalize_whitespace(self, value: str, params: Dict[str, Any]) -> str:
        """Normalize whitespace characters."""
        if isinstance(value, str):
            return re.sub(r"\s+", " ", value)
        return value

    def _remove_extra_spaces(self, value: str, params: Dict[str, Any]) -> str:
        """Remove extra spaces between words."""
        if isinstance(value, str):
            return " ".join(value.split())
        return value

    def _trim(self, value: str, params: Dict[str, Any]) -> str:
        """Trim whitespace from both ends."""
        if isinstance(value, str):
            return value.strip()
        return value

    def _lowercase(self, value: str, params: Dict[str, Any]) -> str:
        """Convert to lowercase."""
        if isinstance(value, str):
            return value.lower()
        return value

    def _uppercase(self, value: str, params: Dict[str, Any]) -> str:
        """Convert to uppercase."""
        if isinstance(value, str):
            return value.upper()
        return value

    def _capitalize(self, value: str, params: Dict[str, Any]) -> str:
        """Capitalize first letter."""
        if isinstance(value, str):
            return value.capitalize()
        return value

    def _title_case(self, value: str, params: Dict[str, Any]) -> str:
        """Convert to title case."""
        if isinstance(value, str):
            return value.title()
        return value

    # Date transformations
    def _parse_date(self, value: str, params: Dict[str, Any]) -> Optional[str]:
        """Parse date string to ISO format."""
        if not isinstance(value, str):
            return value

        # Common date formats
        date_formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%Y/%m/%d",
            "%d-%m-%Y",
            "%m-%d-%Y",
            "%B %d, %Y",
            "%d %B %Y",
            "%Y-%m-%d %H:%M:%S",
            "%d/%m/%Y %H:%M:%S",
        ]

        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(value.strip(), fmt)
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                continue

        # Try to extract year if full date parsing fails
        year_match = re.search(r"\b(19|20)\d{2}\b", value)
        if year_match:
            return f"{year_match.group()}-01-01"

        return value

    def _format_date(self, value: str, params: Dict[str, Any]) -> str:
        """Format date string."""
        if not isinstance(value, str):
            return value

        format_str = params.get("format", "%Y-%m-%d")
        try:
            parsed_date = datetime.strptime(value, "%Y-%m-%d")
            return parsed_date.strftime(format_str)
        except ValueError:
            return value

    def _extract_year(self, value: str, params: Dict[str, Any]) -> Optional[int]:
        """Extract year from date string."""
        if not isinstance(value, str):
            return value

        year_match = re.search(r"\b(19|20)\d{2}\b", value)
        if year_match:
            return int(year_match.group())
        return None

    def _extract_month(self, value: str, params: Dict[str, Any]) -> Optional[int]:
        """Extract month from date string."""
        if not isinstance(value, str):
            return value

        # Try to extract month number
        month_match = re.search(r"\b(0?[1-9]|1[0-2])\b", value)
        if month_match:
            return int(month_match.group())
        return None

    def _extract_day(self, value: str, params: Dict[str, Any]) -> Optional[int]:
        """Extract day from date string."""
        if not isinstance(value, str):
            return value

        # Try to extract day number
        day_match = re.search(r"\b(0?[1-9]|[12]\d|3[01])\b", value)
        if day_match:
            return int(day_match.group())
        return None

    # URL transformations
    def _normalize_url(self, value: str, params: Dict[str, Any]) -> str:
        """Normalize URL format."""
        if not isinstance(value, str):
            return value

        # Add protocol if missing
        if value.startswith("//"):
            value = "https:" + value
        elif not value.startswith(("http://", "https://")):
            value = "https://" + value

        return value

    def _extract_domain(self, value: str, params: Dict[str, Any]) -> str:
        """Extract domain from URL."""
        if not isinstance(value, str):
            return value

        import urllib.parse

        try:
            parsed = urllib.parse.urlparse(value)
            return parsed.netloc
        except Exception:
            return value

    def _extract_path(self, value: str, params: Dict[str, Any]) -> str:
        """Extract path from URL."""
        if not isinstance(value, str):
            return value

        import urllib.parse

        try:
            parsed = urllib.parse.urlparse(value)
            return parsed.path
        except Exception:
            return value

    def _normalize_doi(self, value: str, params: Dict[str, Any]) -> str:
        """Normalize DOI format."""
        if not isinstance(value, str):
            return value

        # Remove common prefixes
        doi = re.sub(r"^(doi:|https?://doi\.org/)", "", value.strip())

        # Ensure proper format
        if not doi.startswith("10."):
            return value

        return doi

    # Data type transformations
    def _to_int(self, value: Any, params: Dict[str, Any]) -> Optional[int]:
        """Convert to integer."""
        if value is None:
            return None

        try:
            if isinstance(value, str):
                # Extract numbers from string
                numbers = re.findall(r"-?\d+", value)
                if numbers:
                    return int(numbers[0])
            return int(value)
        except (ValueError, TypeError):
            return None

    def _to_float(self, value: Any, params: Dict[str, Any]) -> Optional[float]:
        """Convert to float."""
        if value is None:
            return None

        try:
            if isinstance(value, str):
                # Extract numbers from string
                numbers = re.findall(r"-?\d+\.?\d*", value)
                if numbers:
                    return float(numbers[0])
            return float(value)
        except (ValueError, TypeError):
            return None

    def _to_bool(self, value: Any, params: Dict[str, Any]) -> bool:
        """Convert to boolean."""
        if isinstance(value, bool):
            return value
        elif isinstance(value, str):
            return value.lower() in ("true", "yes", "1", "on")
        elif isinstance(value, (int, float)):
            return bool(value)
        return False

    def _to_string(self, value: Any, params: Dict[str, Any]) -> str:
        """Convert to string."""
        if value is None:
            return ""
        return str(value)

    # Content transformations
    def _extract_text(self, value: str, params: Dict[str, Any]) -> str:
        """Extract text content."""
        if not isinstance(value, str):
            return value

        # Remove HTML tags and entities
        text = re.sub(r"<[^>]+>", "", value)
        text = re.sub(r"&[a-zA-Z]+;", "", text)
        return text.strip()

    def _remove_special_chars(self, value: str, params: Dict[str, Any]) -> str:
        """Remove special characters."""
        if not isinstance(value, str):
            return value

        # Keep alphanumeric, spaces, and common punctuation
        return re.sub(r"[^\w\s.,!?-]", "", value)

    def _normalize_unicode(self, value: str, params: Dict[str, Any]) -> str:
        """Normalize Unicode characters."""
        if not isinstance(value, str):
            return value

        import unicodedata

        return unicodedata.normalize("NFKC", value)

    def _decode_html_entities(self, value: str, params: Dict[str, Any]) -> str:
        """Decode HTML entities."""
        if not isinstance(value, str):
            return value

        import html

        return html.unescape(value)

    # List transformations
    def _split_by_comma(self, value: str, params: Dict[str, Any]) -> List[str]:
        """Split string by comma."""
        if not isinstance(value, str):
            return [value] if value is not None else []

        return [item.strip() for item in value.split(",") if item.strip()]

    def _split_by_semicolon(self, value: str, params: Dict[str, Any]) -> List[str]:
        """Split string by semicolon."""
        if not isinstance(value, str):
            return [value] if value is not None else []

        return [item.strip() for item in value.split(";") if item.strip()]

    def _split_by_pipe(self, value: str, params: Dict[str, Any]) -> List[str]:
        """Split string by pipe."""
        if not isinstance(value, str):
            return [value] if value is not None else []

        return [item.strip() for item in value.split("|") if item.strip()]

    def _join_list(self, value: List[str], params: Dict[str, Any]) -> str:
        """Join list into string."""
        if not isinstance(value, list):
            return str(value)

        separator = params.get("separator", ", ")
        return separator.join(str(item) for item in value)

    def _unique_items(self, value: List[str], params: Dict[str, Any]) -> List[str]:
        """Remove duplicate items from list."""
        if not isinstance(value, list):
            return [value] if value is not None else []

        seen = set()
        unique_items = []
        for item in value:
            if item not in seen:
                seen.add(item)
                unique_items.append(item)
        return unique_items

    # Author name transformations
    def _extract_first_name(self, value: str, params: Dict[str, Any]) -> str:
        """Extract first name from author string."""
        if not isinstance(value, str):
            return value

        parts = value.split()
        return parts[0] if parts else value

    def _extract_last_name(self, value: str, params: Dict[str, Any]) -> str:
        """Extract last name from author string."""
        if not isinstance(value, str):
            return value

        parts = value.split()
        return parts[-1] if len(parts) > 1 else value

    def _extract_initials(self, value: str, params: Dict[str, Any]) -> str:
        """Extract initials from author string."""
        if not isinstance(value, str):
            return value

        parts = value.split()
        initials = []
        for part in parts:
            if part and part[0].isupper():
                initials.append(part[0])
        return ". ".join(initials) + "." if initials else value

    def _normalize_author_name(self, value: str, params: Dict[str, Any]) -> str:
        """Normalize author name format."""
        if not isinstance(value, str):
            return value

        # Remove extra spaces and normalize
        name = " ".join(value.split())

        # Handle "Last, First" format
        if "," in name:
            parts = name.split(",", 1)
            if len(parts) == 2:
                last_name = parts[0].strip()
                first_name = parts[1].strip()
                return f"{first_name} {last_name}"

        return name

    def register_custom_transformation(self, name: str, func: Callable):
        """
        Register a custom transformation function.

        Args:
            name: Name of the transformation
            func: Function to apply the transformation
        """
        self.transformations[name] = func
        logger.info(f"Registered custom transformation: {name}")

    def get_available_transformations(self) -> List[str]:
        """
        Get list of available transformation names.

        Returns:
            List of transformation names
        """
        return list(self.transformations.keys())

    def validate_transformations(self, transformations: List[str]) -> List[str]:
        """
        Validate transformation names and return invalid ones.

        Args:
            transformations: List of transformation names to validate

        Returns:
            List of invalid transformation names
        """
        invalid = []
        for transform in transformations:
            if transform not in self.transformations:
                invalid.append(transform)
        return invalid
