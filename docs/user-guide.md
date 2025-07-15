# Pygetpapers Streamlit UI - User Guide

## Getting Started

### Prerequisites

Before using the Pygetpapers Streamlit UI, ensure you have:

1. **Python 3.8 or higher** (3.12 supported) installed on your system
2. **pygetpapers** installed and accessible from command line
3. **Required dependencies** installed (see requirements.txt)

### Installation

1. **Install pygetpapers** (if not already installed):
   ```bash
   pip install pygetpapers
   ```

2. **Install Streamlit UI dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Streamlit application**:
   ```bash
   # Option 1: Use the convenience script (recommended)
   python run_streamlit.py
   
   # Option 2: Run directly with streamlit
   streamlit run streamlit_app.py --server.port 8502
   ```

4. **Access the web interface**:
   Open your browser and navigate to `http://localhost:8502`

## Interface Overview

The Streamlit UI is organized into five main pages:

1. **🔍 Search Papers** - Main search and download interface
2. **🔧 Query Builder** - Advanced query construction tool
3. **📁 Corpus Manager** - Manage downloaded paper collections
4. **⚙️ Settings** - Application configuration
5. **❓ Help** - Documentation and troubleshooting

## Page-by-Page Guide

### 🔍 Search Papers

This is the main page for searching and downloading papers.

#### Step 1: Select Repository

Choose from the available scholarly repositories:

- **Europe PMC**: Biomedical literature (most features)
- **arXiv**: Physics, mathematics, computer science
- **Crossref**: Academic metadata
- **OpenAlex**: Academic papers with PDF access
- **bioRxiv**: Biology preprints (date-based only)
- **medRxiv**: Medical preprints (date-based only)


Each repository shows its supported features with checkmarks.

#### Step 2: Enter Your Query

**Simple Queries:**
- Single terms: `"artificial intelligence"`
- Multiple terms: `"machine learning" AND "deep learning"`

**Complex Queries:**
- Field-specific: `TITLE:"neural networks" AND ABSTRACT:"deep learning"`
- Boolean operators: `"cancer" AND ("treatment" OR "therapy") AND NOT "review"`

**Date-based Queries (for supported repositories):**
- Use the date pickers to specify start and end dates
- The system will automatically format the query with date ranges

#### Step 3: Configure Download Options

**Basic Options:**
- **Maximum Results**: Set the number of papers to download (1-10,000)
- **Download XML**: Get full-text XML files (where available)
- **Download PDF**: Get PDF files (where available)

**Advanced Options:**
- **Download Supplementary Files**: Get additional materials (Europe PMC only)
- **Download References**: Get paper references (Europe PMC only)
- **Download Citations**: Get papers that cite this work (Europe PMC only)

**Metadata Options:**
- **Generate CSV Metadata**: Create CSV file with paper metadata
- **Generate HTML Metadata**: Create HTML file with paper metadata
- **Save Query Configuration**: Save the query for later use

#### Step 4: Set Output Directory

Specify where to save the downloaded papers:
- Default: `pygetpapers_output_YYYYMMDD_HHMMSS`
- Custom: Enter your preferred directory name

#### Step 5: Execute Search

Click the **"🔍 Search and Download"** button to start the process.

**What happens:**
1. The system validates your query and settings
2. pygetpapers command is executed in the background
3. Progress is shown with a spinner
4. Results are displayed upon completion

**Success indicators:**
- ✅ Green success message
- Command output displayed
- Corpus added to Corpus Manager
- Statistics updated in sidebar

**Error handling:**
- ❌ Red error message with details
- Command error output displayed
- Suggestions for troubleshooting

### 🔧 Query Builder

The Query Builder helps you construct complex Boolean queries visually.

#### Building a Query

**Step 1: Add Query Parts**
- Start with one query part
- Click **"➕ Add Query Part"** to add more

**Step 2: Configure Each Part**
- **Query**: Enter your search terms
- **Operator**: Choose AND, OR, or AND NOT (not shown for first part)
- **Field**: Select which field to search in

**Available Fields:**
- **all**: Search across all fields
- **title**: Search in paper titles only
- **abstract**: Search in abstracts only
- **author**: Search by author names
- **journal**: Search by journal names
- **license**: Search by license type
- **methods**: Search in methods sections

#### Query Preview

The **Generated Query Preview** shows your query in real-time as you build it.

**Example:**
```
TITLE:"machine learning" AND ABSTRACT:"deep learning" OR AUTH:"Smith J"
```

#### Using the Query

**Copy to Search Page:**
1. Click **"📋 Copy to Search Page"**
2. Switch to the Search Papers page
3. Your query will be pre-filled

**Query Examples:**
- `"artificial intelligence" AND "healthcare"`
- `TITLE:"neural networks" AND ABSTRACT:"deep learning"`
- `"(LICENSE:'cc by' OR LICENSE:'cc-by') AND METHODS:'transcriptome assembly'"`

### 📁 Corpus Manager

The Corpus Manager helps you organize and analyze your downloaded papers.

#### Viewing Corpora

Each corpus shows:
- **Name**: Directory name
- **Repository**: Source repository
- **Query**: Original search query
- **Created**: Date and time of creation
- **Papers**: Number of papers downloaded

#### Corpus Actions

**View Details:**
- Click the expander arrow to see corpus details
- View repository, query, and creation information

**Delete Corpus:**
- Click **"🗑️ Delete Corpus"** to remove from the list
- Note: This only removes from the UI, not from disk

#### Analytics

**Papers by Repository:**
- Pie chart showing distribution across repositories
- Hover for exact numbers

**Papers Over Time:**
- Line chart showing download activity
- Track your research progress

#### Statistics

The sidebar shows:
- **Total Papers Downloaded**: Cumulative count
- **Total Corpora Created**: Number of collections

### ⚙️ Settings

Configure default behavior and preferences.

#### Default Settings

**Repository:**
- Choose your preferred default repository
- Affects the initial selection on Search Papers page

**Result Limit:**
- Set default maximum number of results
- Range: 10-1000 papers

**Output Directory:**
- Define pattern for automatic directory naming
- Use `{timestamp}` for unique names

**Auto-save:**
- Automatically save query configurations
- Useful for repeated searches

#### Advanced Settings

**Log Level:**
- **info**: Standard information (default)
- **debug**: Detailed debugging information
- **warning**: Only warnings and errors
- **error**: Only errors
- **critical**: Only critical errors

**Command Timeout:**
- Maximum time for pygetpapers commands
- Range: 60-1800 seconds (1-30 minutes)
- Default: 300 seconds (5 minutes)

#### Saving Settings

Click **"💾 Save Settings"** to apply your changes.

### ❓ Help

Comprehensive documentation and troubleshooting.

#### Quick Start Guide

Step-by-step instructions for new users:
1. Choose a repository
2. Enter your query
3. Configure download options
4. Click search
5. Manage your corpus

#### Repository Information

Detailed comparison table showing:
- **Repository**: Name and description
- **Content**: Type of papers available
- **Features**: Available functionality
- **Query Support**: Query capabilities

#### Query Syntax Guide

**Basic Operators:**
- `AND`: Both terms must be present
- `OR`: Either term can be present
- `AND NOT`: First term must be present, second must not

**Field-Specific Search:**
- `TITLE:"your term"`: Search in title only
- `ABSTRACT:"your term"`: Search in abstract only
- `AUTH:"author name"`: Search by author
- `JOURNAL:"journal name"`: Search by journal

**Quoting Rules:**
- Use double quotes for phrases: `"machine learning"`
- Use single quotes inside double quotes: `"(LICENSE:'cc by')"`

**Date Ranges (Europe PMC):**
- `FIRST_PDATE:[2020-01-01 TO 2023-12-31]`

#### Troubleshooting

**Common Issues and Solutions:**

**No results found:**
- Try simpler queries
- Check spelling and terminology
- Use broader terms
- Verify repository content

**Download errors:**
- Check internet connection
- Verify repository availability
- Try smaller result limits
- Check disk space

**Query syntax errors:**
- Use the Query Builder for complex queries
- Check quote matching
- Verify field names
- Review operator usage

## Advanced Usage

### Complex Query Examples

**Multi-field Search:**
```
TITLE:"cancer" AND ABSTRACT:"treatment" AND AUTH:"Smith J"
```

**Boolean Logic:**
```
"artificial intelligence" AND ("machine learning" OR "deep learning") AND NOT "review"
```

**License and Method Search:**
```
"(LICENSE:'cc by' OR LICENSE:'cc-by') AND METHODS:'transcriptome assembly'"
```

**Date Range with Content:**
```
"covid-19" AND FIRST_PDATE:[2020-01-01 TO 2023-12-31]
```

### Repository-Specific Tips

**Europe PMC:**
- Best for biomedical research
- Supports all features
- Rich metadata and full-text access

**arXiv:**
- Excellent for computer science, physics, mathematics
- PDF and XML available
- No date range queries

**Crossref:**
- Good for metadata across all disciplines
- XML format only
- No PDF downloads

**OpenAlex:**
- Growing academic database
- PDF access for many papers
- Good for recent publications

**bioRxiv/medRxiv:**
- Preprint servers
- Date-based searches only
- No complex queries

### Best Practices

**Query Construction:**
1. Start simple and refine
2. Use specific terminology
3. Combine multiple search strategies
4. Test with small limits first

**File Management:**
1. Use descriptive output directory names
2. Organize by project or topic
3. Keep track of queries used
4. Regular cleanup of old corpora

**Performance:**
1. Use appropriate result limits
2. Avoid overly complex queries
3. Monitor download progress
4. Check available disk space

## Troubleshooting

### Common Error Messages

**"Command timed out":**
- Reduce result limit
- Check internet connection
- Try simpler query

**"API not supported":**
- Verify repository selection
- Check pygetpapers installation
- Update to latest version

**"No query specified":**
- Enter a search query
- Use date range for bioRxiv/medRxiv
- Check query syntax

**"Permission denied":**
- Check write permissions
- Use different output directory
- Verify disk space

### Getting Help

**Documentation:**
- Check the Help page
- Review query examples
- Consult repository information

**Technical Support:**
- Check pygetpapers documentation
- Verify installation
- Test command line version

**Community:**
- GitHub issues
- User forums
- Documentation updates

## Tips and Tricks

### Efficient Searching

1. **Use the Query Builder** for complex queries
2. **Start with small limits** to test queries
3. **Save successful queries** for reuse
4. **Use field-specific searches** for precision

### Corpus Management

1. **Organize by topic** or project
2. **Use descriptive names** for output directories
3. **Track your searches** in the Corpus Manager
4. **Analyze patterns** with the statistics

### Performance Optimization

1. **Choose appropriate repositories** for your needs
2. **Use efficient queries** to reduce processing time
3. **Monitor system resources** during large downloads
4. **Plan your searches** to avoid redundant downloads

This user guide should help you get the most out of the Pygetpapers Streamlit UI. For additional help, consult the Help page within the application or refer to the pygetpapers documentation. 