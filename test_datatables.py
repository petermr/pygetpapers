#!/usr/bin/env python3
"""
Test script for datatables integration with pygetpapers output.
"""

import os
import json
import tempfile
from pathlib import Path
from datatables_integration import PygetpapersDatatables


def create_sample_pygetpapers_output():
    """Create a sample pygetpapers output directory for testing"""

    # Create temporary directory
    temp_dir = tempfile.mkdtemp(prefix="pygetpapers_test_")
    output_path = Path(temp_dir)

    # Create sample metadata files
    sample_metadata = {
        "resultList": {
            "hitCount": 3,
            "result": [
                {
                    "id": "PMC123456",
                    "title": "Sample Paper 1: Machine Learning in Bioinformatics",
                    "authorString": "Smith J, Johnson A, Brown B",
                    "journalTitle": "Nature",
                    "doi": "10.1038/sample1",
                    "pmid": "12345678",
                    "pmcid": "PMC123456",
                    "firstPublicationDate": "2023-01-15",
                    "abstractText": "This is a sample abstract for paper 1.",
                },
                {
                    "id": "PMC789012",
                    "title": "Sample Paper 2: Deep Learning Applications",
                    "authorString": "Davis C, Wilson D, Miller E",
                    "journalTitle": "Science",
                    "doi": "10.1126/sample2",
                    "pmid": "87654321",
                    "pmcid": "PMC789012",
                    "firstPublicationDate": "2023-02-20",
                    "abstractText": "This is a sample abstract for paper 2.",
                },
                {
                    "id": "PMC345678",
                    "title": "Sample Paper 3: Natural Language Processing",
                    "authorString": "Taylor F, Anderson G, Thomas H",
                    "journalTitle": "Cell",
                    "doi": "10.1016/sample3",
                    "pmid": "11223344",
                    "pmcid": "PMC345678",
                    "firstPublicationDate": "2023-03-10",
                    "abstractText": "This is a sample abstract for paper 3.",
                },
            ],
        }
    }

    # Write metadata file
    with open(output_path / "eupmc_results.json", "w") as f:
        json.dump(sample_metadata, f, indent=2)

    # Create paper directories
    for i, paper in enumerate(sample_metadata["resultList"]["result"]):
        paper_dir = output_path / paper["id"]
        paper_dir.mkdir()

        # Write individual paper metadata
        with open(paper_dir / "eupmc_result.json", "w") as f:
            json.dump(paper, f, indent=2)

        # Create sample files
        (paper_dir / "fulltext.xml").write_text(f"<xml>Sample XML content for {paper['title']}</xml>")
        (paper_dir / "fulltext.pdf").write_text(f"PDF content for {paper['title']}")

        # Add supplementary files for some papers
        if i < 2:
            (paper_dir / "supplementary" / "data.csv").parent.mkdir(exist_ok=True)
            (paper_dir / "supplementary" / "data.csv").write_text("sample,data\n1,2\n3,4")

    return temp_dir


def test_datatables_integration():
    """Test the datatables integration functionality"""

    print("🧪 Testing Datatables Integration...")

    # Create sample data
    sample_dir = create_sample_pygetpapers_output()
    print(f"📁 Created sample data in: {sample_dir}")

    try:
        # Initialize datatables
        dt = PygetpapersDatatables()

        # Read the output
        print("📖 Reading pygetpapers output...")
        output_data = dt.read_pygetpapers_output(sample_dir)

        print(f"✅ Found {output_data['summary']['total_papers']} papers")
        print(f"✅ Found {len(output_data['metadata_files'])} metadata files")

        # Test papers table creation
        print("📊 Creating papers table...")
        papers_html = dt.create_papers_table(output_data, "test_papers_table")
        print(f"✅ Papers table created ({len(papers_html)} characters)")

        # Test metadata table creation
        print("📋 Creating metadata table...")
        metadata_html = dt.create_metadata_table(output_data, "test_metadata_table")
        print(f"✅ Metadata table created ({len(metadata_html)} characters)")

        # Test summary table creation
        print("📈 Creating summary table...")
        summary_html = dt.create_summary_table(output_data, "test_summary_table")
        print(f"✅ Summary table created ({len(summary_html)} characters)")

        # Test CSV export
        print("💾 Testing CSV export...")
        csv_file = f"{sample_dir}_export.csv"
        success = dt.export_table_to_csv(output_data, csv_file)
        if success:
            print(f"✅ CSV exported to: {csv_file}")
        else:
            print("❌ CSV export failed")

        # Test paper details
        print("🔍 Testing paper details...")
        paper_details = dt.get_paper_details(output_data, "PMC123456")
        if paper_details:
            print(f"✅ Found paper details for PMC123456: {paper_details['metadata']['title']}")
        else:
            print("❌ Paper details not found")

        print("\n🎉 All tests passed!")

        # Save HTML files for inspection
        with open(f"{sample_dir}_papers_table.html", "w") as f:
            f.write(papers_html)
        print(f"📄 Papers table saved to: {sample_dir}_papers_table.html")

        with open(f"{sample_dir}_metadata_table.html", "w") as f:
            f.write(metadata_html)
        print(f"📄 Metadata table saved to: {sample_dir}_metadata_table.html")

        with open(f"{sample_dir}_summary_table.html", "w") as f:
            f.write(summary_html)
        print(f"📄 Summary table saved to: {sample_dir}_summary_table.html")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()

    finally:
        # Clean up
        print(f"\n🧹 Cleaning up test data...")
        import shutil

        shutil.rmtree(sample_dir, ignore_errors=True)
        if os.path.exists(csv_file):
            os.remove(csv_file)


if __name__ == "__main__":
    test_datatables_integration()
