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
    
    def create_papers_table(self, output_data: Dict[str, Any], table_id: str = "papers_table") -> str:
        """
        Create an interactive HTML table from pygetpapers output.
        
        Args:
            output_data: Output from read_pygetpapers_output
            table_id: Unique ID for the table
            
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
            
            # Create row data
            row = {
                "ID": paper["directory"],
                "Title": title[:100] + "..." if len(title) > 100 else title,
                "Authors": authors[:50] + "..." if len(authors) > 50 else authors,
                "Journal": journal,
                "DOI": doi,
                "PMID": pmid,
                "PMCID": pmcid,
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


# Import ET for HTML generation
import lxml.etree as ET 