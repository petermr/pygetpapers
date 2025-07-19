#!/usr/bin/env python3
"""
Simple demo script for abstract functionality.

ORIGINAL AUTHOR: Assistant on December 19, 2024
PURPOSE: Demonstrate abstract extraction and analysis
"""

import sys
import tempfile
import json
from pathlib import Path

# Add the pygetpapers directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pygetpapers.tools.datatables_integration import PygetpapersDatatables


def create_sample_data():
    """Create sample paper data for demonstration."""
    papers = [
        {
            "directory": "climate_paper_001",
            "metadata": {
                "title": "Climate Change Adaptation in Agriculture",
                "authors": "Smith, J., Johnson, A.",
                "abstract": "This study examines climate change adaptation strategies in agricultural systems. We found that sustainable farming practices can mitigate the effects of global warming and improve crop resilience.",
                "journal": "Environmental Science",
                "doi": "10.1000/climate.001"
            }
        },
        {
            "directory": "carbon_paper_002", 
            "metadata": {
                "title": "Carbon Sequestration in Forest Ecosystems",
                "authors": "Brown, M., Davis, R.",
                "abstractText": "Forest ecosystems play a crucial role in carbon sequestration and reducing greenhouse gas emissions. Our research shows significant potential for climate mitigation through sustainable forest management.",
                "journal": "Forest Ecology",
                "doi": "10.1000/carbon.002"
            }
        },
        {
            "directory": "energy_paper_003",
            "metadata": {
                "title": "Renewable Energy Technologies for Sustainability",
                "authors": "Wilson, K.",
                "description": "This paper reviews renewable energy technologies and their potential to reduce carbon emissions. Solar and wind power show great promise for achieving sustainability goals.",
                "journal": "Energy Research",
                "doi": "10.1000/energy.003"
            }
        },
        {
            "directory": "no_abstract_paper_004",
            "metadata": {
                "title": "Paper Without Abstract",
                "authors": "Unknown, A.",
                "journal": "Unknown Journal",
                "doi": "10.1000/unknown.004"
            }
        }
    ]
    return papers


def main():
    """Run the abstract functionality demo."""
    print("=" * 60)
    print("           ABSTRACT FUNCTIONALITY DEMO")
    print("=" * 60)
    print()
    
    # Initialize datatables
    datatables = PygetpapersDatatables()
    
    # Create temporary directory with sample data
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        output_dir = temp_path / "demo_output"
        output_dir.mkdir()
        
        # Create sample papers
        papers = create_sample_data()
        print(f"📁 Creating {len(papers)} sample papers...")
        
        for paper in papers:
            paper_dir = output_dir / paper["directory"]
            paper_dir.mkdir()
            
            # Create metadata file
            metadata_file = paper_dir / "eupmc_result.json"
            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(paper["metadata"], f, indent=2)
            
            # Create dummy files
            (paper_dir / "fulltext.xml").touch()
            (paper_dir / "fulltext.pdf").touch()
        
        print("✅ Sample data created successfully!")
        print()
        
        # Read the output data
        print("🔍 Reading output data...")
        output_data = datatables.read_pygetpapers_output(str(output_dir))
        print(f"✅ Found {len(output_data['paper_directories'])} papers")
        print()
        
        # Extract abstracts
        print("📄 Extracting abstracts...")
        abstracts_data = datatables.extract_abstracts(output_data)
        
        # Display results
        print("\n📊 ABSTRACT ANALYSIS RESULTS:")
        print("-" * 50)
        print(f"Total Papers: {abstracts_data['total_papers']}")
        print(f"Papers with Abstracts: {abstracts_data['papers_with_abstracts']}")
        print(f"Papers without Abstracts: {abstracts_data['papers_without_abstracts']}")
        print(f"Abstract Coverage: {abstracts_data['abstract_coverage']:.1%}")
        print(f"Average Abstract Length: {abstracts_data['average_abstract_length']} characters")
        print()
        
        # Show abstract sources
        print("📋 ABSTRACT SOURCES:")
        print("-" * 50)
        source_counts = {}
        for paper_data in abstracts_data["papers"].values():
            source = paper_data["abstract_source"]
            source_counts[source] = source_counts.get(source, 0) + 1
        
        for source, count in sorted(source_counts.items()):
            print(f"{source}: {count} papers")
        print()
        
        # Show individual abstracts
        print("📄 INDIVIDUAL ABSTRACTS:")
        print("-" * 50)
        for paper_id, paper_data in abstracts_data["papers"].items():
            print(f"\n📑 {paper_data['title']}")
            print(f"   Authors: {paper_data['authors']}")
            print(f"   Journal: {paper_data['journal']}")
            print(f"   Source: {paper_data['abstract_source']}")
            print(f"   Length: {paper_data['abstract_length']} characters")
            if paper_data['has_abstract']:
                print(f"   Abstract: {paper_data['abstract'][:100]}...")
            else:
                print(f"   Abstract: No abstract available")
        
        # Test wordlist search
        print("\n🔍 WORDLIST SEARCH TEST:")
        print("-" * 50)
        climate_words = ["climate", "carbon", "energy", "sustainability"]
        
        search_results = datatables.search_datatables_fields(
            output_data=output_data,
            wordlist=climate_words,
            search_fields=["Title", "Abstract", "Keywords"],
            case_sensitive=False,
            min_hits=1
        )
        
        print(f"Search words: {climate_words}")
        print(f"Papers with matches: {search_results['summary']['flagged_papers']}")
        print(f"Total hits: {search_results['summary']['total_hits']}")
        
        # Show hits by field
        print("\nHits by field:")
        for field in ["Title", "Abstract"]:
            hits = search_results["field_hit_counts"][field]["total_hits"]
            print(f"  {field}: {hits} hits")
        
        # Show hits by word
        print("\nHits by word:")
        for word in climate_words:
            total_hits = sum(
                search_results["field_hit_counts"][field]["word_hits"][word]
                for field in ["Title", "Abstract"]
            )
            print(f"  '{word}': {total_hits} hits")
        
        # Create tables
        print("\n🔄 CREATING TABLES:")
        print("-" * 50)
        
        abstracts_table = datatables.create_abstracts_table(abstracts_data)
        summary_table = datatables.create_abstracts_summary_table(abstracts_data)
        
        print("✅ Abstracts table created")
        print("✅ Summary table created")
        print(f"📊 Tables contain {len(abstracts_data['papers'])} paper entries")
        
        # Save demo output
        demo_file = output_dir / "abstract_demo.html"
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Abstract Functionality Demo - Pygetpapers</title>
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
        <h1>📊 Abstract Functionality Demo</h1>
        
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
                <div class="stat-value">{abstracts_data['papers_without_abstracts']}</div>
                <div class="stat-label">Without Abstracts</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{abstracts_data['abstract_coverage']:.1%}</div>
                <div class="stat-label">Coverage</div>
            </div>
        </div>
        
        <h2>📋 Summary Statistics</h2>
        {summary_table}
        
        <h2>📄 Detailed Abstracts</h2>
        {abstracts_table}
    </div>
</body>
</html>
"""
        
        with open(demo_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Demo HTML saved to: {demo_file}")
        
        print("\n🎉 DEMO COMPLETE!")
        print("=" * 60)
        print("The abstract functionality is working correctly!")
        print("Features demonstrated:")
        print("✅ Abstract extraction from multiple formats")
        print("✅ Abstract analysis and statistics")
        print("✅ Wordlist search integration")
        print("✅ Table creation and display")
        print("✅ HTML report generation")


if __name__ == "__main__":
    main() 