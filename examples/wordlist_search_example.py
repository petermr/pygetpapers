#!/usr/bin/env python3
"""
Wordlist Search Example for Pygetpapers Datatables

This example demonstrates how to search datatables fields with a wordlist
and flag which papers have the highest hits.

AUTHOR: P. Murray-Rust with assistance from CursorAI (Claude Sonnet 4)
VERSION: 1.0.0
PURPOSE: Demonstrate wordlist search functionality for datatables fields
"""

import sys
from pathlib import Path

from pygetpapers.tools.datatables_integration import PygetpapersDatatables


def main():
    """Demonstrate wordlist search functionality."""
    print("=" * 60)
    print("           Pygetpapers Wordlist Search Example")
    print("=" * 60)
    print()

    # Initialize datatables
    datatables = PygetpapersDatatables()

    # Example output directory (you would replace this with your actual output)
    output_dir = "~/pygetpapers/europe_pmc_20241219_143022"

    print(f"📁 Reading output from: {output_dir}")

    try:
        # Read pygetpapers output
        output_data = datatables.read_pygetpapers_output(output_dir)

        if not output_data["paper_directories"]:
            print("❌ No papers found in the output directory.")
            print("   Please run a pygetpapers search first, for example:")
            print(
                "   pygetpapers --query 'climate change AND adaptation' --api europe_pmc --limit 10 -x -p --fulltext_html --datatables"
            )
            return

        print(f"✅ Found {len(output_data['paper_directories'])} papers")

        # Define climate change wordlist (following style guide)
        climate_wordlist = [
            "climate",
            "warming",
            "adaptation",
            "mitigation",
            "carbon",
            "emissions",
            "temperature",
            "greenhouse",
            "sustainability",
            "renewable",
        ]

        print(f"\n🔍 Searching for climate change terms: {', '.join(climate_wordlist)}")

        # Perform wordlist search
        search_results = datatables.search_datatables_fields(
            output_data=output_data,
            wordlist=climate_wordlist,
            search_fields=["Title", "Authors", "Abstract", "Keywords", "Journal"],
            case_sensitive=False,
            min_hits=1,
        )

        # Display summary
        summary = search_results["summary"]
        print(f"\n📊 Search Summary:")
        print(f"   Total papers: {summary['total_papers']}")
        print(f"   Flagged papers: {summary['flagged_papers']}")
        print(f"   Flag rate: {summary['flag_rate']:.1%}")
        print(f"   Total hits: {summary['total_hits']}")

        print(f"\n🏆 Most hit fields: {', '.join(summary['most_hit_fields'][:3])}")
        print(f"🏆 Most hit words: {', '.join(summary['most_hit_words'][:3])}")

        # Create and save tables
        print(f"\n📋 Creating search result tables...")

        # Create wordlist search table
        wordlist_table = datatables.create_wordlist_search_table(search_results)

        # Create field hit summary table
        field_summary_table = datatables.create_field_hit_summary_table(search_results)

        # Save to temp directory (following style guide)
        temp_dir = Path("temp")
        temp_dir.mkdir(exist_ok=True)

        # Save wordlist search results
        wordlist_file = temp_dir / "wordlist_search_results.html"
        with open(wordlist_file, "w", encoding="utf-8") as f:
            f.write(
                f"""
<!DOCTYPE html>
<html>
<head>
    <title>Wordlist Search Results - Climate Change Terms</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 30px; }}
        .summary {{ background-color: #e9ecef; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .table-section {{ margin-bottom: 30px; }}
        h2 {{ color: #495057; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Wordlist Search Results</h1>
        <p>Search terms: {', '.join(climate_wordlist)}</p>
        <p>Papers flagged: {summary['flagged_papers']} out of {summary['total_papers']} ({summary['flag_rate']:.1%})</p>
    </div>
    
    <div class="summary">
        <h3>Search Summary</h3>
        <p><strong>Total hits:</strong> {summary['total_hits']}</p>
        <p><strong>Most hit fields:</strong> {', '.join(summary['most_hit_fields'][:3])}</p>
        <p><strong>Most hit words:</strong> {', '.join(summary['most_hit_words'][:3])}</p>
    </div>
    
    <div class="table-section">
        <h2>Field Hit Summary</h2>
        {field_summary_table}
    </div>
    
    <div class="table-section">
        <h2>Flagged Papers (Sorted by Hit Count)</h2>
        {wordlist_table}
    </div>
</body>
</html>
            """
            )

        print(f"✅ Saved wordlist search results to: {wordlist_file}")
        print(
            f"\n🌐 Open the HTML file in your browser to view the interactive tables."
        )
        print(
            f"   The tables show which papers have the highest hits for climate change terms."
        )

        # Show top flagged papers
        if search_results["flagged_papers"]:
            print(f"\n📈 Top 5 flagged papers:")
            for i, paper_id in enumerate(search_results["flagged_papers"][:5], 1):
                paper_hits = search_results["paper_hits"][paper_id]
                print(f"   {i}. {paper_id} - {paper_hits['total_hits']} hits")

    except FileNotFoundError:
        print(f"❌ Output directory not found: {output_dir}")
        print("\n📋 To create sample data, run:")
        print(
            "   pygetpapers --query 'climate change AND adaptation' --api europe_pmc --limit 10 -x -p --fulltext_html --datatables"
        )
        print("   Then update the output_dir variable in this script.")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
