# DataTables Module

A standalone Python module for creating interactive HTML tables using jQuery DataTables. Extracted from the AmiLib project for use in pygetpapers Streamlit UI and other projects.

**Proven technology used for many years in production environments. All data is exposed in the filestore for transparency and accessibility.**

## Features

- **Proven Core Functionality**: DataTables technology used successfully for many years
- **Filestore Integration**: All data exposed as files for transparency and accessibility
- **Interactive HTML Tables**: Sorting, searching, and pagination
- **Stable Versions**: Support for proven DataTable versions (JQ182, JQ217)
- **Column Manipulation**: Extract, insert, and modify columns
- **Modal Popups**: Cell content display with modal windows
- **Scrollable Content**: Support for large datasets
- **JSON to HTML Conversion**: Transform data structures to interactive tables
- **Bootstrap Integration**: Modern styling and responsive design

## Why DataTables?

DataTables has been our core technology for many years because it provides:

- **Proven Stability**: Battle-tested in production environments
- **Rich Functionality**: Sorting, filtering, pagination, and more
- **File-Based Output**: All data exposed in the filestore
- **Browser Compatibility**: Works across all modern browsers
- **Extensibility**: Easy to customize and extend
- **Performance**: Handles large datasets efficiently

## Installation

```bash
pip install datatables-module
```

## Quick Start

```python
from datatables_module import Datatables, DataTable

# Create a simple DataTable
labels = ["Name", "Position", "Office", "Age", "Start date", "Salary"]
htmlx, tbody = Datatables.create_table(labels, "my_table")

# Add data rows
data = [
    ["John Doe", "Developer", "New York", "30", "2021/01/01", "$50000"],
    ["Jane Smith", "Manager", "London", "35", "2020/01/01", "$60000"],
]

for row in data:
    tr = tbody.makeelement("tr")
    for value in row:
        td = tr.makeelement("td")
        td.text = value
        tr.append(td)
    tbody.append(tr)

# Write to filestore - all data exposed as files
with open("table.html", "w", encoding="utf-8") as f:
    f.write(ET.tostring(htmlx, encoding='unicode', pretty_print=True))
```

## Filestore Integration

All data is exposed in the filestore for transparency and accessibility:

```python
from datatables_module import DataTable

# Create DataTable with data
colheads = ["Name", "Position", "Office"]
rowdata = [
    ["John Doe", "Developer", "New York"],
    ["Jane Smith", "Manager", "London"],
]

# Write to filestore - creates full_data_table.html
dt = DataTable("Employee Table", colheads, rowdata)
dt.write_full_data_tables("output_directory")
```

## Advanced Features

### Column Manipulation

```python
# Extract a column for analysis
column_data = Datatables.extract_column(html_doc, "Name")

# Insert a new column
new_column = ["Value 1", "Value 2", "Value 3"]
Datatables.insert_column(html_doc, new_column, "New Column", before="Age")
```

### HTML Table Creation from JSON

```python
from datatables_module import HtmlTable

# Create table from dictionary data
data = {
    "row1": {"Name": "John", "Age": "30"},
    "row2": {"Name": "Jane", "Age": "25"},
}

# Creates interactive table with all data in filestore
htmlx, table = HtmlTable.create_html_table(
    data, 
    datatables=True, 
    table_id="json_table"
)
```

## Configuration

The module supports different DataTable versions - all proven stable:

- **JQ182**: jQuery 1.8.2 + DataTables 1.9.4 (legacy - stable for many years)
- **JQ217**: jQuery 3.7.1 + DataTables 2.1.7 (current - backward compatible)

To change the version:

```python
from datatables_module.datatables import JSDTable, JQ182

# Use legacy version - proven stable
JSDTable = JQ182
```

## Dependencies

- **lxml**: XML/HTML processing
- **jQuery**: Client-side JavaScript (loaded from CDN)
- **DataTables**: Table enhancement library (loaded from CDN)

## Integration with Streamlit

This module is designed to work seamlessly with Streamlit applications while maintaining filestore integration:

```python
import streamlit as st
from datatables_module import Datatables

# Create DataTable
htmlx, tbody = Datatables.create_table(["Name", "Value"], "streamlit_table")

# Display in Streamlit
st.components.v1.html(
    ET.tostring(htmlx, encoding='unicode'),
    height=400
)

# Also write to filestore for transparency
with open("streamlit_table.html", "w", encoding="utf-8") as f:
    f.write(ET.tostring(htmlx, encoding='unicode', pretty_print=True))
```

## Filestore Benefits

Exposing all data in the filestore provides:

- **Transparency**: All data visible and accessible
- **Auditability**: Complete data trail
- **Reproducibility**: Data can be recreated from files
- **Integration**: Easy to integrate with other tools
- **Backup**: Data backed up with file system
- **Sharing**: Easy to share data files

## Production Usage

This module has been used in production for many years with:

- **Large Datasets**: Handles thousands of rows efficiently
- **Complex Queries**: Supports advanced filtering and sorting
- **Real-time Updates**: Dynamic table manipulation
- **Cross-browser Compatibility**: Works on all modern browsers
- **Accessibility**: Screen reader friendly

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

This module was extracted from the [AmiLib](https://github.com/amilib/amilib) project and adapted for standalone use. DataTables has been our core technology for many years, providing reliable and powerful table functionality. 