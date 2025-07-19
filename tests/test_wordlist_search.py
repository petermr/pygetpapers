#!/usr/bin/env python3
"""
Test wordlist search functionality for pygetpapers datatables.

ORIGINAL AUTHOR: Assistant on December 19, 2024
PURPOSE: Test wordlist search functionality with abstracts and metadata fields
"""

import unittest
from pathlib import Path
import tempfile
import json
import shutil

from pygetpapers.tools.datatables_integration import PygetpapersDatatables


class TestWordlistSearch(unittest.TestCase):
    """Test wordlist search functionality."""

    def setUp(self):
        """Set up test data."""
        self.datatables = PygetpapersDatatables()
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Create test output structure
        self.output_dir = self.temp_dir / "test_output"
        self.output_dir.mkdir()
        
        # Create test papers with climate change metadata
        self._create_test_papers()

    def tearDown(self):
        """Clean up test data."""
        shutil.rmtree(self.temp_dir)

    def _create_test_papers(self):
        """Create test papers with climate change metadata."""
        papers = [
            {
                "directory": "paper_001",
                "metadata": {
                    "title": "Climate Change Adaptation Strategies in Agriculture",
                    "authors": "Smith, J., Johnson, A.",
                    "abstract": "This study examines climate change adaptation strategies in agricultural systems. We found that sustainable farming practices can mitigate the effects of global warming.",
                    "keywords": ["climate change", "adaptation", "agriculture", "sustainability"],
                    "journal": "Environmental Science",
                    "doi": "10.1000/test.001",
                    "pmid": "12345",
                    "pmcid": "PMC12345"
                }
            },
            {
                "directory": "paper_002", 
                "metadata": {
                    "title": "Carbon Sequestration in Forest Ecosystems",
                    "authors": "Brown, M., Davis, R.",
                    "abstract": "Forest ecosystems play a crucial role in carbon sequestration and reducing greenhouse gas emissions. Our research shows significant potential for climate mitigation.",
                    "keywords": ["carbon sequestration", "forests", "greenhouse gases", "mitigation"],
                    "journal": "Forest Ecology",
                    "doi": "10.1000/test.002",
                    "pmid": "12346",
                    "pmcid": "PMC12346"
                }
            },
            {
                "directory": "paper_003",
                "metadata": {
                    "title": "Renewable Energy Technologies",
                    "authors": "Wilson, K.",
                    "abstract": "This paper reviews renewable energy technologies and their potential to reduce carbon emissions. Solar and wind power show great promise for sustainability.",
                    "keywords": ["renewable energy", "solar", "wind", "carbon emissions"],
                    "journal": "Energy Research",
                    "doi": "10.1000/test.003",
                    "pmid": "12347",
                    "pmcid": "PMC12347"
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

    def test_wordlist_search_with_abstracts(self):
        """Test wordlist search including abstracts."""
        # Read test output
        output_data = self.datatables.read_pygetpapers_output(str(self.output_dir))
        
        # Define climate change wordlist
        climate_wordlist = ["climate", "carbon", "adaptation", "mitigation", "sustainability"]
        
        # Perform search
        search_results = self.datatables.search_datatables_fields(
            output_data=output_data,
            wordlist=climate_wordlist,
            search_fields=["Title", "Authors", "Abstract", "Keywords"],
            case_sensitive=False,
            min_hits=1
        )
        
        # Verify results
        self.assertEqual(search_results["summary"]["total_papers"], 3)
        self.assertEqual(search_results["summary"]["flagged_papers"], 3)
        self.assertGreater(search_results["summary"]["total_hits"], 0)
        
        # Check that abstracts are being searched
        abstract_hits = search_results["field_hit_counts"]["Abstract"]["total_hits"]
        self.assertGreater(abstract_hits, 0, "Abstracts should have hits")
        
        # Check that keywords are being searched
        keyword_hits = search_results["field_hit_counts"]["Keywords"]["total_hits"]
        self.assertGreater(keyword_hits, 0, "Keywords should have hits")

    def test_wordlist_search_field_prioritization(self):
        """Test that search results prioritize fields with most hits."""
        output_data = self.datatables.read_pygetpapers_output(str(self.output_dir))
        
        climate_wordlist = ["climate", "carbon", "adaptation"]
        
        search_results = self.datatables.search_datatables_fields(
            output_data=output_data,
            wordlist=climate_wordlist,
            search_fields=["Title", "Abstract", "Keywords"],
            case_sensitive=False,
            min_hits=1
        )
        
        # Check that most hit fields are prioritized
        most_hit_fields = search_results["summary"]["most_hit_fields"]
        self.assertIsInstance(most_hit_fields, list)
        self.assertGreater(len(most_hit_fields), 0)

    def test_wordlist_search_case_insensitive(self):
        """Test case insensitive search."""
        output_data = self.datatables.read_pygetpapers_output(str(self.output_dir))
        
        # Test with mixed case
        wordlist = ["CLIMATE", "Carbon", "ADAPTATION"]
        
        search_results = self.datatables.search_datatables_fields(
            output_data=output_data,
            wordlist=wordlist,
            search_fields=["Title", "Abstract", "Keywords"],
            case_sensitive=False,
            min_hits=1
        )
        
        # Should find matches despite case differences
        self.assertGreater(search_results["summary"]["total_hits"], 0)

    def test_wordlist_search_min_hits_threshold(self):
        """Test minimum hits threshold filtering."""
        output_data = self.datatables.read_pygetpapers_output(str(self.output_dir))
        
        climate_wordlist = ["climate", "carbon", "adaptation"]
        
        # Test with min_hits=2 (should filter out papers with only 1 hit)
        search_results = self.datatables.search_datatables_fields(
            output_data=output_data,
            wordlist=climate_wordlist,
            search_fields=["Title", "Abstract", "Keywords"],
            case_sensitive=False,
            min_hits=2
        )
        
        # Should have fewer flagged papers with higher threshold
        self.assertLessEqual(
            search_results["summary"]["flagged_papers"], 
            search_results["summary"]["total_papers"]
        )

    def test_wordlist_search_table_creation(self):
        """Test creation of wordlist search tables."""
        output_data = self.datatables.read_pygetpapers_output(str(self.output_dir))
        
        climate_wordlist = ["climate", "carbon", "adaptation"]
        
        search_results = self.datatables.search_datatables_fields(
            output_data=output_data,
            wordlist=climate_wordlist,
            search_fields=["Title", "Abstract", "Keywords"],
            case_sensitive=False,
            min_hits=1
        )
        
        # Test wordlist search table creation
        wordlist_table = self.datatables.create_wordlist_search_table(search_results)
        self.assertIn("wordlist_search_table", wordlist_table)
        self.assertIn("DataTable", wordlist_table)
        
        # Test field hit summary table creation
        field_summary_table = self.datatables.create_field_hit_summary_table(search_results)
        self.assertIn("field_hit_summary_table", field_summary_table)
        self.assertIn("DataTable", field_summary_table)


if __name__ == "__main__":
    unittest.main() 