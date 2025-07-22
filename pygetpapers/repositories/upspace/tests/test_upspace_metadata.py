"""
Real integration tests for UPSpace metadata extraction.

These tests use actual API responses to validate metadata extraction,
SDG classification parsing, and Dublin Core field mapping.
"""

import json
import logging
import re
import unittest
from pathlib import Path

from pygetpapers.repositories.upspace.upspace import UPSpace


class TestUPSpaceMetadata(unittest.TestCase):
    def setUp(self):
        self.upspace = UPSpace()
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def test_dublin_core_metadata_extraction(self):
        """Test that Dublin Core metadata is properly extracted."""
        articles = self.upspace.search_articles("sustainable", max_results=3)
        self.assertGreater(len(articles), 0)

        for article in articles:
            # Check required Dublin Core fields
            self.assertIn("title", article)
            self.assertIn("authors", article)
            self.assertIn("uuid", article)

            # Check field types
            self.assertIsInstance(article["title"], str)
            self.assertIsInstance(article["authors"], list)
            self.assertIsInstance(article["uuid"], str)

            # Check that required fields are not empty
            self.assertGreater(len(article["title"]), 0)
            self.assertGreater(len(article["uuid"]), 0)

    def test_sdg_classification_parsing(self):
        """Test that SDG classifications are parsed and validated correctly."""
        articles = self.upspace.search_articles("SDG", max_results=10)
        sdg_articles = [a for a in articles if a.get("sdg_classifications")]

        # At least some articles should have SDG classifications
        self.assertGreater(len(sdg_articles), 0)

        for article in sdg_articles:
            sdgs = article["sdg_classifications"]
            self.assertIsInstance(sdgs, list)

            for sdg in sdgs:
                self.assertIsInstance(sdg, str)
                # Check SDG format: "SDG-XX: Description"
                self.assertRegex(sdg, r"^SDG-\d+:")

                # Extract and validate SDG number
                match = re.search(r"SDG-(\d+)", sdg)
                if match:
                    sdg_num = int(match.group(1))
                    self.assertGreaterEqual(sdg_num, 1)
                    self.assertLessEqual(sdg_num, 17)

                    # Check that SDG name matches our mapping
                    expected_name = self.upspace.sdg_mappings.get(f"SDG-{sdg_num:02d}")
                    if expected_name:
                        # Use case-insensitive comparison
                        self.assertIn(expected_name.lower(), sdg.lower())

    def test_identifier_extraction(self):
        """Test that identifiers (Handle, DOI) are properly extracted."""
        articles = self.upspace.search_articles("sustainable", max_results=5)
        self.assertGreater(len(articles), 0)

        for article in articles:
            # Check Handle URL format
            if article.get("handle_url"):
                handle_url = article["handle_url"]
                self.assertIn("hdl.handle.net", handle_url)
                self.assertRegex(handle_url, r"http://hdl\.handle\.net/\d+/\d+")

                # Check Handle ID extraction
                if article.get("handle_id"):
                    handle_id = article["handle_id"]
                    self.assertRegex(handle_id, r"^\d+/\d+$")

            # Check DOI format
            if article.get("doi"):
                doi = article["doi"]
                self.assertRegex(doi, r"^10\.\d+/")
                self.assertGreater(len(doi), 10)  # DOI should be reasonably long

    def test_keywords_extraction(self):
        """Test that keywords/subjects are properly extracted."""
        articles = self.upspace.search_articles("sustainable", max_results=3)
        self.assertGreater(len(articles), 0)

        for article in articles:
            keywords = article.get("keywords", [])
            self.assertIsInstance(keywords, list)

            # Keywords should be strings
            for keyword in keywords:
                self.assertIsInstance(keyword, str)
                self.assertGreater(len(keyword), 0)

    def test_abstract_extraction(self):
        """Test that abstracts are properly extracted."""
        articles = self.upspace.search_articles("sustainable", max_results=3)
        self.assertGreater(len(articles), 0)

        for article in articles:
            abstract = article.get("abstract")
            if abstract:
                self.assertIsInstance(abstract, str)
                self.assertGreater(
                    len(abstract), 10
                )  # Abstract should be reasonably long

    def test_publisher_extraction(self):
        """Test that publisher information is properly extracted."""
        articles = self.upspace.search_articles("sustainable", max_results=3)
        self.assertGreater(len(articles), 0)

        for article in articles:
            publisher = article.get("publisher")
            if publisher:
                self.assertIsInstance(publisher, str)
                self.assertGreater(len(publisher), 0)

    def test_content_type_extraction(self):
        """Test that content type information is properly extracted."""
        articles = self.upspace.search_articles("sustainable", max_results=3)
        self.assertGreater(len(articles), 0)

        for article in articles:
            content_type = article.get("type")
            if content_type:
                self.assertIsInstance(content_type, str)
                self.assertGreater(len(content_type), 0)

    def test_metadata_completeness(self):
        """Test that metadata extraction is reasonably complete."""
        articles = self.upspace.search_articles("sustainable", max_results=5)
        self.assertGreater(len(articles), 0)

        required_fields = ["title", "uuid"]
        optional_fields = [
            "authors",
            "abstract",
            "year",
            "publisher",
            "keywords",
            "sdg_classifications",
        ]

        for article in articles:
            # Check required fields
            for field in required_fields:
                self.assertIn(field, article)
                self.assertIsNotNone(article[field])
                self.assertGreater(len(str(article[field])), 0)

            # Check that at least some optional fields are present
            present_optional_fields = sum(
                1 for field in optional_fields if article.get(field)
            )
            self.assertGreater(
                present_optional_fields,
                0,
                "Article should have at least some optional metadata",
            )

    def test_metadata_consistency(self):
        """Test that metadata is consistent across articles."""
        articles = self.upspace.search_articles("sustainable", max_results=3)
        self.assertGreater(len(articles), 0)

        # Check that all articles have the same basic structure
        first_article = articles[0]
        for article in articles[1:]:
            # Check that both articles have the same basic fields
            first_fields = set(first_article.keys())
            current_fields = set(article.keys())

            # Should have similar field sets
            common_fields = first_fields.intersection(current_fields)
            self.assertGreater(
                len(common_fields), 5
            )  # Should have at least 5 common fields

    def test_sdg_mapping_validation(self):
        """Test that SDG mappings are correct and complete."""
        # Check that all 17 SDGs are mapped
        self.assertEqual(len(self.upspace.sdg_mappings), 17)

        # Check that all SDG numbers are present
        for i in range(1, 18):
            sdg_key = f"SDG-{i:02d}"
            self.assertIn(sdg_key, self.upspace.sdg_mappings)

            # Check that mapping has a meaningful name
            sdg_name = self.upspace.sdg_mappings[sdg_key]
            self.assertIsInstance(sdg_name, str)
            self.assertGreater(len(sdg_name), 0)

    def test_year_extraction(self):
        """Test that year information is properly extracted."""
        articles = self.upspace.search_articles("sustainable", max_results=3)
        self.assertGreater(len(articles), 0)

        for article in articles:
            year = article.get("year")
            if year:
                self.assertIsInstance(year, str)
                # Year should be reasonable (between 1900 and current year + 1)
                try:
                    year_int = int(year)
                    self.assertGreaterEqual(year_int, 1900)
                    self.assertLessEqual(year_int, 2030)
                except ValueError:
                    # Year might be in format like "2024-09" or "2024"
                    self.assertRegex(year, r"^\d{4}(-\d{2})?$")

    def test_language_extraction(self):
        """Test that language information is properly extracted."""
        articles = self.upspace.search_articles("sustainable", max_results=3)
        self.assertGreater(len(articles), 0)

        for article in articles:
            language = article.get("language")
            if language:
                self.assertIsInstance(language, str)
                # Language should be a valid ISO code or reasonable value
                self.assertIn(language, ["en", "en_ZA", "en_US", "af", "zu"])


if __name__ == "__main__":
    unittest.main()
