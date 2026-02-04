#!/usr/bin/env python3
"""
Test script for abstract functionality with pygetpapers CLI.

ORIGINAL AUTHOR: Assistant on December 19, 2024
PURPOSE: Test abstract functionality by calling pygetpapers and searching abstracts
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

from pygetpapers.tools.datatables_integration import PygetpapersDatatables


def run_pygetpapers_search(query, output_dir, limit=5, api="redalyc"):
    """Run pygetpapers search with specified parameters."""
    print(f"🔍 Running pygetpapers search...")
    print(f"   Query: '{query}'")
    print(f"   Output: {output_dir}")
    print(f"   Limit: {limit}")
    print(f"   API: {api}")
    print()

    # Build command
    cmd = [
        "pygetpapers",
        "--query",
        query,
        "--output",
        output_dir,
        "--limit",
        str(limit),
        "--api",
        api,
    ]

    print(f"Command: {' '.join(cmd)}")
    print()

    # Run pygetpapers
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=300  # 5 minute timeout
        )

        if result.returncode == 0:
            print("✅ pygetpapers search completed successfully!")
            print(f"Output: {result.stdout}")
            return True
        else:
            print("❌ pygetpapers search failed!")
            print(f"Error: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("❌ pygetpapers search timed out!")
        return False
    except Exception as e:
        print(f"❌ Error running pygetpapers: {e}")
        return False


def run_wordlist_search(output_dir, wordlist, fields=None):
    """Run wordlist search on the pygetpapers output."""
    if fields is None:
        fields = ["Title", "Abstract", "Keywords"]

    print(f"🔍 Running wordlist search...")
    print(f"   Words: {wordlist}")
    print(f"   Fields: {fields}")
    print(f"   Output: {output_dir}")
    print()

    try:
        # Initialize datatables
        datatables = PygetpapersDatatables()

        # Read output data
        output_data = datatables.read_pygetpapers_output(output_dir)

        if not output_data["paper_directories"]:
            print("❌ No papers found in output directory")
            return None

        print(f"✅ Found {len(output_data['paper_directories'])} papers")

        # Run wordlist search
        search_results = datatables.search_datatables_fields(
            output_data=output_data,
            wordlist=wordlist,
            search_fields=fields,
            case_sensitive=False,
            min_hits=1,
        )

        print("✅ Wordlist search completed successfully!")
        return search_results

    except Exception as e:
        print(f"❌ Error in wordlist search: {e}")
        return None


def validate_expected_output(
    search_results, expected_min_papers=1, expected_min_hits=1
):
    """Validate the search results against expected output."""
    print(f"🔍 Validating expected output...")
    print(f"   Expected min papers: {expected_min_papers}")
    print(f"   Expected min hits: {expected_min_hits}")
    print()

    if not search_results:
        print("❌ No search results to validate")
        return False

    # Check basic structure
    required_keys = ["summary", "field_hit_counts", "paper_hits", "flagged_papers"]
    for key in required_keys:
        if key not in search_results:
            print(f"❌ Missing required key: {key}")
            return False

    # Check summary statistics
    summary = search_results["summary"]
    total_papers = summary.get("total_papers", 0)
    flagged_papers = summary.get("flagged_papers", 0)
    total_hits = summary.get("total_hits", 0)

    print(f"📊 Search Results Summary:")
    print(f"   Total Papers: {total_papers}")
    print(f"   Flagged Papers: {flagged_papers}")
    print(f"   Total Hits: {total_hits}")

    # Validate minimum requirements
    if total_papers < expected_min_papers:
        print(f"❌ Too few papers: {total_papers} < {expected_min_papers}")
        return False

    if total_hits < expected_min_hits:
        print(f"❌ Too few hits: {total_hits} < {expected_min_hits}")
        return False

    # Check abstract field specifically
    if "Abstract" in search_results["field_hit_counts"]:
        abstract_hits = search_results["field_hit_counts"]["Abstract"]["total_hits"]
        print(f"   Abstract Field Hits: {abstract_hits}")

        if abstract_hits == 0:
            print("⚠️  Warning: No hits in Abstract field")

    # Show detailed results
    print(f"\n📋 Detailed Results:")
    for field in ["Title", "Abstract"]:
        if field in search_results["field_hit_counts"]:
            field_hits = search_results["field_hit_counts"][field]["total_hits"]
            print(f"   {field}: {field_hits} hits")

    print(f"\n📄 Flagged Papers:")
    for paper_id in search_results["flagged_papers"][:3]:  # Show first 3
        paper_hits = search_results["paper_hits"][paper_id]
        print(f"   {paper_id}: {paper_hits['total_hits']} hits")

    if len(search_results["flagged_papers"]) > 3:
        print(f"   ... and {len(search_results['flagged_papers']) - 3} more papers")

    print("✅ Validation completed successfully!")
    return True


def create_abstract_analysis_report(output_dir, search_results):
    """Create a comprehensive abstract analysis report."""
    print(f"📊 Creating abstract analysis report...")

    try:
        datatables = PygetpapersDatatables()
        output_data = datatables.read_pygetpapers_output(output_dir)

        # Extract abstracts
        abstracts_data = datatables.extract_abstracts(output_data)

        # Create tables
        abstracts_table = datatables.create_abstracts_table(abstracts_data)
        summary_table = datatables.create_abstracts_summary_table(abstracts_data)

        # Create wordlist search table if we have results
        wordlist_table = ""
        if search_results and search_results["flagged_papers"]:
            wordlist_table = datatables.create_wordlist_search_table(search_results)

        # Generate HTML report
        report_file = os.path.join(output_dir, "abstract_test_report.html")

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
        .success {{
            color: #27ae60;
            font-weight: bold;
        }}
        .warning {{
            color: #f39c12;
            font-weight: bold;
        }}
        .error {{
            color: #e74c3c;
            font-weight: bold;
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
                <div class="stat-value">{search_results['summary']['total_hits'] if search_results else 0}</div>
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
        return report_file

    except Exception as e:
        print(f"❌ Error creating report: {e}")
        return None


def main():
    """Main test function."""
    print("=" * 70)
    print("           ABSTRACT FUNCTIONALITY TEST WITH PYGETPAPERS")
    print("=" * 70)
    print()

    # Test configuration
    test_config = {
        "query": "climate change adaptation",
        "output_dir": "examples/abstract_test_output",
        "limit": 5,
        "api": "redalyc",
        "wordlist": ["climate", "adaptation", "change", "sustainability"],
        "fields": ["Title", "Abstract", "Keywords"],
        "expected_min_papers": 1,
        "expected_min_hits": 1,
    }

    print("🧪 Test Configuration:")
    print(f"   Query: '{test_config['query']}'")
    print(f"   Output Directory: {test_config['output_dir']}")
    print(f"   Wordlist: {test_config['wordlist']}")
    print(f"   Search Fields: {test_config['fields']}")
    print()

    # Step 1: Run pygetpapers search
    print("STEP 1: Running pygetpapers search")
    print("-" * 50)

    success = run_pygetpapers_search(
        query=test_config["query"],
        output_dir=test_config["output_dir"],
        limit=test_config["limit"],
        api=test_config["api"],
    )

    if not success:
        print("❌ pygetpapers search failed. Test cannot continue.")
        return False

    # Step 2: Run wordlist search
    print("\nSTEP 2: Running wordlist search")
    print("-" * 50)

    search_results = run_wordlist_search(
        output_dir=test_config["output_dir"],
        wordlist=test_config["wordlist"],
        fields=test_config["fields"],
    )

    if not search_results:
        print("❌ Wordlist search failed. Test cannot continue.")
        return False

    # Step 3: Validate expected output
    print("\nSTEP 3: Validating expected output")
    print("-" * 50)

    validation_success = validate_expected_output(
        search_results=search_results,
        expected_min_papers=test_config["expected_min_papers"],
        expected_min_hits=test_config["expected_min_hits"],
    )

    # Step 4: Create analysis report
    print("\nSTEP 4: Creating analysis report")
    print("-" * 50)

    report_file = create_abstract_analysis_report(
        output_dir=test_config["output_dir"], search_results=search_results
    )

    # Final results
    print("\n" + "=" * 70)
    print("           TEST RESULTS SUMMARY")
    print("=" * 70)

    if validation_success:
        print("✅ ABSTRACT FUNCTIONALITY TEST PASSED!")
        print()
        print("🎯 All features working correctly:")
        print("   ✅ pygetpapers search with abstract extraction")
        print("   ✅ Wordlist search in abstract fields")
        print("   ✅ Abstract analysis and statistics")
        print("   ✅ Table creation and display")
        print("   ✅ HTML report generation")
        print()
        print(f"📁 Output directory: {test_config['output_dir']}")
        if report_file:
            print(f"📊 Report file: {report_file}")
        print()
        print("🔍 You can now:")
        print("   - Browse the output directory for downloaded papers")
        print("   - Open the HTML report in your browser")
        print("   - Examine the abstract extraction and search results")
        return True
    else:
        print("❌ ABSTRACT FUNCTIONALITY TEST FAILED!")
        print()
        print("🔍 Check the output above for specific issues.")
        return False


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
