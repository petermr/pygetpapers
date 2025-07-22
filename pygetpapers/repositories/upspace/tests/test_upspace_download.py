"""
Real integration tests for UPSpace download functionality.

These tests use actual API calls to download real files from UPSpace
to validate file download, bundle access, and bitstream handling.
"""

import json
import logging
import os
import tempfile
import unittest
from pathlib import Path

from pygetpapers.repositories.upspace.upspace import UPSpace


class TestUPSpaceDownload(unittest.TestCase):
    def setUp(self):
        self.upspace = UPSpace()
        self.test_dir = tempfile.mkdtemp(prefix="upspace_test_")
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def tearDown(self):
        import shutil

        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_pdf_download(self):
        """Test downloading PDF files from real articles."""
        articles = self.upspace.search_articles(
            "sustainable development", max_results=3
        )
        self.assertGreater(len(articles), 0)

        downloaded_count = 0
        for article in articles:
            success = self.upspace.download_article(article, self.test_dir)
            if success:
                downloaded_count += 1
                article_id = self.upspace._generate_article_id(article)
                pdf_file = Path(self.test_dir, article_id, "fulltext.pdf")

                # Check if PDF was downloaded
                if pdf_file.exists():
                    self.assertGreater(pdf_file.stat().st_size, 0)
                    # Verify it's a PDF file
                    with open(pdf_file, "rb") as f:
                        header = f.read(4)
                        self.assertEqual(header, b"%PDF", "File should be a valid PDF")

        # At least one article should be downloadable
        self.assertGreater(downloaded_count, 0)

    def test_metadata_file_creation(self):
        """Test that metadata files are created correctly."""
        articles = self.upspace.search_articles("sustainable", max_results=2)
        self.assertGreater(len(articles), 0)

        for article in articles:
            success = self.upspace.download_article(article, self.test_dir)
            self.assertTrue(success)

            article_id = self.upspace._generate_article_id(article)
            metadata_file = Path(self.test_dir, article_id, "metadata.json")

            # Check metadata file exists and is valid JSON
            self.assertTrue(metadata_file.exists())
            with open(metadata_file, "r", encoding="utf-8") as f:
                saved_metadata = json.load(f)

            # Check that metadata contains expected fields
            self.assertIn("title", saved_metadata)
            self.assertIn("uuid", saved_metadata)
            self.assertEqual(saved_metadata["title"], article["title"])

    def test_directory_structure(self):
        """Test that the correct directory structure is created."""
        articles = self.upspace.search_articles("sustainable", max_results=1)
        self.assertGreater(len(articles), 0)

        article = articles[0]
        success = self.upspace.download_article(article, self.test_dir)
        self.assertTrue(success)

        article_id = self.upspace._generate_article_id(article)
        article_dir = Path(self.test_dir, article_id)

        # Check directory exists
        self.assertTrue(article_dir.exists())
        self.assertTrue(article_dir.is_dir())

        # Check for expected files
        metadata_file = Path(article_dir, "metadata.json")
        self.assertTrue(metadata_file.exists())

        # PDF might or might not exist depending on availability
        pdf_file = Path(article_dir, "fulltext.pdf")
        if pdf_file.exists():
            self.assertTrue(pdf_file.is_file())

    def test_download_error_handling(self):
        """Test that download handles errors gracefully."""
        # Test with invalid article (missing UUID)
        invalid_article = {"title": "Test Article", "authors": ["Test Author"]}
        success = self.upspace.download_article(invalid_article, self.test_dir)
        self.assertFalse(success)

        # Test with invalid output directory
        articles = self.upspace.search_articles("sustainable", max_results=1)
        if articles:
            article = articles[0]
            # Try to download to a path that should be invalid but won't cause permission issues
            invalid_dir = "/dev/null"  # This is a device file, not a directory
            success = self.upspace.download_article(article, invalid_dir)
            # Should handle the error gracefully
            self.assertIsInstance(success, bool)

    def test_concurrent_downloads(self):
        """Test downloading multiple articles concurrently."""
        articles = self.upspace.search_articles("sustainable", max_results=3)
        self.assertGreater(len(articles), 0)

        import threading
        import time

        results = []
        errors = []

        def download_article_thread(article, index):
            try:
                success = self.upspace.download_article(article, self.test_dir)
                results.append((index, success))
            except Exception as e:
                errors.append((index, str(e)))

        # Start download threads
        threads = []
        for i, article in enumerate(articles):
            thread = threading.Thread(target=download_article_thread, args=(article, i))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Check results
        self.assertEqual(len(errors), 0, f"Download errors: {errors}")
        self.assertEqual(len(results), len(articles))

        # Check that files were created
        for i, (index, success) in enumerate(results):
            if success:
                article = articles[index]
                article_id = self.upspace._generate_article_id(article)
                metadata_file = Path(self.test_dir, article_id, "metadata.json")
                self.assertTrue(metadata_file.exists())

    def test_file_permissions(self):
        """Test that downloaded files have correct permissions."""
        articles = self.upspace.search_articles("sustainable", max_results=1)
        if not articles:
            self.skipTest("No articles found for testing")

        article = articles[0]
        success = self.upspace.download_article(article, self.test_dir)
        self.assertTrue(success)

        article_id = self.upspace._generate_article_id(article)
        article_dir = Path(self.test_dir, article_id)
        metadata_file = Path(article_dir, "metadata.json")

        # Check file permissions
        self.assertTrue(metadata_file.exists())
        self.assertTrue(os.access(metadata_file, os.R_OK))

        # Check directory permissions
        self.assertTrue(os.access(article_dir, os.R_OK))
        self.assertTrue(os.access(article_dir, os.W_OK))

    def test_bundle_and_bitstream_retrieval(self):
        """Test that bundle and bitstream retrieval works correctly."""
        articles = self.upspace.search_articles("sustainable", max_results=1)
        if not articles:
            self.skipTest("No articles found for testing")

        article = articles[0]
        uuid = article["uuid"]

        # Test bundle retrieval
        bundles_data = self.upspace._get_item_bundles(uuid)
        self.assertIsNotNone(bundles_data)
        self.assertIsInstance(bundles_data, dict)

        # Check bundles structure
        if "_embedded" in bundles_data and "bundles" in bundles_data["_embedded"]:
            bundles = bundles_data["_embedded"]["bundles"]
            self.assertIsInstance(bundles, list)

            # Test bitstream retrieval for ORIGINAL bundle
            for bundle in bundles:
                if isinstance(bundle, dict) and bundle.get("name") == "ORIGINAL":
                    bundle_uuid = bundle.get("uuid")
                    if bundle_uuid:
                        bitstreams_data = self.upspace._get_bundle_bitstreams(
                            bundle_uuid
                        )
                        self.assertIsNotNone(bitstreams_data)
                        self.assertIsInstance(bitstreams_data, dict)

                        # Check bitstreams structure
                        if (
                            "_embedded" in bitstreams_data
                            and "bitstreams" in bitstreams_data["_embedded"]
                        ):
                            bitstreams = bitstreams_data["_embedded"]["bitstreams"]
                            self.assertIsInstance(bitstreams, list)
                            break


if __name__ == "__main__":
    unittest.main()
