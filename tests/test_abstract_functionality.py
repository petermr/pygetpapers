#!/usr/bin/env python3
"""
Test abstract functionality for pygetpapers datatables.

ORIGINAL AUTHOR: Assistant on December 19, 2024
PURPOSE: Test abstract extraction, processing, and table creation functionality
"""

import unittest
from pathlib import Path
import tempfile
import json
import shutil

from pygetpapers.tools.datatables_integration import PygetpapersDatatables


class TestAbstractFunctionality(unittest.TestCase):
    """Test abstract extraction and processing functionality."""

    def setUp(self):
        """Set up test data."""
        self.datatables = PygetpapersDatatables()
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Create test output structure
        self.output_dir = self.temp_dir / "test_output"
        self.output_dir.mkdir()
        
        # Create test papers with various abstract formats
        self._create_test_papers()

    def tearDown(self):
        """Clean up test data."""
        shutil.rmtree(self.temp_dir)

    def _create_test_papers(self):
        """Create test papers with various abstract formats."""
        papers = [
            {
                "directory": "paper_001",
                "metadata": {
                    "title": "Climate Change Adaptation Strategies",
                    "authors": "Smith, J., Johnson, A.",
                    "abstract": "This study examines climate change adaptation strategies in agricultural systems. We found that sustainable farming practices can mitigate the effects of global warming.",
                    "journal": "Environmental Science",
                    "doi": "10.1000/test.001"
                }
            },
            {
                "directory": "paper_002", 
                "metadata": {
                    "title": "Carbon Sequestration in Forests",
                    "authors": "Brown, M., Davis, R.",
                    "abstractText": "Forest ecosystems play a crucial role in carbon sequestration and reducing greenhouse gas emissions. Our research shows significant potential for climate mitigation.",
                    "journal": "Forest Ecology",
                    "doi": "10.1000/test.002"
                }
            },
            {
                "directory": "paper_003",
                "metadata": {
                    "title": "Renewable Energy Technologies",
                    "authors": "Wilson, K.",
                    "description": "This paper reviews renewable energy technologies and their potential to reduce carbon emissions. Solar and wind power show great promise for sustainability.",
                    "journal": "Energy Research",
                    "doi": "10.1000/test.003"
                }
            },
            {
                "directory": "paper_004",
                "metadata": {
                    "title": "Machine Learning Applications",
                    "authors": "Lee, S.",
                    "summary": "We present novel machine learning approaches for data analysis. The methods show improved accuracy and efficiency compared to traditional approaches.",
                    "journal": "Computer Science",
                    "doi": "10.1000/test.004"
                }
            },
            {
                "directory": "paper_005",
                "metadata": {
                    "title": "No Abstract Paper",
                    "authors": "Unknown, A.",
                    "journal": "Unknown Journal",
                    "doi": "10.1000/test.005"
                }
            },
            {
                "directory": "paper_006",
                "metadata": {
                    "title": "Europe PMC Format Paper",
                    "authors": "Europe, P.",
                    "abstractText": "This paper uses Europe PMC format with abstractText field. The content discusses biodiversity conservation.",
                    "journalInfo": {
                        "journal": {
                            "title": "Biodiversity Journal"
                        }
                    },
                    "doi": "10.1000/test.006"
                }
            },
            {
                "directory": "paper_007",
                "metadata": {
                    "title": "List Format Abstract",
                    "authors": "List, F.",
                    "abstract": [
                        "This abstract is in list format.",
                        "It has multiple paragraphs.",
                        "Each paragraph is a separate list item."
                    ],
                    "journal": "List Journal",
                    "doi": "10.1000/test.007"
                }
            }
        ]
        
        # Create paper directories and metadata files
        for paper in papers:
            paper_dir = self.output_dir / paper["directory"]
            paper_dir.mkdir()
            
            # Create metadata file
            metadata_file = paper_dir / "eupmc_result.json"
            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(paper["metadata"], f, indent=2)
            
            # Create dummy files
            (paper_dir / "fulltext.xml").touch()
            (paper_dir / "fulltext.pdf").touch()

    def test_extract_abstract_string_basic(self):
        """Test basic abstract extraction."""
        metadata = {
            "title": "Test Paper",
            "abstract": "This is a test abstract."
        }
        
        abstract = self.datatables._extract_abstract_string(metadata)
        self.assertEqual(abstract, "This is a test abstract.")

    def test_extract_abstract_string_abstracttext(self):
        """Test abstract extraction from abstractText field."""
        metadata = {
            "title": "Test Paper",
            "abstractText": "This is an abstractText abstract."
        }
        
        abstract = self.datatables._extract_abstract_string(metadata)
        self.assertEqual(abstract, "This is an abstractText abstract.")

    def test_extract_abstract_string_description(self):
        """Test abstract extraction from description field."""
        metadata = {
            "title": "Test Paper",
            "description": "This is a description abstract."
        }
        
        abstract = self.datatables._extract_abstract_string(metadata)
        self.assertEqual(abstract, "This is a description abstract.")

    def test_extract_abstract_string_summary(self):
        """Test abstract extraction from summary field."""
        metadata = {
            "title": "Test Paper",
            "summary": "This is a summary abstract."
        }
        
        abstract = self.datatables._extract_abstract_string(metadata)
        self.assertEqual(abstract, "This is a summary abstract.")

    def test_extract_abstract_string_list_format(self):
        """Test abstract extraction from list format."""
        metadata = {
            "title": "Test Paper",
            "abstract": [
                "First paragraph.",
                "Second paragraph.",
                "Third paragraph."
            ]
        }
        
        abstract = self.datatables._extract_abstract_string(metadata)
        self.assertEqual(abstract, "First paragraph. Second paragraph. Third paragraph.")

    def test_extract_abstract_string_empty(self):
        """Test abstract extraction with no abstract."""
        metadata = {
            "title": "Test Paper"
        }
        
        abstract = self.datatables._extract_abstract_string(metadata)
        self.assertEqual(abstract, "")

    def test_extract_abstract_string_whitespace(self):
        """Test abstract extraction with whitespace handling."""
        metadata = {
            "title": "Test Paper",
            "abstract": "  This abstract has whitespace.  "
        }
        
        abstract = self.datatables._extract_abstract_string(metadata)
        self.assertEqual(abstract, "This abstract has whitespace.")

    def test_extract_abstracts_comprehensive(self):
        """Test comprehensive abstract extraction from all papers."""
        output_data = self.datatables.read_pygetpapers_output(str(self.output_dir))
        
        abstracts_data = self.datatables.extract_abstracts(output_data)
        
        # Verify basic structure
        self.assertEqual(abstracts_data["total_papers"], 7)
        self.assertEqual(abstracts_data["papers_with_abstracts"], 6)
        self.assertEqual(abstracts_data["papers_without_abstracts"], 1)
        self.assertAlmostEqual(abstracts_data["abstract_coverage"], 6/7, places=2)
        
        # Verify specific papers
        self.assertTrue(abstracts_data["papers"]["paper_001"]["has_abstract"])
        self.assertEqual(abstracts_data["papers"]["paper_001"]["abstract_source"], "abstract")
        self.assertIn("climate change adaptation", abstracts_data["papers"]["paper_001"]["abstract"].lower())
        
        self.assertTrue(abstracts_data["papers"]["paper_002"]["has_abstract"])
        self.assertEqual(abstracts_data["papers"]["paper_002"]["abstract_source"], "abstractText")
        self.assertIn("carbon sequestration", abstracts_data["papers"]["paper_002"]["abstract"].lower())
        
        self.assertTrue(abstracts_data["papers"]["paper_003"]["has_abstract"])
        self.assertEqual(abstracts_data["papers"]["paper_003"]["abstract_source"], "description")
        self.assertIn("renewable energy", abstracts_data["papers"]["paper_003"]["abstract"].lower())
        
        self.assertTrue(abstracts_data["papers"]["paper_004"]["has_abstract"])
        self.assertEqual(abstracts_data["papers"]["paper_004"]["abstract_source"], "summary")
        self.assertIn("machine learning", abstracts_data["papers"]["paper_004"]["abstract"].lower())
        
        self.assertFalse(abstracts_data["papers"]["paper_005"]["has_abstract"])
        self.assertEqual(abstracts_data["papers"]["paper_005"]["abstract_source"], "none")
        self.assertEqual(abstracts_data["papers"]["paper_005"]["abstract"], "")
        
        # Verify list format abstract
        self.assertTrue(abstracts_data["papers"]["paper_007"]["has_abstract"])
        self.assertEqual(abstracts_data["papers"]["paper_007"]["abstract_source"], "abstract")
        self.assertIn("list format", abstracts_data["papers"]["paper_007"]["abstract"].lower())

    def test_create_abstracts_table(self):
        """Test creation of abstracts table."""
        output_data = self.datatables.read_pygetpapers_output(str(self.output_dir))
        abstracts_data = self.datatables.extract_abstracts(output_data)
        
        abstracts_table = self.datatables.create_abstracts_table(abstracts_data)
        
        # Verify table contains expected elements
        self.assertIn("abstracts_table", abstracts_table)
        self.assertIn("DataTable", abstracts_table)
        self.assertIn("paper_001", abstracts_table)
        self.assertIn("paper_002", abstracts_table)
        self.assertIn("Climate Change Adaptation", abstracts_table)
        self.assertIn("Carbon Sequestration", abstracts_table)

    def test_create_abstracts_summary_table(self):
        """Test creation of abstracts summary table."""
        output_data = self.datatables.read_pygetpapers_output(str(self.output_dir))
        abstracts_data = self.datatables.extract_abstracts(output_data)
        
        summary_table = self.datatables.create_abstracts_summary_table(abstracts_data)
        
        # Verify summary table contains expected elements
        self.assertIn("abstracts_summary_table", summary_table)
        self.assertIn("DataTable", summary_table)
        self.assertIn("Total Papers", summary_table)
        self.assertIn("Papers with Abstracts", summary_table)
        self.assertIn("Abstract Coverage", summary_table)
        self.assertIn("85.7%", summary_table)  # 6/7 papers have abstracts

    def test_abstract_length_calculation(self):
        """Test abstract length calculation."""
        output_data = self.datatables.read_pygetpapers_output(str(self.output_dir))
        abstracts_data = self.datatables.extract_abstracts(output_data)
        
        # Verify length calculations
        self.assertGreater(abstracts_data["papers"]["paper_001"]["abstract_length"], 0)
        self.assertGreater(abstracts_data["papers"]["paper_002"]["abstract_length"], 0)
        self.assertEqual(abstracts_data["papers"]["paper_005"]["abstract_length"], 0)
        
        # Verify average length calculation
        self.assertGreater(abstracts_data["average_abstract_length"], 0)
        self.assertIsInstance(abstracts_data["average_abstract_length"], (int, float))

    def test_abstract_source_tracking(self):
        """Test tracking of abstract sources."""
        output_data = self.datatables.read_pygetpapers_output(str(self.output_dir))
        abstracts_data = self.datatables.extract_abstracts(output_data)
        
        # Verify source tracking
        self.assertEqual(abstracts_data["papers"]["paper_001"]["abstract_source"], "abstract")
        self.assertEqual(abstracts_data["papers"]["paper_002"]["abstract_source"], "abstractText")
        self.assertEqual(abstracts_data["papers"]["paper_003"]["abstract_source"], "description")
        self.assertEqual(abstracts_data["papers"]["paper_004"]["abstract_source"], "summary")
        self.assertEqual(abstracts_data["papers"]["paper_005"]["abstract_source"], "none")

    def test_abstract_integration_with_papers_table(self):
        """Test that abstracts are properly integrated in papers table."""
        output_data = self.datatables.read_pygetpapers_output(str(self.output_dir))
        
        papers_table = self.datatables.create_papers_table(output_data)
        
        # Verify abstracts are included in papers table
        self.assertIn("Abstract", papers_table)
        self.assertIn("climate change adaptation", papers_table.lower())
        self.assertIn("carbon sequestration", papers_table.lower())
        self.assertIn("renewable energy", papers_table.lower())
        self.assertIn("machine learning", papers_table.lower())

    def test_abstract_integration_with_wordlist_search(self):
        """Test that abstracts are properly integrated in wordlist search."""
        output_data = self.datatables.read_pygetpapers_output(str(self.output_dir))
        
        # Test wordlist search including abstracts
        search_results = self.datatables.search_datatables_fields(
            output_data=output_data,
            wordlist=["climate", "carbon", "energy", "learning"],
            search_fields=["Title", "Abstract", "Keywords"],
            case_sensitive=False,
            min_hits=1
        )
        
        # Verify abstracts are being searched
        abstract_hits = search_results["field_hit_counts"]["Abstract"]["total_hits"]
        self.assertGreater(abstract_hits, 0, "Abstracts should have hits")
        
        # Verify specific words are found in abstracts
        self.assertGreater(search_results["field_hit_counts"]["Abstract"]["word_hits"]["climate"], 0)
        self.assertGreater(search_results["field_hit_counts"]["Abstract"]["word_hits"]["carbon"], 0)
        self.assertGreater(search_results["field_hit_counts"]["Abstract"]["word_hits"]["energy"], 0)
        self.assertGreater(search_results["field_hit_counts"]["Abstract"]["word_hits"]["learning"], 0)


if __name__ == "__main__":
    unittest.main() 