"""
HTML table utilities for working with DataTables.
"""

import collections
import logging
from typing import Dict, List, Optional, Any
import lxml.etree as ET

logger = logging.getLogger(__name__)


class HtmlTable:
    """
    Utility class for HTML table operations.
    """

    @classmethod
    def create_html_table(cls, dict_by_id: Dict, transform_dict: Optional[Dict] = None, 
                         styles: Optional[List[str]] = None, datatables: bool = True, 
                         table_id: Optional[str] = None):
        """
        Create HTML table from JSON data.
        
        Args:
            dict_by_id: Dictionary with data organized by ID
            transform_dict: Optional transformation dictionary
            styles: Optional CSS styles
            datatables: Whether to enable DataTables
            table_id: Unique table ID
            
        Returns:
            tuple: (html_document, table_element)
        """
        if table_id is None:
            table_id = "table999"
            
        if not isinstance(dict_by_id, collections.OrderedDict):
            logger.warning(f"not an OrderedDict {type(dict_by_id)}")
            return None
            
        row_keys = list(dict_by_id.keys())
        if len(row_keys) == 0:
            logger.warning(f"empty JSON table")
            return None
            
        body, htmlx = cls.create_html_with_body(styles=styles, datatables=datatables, table_id=table_id)
        table = ET.SubElement(body, "table")
        table.attrib["id"] = table_id

        row0 = dict_by_id.get(row_keys[0])
        cls.add_column_headings(row0, table)

        cls.add_rows(dict_by_id, row_keys, table, transform_dict)
        
        if datatables:
            from .datatables import Datatables
            Datatables.add_body_scripts(body, table_id)
            
        return htmlx, table

    @classmethod
    def create_html_with_body(cls, styles: Optional[List[str]] = None, 
                             datatables: bool = False, table_id: Optional[str] = None):
        """
        Create HTML document with body and optional styles/DataTables.
        
        Args:
            styles: Optional CSS styles
            datatables: Whether to enable DataTables
            table_id: Table ID for DataTables
            
        Returns:
            tuple: (body_element, html_document)
        """
        htmlx = cls.create_html_with_empty_head_body()
        head = cls.get_or_create_head(htmlx)
        
        if datatables:
            from .datatables import Datatables
            Datatables.add_head_info(head, htmlx)

        if styles and len(styles) > 0:
            for style_t in styles:
                style = ET.SubElement(cls.get_head(htmlx), "style")
                style.text = style_t
                
        body = cls.get_body(htmlx)
        return body, htmlx

    @classmethod
    def add_column_headings(cls, row0: Dict, table):
        """
        Add column headings to table.
        
        Args:
            row0: First row data (used for column names)
            table: Table element
        """
        effective = logger.getEffectiveLevel()
        logger.setLevel(logging.WARNING)
        thead = ET.SubElement(table, "thead")
        col_items = row0.items()
        col_keys = [col_item[0] for col_item in col_items]
        logger.warning(f"keys {col_keys}")
        logger.debug(f"col_keys {col_keys}")
        tr = ET.SubElement(thead, "tr")
        for col_key in col_keys:
            th = ET.SubElement(tr, "th")
            th.text = col_key
        logger.setLevel(effective)

    @classmethod
    def add_rows(cls, dict_by_id: Dict, row_keys: List, table, transform_dict: Optional[Dict]):
        """
        Add rows to table from dictionary data.
        
        Args:
            dict_by_id: Data dictionary
            row_keys: Row keys
            table: Table element
            transform_dict: Optional transformation dictionary
        """
        new_level = logging.WARNING
        effective = logger.getEffectiveLevel()
        logger.setLevel(new_level)
        tbody = ET.SubElement(table, "tbody")
        for row_key in row_keys:
            cls._add_row(dict_by_id, row_key, tbody, transform_dict)
        logger.setLevel(effective)

    @classmethod
    def _add_row(cls, dict_by_id: Dict, row_key: str, tbody, transform_dict: Optional[Dict]):
        """
        Add a single row to table.
        
        Args:
            dict_by_id: Data dictionary
            row_key: Key for this row
            tbody: Table body element
            transform_dict: Optional transformation dictionary
        """
        row_data = dict_by_id.get(row_key)
        if row_data is None:
            return
            
        tr = ET.SubElement(tbody, "tr")
        for key, value in row_data.items():
            td = ET.SubElement(tr, "td")
            if transform_dict and key in transform_dict:
                # Apply transformation if available
                transformed_value = transform_dict[key](value)
                td.text = str(transformed_value)
            else:
                td.text = str(value)

    @classmethod
    def make_skeleton_table(cls, colheads: List[str]):
        """
        Create a skeleton table with headers.
        
        Args:
            colheads: Column headers
            
        Returns:
            tuple: (html_document, tbody_element)
        """
        htmlx = cls.create_html_with_empty_head_body()
        body = cls.get_body(htmlx)
        table = ET.SubElement(body, "table")
        thead = ET.SubElement(table, "thead")
        tr = ET.SubElement(thead, "tr")
        
        for colhead in colheads:
            th = ET.SubElement(tr, "th")
            th.text = colhead
            
        tbody = ET.SubElement(table, "tbody")
        return htmlx, tbody

    @classmethod
    def add_cell_content(cls, tr, cell_type: str = "td", text: str = None, href: str = None):
        """
        Add cell content to table row.
        
        Args:
            tr: Table row element
            cell_type: Cell type (td or th)
            text: Cell text content
            href: Optional link URL
            
        Returns:
            Cell element
        """
        cell = ET.SubElement(tr, cell_type)
        if href:
            a = ET.SubElement(cell, "a")
            a.attrib["href"] = href
            a.text = text
        elif text:
            cell.text = text
        return cell

    # Utility methods
    @staticmethod
    def create_html_with_empty_head_body():
        """Create basic HTML document structure."""
        html = ET.Element("html")
        head = ET.SubElement(html, "head")
        body = ET.SubElement(html, "body")
        return html

    @staticmethod
    def get_or_create_head(htmlx):
        """Get or create head element."""
        heads = htmlx.xpath("head")
        if heads:
            return heads[0]
        else:
            return ET.SubElement(htmlx, "head")

    @staticmethod
    def get_head(htmlx):
        """Get head element from HTML document."""
        return htmlx.xpath("head")[0]

    @staticmethod
    def get_body(htmlx):
        """Get body element from HTML document."""
        return htmlx.xpath("body")[0]

    @staticmethod
    def write_html_file(htmlx, outfile, debug: bool = False):
        """
        Write HTML document to file.
        
        Args:
            htmlx: HTML document
            outfile: Output file path
            debug: Enable debug logging
        """
        if debug:
            logger.info(f"writing HTML to {outfile}")
            
        with open(outfile, "w", encoding="UTF-8") as f:
            text = ET.tostring(htmlx, encoding='unicode', pretty_print=True)
            f.write(text) 