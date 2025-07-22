#!/usr/bin/env python3
"""
hOCR Builder for Pygetpapers

This module provides a standalone hOCR builder that creates standardized hOCR output
for both PDF and image-to-text conversion pipelines.

AUTHOR: P. Murray-Rust with assistance from CursorAI (Claude Sonnet 4)
VERSION: 1.0.0
PURPOSE: Create unified hOCR output format for PDF and image processing
"""

import logging
import html
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
import lxml.etree as ET

logger = logging.getLogger(__name__)


def round_coordinates(value: float) -> float:
    """Round coordinate values to 3 decimal places or less."""
    return round(value, 3)


def convert_html_entities(text: str) -> str:
    """Convert HTML character entities to Unicode."""
    return html.unescape(text)


def replace_ocr_with_pdf(text: str) -> str:
    """Replace all ocr_* and ocr-* with pdf_* and pdf-* respectively."""
    # Replace ocr_* with pdf_*
    text = re.sub(r"ocr_", "pdf_", text)
    # Replace ocr-* with pdf-*
    text = re.sub(r"ocr-", "pdf-", text)
    return text


def remove_font_prefix(font_name: str) -> str:
    """
    Remove font prefixes (e.g., ABCDEF+FontName, ABCDEFG+FontName).

    Args:
        font_name: Font name that may contain a prefix

    Returns:
        Font name with prefix removed
    """
    if not font_name:
        return font_name

    # Pattern to match 6-8 uppercase letters followed by a plus sign
    # e.g., "OWIINY+ArialMT" -> "ArialMT"
    # e.g., "YLWFOA+TimesNewRomanPSMT" -> "TimesNewRomanPSMT"
    # e.g., "ABQRQW+TimesNewRomanPSMT" -> "TimesNewRomanPSMT"
    pattern = r"^[A-Z]{6,8}\+"
    return re.sub(pattern, "", font_name)


def decompose_font_name(font_name: str) -> Tuple[str, str, str]:
    """
    Decompose font name to extract family, weight, and style.

    This is a heuristic approach that handles common font naming patterns:
    - Arial-Bold => family=Arial, weight=bold, style=normal
    - Times-Italic => family=Times, weight=normal, style=italic
    - Helvetica-BoldItalic => family=Helvetica, weight=bold, style=italic
    - Foo-B => family=Foo, weight=bold, style=normal
    - Bar-I => family=Bar, weight=normal, style=italic

    Args:
        font_name: Font name to decompose (should already have prefixes removed)

    Returns:
        Tuple of (font_family, font_weight, font_style)
    """
    if not font_name:
        return "Arial", "normal", "normal"

    font_name = font_name.strip()

    # Handle common patterns
    if "-BoldItalic" in font_name or "-Bold-Italic" in font_name:
        family = font_name.replace("-BoldItalic", "").replace("-Bold-Italic", "")
        return family, "bold", "italic"

    if "-ItalicBold" in font_name or "-Italic-Bold" in font_name:
        family = font_name.replace("-ItalicBold", "").replace("-Italic-Bold", "")
        return family, "bold", "italic"

    if "-Bold" in font_name:
        family = font_name.replace("-Bold", "")
        return family, "bold", "normal"

    if "-Italic" in font_name:
        family = font_name.replace("-Italic", "")
        return family, "normal", "italic"

    # Handle single letter patterns
    if font_name.endswith("-B"):
        family = font_name[:-2]
        return family, "bold", "normal"

    if font_name.endswith("-I"):
        family = font_name[:-2]
        return family, "normal", "italic"

    if font_name.endswith("-BI"):
        family = font_name[:-3]
        return family, "bold", "italic"

    if font_name.endswith("-IB"):
        family = font_name[:-3]
        return family, "bold", "italic"

    # Default case - assume normal weight and style
    return font_name, "normal", "normal"


@dataclass
class HOCRCharacter:
    """Represents a single character in hOCR format."""

    text: str
    x0: float
    y0: float
    x1: float
    y1: float
    confidence: float = 1.0
    font_family: Optional[str] = None
    font_size: Optional[float] = None
    font_weight: Optional[str] = None
    font_style: Optional[str] = None
    color: Optional[str] = None
    baseline: Optional[float] = None


@dataclass
class HOCRWord:
    """Represents a word in hOCR format."""

    text: str
    x0: float
    y0: float
    x1: float
    y1: float
    confidence: float = 1.0
    characters: List[HOCRCharacter] = field(default_factory=list)
    font_family: Optional[str] = None
    font_size: Optional[float] = None
    font_weight: Optional[str] = None
    font_style: Optional[str] = None
    color: Optional[str] = None
    baseline: Optional[float] = None


@dataclass
class HOCRLine:
    """Represents a line of text in hOCR format."""

    words: List[HOCRWord] = field(default_factory=list)
    x0: float = 0.0
    y0: float = 0.0
    x1: float = 0.0
    y1: float = 0.0
    baseline: Optional[float] = None
    text: str = ""
    confidence: float = 1.0


@dataclass
class HOCRParagraph:
    """Represents a paragraph in hOCR format."""

    lines: List[HOCRLine] = field(default_factory=list)
    x0: float = 0.0
    y0: float = 0.0
    x1: float = 0.0
    y1: float = 0.0
    text: str = ""
    confidence: float = 1.0
    paragraph_type: str = "normal"  # normal, heading, list_item, etc.


@dataclass
class HOCRPage:
    """Represents a page in hOCR format."""

    page_number: int
    width: float
    height: float
    paragraphs: List[HOCRParagraph] = field(default_factory=list)
    images: List[Dict[str, Any]] = field(default_factory=list)
    graphics: List[Dict[str, Any]] = field(default_factory=list)
    confidence: float = 1.0


@dataclass
class HOCRDocument:
    """Represents a complete hOCR document."""

    title: str = "Converted Document"
    pages: List[HOCRPage] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_date: str = field(default_factory=lambda: datetime.now().isoformat())
    creator: str = "pygetpapers hOCR Builder"
    language: str = "en"


class HOCRBuilder:
    """
    Standalone hOCR builder for creating standardized hOCR output.

    This builder can be used by both PDF and image processing pipelines
    to create consistent hOCR output that can later be converted to
    semantic HTML with sections, lists, footnotes, etc.
    """

    def __init__(self, document_title: str = "Converted Document"):
        """
        Initialize the hOCR builder.

        Args:
            document_title: Title of the document
        """
        self.document = HOCRDocument(title=document_title)
        self.current_page = None
        self.current_paragraph = None
        self.current_line = None
        self.id_counter = 1  # Global ID counter for all elements

    def add_page(self, page_number: int, width: float, height: float) -> HOCRPage:
        """
        Add a new page to the document.

        Args:
            page_number: Page number (1-based)
            width: Page width in points
            height: Page height in points

        Returns:
            The created page object
        """
        page = HOCRPage(page_number=page_number, width=width, height=height)
        self.document.pages.append(page)
        self.current_page = page
        return page

    def add_paragraph(self, paragraph_type: str = "normal") -> HOCRParagraph:
        """
        Add a new paragraph to the current page.

        Args:
            paragraph_type: Type of paragraph (normal, heading, list_item, etc.)

        Returns:
            The created paragraph object
        """
        if not self.current_page:
            raise ValueError("No current page. Call add_page() first.")

        paragraph = HOCRParagraph(paragraph_type=paragraph_type)
        self.current_page.paragraphs.append(paragraph)
        self.current_paragraph = paragraph
        return paragraph

    def add_line(self) -> HOCRLine:
        """
        Add a new line to the current paragraph.

        Returns:
            The created line object
        """
        if not self.current_paragraph:
            raise ValueError("No current paragraph. Call add_paragraph() first.")

        line = HOCRLine()
        self.current_paragraph.lines.append(line)
        self.current_line = line
        return line

    def add_word(
        self,
        text: str,
        x0: float,
        y0: float,
        x1: float,
        y1: float,
        confidence: float = 1.0,
        font_family: Optional[str] = None,
        font_size: Optional[float] = None,
        font_weight: Optional[str] = None,
        font_style: Optional[str] = None,
        color: Optional[str] = None,
        baseline: Optional[float] = None,
    ) -> HOCRWord:
        """
        Add a word to the current line.

        Args:
            text: Word text
            x0, y0, x1, y1: Bounding box coordinates
            confidence: Confidence score (0.0 to 1.0)
            font_family: Font family name
            font_size: Font size in points
            font_weight: Font weight (normal, bold, etc.)
            font_style: Font style (normal, italic, etc.)
            color: Text color
            baseline: Baseline position

        Returns:
            The created word object
        """
        if not self.current_line:
            raise ValueError("No current line. Call add_line() first.")

        word = HOCRWord(
            text=text,
            x0=x0,
            y0=y0,
            x1=x1,
            y1=y1,
            confidence=confidence,
            font_family=font_family,
            font_size=font_size,
            font_weight=font_weight,
            font_style=font_style,
            color=color,
            baseline=baseline,
        )

        self.current_line.words.append(word)

        # Update line bounding box
        if len(self.current_line.words) == 1:
            # First word in line - initialize bounding box
            self.current_line.x0 = x0
            self.current_line.y0 = y0
            self.current_line.x1 = x1
            self.current_line.y1 = y1
        else:
            # Subsequent words - expand bounding box
            self.current_line.x0 = min(self.current_line.x0, x0)
            self.current_line.y0 = min(self.current_line.y0, y0)
            self.current_line.x1 = max(self.current_line.x1, x1)
            self.current_line.y1 = max(self.current_line.y1, y1)

        return word

    def add_word_with_font_name(
        self,
        text: str,
        x0: float,
        y0: float,
        x1: float,
        y1: float,
        confidence: float = 1.0,
        font_name: Optional[str] = None,
        font_size: Optional[float] = None,
        color: Optional[str] = None,
        baseline: Optional[float] = None,
    ) -> HOCRWord:
        """
        Add a word to the current line with automatic font decomposition.

        Args:
            text: Word text
            x0, y0, x1, y1: Bounding box coordinates
            confidence: Confidence score (0.0 to 1.0)
            font_name: Font name to decompose (e.g., "Arial-Bold", "Times-Italic")
            font_size: Font size in points
            color: Text color
            baseline: Baseline position

        Returns:
            The created word object
        """
        if not self.current_line:
            raise ValueError("No current line. Call add_line() first.")

        # Remove font prefix first, then decompose font name
        font_family = None
        font_weight = None
        font_style = None

        if font_name:
            # Remove 7-letter font prefixes first
            clean_font_name = remove_font_prefix(font_name)
            # Then decompose the clean font name
            font_family, font_weight, font_style = decompose_font_name(clean_font_name)

        return self.add_word(
            text=text,
            x0=x0,
            y0=y0,
            x1=x1,
            y1=y1,
            confidence=confidence,
            font_family=font_family,
            font_size=font_size,
            font_weight=font_weight,
            font_style=font_style,
            color=color,
            baseline=baseline,
        )

    def add_character(
        self,
        text: str,
        x0: float,
        y0: float,
        x1: float,
        y1: float,
        confidence: float = 1.0,
        font_family: Optional[str] = None,
        font_size: Optional[float] = None,
        font_weight: Optional[str] = None,
        font_style: Optional[str] = None,
        color: Optional[str] = None,
        baseline: Optional[float] = None,
    ) -> HOCRCharacter:
        """
        Add a character to the current word.

        Args:
            text: Character text
            x0, y0, x1, y1: Bounding box coordinates
            confidence: Confidence score (0.0 to 1.0)
            font_family: Font family name
            font_size: Font size in points
            font_weight: Font weight (normal, bold, etc.)
            font_style: Font style (normal, italic, etc.)
            color: Text color
            baseline: Baseline position

        Returns:
            The created character object
        """
        if not self.current_line or not self.current_line.words:
            raise ValueError("No current word. Call add_word() first.")

        character = HOCRCharacter(
            text=text,
            x0=x0,
            y0=y0,
            x1=x1,
            y1=y1,
            confidence=confidence,
            font_family=font_family,
            font_size=font_size,
            font_weight=font_weight,
            font_style=font_style,
            color=color,
            baseline=baseline,
        )

        current_word = self.current_line.words[-1]
        current_word.characters.append(character)

        return character

    def add_image(
        self,
        x0: float,
        y0: float,
        x1: float,
        y1: float,
        image_data: Optional[bytes] = None,
        image_path: Optional[str] = None,
        alt_text: Optional[str] = None,
        confidence: float = 1.0,
    ) -> Dict[str, Any]:
        """
        Add an image to the current page.

        Args:
            x0, y0, x1, y1: Bounding box coordinates
            image_data: Raw image data
            image_path: Path to image file
            alt_text: Alternative text description
            confidence: Confidence score

        Returns:
            The created image object
        """
        if not self.current_page:
            raise ValueError("No current page. Call add_page() first.")

        image = {
            "x0": x0,
            "y0": y0,
            "x1": x1,
            "y1": y1,
            "image_data": image_data,
            "image_path": image_path,
            "alt_text": alt_text,
            "confidence": confidence,
        }

        self.current_page.images.append(image)
        return image

    def add_graphic(
        self,
        graphic_type: str,
        x0: float,
        y0: float,
        x1: float,
        y1: float,
        svg_data: Optional[str] = None,
        confidence: float = 1.0,
    ) -> Dict[str, Any]:
        """
        Add a graphic element to the current page.

        Args:
            graphic_type: Type of graphic (rect, circle, line, path, etc.)
            x0, y0, x1, y1: Bounding box coordinates
            svg_data: SVG representation of the graphic
            confidence: Confidence score

        Returns:
            The created graphic object
        """
        if not self.current_page:
            raise ValueError("No current page. Call add_page() first.")

        graphic = {
            "type": graphic_type,
            "x0": x0,
            "y0": y0,
            "x1": x1,
            "y1": y1,
            "svg_data": svg_data,
            "confidence": confidence,
        }

        self.current_page.graphics.append(graphic)
        return graphic

    def _update_text_content(self):
        """Update text content for lines, paragraphs, and pages."""
        # Update line text
        if self.current_line:
            self.current_line.text = " ".join(
                word.text for word in self.current_line.words
            )

        # Update paragraph text
        if self.current_paragraph:
            self.current_paragraph.text = " ".join(
                line.text for line in self.current_paragraph.lines
            )

            # Update paragraph bounding box
            if self.current_paragraph.lines:
                x0s = [line.x0 for line in self.current_paragraph.lines]
                y0s = [line.y0 for line in self.current_paragraph.lines]
                x1s = [line.x1 for line in self.current_paragraph.lines]
                y1s = [line.y1 for line in self.current_paragraph.lines]

                self.current_paragraph.x0 = min(x0s)
                self.current_paragraph.y0 = min(y0s)
                self.current_paragraph.x1 = max(x1s)
                self.current_paragraph.y1 = max(y1s)

    def finalize_current_structures(self):
        """Finalize current line and paragraph structures."""
        self._update_text_content()

    def generate_hocr_xml(self) -> str:
        """
        Generate hOCR XML output using lxml.

        Returns:
            hOCR XML string
        """
        self.finalize_current_structures()

        # Create root element
        root = ET.Element(
            "html", {"xmlns": "http://www.w3.org/1999/xhtml", "lang": "en"}
        )

        # Create head element
        head = ET.SubElement(root, "head")

        # Add title
        title = ET.SubElement(head, "title")
        title.text = convert_html_entities(self.document.title)

        # Add meta tags
        meta_tags = [
            ("http-equiv", "Content-Type", "text/html;charset=utf-8"),
            ("name", "pdf-system", self.document.creator),
            ("name", "pdf-langs", self.document.language),
            ("name", "pdf-number-of-pages", str(len(self.document.pages))),
            ("name", "pdf-datetime", self.document.created_date),
        ]

        for attr_name, attr_value, content in meta_tags:
            meta = ET.SubElement(head, "meta", {attr_name: attr_value})
            meta.set("content", content)

        # Create body element
        body = ET.SubElement(root, "body")

        # Add pages
        for page in self.document.pages:
            self._add_page_to_hocr_xml(body, page)

        # Generate XML string with proper declaration
        xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
        doctype = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n'
        xml_content = ET.tostring(root, encoding="unicode", pretty_print=True)
        return xml_declaration + doctype + xml_content

    def _add_page_to_hocr_xml(self, parent: ET._Element, page: HOCRPage):
        """Add a page to hOCR XML using lxml."""
        page_div = ET.SubElement(
            parent,
            "div",
            {
                "class": "pdf_page",
                "id": f"p{self.id_counter}",
                "title": f"image ''; bbox 0 0 {round_coordinates(page.width)} {round_coordinates(page.height)}; ppageno {page.page_number}",
            },
        )
        self.id_counter += 1

        # Add paragraphs
        for paragraph in page.paragraphs:
            self._add_paragraph_to_hocr_xml(page_div, paragraph)

        # Add images
        for image in page.images:
            self._add_image_to_hocr_xml(page_div, image)

        # Add graphics
        for graphic in page.graphics:
            self._add_graphic_to_hocr_xml(page_div, graphic)

    def _add_paragraph_to_hocr_xml(self, parent: ET._Element, paragraph: HOCRParagraph):
        """Add a paragraph to hOCR XML using lxml."""
        par_div = ET.SubElement(
            parent, "div", {"class": "pdf_par", "id": f"p{self.id_counter}"}
        )
        self.id_counter += 1

        # Add lines
        for line in paragraph.lines:
            self._add_line_to_hocr_xml(par_div, line)

    def _add_line_to_hocr_xml(self, parent: ET._Element, line: HOCRLine):
        """Add a line to hOCR XML using lxml."""
        line_span = ET.SubElement(
            parent,
            "span",
            {
                "class": "pdf_line",
                "id": f"p{self.id_counter}",
                "title": f"bbox {round_coordinates(line.x0)} {round_coordinates(line.y0)} {round_coordinates(line.x1)} {round_coordinates(line.y1)}",
            },
        )
        self.id_counter += 1

        # Add words
        for word in line.words:
            self._add_word_to_hocr_xml(line_span, word)

    def _add_word_to_hocr_xml(self, parent: ET._Element, word: HOCRWord):
        """Add a word to hOCR XML using lxml."""
        # Build word attributes
        attrs = {
            "class": "pdf_word",
            "id": f"p{self.id_counter}",
            "title": f"bbox {round_coordinates(word.x0)} {round_coordinates(word.y0)} {round_coordinates(word.x1)} {round_coordinates(word.y1)}",
        }

        # Build CSS style for font properties
        style_parts = []

        if word.font_family:
            style_parts.append(
                f'font-family: "{convert_html_entities(word.font_family)}"'
            )
        if word.font_size:
            style_parts.append(f"font-size: {round_coordinates(word.font_size)}pt")
        if word.font_weight:
            style_parts.append(
                f"font-weight: {convert_html_entities(word.font_weight)}"
            )
        if word.font_style:
            style_parts.append(f"font-style: {convert_html_entities(word.font_style)}")
        if word.color:
            style_parts.append(f"fill: {convert_html_entities(word.color)}")
        if word.baseline:
            style_parts.append(f"baseline: {round_coordinates(word.baseline)}")

        # Add style attribute if we have any styles
        if style_parts:
            attrs["style"] = "; ".join(style_parts)

        word_span = ET.SubElement(parent, "span", attrs)
        word_span.text = convert_html_entities(word.text)
        self.id_counter += 1

    def _add_image_to_hocr_xml(self, parent: ET._Element, image: Dict[str, Any]):
        """Add an image to hOCR XML using lxml."""
        img_div = ET.SubElement(
            parent,
            "div",
            {
                "class": "pdf_image",
                "id": f"p{self.id_counter}",
                "title": f"bbox {round_coordinates(image['x0'])} {round_coordinates(image['y0'])} {round_coordinates(image['x1'])} {round_coordinates(image['y1'])}",
            },
        )
        self.id_counter += 1

        if image.get("alt_text"):
            caption_span = ET.SubElement(img_div, "span", {"class": "pdf_caption"})
            caption_span.text = convert_html_entities(image["alt_text"])

    def _add_graphic_to_hocr_xml(self, parent: ET._Element, graphic: Dict[str, Any]):
        """Add a graphic to hOCR XML using lxml."""
        graphic_div = ET.SubElement(
            parent,
            "div",
            {
                "class": "pdf_graphic",
                "id": f"p{self.id_counter}",
                "title": f"bbox {round_coordinates(graphic['x0'])} {round_coordinates(graphic['y0'])} {round_coordinates(graphic['x1'])} {round_coordinates(graphic['y1'])}",
            },
        )
        self.id_counter += 1

        if graphic.get("svg_data"):
            # Parse SVG data and add as child element
            try:
                svg_element = ET.fromstring(graphic["svg_data"])
                graphic_div.append(svg_element)
            except ET.XMLSyntaxError:
                # If SVG is malformed, add as text
                graphic_div.text = convert_html_entities(graphic["svg_data"])

    def save_hocr(self, output_path: Union[str, Path]) -> Path:
        """
        Save hOCR output to file.

        Args:
            output_path: Path to save the hOCR file

        Returns:
            Path to the saved file
        """
        output_path = Path(output_path)

        # Ensure .hocr extension
        if not output_path.suffix.lower() in [".hocr", ".xml", ".html"]:
            output_path = output_path.with_suffix(".hocr")

        hocr_xml = self.generate_hocr_xml()

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(hocr_xml)

        logger.info(f"✅ hOCR saved to: {output_path}")
        return output_path

    def get_document_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the document structure.

        Returns:
            Dictionary with document statistics
        """
        total_words = 0
        total_lines = 0
        total_paragraphs = 0
        total_images = 0
        total_graphics = 0

        for page in self.document.pages:
            for paragraph in page.paragraphs:
                total_paragraphs += 1
                for line in paragraph.lines:
                    total_lines += 1
                    total_words += len(line.words)
            total_images += len(page.images)
            total_graphics += len(page.graphics)

        return {
            "title": self.document.title,
            "pages": len(self.document.pages),
            "paragraphs": total_paragraphs,
            "lines": total_lines,
            "words": total_words,
            "images": total_images,
            "graphics": total_graphics,
            "created_date": self.document.created_date,
            "creator": self.document.creator,
        }


def create_hocr_from_pdfplumber_data(pdfplumber_data: List[Dict]) -> HOCRBuilder:
    """
    Create hOCR from PDFPlumber extracted data.

    Args:
        pdfplumber_data: List of page data from PDFPlumber

    Returns:
        HOCRBuilder instance with populated data
    """
    builder = HOCRBuilder("PDF Document")

    for page_data in pdfplumber_data:
        page_num = page_data.get("page_num", 1)
        width = page_data.get("width", 612)  # Default letter size
        height = page_data.get("height", 792)

        page = builder.add_page(page_num, width, height)

        # Process text blocks
        text_blocks = page_data.get("text_blocks", [])
        if text_blocks:
            # Group text blocks by approximate line (y position)
            lines = {}
            for block in text_blocks:
                text = block.get("text", "")
                x0 = block.get("x0", 0)
                y0 = block.get("y0", 0)
                x1 = block.get("x1", 0)
                y1 = block.get("y1", 0)
                fontname = block.get("fontname", "Arial")
                size = block.get("size", 12)
                color = block.get("color", "#000000")

                # Group by y position (within 5 points)
                y_key = round(y0 / 5) * 5
                if y_key not in lines:
                    lines[y_key] = []
                lines[y_key].append(
                    {
                        "text": text,
                        "x0": x0,
                        "y0": y0,
                        "x1": x1,
                        "y1": y1,
                        "fontname": fontname,
                        "size": size,
                        "color": color,
                    }
                )

            # Create one paragraph with all lines
            paragraph = builder.add_paragraph()

            # Sort lines by y position
            for y_key in sorted(lines.keys()):
                line_blocks = lines[y_key]
                line = builder.add_line()

                # Sort blocks within line by x position
                line_blocks.sort(key=lambda b: b["x0"])

                for block in line_blocks:
                    # Use font decomposition for better style extraction
                    builder.add_word_with_font_name(
                        text=block["text"],
                        x0=block["x0"],
                        y0=block["y0"],
                        x1=block["x1"],
                        y1=block["y1"],
                        confidence=0.95,  # Default confidence for PDF text
                        font_name=block["fontname"],
                        font_size=block["size"],
                        color=block["color"],
                    )

        # Process images
        for image_data in page_data.get("images", []):
            builder.add_image(
                x0=image_data.get("x0", 0),
                y0=image_data.get("y0", 0),
                x1=image_data.get("x1", 0),
                y1=image_data.get("y1", 0),
                alt_text=image_data.get("alt_text", "Image"),
            )

        # Process graphics
        for graphic_data in page_data.get("graphics", []):
            svg_data = f'<svg width="{graphic_data["x1"]-graphic_data["x0"]}" height="{graphic_data["y1"]-graphic_data["y0"]}"><rect x="0" y="0" width="100%" height="100%" fill="{graphic_data.get("fill", "#ffffff")}" stroke="{graphic_data.get("stroke", "#000000")}"/></svg>'
            builder.add_graphic(
                graphic_type=graphic_data.get("type", "rect"),
                x0=graphic_data.get("x0", 0),
                y0=graphic_data.get("y0", 0),
                x1=graphic_data.get("x1", 0),
                y1=graphic_data.get("y1", 0),
                svg_data=svg_data,
            )

    return builder


def create_hocr_from_tesseract_data(tesseract_data: Dict) -> HOCRBuilder:
    """
    Create hOCR from Tesseract OCR data.

    Args:
        tesseract_data: Dictionary with Tesseract OCR results

    Returns:
        HOCRBuilder instance with populated data
    """
    builder = HOCRBuilder("OCR Document")

    for page_data in tesseract_data.get("pages", []):
        page_number = page_data.get("page_number", 1)
        width = page_data.get("width", 612)
        height = page_data.get("height", 792)

        page = builder.add_page(page_number, width, height)

        # Process content areas
        for area in page_data.get("areas", []):
            for paragraph_data in area.get("paragraphs", []):
                paragraph = builder.add_paragraph()

                for line_data in paragraph_data.get("lines", []):
                    line = builder.add_line()

                    for word_data in line_data.get("words", []):
                        confidence = word_data.get("confidence", 100) / 100.0
                        builder.add_word(
                            text=word_data["text"],
                            x0=word_data["bbox"][0],
                            y0=word_data["bbox"][1],
                            x1=word_data["bbox"][2],
                            y1=word_data["bbox"][3],
                            confidence=confidence,
                        )

        # Process images
        for image_data in page_data.get("images", []):
            builder.add_image(
                x0=image_data["bbox"][0],
                y0=image_data["bbox"][1],
                x1=image_data["bbox"][2],
                y1=image_data["bbox"][3],
            )

    return builder
