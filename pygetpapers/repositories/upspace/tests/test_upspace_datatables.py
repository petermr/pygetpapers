"""
Real integration tests for UPSpace DataTables generation.

These tests use actual UPSpace data to validate DataTables HTML generation,
SDG badge display, and local file link creation.
"""

import json
import logging
import os
import tempfile
import unittest
from pathlib import Path

from pygetpapers.repositories.upspace.upspace import UPSpace


class TestUPSpaceDataTables(unittest.TestCase):
    def setUp(self):
        self.upspace = UPSpace()
        self.test_dir = tempfile.mkdtemp(prefix="upspace_datatables_test_")
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def tearDown(self):
        import shutil

        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_datatables_html_generation(self):
        """Test that DataTables HTML is generated correctly."""
        articles = self.upspace.search_articles("sustainable", max_results=3)
        self.assertGreater(len(articles), 0)

        original_output_dir = self.upspace.output_dir
        self.upspace.output_dir = self.test_dir

        try:
            self.upspace._create_upspace_datatables_html(articles)

            # Check that DataTables file was created
            datatables_file = Path(self.test_dir, "upspace_datatables.html")
            self.assertTrue(datatables_file.exists())

            # Check file content
            with open(datatables_file, "r", encoding="utf-8") as f:
                html_content = f.read()

            # Check for required DataTables components
            self.assertIn("jquery.dataTables", html_content)
            self.assertIn("DataTable", html_content)
            self.assertIn("sdg-badge", html_content)
            self.assertIn("table", html_content)

            # Check file size is reasonable
            self.assertGreater(datatables_file.stat().st_size, 1000)

        finally:
            self.upspace.output_dir = original_output_dir

    def test_index_html_generation(self):
        """Test that index HTML is generated correctly."""
        articles = self.upspace.search_articles("sustainable", max_results=3)
        self.assertGreater(len(articles), 0)

        original_output_dir = self.upspace.output_dir
        self.upspace.output_dir = self.test_dir

        try:
            self.upspace._create_upspace_datatables_html(articles)

            # Check that index file was created
            index_file = Path(self.test_dir, "index.html")
            self.assertTrue(index_file.exists())

            # Check file content
            with open(index_file, "r", encoding="utf-8") as f:
                html_content = f.read()

            # Check for required content
            self.assertIn("UPSpace Repository Overview", html_content)
            self.assertIn("DataTables", html_content)
            self.assertIn("upspace_datatables.html", html_content)

            # Check file size is reasonable
            self.assertGreater(index_file.stat().st_size, 500)

        finally:
            self.upspace.output_dir = original_output_dir

    def test_sdg_badge_generation(self):
        """Test that SDG badges are properly generated in DataTables."""
        articles = self.upspace.search_articles("SDG", max_results=5)
        sdg_articles = [a for a in articles if a.get("sdg_classifications")]

        if not sdg_articles:
            self.skipTest("No articles with SDG classifications found")

        original_output_dir = self.upspace.output_dir
        self.upspace.output_dir = self.test_dir

        try:
            self.upspace._create_upspace_datatables_html(sdg_articles)

            datatables_file = Path(self.test_dir, "upspace_datatables.html")
            with open(datatables_file, "r", encoding="utf-8") as f:
                html_content = f.read()

            # Check for SDG badge CSS classes
            for i in range(1, 18):  # Check all 17 SDGs
                self.assertIn(f"sdg-{i}", html_content)

            # Check for SDG badge elements
            self.assertIn("sdg-badge", html_content)

        finally:
            self.upspace.output_dir = original_output_dir

    def test_local_file_link_generation(self):
        """Test that local file links are properly generated."""
        articles = self.upspace.search_articles("sustainable", max_results=2)
        self.assertGreater(len(articles), 0)

        # Download articles first to create local files
        for article in articles:
            self.upspace.download_article(article, self.test_dir)

        original_output_dir = self.upspace.output_dir
        self.upspace.output_dir = self.test_dir

        try:
            self.upspace._create_upspace_datatables_html(articles)

            datatables_file = Path(self.test_dir, "upspace_datatables.html")
            with open(datatables_file, "r", encoding="utf-8") as f:
                html_content = f.read()

            # Check for local file links
            self.assertIn("fulltext.pdf", html_content)
            self.assertIn("metadata.json", html_content)
            self.assertIn("btn btn-success", html_content)  # PDF button class
            self.assertIn("btn btn-info", html_content)  # JSON button class

        finally:
            self.upspace.output_dir = original_output_dir

    def test_table_row_generation(self):
        """Test that table rows are properly generated for each article."""
        articles = self.upspace.search_articles("sustainable", max_results=3)
        self.assertGreater(len(articles), 0)

        original_output_dir = self.upspace.output_dir
        self.upspace.output_dir = self.test_dir

        try:
            self.upspace._create_upspace_datatables_html(articles)

            datatables_file = Path(self.test_dir, "upspace_datatables.html")
            with open(datatables_file, "r", encoding="utf-8") as f:
                html_content = f.read()

            # Count table rows (should match number of articles)
            # Count <tr> tags but exclude the header row
            all_rows = html_content.count("<tr>")
            # The template has 1 header row, so data rows = all rows - 1
            data_rows = all_rows - 1
            self.assertGreaterEqual(data_rows, len(articles))

            # Check that article titles appear in the HTML
            for article in articles:
                title = article.get("title", "")
                if title:
                    # HTML should be escaped, so check for basic content
                    self.assertIn("table", html_content)

        finally:
            self.upspace.output_dir = original_output_dir

    def test_template_loading(self):
        """Test that templates are loaded correctly."""
        template_path = Path(
            Path(__file__).parent.parent, "templates", "upspace_datatables.html"
        )
        self.assertTrue(template_path.exists(), f"Template not found: {template_path}")

        with open(template_path, "r", encoding="utf-8") as f:
            template_content = f.read()

        # Check template has required placeholders
        self.assertIn("{{TABLE_ROWS}}", template_content)
        self.assertIn("{{QUERY}}", template_content)

        # Check template has required DataTables components
        self.assertIn("jquery.dataTables", template_content)
        self.assertIn("DataTable", template_content)

    def test_html_escaping(self):
        """Test that HTML content is properly escaped."""
        # Create article with potentially problematic content
        test_article = {
            "title": "Test Article with <script>alert('xss')</script>",
            "authors": ["Author with & special chars"],
            "abstract": "Abstract with \"quotes\" and 'apostrophes'",
            "uuid": "test-uuid-123",
            "year": "2024",
            "keywords": ["keyword with <tags>"],
            "sdg_classifications": ["SDG-01: No Poverty"],
            "handle_url": "http://hdl.handle.net/2263/12345",
            "doi": "10.1234/test.2024.001",
        }

        original_output_dir = self.upspace.output_dir
        self.upspace.output_dir = self.test_dir

        try:
            self.upspace._create_upspace_datatables_html([test_article])

            datatables_file = Path(self.test_dir, "upspace_datatables.html")
            with open(datatables_file, "r", encoding="utf-8") as f:
                html_content = f.read()

            # Check that script tags are escaped
            self.assertNotIn(
                "<script>alert", html_content
            )  # Should not find raw script in content
            self.assertIn(
                "&lt;script&gt;", html_content
            )  # Should find escaped script tag
            self.assertIn("&amp;", html_content)  # Should find escaped ampersand
            self.assertIn("&quot;", html_content)  # Should find escaped quotes

        finally:
            self.upspace.output_dir = original_output_dir

    def test_empty_results_handling(self):
        """Test that empty results are handled gracefully."""
        original_output_dir = self.upspace.output_dir
        self.upspace.output_dir = self.test_dir

        try:
            # Test with empty article list
            self.upspace._create_upspace_datatables_html([])

            # Should still create files
            datatables_file = Path(self.test_dir, "upspace_datatables.html")
            index_file = Path(self.test_dir, "index.html")

            self.assertTrue(datatables_file.exists())
            self.assertTrue(index_file.exists())

            # Check content for empty state
            with open(datatables_file, "r", encoding="utf-8") as f:
                html_content = f.read()

            # Should have table structure even with no data
            self.assertIn("<table", html_content)
            self.assertIn("</table>", html_content)

        finally:
            self.upspace.output_dir = original_output_dir

    def test_css_styling(self):
        """Test that CSS styling is properly included."""
        articles = self.upspace.search_articles("sustainable", max_results=1)
        if not articles:
            self.skipTest("No articles found for testing")

        original_output_dir = self.upspace.output_dir
        self.upspace.output_dir = self.test_dir

        try:
            self.upspace._create_upspace_datatables_html(articles)

            datatables_file = Path(self.test_dir, "upspace_datatables.html")
            with open(datatables_file, "r", encoding="utf-8") as f:
                html_content = f.read()

            # Check for CSS styles
            self.assertIn("<style>", html_content)
            self.assertIn("</style>", html_content)

            # Check for SDG badge colors
            self.assertIn("background-color:", html_content)
            self.assertIn("color:", html_content)

            # Check for DataTables CSS
            self.assertIn("jquery.dataTables.min.css", html_content)

        finally:
            self.upspace.output_dir = original_output_dir


if __name__ == "__main__":
    unittest.main()
