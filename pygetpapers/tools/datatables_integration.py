"""
Datatables integration for pygetpapers output visualization.

This module provides functionality to create interactive HTML tables using jQuery
DataTables for displaying pygetpapers output data.

ORIGINAL AUTHOR: petermr (Peter Murray-Rust) <peter.murray.rust@googlemail.com>
ORIGINAL DATE: July 5, 2025
GIT COMMITS:
- f92cfab (Jul 5, 2025): Initial implementation "added datatables and corpus FIRST PASS MAY HAV BUGS"
- 84c12de (Jul 11, 2025): Major enhancement "Add datatables HTML export functionality with external CSS support"
- 2e9f96d (Jul 15, 2025): Final tidy "tidying and testing"

EDITED: Assistant on December 19, 2024 for pygetpapers v2.0 (1.2.5a23)
- Removed draft features (figure extraction, corpus comparison) from public API
- Added warning messages for disabled functionality
- Preserved original code structure for future re-enablement
"""

import base64
import json
import logging
from collections import OrderedDict
from pathlib import Path
from typing import Any, Dict, List, Optional

import lxml.etree as ET
import pandas as pd

# CSS styles for datatables
DATATABLES_CSS = """
body {
    font-family: Arial, sans-serif;
    margin: 40px;
}
.header {
    background-color: #f8f9fa;
    padding: 20px;
    border-radius: 5px;
    margin-bottom: 30px;
}
.stats {
    display: flex;
    gap: 20px;
    margin-bottom: 20px;
}
.stat {
    background-color: #e9ecef;
    padding: 10px;
    border-radius: 5px;
    text-align: center;
}
.stat-number {
    font-size: 24px;
    font-weight: bold;
    color: #007bff;
}
.stat-label {
    font-size: 12px;
    color: #6c757d;
}
.table-links {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
}
.table-card {
    border: 1px solid #dee2e6;
    border-radius: 5px;
    padding: 20px;
    text-align: center;
}
.table-card h3 {
    margin-top: 0;
    color: #495057;
}
.table-card p {
    color: #6c757d;
    margin-bottom: 20px;
}
.table-link {
    display: inline-block;
    background-color: #007bff;
    color: white;
    padding: 10px 20px;
    text-decoration: none;
    border-radius: 5px;
}
.table-link:hover {
    background-color: #0056b3;
}
"""

logger = logging.getLogger(__name__)

# Check if datatables_module is available
try:
    from datatables_module import HtmlTable as ExternalHtmlTable

    DATATABLES_AVAILABLE = True
    HtmlTable = ExternalHtmlTable
except ImportError:
    DATATABLES_AVAILABLE = False
    logger.warning(
        "datatables_module not available. Using fallback HTML table implementation."
    )

    class HtmlTable:
        """Fallback HTML table implementation when datatables_module is not available."""

        @staticmethod
        def create_html_table(dict_by_id, datatables=True, table_id="table"):
            """Create a simple HTML table from dictionary data with jQuery datatables support."""
            if not dict_by_id:
                # Return empty divs as strings
                return "<div></div>", "<table></table>"

            # Get headers from first item
            first_item = next(iter(dict_by_id.values()))
            headers = list(first_item.keys())

            # Build HTML table as string to avoid escaping issues
            html_parts = []

            # Table structure
            html_parts.append(
                f'<table id="{table_id}" style="width: 100%; border-collapse: collapse;">'
            )

            # Header
            html_parts.append("<thead><tr>")
            for header in headers:
                html_parts.append(
                    f'<th style="border: 1px solid #ddd; padding: 8px; '
                    f'background-color: #f2f2f2;">{header}</th>'
                )
            html_parts.append("</tr></thead>")

            # Body
            html_parts.append("<tbody>")
            for item_id, item_data in dict_by_id.items():
                html_parts.append("<tr>")
                for key in headers:
                    value = item_data.get(key, "")
                    html_parts.append(
                        f'<td style="border: 1px solid #ddd; padding: 8px;">{value}</td>'
                    )
                html_parts.append("</tr>")
            html_parts.append("</tbody>")

            html_parts.append("</table>")

            table_html = "".join(html_parts)

            # Add jQuery datatables if requested
            if datatables:
                # Create complete HTML document
                full_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <script src=\"https://code.jquery.com/jquery-3.6.0.min.js\"></script>
                    <link rel=\"stylesheet\" type=\"text/css\"
                          href=\"https://cdn.datatables.net/1.11.5/css/jquery.dataTables.css\">
                    <script src=\"https://cdn.datatables.net/1.11.5/js/jquery.dataTables.js\"></script>
                    <script>
                    $(document).ready(function() {{
                        $('#{table_id}').DataTable({{
                            pageLength: 25,
                            lengthMenu: [[10, 25, 50, 100, -1], [10, 25, 50, 100, \"All\"]],
                            responsive: true,
                            scrollX: true,
                            columnDefs: [
                                {{
                                    targets: '_all',
                                    render: function(data, type, row) {{
                                        if (type === 'display' && typeof data === 'string' && data.includes('<')) {{
                                            return data; // Allow HTML rendering
                                        }}
                                        return data;
                                    }}
                                }}
                            ],
                            language: {{
                                search: \"Search:\",
                                lengthMenu: \"Show _MENU_ entries per page\",
                                info: \"Showing _START_ to _END_ of _TOTAL_ entries\",
                                infoEmpty: \"Showing 0 to 0 of 0 entries\",
                                infoFiltered: \"(filtered from _MAX_ total entries)\",
                                paginate: {{
                                    first: \"First\",
                                    last: \"Last\",
                                    next: \"Next\",
                                    previous: \"Previous\"
                                }}
                            }}
                        }});
                    }});
                    </script>
                </head>
                <body>
                    <div style=\"overflow-x: auto;\">
                        {table_html}
                    </div>
                </body>
                </html>
                """

                return full_html, table_html

            # For non-datatables version, create a simple container
            container_html = f'<div style="overflow-x: auto;">{table_html}</div>'
            return container_html, table_html


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
            "openalex_results.json",
        ]

        if not DATATABLES_AVAILABLE:
            logger.warning(
                "datatables_module not available. Tables will be displayed using basic HTML. "
                "For enhanced functionality, install the datatables_module from the amilib project."
            )

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
            "summary": {},
        }

        # Read metadata files
        for filename in self.supported_metadata_files:
            file_path = output_path / filename
            if file_path.exists():
                try:
                    if filename.endswith(".json"):
                        with open(file_path, "r", encoding="utf-8") as f:
                            result["metadata_files"][filename] = json.load(f)
                    elif filename.endswith(".csv"):
                        result["metadata_files"][filename] = pd.read_csv(file_path)
                    elif filename.endswith(".html"):
                        with open(file_path, "r", encoding="utf-8") as f:
                            result["metadata_files"][filename] = f.read()
                except Exception as e:
                    logger.warning(f"Error reading {filename}: {e}")

        # Scan for paper directories
        for item in output_path.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                paper_info = self._analyze_paper_directory(item)
                if paper_info:
                    result["paper_directories"].append(paper_info)

        # Create summary
        result["summary"] = {
            "total_papers": len(result["paper_directories"]),
            "metadata_files_found": list(result["metadata_files"].keys()),
            "has_xml": any(
                "fulltext.xml" in str(p) for p in result["paper_directories"]
            ),
            "has_pdf": any(
                "fulltext.pdf" in str(p) for p in result["paper_directories"]
            ),
            "has_supplementary": any(
                "supplementary" in str(p) for p in result["paper_directories"]
            ),
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
            "metadata": {},
        }

        # Check for metadata files
        metadata_files = [
            "eupmc_result.json",
            "crossref_result.json",
            "arxiv_result.json",
        ]
        for metadata_file in metadata_files:
            metadata_path = paper_dir / metadata_file
            if metadata_path.exists():
                try:
                    with open(metadata_path, "r", encoding="utf-8") as f:
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

    def create_papers_table(
        self,
        output_data: Dict[str, Any],
        table_id: str = "papers_table",
        include_checkboxes: bool = True,
        selectable_rows: bool = True,
    ) -> str:
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

            # Handle different author field names
            authors = "Unknown"
            if "authorString" in metadata:
                authors = metadata["authorString"]
            elif "authors" in metadata:
                authors = metadata["authors"]
            elif "authorList" in metadata and "author" in metadata["authorList"]:
                # Europe PMC format
                author_list = []
                for author in metadata["authorList"]["author"]:
                    if "fullName" in author:
                        author_list.append(author["fullName"])
                authors = ", ".join(author_list) if author_list else "Unknown"

            # Extract journal name from nested structure
            journal = "Unknown"
            if "journalInfo" in metadata and "journal" in metadata["journalInfo"]:
                journal = metadata["journalInfo"]["journal"].get("title", "Unknown")
            elif "journalTitle" in metadata:
                journal = metadata["journalTitle"]
            elif "journal" in metadata:
                journal = metadata["journal"]

            doi = metadata.get("doi", "")
            pmid = metadata.get("pmid", "")
            pmcid = metadata.get("pmcid", "")

            # Handle different date field names
            pub_date = ""
            if "firstPublicationDate" in metadata:
                pub_date = metadata["firstPublicationDate"]
            elif "publication_date" in metadata:
                pub_date = metadata["publication_date"]
            elif "date" in metadata:
                pub_date = metadata["date"]

            # Check file availability
            has_xml = any("fulltext.xml" in f for f in paper["files"])
            has_pdf = any("fulltext.pdf" in f for f in paper["files"])
            has_supp = any("supplementary" in f for f in paper["files"])

            # Check HTML file types
            has_raw_html = any("fulltext.raw.html" in f for f in paper["files"])
            has_xml_html = any("fulltext.xml.html" in f for f in paper["files"])
            has_pdf_html = any("fulltext.pdf.html" in f for f in paper["files"])
            has_doc_html = any("fulltext.doc.html" in f for f in paper["files"])
            has_enhanced_html = any("html_with_ids.html" in f for f in paper["files"])

            # Create hyperlinks
            doi_link = f"https://doi.org/{doi}" if doi else ""
            pmid_link = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else ""
            pmcid_link = (
                f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/" if pmcid else ""
            )

            # Create comprehensive file links
            pdf_link = ""
            xml_link = ""
            html_link = ""
            supp_link = ""

            # Calculate relative path from datatables location to paper directory
            # Datatables are typically in output_dir/examples/output_dir/, so we need to go up two levels
            relative_paper_path = f"../../{paper['directory']}"

            # PDF link
            if has_pdf:
                pdf_file = next(
                    (f for f in paper["files"] if "fulltext.pdf" in f), None
                )
                if pdf_file:
                    pdf_link = f'<a href="{relative_paper_path}/{pdf_file}" target="_blank" title="Open PDF file">📄 PDF</a>'

            # XML link
            if has_xml:
                xml_file = next(
                    (f for f in paper["files"] if "fulltext.xml" in f), None
                )
                if xml_file:
                    xml_link = f'<a href="{relative_paper_path}/{xml_file}" target="_blank" title="Open XML file">📋 XML</a>'

            # HTML link (prioritize enhanced HTML, then XML HTML, then raw HTML)
            if has_enhanced_html:
                html_file = next(
                    (f for f in paper["files"] if "html_with_ids.html" in f), None
                )
                if html_file:
                    html_link = f'<a href="{relative_paper_path}/{html_file}" target="_blank" title="Open enhanced HTML file">🌐 Enhanced</a>'
            elif has_xml_html:
                html_file = next(
                    (f for f in paper["files"] if "fulltext.xml.html" in f), None
                )
                if html_file:
                    html_link = f'<a href="{relative_paper_path}/{html_file}" target="_blank" title="Open HTML file">🌐 HTML</a>'
            elif has_raw_html:
                html_file = next(
                    (f for f in paper["files"] if "fulltext.raw.html" in f), None
                )
                if html_file:
                    html_link = f'<a href="{relative_paper_path}/{html_file}" target="_blank" title="Open HTML file">🌐 HTML</a>'

            # Supplementary files link
            if has_supp:
                supp_files = [f for f in paper["files"] if "supplementary" in f]
                if supp_files:
                    supp_link = f'<a href="{relative_paper_path}/supplementary/" target="_blank" title="Open supplementary files directory">📁 Suppl ({len(supp_files)})</a>'

            # Extract abstract using enhanced method
            abstract = self._extract_abstract_string(metadata)
            if not abstract:
                abstract = "No abstract available"

            # Create row data with hyperlinks and tooltips
            row = {
                "Select": (
                    f'<input type="checkbox" class="paper-checkbox" '
                    f'data-paper-id="{paper["directory"]}">'
                    if include_checkboxes
                    else ""
                ),
                "ID": paper["directory"],
                "Title": title[:100] + "..." if len(title) > 100 else title,
                "Authors": authors[:50] + "..." if len(authors) > 50 else authors,
                "Abstract": abstract[:150] + "..." if len(abstract) > 150 else abstract,
                "Journal": journal,
                "DOI": (
                    f'<a href="{doi_link}" target="_blank" title="Open DOI link">{doi}</a>'
                    if doi_link
                    else doi
                ),
                "PMID": (
                    f'<a href="{pmid_link}" target="_blank" title="Open PubMed link">{pmid}</a>'
                    if pmid_link
                    else pmid
                ),
                "PMCID": (
                    f'<a href="{pmcid_link}" target="_blank" title="Open PMC link">{pmcid}</a>'
                    if pmcid_link
                    else pmcid
                ),
                "Date": pub_date,
                "XML": xml_link if xml_link else ("✅" if has_xml else "❌"),
                "PDF": pdf_link if pdf_link else ("✅" if has_pdf else "❌"),
                "Suppl": supp_link if supp_link else ("✅" if has_supp else "❌"),
                "HTML": (
                    html_link
                    if html_link
                    else (
                        "✅"
                        if (
                            has_raw_html
                            or has_xml_html
                            or has_pdf_html
                            or has_doc_html
                            or has_enhanced_html
                        )
                        else "❌"
                    )
                ),
                "Enhanced": "✅" if has_enhanced_html else "❌",
                "Files": len(paper["files"]),
            }
            table_data.append(row)

        # Create HTML table with tooltips using datatables
        try:
            # Define column tooltips
            column_tooltips = {
                "Select": "Select paper for bulk operations",
                "ID": "Unique paper identifier",
                "Title": "Paper title (truncated if >100 characters)",
                "Authors": "Author names (truncated if >50 characters)",
                "Abstract": "Paper abstract (truncated if >150 characters)",
                "Journal": "Journal or repository name",
                "DOI": "Digital Object Identifier - click to open",
                "PMID": "PubMed ID - click to open in PubMed",
                "PMCID": "PubMed Central ID - click to open in PMC",
                "Date": "Publication date",
                "XML": "XML fulltext file - click to download/view",
                "PDF": "PDF fulltext file - click to download/view",
                "Suppl": "Supplementary files - click to browse",
                "HTML": "HTML version of fulltext - click to view",
                "Enhanced": "Enhanced HTML with semantic markup",
                "Files": "Total number of files in paper directory",
            }

            htmlx = self._create_datatable_with_tooltips(
                dict_by_id=OrderedDict({row["ID"]: row for row in table_data}),
                table_id=table_id,
                column_tooltips=column_tooltips,
            )

            return htmlx

        except Exception as e:
            logger.error(f"Error creating datatable: {e}")
            # Fallback to simple HTML table
            return self._create_simple_table(table_data)

    def create_metadata_table(
        self, output_data: Dict[str, Any], table_id: str = "metadata_table"
    ) -> str:
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
                    metadata_data.append(
                        {
                            "File": filename,
                            "Type": "JSON",
                            "Records": len(result_list.get("result", [])),
                            "Total Hits": result_list.get("hitCount", "Unknown"),
                            "Format": "Europe PMC",
                        }
                    )
                else:
                    # Other JSON format
                    metadata_data.append(
                        {
                            "File": filename,
                            "Type": "JSON",
                            "Records": len(data) if isinstance(data, list) else 1,
                            "Total Hits": "Unknown",
                            "Format": "Generic",
                        }
                    )
            elif isinstance(data, pd.DataFrame):
                # CSV metadata
                metadata_data.append(
                    {
                        "File": filename,
                        "Type": "CSV",
                        "Records": len(data),
                        "Total Hits": len(data),
                        "Format": "CSV",
                    }
                )
            else:
                # HTML or other format
                metadata_data.append(
                    {
                        "File": filename,
                        "Type": "HTML",
                        "Records": "Unknown",
                        "Total Hits": "Unknown",
                        "Format": "HTML",
                    }
                )

        # Create HTML table
        try:
            htmlx, table = HtmlTable.create_html_table(
                dict_by_id=OrderedDict({row["File"]: row for row in metadata_data}),
                datatables=True,
                table_id=table_id,
            )

            # htmlx is now a string, not an lxml element
            return htmlx

        except Exception as e:
            logger.error(f"Error creating metadata table: {e}")
            return self._create_simple_table(metadata_data)

    def create_summary_table(
        self, output_data: Dict[str, Any], table_id: str = "summary_table"
    ) -> str:
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
                "Description": "Number of papers downloaded",
            },
            {
                "Metric": "Metadata Files",
                "Value": len(summary["metadata_files_found"]),
                "Description": "Number of metadata files found",
            },
            {
                "Metric": "XML Files",
                "Value": "✅" if summary["has_xml"] else "❌",
                "Description": "Full-text XML available",
            },
            {
                "Metric": "PDF Files",
                "Value": "✅" if summary["has_pdf"] else "❌",
                "Description": "Full-text PDF available",
            },
            {
                "Metric": "Supplementary Files",
                "Value": "✅" if summary["has_supplementary"] else "❌",
                "Description": "Supplementary materials available",
            },
        ]

        # Create HTML table
        try:
            htmlx, table = HtmlTable.create_html_table(
                dict_by_id=OrderedDict({row["Metric"]: row for row in summary_data}),
                datatables=True,
                table_id=table_id,
            )

            # htmlx is now a string, not an lxml element
            return htmlx

        except Exception as e:
            logger.error(f"Error creating summary table: {e}")
            return self._create_simple_table(summary_data)

    def _create_datatable_with_tooltips(
        self, dict_by_id: OrderedDict, table_id: str, column_tooltips: Dict[str, str]
    ) -> str:
        """
        Create a datatable with tooltips for column headers.

        Args:
            dict_by_id: OrderedDict with data
            table_id: Unique ID for the table
            column_tooltips: Dictionary mapping column names to tooltip text

        Returns:
            HTML string with datatable and tooltips
        """
        if not dict_by_id:
            return "<p>No data available.</p>"

        # Get headers from first item
        first_item = next(iter(dict_by_id.values()))
        headers = list(first_item.keys())

        # Build HTML table with tooltips
        html_parts = []
        html_parts.append(
            f'<table id="{table_id}" style="width: 100%; border-collapse: collapse;">'
        )

        # Header with tooltips
        html_parts.append("<thead><tr>")
        for header in headers:
            tooltip = column_tooltips.get(header, header)
            html_parts.append(
                f'<th style="border: 1px solid #ddd; padding: 8px; '
                f'background-color: #f2f2f2;" title="{tooltip}">{header}</th>'
            )
        html_parts.append("</tr></thead>")

        # Body
        html_parts.append("<tbody>")
        for item_id, item_data in dict_by_id.items():
            html_parts.append("<tr>")
            for header in headers:
                value = item_data.get(header, "")
                html_parts.append(
                    f'<td style="border: 1px solid #ddd; padding: 8px;">{value}</td>'
                )
            html_parts.append("</tr>")
        html_parts.append("</tbody>")

        html_parts.append("</table>")
        table_html = "".join(html_parts)

        # Create complete HTML document with datatables
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
            <link rel="stylesheet" type="text/css"
                  href="https://cdn.datatables.net/1.11.5/css/jquery.dataTables.css">
            <script src="https://cdn.datatables.net/1.11.5/js/jquery.dataTables.js"></script>
            <style>
                .tooltip {{
                    position: relative;
                    display: inline-block;
                }}
                .tooltip .tooltiptext {{
                    visibility: hidden;
                    width: 200px;
                    background-color: #555;
                    color: #fff;
                    text-align: center;
                    border-radius: 6px;
                    padding: 5px;
                    position: absolute;
                    z-index: 1;
                    bottom: 125%;
                    left: 50%;
                    margin-left: -100px;
                    opacity: 0;
                    transition: opacity 0.3s;
                }}
                .tooltip:hover .tooltiptext {{
                    visibility: visible;
                    opacity: 1;
                }}
            </style>
            <script>
            $(document).ready(function() {{
                $('#{table_id}').DataTable({{
                    pageLength: 25,
                    lengthMenu: [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
                    responsive: true,
                    scrollX: true,
                    columnDefs: [
                        {{
                            targets: '_all',
                            render: function(data, type, row) {{
                                if (type === 'display' && typeof data === 'string' && data.includes('<')) {{
                                    return data; // Allow HTML rendering
                                }}
                                return data;
                            }}
                        }}
                    ],
                    language: {{
                        search: "Search:",
                        lengthMenu: "Show _MENU_ entries per page",
                        info: "Showing _START_ to _END_ of _TOTAL_ entries",
                        infoEmpty: "Showing 0 to 0 of 0 entries",
                        infoFiltered: "(filtered from _MAX_ total entries)",
                        paginate: {{
                            first: "First",
                            last: "Last",
                            next: "Next",
                            previous: "Previous"
                        }}
                    }}
                }});
            }});
            </script>
        </head>
        <body>
            <div style="overflow-x: auto;">
                {table_html}
            </div>
        </body>
        </html>
        """

        return full_html

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

    def export_table_to_csv(
        self, output_data: Dict[str, Any], output_file: str
    ) -> bool:
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

                # Extract journal name from nested structure
                journal = ""
                if "journalInfo" in metadata and "journal" in metadata["journalInfo"]:
                    journal = metadata["journalInfo"]["journal"].get("title", "")
                elif "journalTitle" in metadata:
                    journal = metadata["journalTitle"]

                row = {
                    "ID": paper["directory"],
                    "Title": metadata.get("title", ""),
                    "Authors": metadata.get("authorString", ""),
                    "Journal": journal,
                    "DOI": metadata.get("doi", ""),
                    "PMID": metadata.get("pmid", ""),
                    "PMCID": metadata.get("pmcid", ""),
                    "Publication_Date": metadata.get("firstPublicationDate", ""),
                    "Abstract": metadata.get("abstractText", ""),
                    "Keywords": metadata.get("keywordList", ""),
                    "Has_XML": any("fulltext.xml" in f for f in paper["files"]),
                    "Has_PDF": any("fulltext.pdf" in f for f in paper["files"]),
                    "Has_Supplementary": any(
                        "supplementary" in f for f in paper["files"]
                    ),
                    "Has_Raw_HTML": any(
                        "fulltext.raw.html" in f for f in paper["files"]
                    ),
                    "Has_XML_HTML": any(
                        "fulltext.xml.html" in f for f in paper["files"]
                    ),
                    "Has_PDF_HTML": any(
                        "fulltext.pdf.html" in f for f in paper["files"]
                    ),
                    "Has_DOC_HTML": any(
                        "fulltext.doc.html" in f for f in paper["files"]
                    ),
                    "Has_Enhanced_HTML": any(
                        "html_with_ids.html" in f for f in paper["files"]
                    ),
                    "File_Count": len(paper["files"]),
                }
                csv_data.append(row)

            # Create DataFrame and save
            df = pd.DataFrame(csv_data)
            df.to_csv(output_file, index=False, encoding="utf-8")
            return True

        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            return False

    def get_paper_details(
        self, output_data: Dict[str, Any], paper_id: str
    ) -> Optional[Dict[str, Any]]:
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

    # DRAFT: Corpus comparison functionality - REMOVED FROM PUBLIC VIEW
    # This feature is under development and not ready for public use
    # ORIGINAL AUTHOR: petermr (Peter Murray-Rust) - July 5, 2025
    # EDITED: Assistant on 2024-12-19 for pygetpapers v2.0 - CURRENTLY IN DRAFT STATUS
    def merge_corpora(
        self, corpora_data: List[Dict[str, Any]], merged_name: str = "merged_corpus"
    ) -> Dict[str, Any]:
        """
        DRAFT: Merge multiple corpora into a single dataset.

        This feature is under development and not ready for public use.
        It has been removed from the public API.

        Args:
            corpora_data: List of output data from multiple corpora
            merged_name: Name for the merged corpus

        Returns:
            Merged corpus data
        """
        logger.warning(
            "Corpus merging is currently in draft status and not available for public use."
        )
        return {
            "output_dir": merged_name,
            "metadata_files": {},
            "paper_directories": [],
            "summary": {"total_papers": 0, "source_corpora": 0},
        }

    def compare_corpora(self, corpora_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        DRAFT: Compare multiple corpora and generate comparison statistics.

        This feature is under development and not ready for public use.
        It has been removed from the public API.

        Args:
            corpora_data: List of output data from multiple corpora

        Returns:
            Comparison data with statistics
        """
        logger.warning(
            "Corpus comparison is currently in draft status and not available for public use."
        )
        return {
            "corpora": [],
            "overlap_analysis": {},
            "summary_stats": {
                "total_corpora": 0,
                "total_papers": 0,
                "average_papers_per_corpus": 0,
            },
        }

    def search_fulltext(
        self,
        output_data: Dict[str, Any],
        search_terms: List[str],
        search_fields: List[str] = None,
        case_sensitive: bool = False,
    ) -> Dict[str, Any]:
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
            "summary": {},
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
                        with open(
                            xml_file, "r", encoding="utf-8", errors="ignore"
                        ) as f:
                            content = f.read()
                            matches = self._search_in_content(
                                content, search_terms, case_sensitive, "XML"
                            )
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
                        # Basic PDF text extraction (could be enhanced with PyPDF2 or
                        # similar)
                        content = self._extract_pdf_text(pdf_file)
                        if content:
                            matches = self._search_in_content(
                                content, search_terms, case_sensitive, "PDF"
                            )
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
                            with open(
                                supp_file, "r", encoding="utf-8", errors="ignore"
                            ) as f:
                                content = f.read()
                                matches = self._search_in_content(
                                    content,
                                    search_terms,
                                    case_sensitive,
                                    "Supplementary",
                                )
                                for match in matches:
                                    match["file"] = str(
                                        supp_file.relative_to(paper_path)
                                    )
                                    match["paper_id"] = paper["directory"]
                                    paper_matches.append(match)
                        except Exception as e:
                            logger.warning(
                                f"Error reading supplementary file {supp_file}: {e}"
                            )

            # Search in metadata
            if "metadata" in search_fields:
                metadata = paper.get("metadata", {})
                metadata_text = json.dumps(metadata, ensure_ascii=False)
                matches = self._search_in_content(
                    metadata_text, search_terms, case_sensitive, "Metadata"
                )
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
            "match_rate": (
                papers_with_matches / len(output_data["paper_directories"])
                if output_data["paper_directories"]
                else 0
            ),
        }

        return search_results

    def _search_in_content(
        self,
        content: str,
        search_terms: List[str],
        case_sensitive: bool,
        content_type: str,
    ) -> List[Dict[str, Any]]:
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
        lines = content.split("\n")

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

                        line_matches.append(
                            {
                                "term": term,
                                "line_number": line_num,
                                "position": start_pos,
                                "context": context,
                                "content_type": content_type,
                            }
                        )

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

                with open(pdf_file, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                    return text
            except ImportError:
                # Fallback: try to extract text using system tools
                import subprocess

                try:
                    result = subprocess.run(
                        ["pdftotext", str(pdf_file), "-"],
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )
                    if result.returncode == 0:
                        return result.stdout
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    pass

                # Last resort: return None
                return None
        except Exception as e:
            logger.warning(f"Error extracting text from PDF {pdf_file}: {e}")
            return None

    def create_search_results_table(
        self, search_results: Dict[str, Any], table_id: str = "search_results_table"
    ) -> str:
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
            paper_link = (
                f'<a href="#paper_{match["paper_id"]}" '
                f'onclick="showPaperDetails(\'{match["paper_id"]}\')">'
                f'{match["paper_id"]}</a>'
            )

            row = {
                "Paper ID": paper_link,
                "Term": match["term"],
                "File": match["file"],
                "Line": match["line_number"],
                "Context": (
                    match["context"][:100] + "..."
                    if len(match["context"]) > 100
                    else match["context"]
                ),
                "Content Type": match["content_type"],
            }
            table_data.append(row)

        # Create HTML table
        try:
            htmlx, table = HtmlTable.create_html_table(
                dict_by_id=OrderedDict(
                    {f"{row['Paper ID']}_{i}": row for i, row in enumerate(table_data)}
                ),
                datatables=True,
                table_id=table_id,
            )

            html_string = ET.tostring(htmlx, encoding="unicode", pretty_print=True)
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

    def filter_papers_by_search(
        self, output_data: Dict[str, Any], search_results: Dict[str, Any]
    ) -> Dict[str, Any]:
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
            "paper_directories": [
                paper
                for paper in output_data["paper_directories"]
                if paper["directory"] in papers_with_matches
            ],
            "summary": {},
        }

        # Update summary
        filtered_data["summary"] = {
            "total_papers": len(filtered_data["paper_directories"]),
            "metadata_files_found": list(filtered_data["metadata_files"].keys()),
            "has_xml": any(
                "fulltext.xml" in str(p) for p in filtered_data["paper_directories"]
            ),
            "has_pdf": any(
                "fulltext.pdf" in str(p) for p in filtered_data["paper_directories"]
            ),
            "has_supplementary": any(
                "supplementary" in str(p) for p in filtered_data["paper_directories"]
            ),
            "search_matches": search_results["summary"]["total_matches"],
        }

        return filtered_data

    # DRAFT: Figure extraction functionality - REMOVED FROM PUBLIC VIEW
    # This feature is under development and not ready for public use
    # ORIGINAL AUTHOR: petermr (Peter Murray-Rust) - July 5, 2025
    # EDITED: Assistant on 2024-12-19 for pygetpapers v2.0 - CURRENTLY IN DRAFT STATUS
    def extract_figures(self, output_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        DRAFT: Extract figures, captions, and thumbnails from papers.

        This feature is under development and not ready for public use.
        It has been removed from the public API.

        Args:
            output_data: Output from read_pygetpapers_output

        Returns:
            Dictionary containing figure information for each paper
        """
        logger.warning(
            "Figure extraction is currently in draft status and not available for public use."
        )
        return {
            "papers": {},
            "summary": {
                "total_figures": 0,
                "papers_with_figures": 0,
                "figure_types": {},
            },
        }

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
                xml_figures = self._extract_figures_from_xml(
                    xml_file, paper["directory"]
                )
                figures.extend(xml_figures)
            except Exception as e:
                logger.warning(f"Error extracting figures from XML {xml_file}: {e}")

        # Extract from supplementary files
        supp_files = list(paper_path.rglob("supplementary/*"))
        for supp_file in supp_files:
            if supp_file.is_file() and supp_file.suffix.lower() in [".xml", ".html"]:
                try:
                    supp_figures = self._extract_figures_from_supplementary(
                        supp_file, paper["directory"]
                    )
                    figures.extend(supp_figures)
                except Exception as e:
                    logger.warning(
                        f"Error extracting figures from supplementary {supp_file}: {e}"
                    )

        # Look for image files
        image_files = (
            list(paper_path.rglob("*.jpg"))
            + list(paper_path.rglob("*.jpeg"))
            + list(paper_path.rglob("*.png"))
            + list(paper_path.rglob("*.gif"))
            + list(paper_path.rglob("*.tiff"))
            + list(paper_path.rglob("*.tif"))
        )

        for image_file in image_files:
            try:
                image_figure = self._extract_image_figure(
                    image_file, paper["directory"]
                )
                if image_figure:
                    figures.append(image_figure)
            except Exception as e:
                logger.warning(f"Error processing image {image_file}: {e}")

        if figures:
            return {
                "paper_id": paper["directory"],
                "paper_title": paper.get("metadata", {}).get(
                    "title", paper["directory"]
                ),
                "figures": figures,
                "total_figures": len(figures),
            }

        return None

    def _extract_figures_from_xml(
        self, xml_file: Path, paper_id: str
    ) -> List[Dict[str, Any]]:
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
                "fig",
                "figure",
                "fig-group",
                "fig-group-wrap",
                "graphic",
                "media",
                "inline-graphic",
                "inline-media",
            ]

            # Search for figure elements
            for tag in figure_tags:
                try:
                    elements = root.xpath(f"//*[local-name()='{tag}']")
                    for i, element in enumerate(elements):
                        figure_info = self._parse_figure_element(
                            element, paper_id, f"{xml_file.stem}_fig_{i + 1}"
                        )
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
                        caption_info = self._parse_caption_element(
                            element, paper_id, f"{xml_file.stem}_caption_{i + 1}"
                        )
                        if caption_info:
                            figures.append(caption_info)
                except Exception as e:
                    logger.debug(f"Error searching for {tag} captions: {e}")

        except Exception as e:
            logger.warning(f"Error parsing XML {xml_file}: {e}")

        return figures

    def _parse_figure_element(
        self, element, paper_id: str, figure_id: str
    ) -> Optional[Dict[str, Any]]:
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
                    "figure_type": "xml_extracted",
                }

        except Exception as e:
            logger.debug(f"Error parsing figure element: {e}")

        return None

    def _parse_caption_element(
        self, element, paper_id: str, caption_id: str
    ) -> Optional[Dict[str, Any]]:
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
                    "figure_type": "caption_only",
                }

        except Exception as e:
            logger.debug(f"Error parsing caption element: {e}")

        return None

    def _extract_figures_from_supplementary(
        self, supp_file: Path, paper_id: str
    ) -> List[Dict[str, Any]]:
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
            if supp_file.suffix.lower() == ".xml":
                figures = self._extract_figures_from_xml(supp_file, paper_id)
            elif supp_file.suffix.lower() == ".html":
                figures = self._extract_figures_from_html(supp_file, paper_id)

        except Exception as e:
            logger.warning(
                f"Error extracting figures from supplementary {supp_file}: {e}"
            )

        return figures

    def _extract_figures_from_html(
        self, html_file: Path, paper_id: str
    ) -> List[Dict[str, Any]]:
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

            with open(html_file, "r", encoding="utf-8", errors="ignore") as f:
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
                    figures.append(
                        {
                            "figure_id": f"{html_file.stem}_fig_{i + 1}",
                            "paper_id": paper_id,
                            "caption": caption,
                            "label": "",
                            "title": "",
                            "image_src": img_src,
                            "source_file": str(html_file),
                            "figure_type": "html_extracted",
                        }
                    )

        except Exception as e:
            logger.warning(f"Error extracting figures from HTML {html_file}: {e}")

        return figures

    def _extract_image_figure(
        self, image_file: Path, paper_id: str
    ) -> Optional[Dict[str, Any]]:
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
                "thumbnail": thumbnail,
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
            import io

            from PIL import Image

            # Open and resize image
            with Image.open(image_file) as img:
                # Convert to RGB if necessary
                if img.mode in ("RGBA", "LA", "P"):
                    img = img.convert("RGB")

                # Resize to thumbnail
                img.thumbnail((200, 200), Image.Resampling.LANCZOS)

                # Convert to base64
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=85)
                img_str = base64.b64encode(buffer.getvalue()).decode()

                return f"data:image/jpeg;base64,{img_str}"

        except ImportError:
            logger.warning("PIL/Pillow not available for thumbnail creation")
            return None
        except Exception as e:
            logger.warning(f"Error creating thumbnail for {image_file}: {e}")
            return None

    # DRAFT: Figure table creation - REMOVED FROM PUBLIC VIEW
    # This feature is under development and not ready for public use
    # ORIGINAL AUTHOR: petermr (Peter Murray-Rust) - July 5, 2025
    # EDITED: Assistant on 2024-12-19 for pygetpapers v2.0 - CURRENTLY IN DRAFT STATUS
    def create_figures_table(
        self, figures_data: Dict[str, Any], table_id: str = "figures_table"
    ) -> str:
        """
        DRAFT: Create a table showing figures with thumbnails.

        This feature is under development and not ready for public use.
        It has been removed from the public API.

        Args:
            figures_data: Output from extract_figures
            table_id: Unique ID for the table

        Returns:
            HTML string with figures table
        """
        logger.warning(
            "Figure table creation is currently in draft status and not available for public use."
        )
        return "<p>Figure table creation is currently in draft status and not available for public use.</p>"

    # DRAFT: Figure summary table creation - REMOVED FROM PUBLIC VIEW
    # This feature is under development and not ready for public use
    # ORIGINAL AUTHOR: petermr (Peter Murray-Rust) - July 5, 2025
    # EDITED: Assistant on 2024-12-19 for pygetpapers v2.0 - CURRENTLY IN DRAFT STATUS
    def create_figures_summary_table(
        self, figures_data: Dict[str, Any], table_id: str = "figures_summary_table"
    ) -> str:
        """
        DRAFT: Create a summary table of figures by paper.

        This feature is under development and not ready for public use.
        It has been removed from the public API.

        Args:
            figures_data: Output from extract_figures
            table_id: Unique ID for the table

        Returns:
            HTML string with figures summary table
        """
        logger.warning(
            "Figure summary table creation is currently in draft status and not available for public use."
        )
        return "<p>Figure summary table creation is currently in draft status and not available for public use.</p>"

    # DRAFT: Corpus comparison table creation - REMOVED FROM PUBLIC VIEW
    # This feature is under development and not ready for public use
    # ORIGINAL AUTHOR: petermr (Peter Murray-Rust) - July 5, 2025
    # EDITED: Assistant on 2024-12-19 for pygetpapers v2.0 - CURRENTLY IN DRAFT STATUS
    def create_comparison_table(
        self, comparison_data: Dict[str, Any], table_id: str = "comparison_table"
    ) -> str:
        """
        DRAFT: Create a comparison table for multiple corpora.

        This feature is under development and not ready for public use.
        It has been removed from the public API.

        Args:
            comparison_data: Output from compare_corpora
            table_id: Unique ID for the table

        Returns:
            HTML string with comparison table
        """
        logger.warning(
            "Corpus comparison table creation is currently in draft status and not available for public use."
        )
        return "<p>Corpus comparison table creation is currently in draft status and not available for public use.</p>"

    # DRAFT: Corpus overlap table creation - REMOVED FROM PUBLIC VIEW
    # This feature is under development and not ready for public use
    # ORIGINAL AUTHOR: petermr (Peter Murray-Rust) - July 5, 2025
    # EDITED: Assistant on 2024-12-19 for pygetpapers v2.0 - CURRENTLY IN DRAFT STATUS
    def create_overlap_table(
        self, comparison_data: Dict[str, Any], table_id: str = "overlap_table"
    ) -> str:
        """
        DRAFT: Create an overlap analysis table.

        This feature is under development and not ready for public use.
        It has been removed from the public API.

        Args:
            comparison_data: Output from compare_corpora
            table_id: Unique ID for the table

        Returns:
            HTML string with overlap table
        """
        logger.warning(
            "Corpus overlap table creation is currently in draft status and not available for public use."
        )
        return "<p>Corpus overlap table creation is currently in draft status and not available for public use.</p>"

    def search_datatables_fields(
        self,
        output_data: Dict[str, Any],
        wordlist: List[str],
        search_fields: List[str] = None,
        case_sensitive: bool = False,
        min_hits: int = 1,
    ) -> Dict[str, Any]:
        """
        Search datatables fields with a wordlist and flag which ones have the highest hits.

        Args:
            output_data: Output from read_pygetpapers_output
            wordlist: List of words to search for
            search_fields: Fields to search in (default: all text fields)
            case_sensitive: Whether search should be case sensitive
            min_hits: Minimum number of hits to include in results

        Returns:
            Search results with field hit counts and flagged papers
        """
        if search_fields is None:
            search_fields = [
                "Title",
                "Authors",
                "Abstract",
                "Journal",
                "Keywords",
                "DOI",
                "PMID",
                "PMCID",
            ]

        search_results = {
            "wordlist": wordlist,
            "search_fields": search_fields,
            "case_sensitive": case_sensitive,
            "min_hits": min_hits,
            "field_hit_counts": {},
            "paper_hits": {},
            "flagged_papers": [],
            "summary": {},
        }

        # Initialize field hit counts
        for field in search_fields:
            search_results["field_hit_counts"][field] = {
                "total_hits": 0,
                "papers_with_hits": 0,
                "word_hits": {word: 0 for word in wordlist},
            }

        # Initialize paper hits
        for paper in output_data["paper_directories"]:
            search_results["paper_hits"][paper["directory"]] = {
                "total_hits": 0,
                "field_hits": {field: 0 for field in search_fields},
                "word_hits": {word: 0 for word in wordlist},
                "matches": [],
            }

        # Process each paper
        for paper in output_data["paper_directories"]:
            metadata = paper.get("metadata", {})
            paper_id = paper["directory"]

            # Extract field values
            field_values = {
                "Title": metadata.get("title", ""),
                "Authors": self._extract_authors_string(metadata),
                "Abstract": self._extract_abstract_string(metadata),
                "Journal": self._extract_journal_string(metadata),
                "Keywords": self._extract_keywords_string(metadata),
                "DOI": metadata.get("doi", ""),
                "PMID": metadata.get("pmid", ""),
                "PMCID": metadata.get("pmcid", ""),
            }

            # Search in each field
            for field in search_fields:
                if field in field_values:
                    field_text = str(field_values[field])

                    if not case_sensitive:
                        field_text = field_text.lower()
                        # Keep original words for dictionary keys, use lowercase for searching
                        search_words = [
                            (original_word, original_word.lower())
                            for original_word in wordlist
                        ]
                    else:
                        search_words = [(word, word) for word in wordlist]

                    # Count hits for each word
                    for original_word, search_word in search_words:
                        hit_count = field_text.count(search_word)
                        if hit_count > 0:
                            # Update field hit counts using original word case
                            search_results["field_hit_counts"][field]["word_hits"][
                                original_word
                            ] += hit_count
                            search_results["field_hit_counts"][field][
                                "total_hits"
                            ] += hit_count

                            # Update paper hit counts
                            search_results["paper_hits"][paper_id]["word_hits"][
                                original_word
                            ] += hit_count
                            search_results["paper_hits"][paper_id]["field_hits"][
                                field
                            ] += hit_count
                            search_results["paper_hits"][paper_id][
                                "total_hits"
                            ] += hit_count

                            # Add match details
                            search_results["paper_hits"][paper_id]["matches"].append(
                                {
                                    "field": field,
                                    "word": original_word,
                                    "count": hit_count,
                                    "value": (
                                        field_values[field][:100] + "..."
                                        if len(field_values[field]) > 100
                                        else field_values[field]
                                    ),
                                }
                            )

            # Check if paper meets minimum hit threshold
            if search_results["paper_hits"][paper_id]["total_hits"] >= min_hits:
                search_results["flagged_papers"].append(paper_id)

        # Update field summary
        for field in search_fields:
            papers_with_hits = sum(
                1
                for paper_hits in search_results["paper_hits"].values()
                if paper_hits["field_hits"][field] > 0
            )
            search_results["field_hit_counts"][field][
                "papers_with_hits"
            ] = papers_with_hits

        # Calculate overall summary
        total_papers = len(output_data["paper_directories"])
        flagged_count = len(search_results["flagged_papers"])

        search_results["summary"] = {
            "total_papers": total_papers,
            "flagged_papers": flagged_count,
            "flag_rate": flagged_count / total_papers if total_papers > 0 else 0,
            "total_hits": sum(
                paper_hits["total_hits"]
                for paper_hits in search_results["paper_hits"].values()
            ),
            "most_hit_fields": sorted(
                search_fields,
                key=lambda f: search_results["field_hit_counts"][f]["total_hits"],
                reverse=True,
            ),
            "most_hit_words": sorted(
                wordlist,
                key=lambda w: sum(
                    search_results["field_hit_counts"][f]["word_hits"][w]
                    for f in search_fields
                ),
                reverse=True,
            ),
        }

        return search_results

    def _extract_authors_string(self, metadata: Dict[str, Any]) -> str:
        """Extract authors as a string from metadata."""
        if "authorString" in metadata:
            return metadata["authorString"]
        elif "authors" in metadata:
            return metadata["authors"]
        elif "authorList" in metadata and "author" in metadata["authorList"]:
            # Europe PMC format
            author_list = []
            for author in metadata["authorList"]["author"]:
                if "fullName" in author:
                    author_list.append(author["fullName"])
            return ", ".join(author_list) if author_list else ""
        return ""

    def _extract_journal_string(self, metadata: Dict[str, Any]) -> str:
        """Extract journal name as a string from metadata."""
        if "journalInfo" in metadata and "journal" in metadata["journalInfo"]:
            return metadata["journalInfo"]["journal"].get("title", "")
        elif "journalTitle" in metadata:
            return metadata["journalTitle"]
        elif "journal" in metadata:
            return metadata["journal"]
        return ""

    def _extract_keywords_string(self, metadata: Dict[str, Any]) -> str:
        """Extract keywords as a string from metadata."""
        keywords = metadata.get("keywords", [])
        if isinstance(keywords, list):
            return ", ".join(keywords)
        elif isinstance(keywords, str):
            return keywords
        return ""

    def _extract_abstract_string(self, metadata: Dict[str, Any]) -> str:
        """
        Extract abstract as a string from metadata.

        Handles multiple abstract field names and formats:
        - abstract
        - abstractText
        - description
        - summary
        - Europe PMC format: abstractText
        - Crossref format: abstract
        - ArXiv format: summary

        Args:
            metadata: Paper metadata dictionary

        Returns:
            Abstract text string or empty string if not found
        """
        # Try different abstract field names
        abstract_fields = [
            "abstract",
            "abstractText",
            "description",
            "summary",
            "content",
        ]

        for field in abstract_fields:
            if field in metadata:
                abstract = metadata[field]
                if isinstance(abstract, str) and abstract.strip():
                    return abstract.strip()
                elif isinstance(abstract, list):
                    # Handle list format (e.g., multiple paragraphs)
                    return " ".join(
                        str(item).strip() for item in abstract if str(item).strip()
                    )

        # Try nested structures (Europe PMC format)
        if "abstractText" in metadata:
            abstract_text = metadata["abstractText"]
            if isinstance(abstract_text, str) and abstract_text.strip():
                return abstract_text.strip()

        # Try journal info structure
        if "journalInfo" in metadata and "journal" in metadata["journalInfo"]:
            journal_info = metadata["journalInfo"]["journal"]
            if "abstract" in journal_info:
                abstract = journal_info["abstract"]
                if isinstance(abstract, str) and abstract.strip():
                    return abstract.strip()

        return ""

    def extract_abstracts(self, output_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract abstracts from all papers in the output data.

        Args:
            output_data: Output from read_pygetpapers_output

        Returns:
            Dictionary with abstract extraction results
        """
        abstracts_data = {
            "total_papers": len(output_data["paper_directories"]),
            "papers_with_abstracts": 0,
            "papers_without_abstracts": 0,
            "abstract_lengths": {},
            "abstract_sources": {},
            "papers": {},
        }

        for paper in output_data["paper_directories"]:
            paper_id = paper["directory"]
            metadata = paper.get("metadata", {})

            # Extract abstract
            abstract = self._extract_abstract_string(metadata)

            # Determine abstract source
            abstract_source = "none"
            if "abstract" in metadata and metadata["abstract"]:
                abstract_source = "abstract"
            elif "abstractText" in metadata and metadata["abstractText"]:
                abstract_source = "abstractText"
            elif "description" in metadata and metadata["description"]:
                abstract_source = "description"
            elif "summary" in metadata and metadata["summary"]:
                abstract_source = "summary"
            elif "content" in metadata and metadata["content"]:
                abstract_source = "content"

            # Store paper abstract data
            abstracts_data["papers"][paper_id] = {
                "has_abstract": bool(abstract),
                "abstract": abstract,
                "abstract_length": len(abstract) if abstract else 0,
                "abstract_source": abstract_source,
                "title": metadata.get("title", ""),
                "authors": self._extract_authors_string(metadata),
                "journal": self._extract_journal_string(metadata),
            }

            # Update counts
            if abstract:
                abstracts_data["papers_with_abstracts"] += 1
                abstracts_data["abstract_lengths"][paper_id] = len(abstract)
                abstracts_data["abstract_sources"][paper_id] = abstract_source
            else:
                abstracts_data["papers_without_abstracts"] += 1

        # Calculate statistics
        abstracts_data["abstract_coverage"] = (
            abstracts_data["papers_with_abstracts"] / abstracts_data["total_papers"]
            if abstracts_data["total_papers"] > 0
            else 0
        )

        # Calculate average abstract length
        if abstracts_data["abstract_lengths"]:
            avg_length = sum(abstracts_data["abstract_lengths"].values()) / len(
                abstracts_data["abstract_lengths"]
            )
            abstracts_data["average_abstract_length"] = round(avg_length, 2)
        else:
            abstracts_data["average_abstract_length"] = 0

        return abstracts_data

    def create_abstracts_table(
        self, abstracts_data: Dict[str, Any], table_id: str = "abstracts_table"
    ) -> str:
        """
        Create an interactive HTML table showing abstract information.

        Args:
            abstracts_data: Output from extract_abstracts
            table_id: Unique ID for the table

        Returns:
            HTML string with interactive table
        """
        if not abstracts_data["papers"]:
            return "<p>No papers found for abstract analysis.</p>"

        # Prepare table data
        table_data = []
        for paper_id, paper_data in abstracts_data["papers"].items():
            abstract = paper_data["abstract"]
            if not abstract:
                abstract = "No abstract available"

            # Truncate abstract for display
            display_abstract = (
                abstract[:200] + "..." if len(abstract) > 200 else abstract
            )

            row = {
                "Paper ID": paper_id,
                "Title": (
                    paper_data["title"][:80] + "..."
                    if len(paper_data["title"]) > 80
                    else paper_data["title"]
                ),
                "Authors": (
                    paper_data["authors"][:50] + "..."
                    if len(paper_data["authors"]) > 50
                    else paper_data["authors"]
                ),
                "Journal": (
                    paper_data["journal"][:40] + "..."
                    if len(paper_data["journal"]) > 40
                    else paper_data["journal"]
                ),
                "Abstract": display_abstract,
                "Length": paper_data["abstract_length"],
                "Source": paper_data["abstract_source"],
                "Has Abstract": "✅" if paper_data["has_abstract"] else "❌",
            }
            table_data.append(row)

        # Sort by abstract length (descending)
        table_data.sort(key=lambda x: x["Length"], reverse=True)

        # Create HTML table with tooltips
        column_tooltips = {
            "Paper ID": "Unique paper identifier",
            "Title": "Paper title (truncated if >80 characters)",
            "Authors": "Author names (truncated if >50 characters)",
            "Journal": "Journal name (truncated if >40 characters)",
            "Abstract": "Paper abstract (truncated if >200 characters)",
            "Length": "Number of characters in abstract",
            "Source": "Source field used for abstract extraction",
            "Has Abstract": "Whether paper has an abstract",
        }

        try:
            html_table = self._create_datatable_with_tooltips(
                dict_by_id=OrderedDict({row["Paper ID"]: row for row in table_data}),
                table_id=table_id,
                column_tooltips=column_tooltips,
            )

            return html_table

        except Exception as e:
            logger.error(f"Error creating abstracts table: {e}")
            return self._create_simple_table(table_data)

    def create_abstracts_summary_table(
        self, abstracts_data: Dict[str, Any], table_id: str = "abstracts_summary_table"
    ) -> str:
        """
        Create a summary table showing abstract statistics.

        Args:
            abstracts_data: Output from extract_abstracts
            table_id: Unique ID for the table

        Returns:
            HTML string with summary table
        """
        # Prepare summary data
        summary_data = [
            {
                "Metric": "Total Papers",
                "Value": abstracts_data["total_papers"],
                "Description": "Total number of papers analyzed",
            },
            {
                "Metric": "Papers with Abstracts",
                "Value": abstracts_data["papers_with_abstracts"],
                "Description": "Number of papers that have abstracts",
            },
            {
                "Metric": "Papers without Abstracts",
                "Value": abstracts_data["papers_without_abstracts"],
                "Description": "Number of papers missing abstracts",
            },
            {
                "Metric": "Abstract Coverage",
                "Value": f"{abstracts_data['abstract_coverage']:.1%}",
                "Description": "Percentage of papers with abstracts",
            },
            {
                "Metric": "Average Abstract Length",
                "Value": f"{abstracts_data['average_abstract_length']} characters",
                "Description": "Average number of characters per abstract",
            },
        ]

        # Create HTML table
        try:
            html_table = self._create_datatable_with_tooltips(
                dict_by_id=OrderedDict({row["Metric"]: row for row in summary_data}),
                table_id=table_id,
                column_tooltips={
                    "Metric": "Statistical measure",
                    "Value": "Calculated value",
                    "Description": "Explanation of the metric",
                },
            )

            return html_table

        except Exception as e:
            logger.error(f"Error creating abstracts summary table: {e}")
            return self._create_simple_table(summary_data)

    def create_wordlist_search_table(
        self, search_results: Dict[str, Any], table_id: str = "wordlist_search_table"
    ) -> str:
        """
        Create an interactive HTML table showing wordlist search results.

        Args:
            search_results: Results from search_datatables_fields
            table_id: Unique ID for the table

        Returns:
            HTML string with interactive table
        """
        if not search_results["flagged_papers"]:
            return "<p>No papers found matching the wordlist criteria.</p>"

        # Prepare table data
        table_data = []
        for paper_id in search_results["flagged_papers"]:
            paper_hits = search_results["paper_hits"][paper_id]

            # Create field hit summary
            field_summary = []
            for field in search_results["search_fields"]:
                hits = paper_hits["field_hits"][field]
                if hits > 0:
                    field_summary.append(f"{field}: {hits}")

            # Create word hit summary
            word_summary = []
            for word in search_results["wordlist"]:
                hits = paper_hits["word_hits"][word]
                if hits > 0:
                    word_summary.append(f"{word}: {hits}")

            # Create match details
            match_details = []
            for match in paper_hits["matches"][:5]:  # Show first 5 matches
                match_details.append(
                    f"{match['field']} ({match['word']}): {match['count']} - {match['value']}"
                )
            if len(paper_hits["matches"]) > 5:
                match_details.append(
                    f"... and {len(paper_hits['matches']) - 5} more matches"
                )

            row = {
                "Paper ID": paper_id,
                "Total Hits": paper_hits["total_hits"],
                "Field Hits": "<br>".join(field_summary),
                "Word Hits": "<br>".join(word_summary),
                "Top Matches": "<br>".join(match_details),
            }
            table_data.append(row)

        # Sort by total hits (descending)
        table_data.sort(key=lambda x: x["Total Hits"], reverse=True)

        # Create HTML table with tooltips
        column_tooltips = {
            "Paper ID": "Unique paper identifier",
            "Total Hits": "Total number of word matches across all fields",
            "Field Hits": "Breakdown of hits by field",
            "Word Hits": "Breakdown of hits by word",
            "Top Matches": "Detailed match information with context",
        }

        try:
            html_table = self._create_datatable_with_tooltips(
                dict_by_id=OrderedDict({row["Paper ID"]: row for row in table_data}),
                table_id=table_id,
                column_tooltips=column_tooltips,
            )

            return html_table

        except Exception as e:
            logger.error(f"Error creating wordlist search table: {e}")
            return self._create_simple_table(table_data)

    def create_field_hit_summary_table(
        self, search_results: Dict[str, Any], table_id: str = "field_hit_summary_table"
    ) -> str:
        """
        Create a summary table showing hit counts by field.

        Args:
            search_results: Results from search_datatables_fields
            table_id: Unique ID for the table

        Returns:
            HTML string with summary table
        """
        # Prepare table data
        table_data = []
        for field in search_results["search_fields"]:
            field_stats = search_results["field_hit_counts"][field]

            # Create word breakdown
            word_breakdown = []
            for word in search_results["wordlist"]:
                hits = field_stats["word_hits"][word]
                if hits > 0:
                    word_breakdown.append(f"{word}: {hits}")

            row = {
                "Field": field,
                "Total Hits": field_stats["total_hits"],
                "Papers with Hits": field_stats["papers_with_hits"],
                "Word Breakdown": (
                    "<br>".join(word_breakdown) if word_breakdown else "No hits"
                ),
            }
            table_data.append(row)

        # Sort by total hits (descending)
        table_data.sort(key=lambda x: x["Total Hits"], reverse=True)

        # Create HTML table with tooltips
        column_tooltips = {
            "Field": "Datatables field name",
            "Total Hits": "Total number of word matches in this field",
            "Papers with Hits": "Number of papers with matches in this field",
            "Word Breakdown": "Breakdown of hits by individual words",
        }

        try:
            html_table = self._create_datatable_with_tooltips(
                dict_by_id=OrderedDict({row["Field"]: row for row in table_data}),
                table_id=table_id,
                column_tooltips=column_tooltips,
            )

            return html_table

        except Exception as e:
            logger.error(f"Error creating field hit summary table: {e}")
            return self._create_simple_table(table_data)

    def save_datatables_to_output(
        self,
        output_data: Dict[str, Any],
        output_dir: str = None,
        save_css_file: bool = True,
    ) -> Dict[str, str]:
        """
        Save datatables HTML files to the output directory.

        Args:
            output_data: Output from read_pygetpapers_output
            output_dir: Output directory path (defaults to output_data["output_dir"])
            save_css_file: Whether to save CSS as a separate file

        Returns:
            Dictionary mapping table names to their file paths
        """
        if output_dir is None:
            output_dir = output_data["output_dir"]

        output_path = Path(output_dir)
        if not output_path.exists():
            raise FileNotFoundError(f"Output directory not found: {output_dir}")

        saved_files = {}

        try:
            # Save CSS file if requested
            if save_css_file:
                css_file = output_path / "datatables.css"
                with open(css_file, "w", encoding="utf-8") as f:
                    f.write(DATATABLES_CSS)
                saved_files["css"] = str(css_file)

            # Create papers table
            papers_html = self.create_papers_table(output_data, "papers_table")
            papers_file = output_path / "papers_datatable.html"
            with open(papers_file, "w", encoding="utf-8") as f:
                f.write(papers_html)
            saved_files["papers"] = str(papers_file)

            # Create metadata table
            metadata_html = self.create_metadata_table(output_data, "metadata_table")
            metadata_file = output_path / "metadata_datatable.html"
            with open(metadata_file, "w", encoding="utf-8") as f:
                f.write(metadata_html)
            saved_files["metadata"] = str(metadata_file)

            # Create summary table
            summary_html = self.create_summary_table(output_data, "summary_table")
            summary_file = output_path / "summary_datatable.html"
            with open(summary_file, "w", encoding="utf-8") as f:
                f.write(summary_html)
            saved_files["summary"] = str(summary_file)

            # Create index file that links to all tables
            index_html = self._create_datatables_index(
                saved_files, output_data, use_external_css=save_css_file
            )
            index_file = output_path / "datatables_index.html"
            with open(index_file, "w", encoding="utf-8") as f:
                f.write(index_html)
            saved_files["index"] = str(index_file)

            logger.info(
                f"Saved {len(saved_files)} datatables HTML files to {output_dir}"
            )

        except Exception as e:
            logger.error(f"Error saving datatables: {e}")
            raise

        return saved_files

    def _create_datatables_index(
        self,
        saved_files: Dict[str, str],
        output_data: Dict[str, Any],
        use_external_css: bool = False,
    ) -> str:
        """
        Create an index HTML file that links to all datatables.

        Args:
            saved_files: Dictionary of saved file paths
            output_data: Output data for summary information
            use_external_css: Whether to link to external CSS file

        Returns:
            HTML string for the index page
        """
        summary = output_data["summary"]

        # Choose CSS source
        if use_external_css and "css" in saved_files:
            css_content = (
                '<link rel="stylesheet" type="text/css" href="datatables.css">'
            )
        else:
            css_content = f"<style>\n{DATATABLES_CSS}\n</style>"

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>pygetpapers Datatables - {Path(output_data['output_dir']).name}</title>
            {css_content}
        </head>
        <body>
            <div class="header">
                <h1>pygetpapers Datatables</h1>
                <p>Interactive data tables for corpus:
                   <strong>{Path(output_data['output_dir']).name}</strong></p>

                <div class="stats">
                    <div class="stat">
                        <div class="stat-number">{summary['total_papers']}</div>
                        <div class="stat-label">Total Papers</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">{len(summary['metadata_files_found'])}</div>
                        <div class="stat-label">Metadata Files</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">{'✅' if summary['has_xml'] else '❌'}</div>
                        <div class="stat-label">XML Files</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">{'✅' if summary['has_pdf'] else '❌'}</div>
                        <div class="stat-label">PDF Files</div>
                    </div>
                </div>
            </div>

            <div class="table-links">
                <div class="table-card">
                    <h3>📄 Papers Table</h3>
                    <p>Interactive table showing all papers with metadata, file availability,
                       and links.</p>
                    <a href="papers_datatable.html" class="table-link">Open Papers Table</a>
                </div>

                <div class="table-card">
                    <h3>📊 Metadata Table</h3>
                    <p>Overview of metadata files and their contents.</p>
                    <a href="metadata_datatable.html" class="table-link">Open Metadata Table</a>
                </div>

                <div class="table-card">
                    <h3>📈 Summary Table</h3>
                    <p>Corpus statistics and summary information.</p>
                    <a href="summary_datatable.html" class="table-link">Open Summary Table</a>
                </div>
            </div>

            <div style="margin-top: 40px; padding: 20px; background-color: #f8f9fa;
                        border-radius: 5px;">
                <h3>📝 Notes</h3>
                <ul>
                    <li>All tables include search, pagination, and sorting functionality</li>
                    <li>Tables are responsive and work on mobile devices</li>
                    <li>DOI links open in new tabs</li>
                    <li>Checkboxes allow for paper selection (functionality can be extended)</li>
                </ul>
            </div>
        </body>
        </html>
        """

        return html
