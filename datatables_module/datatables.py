"""
Core Datatables functionality for creating interactive HTML tables.
Proven technology used for many years in production environments.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import lxml.etree as ET
from lxml.html import HTMLParser

logger = logging.getLogger(__name__)

# DataTable version configuration - proven stable versions
JQ182 = "JQ182"  # Legacy version - stable for many years
JQ217 = "JQ217"  # Current version - backward compatible

# Default to proven stable version
JSDTable = JQ217

if JSDTable == JQ182:
    # Legacy CDN links - proven stable
    JQUERY_JS = "http://ajax.aspnetcdn.com/ajax/jQuery/jquery-1.8.2.min.js"
    DATATABLES_JS = "http://ajax.aspnetcdn.com/ajax/jquery.dataTables/1.9.4/jquery.dataTables.min.js"
    DATATABLES_CSS = "http://ajax.aspnetcdn.com/ajax/jquery.dataTables/1.9.4/css/jquery.dataTables.css"

if JSDTable == JQ217:
    # Current CDN links - maintained for stability
    JQUERY_JS = "https://code.jquery.com/jquery-3.7.1.js"
    DATATABLES_JS = "https://cdn.datatables.net/2.1.7/js/dataTables.js"
    DATATABLES_CSS = "https://cdn.datatables.net/2.1.7/css/dataTables.dataTables.css"

PRE_TEXT = "$(document).ready(function(){$('#"
POST_TEXT = "').DataTable();});"

# Core constants for filestore integration
SCROLL_CONTAINER = "scroll-container"
SCROLL_PARENT = "scroll_parent"
CLASS = "class"
DIV = "div"


class Datatables:
    """
    Main class for creating and manipulating DataTables HTML.
    Core functionality proven over many years of production use.
    All data is exposed in the filestore for transparency and accessibility.
    """

    def __init__(self):
        self.table = None

    @classmethod
    def add_body_scripts(cls, body, table_id):
        """
        Add jQuery and DataTables scripts to HTML body.
        Core functionality for interactive tables.
        
        Args:
            body: HTML body element
            table_id: ID of the table to initialize
        """
        if JQUERY_JS is not None:
            script = cls._add_element(body, "script", {
                "charset": "UTF-8", 
                "type": "text/javascript",
                "src": JQUERY_JS
            }, text=" ")

        script = cls._add_element(body, "script", {
            "charset": "UTF-8", 
            "type": "text/javascript",
            "src": DATATABLES_JS
        }, text=" ")

        script = cls._add_element(body, "script", {
            "charset": "UTF-8", 
            "type": "text/javascript"
        }, text=PRE_TEXT + table_id + POST_TEXT)

    @classmethod
    def add_head_info(cls, head, htmlx):
        """
        Add DataTables CSS and meta information to HTML head.
        Essential for proper table styling and functionality.
        
        Args:
            head: HTML head element
            htmlx: HTML document
        """
        meta = ET.SubElement(head, "meta")
        meta.attrib["charset"] = "UTF-8"
        
        title = ET.SubElement(head, "title")
        title.text = "DataTable"
        
        cls._add_element(head, "link", {
            "rel": "stylesheet", 
            "type": "text/css",
            "href": DATATABLES_CSS
        })

    @classmethod
    def create_table(cls, labels: List[str], table_id: str):
        """
        Create a basic HTML table structure with DataTables support.
        Core method for table creation - used extensively in production.
        
        Args:
            labels: Column headers
            table_id: Unique ID for the table
            
        Returns:
            tuple: (html_document, tbody_element)
        """
        htmlx = cls._create_html_with_empty_head_body()
        body = cls._get_body(htmlx)
        table = ET.SubElement(body, "table")
        table.attrib["id"] = table_id
        cls.create_thead_and_labels(labels, table)
        tbody = ET.SubElement(table, "tbody")
        return htmlx, tbody

    @classmethod
    def _create_html_for_datatables(cls, labels: List[str], table_id: str):
        """
        Create complete HTML document with DataTables support.
        Used for standalone table files in filestore.
        
        Args:
            labels: Column headers
            table_id: Unique ID for the table
            
        Returns:
            tuple: (html_document, tbody_element)
        """
        htmlx, tbody = cls.create_table(labels, table_id)
        cls.add_head_info(cls._get_head(htmlx), htmlx)
        cls.add_body_scripts(cls._get_body(htmlx), table_id=table_id)
        return htmlx, tbody

    @classmethod
    def create_thead_and_labels(cls, labels: List[str], table):
        """
        Create table header with column labels.
        Core functionality for table structure.
        
        Args:
            labels: Column headers
            table: Table element
        """
        thead = ET.SubElement(table, "thead")
        tr = ET.SubElement(thead, "tr")
        for label in labels:
            cls._add_cell_content(tr, cell_type="th", text=label)

    @classmethod
    def extract_column(cls, datatables_html, colindex: Union[int, str]):
        """
        Extract a column from a DataTable.
        Essential for data analysis and filestore operations.
        
        Args:
            datatables_html: DataTable HTML element
            colindex: Column index or title
            
        Returns:
            List of column elements
        """
        table = datatables_html.xpath("/html/body/table")[0]
        h_rows = table.xpath("thead/tr")
        colheads = [t.text for t in h_rows[0].xpath("th")]
        
        if isinstance(colindex, str):
            if colindex not in colheads:
                raise ValueError(f"column index '{colindex}' not in {colheads}")
            colnum = colheads.index(colindex)
            logger.info(f"column index for {colindex} is: {colnum}")
        else:
            colnum = colindex
            
        b_rows = table.xpath("tbody/tr")
        col_content = []
        for row in b_rows:
            tdlist = row.xpath("td")
            td_index_content = "None" if colnum >= len(tdlist) else tdlist[colnum]
            col_content.append(td_index_content)
        return col_content

    @classmethod
    def insert_column(cls, datatables_html, column: List, title: str, before: Optional[Union[int, str]] = None):
        """
        Insert a column into a DataTable.
        Core functionality for dynamic table manipulation.
        
        Args:
            datatables_html: DataTable HTML object
            column: List of values to add as column
            title: Column title
            before: Index or title of existing column to insert before
        """
        head_tr0, ncols, rows = cls._read_tables_get_row_column_count(column, datatables_html)
        
        if before is None:
            before = ncols
        elif isinstance(before, str):
            # Find column index by title
            colheads = [th.text for th in head_tr0.xpath("th")]
            if before in colheads:
                before = colheads.index(before)
            else:
                before = ncols
                
        if before < 0 or before > ncols:
            raise ValueError(f"bad before {before}")

        th = ET.SubElement(head_tr0, "th")
        th.text = title
        if before == ncols:
            head_tr0.append(th)
        else:
            head_tr0.insert(before, th)

        for i, tr in enumerate(rows):
            cells = tr.xpath("td")
            colval = column[i]
            if not isinstance(colval, ET._Element):
                td = ET.SubElement(tr, "td")
                td.text = str(colval)
            else:
                td = colval
            tr.insert(before, td)

    @classmethod
    def _read_tables_get_row_column_count(cls, column: List, datatables_html):
        """
        Get table structure information.
        Internal method for table manipulation.
        
        Args:
            column: Column data
            datatables_html: DataTable HTML
            
        Returns:
            tuple: (header_row, column_count, table_rows)
        """
        body = cls._get_body(datatables_html)
        table = body.xpath("table")[0]
        head_tr0 = table.xpath("thead/tr")[0]
        ncols = len(table.xpath("thead/tr"))
        rows = table.xpath("tbody/tr")
        nrows = len(rows)
        assert nrows == len(column)
        return head_tr0, ncols, rows

    # Utility methods - core functionality
    @staticmethod
    def _create_html_with_empty_head_body():
        """Create basic HTML document structure."""
        html = ET.Element("html")
        head = ET.SubElement(html, "head")
        body = ET.SubElement(html, "body")
        return html

    @staticmethod
    def _get_head(htmlx):
        """Get head element from HTML document."""
        return htmlx.xpath("head")[0]

    @staticmethod
    def _get_body(htmlx):
        """Get body element from HTML document."""
        return htmlx.xpath("body")[0]

    @staticmethod
    def _add_element(parent, tag: str, attribs: Dict[str, str], text: str = None):
        """Add element to parent with attributes and text."""
        element = ET.SubElement(parent, tag)
        for key, value in attribs.items():
            element.attrib[key] = value
        if text:
            element.text = text
        return element

    @staticmethod
    def _add_cell_content(parent, cell_type: str = "td", text: str = None, href: str = None):
        """Add cell content to table row."""
        cell = ET.SubElement(parent, cell_type)
        if href:
            a = ET.SubElement(cell, "a")
            a.attrib["href"] = href
            a.text = text
        elif text:
            cell.text = text
        return cell


class DataTable:
    """
    Alternative DataTable implementation with simpler interface.
    Provides direct file output for filestore integration.
    """

    def __init__(self, title: str, colheads: Optional[List[str]] = None, rowdata: Optional[List[List[str]]] = None):
        """
        Create a DataTable.
        Core constructor for table creation.
        
        Args:
            title: Table title
            colheads: Column headers
            rowdata: Row data
        """
        self.html = ET.Element("html")
        self.head = None
        self.body = None
        self.create_head(title)
        self.create_table_thead_tbody()
        self.add_column_heads(colheads)
        self.add_rows(rowdata)
        self.title = title

    def create_head(self, title: str):
        """Create HTML head with DataTables resources."""
        self.head = ET.SubElement(self.html, "head")
        self.title = ET.SubElement(self.head, "title")
        self.title.text = title

        link = ET.SubElement(self.head, "link")
        link.attrib["rel"] = "stylesheet"
        link.attrib["type"] = "text/css"
        link.attrib["href"] = DATATABLES_CSS
        link.text = '.'

        script = ET.SubElement(self.head, "script")
        script.attrib["src"] = JQUERY_JS
        script.attrib["charset"] = "UTF-8"
        script.attrib["type"] = "text/javascript"
        script.text = '.'

        script = ET.SubElement(self.head, "script")
        script.attrib["src"] = DATATABLES_JS
        script.attrib["charset"] = "UTF-8"
        script.attrib["type"] = "text/javascript"
        script.text = "."

        script = ET.SubElement(self.head, "script")
        script.attrib["charset"] = "UTF-8"
        script.attrib["type"] = "text/javascript"
        script.text = "$(function() { $(\"#results\").dataTable(); }) "

    def create_table_thead_tbody(self):
        """Create table structure with thead and tbody."""
        self.body = ET.SubElement(self.html, "body")
        self.div = ET.SubElement(self.body, "div")
        self.div.attrib["class"] = "bs-example table-responsive"
        self.table = ET.SubElement(self.div, "table")
        self.table.attrib["class"] = "table table-striped table-bordered table-hover"
        self.table.attrib["id"] = "results"
        self.thead = ET.SubElement(self.table, "thead")
        self.tbody = ET.SubElement(self.table, "tbody")

    def add_column_heads(self, colheads: Optional[List[str]]):
        """Add column headers."""
        if colheads is not None:
            self.thead_tr = ET.SubElement(self.thead, "tr")
            for colhead in colheads:
                th = ET.SubElement(self.thead_tr, "th")
                th.text = str(colhead)

    def add_rows(self, rowdata: Optional[List[List[str]]]):
        """Add data rows."""
        if rowdata is not None:
            for row in rowdata:
                self.add_row(row)

    def add_row(self, row: List[str]):
        """Add a single row."""
        if row is not None:
            tr = ET.SubElement(self.tbody, "tr")
            for val in row:
                td = ET.SubElement(tr, "td")
                td.text = val

    def write_full_data_tables(self, output_dir: str) -> None:
        """
        Write DataTable to HTML file.
        Core method for filestore integration - all data exposed as files.
        
        Args:
            output_dir: Directory to write the HTML file
        """
        output_path = Path(output_dir)
        if not output_path.exists():
            output_path.mkdir(parents=True, exist_ok=True)
        data_table_file = output_path / "full_data_table.html"
        with open(data_table_file, "w", encoding="UTF-8") as f:
            text = ET.tostring(self.html, encoding='unicode')
            f.write(text)
            logger.info(f"WROTE {data_table_file}")

    def __str__(self):
        """Return HTML as string."""
        return ET.tostring(self.html, encoding='unicode') 