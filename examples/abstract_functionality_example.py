#!/usr/bin/env python3
"""
Example script demonstrating abstract functionality in pygetpapers datatables.

ORIGINAL AUTHOR: Assistant on December 19, 2024
PURPOSE: Demonstrate abstract extraction, analysis, and table creation
"""

import sys
import os
from pathlib import Path

# Add the pygetpapers directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pygetpapers.tools.datatables_integration import PygetpapersDatatables


def main():
    """Demonstrate abstract functionality."""
    print("=" * 60)
    print("           Abstract Functionality Demo")
    print("=" * 60)
    print()
    
    # Initialize datatables
    datatables = PygetpapersDatatables()
    
    # Example output directory (you can change this to your actual output)
    output_dir = "examples/redalyc_datatables_output"
    
    if not os.path.exists(output_dir):
        print(f"❌ Output directory not found: {output_dir}")
        print("Please run a pygetpapers search first to generate output data.")
        print("Example: pygetpapers --query 'climate change' --limit 10 --api redalyc")
        return
    
    print(f"📁 Reading output from: {output_dir}")
    
    try:
        # Read pygetpapers output
        output_data = datatables.read_pygetpapers_output(output_dir)
        
        if not output_data["paper_directories"]:
            print("❌ No papers found in output directory")
            return
        
        print(f"✅ Found {len(output_data['paper_directories'])} papers")
        print()
        
        # Extract abstracts
        print("🔍 Extracting abstracts...")
        abstracts_data = datatables.extract_abstracts(output_data)
        
        # Display summary
        print("\n📊 Abstract Analysis Summary:")
        print("-" * 40)
        print(f"Total Papers: {abstracts_data['total_papers']}")
        print(f"Papers with Abstracts: {abstracts_data['papers_with_abstracts']}")
        print(f"Papers without Abstracts: {abstracts_data['papers_without_abstracts']}")
        print(f"Abstract Coverage: {abstracts_data['abstract_coverage']:.1%}")
        print(f"Average Abstract Length: {abstracts_data['average_abstract_length']} characters")
        print()
        
        # Show abstract sources
        print("📋 Abstract Sources:")
        print("-" * 40)
        source_counts = {}
        for paper_data in abstracts_data["papers"].values():
            source = paper_data["abstract_source"]
            source_counts[source] = source_counts.get(source, 0) + 1
        
        for source, count in sorted(source_counts.items()):
            print(f"{source}: {count} papers")
        print()
        
        # Show sample abstracts
        print("📄 Sample Abstracts:")
        print("-" * 40)
        papers_with_abstracts = [
            (paper_id, paper_data) 
            for paper_id, paper_data in abstracts_data["papers"].items()
            if paper_data["has_abstract"]
        ]
        
        for i, (paper_id, paper_data) in enumerate(papers_with_abstracts[:3]):
            print(f"\nPaper {i+1}: {paper_data['title']}")
            print(f"Source: {paper_data['abstract_source']}")
            print(f"Length: {paper_data['abstract_length']} characters")
            abstract_preview = paper_data['abstract'][:150] + "..." if len(paper_data['abstract']) > 150 else paper_data['abstract']
            print(f"Abstract: {abstract_preview}")
        
        # Create abstracts table
        print("\n🔄 Creating abstracts table...")
        abstracts_table = datatables.create_abstracts_table(abstracts_data)
        
        # Create summary table
        print("🔄 Creating summary table...")
        summary_table = datatables.create_abstracts_summary_table(abstracts_data)
        
        # Save tables to output
        output_file = os.path.join(output_dir, "abstracts_analysis.html")
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Abstract Analysis - Pygetpapers</title>
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
        .summary-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .stat-label {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
            font-weight: bold;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        .abstract-cell {{
            max-width: 300px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Abstract Analysis Report</h1>
        
        <div class="summary-stats">
            <div class="stat-card">
                <div class="stat-value">{abstracts_data['total_papers']}</div>
                <div class="stat-label">Total Papers</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{abstracts_data['papers_with_abstracts']}</div>
                <div class="stat-label">With Abstracts</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{abstracts_data['papers_without_abstracts']}</div>
                <div class="stat-label">Without Abstracts</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{abstracts_data['abstract_coverage']:.1%}</div>
                <div class="stat-label">Coverage</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{abstracts_data['average_abstract_length']}</div>
                <div class="stat-label">Avg Length</div>
            </div>
        </div>
        
        <h2>📋 Abstract Sources</h2>
        <table>
            <tr>
                <th>Source Field</th>
                <th>Count</th>
                <th>Percentage</th>
            </tr>
"""
        
        for source, count in sorted(source_counts.items()):
            percentage = (count / abstracts_data['total_papers']) * 100
            html_content += f"""
            <tr>
                <td>{source}</td>
                <td>{count}</td>
                <td>{percentage:.1f}%</td>
            </tr>
"""
        
        html_content += """
        </table>
        
        <h2>📄 Abstracts Summary Table</h2>
"""
        html_content += summary_table
        
        html_content += """
        <h2>📊 Detailed Abstracts Table</h2>
"""
        html_content += abstracts_table
        
        html_content += """
    </div>
</body>
</html>
"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Abstract analysis saved to: {output_file}")
        print(f"📊 Analysis complete! Open {output_file} in your browser to view the results.")
        
        # Demonstrate wordlist search with abstracts
        print("\n🔍 Demonstrating wordlist search with abstracts...")
        climate_words = ["climate", "carbon", "adaptation", "mitigation", "sustainability"]
        
        search_results = datatables.search_datatables_fields(
            output_data=output_data,
            wordlist=climate_words,
            search_fields=["Title", "Abstract", "Keywords"],
            case_sensitive=False,
            min_hits=1
        )
        
        print(f"Found {search_results['summary']['flagged_papers']} papers with climate-related terms")
        print(f"Total hits: {search_results['summary']['total_hits']}")
        
        # Show abstract hits specifically
        abstract_hits = search_results["field_hit_counts"]["Abstract"]["total_hits"]
        print(f"Abstract field hits: {abstract_hits}")
        
        print("\n🎉 Abstract functionality demonstration complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 