"""
HTML Processor for Pygetpapers

This module handles different types of HTML files and conversions:
- fulltext.raw.html (provided by publisher/repo)
- fulltext.xml.html (converted from XML)
- fulltext.pdf.html (converted from PDF)
- fulltext.doc.html (converted from DOC)
- html_with_ids.html (cleaned and enhanced HTML for analysis)
"""

import logging
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class HTMLProcessor:
    """
    Handles different types of HTML files and conversions.
    """

    def __init__(self):
        self.html_types = {
            "raw": "fulltext.raw.html",  # Provided by publisher/repo
            "xml": "fulltext.xml.html",  # Converted from XML
            "pdf": "fulltext.pdf.html",  # Converted from PDF
            "doc": "fulltext.doc.html",  # Converted from DOC
            "enhanced": "html_with_ids.html",  # Cleaned and enhanced for analysis
        }

    def get_html_files_for_paper(self, paper_dir: Path) -> Dict[str, Path]:
        """
        Get all HTML files for a paper with their types.

        Args:
            paper_dir: Path to paper directory

        Returns:
            Dictionary mapping HTML types to file paths
        """
        html_files = {}

        for html_type, filename in self.html_types.items():
            file_path = paper_dir / filename
            if file_path.exists():
                html_files[html_type] = file_path

        return html_files

    def get_best_html_file(self, paper_dir: Path) -> Optional[Tuple[str, Path]]:
        """
        Get the best available HTML file for a paper.
        Priority order: enhanced > xml > raw > pdf > doc

        Args:
            paper_dir: Path to paper directory

        Returns:
            Tuple of (html_type, file_path) or None if no HTML files found
        """
        html_files = self.get_html_files_for_paper(paper_dir)

        # Priority order
        priority_order = ["enhanced", "xml", "raw", "pdf", "doc"]

        for html_type in priority_order:
            if html_type in html_files:
                return html_type, html_files[html_type]

        return None

    def create_enhanced_html(
        self, source_html_path: Path, output_path: Optional[Path] = None
    ) -> bool:
        """
        Create enhanced HTML with IDs and cleaned structure.

        Args:
            source_html_path: Path to source HTML file
            output_path: Output path (defaults to html_with_ids.html in same directory)

        Returns:
            True if successful, False otherwise
        """
        try:
            if output_path is None:
                output_path = source_html_path.parent / self.html_types["enhanced"]

            # Read source HTML
            with open(source_html_path, "r", encoding="utf-8") as f:
                html_content = f.read()

            # Clean and enhance HTML
            enhanced_html = self._enhance_html_content(html_content)

            # Write enhanced HTML
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(enhanced_html)

            logger.info(f"Created enhanced HTML: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error creating enhanced HTML: {e}")
            return False

    def _enhance_html_content(self, html_content: str) -> str:
        """
        Enhance HTML content by adding IDs and cleaning structure.

        Args:
            html_content: Original HTML content

        Returns:
            Enhanced HTML content
        """
        # Add IDs to sections
        html_content = self._add_section_ids(html_content)

        # Clean up structure
        html_content = self._clean_html_structure(html_content)

        # Add metadata
        html_content = self._add_enhancement_metadata(html_content)

        return html_content

    def _add_section_ids(self, html_content: str) -> str:
        """Add IDs to HTML sections for better navigation and analysis."""
        # Add IDs to headings
        heading_pattern = r"<(h[1-6])([^>]*)>"

        def add_heading_id(match):
            tag = match.group(1)
            attrs = match.group(2)

            # Check if ID already exists
            if "id=" in attrs:
                return match.group(0)

            # Generate ID from text content
            # This is a simplified version - in practice, you'd want to extract the text
            import uuid

            section_id = f"section_{uuid.uuid4().hex[:8]}"

            return f'<{tag}{attrs} id="{section_id}">'

        html_content = re.sub(heading_pattern, add_heading_id, html_content)

        return html_content

    def _clean_html_structure(self, html_content: str) -> str:
        """Clean up HTML structure for better analysis."""
        # Remove unnecessary whitespace
        html_content = re.sub(r"\s+", " ", html_content)

        # Ensure proper HTML structure
        if "<html>" not in html_content.lower():
            html_content = f"<html><head><title>Enhanced Document</title></head><body>{html_content}</body></html>"

        return html_content

    def _add_enhancement_metadata(self, html_content: str) -> str:
        """Add metadata about the enhancement process."""
        import datetime

        enhancement_info = f"""
<!-- 
Enhanced HTML created by Pygetpapers HTML Processor
Created: {datetime.datetime.now().isoformat()}
Enhancements: Added section IDs, cleaned structure
-->
"""

        # Insert after DOCTYPE or at start of HTML
        if "<!DOCTYPE" in html_content:
            pos = html_content.find(">", html_content.find("<!DOCTYPE")) + 1
            return html_content[:pos] + enhancement_info + html_content[pos:]
        else:
            return enhancement_info + html_content

    def convert_pdf_to_html(
        self, pdf_path: Path, output_path: Optional[Path] = None
    ) -> bool:
        """
        Convert PDF to HTML.

        Args:
            pdf_path: Path to PDF file
            output_path: Output path (defaults to fulltext.pdf.html in same directory)

        Returns:
            True if successful, False otherwise
        """
        try:
            if output_path is None:
                output_path = pdf_path.parent / self.html_types["pdf"]

            # Try different PDF to HTML converters
            converters = [
                self._convert_pdf_with_pdfplumber,
                self._convert_pdf_with_pymupdf,
                self._convert_pdf_with_system_tools,
            ]

            for converter in converters:
                try:
                    if converter(pdf_path, output_path):
                        logger.info(f"Converted PDF to HTML: {output_path}")
                        return True
                except Exception as e:
                    logger.debug(f"PDF converter {converter.__name__} failed: {e}")
                    continue

            logger.error("All PDF to HTML converters failed")
            return False

        except Exception as e:
            logger.error(f"Error converting PDF to HTML: {e}")
            return False

    def _convert_pdf_with_pdfplumber(self, pdf_path: Path, output_path: Path) -> bool:
        """Convert PDF using pdfplumber."""
        try:
            import pdfplumber

            html_content = ["<html><head><title>PDF Document</title></head><body>"]

            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text:
                        html_content.append(f'<div class="page" id="page_{page_num}">')
                        html_content.append(f"<h2>Page {page_num}</h2>")
                        html_content.append(f"<p>{text}</p>")
                        html_content.append("</div>")

            html_content.append("</body></html>")

            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n".join(html_content))

            return True

        except ImportError:
            return False

    def _convert_pdf_with_pymupdf(self, pdf_path: Path, output_path: Path) -> bool:
        """Convert PDF using PyMuPDF (fitz)."""
        try:
            import fitz

            html_content = ["<html><head><title>PDF Document</title></head><body>"]

            doc = fitz.open(pdf_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                if text:
                    html_content.append(f'<div class="page" id="page_{page_num + 1}">')
                    html_content.append(f"<h2>Page {page_num + 1}</h2>")
                    html_content.append(f"<p>{text}</p>")
                    html_content.append("</div>")

            doc.close()
            html_content.append("</body></html>")

            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n".join(html_content))

            return True

        except ImportError:
            return False

    def _convert_pdf_with_system_tools(self, pdf_path: Path, output_path: Path) -> bool:
        """Convert PDF using system tools like pdftotext."""
        try:
            import subprocess

            # Try pdftotext
            result = subprocess.run(
                ["pdftotext", str(pdf_path), "-"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                text_content = result.stdout
                html_content = f"""
<html>
<head><title>PDF Document</title></head>
<body>
<div class="content">
<p>{text_content}</p>
</div>
</body>
</html>
"""
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(html_content)
                return True

            return False

        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def convert_doc_to_html(
        self, doc_path: Path, output_path: Optional[Path] = None
    ) -> bool:
        """
        Convert DOC/DOCX to HTML.

        Args:
            doc_path: Path to DOC/DOCX file
            output_path: Output path (defaults to fulltext.doc.html in same directory)

        Returns:
            True if successful, False otherwise
        """
        try:
            if output_path is None:
                output_path = doc_path.parent / self.html_types["doc"]

            # Try different DOC to HTML converters
            converters = [
                self._convert_doc_with_python_docx,
                self._convert_doc_with_system_tools,
            ]

            for converter in converters:
                try:
                    if converter(doc_path, output_path):
                        logger.info(f"Converted DOC to HTML: {output_path}")
                        return True
                except Exception as e:
                    logger.debug(f"DOC converter {converter.__name__} failed: {e}")
                    continue

            logger.error("All DOC to HTML converters failed")
            return False

        except Exception as e:
            logger.error(f"Error converting DOC to HTML: {e}")
            return False

    def _convert_doc_with_python_docx(self, doc_path: Path, output_path: Path) -> bool:
        """Convert DOCX using python-docx."""
        try:
            from docx import Document

            doc = Document(doc_path)
            html_content = ["<html><head><title>Document</title></head><body>"]

            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    html_content.append(f"<p>{paragraph.text}</p>")

            html_content.append("</body></html>")

            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n".join(html_content))

            return True

        except ImportError:
            return False

    def _convert_doc_with_system_tools(self, doc_path: Path, output_path: Path) -> bool:
        """Convert DOC using system tools like pandoc."""
        try:
            import subprocess

            # Try pandoc
            result = subprocess.run(
                ["pandoc", str(doc_path), "-o", str(output_path), "--to", "html"],
                capture_output=True,
                timeout=60,
            )

            return result.returncode == 0

        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def process_corpus_html(self, corpus_dir: Path) -> Dict[str, int]:
        """
        Process all HTML files in a corpus.

        Args:
            corpus_dir: Path to corpus directory

        Returns:
            Dictionary with processing statistics
        """
        stats = {
            "papers_processed": 0,
            "enhanced_html_created": 0,
            "pdf_conversions": 0,
            "doc_conversions": 0,
            "errors": 0,
        }

        try:
            # Find all paper directories
            paper_dirs = [
                d
                for d in corpus_dir.iterdir()
                if d.is_dir() and not d.name.startswith(".")
            ]

            for paper_dir in paper_dirs:
                try:
                    stats["papers_processed"] += 1

                    # Get existing HTML files
                    html_files = self.get_html_files_for_paper(paper_dir)

                    # Create enhanced HTML if we have any source HTML
                    if html_files:
                        best_html = self.get_best_html_file(paper_dir)
                        if best_html:
                            source_type, source_path = best_html
                            enhanced_path = paper_dir / self.html_types["enhanced"]

                            if self.create_enhanced_html(source_path, enhanced_path):
                                stats["enhanced_html_created"] += 1

                    # Convert PDFs if they exist
                    pdf_files = list(paper_dir.glob("*.pdf"))
                    for pdf_file in pdf_files:
                        if self.convert_pdf_to_html(pdf_file):
                            stats["pdf_conversions"] += 1

                    # Convert DOCs if they exist
                    doc_files = list(paper_dir.glob("*.doc*"))
                    for doc_file in doc_files:
                        if self.convert_doc_to_html(doc_file):
                            stats["doc_conversions"] += 1

                except Exception as e:
                    logger.error(f"Error processing paper {paper_dir.name}: {e}")
                    stats["errors"] += 1

            logger.info(f"Corpus processing complete: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Error processing corpus: {e}")
            return stats
