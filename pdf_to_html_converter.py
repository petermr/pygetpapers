#!/usr/bin/env python3
"""
PDF to HTML Converter

This script downloads PDFs, parses them with PDFPlumber, and converts them to 
well-formatted HTML with intelligent text processing including:
- Line joining
- Paragraph creation
- Section title combination with following text
- Page trimming and joining
"""

import os
import re
import requests
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import pdfplumber
from urllib.parse import urlparse
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PDFToHTMLConverter:
    """Converts PDF files to well-formatted HTML with intelligent text processing."""

    def __init__(self, output_dir: str = "pdf_output"):
        """
        Initialize the converter.

        Args:
            output_dir: Directory to save downloaded PDFs and generated HTML
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Text processing patterns
        self.section_patterns = [
            r"^[A-Z][A-Z\s]+$",  # ALL CAPS titles
            r"^\d+\.\s+[A-Z]",  # Numbered sections
            r"^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$",  # Title Case
            r"^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*$",  # Title Case with trailing space
        ]

        # Line joining patterns
        self.line_break_patterns = [
            r"([a-z])\s*\n\s*([a-z])",  # Lowercase to lowercase
            r"([a-z])\s*\n\s*([A-Z][a-z])",  # Lowercase to title case (likely continuation)
            r"([a-z])\s*\n\s*([0-9])",  # Lowercase to number (likely continuation)
        ]

        # Paragraph break patterns
        self.paragraph_break_patterns = [
            r"\n\s*\n",  # Double newlines
            r"([.!?])\s*\n\s*([A-Z][A-Z\s]+$)",  # Sentence end followed by ALL CAPS
            r"([.!?])\s*\n\s*(\d+\.\s+[A-Z])",  # Sentence end followed by numbered section
        ]

    def download_pdf(self, url: str, filename: Optional[str] = None) -> Path:
        """
        Download a PDF from a URL.

        Args:
            url: URL of the PDF to download
            filename: Optional custom filename

        Returns:
            Path to the downloaded PDF file
        """
        if not filename:
            # Extract filename from URL
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)
            if not filename.endswith(".pdf"):
                filename = "downloaded_document.pdf"

        pdf_path = self.output_dir / filename

        logger.info(f"Downloading PDF from: {url}")
        logger.info(f"Saving to: {pdf_path}")

        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            with open(pdf_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            logger.info(f"✅ PDF downloaded successfully: {pdf_path}")
            return pdf_path

        except Exception as e:
            logger.error(f"❌ Failed to download PDF: {e}")
            raise

    def extract_text_from_pdf(self, pdf_path: Path) -> List[Dict]:
        """
        Extract text from PDF using PDFPlumber.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            List of page data with text and metadata
        """
        logger.info(f"Extracting text from: {pdf_path}")

        pages_data = []

        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    logger.info(f"Processing page {page_num}/{len(pdf.pages)}")

                    # Extract text
                    text = page.extract_text()

                    # Extract text blocks with positioning
                    text_blocks = []
                    if page.extract_words():
                        for word in page.extract_words():
                            text_blocks.append(
                                {
                                    "text": word.get("text", ""),
                                    "x0": word.get("x0", 0),
                                    "y0": word.get("y0", 0),
                                    "x1": word.get("x1", 0),
                                    "y1": word.get("y1", 0),
                                    "top": word.get("top", 0),
                                    "bottom": word.get("bottom", 0),
                                }
                            )

                    pages_data.append(
                        {
                            "page_num": page_num,
                            "text": text,
                            "text_blocks": text_blocks,
                            "width": page.width,
                            "height": page.height,
                        }
                    )

            logger.info(f"✅ Text extraction completed: {len(pages_data)} pages")
            return pages_data

        except Exception as e:
            logger.error(f"❌ Failed to extract text: {e}")
            raise

    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text.

        Args:
            text: Raw text from PDF

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        # Remove excessive whitespace
        text = re.sub(r"\s+", " ", text)

        # Normalize line breaks
        text = re.sub(r"\r\n", "\n", text)
        text = re.sub(r"\r", "\n", text)

        # Remove page numbers and headers/footers (common patterns)
        text = re.sub(
            r"^\s*\d+\s*$", "", text, flags=re.MULTILINE
        )  # Standalone page numbers
        text = re.sub(r"Page\s+\d+", "", text, flags=re.IGNORECASE)  # "Page X" headers

        # Trim whitespace
        text = text.strip()

        return text

    def join_lines(self, text: str) -> str:
        """
        Intelligently join broken lines.

        Args:
            text: Text with potential line breaks

        Returns:
            Text with lines joined where appropriate
        """
        if not text:
            return ""

        # Apply line joining patterns
        for pattern in self.line_break_patterns:
            text = re.sub(pattern, r"\1 \2", text, flags=re.MULTILINE)

        # Join hyphenated words at line breaks
        text = re.sub(r"(\w+)-\s*\n\s*(\w+)", r"\1\2", text, flags=re.MULTILINE)

        return text

    def identify_sections(self, text: str) -> List[Dict]:
        """
        Identify section titles and their content.

        Args:
            text: Processed text

        Returns:
            List of sections with titles and content
        """
        lines = text.split("\n")
        sections = []
        current_section = {"title": "", "content": []}

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if line is a section title
            is_title = any(re.match(pattern, line) for pattern in self.section_patterns)

            if is_title:
                # Save previous section if it has content
                if current_section["title"] or current_section["content"]:
                    sections.append(current_section)

                # Start new section
                current_section = {"title": line, "content": []}
            else:
                # Add line to current section content
                current_section["content"].append(line)

        # Add the last section
        if current_section["title"] or current_section["content"]:
            sections.append(current_section)

        return sections

    def create_paragraphs(self, text: str) -> List[str]:
        """
        Split text into logical paragraphs.

        Args:
            text: Text to split into paragraphs

        Returns:
            List of paragraphs
        """
        if not text:
            return []

        # Split on paragraph breaks
        paragraphs = re.split(r"\n\s*\n", text)

        # Clean up paragraphs
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        return paragraphs

    def generate_html(
        self, sections: List[Dict], title: str = "Converted Document"
    ) -> str:
        """
        Generate HTML from processed sections.

        Args:
            sections: List of sections with titles and content
            title: Document title

        Returns:
            HTML string
        """
        html_parts = [
            "<!DOCTYPE html>",
            '<html lang="en">',
            "<head>",
            f"    <title>{title}</title>",
            '    <meta charset="utf-8">',
            "    <style>",
            "        body { font-family: Arial, sans-serif; line-height: 1.6; margin: 40px; }",
            "        h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }",
            "        h2 { color: #34495e; margin-top: 30px; margin-bottom: 15px; }",
            "        h3 { color: #7f8c8d; margin-top: 25px; margin-bottom: 10px; }",
            "        p { margin-bottom: 15px; text-align: justify; }",
            "        .section { margin-bottom: 30px; }",
            "        .content { margin-left: 20px; }",
            "    </style>",
            "</head>",
            "<body>",
            f"    <h1>{title}</h1>",
        ]

        for section in sections:
            if section["title"]:
                # Determine heading level based on title characteristics
                if re.match(r"^[A-Z][A-Z\s]+$", section["title"]):
                    html_parts.append(f'    <h1>{section["title"]}</h1>')
                elif re.match(r"^\d+\.\s+", section["title"]):
                    html_parts.append(f'    <h2>{section["title"]}</h2>')
                else:
                    html_parts.append(f'    <h3>{section["title"]}</h3>')

            if section["content"]:
                html_parts.append('    <div class="content">')

                # Group content into paragraphs
                content_text = " ".join(section["content"])
                paragraphs = self.create_paragraphs(content_text)

                for paragraph in paragraphs:
                    if paragraph.strip():
                        html_parts.append(f"        <p>{paragraph}</p>")

                html_parts.append("    </div>")

        html_parts.extend(["</body>", "</html>"])

        return "\n".join(html_parts)

    def convert_pdf_to_html(self, pdf_path: Path, title: str = None) -> Path:
        """
        Convert a PDF file to HTML with intelligent text processing.

        Args:
            pdf_path: Path to the PDF file
            title: Optional document title

        Returns:
            Path to the generated HTML file
        """
        if not title:
            title = pdf_path.stem.replace("_", " ").title()

        logger.info(f"Converting PDF to HTML: {pdf_path}")

        # Extract text from PDF
        pages_data = self.extract_text_from_pdf(pdf_path)

        # Combine all page text
        all_text = "\n".join(page["text"] for page in pages_data if page["text"])

        # Clean text
        cleaned_text = self.clean_text(all_text)

        # Join lines
        joined_text = self.join_lines(cleaned_text)

        # Identify sections
        sections = self.identify_sections(joined_text)

        # Generate HTML
        html_content = self.generate_html(sections, title)

        # Save HTML file
        html_path = self.output_dir / f"{pdf_path.stem}.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info(f"✅ HTML generated successfully: {html_path}")
        return html_path

    def download_and_convert(self, url: str, title: str = None) -> Tuple[Path, Path]:
        """
        Download a PDF and convert it to HTML in one step.

        Args:
            url: URL of the PDF to download
            title: Optional document title

        Returns:
            Tuple of (PDF path, HTML path)
        """
        # Download PDF
        pdf_path = self.download_pdf(url)

        # Convert to HTML
        html_path = self.convert_pdf_to_html(pdf_path, title)

        return pdf_path, html_path


def main():
    """Example usage of the PDF to HTML converter."""
    converter = PDFToHTMLConverter()

    # Example: Convert a local PDF file
    # pdf_path = Path("example.pdf")
    # html_path = converter.convert_pdf_to_html(pdf_path, "Example Document")

    # Example: Download and convert a PDF from URL
    # url = "https://example.com/document.pdf"
    # pdf_path, html_path = converter.download_and_convert(url, "Downloaded Document")

    print("PDF to HTML Converter ready!")
    print("Use the converter methods to process your PDFs:")
    print("- converter.convert_pdf_to_html(pdf_path)")
    print("- converter.download_and_convert(url)")


if __name__ == "__main__":
    main()
