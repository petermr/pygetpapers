"""
Simple HTML Converter for Pygetpapers

This module provides basic XML to HTML conversion functionality
without requiring external JATS4R dependencies.
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import lxml.etree as ET

logger = logging.getLogger(__name__)


class SimpleHTMLConverter:
    """
    Simple XML to HTML converter for JATS documents.
    """

    def __init__(self):
        self.namespaces = {
            "jats": "http://jats.nlm.nih.gov",
            "xlink": "http://www.w3.org/1999/xlink",
        }

    def convert_xml_to_html(
        self, xml_file: str, output_file: str = None
    ) -> Tuple[bool, str]:
        """
        Convert JATS XML file to HTML.

        Args:
            xml_file: Path to input XML file
            output_file: Path to output HTML file (optional)

        Returns:
            Tuple of (success, output_file_path or error_message)
        """
        try:
            xml_path = Path(xml_file)
            if not xml_path.exists():
                return False, f"XML file not found: {xml_file}"

            # Generate output filename if not provided
            if output_file is None:
                output_file = str(xml_path.with_name(f"{xml_path.stem}.xml.html"))

            # Parse XML
            tree = ET.parse(xml_path)
            root = tree.getroot()

            # Convert to HTML
            html_content = self._convert_jats_to_html(root)

            # Write HTML file
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(html_content)

            logger.info(f"Converted {xml_file} to {output_file}")
            return True, output_file

        except Exception as e:
            logger.error(f"Error converting XML to HTML: {e}")
            return False, f"Conversion error: {str(e)}"

    def _convert_jats_to_html(self, root) -> str:
        """Convert JATS XML root element to HTML."""

        # Extract basic metadata
        title = self._extract_title(root)
        authors = self._extract_authors(root)
        abstract = self._extract_abstract(root)
        body = self._extract_body(root)
        references = self._extract_references(root)

        # Build HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 40px; }}
        h1 {{ color: #333; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        h3 {{ color: #666; }}
        .authors {{ color: #777; font-style: italic; margin: 20px 0; }}
        .abstract {{ background: #f9f9f9; padding: 20px; border-left: 4px solid #007acc; margin: 20px 0; }}
        .section {{ margin: 20px 0; }}
        .reference {{ margin: 10px 0; padding: 10px; background: #f5f5f5; border-radius: 5px; }}
        .figure {{ text-align: center; margin: 20px 0; }}
        .figure img {{ max-width: 100%; height: auto; }}
        .table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        .table th, .table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        .table th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <div class="authors">{authors}</div>
    
    <div class="abstract">
        <h2>Abstract</h2>
        {abstract}
    </div>
    
    <div class="body">
        {body}
    </div>
    
    {references}
    
    <hr>
    <p><em>Converted by Pygetpapers Simple HTML Converter</em></p>
</body>
</html>"""

        return html

    def _extract_title(self, root) -> str:
        """Extract document title."""
        try:
            # Try different title elements
            title_elem = root.find(".//jats:article-title", self.namespaces)
            if title_elem is None:
                title_elem = root.find(".//title")
            if title_elem is None:
                title_elem = root.find(".//article-title")

            if title_elem is not None:
                return self._get_element_text(title_elem)
        except Exception as e:
            logger.debug(f"Error extracting title: {e}")

        return "Document Title"

    def _extract_authors(self, root) -> str:
        """Extract author information."""
        try:
            authors = []
            author_elems = root.findall(
                './/jats:contrib[@contrib-type="author"]', self.namespaces
            )

            for author_elem in author_elems:
                name_elem = author_elem.find(".//jats:name", self.namespaces)
                if name_elem is not None:
                    given_name = name_elem.find(".//jats:given-names", self.namespaces)
                    surname = name_elem.find(".//jats:surname", self.namespaces)

                    if given_name is not None and surname is not None:
                        authors.append(
                            f"{self._get_element_text(given_name)} {self._get_element_text(surname)}"
                        )
                    elif surname is not None:
                        authors.append(self._get_element_text(surname))

            if authors:
                return ", ".join(authors)
        except Exception as e:
            logger.debug(f"Error extracting authors: {e}")

        return "Authors"

    def _extract_abstract(self, root) -> str:
        """Extract abstract text."""
        try:
            abstract_elem = root.find(".//jats:abstract", self.namespaces)
            if abstract_elem is None:
                abstract_elem = root.find(".//abstract")

            if abstract_elem is not None:
                return self._get_element_text(abstract_elem)
        except Exception as e:
            logger.debug(f"Error extracting abstract: {e}")

        return "Abstract not available."

    def _extract_body(self, root) -> str:
        """Extract body content."""
        try:
            body_elem = root.find(".//jats:body", self.namespaces)
            if body_elem is None:
                body_elem = root.find(".//body")

            if body_elem is not None:
                return self._convert_body_content(body_elem)
        except Exception as e:
            logger.debug(f"Error extracting body: {e}")

        return "<p>Body content not available.</p>"

    def _extract_references(self, root) -> str:
        """Extract references section."""
        try:
            ref_list_elem = root.find(".//jats:ref-list", self.namespaces)
            if ref_list_elem is None:
                ref_list_elem = root.find(".//ref-list")

            if ref_list_elem is not None:
                return self._convert_references(ref_list_elem)
        except Exception as e:
            logger.debug(f"Error extracting references: {e}")

        return ""

    def _convert_body_content(self, body_elem) -> str:
        """Convert body content to HTML."""
        html_parts = []

        for child in body_elem:
            tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag

            if tag == "sec":
                html_parts.append(self._convert_section(child))
            elif tag == "p":
                html_parts.append(f"<p>{self._get_element_text(child)}</p>")
            elif tag == "fig":
                html_parts.append(self._convert_figure(child))
            elif tag == "table-wrap":
                html_parts.append(self._convert_table(child))
            elif tag == "list":
                html_parts.append(self._convert_list(child))

        return "\n".join(html_parts)

    def _convert_section(self, section_elem) -> str:
        """Convert a section element to HTML."""
        html_parts = []

        # Extract section title
        title_elem = section_elem.find(".//jats:title", self.namespaces)
        if title_elem is None:
            title_elem = section_elem.find(".//title")

        if title_elem is not None:
            title_text = self._get_element_text(title_elem)
            html_parts.append(f"<h2>{title_text}</h2>")

        # Convert section content
        for child in section_elem:
            if child.tag.endswith("title"):
                continue  # Already handled

            tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag

            if tag == "p":
                html_parts.append(f"<p>{self._get_element_text(child)}</p>")
            elif tag == "sec":
                html_parts.append(self._convert_section(child))
            elif tag == "fig":
                html_parts.append(self._convert_figure(child))
            elif tag == "table-wrap":
                html_parts.append(self._convert_table(child))
            elif tag == "list":
                html_parts.append(self._convert_list(child))

        return f'<div class="section">{"".join(html_parts)}</div>'

    def _convert_figure(self, fig_elem) -> str:
        """Convert a figure element to HTML."""
        html_parts = []

        # Extract figure caption
        caption_elem = fig_elem.find(".//jats:caption", self.namespaces)
        if caption_elem is None:
            caption_elem = fig_elem.find(".//caption")

        caption_text = ""
        if caption_elem is not None:
            caption_text = self._get_element_text(caption_elem)

        # Extract figure label
        label_elem = fig_elem.find(".//jats:label", self.namespaces)
        if label_elem is None:
            label_elem = fig_elem.find(".//label")

        label_text = ""
        if label_elem is not None:
            label_text = self._get_element_text(label_elem)

        html_parts.append('<div class="figure">')
        if label_text:
            html_parts.append(f"<strong>{label_text}</strong><br>")
        if caption_text:
            html_parts.append(f"<em>{caption_text}</em>")
        html_parts.append("</div>")

        return "".join(html_parts)

    def _convert_table(self, table_elem) -> str:
        """Convert a table element to HTML."""
        try:
            table = table_elem.find(".//jats:table", self.namespaces)
            if table is None:
                table = table_elem.find(".//table")

            if table is not None:
                return self._convert_table_content(table)
        except Exception as e:
            logger.debug(f"Error converting table: {e}")

        return "<p>Table content not available.</p>"

    def _convert_table_content(self, table_elem) -> str:
        """Convert table content to HTML."""
        html_parts = ['<table class="table">']

        # Process table rows
        for row in table_elem.findall(".//jats:row", self.namespaces):
            html_parts.append("<tr>")
            for cell in row.findall(".//jats:cell", self.namespaces):
                cell_text = self._get_element_text(cell)
                html_parts.append(f"<td>{cell_text}</td>")
            html_parts.append("</tr>")

        html_parts.append("</table>")
        return "".join(html_parts)

    def _convert_list(self, list_elem) -> str:
        """Convert a list element to HTML."""
        html_parts = ["<ul>"]

        for item in list_elem.findall(".//jats:list-item", self.namespaces):
            item_text = self._get_element_text(item)
            html_parts.append(f"<li>{item_text}</li>")

        html_parts.append("</ul>")
        return "".join(html_parts)

    def _convert_references(self, ref_list_elem) -> str:
        """Convert references to HTML."""
        html_parts = ["<h2>References</h2>"]

        for ref in ref_list_elem.findall(".//jats:ref", self.namespaces):
            ref_text = self._get_element_text(ref)
            html_parts.append(f'<div class="reference">{ref_text}</div>')

        return "".join(html_parts)

    def _get_element_text(self, elem) -> str:
        """Extract text content from an element."""
        if elem is None:
            return ""

        # Get text content
        text_parts = []
        if elem.text:
            text_parts.append(elem.text.strip())

        # Get text from child elements
        for child in elem:
            if child.text:
                text_parts.append(child.text.strip())
            if child.tail:
                text_parts.append(child.tail.strip())

        return " ".join(text_parts).strip()

    def convert_corpus_xml_files(self, corpus_dir: str) -> Dict[str, List[str]]:
        """
        Convert all XML files in a corpus directory to HTML.

        Args:
            corpus_dir: Path to corpus directory

        Returns:
            Dictionary with conversion results
        """
        results = {"successful": [], "failed": [], "skipped": []}

        try:
            corpus_path = Path(corpus_dir)
            if not corpus_path.exists():
                results["failed"].append(f"Corpus directory not found: {corpus_dir}")
                return results

            # Find all XML files
            xml_files = list(corpus_path.rglob("*.xml"))

            if not xml_files:
                results["skipped"].append("No XML files found in corpus")
                return results

            logger.info(f"Found {len(xml_files)} XML files to convert")

            for xml_file in xml_files:
                try:
                    # Create HTML file as sibling to XML file with .xml.html naming
                    html_file = xml_file.with_name(f"{xml_file.stem}.xml.html")

                    # Convert file
                    success, result = self.convert_xml_to_html(
                        str(xml_file), str(html_file)
                    )

                    if success:
                        results["successful"].append(str(html_file))
                        logger.info(f"Converted: {xml_file.name} -> {html_file.name}")
                    else:
                        results["failed"].append(f"{xml_file.name}: {result}")

                except Exception as e:
                    results["failed"].append(f"{xml_file.name}: {str(e)}")

            logger.info(
                f"Conversion complete: {len(results['successful'])} successful, "
                f"{len(results['failed'])} failed, {len(results['skipped'])} skipped"
            )

        except Exception as e:
            results["failed"].append(f"Corpus conversion error: {str(e)}")

        return results
