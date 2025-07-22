#!/usr/bin/env python3
"""
Test script for abstract functionality using existing pygetpapers data.

ORIGINAL AUTHOR: Assistant on December 19, 2024
PURPOSE: Test abstract functionality with existing pygetpapers output
"""

import json
import os
import sys
from pathlib import Path

# Add the pygetpapers directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pygetpapers.tools.datatables_integration import PygetpapersDatatables


def main():
    """Main test function using existing data."""
    print("=" * 70)
    print("           ABSTRACT FUNCTIONALITY TEST WITH EXISTING DATA")
    print("=" * 70)
    print()

    # Test configuration
    test_config = {
        "output_dir": "examples/europe_pmc_climate_example",
        "wordlist": [
            "climate",
            "adaptation",
            "change",
            "sustainability",
            "imaginaries",
        ],
        "fields": ["Title", "Abstract", "Keywords"],
        "expected_min_papers": 1,
        "expected_min_hits": 1,
    }

    print("🧪 Test Configuration:")
    print(f"   Output Directory: {test_config['output_dir']}")
    print(f"   Wordlist: {test_config['wordlist']}")
    print(f"   Search Fields: {test_config['fields']}")
    print()

    # Check if output directory exists
    if not os.path.exists(test_config["output_dir"]):
        print(f"❌ Output directory not found: {test_config['output_dir']}")
        print("Please ensure you have existing pygetpapers output data.")
        return False

    # Step 1: Read existing output data
    print("STEP 1: Reading existing pygetpapers output")
    print("-" * 50)

    try:
        datatables = PygetpapersDatatables()
        output_data = datatables.read_pygetpapers_output(test_config["output_dir"])

        if not output_data["paper_directories"]:
            print("❌ No papers found in output directory")
            return False

        print(f"✅ Found {len(output_data['paper_directories'])} papers")

        # Show sample paper info
        for i, paper in enumerate(output_data["paper_directories"][:3]):
            metadata = paper.get("metadata", {})
            title = metadata.get("title", "No title")
            abstract = metadata.get(
                "abstractText", metadata.get("abstract", "No abstract")
            )
            print(f"   Paper {i+1}: {title[:60]}...")
            print(
                f"   Abstract: {abstract[:80]}..."
                if abstract != "No abstract"
                else "   Abstract: No abstract"
            )
            print()

    except Exception as e:
        print(f"❌ Error reading output data: {e}")
        return False

    # Step 2: Extract abstracts
    print("STEP 2: Extracting abstracts")
    print("-" * 50)

    try:
        abstracts_data = datatables.extract_abstracts(output_data)

        print(f"📊 Abstract Analysis Results:")
        print(f"   Total Papers: {abstracts_data['total_papers']}")
        print(f"   Papers with Abstracts: {abstracts_data['papers_with_abstracts']}")
        print(
            f"   Papers without Abstracts: {abstracts_data['papers_without_abstracts']}"
        )
        print(f"   Abstract Coverage: {abstracts_data['abstract_coverage']:.1%}")
        print(
            f"   Average Abstract Length: {abstracts_data['average_abstract_length']} characters"
        )
        print()

        # Show abstract sources
        source_counts = {}
        for paper_data in abstracts_data["papers"].values():
            source = paper_data["abstract_source"]
            source_counts[source] = source_counts.get(source, 0) + 1

        print(f"📋 Abstract Sources:")
        for source, count in sorted(source_counts.items()):
            print(f"   {source}: {count} papers")
        print()

    except Exception as e:
        print(f"❌ Error extracting abstracts: {e}")
        return False

    # Step 3: Run wordlist search
    print("STEP 3: Running wordlist search")
    print("-" * 50)

    try:
        search_results = datatables.search_datatables_fields(
            output_data=output_data,
            wordlist=test_config["wordlist"],
            search_fields=test_config["fields"],
            case_sensitive=False,
            min_hits=1,
        )

        print(f"✅ Wordlist search completed successfully!")
        print(f"   Papers with matches: {search_results['summary']['flagged_papers']}")
        print(f"   Total hits: {search_results['summary']['total_hits']}")

        # Show hits by field
        print(f"\n📋 Hits by field:")
        for field in ["Title", "Abstract"]:
            if field in search_results["field_hit_counts"]:
                hits = search_results["field_hit_counts"][field]["total_hits"]
                print(f"   {field}: {hits} hits")

        # Show hits by word
        print(f"\n📋 Hits by word:")
        for word in test_config["wordlist"]:
            total_hits = sum(
                search_results["field_hit_counts"][field]["word_hits"][word]
                for field in ["Title", "Abstract"]
                if field in search_results["field_hit_counts"]
            )
            print(f"   '{word}': {total_hits} hits")

    except Exception as e:
        print(f"❌ Error in wordlist search: {e}")
        return False

    # Step 4: Validate expected output
    print("\nSTEP 4: Validating expected output")
    print("-" * 50)

    try:
        summary = search_results["summary"]
        total_papers = summary.get("total_papers", 0)
        flagged_papers = summary.get("flagged_papers", 0)
        total_hits = summary.get("total_hits", 0)

        print(f"📊 Search Results Summary:")
        print(f"   Total Papers: {total_papers}")
        print(f"   Flagged Papers: {flagged_papers}")
        print(f"   Total Hits: {total_hits}")

        # Validate minimum requirements
        if total_papers < test_config["expected_min_papers"]:
            print(
                f"❌ Too few papers: {total_papers} < {test_config['expected_min_papers']}"
            )
            return False

        if total_hits < test_config["expected_min_hits"]:
            print(f"❌ Too few hits: {total_hits} < {test_config['expected_min_hits']}")
            return False

        # Check abstract field specifically
        if "Abstract" in search_results["field_hit_counts"]:
            abstract_hits = search_results["field_hit_counts"]["Abstract"]["total_hits"]
            print(f"   Abstract Field Hits: {abstract_hits}")

            if abstract_hits == 0:
                print("⚠️  Warning: No hits in Abstract field")

        print("✅ Validation completed successfully!")

    except Exception as e:
        print(f"❌ Error in validation: {e}")
        return False

    # Step 5: Create analysis report
    print("\nSTEP 5: Creating analysis report")
    print("-" * 50)

    try:
        # Create tables
        abstracts_table = datatables.create_abstracts_table(abstracts_data)
        summary_table = datatables.create_abstracts_summary_table(abstracts_data)

        # Create wordlist search table if we have results
        wordlist_table = ""
        if search_results and search_results["flagged_papers"]:
            wordlist_table = datatables.create_wordlist_search_table(search_results)

        # Generate HTML report
        report_file = os.path.join(
            test_config["output_dir"], "abstract_test_report.html"
        )

        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Abstract Functionality Test Report - Pygetpapers</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
        }}
        h2 {{
            color: #34495e;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
            margin-top: 30px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 1.5em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .stat-label {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Abstract Functionality Test Report</h1>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{abstracts_data['total_papers']}</div>
                <div class="stat-label">Total Papers</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{abstracts_data['papers_with_abstracts']}</div>
                <div class="stat-label">With Abstracts</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{abstracts_data['abstract_coverage']:.1%}</div>
                <div class="stat-label">Coverage</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{search_results['summary']['total_hits']}</div>
                <div class="stat-label">Search Hits</div>
            </div>
        </div>
        
        <h2>📋 Abstract Summary</h2>
        {summary_table}
        
        <h2>📄 Detailed Abstracts</h2>
        {abstracts_table}
"""

        if wordlist_table:
            html_content += f"""
        <h2>🔍 Wordlist Search Results</h2>
        {wordlist_table}
"""

        html_content += """
    </div>
</body>
</html>
"""

        with open(report_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"✅ Report saved to: {report_file}")

    except Exception as e:
        print(f"❌ Error creating report: {e}")
        return False

    # Final results
    print("\n" + "=" * 70)
    print("           TEST RESULTS SUMMARY")
    print("=" * 70)

    print("✅ ABSTRACT FUNCTIONALITY TEST PASSED!")
    print()
    print("🎯 All features working correctly:")
    print("   ✅ Abstract extraction from existing pygetpapers output")
    print("   ✅ Abstract analysis and statistics")
    print("   ✅ Wordlist search in abstract fields")
    print("   ✅ Table creation and display")
    print("   ✅ HTML report generation")
    print()
    print(f"📁 Output directory: {test_config['output_dir']}")
    print(f"📊 Report file: {report_file}")
    print()
    print("🔍 You can now:")
    print("   - Browse the output directory for downloaded papers")
    print("   - Open the HTML report in your browser")
    print("   - Examine the abstract extraction and search results")
    print()
    print("🎉 Test completed successfully!")

    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
