"""
Datatables Integration for Pygetpapers

This module provides functionality to read and display pygetpapers output
using the datatables module for interactive HTML tables.
"""

import json
import os
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import logging
from collections import OrderedDict
import re
import base64
import lxml.etree as ET
from datatables_module import Datatables, HtmlTable, DataTable

logger = logging.getLogger(__name__)


class PygetpapersDatatables:
    """
    Integration class for displaying pygetpapers output using datatables.
    """
    
    def __init__(self):
        self.supported_metadata_files = [
            "eupmc_results.json",
            "europe_pmc.csv", 
            "europe_pmc.html",
            "crossref_results.json",
            "arxiv_results.json",
            "openalex_results.json"
        ]
    
    def read_pygetpapers_output(self, output_dir: str) -> Dict[str, Any]:
        """
        Read pygetpapers output directory and extract metadata.
        
        Args:
            output_dir: Path to pygetpapers output directory
            
        Returns:
            Dictionary containing metadata and file information
        """
        output_path = Path(output_dir)
        if not output_path.exists():
            raise FileNotFoundError(f"Output directory not found: {output_dir}")
        
        result = {
            "output_dir": output_dir,
            "metadata_files": {},
            "paper_directories": [],
            "summary": {}
        }
        
        # Read metadata files
        for filename in self.supported_metadata_files:
            file_path = output_path / filename
            if file_path.exists():
                try:
                    if filename.endswith('.json'):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            result["metadata_files"][filename] = json.load(f)
                    elif filename.endswith('.csv'):
                        result["metadata_files"][filename] = pd.read_csv(file_path)
                    elif filename.endswith('.html'):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            result["metadata_files"][filename] = f.read()
                except Exception as e:
                    logger.warning(f"Error reading {filename}: {e}")
        
        # Scan for paper directories
        for item in output_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                paper_info = self._analyze_paper_directory(item)
                if paper_info:
                    result["paper_directories"].append(paper_info)
        
        # Create summary
        result["summary"] = {
            "total_papers": len(result["paper_directories"]),
            "metadata_files_found": list(result["metadata_files"].keys()),
            "has_xml": any("fulltext.xml" in str(p) for p in result["paper_directories"]),
            "has_pdf": any("fulltext.pdf" in str(p) for p in result["paper_directories"]),
            "has_supplementary": any("supplementary" in str(p) for p in result["paper_directories"])
        }
        
        return result
    
    def _analyze_paper_directory(self, paper_dir: Path) -> Optional[Dict[str, Any]]:
        """
        Analyze a single paper directory and extract information.
        
        Args:
            paper_dir: Path to paper directory
            
        Returns:
            Dictionary with paper information or None if not a valid paper directory
        """
        paper_info = {
            "directory": paper_dir.name,
            "path": str(paper_dir),
            "files": [],
            "metadata": {}
        }
        
        # Check for metadata files
        metadata_files = ["eupmc_result.json", "crossref_result.json", "arxiv_result.json"]
        for metadata_file in metadata_files:
            metadata_path = paper_dir / metadata_file
            if metadata_path.exists():
                try:
                    with open(metadata_path, 'r', encoding='utf-8') as f:
                        paper_info["metadata"] = json.load(f)
                    break
                except Exception as e:
                    logger.warning(f"Error reading metadata for {paper_dir.name}: {e}")
        
        # List all files
        for file_path in paper_dir.rglob("*"):
            if file_path.is_file():
                relative_path = file_path.relative_to(paper_dir)
                paper_info["files"].append(str(relative_path))
        
        return paper_info
    
    def create_papers_table(self, output_data: Dict[str, Any], table_id: str = "papers_table", 
                           include_checkboxes: bool = True, selectable_rows: bool = True) -> str:
        """
        Create an interactive HTML table from pygetpapers output.
        
        Args:
            output_data: Output from read_pygetpapers_output
            table_id: Unique ID for the table
            include_checkboxes: Whether to include checkboxes for selection
            selectable_rows: Whether to make rows selectable
            
        Returns:
            HTML string with interactive table
        """
        if not output_data["paper_directories"]:
            return "<p>No papers found in the output directory.</p>"
        
        # Prepare table data
        table_data = []
        for paper in output_data["paper_directories"]:
            metadata = paper.get("metadata", {})
            
            # Extract key information
            title = metadata.get("title", paper["directory"])
            authors = metadata.get("authorString", "Unknown")
            journal = metadata.get("journalTitle", "Unknown")
            doi = metadata.get("doi", "")
            pmid = metadata.get("pmid", "")
            pmcid = metadata.get("pmcid", "")
            pub_date = metadata.get("firstPublicationDate", "")
            
            # Check file availability
            has_xml = any("fulltext.xml" in f for f in paper["files"])
            has_pdf = any("fulltext.pdf" in f for f in paper["files"])
            has_supp = any("supplementary" in f for f in paper["files"])
            
            # Create hyperlinks
            doi_link = f"https://doi.org/{doi}" if doi else ""
            pmid_link = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else ""
            pmcid_link = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/" if pmcid else ""
            
            # Create row data with hyperlinks
            row = {
                "Select": f'<input type="checkbox" class="paper-checkbox" data-paper-id="{paper["directory"]}">' if include_checkboxes else "",
                "ID": paper["directory"],
                "Title": title[:100] + "..." if len(title) > 100 else title,
                "Authors": authors[:50] + "..." if len(authors) > 50 else authors,
                "Journal": journal,
                "DOI": f'<a href="{doi_link}" target="_blank">{doi}</a>' if doi_link else doi,
                "PMID": f'<a href="{pmid_link}" target="_blank">{pmid}</a>' if pmid_link else pmid,
                "PMCID": f'<a href="{pmcid_link}" target="_blank">{pmcid}</a>' if pmcid_link else pmcid,
                "Date": pub_date,
                "XML": "✅" if has_xml else "❌",
                "PDF": "✅" if has_pdf else "❌",
                "Suppl": "✅" if has_supp else "❌",
                "Files": len(paper["files"])
            }
            table_data.append(row)
        
        # Create HTML table using datatables
        try:
            htmlx, table = HtmlTable.create_html_table(
                dict_by_id=OrderedDict({row["ID"]: row for row in table_data}),
                datatables=True,
                table_id=table_id
            )
            
            # Convert to string
            html_string = ET.tostring(htmlx, encoding='unicode', pretty_print=True)
            return html_string
            
        except Exception as e:
            logger.error(f"Error creating datatable: {e}")
            # Fallback to simple HTML table
            return self._create_simple_table(table_data)
    
    def create_metadata_table(self, output_data: Dict[str, Any], table_id: str = "metadata_table") -> str:
        """
        Create a table showing metadata file information.
        
        Args:
            output_data: Output from read_pygetpapers_output
            table_id: Unique ID for the table
            
        Returns:
            HTML string with metadata table
        """
        if not output_data["metadata_files"]:
            return "<p>No metadata files found.</p>"
        
        # Prepare metadata table data
        metadata_data = []
        for filename, data in output_data["metadata_files"].items():
            if isinstance(data, dict):
                # JSON metadata
                if "resultList" in data:
                    # Europe PMC format
                    result_list = data["resultList"]
                    metadata_data.append({
                        "File": filename,
                        "Type": "JSON",
                        "Records": len(result_list.get("result", [])),
                        "Total Hits": result_list.get("hitCount", "Unknown"),
                        "Format": "Europe PMC"
                    })
                else:
                    # Other JSON format
                    metadata_data.append({
                        "File": filename,
                        "Type": "JSON",
                        "Records": len(data) if isinstance(data, list) else 1,
                        "Total Hits": "Unknown",
                        "Format": "Generic"
                    })
            elif isinstance(data, pd.DataFrame):
                # CSV metadata
                metadata_data.append({
                    "File": filename,
                    "Type": "CSV",
                    "Records": len(data),
                    "Total Hits": len(data),
                    "Format": "CSV"
                })
            else:
                # HTML or other format
                metadata_data.append({
                    "File": filename,
                    "Type": "HTML",
                    "Records": "Unknown",
                    "Total Hits": "Unknown",
                    "Format": "HTML"
                })
        
        # Create HTML table
        try:
            htmlx, table = HtmlTable.create_html_table(
                dict_by_id=OrderedDict({row["File"]: row for row in metadata_data}),
                datatables=True,
                table_id=table_id
            )
            
            html_string = ET.tostring(htmlx, encoding='unicode', pretty_print=True)
            return html_string
            
        except Exception as e:
            logger.error(f"Error creating metadata table: {e}")
            return self._create_simple_table(metadata_data)
    
    def create_summary_table(self, output_data: Dict[str, Any], table_id: str = "summary_table") -> str:
        """
        Create a summary table with corpus statistics.
        
        Args:
            output_data: Output from read_pygetpapers_output
            table_id: Unique ID for the table
            
        Returns:
            HTML string with summary table
        """
        summary = output_data["summary"]
        
        summary_data = [
            {
                "Metric": "Total Papers",
                "Value": summary["total_papers"],
                "Description": "Number of papers downloaded"
            },
            {
                "Metric": "Metadata Files",
                "Value": len(summary["metadata_files_found"]),
                "Description": "Number of metadata files found"
            },
            {
                "Metric": "XML Files",
                "Value": "✅" if summary["has_xml"] else "❌",
                "Description": "Full-text XML available"
            },
            {
                "Metric": "PDF Files", 
                "Value": "✅" if summary["has_pdf"] else "❌",
                "Description": "Full-text PDF available"
            },
            {
                "Metric": "Supplementary Files",
                "Value": "✅" if summary["has_supplementary"] else "❌", 
                "Description": "Supplementary materials available"
            }
        ]
        
        # Create HTML table
        try:
            htmlx, table = HtmlTable.create_html_table(
                dict_by_id=OrderedDict({row["Metric"]: row for row in summary_data}),
                datatables=True,
                table_id=table_id
            )
            
            html_string = ET.tostring(htmlx, encoding='unicode', pretty_print=True)
            return html_string
            
        except Exception as e:
            logger.error(f"Error creating summary table: {e}")
            return self._create_simple_table(summary_data)
    
    def _create_simple_table(self, data: List[Dict[str, Any]]) -> str:
        """
        Create a simple HTML table as fallback.
        
        Args:
            data: List of dictionaries with table data
            
        Returns:
            HTML string with simple table
        """
        if not data:
            return "<p>No data available.</p>"
        
        # Get column headers
        headers = list(data[0].keys())
        
        html = "<table border='1' style='border-collapse: collapse; width: 100%;'>"
        
        # Header row
        html += "<thead><tr>"
        for header in headers:
            html += f"<th style='padding: 8px; text-align: left;'>{header}</th>"
        html += "</tr></thead>"
        
        # Data rows
        html += "<tbody>"
        for row in data:
            html += "<tr>"
            for header in headers:
                value = str(row.get(header, ""))
                html += f"<td style='padding: 8px;'>{value}</td>"
            html += "</tr>"
        html += "</tbody>"
        
        html += "</table>"
        return html
    
    def export_table_to_csv(self, output_data: Dict[str, Any], output_file: str) -> bool:
        """
        Export papers data to CSV file.
        
        Args:
            output_data: Output from read_pygetpapers_output
            output_file: Path to output CSV file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not output_data["paper_directories"]:
                return False
            
            # Prepare data for CSV
            csv_data = []
            for paper in output_data["paper_directories"]:
                metadata = paper.get("metadata", {})
                
                row = {
                    "ID": paper["directory"],
                    "Title": metadata.get("title", ""),
                    "Authors": metadata.get("authorString", ""),
                    "Journal": metadata.get("journalTitle", ""),
                    "DOI": metadata.get("doi", ""),
                    "PMID": metadata.get("pmid", ""),
                    "PMCID": metadata.get("pmcid", ""),
                    "Publication_Date": metadata.get("firstPublicationDate", ""),
                    "Abstract": metadata.get("abstractText", ""),
                    "Keywords": metadata.get("keywordList", ""),
                    "Has_XML": any("fulltext.xml" in f for f in paper["files"]),
                    "Has_PDF": any("fulltext.pdf" in f for f in paper["files"]),
                    "Has_Supplementary": any("supplementary" in f for f in paper["files"]),
                    "File_Count": len(paper["files"])
                }
                csv_data.append(row)
            
            # Create DataFrame and save
            df = pd.DataFrame(csv_data)
            df.to_csv(output_file, index=False, encoding='utf-8')
            return True
            
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            return False
    
    def get_paper_details(self, output_data: Dict[str, Any], paper_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific paper.
        
        Args:
            output_data: Output from read_pygetpapers_output
            paper_id: ID of the paper to get details for
            
        Returns:
            Dictionary with paper details or None if not found
        """
        for paper in output_data["paper_directories"]:
            if paper["directory"] == paper_id:
                return paper
        return None
    
    def merge_corpora(self, corpora_data: List[Dict[str, Any]], merged_name: str = "merged_corpus") -> Dict[str, Any]:
        """
        Merge multiple corpora into a single dataset.
        
        Args:
            corpora_data: List of output data from multiple corpora
            merged_name: Name for the merged corpus
            
        Returns:
            Merged corpus data
        """
        merged_data = {
            "output_dir": merged_name,
            "metadata_files": {},
            "paper_directories": [],
            "summary": {}
        }
        
        # Merge paper directories
        seen_papers = set()
        for corpus_data in corpora_data:
            for paper in corpus_data["paper_directories"]:
                if paper["directory"] not in seen_papers:
                    merged_data["paper_directories"].append(paper)
                    seen_papers.add(paper["directory"])
        
        # Merge metadata files (keep unique ones)
        for corpus_data in corpora_data:
            for filename, data in corpus_data["metadata_files"].items():
                if filename not in merged_data["metadata_files"]:
                    merged_data["metadata_files"][filename] = data
        
        # Update summary
        merged_data["summary"] = {
            "total_papers": len(merged_data["paper_directories"]),
            "metadata_files_found": list(merged_data["metadata_files"].keys()),
            "has_xml": any("fulltext.xml" in str(p) for p in merged_data["paper_directories"]),
            "has_pdf": any("fulltext.pdf" in str(p) for p in merged_data["paper_directories"]),
            "has_supplementary": any("supplementary" in str(p) for p in merged_data["paper_directories"]),
            "source_corpora": len(corpora_data)
        }
        
        return merged_data
    
    def compare_corpora(self, corpora_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare multiple corpora and generate comparison statistics.
        
        Args:
            corpora_data: List of output data from multiple corpora
            
        Returns:
            Comparison data with statistics
        """
        comparison = {
            "corpora": [],
            "overlap_analysis": {},
            "summary_stats": {}
        }
        
        # Analyze each corpus
        for i, corpus_data in enumerate(corpora_data):
            corpus_info = {
                "name": corpus_data["output_dir"],
                "total_papers": corpus_data["summary"]["total_papers"],
                "has_xml": corpus_data["summary"]["has_xml"],
                "has_pdf": corpus_data["summary"]["has_pdf"],
                "has_supplementary": corpus_data["summary"]["has_supplementary"],
                "paper_ids": set(paper["directory"] for paper in corpus_data["paper_directories"])
            }
            comparison["corpora"].append(corpus_info)
        
        # Find overlaps
        if len(corpora_data) > 1:
            all_paper_ids = [corpus["paper_ids"] for corpus in comparison["corpora"]]
            common_papers = set.intersection(*all_paper_ids)
            
            comparison["overlap_analysis"] = {
                "common_papers": len(common_papers),
                "common_paper_ids": list(common_papers),
                "unique_papers_per_corpus": [len(corpus["paper_ids"] - common_papers) for corpus in comparison["corpora"]]
            }
        
        # Summary statistics
        total_papers = sum(corpus["total_papers"] for corpus in comparison["corpora"])
        comparison["summary_stats"] = {
            "total_corpora": len(corpora_data),
            "total_papers": total_papers,
            "average_papers_per_corpus": total_papers / len(corpora_data) if corpora_data else 0,
            "corpora_with_xml": sum(1 for corpus in comparison["corpora"] if corpus["has_xml"]),
            "corpora_with_pdf": sum(1 for corpus in comparison["corpora"] if corpus["has_pdf"]),
            "corpora_with_supplementary": sum(1 for corpus in comparison["corpora"] if corpus["has_supplementary"])
        }
        
        return comparison
    
    def search_fulltext(self, output_data: Dict[str, Any], search_terms: List[str], 
                       search_fields: List[str] = None, case_sensitive: bool = False) -> Dict[str, Any]:
        """
        Search within fulltext content of papers.
        
        Args:
            output_data: Output from read_pygetpapers_output
            search_terms: List of terms to search for
            search_fields: Fields to search in (xml, pdf, supplementary, metadata)
            case_sensitive: Whether search should be case sensitive
            
        Returns:
            Search results with matches and context
        """
        if search_fields is None:
            search_fields = ["xml", "metadata"]
        
        search_results = {
            "search_terms": search_terms,
            "search_fields": search_fields,
            "case_sensitive": case_sensitive,
            "matches": [],
            "summary": {}
        }
        
        total_matches = 0
        papers_with_matches = 0
        
        for paper in output_data["paper_directories"]:
            paper_matches = []
            paper_path = Path(paper["path"])
            
            # Search in XML files
            if "xml" in search_fields:
                xml_files = list(paper_path.glob("*.xml"))
                for xml_file in xml_files:
                    try:
                        with open(xml_file, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            matches = self._search_in_content(content, search_terms, case_sensitive, "XML")
                            for match in matches:
                                match["file"] = str(xml_file.relative_to(paper_path))
                                match["paper_id"] = paper["directory"]
                                paper_matches.append(match)
                    except Exception as e:
                        logger.warning(f"Error reading XML file {xml_file}: {e}")
            
            # Search in PDF files (basic text extraction)
            if "pdf" in search_fields:
                pdf_files = list(paper_path.glob("*.pdf"))
                for pdf_file in pdf_files:
                    try:
                        # Basic PDF text extraction (could be enhanced with PyPDF2 or similar)
                        content = self._extract_pdf_text(pdf_file)
                        if content:
                            matches = self._search_in_content(content, search_terms, case_sensitive, "PDF")
                            for match in matches:
                                match["file"] = str(pdf_file.relative_to(paper_path))
                                match["paper_id"] = paper["directory"]
                                paper_matches.append(match)
                    except Exception as e:
                        logger.warning(f"Error reading PDF file {pdf_file}: {e}")
            
            # Search in supplementary files
            if "supplementary" in search_fields:
                supp_files = list(paper_path.rglob("supplementary/*"))
                for supp_file in supp_files:
                    if supp_file.is_file():
                        try:
                            with open(supp_file, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                matches = self._search_in_content(content, search_terms, case_sensitive, "Supplementary")
                                for match in matches:
                                    match["file"] = str(supp_file.relative_to(paper_path))
                                    match["paper_id"] = paper["directory"]
                                    paper_matches.append(match)
                        except Exception as e:
                            logger.warning(f"Error reading supplementary file {supp_file}: {e}")
            
            # Search in metadata
            if "metadata" in search_fields:
                metadata = paper.get("metadata", {})
                metadata_text = json.dumps(metadata, ensure_ascii=False)
                matches = self._search_in_content(metadata_text, search_terms, case_sensitive, "Metadata")
                for match in matches:
                    match["file"] = "metadata"
                    match["paper_id"] = paper["directory"]
                    paper_matches.append(match)
            
            if paper_matches:
                search_results["matches"].extend(paper_matches)
                papers_with_matches += 1
                total_matches += len(paper_matches)
        
        # Update summary
        search_results["summary"] = {
            "total_matches": total_matches,
            "papers_with_matches": papers_with_matches,
            "total_papers_searched": len(output_data["paper_directories"]),
            "match_rate": papers_with_matches / len(output_data["paper_directories"]) if output_data["paper_directories"] else 0
        }
        
        return search_results
    
    def _search_in_content(self, content: str, search_terms: List[str], case_sensitive: bool, content_type: str) -> List[Dict[str, Any]]:
        """
        Search for terms in content and return matches with context.
        
        Args:
            content: Text content to search in
            search_terms: Terms to search for
            case_sensitive: Whether search should be case sensitive
            content_type: Type of content being searched
            
        Returns:
            List of matches with context
        """
        matches = []
        
        if not case_sensitive:
            content = content.lower()
            search_terms = [term.lower() for term in search_terms]
        
        # Split content into lines for better context
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line_matches = []
            
            for term in search_terms:
                if term in line:
                    # Find all occurrences of the term in this line
                    start_positions = []
                    pos = 0
                    while True:
                        pos = line.find(term, pos)
                        if pos == -1:
                            break
                        start_positions.append(pos)
                        pos += 1
                    
                    for start_pos in start_positions:
                        # Extract context around the match
                        context_start = max(0, start_pos - 50)
                        context_end = min(len(line), start_pos + len(term) + 50)
                        context = line[context_start:context_end]
                        
                        # Highlight the match
                        if context_start > 0:
                            context = "..." + context
                        if context_end < len(line):
                            context = context + "..."
                        
                        line_matches.append({
                            "term": term,
                            "line_number": line_num,
                            "position": start_pos,
                            "context": context,
                            "content_type": content_type
                        })
            
            matches.extend(line_matches)
        
        return matches
    
    def _extract_pdf_text(self, pdf_file: Path) -> Optional[str]:
        """
        Basic PDF text extraction. This is a simple implementation.
        For better results, consider using PyPDF2, pdfplumber, or similar libraries.
        
        Args:
            pdf_file: Path to PDF file
            
        Returns:
            Extracted text or None if extraction fails
        """
        try:
            # Try to use PyPDF2 if available
            try:
                import PyPDF2
                with open(pdf_file, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                    return text
            except ImportError:
                # Fallback: try to extract text using system tools
                import subprocess
                try:
                    result = subprocess.run(['pdftotext', str(pdf_file), '-'], 
                                          capture_output=True, text=True, timeout=30)
                    if result.returncode == 0:
                        return result.stdout
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    pass
                
                # Last resort: return None
                return None
        except Exception as e:
            logger.warning(f"Error extracting text from PDF {pdf_file}: {e}")
            return None
    
    def create_search_results_table(self, search_results: Dict[str, Any], table_id: str = "search_results_table") -> str:
        """
        Create a table showing fulltext search results.
        
        Args:
            search_results: Output from search_fulltext
            table_id: Unique ID for the table
            
        Returns:
            HTML string with search results table
        """
        if not search_results["matches"]:
            return "<p>No matches found in the search.</p>"
        
        # Prepare table data
        table_data = []
        for match in search_results["matches"]:
            # Create hyperlink to paper
            paper_link = f'<a href="#paper_{match["paper_id"]}" onclick="showPaperDetails(\'{match["paper_id"]}\')">{match["paper_id"]}</a>'
            
            row = {
                "Paper ID": paper_link,
                "Term": match["term"],
                "File": match["file"],
                "Line": match["line_number"],
                "Context": match["context"][:100] + "..." if len(match["context"]) > 100 else match["context"],
                "Content Type": match["content_type"]
            }
            table_data.append(row)
        
        # Create HTML table
        try:
            htmlx, table = HtmlTable.create_html_table(
                dict_by_id=OrderedDict({f"{row['Paper ID']}_{i}": row for i, row in enumerate(table_data)}),
                datatables=True,
                table_id=table_id
            )
            
            html_string = ET.tostring(htmlx, encoding='unicode', pretty_print=True)
            return html_string
            
        except Exception as e:
            logger.error(f"Error creating search results table: {e}")
            return self._create_simple_table(table_data)
    
    def get_papers_with_matches(self, search_results: Dict[str, Any]) -> List[str]:
        """
        Get list of paper IDs that contain search matches.
        
        Args:
            search_results: Output from search_fulltext
            
        Returns:
            List of unique paper IDs with matches
        """
        return list(set(match["paper_id"] for match in search_results["matches"]))
    
    def filter_papers_by_search(self, output_data: Dict[str, Any], search_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filter papers to only include those with search matches.
        
        Args:
            output_data: Original output data
            search_results: Search results
            
        Returns:
            Filtered output data containing only papers with matches
        """
        papers_with_matches = self.get_papers_with_matches(search_results)
        
        filtered_data = {
            "output_dir": f"{output_data['output_dir']}_filtered",
            "metadata_files": output_data["metadata_files"],
            "paper_directories": [paper for paper in output_data["paper_directories"] 
                                if paper["directory"] in papers_with_matches],
            "summary": {}
        }
        
        # Update summary
        filtered_data["summary"] = {
            "total_papers": len(filtered_data["paper_directories"]),
            "metadata_files_found": list(filtered_data["metadata_files"].keys()),
            "has_xml": any("fulltext.xml" in str(p) for p in filtered_data["paper_directories"]),
            "has_pdf": any("fulltext.pdf" in str(p) for p in filtered_data["paper_directories"]),
            "has_supplementary": any("supplementary" in str(p) for p in filtered_data["paper_directories"]),
            "search_matches": search_results["summary"]["total_matches"]
        }
        
        return filtered_data
    
    def extract_figures(self, output_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract figures, captions, and thumbnails from papers.
        
        Args:
            output_data: Output from read_pygetpapers_output
            
        Returns:
            Dictionary containing figure information for each paper
        """
        figures_data = {
            "papers": {},
            "summary": {
                "total_figures": 0,
                "papers_with_figures": 0,
                "figure_types": {}
            }
        }
        
        for paper in output_data["paper_directories"]:
            paper_figures = self._extract_paper_figures(paper)
            if paper_figures:
                figures_data["papers"][paper["directory"]] = paper_figures
                figures_data["summary"]["papers_with_figures"] += 1
                figures_data["summary"]["total_figures"] += len(paper_figures["figures"])
        
        return figures_data
    
    def _extract_paper_figures(self, paper: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract figures from a single paper.
        
        Args:
            paper: Paper information dictionary
            
        Returns:
            Dictionary with figure information or None if no figures found
        """
        paper_path = Path(paper["path"])
        figures = []
        
        # Extract from XML files
        xml_files = list(paper_path.glob("*.xml"))
        for xml_file in xml_files:
            try:
                xml_figures = self._extract_figures_from_xml(xml_file, paper["directory"])
                figures.extend(xml_figures)
            except Exception as e:
                logger.warning(f"Error extracting figures from XML {xml_file}: {e}")
        
        # Extract from supplementary files
        supp_files = list(paper_path.rglob("supplementary/*"))
        for supp_file in supp_files:
            if supp_file.is_file() and supp_file.suffix.lower() in ['.xml', '.html']:
                try:
                    supp_figures = self._extract_figures_from_supplementary(supp_file, paper["directory"])
                    figures.extend(supp_figures)
                except Exception as e:
                    logger.warning(f"Error extracting figures from supplementary {supp_file}: {e}")
        
        # Look for image files
        image_files = list(paper_path.rglob("*.jpg")) + list(paper_path.rglob("*.jpeg")) + \
                     list(paper_path.rglob("*.png")) + list(paper_path.rglob("*.gif")) + \
                     list(paper_path.rglob("*.tiff")) + list(paper_path.rglob("*.tif"))
        
        for image_file in image_files:
            try:
                image_figure = self._extract_image_figure(image_file, paper["directory"])
                if image_figure:
                    figures.append(image_figure)
            except Exception as e:
                logger.warning(f"Error processing image {image_file}: {e}")
        
        if figures:
            return {
                "paper_id": paper["directory"],
                "paper_title": paper.get("metadata", {}).get("title", paper["directory"]),
                "figures": figures,
                "total_figures": len(figures)
            }
        
        return None
    
    def _extract_figures_from_xml(self, xml_file: Path, paper_id: str) -> List[Dict[str, Any]]:
        """
        Extract figures from XML content.
        
        Args:
            xml_file: Path to XML file
            paper_id: Paper identifier
            
        Returns:
            List of figure dictionaries
        """
        figures = []
        
        try:
            import lxml.etree as ET
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Define common figure-related tags
            figure_tags = [
                "fig", "figure", "fig-group", "fig-group-wrap",
                "graphic", "media", "inline-graphic", "inline-media"
            ]
            
            # Search for figure elements
            for tag in figure_tags:
                try:
                    elements = root.xpath(f"//*[local-name()='{tag}']")
                    for i, element in enumerate(elements):
                        figure_info = self._parse_figure_element(element, paper_id, f"{xml_file.stem}_fig_{i+1}")
                        if figure_info:
                            figures.append(figure_info)
                except Exception as e:
                    logger.debug(f"Error searching for {tag} elements: {e}")
            
            # Also look for captions that might be separate
            caption_tags = ["caption", "fig-caption", "title", "label"]
            for tag in caption_tags:
                try:
                    elements = root.xpath(f"//*[local-name()='{tag}']")
                    for i, element in enumerate(elements):
                        caption_info = self._parse_caption_element(element, paper_id, f"{xml_file.stem}_caption_{i+1}")
                        if caption_info:
                            figures.append(caption_info)
                except Exception as e:
                    logger.debug(f"Error searching for {tag} captions: {e}")
            
        except Exception as e:
            logger.warning(f"Error parsing XML {xml_file}: {e}")
        
        return figures
    
    def _parse_figure_element(self, element, paper_id: str, figure_id: str) -> Optional[Dict[str, Any]]:
        """
        Parse a figure element and extract information.
        
        Args:
            element: XML element
            paper_id: Paper identifier
            figure_id: Figure identifier
            
        Returns:
            Figure information dictionary
        """
        try:
            # Extract caption
            caption = ""
            try:
                caption_elem = element.find(".//*[local-name()='caption']")
                if caption_elem is not None:
                    caption = " ".join(caption_elem.itertext()).strip()
            except Exception:
                pass
            
            # Extract label
            label = ""
            try:
                label_elem = element.find(".//*[local-name()='label']")
                if label_elem is not None:
                    label = " ".join(label_elem.itertext()).strip()
            except Exception:
                pass
            
            # Extract image source
            image_src = ""
            try:
                graphic_elem = element.find(".//*[local-name()='graphic']")
                if graphic_elem is not None:
                    image_src = graphic_elem.get("href", graphic_elem.get("src", ""))
            except Exception:
                pass
            
            # Extract title
            title = ""
            try:
                title_elem = element.find(".//*[local-name()='title']")
                if title_elem is not None:
                    title = " ".join(title_elem.itertext()).strip()
            except Exception:
                pass
            
            if caption or label or image_src:
                return {
                    "figure_id": figure_id,
                    "paper_id": paper_id,
                    "caption": caption,
                    "label": label,
                    "title": title,
                    "image_src": image_src,
                    "source_file": str(element.getroottree().docinfo.URL or "unknown"),
                    "figure_type": "xml_extracted"
                }
        
        except Exception as e:
            logger.debug(f"Error parsing figure element: {e}")
        
        return None
    
    def _parse_caption_element(self, element, paper_id: str, caption_id: str) -> Optional[Dict[str, Any]]:
        """
        Parse a caption element and extract information.
        
        Args:
            element: XML element
            paper_id: Paper identifier
            caption_id: Caption identifier
            
        Returns:
            Caption information dictionary
        """
        try:
            caption_text = " ".join(element.itertext()).strip()
            if caption_text:
                return {
                    "figure_id": caption_id,
                    "paper_id": paper_id,
                    "caption": caption_text,
                    "label": "",
                    "title": "",
                    "image_src": "",
                    "source_file": str(element.getroottree().docinfo.URL or "unknown"),
                    "figure_type": "caption_only"
                }
        
        except Exception as e:
            logger.debug(f"Error parsing caption element: {e}")
        
        return None
    
    def _extract_figures_from_supplementary(self, supp_file: Path, paper_id: str) -> List[Dict[str, Any]]:
        """
        Extract figures from supplementary files.
        
        Args:
            supp_file: Path to supplementary file
            paper_id: Paper identifier
            
        Returns:
            List of figure dictionaries
        """
        figures = []
        
        try:
            if supp_file.suffix.lower() == '.xml':
                figures = self._extract_figures_from_xml(supp_file, paper_id)
            elif supp_file.suffix.lower() == '.html':
                figures = self._extract_figures_from_html(supp_file, paper_id)
        
        except Exception as e:
            logger.warning(f"Error extracting figures from supplementary {supp_file}: {e}")
        
        return figures
    
    def _extract_figures_from_html(self, html_file: Path, paper_id: str) -> List[Dict[str, Any]]:
        """
        Extract figures from HTML content.
        
        Args:
            html_file: Path to HTML file
            paper_id: Paper identifier
            
        Returns:
            List of figure dictionaries
        """
        figures = []
        
        try:
            import lxml.html as html
            with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            tree = html.fromstring(content)
            
            # Find figure elements
            figure_elements = tree.xpath("//figure")
            for i, element in enumerate(figure_elements):
                caption = ""
                caption_elem = element.find(".//figcaption")
                if caption_elem is not None:
                    caption = caption_elem.text_content().strip()
                
                img_src = ""
                img_elem = element.find(".//img")
                if img_elem is not None:
                    img_src = img_elem.get("src", "")
                
                if caption or img_src:
                    figures.append({
                        "figure_id": f"{html_file.stem}_fig_{i+1}",
                        "paper_id": paper_id,
                        "caption": caption,
                        "label": "",
                        "title": "",
                        "image_src": img_src,
                        "source_file": str(html_file),
                        "figure_type": "html_extracted"
                    })
        
        except Exception as e:
            logger.warning(f"Error extracting figures from HTML {html_file}: {e}")
        
        return figures
    
    def _extract_image_figure(self, image_file: Path, paper_id: str) -> Optional[Dict[str, Any]]:
        """
        Extract figure information from an image file.
        
        Args:
            image_file: Path to image file
            paper_id: Paper identifier
            
        Returns:
            Figure information dictionary
        """
        try:
            # Try to create a thumbnail
            thumbnail = self._create_image_thumbnail(image_file)
            
            return {
                "figure_id": f"{image_file.stem}",
                "paper_id": paper_id,
                "caption": f"Image: {image_file.name}",
                "label": image_file.stem,
                "title": image_file.name,
                "image_src": str(image_file),
                "source_file": str(image_file),
                "figure_type": "image_file",
                "thumbnail": thumbnail
            }
        
        except Exception as e:
            logger.warning(f"Error processing image {image_file}: {e}")
            return None
    
    def _create_image_thumbnail(self, image_file: Path) -> Optional[str]:
        """
        Create a base64 thumbnail of an image.
        
        Args:
            image_file: Path to image file
            
        Returns:
            Base64 encoded thumbnail or None
        """
        try:
            from PIL import Image
            import io
            
            # Open and resize image
            with Image.open(image_file) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Resize to thumbnail
                img.thumbnail((200, 200), Image.Resampling.LANCZOS)
                
                # Convert to base64
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=85)
                img_str = base64.b64encode(buffer.getvalue()).decode()
                
                return f"data:image/jpeg;base64,{img_str}"
        
        except ImportError:
            logger.warning("PIL/Pillow not available for thumbnail creation")
            return None
        except Exception as e:
            logger.warning(f"Error creating thumbnail for {image_file}: {e}")
            return None
    
    def create_figures_table(self, figures_data: Dict[str, Any], table_id: str = "figures_table") -> str:
        """
        Create a table showing figures with thumbnails.
        
        Args:
            figures_data: Output from extract_figures
            table_id: Unique ID for the table
            
        Returns:
            HTML string with figures table
        """
        if not figures_data["papers"]:
            return "<p>No figures found in the papers.</p>"
        
        # Prepare table data
        table_data = []
        for paper_id, paper_figures in figures_data["papers"].items():
            for figure in paper_figures["figures"]:
                # Create thumbnail HTML
                thumbnail_html = ""
                if figure.get("thumbnail"):
                    thumbnail_html = f'<img src="{figure["thumbnail"]}" alt="Thumbnail" style="max-width: 100px; max-height: 100px;">'
                elif figure.get("image_src"):
                    thumbnail_html = f'<span style="color: #666;">📷 Image available</span>'
                else:
                    thumbnail_html = f'<span style="color: #999;">No image</span>'
                
                # Create paper link
                paper_link = f'<a href="#paper_{figure["paper_id"]}" onclick="showPaperDetails(\'{figure["paper_id"]}\')">{figure["paper_id"]}</a>'
                
                row = {
                    "Paper ID": paper_link,
                    "Figure ID": figure["figure_id"],
                    "Thumbnail": thumbnail_html,
                    "Caption": figure["caption"][:100] + "..." if len(figure["caption"]) > 100 else figure["caption"],
                    "Label": figure["label"],
                    "Title": figure["title"],
                    "Type": figure["figure_type"]
                }
                table_data.append(row)
        
        # Create HTML table
        try:
            htmlx, table = HtmlTable.create_html_table(
                dict_by_id=OrderedDict({f"{row['Paper ID']}_{row['Figure ID']}": row for row in table_data}),
                datatables=True,
                table_id=table_id
            )
            
            html_string = ET.tostring(htmlx, encoding='unicode', pretty_print=True)
            return html_string
            
        except Exception as e:
            logger.error(f"Error creating figures table: {e}")
            return self._create_simple_table(table_data)
    
    def _create_simple_table(self, table_data: List[Dict[str, Any]]) -> str:
        """
        Create a simple HTML table as fallback.
        
        Args:
            table_data: List of row dictionaries
            
        Returns:
            HTML string with simple table
        """
        if not table_data:
            return "<p>No data available.</p>"
        
        html = "<table border='1' style='border-collapse: collapse; width: 100%;'>"
        
        # Header
        html += "<thead><tr>"
        for key in table_data[0].keys():
            html += f"<th style='padding: 8px; text-align: left;'>{key}</th>"
        html += "</tr></thead>"
        
        # Body
        html += "<tbody>"
        for row in table_data:
            html += "<tr>"
            for value in row.values():
                html += f"<td style='padding: 8px;'>{value}</td>"
            html += "</tr>"
        html += "</tbody></table>"
        
        return html
    
    def create_figures_summary_table(self, figures_data: Dict[str, Any], table_id: str = "figures_summary_table") -> str:
        """
        Create a summary table of figures by paper.
        
        Args:
            figures_data: Output from extract_figures
            table_id: Unique ID for the table
            
        Returns:
            HTML string with figures summary table
        """
        if not figures_data["papers"]:
            return "<p>No figures found in the papers.</p>"
        
        # Prepare summary data
        summary_data = []
        for paper_id, paper_figures in figures_data["papers"].items():
            # Count figure types
            type_counts = {}
            for figure in paper_figures["figures"]:
                fig_type = figure["figure_type"]
                type_counts[fig_type] = type_counts.get(fig_type, 0) + 1
            
            row = {
                "Paper ID": paper_id,
                "Paper Title": paper_figures["paper_title"][:50] + "..." if len(paper_figures["paper_title"]) > 50 else paper_figures["paper_title"],
                "Total Figures": paper_figures["total_figures"],
                "XML Figures": type_counts.get("xml_extracted", 0),
                "Image Files": type_counts.get("image_file", 0),
                "Captions Only": type_counts.get("caption_only", 0)
            }
            summary_data.append(row)
        
        # Create HTML table
        try:
            htmlx, table = HtmlTable.create_html_table(
                dict_by_id=OrderedDict({row["Paper ID"]: row for row in summary_data}),
                datatables=True,
                table_id=table_id
            )
            
            html_string = ET.tostring(htmlx, encoding='unicode', pretty_print=True)
            return html_string
            
        except Exception as e:
            logger.error(f"Error creating figures summary table: {e}")
            return self._create_simple_table(summary_data)
    
    def create_comparison_table(self, comparison_data: Dict[str, Any], table_id: str = "comparison_table") -> str:
        """
        Create a comparison table for multiple corpora.
        
        Args:
            comparison_data: Output from compare_corpora
            table_id: Unique ID for the table
            
        Returns:
            HTML string with comparison table
        """
        if not comparison_data["corpora"]:
            return "<p>No corpora to compare.</p>"
        
        # Prepare comparison data
        comparison_rows = []
        for corpus in comparison_data["corpora"]:
            row = {
                "Corpus": corpus["name"],
                "Total Papers": corpus["total_papers"],
                "XML Files": "✅" if corpus["has_xml"] else "❌",
                "PDF Files": "✅" if corpus["has_pdf"] else "❌",
                "Supplementary": "✅" if corpus["has_supplementary"] else "❌"
            }
            comparison_rows.append(row)
        
        # Create HTML table
        try:
            htmlx, table = HtmlTable.create_html_table(
                dict_by_id=OrderedDict({row["Corpus"]: row for row in comparison_rows}),
                datatables=True,
                table_id=table_id
            )
            
            html_string = ET.tostring(htmlx, encoding='unicode', pretty_print=True)
            return html_string
            
        except Exception as e:
            logger.error(f"Error creating comparison table: {e}")
            return self._create_simple_table(comparison_rows)
    
    def create_overlap_table(self, comparison_data: Dict[str, Any], table_id: str = "overlap_table") -> str:
        """
        Create an overlap analysis table.
        
        Args:
            comparison_data: Output from compare_corpora
            table_id: Unique ID for the table
            
        Returns:
            HTML string with overlap table
        """
        if not comparison_data.get("overlap_analysis"):
            return "<p>No overlap analysis available.</p>"
        
        overlap = comparison_data["overlap_analysis"]
        summary = comparison_data["summary_stats"]
        
        overlap_data = [
            {
                "Metric": "Total Corpora",
                "Value": summary["total_corpora"],
                "Description": "Number of corpora compared"
            },
            {
                "Metric": "Common Papers",
                "Value": overlap["common_papers"],
                "Description": "Papers found in all corpora"
            },
            {
                "Metric": "Average Papers per Corpus",
                "Value": f"{summary['average_papers_per_corpus']:.1f}",
                "Description": "Average number of papers per corpus"
            }
        ]
        
        # Add unique papers per corpus
        for i, unique_count in enumerate(overlap.get("unique_papers_per_corpus", [])):
            corpus_name = comparison_data["corpora"][i]["name"] if i < len(comparison_data["corpora"]) else f"Corpus {i+1}"
            overlap_data.append({
                "Metric": f"Unique in {corpus_name}",
                "Value": unique_count,
                "Description": f"Papers unique to {corpus_name}"
            })
        
        # Create HTML table
        try:
            htmlx, table = HtmlTable.create_html_table(
                dict_by_id=OrderedDict({row["Metric"]: row for row in overlap_data}),
                datatables=True,
                table_id=table_id
            )
            
            html_string = ET.tostring(htmlx, encoding='unicode', pretty_print=True)
            return html_string
            
        except Exception as e:
            logger.error(f"Error creating overlap table: {e}")
            return self._create_simple_table(overlap_data)


# Import ET for HTML generation
import lxml.etree as ET 