#!/usr/bin/env python3
"""
Manual PDF Adder for Lantana Analysis

This script allows manual addition of PDFs when automated downloads fail.
Simply place PDFs in the pdfs/ directory and run this script to update the results.

Author: AI Assistant
Date: July 28, 2025 (system date of generation)
"""

import json
import os
from pathlib import Path

def add_manual_pdfs():
    """Add manually downloaded PDFs to the analysis results"""
    
    # Paths
    project_dir = Path("examples/lantana_biorxiv")
    results_file = project_dir / "lantana_results.json"
    pdf_dir = project_dir / "pdfs"
    
    if not results_file.exists():
        print("❌ No results file found. Run the main analysis first.")
        return
    
    # Load existing results
    with open(results_file, 'r') as f:
        results = json.load(f)
    
    print("📁 Checking for manually added PDFs...")
    
    # Check for PDFs in the directory
    pdf_files = list(pdf_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("❌ No PDF files found in pdfs/ directory")
        print("💡 To add PDFs manually:")
        print("   1. Download PDFs from BioRxiv manually")
        print("   2. Place them in examples/lantana_biorxiv/pdfs/")
        print("   3. Name them with the DOI (e.g., 10.1101_2023.11.10.566554.pdf)")
        print("   4. Run this script again")
        return
    
    print(f"✅ Found {len(pdf_files)} PDF files")
    
    # Update results for each PDF
    updated_count = 0
    for pdf_file in pdf_files:
        # Extract DOI from filename
        filename = pdf_file.stem  # Remove .pdf extension
        doi = filename.replace('_', '/', 1)  # Convert back to DOI format
        
        # Find matching paper in results
        for paper in results["papers"]:
            if paper["doi"] == doi:
                # Update paper with PDF info
                file_size_mb = pdf_file.stat().st_size / (1024 * 1024)
                
                paper["pdf_status"] = "downloaded"
                paper["pdf_reason"] = "Manually added"
                paper["pdf_size_mb"] = file_size_mb
                paper["pdf_filepath"] = str(pdf_file)
                
                print(f"✅ Updated: {doi} ({file_size_mb:.1f}MB)")
                updated_count += 1
                break
        else:
            print(f"⚠️  No matching paper found for: {filename}")
    
    # Update statistics
    if updated_count > 0:
        # Recalculate statistics
        stats = {"downloaded": 0, "absent": 0, "too_large": 0}
        for paper in results["papers"]:
            status = paper.get("pdf_status", "absent")
            stats[status] = stats.get(status, 0) + 1
        
        results["summary"]["pdf_statistics"] = stats
        
        # Save updated results
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Updated {updated_count} papers with PDF information")
        print(f"📊 New statistics:")
        print(f"   Downloaded: {stats['downloaded']}")
        print(f"   Absent: {stats['absent']}")
        print(f"   Too Large: {stats['too_large']}")
        
        # Generate updated report
        generate_updated_report(results)
    else:
        print("❌ No papers were updated")

def generate_updated_report(results):
    """Generate an updated markdown report"""
    from datetime import datetime
    
    report_file = Path("examples/lantana_biorxiv/lantana_analysis_report.md")
    
    report = f"""# Lantana BioRxiv Analysis Report (Updated)

**Date:** {datetime.now().strftime('%B %d, %Y')}  
**Query:** Lantana  
**Papers Analyzed:** {results['papers_analyzed']}

## PDF Download Summary

| Status | Count |
|--------|-------|
| Downloaded | {results['summary']['pdf_statistics']['downloaded']} |
| Too Large (>25MB) | {results['summary']['pdf_statistics']['too_large']} |
| Absent | {results['summary']['pdf_statistics']['absent']} |

## Papers

"""
    
    for i, paper in enumerate(results['papers'], 1):
        report += f"""### {i}. {paper['title']}

- **DOI:** {paper['doi']}
- **Authors:** {', '.join(paper['authors'][:3])}{'...' if len(paper['authors']) > 3 else ''}
- **Publication Date:** {paper['publication_date']}
- **PDF Status:** {paper['pdf_status']}
- **PDF Size:** {paper['pdf_size_mb']:.1f} MB
- **Reason:** {paper['pdf_reason']}

"""
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"📄 Updated report saved to: {report_file}")

if __name__ == "__main__":
    add_manual_pdfs() 