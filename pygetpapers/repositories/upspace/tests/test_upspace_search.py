"""
Real integration tests for UPSpace search functionality.

These tests use actual API calls to the UPSpace repository to validate
search functionality, metadata extraction, and SDG classification.
"""

import json
import logging
import os
import tempfile
import unittest
from pathlib import Path

from pygetpapers.repositories.upspace.upspace import UPSpace


class TestUPSpaceSearch(unittest.TestCase):
    def setUp(self):
        self.upspace = UPSpace()
        self.test_queries = ["sustainable development", "climate change"]
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def test_search_api_connectivity(self):
        """Test that we can connect to the UPSpace search API."""
        response = self.upspace._make_request(self.upspace.search_url, {"size": 1})
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("_embedded", data)
        self.assertIn("searchResult", data["_embedded"])

    def test_real_query_search(self):
        """Test search with real queries using the REST API."""
        for query in self.test_queries:
            with self.subTest(query=query):
                articles = self.upspace.search_articles(query, max_results=5)
                self.assertIsInstance(articles, list)
                self.assertGreater(len(articles), 0)

                # Check that articles have required fields
                for article in articles:
                    self.assertIn("title", article)
                    self.assertIn("uuid", article)
                    self.assertIsInstance(article["title"], str)
                    self.assertIsInstance(article["uuid"], str)

    def test_metadata_extraction(self):
        """Test that metadata is properly extracted from search results."""
        articles = self.upspace.search_articles("sustainable", max_results=3)
        self.assertGreater(len(articles), 0)

        for article in articles:
            # Check required fields
            self.assertIn("title", article)
            self.assertIn("authors", article)
            self.assertIn("uuid", article)

            # Check field types
            self.assertIsInstance(article["title"], str)
            self.assertIsInstance(article["authors"], list)
            self.assertIsInstance(article["uuid"], str)

            # Check that title is not empty
            self.assertGreater(len(article["title"]), 0)

    def test_sdg_classification_extraction(self):
        """Test that SDG classifications are properly extracted."""
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

    def test_article_id_generation(self):
        """Test that article IDs are generated correctly."""
        articles = self.upspace.search_articles("sustainable", max_results=3)
        self.assertGreater(len(articles), 0)

        for article in articles:
            article_id = self.upspace._generate_article_id(article)
            self.assertIsInstance(article_id, str)
            self.assertGreater(len(article_id), 0)

            # Check ID format
            self.assertTrue(
                article_id.startswith(("UPSPACE_", "DOI_", "UUID_", "TITLE_")),
                f"Invalid article ID format: {article_id}",
            )

    def test_search_pagination(self):
        """Test that search pagination works correctly."""
        # Get first page
        articles_page1 = self.upspace.search_articles("sustainable", max_results=3)
        self.assertEqual(len(articles_page1), 3)

        # Get second page (different results)
        articles_page2 = self.upspace.search_articles("sustainable", max_results=6)
        self.assertEqual(len(articles_page2), 6)

        # Check that we got more results
        self.assertGreater(len(articles_page2), len(articles_page1))

    def test_search_error_handling(self):
        """Test that search handles errors gracefully."""
        # Test with empty query
        articles = self.upspace.search_articles("", max_results=5)
        self.assertIsInstance(articles, list)

        # Test with very long query
        long_query = "a" * 1000
        articles = self.upspace.search_articles(long_query, max_results=5)
        self.assertIsInstance(articles, list)

    def test_rate_limiting(self):
        """Test that rate limiting works correctly."""
        import time

        start_time = time.time()

        # Make multiple requests quickly
        for i in range(3):
            articles = self.upspace.search_articles("sustainable", max_results=1)
            self.assertIsInstance(articles, list)

        end_time = time.time()

        # Should take at least 2 seconds due to rate limiting (1 second delay between requests)
        self.assertGreater(end_time - start_time, 2.0)


if __name__ == "__main__":
    unittest.main()
