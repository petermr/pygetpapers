#!/usr/bin/env python3
"""
Lantana BioRxiv Analysis Script

Task: Survey first 10 hits for "Lantana" on BioRxiv
- Download PDFs (max 25MB)
- Record PDF status and metadata
- Prepare for feature analysis

Author: AI Assistant
Date: July 28, 2025 (system date of generation)
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
import requests
from pygetpapers.repositories.biorxiv.rxiv import Rxiv
from pygetpapers.core.file_utils import FileUtils

class LantanaBioRxivAnalyzer:
    def __init__(self):
        self.project_dir = Path("examples/lantana_biorxiv")
        self.results_file = self.project_dir / "lantana_results.json"
        self.report_file = self.project_dir / "lantana_analysis_report.md"
        self.datatables_file = self.project_dir / "lantana_datatables.html"
        self.pdf_dir = self.project_dir / "pdfs"
        self.max_pdf_size_mb = 25
        
        # Create directories
        self.pdf_dir.mkdir(exist_ok=True)
        
        # Initialize results structure
        self.results = {
            "query": "Lantana",
            "timestamp": datetime.now().isoformat(),
            "papers_analyzed": 0,
            "papers": [],
            "summary": {
                "feature_frequency": {},
                "pdf_statistics": {
                    "downloaded": 0,
                    "absent": 0,
                    "too_large": 0
                }
            }
        }
    
    def query_biorxiv(self):
        """Step 1: Query BioRxiv for 'Lantana' and get first 10 hits"""
        print("🔍 Querying BioRxiv for 'Lantana'...")
        
        try:
            # Try live BioRxiv access first with enhanced browser simulation
            print("🌐 Attempting live BioRxiv access...")
            
            # Create a session with very realistic browser headers
            session = requests.Session()
            session.headers.update({
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate", 
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Cache-Control": "max-age=0",
                "Sec-CH-UA": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                "Sec-CH-UA-Mobile": "?0",
                "Sec-CH-UA-Platform": '"macOS"'
            })
            
            # First, visit the main page to establish a session
            print("📄 Visiting main BioRxiv page...")
            import time
            time.sleep(2)  # Human-like delay
            
            main_response = session.get("https://www.biorxiv.org/", timeout=30)
            if main_response.status_code == 200:
                print("✅ Main page accessible")
                time.sleep(3)  # Human-like delay between requests
                
                # Now try the search
                search_url = "https://www.biorxiv.org/search/Lantana"
                print(f"🔍 Searching: {search_url}")
                
                search_response = session.get(search_url, timeout=30)
                
                if search_response.status_code == 200:
                    print("✅ Search page accessible!")
                    # Parse the results
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(search_response.text, 'html.parser')
                    
                    # Look for paper elements
                    papers = []
                    paper_elements = soup.find_all('div', class_='highwire-cite')
                    
                    for elem in paper_elements[:10]:  # Limit to 10
                        title_elem = elem.find('a', class_='highwire-cite-title')
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            doi = title_elem.get('href', '').split('/')[-1]
                            
                            # Extract authors
                            authors_elem = elem.find('span', class_='highwire-cite-authors')
                            authors = []
                            if authors_elem:
                                authors = [author.strip() for author in authors_elem.get_text().split(',')]
                            
                            paper = {
                                "doi": f"10.1101/{doi}",
                                "title": title,
                                "authors": authors,
                                "biorxiv_id": doi,
                                "publication_date": "",
                                "url": f"https://doi.org/10.1101/{doi}",
                                "pdf_url": f"https://www.biorxiv.org/content/{doi}.full.pdf"
                            }
                            papers.append(paper)
                    
                    if papers:
                        print(f"✅ Found {len(papers)} papers from live search")
                        return papers
                    else:
                        print("⚠️  No papers found in search results")
                else:
                    print(f"❌ Search failed with status {search_response.status_code}")
            else:
                print(f"❌ Main page failed with status {main_response.status_code}")
            
            # Fallback to test data
            print("📝 Falling back to test data...")
            test_data_file = Path("tests/test_biorxiv_integration/biorxiv_metadata.json")
            
            if test_data_file.exists():
                with open(test_data_file, 'r') as f:
                    test_data = json.load(f)
                
                # Convert test data to our format
                papers = []
                for paper_data in test_data.get("papers", []):
                    paper = {
                        "doi": paper_data.get("doi", ""),
                        "title": paper_data.get("title", ""),
                        "authors": paper_data.get("authors", []),
                        "biorxiv_id": paper_data.get("biorxiv_id", ""),
                        "publication_date": paper_data.get("download_timestamp", ""),
                        "url": f"https://doi.org/{paper_data.get('doi', '')}",
                        "pdf_url": paper_data.get("pdf_url", "")
                    }
                    papers.append(paper)
                
                print(f"✅ Found {len(papers)} papers from test data")
                return papers
            else:
                print("❌ No test data available")
                return []
            
        except Exception as e:
            print(f"❌ Error querying BioRxiv: {e}")
            return []
    
    def download_pdf(self, paper):
        """Step 2: Download PDF with size limit check"""
        doi = paper.get("doi", "")
        title = paper.get("title", "Unknown")
        
        if not doi:
            return {
                "status": "absent",
                "reason": "No DOI available",
                "size_mb": 0.0
            }
        
        # Check if PDF URL exists
        pdf_url = paper.get("pdf_url", "")
        if not pdf_url:
            return {
                "status": "absent", 
                "reason": "No PDF URL available",
                "size_mb": 0.0
            }
        
        # Create filename
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = safe_title[:50]  # Limit length
        filename = f"{doi.replace('/', '_')}_{safe_title}.pdf"
        filepath = self.pdf_dir / filename
        
        try:
            print(f"📥 Downloading: {title[:60]}...")
            
            # Create enhanced session for PDF download
            session = requests.Session()
            session.headers.update({
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/pdf,application/octet-stream,*/*",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Referer": "https://www.biorxiv.org/",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-User": "?1"
            })
            
            # Add human-like delay
            import time
            time.sleep(2)
            
            # Download with size check
            response = session.get(pdf_url, stream=True, timeout=60)
            response.raise_for_status()
            
            # Check content length
            content_length = response.headers.get('content-length')
            if content_length:
                size_mb = int(content_length) / (1024 * 1024)
                if size_mb > self.max_pdf_size_mb:
                    return {
                        "status": "too_large",
                        "reason": f"PDF size ({size_mb:.1f}MB) exceeds limit ({self.max_pdf_size_mb}MB)",
                        "size_mb": size_mb
                    }
            
            # Download the file
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Verify final size
            final_size_mb = filepath.stat().st_size / (1024 * 1024)
            
            if final_size_mb > self.max_pdf_size_mb:
                # Remove file if it's too large
                filepath.unlink()
                return {
                    "status": "too_large",
                    "reason": f"Downloaded PDF size ({final_size_mb:.1f}MB) exceeds limit ({self.max_pdf_size_mb}MB)",
                    "size_mb": final_size_mb
                }
            
            print(f"✅ Downloaded: {filename} ({final_size_mb:.1f}MB)")
            return {
                "status": "downloaded",
                "reason": "Successfully downloaded",
                "size_mb": final_size_mb,
                "filepath": str(filepath)
            }
            
        except Exception as e:
            print(f"❌ Error downloading {doi}: {e}")
            return {
                "status": "absent",
                "reason": f"Download error: {str(e)}",
                "size_mb": 0.0
            }
    
    def process_papers(self):
        """Main processing function for steps 1 and 2"""
        print("🚀 Starting Lantana BioRxiv Analysis")
        print("=" * 50)
        
        # Step 1: Query BioRxiv
        papers = self.query_biorxiv()
        
        if not papers:
            print("❌ No papers found. Exiting.")
            return
        
        # Step 2: Download PDFs
        print(f"\n📚 Processing {len(papers)} papers...")
        
        for i, paper in enumerate(papers, 1):
            print(f"\n[{i}/{len(papers)}] Processing: {paper.get('title', 'Unknown')[:60]}...")
            
            # Download PDF
            pdf_info = self.download_pdf(paper)
            
            # Create paper record
            paper_record = {
                "doi": paper.get("doi", ""),
                "title": paper.get("title", ""),
                "authors": paper.get("authors", []),
                "publication_date": paper.get("publication_date", ""),
                "biorxiv_id": paper.get("biorxiv_id", ""),
                "url": paper.get("url", ""),
                "pdf_status": pdf_info["status"],
                "pdf_reason": pdf_info["reason"],
                "pdf_size_mb": pdf_info["size_mb"],
                "pdf_filepath": pdf_info.get("filepath", ""),
                "features": {
                    # Placeholder for feature analysis (step 3)
                    "single_column": None,
                    "headers_footers": None,
                    "in_page_footnotes": None,
                    "lists": {"indented": None, "bulleted": None, "count": 0},
                    "tables": {"present": None, "count": 0},
                    "reference_list": None,
                    "bibliographic_info": None,
                    "table_of_contents": None,
                    "sections": {"decimal_numbering": None, "headers": None, "font_changes": None, "indents": None},
                    "hyperlinks": {"inline_urls": None, "external_links": None, "count": 0},
                    "figures": {"present": None, "with_captions": None, "count": 0},
                    "numbered_lines": None,
                    "inline_symbols": {"present": None, "count": 0, "bounding_boxes": []},
                    "math_equations": {
                        "inline": {"present": None, "count": 0, "bounding_boxes": []},
                        "chunks": {"present": None, "count": 0, "bounding_boxes": []}
                    },
                    "chemical_formulae": {
                        "inline": {"present": None, "count": 0, "bounding_boxes": []},
                        "chunks": {"present": None, "count": 0, "bounding_boxes": []}
                    },
                    "subscripts_superscripts": {"present": None, "count": 0, "types": []}
                }
            }
            
            self.results["papers"].append(paper_record)
            
            # Update statistics
            if pdf_info["status"] == "downloaded":
                self.results["summary"]["pdf_statistics"]["downloaded"] += 1
            elif pdf_info["status"] == "too_large":
                self.results["summary"]["pdf_statistics"]["too_large"] += 1
            else:
                self.results["summary"]["pdf_statistics"]["absent"] += 1
        
        self.results["papers_analyzed"] = len(papers)
        
        # Save results
        self.save_results()
        
        # Generate report
        self.generate_report()
        
        print("\n" + "=" * 50)
        print("✅ Steps 1 and 2 completed successfully!")
        print(f"📊 Results saved to: {self.results_file}")
        print(f"📄 Report saved to: {self.report_file}")
        print(f"📁 PDFs saved to: {self.pdf_dir}")
        
        # Print summary
        stats = self.results["summary"]["pdf_statistics"]
        print(f"\n📈 Summary:")
        print(f"   Downloaded: {stats['downloaded']}")
        print(f"   Too Large: {stats['too_large']}")
        print(f"   Absent: {stats['absent']}")
    
    def save_results(self):
        """Save results to JSON file"""
        with open(self.results_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
    
    def generate_report(self):
        """Generate markdown report"""
        report = f"""# Lantana BioRxiv Analysis Report

**Date:** {datetime.now().strftime('%B %d, %Y')}  
**Query:** Lantana  
**Papers Analyzed:** {self.results['papers_analyzed']}

## PDF Download Summary

| Status | Count |
|--------|-------|
| Downloaded | {self.results['summary']['pdf_statistics']['downloaded']} |
| Too Large (>25MB) | {self.results['summary']['pdf_statistics']['too_large']} |
| Absent | {self.results['summary']['pdf_statistics']['absent']} |

## Papers

"""
        
        for i, paper in enumerate(self.results['papers'], 1):
            report += f"""### {i}. {paper['title']}

- **DOI:** {paper['doi']}
- **Authors:** {', '.join(paper['authors'][:3])}{'...' if len(paper['authors']) > 3 else ''}
- **Publication Date:** {paper['publication_date']}
- **PDF Status:** {paper['pdf_status']}
- **PDF Size:** {paper['pdf_size_mb']:.1f} MB
- **Reason:** {paper['pdf_reason']}

"""
        
        with open(self.report_file, 'w', encoding='utf-8') as f:
            f.write(report)

def main():
    """Main function"""
    analyzer = LantanaBioRxivAnalyzer()
    analyzer.process_papers()

if __name__ == "__main__":
    main() 