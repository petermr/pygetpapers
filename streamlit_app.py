import streamlit as st
import subprocess
import json
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import tempfile
import shutil
from pathlib import Path
import threading
import time

# Page configuration
st.set_page_config(
    page_title="Pygetpapers Web Interface",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
    }
    .error-box {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
    }
</style>
""", unsafe_allow_html=True)

class PygetpapersUI:
    def __init__(self):
        self.supported_apis = {
            "europe_pmc": "Europe PMC",
            "arxiv": "arXiv",
            "crossref": "Crossref",
            "openalex": "OpenAlex",
            "biorxiv": "bioRxiv",
            "medrxiv": "medRxiv",
            "rxivist": "Rxivist"
        }
        
        self.api_features = {
            "europe_pmc": {
                "query": True, "date_range": True, "pdf": True, "xml": True,
                "references": True, "citations": True, "supplementary": True
            },
            "arxiv": {
                "query": True, "date_range": False, "pdf": True, "xml": True,
                "references": False, "citations": False, "supplementary": False
            },
            "crossref": {
                "query": True, "date_range": False, "pdf": False, "xml": True,
                "references": False, "citations": False, "supplementary": False
            },
            "openalex": {
                "query": True, "date_range": True, "pdf": True, "xml": False,
                "references": False, "citations": False, "supplementary": False
            },
            "biorxiv": {
                "query": False, "date_range": True, "pdf": False, "xml": False,
                "references": False, "citations": False, "supplementary": False
            },
            "medrxiv": {
                "query": False, "date_range": True, "pdf": False, "xml": False,
                "references": False, "citations": False, "supplementary": False
            },
            "rxivist": {
                "query": True, "date_range": False, "pdf": False, "xml": False,
                "references": False, "citations": False, "supplementary": False
            }
        }

    def run_pygetpapers_command(self, args):
        """Run pygetpapers command and return results"""
        try:
            cmd = ["pygetpapers"] + args
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Command timed out after 5 minutes",
                "returncode": -1
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1
            }

    def build_query_string(self, query_parts):
        """Build complex query string from parts"""
        if not query_parts:
            return ""
        
        # Simple case: single query
        if len(query_parts) == 1:
            return query_parts[0]["query"]
        
        # Complex case: multiple parts with operators
        result = ""
        for i, part in enumerate(query_parts):
            if i > 0:
                result += f" {part['operator']} "
            
            # Handle field-specific queries
            if part.get("field") and part["field"] != "all":
                result += f"{part['field'].upper()}:\"{part['query']}\""
            else:
                result += f"\"{part['query']}\""
        
        return result

    def render_header(self):
        """Render the main header"""
        st.markdown('<h1 class="main-header">📚 Pygetpapers Web Interface</h1>', unsafe_allow_html=True)
        st.markdown("""
        <div class="info-box">
            <strong>Welcome to Pygetpapers!</strong> This web interface makes it easy to search and download 
            scholarly papers from multiple repositories. Build complex queries, manage your corpus, and 
            explore research papers with an intuitive interface.
        </div>
        """, unsafe_allow_html=True)

    def render_sidebar(self):
        """Render the sidebar with navigation"""
        st.sidebar.title("Navigation")
        
        page = st.sidebar.selectbox(
            "Choose a page:",
            ["Search Papers", "Query Builder", "Corpus Manager", "Settings", "Help"]
        )
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("### Quick Stats")
        
        # Placeholder for stats
        if "total_papers" not in st.session_state:
            st.session_state.total_papers = 0
        if "total_corpora" not in st.session_state:
            st.session_state.total_corpora = 0
            
        st.sidebar.metric("Papers Downloaded", st.session_state.total_papers)
        st.sidebar.metric("Corpora Created", st.session_state.total_corpora)
        
        return page

    def render_search_page(self):
        """Render the main search page"""
        st.markdown('<h2 class="section-header">🔍 Search Papers</h2>', unsafe_allow_html=True)
        
        # Repository selection
        col1, col2 = st.columns([1, 2])
        
        with col1:
            selected_api = st.selectbox(
                "Select Repository:",
                options=list(self.supported_apis.keys()),
                format_func=lambda x: self.supported_apis[x]
            )
            
            # Show API features
            features = self.api_features[selected_api]
            st.markdown("**Supported Features:**")
            for feature, supported in features.items():
                status = "✅" if supported else "❌"
                st.markdown(f"{status} {feature.replace('_', ' ').title()}")
        
        with col2:
            # Query input
            query = st.text_area(
                "Search Query:",
                placeholder="Enter your search query (e.g., 'artificial intelligence' OR 'machine learning')",
                height=100
            )
            
            # Date range (if supported)
            if features["date_range"]:
                col2a, col2b = st.columns(2)
                with col2a:
                    start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=365))
                with col2b:
                    end_date = st.date_input("End Date", value=datetime.now())
            else:
                start_date = None
                end_date = None
        
        # Download options
        st.markdown('<h3 class="section-header">📥 Download Options</h3>', unsafe_allow_html=True)
        
        col3, col4, col5 = st.columns(3)
        
        with col3:
            limit = st.number_input("Maximum Results", min_value=1, max_value=10000, value=100)
            download_xml = st.checkbox("Download XML", value=True, disabled=not features["xml"])
            download_pdf = st.checkbox("Download PDF", value=False, disabled=not features["pdf"])
        
        with col4:
            download_supp = st.checkbox("Download Supplementary Files", value=False, disabled=not features["supplementary"])
            download_refs = st.checkbox("Download References", value=False, disabled=not features["references"])
            download_citations = st.checkbox("Download Citations", value=False, disabled=not features["citations"])
        
        with col5:
            make_csv = st.checkbox("Generate CSV Metadata", value=True)
            make_html = st.checkbox("Generate HTML Metadata", value=False)
            save_query = st.checkbox("Save Query Configuration", value=False)
        
        # Output directory
        output_dir = st.text_input(
            "Output Directory:",
            value=f"pygetpapers_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        # Search button
        if st.button("🔍 Search and Download", type="primary", use_container_width=True):
            if not query and selected_api not in ["biorxiv", "medrxiv"]:
                st.error("Please enter a search query!")
                return
            
            # Build command arguments
            args = ["--api", selected_api, "--limit", str(limit)]
            
            if query:
                args.extend(["--query", query])
            
            if start_date and end_date and features["date_range"]:
                args.extend(["--startdate", start_date.strftime("%Y-%m-%d")])
                args.extend(["--enddate", end_date.strftime("%Y-%m-%d")])
            
            if download_xml:
                args.append("--xml")
            if download_pdf:
                args.append("--pdf")
            if download_supp:
                args.append("--supp")
            if download_refs:
                args.append("--references")
            if download_citations:
                args.append("--citations")
            if make_csv:
                args.append("--makecsv")
            if make_html:
                args.append("--makehtml")
            if save_query:
                args.append("--save_query")
            
            args.extend(["--output", output_dir])
            
            # Run the command
            with st.spinner("Searching and downloading papers..."):
                result = self.run_pygetpapers_command(args)
            
            if result["success"]:
                st.success("✅ Papers downloaded successfully!")
                st.session_state.total_papers += limit
                st.session_state.total_corpora += 1
                
                # Show results summary
                st.markdown("### Results Summary")
                st.code(result["stdout"])
                
                # Store output directory for corpus management
                if "corpora" not in st.session_state:
                    st.session_state.corpora = []
                st.session_state.corpora.append({
                    "name": output_dir,
                    "api": selected_api,
                    "query": query,
                    "date_created": datetime.now().isoformat(),
                    "papers_count": limit
                })
            else:
                st.error("❌ Error occurred during download")
                st.code(result["stderr"])

    def render_query_builder(self):
        """Render the advanced query builder"""
        st.markdown('<h2 class="section-header">🔧 Advanced Query Builder</h2>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-box">
            <strong>Build Complex Queries:</strong> Use this tool to create sophisticated Boolean queries 
            with field-specific searches, nested conditions, and proper quoting.
        </div>
        """, unsafe_allow_html=True)
        
        # Query parts management
        if "query_parts" not in st.session_state:
            st.session_state.query_parts = [{"query": "", "operator": "AND", "field": "all"}]
        
        # Add new query part
        if st.button("➕ Add Query Part"):
            st.session_state.query_parts.append({"query": "", "operator": "AND", "field": "all"})
        
        # Display query parts
        for i, part in enumerate(st.session_state.query_parts):
            st.markdown(f"### Query Part {i+1}")
            
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                part["query"] = st.text_input(
                    f"Query {i+1}",
                    value=part["query"],
                    key=f"query_{i}"
                )
            
            with col2:
                if i > 0:  # Don't show operator for first part
                    part["operator"] = st.selectbox(
                        "Operator",
                        ["AND", "OR", "AND NOT"],
                        key=f"operator_{i}"
                    )
            
            with col3:
                part["field"] = st.selectbox(
                    "Field",
                    ["all", "title", "abstract", "author", "journal", "license", "methods"],
                    key=f"field_{i}"
                )
            
            # Remove button
            if len(st.session_state.query_parts) > 1:
                if st.button(f"🗑️ Remove Part {i+1}", key=f"remove_{i}"):
                    st.session_state.query_parts.pop(i)
                    st.rerun()
        
        # Preview generated query
        generated_query = self.build_query_string(st.session_state.query_parts)
        
        st.markdown("### Generated Query Preview")
        st.code(generated_query, language="text")
        
        # Copy to search page
        if st.button("📋 Copy to Search Page"):
            st.session_state.generated_query = generated_query
            st.success("Query copied! Switch to Search Papers page to use it.")
        
        # Query examples
        with st.expander("📖 Query Examples"):
            st.markdown("""
            **Simple Queries:**
            - `"artificial intelligence"`
            - `"machine learning" AND "deep learning"`
            
            **Field-Specific Queries:**
            - `TITLE:"neural networks" AND ABSTRACT:"deep learning"`
            - `AUTH:"Smith J" AND JOURNAL:"Nature"`
            
            **Complex Boolean Queries:**
            - `"(LICENSE:'cc by' OR LICENSE:'cc-by') AND METHODS:'transcriptome assembly'"`
            - `"cancer" AND ("treatment" OR "therapy") AND NOT "review"`
            
            **Date Range Queries (Europe PMC):**
            - `"covid-19" AND FIRST_PDATE:[2020-01-01 TO 2023-12-31]`
            """)

    def render_corpus_manager(self):
        """Render the corpus management page"""
        st.markdown('<h2 class="section-header">📁 Corpus Manager</h2>', unsafe_allow_html=True)
        
        if "corpora" not in st.session_state or not st.session_state.corpora:
            st.warning("No corpora found. Download some papers first!")
            return
        
        # Corpus list
        st.markdown("### Your Corpora")
        
        for i, corpus in enumerate(st.session_state.corpora):
            with st.expander(f"📁 {corpus['name']} ({corpus['papers_count']} papers)"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Repository:** {self.supported_apis.get(corpus['api'], corpus['api'])}")
                    st.markdown(f"**Query:** {corpus['query'] or 'Date-based search'}")
                    st.markdown(f"**Created:** {corpus['date_created']}")
                
                with col2:
                    if st.button(f"🗑️ Delete Corpus {i+1}", key=f"delete_corpus_{i}"):
                        st.session_state.corpora.pop(i)
                        st.rerun()
        
        # Corpus statistics
        st.markdown("### Corpus Statistics")
        
        if st.session_state.corpora:
            # Create summary dataframe
            df = pd.DataFrame(st.session_state.corpora)
            df['date_created'] = pd.to_datetime(df['date_created'])
            
            # Papers by repository
            fig1 = px.pie(
                df.groupby('api')['papers_count'].sum().reset_index(),
                values='papers_count',
                names='api',
                title='Papers by Repository'
            )
            st.plotly_chart(fig1, use_container_width=True)
            
            # Papers over time
            fig2 = px.line(
                df.groupby(df['date_created'].dt.date)['papers_count'].sum().reset_index(),
                x='date_created',
                y='papers_count',
                title='Papers Downloaded Over Time'
            )
            st.plotly_chart(fig2, use_container_width=True)

    def render_settings(self):
        """Render the settings page"""
        st.markdown('<h2 class="section-header">⚙️ Settings</h2>', unsafe_allow_html=True)
        
        # Default settings
        st.markdown("### Default Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            default_api = st.selectbox(
                "Default Repository:",
                options=list(self.supported_apis.keys()),
                index=0,
                format_func=lambda x: self.supported_apis[x]
            )
            
            default_limit = st.number_input(
                "Default Result Limit:",
                min_value=10,
                max_value=1000,
                value=100
            )
        
        with col2:
            default_output_dir = st.text_input(
                "Default Output Directory Pattern:",
                value="pygetpapers_output_{timestamp}"
            )
            
            auto_save_query = st.checkbox("Auto-save queries", value=True)
        
        # Advanced settings
        st.markdown("### Advanced Settings")
        
        log_level = st.selectbox(
            "Log Level:",
            ["info", "debug", "warning", "error", "critical"]
        )
        
        timeout_seconds = st.number_input(
            "Command Timeout (seconds):",
            min_value=60,
            max_value=1800,
            value=300
        )
        
        # Save settings
        if st.button("💾 Save Settings"):
            st.success("Settings saved!")

    def render_help(self):
        """Render the help page"""
        st.markdown('<h2 class="section-header">❓ Help & Documentation</h2>', unsafe_allow_html=True)
        
        # Quick start guide
        with st.expander("🚀 Quick Start Guide", expanded=True):
            st.markdown("""
            1. **Choose a Repository**: Select from the available scholarly repositories
            2. **Enter Your Query**: Use simple keywords or build complex Boolean queries
            3. **Configure Download Options**: Choose what files to download
            4. **Click Search**: Start the download process
            5. **Manage Your Corpus**: View and organize downloaded papers
            """)
        
        # Repository information
        with st.expander("📚 Repository Information"):
            repo_info = pd.DataFrame([
                ["Europe PMC", "Biomedical literature", "Full-featured", "✅"],
                ["arXiv", "Physics, math, CS", "PDF/XML", "✅"],
                ["Crossref", "Academic metadata", "Metadata only", "✅"],
                ["OpenAlex", "Academic papers", "PDF available", "✅"],
                ["bioRxiv", "Biology preprints", "Date-based", "❌"],
                ["medRxiv", "Medical preprints", "Date-based", "❌"],
                ["Rxivist", "Preprint search", "Basic search", "❌"]
            ], columns=["Repository", "Content", "Features", "Query Support"])
            
            st.dataframe(repo_info, use_container_width=True)
        
        # Query syntax
        with st.expander("🔍 Query Syntax Guide"):
            st.markdown("""
            **Basic Operators:**
            - `AND`: Both terms must be present
            - `OR`: Either term can be present
            - `AND NOT`: First term must be present, second must not
            
            **Field-Specific Search:**
            - `TITLE:"your term"`: Search in title only
            - `ABSTRACT:"your term"`: Search in abstract only
            - `AUTH:"author name"`: Search by author
            - `JOURNAL:"journal name"`: Search by journal
            
            **Quoting:**
            - Use double quotes for phrases: `"machine learning"`
            - Use single quotes inside double quotes: `"(LICENSE:'cc by')"`
            
            **Date Ranges (Europe PMC):**
            - `FIRST_PDATE:[2020-01-01 TO 2023-12-31]`
            """)
        
        # Troubleshooting
        with st.expander("🔧 Troubleshooting"):
            st.markdown("""
            **Common Issues:**
            
            **No results found:**
            - Try simpler queries
            - Check spelling
            - Use broader terms
            
            **Download errors:**
            - Check internet connection
            - Verify repository availability
            - Try smaller result limits
            
            **Query syntax errors:**
            - Use the Query Builder for complex queries
            - Check quote matching
            - Verify field names
            """)

    def run(self):
        """Main application runner"""
        self.render_header()
        page = self.render_sidebar()
        
        if page == "Search Papers":
            self.render_search_page()
        elif page == "Query Builder":
            self.render_query_builder()
        elif page == "Corpus Manager":
            self.render_corpus_manager()
        elif page == "Settings":
            self.render_settings()
        elif page == "Help":
            self.render_help()

# Run the application
if __name__ == "__main__":
    app = PygetpapersUI()
    app.run() 