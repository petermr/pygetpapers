#!/usr/bin/env python3
"""
Create DataTables for Lantana BioRxiv Analysis - FINAL VERSION

Step 1: Generate DataTables with 10 papers (1 real + 9 realistic) and proper local paths
Step 2: Prepare directory structure for individual paper downloads

Author: AI Assistant
Date: July 28, 2025 (system date of generation)
"""

import json
import requests
import time
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup
import re

class LantanaDataTablesCreatorFinal:
    def __init__(self):
        self.project_dir = Path("examples/lantana_biorxiv")
        self.datatables_file = self.project_dir / "datatables.html"  # Correct filename
        self.papers_data_file = self.project_dir / "lantana_papers_data.json"
        
        # Create directories
        self.project_dir.mkdir(exist_ok=True)
        
    def get_papers_combined(self):
        """Get 1 real paper from test data + 9 realistic papers"""
        print("🔍 Loading papers: 1 real + 9 realistic...")
        
        papers = []
        
        # Get real paper from test data
        test_data_file = Path("tests/test_biorxiv_integration/biorxiv_metadata.json")
        
        if test_data_file.exists():
            with open(test_data_file, 'r') as f:
                test_data = json.load(f)
            
            for paper_data in test_data.get("papers", []):
                doi = paper_data.get("doi", "")
                if doi:
                    doi_id = doi.replace("10.1101/", "")
                    paper_id = doi_id.replace('.', '_').replace('-', '_')
                    
                    paper = {
                        "paper_id": paper_id,
                        "doi": doi,
                        "title": paper_data.get("title", ""),
                        "authors": paper_data.get("authors", []),
                        "publication_date": paper_data.get("download_timestamp", ""),
                        "paper_url": f"https://doi.org/{doi}",
                        "pdf_url": paper_data.get("pdf_url", ""),
                        "status": "not_downloaded",
                        "download_path": f"pdfs/{paper_id}/",
                        "local_pdf_path": f"file:///Users/pm286/workspace/pygetpapers/examples/lantana_biorxiv/pdfs/{paper_id}/fulltext.pdf",
                        "is_real": True
                    }
                    papers.append(paper)
                    print(f"✅ Added real paper: {doi}")
        
        # Add 9 realistic papers to get to 10 total
        realistic_papers = self.create_realistic_sample_papers()
        for paper in realistic_papers[:9]:  # Take first 9
            papers.append(paper)
            print(f"📝 Added realistic paper: {paper['doi']}")
        
        print(f"✅ Total papers: {len(papers)} (1 real + 9 realistic)")
        return papers
    
    def create_realistic_sample_papers(self):
        """Create realistic sample papers with proper local paths"""
        sample_papers = [
            {
                "paper_id": "2023_08_15_553123",
                "doi": "10.1101/2023.08.15.553123",
                "title": "Lantana camara invasion alters soil microbial communities and ecosystem functioning in tropical forests",
                "authors": ["Maria Rodriguez", "Carlos Silva", "Ana Martinez", "Roberto Fernandez"],
                "publication_date": "August 15, 2023",
                "paper_url": "https://doi.org/10.1101/2023.08.15.553123",
                "pdf_url": "https://www.biorxiv.org/content/10.1101/2023.08.15.553123.full.pdf",
                "status": "not_downloaded",
                "download_path": "pdfs/2023_08_15_553123/",
                "local_pdf_path": "file:///Users/pm286/workspace/pygetpapers/examples/lantana_biorxiv/pdfs/2023_08_15_553123/fulltext.pdf",
                "is_real": False
            },
            {
                "paper_id": "2023_07_22_550234",
                "doi": "10.1101/2023.07.22.550234",
                "title": "Chemical composition and biological activity of essential oils from Lantana species: A comprehensive analysis",
                "authors": ["John Smith", "Sarah Johnson", "Michael Brown", "Emily Davis"],
                "publication_date": "July 22, 2023",
                "paper_url": "https://doi.org/10.1101/2023.07.22.550234",
                "pdf_url": "https://www.biorxiv.org/content/10.1101/2023.07.22.550234.full.pdf",
                "status": "not_downloaded",
                "download_path": "pdfs/2023_07_22_550234/",
                "local_pdf_path": "file:///Users/pm286/workspace/pygetpapers/examples/lantana_biorxiv/pdfs/2023_07_22_550234/fulltext.pdf",
                "is_real": False
            },
            {
                "paper_id": "2023_06_18_545678",
                "doi": "10.1101/2023.06.18.545678",
                "title": "Impact of Lantana invasion on native plant diversity and ecosystem services in Mediterranean ecosystems",
                "authors": ["Emily Davis", "Robert Wilson", "Lisa Anderson", "David Thompson"],
                "publication_date": "June 18, 2023",
                "paper_url": "https://doi.org/10.1101/2023.06.18.545678",
                "pdf_url": "https://www.biorxiv.org/content/10.1101/2023.06.18.545678.full.pdf",
                "status": "not_downloaded",
                "download_path": "pdfs/2023_06_18_545678/",
                "local_pdf_path": "file:///Users/pm286/workspace/pygetpapers/examples/lantana_biorxiv/pdfs/2023_06_18_545678/fulltext.pdf",
                "is_real": False
            },
            {
                "paper_id": "2023_05_12_540987",
                "doi": "10.1101/2023.05.12.540987",
                "title": "Molecular mechanisms of Lantana camara adaptation to environmental stress: Insights from transcriptomic analysis",
                "authors": ["David Lee", "Jennifer Garcia", "Thomas Chen", "Amanda White"],
                "publication_date": "May 12, 2023",
                "paper_url": "https://doi.org/10.1101/2023.05.12.540987",
                "pdf_url": "https://www.biorxiv.org/content/10.1101/2023.05.12.540987.full.pdf",
                "status": "not_downloaded",
                "download_path": "pdfs/2023_05_12_540987/",
                "local_pdf_path": "file:///Users/pm286/workspace/pygetpapers/examples/lantana_biorxiv/pdfs/2023_05_12_540987/fulltext.pdf",
                "is_real": False
            },
            {
                "paper_id": "2023_04_08_536543",
                "doi": "10.1101/2023.04.08.536543",
                "title": "Ecological restoration strategies for Lantana-infested habitats: A systematic review",
                "authors": ["Amanda White", "Christopher Taylor", "Rachel Green", "Kevin Miller"],
                "publication_date": "April 8, 2023",
                "paper_url": "https://doi.org/10.1101/2023.04.08.536543",
                "pdf_url": "https://www.biorxiv.org/content/10.1101/2023.04.08.536543.full.pdf",
                "status": "not_downloaded",
                "download_path": "pdfs/2023_04_08_536543/",
                "local_pdf_path": "file:///Users/pm286/workspace/pygetpapers/examples/lantana_biorxiv/pdfs/2023_04_08_536543/fulltext.pdf",
                "is_real": False
            },
            {
                "paper_id": "2023_03_15_532109",
                "doi": "10.1101/2023.03.15.532109",
                "title": "Phylogenetic analysis of Lantana species using molecular markers: Implications for taxonomy and conservation",
                "authors": ["Kevin Miller", "Nicole Thompson", "Steven Clark", "Patricia Moore"],
                "publication_date": "March 15, 2023",
                "paper_url": "https://doi.org/10.1101/2023.03.15.532109",
                "pdf_url": "https://www.biorxiv.org/content/10.1101/2023.03.15.532109.full.pdf",
                "status": "not_downloaded",
                "download_path": "pdfs/2023_03_15_532109/",
                "local_pdf_path": "file:///Users/pm286/workspace/pygetpapers/examples/lantana_biorxiv/pdfs/2023_03_15_532109/fulltext.pdf",
                "is_real": False
            },
            {
                "paper_id": "2023_02_20_528765",
                "doi": "10.1101/2023.02.20.528765",
                "title": "Biological control agents for Lantana camara management: Current status and future prospects",
                "authors": ["Patricia Moore", "James Harris", "Michelle Lewis", "Brian Anderson"],
                "publication_date": "February 20, 2023",
                "paper_url": "https://doi.org/10.1101/2023.02.20.528765",
                "pdf_url": "https://www.biorxiv.org/content/10.1101/2023.02.20.528765.full.pdf",
                "status": "not_downloaded",
                "download_path": "pdfs/2023_02_20_528765/",
                "local_pdf_path": "file:///Users/pm286/workspace/pygetpapers/examples/lantana_biorxiv/pdfs/2023_02_20_528765/fulltext.pdf",
                "is_real": False
            },
            {
                "paper_id": "2023_01_25_525432",
                "doi": "10.1101/2023.01.25.525432",
                "title": "Climate change impacts on Lantana distribution and spread: A global perspective",
                "authors": ["Brian Anderson", "Stephanie Martin", "Daniel Wright", "Laura Johnson"],
                "publication_date": "January 25, 2023",
                "paper_url": "https://doi.org/10.1101/2023.01.25.525432",
                "pdf_url": "https://www.biorxiv.org/content/10.1101/2023.01.25.525432.full.pdf",
                "status": "not_downloaded",
                "download_path": "pdfs/2023_01_25_525432/",
                "local_pdf_path": "file:///Users/pm286/workspace/pygetpapers/examples/lantana_biorxiv/pdfs/2023_01_25_525432/fulltext.pdf",
                "is_real": False
            },
            {
                "paper_id": "2022_12_30_522198",
                "doi": "10.1101/2022.12.30.522198",
                "title": "Economic costs of Lantana invasion in agricultural systems: A comprehensive assessment",
                "authors": ["Laura Johnson", "Mark Davis", "Karen Wilson", "Richard Brown"],
                "publication_date": "December 30, 2022",
                "paper_url": "https://doi.org/10.1101/2022.12.30.522198",
                "pdf_url": "https://www.biorxiv.org/content/10.1101/2022.12.30.522198.full.pdf",
                "status": "not_downloaded",
                "download_path": "pdfs/2022_12_30_522198/",
                "local_pdf_path": "file:///Users/pm286/workspace/pygetpapers/examples/lantana_biorxiv/pdfs/2022_12_30_522198/fulltext.pdf",
                "is_real": False
            }
        ]
        return sample_papers
    
    def create_datatables_html(self, papers):
        """Create DataTables HTML with proper local file paths"""
        
        # Prepare data for DataTables
        table_data = []
        for paper in papers:
            authors_str = ", ".join(paper['authors'][:3]) + ("..." if len(paper['authors']) > 3 else "")
            
            # Create buttons with proper local paths
            view_button = f"<a href='{paper['paper_url']}' target='_blank' class='btn btn-sm btn-primary'>📄 View</a>"
            pdf_button = f"<a href='{paper['local_pdf_path']}' target='_blank' class='btn btn-sm btn-success'>📥 PDF</a>"
            
            # Add indicator for real vs realistic papers
            status_badge = f"<span class='badge badge-{'success' if paper.get('is_real', False) else 'secondary'}'>{'Real' if paper.get('is_real', False) else 'Sample'}</span>"
            
            table_data.append([
                f"<strong>{paper['title'][:80]}{'...' if len(paper['title']) > 80 else ''}</strong>",
                authors_str,
                paper['doi'],
                paper['publication_date'],
                view_button,
                pdf_button,
                status_badge,
                paper['download_path']
            ])
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lantana Papers - DataTables</title>
    
    <!-- DataTables CSS -->
    <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.13.7/css/jquery.dataTables.css">
    <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/responsive/2.5.0/css/responsive.dataTables.min.css">
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            padding: 20px;
            background: #f8f9fa;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .container {{
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        .btn-sm {{
            padding: 4px 8px;
            font-size: 0.875rem;
        }}
        .badge {{
            font-size: 0.75rem;
        }}
        .dataTables_wrapper {{
            margin-top: 20px;
        }}
        .download-info {{
            background: #e9ecef;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .file-path {{
            font-family: monospace;
            background: #f8f9fa;
            padding: 2px 4px;
            border-radius: 3px;
            font-size: 0.9em;
        }}
        .real-paper {{
            background-color: #d4edda !important;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🌿 Lantana Papers - DataTables</h1>
        <p><strong>Generated:</strong> {datetime.now().strftime('%B %d, %Y at %H:%M')}</p>
        <p><strong>Query:</strong> Lantana | <strong>Papers Found:</strong> {len(papers)} (1 Real + 9 Sample)</p>
        <p><strong>File:</strong> <span class="file-path">file:///Users/pm286/workspace/pygetpapers/examples/lantana_biorxiv/datatables.html</span></p>
    </div>
    
    <div class="container">
        <div class="download-info">
            <h4>📋 Download Instructions:</h4>
            <ol>
                <li><strong>Real Paper (Green badge):</strong> Click "View" to go to actual BioRxiv page and download PDF</li>
                <li><strong>Sample Papers (Gray badge):</strong> These are for demonstration - PDFs won't download from BioRxiv</li>
                <li>Save each PDF as <code>fulltext.pdf</code> in its designated directory</li>
                <li>Example: Save to <span class="file-path">examples/lantana_biorxiv/pdfs/2023_11_10_566554/fulltext.pdf</span></li>
                <li>After downloading PDFs, the "📥 PDF" buttons will work locally</li>
            </ol>
        </div>
        
        <table id="lantanaTable" class="display responsive nowrap" style="width:100%">
            <thead>
                <tr>
                    <th>Title</th>
                    <th>Authors</th>
                    <th>DOI</th>
                    <th>Date</th>
                    <th>Paper</th>
                    <th>PDF</th>
                    <th>Type</th>
                    <th>Directory</th>
                </tr>
            </thead>
            <tbody>
"""
        
        for i, row in enumerate(table_data):
            # Add special class for real papers
            row_class = "real-paper" if papers[i].get('is_real', False) else ""
            html_content += f"                <tr class='{row_class}'>\n"
            for cell in row:
                html_content += f"                    <td>{cell}</td>\n"
            html_content += "                </tr>\n"
        
        html_content += """            </tbody>
        </table>
    </div>
    
    <!-- jQuery -->
    <script type="text/javascript" src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
    
    <!-- DataTables JS -->
    <script type="text/javascript" src="https://cdn.datatables.net/1.13.7/js/jquery.dataTables.min.js"></script>
    <script type="text/javascript" src="https://cdn.datatables.net/responsive/2.5.0/js/dataTables.responsive.min.js"></script>
    
    <script>
        $(document).ready(function() {{
            $('#lantanaTable').DataTable({{
                responsive: true,
                pageLength: 10,
                order: [[3, 'desc']], // Sort by date descending
                columnDefs: [
                    {{ targets: [4, 5], orderable: false }}, // Disable sorting for action buttons
                    {{ targets: [7], visible: false }} // Hide directory column by default
                ],
                language: {{
                    search: "Search papers:",
                    lengthMenu: "Show _MENU_ papers per page",
                    info: "Showing _START_ to _END_ of _TOTAL_ papers"
                }}
            }});
        }});
    </script>
</body>
</html>
"""
        
        # Save HTML file
        with open(self.datatables_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"🌐 DataTables HTML saved to: {self.datatables_file}")
    
    def save_papers_data(self, papers):
        """Save papers data to JSON for later use"""
        data = {
            "query": "Lantana",
            "timestamp": datetime.now().isoformat(),
            "total_papers": len(papers),
            "real_papers": len([p for p in papers if p.get('is_real', False)]),
            "sample_papers": len([p for p in papers if not p.get('is_real', False)]),
            "papers": papers
        }
        
        with open(self.papers_data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Papers data saved to: {self.papers_data_file}")
    
    def create_directories(self, papers):
        """Create individual directories for each paper"""
        for paper in papers:
            paper_dir = self.project_dir / "pdfs" / paper['paper_id']
            paper_dir.mkdir(parents=True, exist_ok=True)
            print(f"📁 Created directory: {paper_dir}")
    
    def run(self):
        """Main execution function"""
        print("🚀 Creating FINAL DataTables for Lantana Papers")
        print("=" * 60)
        
        # Get papers (1 real + 9 realistic)
        papers = self.get_papers_combined()
        
        if not papers:
            print("❌ No papers found")
            return
        
        # Create DataTables HTML
        self.create_datatables_html(papers)
        
        # Save papers data
        self.save_papers_data(papers)
        
        # Create directories
        self.create_directories(papers)
        
        print("\n" + "=" * 60)
        print("✅ FINAL DataTables Created Successfully!")
        print("=" * 60)
        
        print(f"🌐 DataTables: {self.datatables_file}")
        print(f"📊 Papers data: {self.papers_data_file}")
        
        print(f"\n📋 Summary:")
        print(f"   Total papers: {len(papers)}")
        print(f"   Real papers: {len([p for p in papers if p.get('is_real', False)])}")
        print(f"   Sample papers: {len([p for p in papers if not p.get('is_real', False)])}")
        print(f"   Directories created: {len(papers)}")
        
        print(f"\n💡 Key Features:")
        print(f"   ✅ PDF links point to local file paths")
        print(f"   ✅ DataTables file is: datatables.html")
        print(f"   ✅ Each paper has its own directory")
        print(f"   ✅ Real BioRxiv paper highlighted in green")
        print(f"   ✅ Sample papers clearly marked")
        
        print(f"\n💡 Next Steps:")
        print(f"   1. Open the DataTables HTML file in your browser")
        print(f"   2. Download the REAL paper (green badge) from BioRxiv")
        print(f"   3. Save as 'fulltext.pdf' in the designated directory")
        print(f"   4. Proceed to Step 2 analysis")

def main():
    """Main function"""
    creator = LantanaDataTablesCreatorFinal()
    creator.run()

if __name__ == "__main__":
    main() 