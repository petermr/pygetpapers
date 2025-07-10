"""
Simple HTML Converter for Pygetpapers

This module provides XML to HTML conversion functionality
that preserves document structure using semantic class names.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import lxml.etree as ET

logger = logging.getLogger(__name__)


class SimpleHTMLConverter:
    """Convert XML documents to HTML with semantic class names."""

    def __init__(self):
        """Initialize the converter."""
        self.namespaces = {
            'jats': 'http://jats.nlm.nih.gov',
            'xlink': 'http://www.w3.org/1999/xlink'
        }

    def convert_xml_to_html(
        self, xml_file: str, output_file: str = None
    ) -> Tuple[bool, str]:
        """
        Convert an XML file to HTML.

        Args:
            xml_file: Path to input XML file
            output_file: Path to output HTML file (optional)

        Returns:
            Tuple of (success, result_message)
        """
        try:
            # Parse XML
            tree = ET.parse(xml_file)
            root = tree.getroot()

            # Generate HTML
            html_content = self._convert_xml_to_html(root)

            # Create output filename if not provided
            if output_file is None:
                xml_path = Path(xml_file)
                output_file = str(xml_path.with_suffix('.xml.html'))

            # Write HTML file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)

            return True, f"Successfully converted to {output_file}"

        except Exception as e:
            error_msg = f"Error converting {xml_file}: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def _convert_xml_to_html(self, root) -> str:
        """Convert XML root element to HTML."""
        # Create HTML document structure
        html_parts = [
            '<!DOCTYPE html>',
            '<html lang="en">',
            '<head>',
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            '<title>Converted Document</title>',
            '<style>',
            'body { font-family: Arial, sans-serif; line-height: 1.6; margin: 20px; }',
            '.xml { margin: 0; padding: 0; }',
            '.xml > * { margin: 10px 0; }',
            '.xml > * > * { margin: 5px 0; }',
            '.title { font-size: 1.5em; font-weight: bold; }',
            '.section { margin: 20px 0; }',
            '.section-title { font-size: 1.2em; font-weight: bold; margin: 10px 0; }',
            '.paragraph { margin: 10px 0; }',
            '.figure { margin: 20px 0; padding: 10px; border: 1px solid #ccc; }',
            '.figure-label { font-weight: bold; }',
            '.figure-caption { font-style: italic; }',
            '.table { margin: 20px 0; }',
            '.table table { border-collapse: collapse; width: 100%; }',
            '.table th, .table td { border: 1px solid #ddd; padding: 8px; text-align: left; }',
            '.table th { background-color: #f2f2f2; }',
            '.list { margin: 10px 0; }',
            '.list-item { margin: 5px 0; }',
            '.reference { margin: 10px 0; padding: 5px; background-color: #f9f9f9; }',
            '.bold { font-weight: bold; }',
            '.italic { font-style: italic; }',
            '.superscript { vertical-align: super; font-size: smaller; }',
            '.subscript { vertical-align: sub; font-size: smaller; }',
            '.link { color: #0066cc; text-decoration: none; }',
            '.link:hover { text-decoration: underline; }',
            '</style>',
            '</head>',
            '<body>',
            '<div class="xml">'
        ]

        # Convert root element
        html_parts.append(self._convert_element(root))

        # Close HTML structure
        html_parts.extend([
            '</div>',
            '</body>',
            '</html>'
        ])

        return '\n'.join(html_parts)

    def _convert_element(self, elem) -> str:
        """Convert an XML element to HTML with semantic class names."""
        if elem is None:
            return ""

        # Get element tag name (remove namespace prefix)
        try:
            tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
        except (AttributeError, TypeError):
            # Fallback if tag is not a string
            tag = "unknown"

        # Handle text-only elements
        try:
            if elem.text and not list(elem):
                return self._format_text_content(elem.text, tag)
        except (TypeError, AttributeError):
            # If iteration fails, treat as text-only
            if elem.text:
                return self._format_text_content(elem.text, tag)

        # Handle special elements
        if tag in ['title', 'article-title', 'book-title']:
            return f'<h1 class="{tag}">{self._get_element_text(elem)}</h1>'
        elif tag in ['sec', 'section']:
            return self._convert_section(elem)
        elif tag in ['p', 'paragraph']:
            return f'<p class="{tag}">{self._get_element_text(elem)}</p>'
        elif tag in ['fig', 'figure']:
            return self._convert_figure(elem)
        elif tag in ['table-wrap', 'table']:
            return self._convert_table(elem)
        elif tag in ['list']:
            return self._convert_list(elem)
        elif tag in ['ref-list', 'references']:
            return self._convert_references(elem)
        elif tag in ['abstract']:
            return f'<div class="{tag}"><h2>Abstract</h2><p>{self._get_element_text(elem)}</p></div>'
        elif tag in ['body']:
            return f'<div class="{tag}">{self._convert_children(elem)}</div>'
        elif tag in ['front', 'back']:
            return f'<div class="{tag}">{self._convert_children(elem)}</div>'
        elif tag in ['article', 'book']:
            return f'<div class="{tag}">{self._convert_children(elem)}</div>'

        # Default: convert to div with class name
        return f'<div class="{tag}">{self._convert_children(elem)}</div>'

    def _convert_children(self, elem) -> str:
        """Convert all child elements of an element."""
        html_parts = []
        
        # Add text content before first child
        if elem.text and elem.text.strip():
            html_parts.append(self._format_text_content(elem.text.strip()))

        # Convert child elements
        try:
            for child in elem:
                html_parts.append(self._convert_element(child))
                
                # Add text content after child
                if child.tail and child.tail.strip():
                    html_parts.append(self._format_text_content(child.tail.strip()))
        except (TypeError, AttributeError) as e:
            # If iteration fails, log and continue
            logger.warning(f"Error iterating over element children: {e}")
            # Try to get text content as fallback
            if elem.text:
                html_parts.append(self._format_text_content(elem.text))

        return ''.join(html_parts)

    def _convert_section(self, section_elem) -> str:
        """Convert a section element to HTML."""
        html_parts = ['<div class="section">']

        # Extract section title
        title_elem = section_elem.find(".//jats:title", self.namespaces)
        if title_elem is None:
            title_elem = section_elem.find(".//title")

        if title_elem is not None:
            title_text = self._get_element_text(title_elem)
            html_parts.append(f'<h2 class="section-title">{title_text}</h2>')

        # Convert section content
        for child in section_elem:
            if child.tag.endswith("title"):
                continue  # Already handled

            html_parts.append(self._convert_element(child))

        html_parts.append('</div>')
        return ''.join(html_parts)

    def _convert_figure(self, fig_elem) -> str:
        """Convert a figure element to HTML."""
        html_parts = ['<div class="figure">']

        # Extract figure label
        label_elem = fig_elem.find(".//jats:label", self.namespaces)
        if label_elem is None:
            label_elem = fig_elem.find(".//label")

        if label_elem is not None:
            label_text = self._get_element_text(label_elem)
            html_parts.append(f'<div class="figure-label">{label_text}</div>')

        # Extract figure caption
        caption_elem = fig_elem.find(".//jats:caption", self.namespaces)
        if caption_elem is None:
            caption_elem = fig_elem.find(".//caption")

        if caption_elem is not None:
            caption_text = self._get_element_text(caption_elem)
            html_parts.append(f'<div class="figure-caption">{caption_text}</div>')

        # Convert other figure content
        for child in fig_elem:
            tag_str = str(child.tag)
            if tag_str.endswith("label") or tag_str.endswith("caption"):
                continue  # Already handled
            html_parts.append(self._convert_element(child))

        html_parts.append('</div>')
        return ''.join(html_parts)

    def _convert_table(self, table_elem) -> str:
        """Convert a table element to HTML."""
        html_parts = ['<div class="table">']

        # Extract table caption
        caption_elem = table_elem.find(".//jats:caption", self.namespaces)
        if caption_elem is None:
            caption_elem = table_elem.find(".//caption")

        if caption_elem is not None:
            caption_text = self._get_element_text(caption_elem)
            html_parts.append(f'<div class="table-caption">{caption_text}</div>')

        # Find the actual table element
        table = table_elem.find(".//jats:table", self.namespaces)
        if table is None:
            table = table_elem.find(".//table")

        if table is not None:
            html_parts.append('<table>')
            
            # Process table rows
            for row in table.findall(".//jats:row", self.namespaces):
                html_parts.append("<tr>")
                for cell in row.findall(".//jats:cell", self.namespaces):
                    cell_text = self._get_element_text(cell)
                    html_parts.append(f"<td>{cell_text}</td>")
                html_parts.append("</tr>")

            html_parts.append("</table>")

        html_parts.append('</div>')
        return ''.join(html_parts)

    def _convert_list(self, list_elem) -> str:
        """Convert a list element to HTML."""
        html_parts = ['<div class="list"><ul>']

        for item in list_elem.findall(".//jats:list-item", self.namespaces):
            item_text = self._get_element_text(item)
            html_parts.append(f'<li class="list-item">{item_text}</li>')

        html_parts.append('</ul></div>')
        return ''.join(html_parts)

    def _convert_references(self, ref_list_elem) -> str:
        """Convert references to HTML."""
        html_parts = ['<div class="references"><h2>References</h2>']

        for ref in ref_list_elem.findall(".//jats:ref", self.namespaces):
            ref_text = self._get_element_text(ref)
            html_parts.append(f'<div class="reference">{ref_text}</div>')

        html_parts.append('</div>')
        return ''.join(html_parts)

    def _get_element_text(self, elem) -> str:
        """Extract text content from an element, preserving formatting."""
        if elem is None:
            return ""

        # Get text content
        text_parts = []
        if elem.text:
            text_parts.append(elem.text.strip())

        # Process child elements with formatting preservation
        for child in elem:
            tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag

            # Handle formatting elements
            if tag == "bold":
                text_parts.append(f'<span class="bold">{self._get_element_text(child)}</span>')
            elif tag == "italic":
                text_parts.append(f'<span class="italic">{self._get_element_text(child)}</span>')
            elif tag == "emphasis":
                text_parts.append(f'<em class="emphasis">{self._get_element_text(child)}</em>')
            elif tag == "ext-link":
                # Handle external links
                href = child.get("{http://www.w3.org/1999/xlink}href")
                if href:
                    link_text = self._get_element_text(child) or href
                    text_parts.append(f'<a href="{href}" target="_blank" class="link">{link_text}</a>')
                else:
                    text_parts.append(self._get_element_text(child))
            elif tag == "uri":
                # Handle URI elements
                href = child.get("{http://www.w3.org/1999/xlink}href")
                if href:
                    link_text = self._get_element_text(child) or href
                    text_parts.append(f'<a href="{href}" target="_blank" class="link">{link_text}</a>')
                else:
                    text_parts.append(self._get_element_text(child))
            elif tag == "sup":
                text_parts.append(f'<span class="superscript">{self._get_element_text(child)}</span>')
            elif tag == "sub":
                text_parts.append(f'<span class="subscript">{self._get_element_text(child)}</span>')
            elif tag == "break":
                text_parts.append("<br>")
            elif tag == "styled-content":
                # Handle styled content with style attributes
                style = child.get("style")
                if style:
                    text_parts.append(f'<span style="{style}">{self._get_element_text(child)}</span>')
                else:
                    text_parts.append(self._get_element_text(child))
            elif tag == "named-content":
                # Handle named content with content-type attributes
                content_type = child.get("content-type")
                if content_type:
                    text_parts.append(f'<span class="{content_type}">{self._get_element_text(child)}</span>')
                else:
                    text_parts.append(self._get_element_text(child))
            else:
                # For other elements, just get their text content
                if child.text:
                    text_parts.append(child.text.strip())
                text_parts.append(self._get_element_text(child))

            if child.tail:
                text_parts.append(child.tail.strip())

        return " ".join(text_parts).strip()

    def _format_text_content(self, text: str, tag: str = None) -> str:
        """Format plain text content."""
        if not text or not text.strip():
            return ""
        
        text = text.strip()
        if tag:
            return f'<span class="{tag}">{text}</span>'
        return text

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
                    error_msg = f"Error processing {xml_file.name}: {str(e)}"
                    logger.error(error_msg)
                    results["failed"].append(error_msg)

            logger.info(
                f"Conversion complete: {len(results['successful'])} successful, "
                f"{len(results['failed'])} failed, {len(results['skipped'])} skipped"
            )

            return results

        except Exception as e:
            error_msg = f"Error processing corpus: {str(e)}"
            logger.error(error_msg)
            results["failed"].append(error_msg)
            return results
