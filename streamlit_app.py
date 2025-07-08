"""
Pygetpapers Streamlit Web Interface

A comprehensive web interface for pygetpapers with advanced features including
query building, corpus management, data visualization, and fulltext search.
"""

import base64
import json
import logging
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import plotly.express as px
import streamlit as st

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from datatables_integration import PygetpapersDatatables
    from jats4r_integration import JATS4RConverter
except ImportError:
    # Fallback if modules are not available
    PygetpapersDatatables = None
    JATS4RConverter = None
    logger.warning("Some modules not available. Some features will be limited.")

# Page configuration
st.set_page_config(
    page_title="Pygetpapers Web Interface",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown(
    """
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
""",
    unsafe_allow_html=True,
)


class PygetpapersUI:
    def __init__(self):
        self.supported_apis = {
            "europe_pmc": "Europe PMC",
            "arxiv": "arXiv",
            "crossref": "Crossref",
            "openalex": "OpenAlex",
            "biorxiv": "bioRxiv",
            "medrxiv": "medRxiv",
            "rxivist": "Rxivist",
        }

        self.api_features = {
            "europe_pmc": {
                "query": True,
                "date_range": True,
                "pdf": True,
                "xml": True,
                "references": True,
                "citations": True,
                "supplementary": True,
            },
            "arxiv": {
                "query": True,
                "date_range": False,
                "pdf": True,
                "xml": True,
                "references": False,
                "citations": False,
                "supplementary": False,
            },
            "crossref": {
                "query": True,
                "date_range": False,
                "pdf": False,
                "xml": True,
                "references": False,
                "citations": False,
                "supplementary": False,
            },
            "openalex": {
                "query": True,
                "date_range": True,
                "pdf": True,
                "xml": False,
                "references": False,
                "citations": False,
                "supplementary": False,
            },
            "biorxiv": {
                "query": False,
                "date_range": True,
                "pdf": False,
                "xml": False,
                "references": False,
                "citations": False,
                "supplementary": False,
            },
            "medrxiv": {
                "query": False,
                "date_range": True,
                "pdf": False,
                "xml": False,
                "references": False,
                "citations": False,
                "supplementary": False,
            },
            "rxivist": {
                "query": True,
                "date_range": False,
                "pdf": False,
                "xml": False,
                "references": False,
                "citations": False,
                "supplementary": False,
            },
        }

        # Initialize datatables integration
        self.datatables = PygetpapersDatatables()

        # Initialize JATS4R converter
        self.jats4r_converter = None
        if JATS4RConverter:
            try:
                self.jats4r_converter = JATS4RConverter()
            except Exception as e:
                logger.warning(f"Failed to initialize JATS4R converter: {e}")

    def run_pygetpapers_command(self, args, progress_placeholder=None):
        """Run pygetpapers command and return results with real-time progress tracking"""
        try:
            # Try to use local development version first, fallback to installed version
            import os
            import sys

            # Check if we're in the development directory
            if os.path.exists("pygetpapers") and os.path.exists(
                "pygetpapers/pygetpapers.py"
            ):
                # Use local development version
                cmd = [sys.executable, "-m", "pygetpapers.pygetpapers"] + args
            else:
                # Use installed version
                cmd = ["pygetpapers"] + args

            # Initialize progress tracking
            progress_data = {
                "total_papers": 0,
                "current_paper": 0,
                "json_downloaded": 0,
                "xml_downloaded": 0,
                "pdf_downloaded": 0,
                "supplementary_downloaded": 0,
                "current_operation": "Initializing...",
                "output_lines": [],
            }

            # Create progress display if placeholder provided
            if progress_placeholder:
                self._display_progress(progress_placeholder, progress_data)
                # Also show a simple progress indicator as fallback
                with progress_placeholder.container():
                    st.info("🔄 Starting download process...")
                    st.progress(0)

            # Run command with real-time output capture
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )

            stdout_lines = []
            stderr_lines = []
            update_counter = 0

            # Read output in real-time
            while True:
                output = process.stdout.readline()
                if output == "" and process.poll() is not None:
                    break
                if output:
                    line = output.strip()
                    stdout_lines.append(line)

                    # Parse progress information
                    self._parse_progress_line(line, progress_data)

                    # Update progress display more frequently
                    update_counter += 1
                    if progress_placeholder and (
                        update_counter % 3 == 0
                        or "it [" in line
                        or "Wrote" in line
                        or "Downloaded" in line
                    ):
                        try:
                            self._display_progress(progress_placeholder, progress_data)
                        except Exception as e:
                            # If display fails, continue but log the error
                            print(f"Progress display error: {e}")

            # Final progress update
            if progress_placeholder:
                try:
                    self._display_progress(progress_placeholder, progress_data)
                except Exception as e:
                    print(f"Final progress display error: {e}")

            # Wait for process to complete
            returncode = process.poll()

            # Check if the command was successful
            success = returncode == 0

            # If successful but no stdout, create a summary
            if success and not stdout_lines:
                stdout_lines = [
                    f"Successfully executed: pygetpapers {' '.join(args)}",
                    "Check the output directory for downloaded files.",
                ]

            return {
                "success": success,
                "stdout": "\n".join(stdout_lines),
                "stderr": "\n".join(stderr_lines),
                "returncode": returncode,
                "command": " ".join(cmd),
                "progress_data": progress_data,
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Command timed out after 5 minutes",
                "returncode": -1,
                "command": " ".join(cmd),
                "progress_data": progress_data if "progress_data" in locals() else {},
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1,
                "command": " ".join(cmd),
                "progress_data": progress_data if "progress_data" in locals() else {},
            }

    def _parse_progress_line(self, line, progress_data):
        """Parse a line of output to extract progress information"""
        import re

        # Skip tqdm progress bar lines (they're redundant with our own progress display)
        if re.match(r"^\d+%\|.*\| \d+/\d+ \[.*\]$", line):
            # This is a tqdm progress bar line, skip it for output display
            # But still extract progress information
            match = re.search(r"(\d+)/(\d+)", line)
            if match:
                current = int(match.group(1))
                total = int(match.group(2))
                progress_data["current_paper"] = current
                if progress_data["total_papers"] == 0:
                    progress_data["total_papers"] = total
            return  # Don't add tqdm lines to output_lines

        # Also skip lines that are just progress percentages without the full bar
        if re.match(r"^\d+%\|.*\| \d+/\d+ \[.*\]$", line.strip()):
            return

        # Skip lines that are just progress updates
        if re.match(r"^\d+/\d+ \[.*\]$", line.strip()):
            return

        # Update current operation
        if "Making request to" in line:
            progress_data["current_operation"] = "Searching repository..."
        elif "Got request result" in line:
            progress_data["current_operation"] = "Processing results..."
        elif "Downloading" in line:
            progress_data["current_operation"] = "Downloading files..."
        elif "Writing" in line or "Wrote" in line:
            progress_data["current_operation"] = "Writing files..."
        elif "Processing" in line:
            progress_data["current_operation"] = "Processing papers..."

        # Extract total hits
        if "Total Hits are" in line:
            match = re.search(r"Total Hits are (\d+)", line)
            if match:
                progress_data["total_papers"] = int(match.group(1))
        elif "Total number of hits" in line:
            match = re.search(r"Total number of hits.*?(\d+)", line)
            if match:
                progress_data["total_papers"] = int(match.group(1))

        # Extract current paper number from tqdm progress
        if "it [" in line and "it/s]" in line:
            # Parse tqdm progress bar: "5it [00:01, 3.16s/it]"
            match = re.search(r"(\d+)it \[", line)
            if match:
                progress_data["current_paper"] = int(match.group(1))
        # Also look for paper numbers in other formats
        elif "paper" in line.lower() and any(str(i) in line for i in range(1, 1000)):
            # Extract paper number from lines like "Wrote json files for paper 1"
            match = re.search(r"paper (\d+)", line.lower())
            if match:
                paper_num = int(match.group(1))
                if paper_num > progress_data["current_paper"]:
                    progress_data["current_paper"] = paper_num

        # Count different file types
        if "json" in line.lower() and (
            "wrote" in line.lower() or "downloaded" in line.lower()
        ):
            progress_data["json_downloaded"] += 1
        elif "xml" in line.lower() and (
            "wrote" in line.lower() or "downloaded" in line.lower()
        ):
            progress_data["xml_downloaded"] += 1
        elif "pdf" in line.lower() and (
            "wrote" in line.lower() or "downloaded" in line.lower()
        ):
            progress_data["pdf_downloaded"] += 1
        elif "supplementary" in line.lower() and (
            "wrote" in line.lower() or "downloaded" in line.lower()
        ):
            progress_data["supplementary_downloaded"] += 1

        # Only store meaningful output lines (skip tqdm bars and progress updates)
        if not re.match(r"^\d+%\|.*\| \d+/\d+ \[.*\]$", line) and not re.match(
            r"^\d+/\d+ \[.*\]$", line.strip()
        ):
            progress_data["output_lines"].append(line)

    def _display_progress(self, placeholder, progress_data):
        """Display progress indicators in the Streamlit placeholder"""
        with placeholder.container():
            st.markdown("### 📊 Download Progress")

            # Current operation with animated indicator
            operation_emoji = "🔄"
            if "Searching" in progress_data["current_operation"]:
                operation_emoji = "🔍"
            elif "Downloading" in progress_data["current_operation"]:
                operation_emoji = "⬇️"
            elif "Writing" in progress_data["current_operation"]:
                operation_emoji = "💾"
            elif "Processing" in progress_data["current_operation"]:
                operation_emoji = "⚙️"

            st.info(f"{operation_emoji} **{progress_data['current_operation']}**")

            # Main animated progress bar
            if progress_data["total_papers"] > 0:
                progress_percent = min(
                    100,
                    (progress_data["current_paper"] / progress_data["total_papers"])
                    * 100,
                )

                # Create animated progress bar with custom styling
                st.markdown(
                    f"""
                <div style="margin: 10px 0;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <span>📄 Papers: {progress_data['current_paper']} / {progress_data['total_papers']}</span>
                        <span>{progress_percent:.1f}%</span>
                    </div>
                    <div style="background-color: #f0f0f0; border-radius: 10px; height: 20px; overflow: hidden;">
                        <div style="background: linear-gradient(90deg, #1f77b4, #ff7f0e); 
                                    height: 100%; 
                                    width: {progress_percent}%; 
                                    border-radius: 10px; 
                                    transition: width 0.3s ease;
                                    display: flex; 
                                    align-items: center; 
                                    justify-content: center;">
                            <span style="color: white; font-size: 12px; font-weight: bold;">
                                {progress_data['current_paper']}/{progress_data['total_papers']}
                            </span>
                        </div>
                    </div>
                </div>
                """,
                    unsafe_allow_html=True,
                )
            else:
                # Show indeterminate progress for initialization
                st.markdown(
                    """
                <div style="margin: 10px 0;">
                    <div style="background: linear-gradient(90deg, #1f77b4, #ff7f0e, #1f77b4); 
                                background-size: 200% 100%; 
                                animation: loading 2s infinite;
                                height: 20px; 
                                border-radius: 10px;">
                    </div>
                </div>
                <style>
                @keyframes loading {
                    0% { background-position: 200% 0; }
                    100% { background-position: -200% 0; }
                }
                </style>
                """,
                    unsafe_allow_html=True,
                )

            # File type progress with animated counters
            st.markdown("**📁 File Downloads:**")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.markdown(
                    f"""
                <div style="text-align: center; padding: 10px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                            border-radius: 10px; color: white;">
                    <div style="font-size: 24px;">📄</div>
                    <div style="font-size: 18px; font-weight: bold;">{progress_data['json_downloaded']}</div>
                    <div style="font-size: 12px;">JSON</div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

            with col2:
                st.markdown(
                    f"""
                <div style="text-align: center; padding: 10px; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                            border-radius: 10px; color: white;">
                    <div style="font-size: 24px;">📋</div>
                    <div style="font-size: 18px; font-weight: bold;">{progress_data['xml_downloaded']}</div>
                    <div style="font-size: 12px;">XML</div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

            with col3:
                st.markdown(
                    f"""
                <div style="text-align: center; padding: 10px; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                            border-radius: 10px; color: white;">
                    <div style="font-size: 24px;">📕</div>
                    <div style="font-size: 18px; font-weight: bold;">{progress_data['pdf_downloaded']}</div>
                    <div style="font-size: 12px;">PDF</div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

            with col4:
                st.markdown(
                    f"""
                <div style="text-align: center; padding: 10px; background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); 
                            border-radius: 10px; color: white;">
                    <div style="font-size: 24px;">📎</div>
                    <div style="font-size: 18px; font-weight: bold;">{progress_data['supplementary_downloaded']}</div>
                    <div style="font-size: 12px;">Suppl</div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

            # Recent output with better formatting
            if progress_data["output_lines"]:
                st.markdown("**📝 Recent Activity:**")
                recent_lines = progress_data["output_lines"][
                    -5:
                ]  # Show last 5 meaningful lines

                # Filter out redundant or less useful messages
                meaningful_lines = []
                for line in recent_lines:
                    # Skip very common or less informative messages
                    if any(
                        skip in line.lower()
                        for skip in [
                            "debug:",
                            "time elapsed:",
                            "got the query result",
                            "making request to",
                            "got request result",
                        ]
                    ):
                        continue
                    meaningful_lines.append(line)

                if meaningful_lines:
                    # Create a styled output area
                    output_html = '<div style="background-color: #f8f9fa; border-left: 4px solid #1f77b4; padding: 10px; border-radius: 5px; font-family: monospace; font-size: 12px;">'
                    for line in meaningful_lines[-3:]:  # Show last 3 meaningful lines
                        # Color code different types of messages
                        if "ERROR" in line or "WARNING" in line:
                            output_html += f'<div style="color: #dc3545; margin: 2px 0;">{line}</div>'
                        elif "INFO" in line:
                            output_html += f'<div style="color: #17a2b8; margin: 2px 0;">{line}</div>'
                        elif "wrote" in line.lower() or "downloaded" in line.lower():
                            output_html += f'<div style="color: #28a745; font-weight: bold; margin: 2px 0;">{line}</div>'
                        else:
                            output_html += f'<div style="color: #6c757d; margin: 2px 0;">{line}</div>'
                    output_html += "</div>"

                    st.markdown(output_html, unsafe_allow_html=True)
                else:
                    st.info("🔄 Processing papers...")

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
        st.markdown(
            '<h1 class="main-header">📚 Pygetpapers Web Interface</h1>',
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="info-box">
                <strong>Welcome to Pygetpapers!</strong> This web interface makes it easy to
                search and download scholarly papers from multiple repositories. Build complex
                queries, manage your corpus, and explore research papers with an intuitive
                interface.
            </div>
            """,
            unsafe_allow_html=True,
        )

    def render_sidebar(self):
        """Render the sidebar with navigation"""
        st.sidebar.title("Navigation")

        page = st.sidebar.selectbox(
            "Choose a page:",
            [
                "Search Papers",
                "Query Builder",
                "Corpus Manager",
                "Data Tables",
                "Figures Gallery",
                "Corpus Comparison",
                "Fulltext Search",
                "XML to HTML",
                "Settings",
                "Help",
            ],
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
        st.markdown(
            '<h2 class="section-header">🔍 Search Papers</h2>', unsafe_allow_html=True
        )

        # Repository selection
        col1, col2 = st.columns([1, 2])

        with col1:
            selected_api = st.selectbox(
                "Select Repository:",
                options=list(self.supported_apis.keys()),
                format_func=lambda x: self.supported_apis[x],
            )

            # Show API features
            features = self.api_features[selected_api]
            st.markdown("**Supported Features:**")
            for feature, supported in features.items():
                status = "✅" if supported else "❌"
                st.markdown(f"{status} {feature.replace('_', ' ').title()}")

        with col2:
            # Query input
            # Check if there's a generated query from Query Builder
            if (
                "generated_query" in st.session_state
                and st.session_state.generated_query
            ):
                default_query = st.session_state.generated_query
                # Clear the generated query after using it
                del st.session_state.generated_query
            else:
                default_query = ""

            st.markdown("### 🔍 **Search Query** (Required)")
            query = st.text_area(
                "Enter your search terms here:",
                value=default_query,
                placeholder=(
                    "Enter your search query (e.g., 'artificial intelligence' OR "
                    "'machine learning')"
                ),
                height=100,
                help="This is where you enter your search terms. Use simple keywords or complex Boolean queries.",
            )

            # Date range (if supported)
            if features["date_range"]:
                col2a, col2b = st.columns(2)
                with col2a:
                    start_date = st.date_input(
                        "Start Date", value=datetime.now() - timedelta(days=365)
                    )
                with col2b:
                    end_date = st.date_input("End Date", value=datetime.now())
            else:
                start_date = None
                end_date = None

        # Download options
        st.markdown(
            '<h3 class="section-header">📥 Download Options</h3>',
            unsafe_allow_html=True,
        )

        col3, col4, col5 = st.columns(3)

        with col3:
            limit = st.number_input(
                "Maximum Results", min_value=1, max_value=1000, value=10
            )
            if limit > 100:
                st.warning(
                    f"⚠️ **Warning:** Requesting {limit} papers may take a long time and use significant resources."
                )
            if limit > 500:
                st.error(
                    f"🚨 **DANGER:** Requesting {limit} papers is very resource-intensive. Consider reducing the limit."
                )

            download_xml = st.checkbox(
                "Download XML", value=True, disabled=not features["xml"]
            )
            download_pdf = st.checkbox(
                "Download PDF", value=False, disabled=not features["pdf"]
            )

        with col4:
            download_supp = st.checkbox(
                "Download Supplementary Files",
                value=False,
                disabled=not features["supplementary"],
            )
            download_refs = st.checkbox(
                "Download References", value=False, disabled=not features["references"]
            )
            download_citations = st.checkbox(
                "Download Citations", value=False, disabled=not features["citations"]
            )

        with col5:
            make_csv = st.checkbox("Generate CSV Metadata", value=True)
            make_html = st.checkbox("Generate HTML Metadata", value=False)
            save_query = st.checkbox("Save Query Configuration", value=False)

        # Output directory
        if "output_dir" not in st.session_state:
            repo_name = self.supported_apis[selected_api].lower().replace(" ", "_")
            st.session_state.output_dir = (
                f"{repo_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )

        output_dir = st.text_input(
            "Output Directory:",
            value=st.session_state.output_dir,
            key="output_dir_input",
        )

        # Update session state when user changes the value
        if output_dir != st.session_state.output_dir:
            st.session_state.output_dir = output_dir

        # Search button
        if st.button(
            "🔍 Search and Download", type="primary", use_container_width=True
        ):
            if not query and selected_api not in ["biorxiv", "medrxiv"]:
                st.error("Please enter a search query!")
                return

            # Safety check for large downloads
            if limit > 200:
                st.error(
                    f"🚨 **SAFETY STOP:** Requesting {limit} papers is too large for this interface."
                )
                st.info("Please reduce the limit to 200 or fewer papers for safety.")
                return
            elif limit > 100:
                st.warning(
                    f"⚠️ **Large Download Warning:** You're requesting {limit} papers."
                )
                st.info(
                    "This may take a long time and use significant resources. Consider starting with a smaller number."
                )

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

            # Debug: Show the exact command being executed
            st.info(f"🔍 **Debug Info:** Executing command with limit={limit}")
            st.code(f"pygetpapers {' '.join(args)}")

            # Create progress placeholder
            progress_placeholder = st.empty()

            # Run the command with progress tracking
            result = self.run_pygetpapers_command(args, progress_placeholder)

            if result["success"]:
                st.success("✅ Papers downloaded successfully!")

                # Validate the number of papers actually downloaded
                actual_papers = result["progress_data"].get("current_paper", 0)
                if actual_papers > limit:
                    st.warning(
                        f"⚠️ **Warning:** Requested {limit} papers but {actual_papers} were downloaded!"
                    )
                    st.error(
                        f"🚨 **CRITICAL:** This exceeds the requested limit by {actual_papers - limit} papers!"
                    )
                    st.info(
                        "This may be due to API behavior or repository-specific limits. Please check the output directory."
                    )
                elif actual_papers == 0:
                    st.warning(
                        "⚠️ **Warning:** No papers were downloaded. Check the query and repository."
                    )
                else:
                    st.success(
                        f"✅ Successfully downloaded {actual_papers} papers (requested: {limit})"
                    )

                st.session_state.total_papers += actual_papers
                st.session_state.total_corpora += 1

                # Debug: Show stats update
                st.info(
                    f"📊 **Stats Updated:** Added {actual_papers} papers and 1 corpus. Total: {st.session_state.total_papers} papers, {st.session_state.total_corpora} corpora"
                )

                # Show results summary
                st.markdown("### Results Summary")

                # Display command that was executed
                st.markdown("**Command executed:**")
                st.code(f"pygetpapers {' '.join(args)}")

                # Display output (filtered to remove tqdm progress bars)
                if result["stdout"].strip():
                    st.markdown("**Output:**")
                    # Filter out tqdm progress bars from the output
                    import re

                    filtered_output = []
                    for line in result["stdout"].split("\n"):
                        # Skip tqdm progress bar lines
                        if not re.match(r"^\d+%\|.*\| \d+/\d+ \[.*\]$", line.strip()):
                            # Also skip lines that are just progress updates
                            if not re.match(r"^\d+/\d+ \[.*\]$", line.strip()):
                                filtered_output.append(line)

                    clean_output = "\n".join(filtered_output).strip()
                    if clean_output:
                        st.code(clean_output)
                    else:
                        st.info(
                            "📝 Command completed successfully. Check the output directory "
                            "for downloaded files."
                        )
                else:
                    st.info(
                        "📝 Command completed successfully. Check the output directory "
                        "for downloaded files."
                    )

                # Show output directory info
                st.markdown("**Output Directory:**")
                st.code(output_dir)

                # Add corpus to session state
                st.session_state.corpora.append(
                    {
                        "name": output_dir,
                        "api": selected_api,
                        "query": query,
                        "downloaded_papers": actual_papers,  # Use actual papers downloaded
                        "requested_limit": limit,  # Store the requested limit
                        "total_hits": result["progress_data"].get(
                            "total_papers", limit
                        ),  # Use actual total hits if available
                        "date_created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    }
                )

                # Show next steps
                st.markdown("**Next Steps:**")
                st.markdown("- Check the output directory for downloaded papers")
                st.markdown("- Use the Corpus Manager to view and analyze your papers")
                st.markdown("- The corpus has been added to your corpus list")

            else:
                st.error("❌ Error occurred during download")
                st.markdown("**Command executed:**")
                st.code(f"pygetpapers {' '.join(args)}")
                st.markdown("**Error output:**")
                # Filter out tqdm progress bars from error output too
                import re

                filtered_stderr = []
                for line in result["stderr"].split("\n"):
                    # Skip tqdm progress bar lines
                    if not re.match(r"^\d+%\|.*\| \d+/\d+ \[.*\]$", line.strip()):
                        # Also skip lines that are just progress updates
                        if not re.match(r"^\d+/\d+ \[.*\]$", line.strip()):
                            filtered_stderr.append(line)

                clean_stderr = "\n".join(filtered_stderr).strip()
                if clean_stderr:
                    st.code(clean_stderr)
                else:
                    st.info("No error output available.")

                # Provide troubleshooting suggestions
                st.markdown("**Troubleshooting:**")
                st.markdown("- Check your internet connection")
                st.markdown("- Verify the query syntax")
                st.markdown("- Try reducing the result limit")
                st.markdown("- Check if the repository is available")

    def render_query_builder(self):
        """Render the advanced query builder"""
        st.markdown(
            '<h2 class="section-header">🔧 Advanced Query Builder</h2>',
            unsafe_allow_html=True,
        )

        st.markdown(
            """
        <div class="info-box">
            <strong>Build Complex Queries:</strong> Use this tool to create sophisticated  # noqa: E501
            Boolean queries with field-specific searches, nested conditions, and proper
            quoting.
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Query parts management
        if "query_parts" not in st.session_state:
            st.session_state.query_parts = [
                {"query": "", "operator": "AND", "field": "all"}
            ]

        # Add new query part
        if st.button("➕ Add Query Part"):
            st.session_state.query_parts.append(
                {"query": "", "operator": "AND", "field": "all"}
            )

        # Display query parts
        for i, part in enumerate(st.session_state.query_parts):
            st.markdown(f"### Query Part {i + 1}")

            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                part["query"] = st.text_input(
                    f"Query {i + 1}", value=part["query"], key=f"query_{i}"
                )

            with col2:
                if i > 0:  # Don't show operator for first part
                    part["operator"] = st.selectbox(
                        "Operator", ["AND", "OR", "AND NOT"], key=f"operator_{i}"
                    )

            with col3:
                part["field"] = st.selectbox(
                    "Field",
                    [
                        "all",
                        "title",
                        "abstract",
                        "author",
                        "journal",
                        "license",
                        "methods",
                    ],
                    key=f"field_{i}",
                )

            # Remove button
            if len(st.session_state.query_parts) > 1:
                if st.button(f"🗑️ Remove Part {i + 1}", key=f"remove_{i}"):
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
            st.markdown(
                """
            **Simple Queries:**
            - `"artificial intelligence"`
            - `"machine learning" AND "deep learning"`

            **Field-Specific Queries:**
            - `TITLE:"neural networks" AND ABSTRACT:"deep learning"`
            - `AUTH:"Smith J" AND JOURNAL:"Nature"`

            **Complex Boolean Queries:**
            - `"(LICENSE:'cc by' OR LICENSE:'cc-by') AND METHODS:'transcriptome assembly'"`  # noqa: E501
            - `"cancer" AND ("treatment" OR "therapy") AND NOT "review"`

            **Date Range Queries (Europe PMC):**
            - `"covid-19" AND FIRST_PDATE:[2020-01-01 TO 2023-12-31]`
            """
            )

    def render_corpus_manager(self):
        """Render the corpus management page"""
        st.markdown(
            '<h2 class="section-header">📁 Corpus Manager</h2>', unsafe_allow_html=True
        )

        # Add refresh button
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("### Your Corpora")
        with col2:
            if st.button(
                "🔄 Refresh Corpus List", help="Scan for newly downloaded corpora"
            ):
                self._scan_for_existing_corpora()
                st.success("Corpus list refreshed!")
                st.rerun()

        if "corpora" not in st.session_state or not st.session_state.corpora:
            st.warning("No corpora found. Download some papers first!")
            return

        # Corpus list with datatables integration
        st.markdown("### Your Corpora")

        for i, corpus in enumerate(st.session_state.corpora):
            # Create display text showing requested vs downloaded
            if corpus.get("requested_limit", 0) > 0:
                papers_text = f"{corpus['downloaded_papers']} / {corpus['requested_limit']} papers"
            else:
                papers_text = f"{corpus['downloaded_papers']} papers"

            with st.expander(f"📁 {corpus['name']} ({papers_text})"):
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.markdown(
                        f"**Repository:** "
                        f"{self.supported_apis.get(corpus['api'], corpus['api'])}"
                    )
                    st.markdown(f"**Query:** {corpus['query'] or 'Date-based search'}")
                    st.markdown(f"**Created:** {corpus['date_created']}")

                    # Show paper count details
                    if corpus.get("requested_limit", 0) > 0:
                        st.markdown(
                            f"**Downloaded:** {corpus['downloaded_papers']} papers"
                        )
                        st.markdown(
                            f"**Requested:** {corpus['requested_limit']} papers"
                        )

                        # Show download success rate
                        success_rate = (
                            corpus["downloaded_papers"] / corpus["requested_limit"]
                        ) * 100
                        if success_rate == 100:
                            st.markdown(
                                f"**Status:** ✅ Complete ({success_rate:.0f}%)"
                            )
                        elif success_rate > 80:
                            st.markdown(
                                f"**Status:** ⚠️ Mostly Complete ({success_rate:.0f}%)"
                            )
                        else:
                            st.markdown(
                                f"**Status:** ❌ Incomplete ({success_rate:.0f}%)"
                            )

                        # Show total available in repository (if different from requested)
                        if (
                            corpus.get("total_hits", 0) > 0
                            and corpus["total_hits"] != corpus["requested_limit"]
                        ):
                            st.markdown(
                                f"**Total Available in Repository:** {corpus['total_hits']} papers"
                            )
                    else:
                        st.markdown(
                            f"**Papers Downloaded:** {corpus['downloaded_papers']}"
                        )

                    # Add datatables view button
                    if st.button(
                        f"📊 View Papers Table {i + 1}", key=f"view_table_{i}"
                    ):
                        st.session_state.selected_corpus = corpus["name"]
                        st.session_state.show_datatable = True

                with col2:
                    if st.button(f"🗑️ Delete Corpus {i + 1}", key=f"delete_corpus_{i}"):
                        st.session_state.corpora.pop(i)
                        st.rerun()

        # Show datatables if requested
        if st.session_state.get("show_datatable", False) and st.session_state.get(
            "selected_corpus"
        ):
            self._render_corpus_datatables(st.session_state.selected_corpus)

        # Corpus statistics
        st.markdown("### Corpus Statistics")

        if st.session_state.corpora:
            # Create summary dataframe
            df = pd.DataFrame(st.session_state.corpora)
            df["date_created"] = pd.to_datetime(df["date_created"])

            # Papers by repository
            fig1 = px.pie(
                df.groupby("api")["downloaded_papers"].sum().reset_index(),
                values="downloaded_papers",
                names="api",
                title="Downloaded Papers by Repository",
            )
            st.plotly_chart(fig1, use_container_width=True)

            # Papers over time
            fig2 = px.line(
                df.groupby(df["date_created"].dt.date)["downloaded_papers"]
                .sum()
                .reset_index(),
                x="date_created",
                y="downloaded_papers",
                title="Papers Downloaded Over Time",
            )
            st.plotly_chart(fig2, use_container_width=True)

            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                total_downloaded = df["downloaded_papers"].sum()
                st.metric("Total Downloaded", total_downloaded)
            with col2:
                total_requested = df["requested_limit"].sum()
                st.metric("Total Requested", total_requested)
            with col3:
                total_corpora = len(df)
                st.metric("Total Corpora", total_corpora)
            with col4:
                avg_success_rate = (
                    (total_downloaded / total_requested * 100)
                    if total_requested > 0
                    else 0
                )
                st.metric("Avg Success Rate", f"{avg_success_rate:.1f}%")

    def _render_corpus_datatables(self, corpus_name: str):
        """Render datatables for a specific corpus"""
        st.markdown(f"### 📊 Papers Table: {corpus_name}")

        try:
            # Read the corpus data
            output_data = self.datatables.read_pygetpapers_output(corpus_name)

            # Create tabs for different views
            tab1, tab2, tab3, tab4, tab5 = st.tabs(
                [
                    "📄 Papers",
                    "📋 Metadata",
                    "📊 Summary",
                    "🔍 Fulltext Search",
                    "💾 Export",
                ]
            )

            with tab1:
                st.markdown("#### Papers Overview")

                # Table options
                col1, col2 = st.columns(2)
                with col1:
                    include_checkboxes = st.checkbox("Include Checkboxes", value=True)
                with col2:
                    selectable_rows = st.checkbox("Selectable Rows", value=True)

                papers_html = self.datatables.create_papers_table(
                    output_data,
                    "papers_table",
                    include_checkboxes=include_checkboxes,
                    selectable_rows=selectable_rows,
                )
                st.components.v1.html(papers_html, height=600, scrolling=True)

                # Selection summary
                if include_checkboxes:
                    st.markdown("**Selection Actions:**")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("📋 Select All"):
                            st.info("Select all functionality will be implemented")
                    with col2:
                        if st.button("📋 Deselect All"):
                            st.info("Deselect all functionality will be implemented")
                    with col3:
                        if st.button("📥 Export Selected"):
                            st.info(
                                "Export selected papers functionality will be implemented"  # noqa: E501
                            )

                # Paper details on selection
                if st.button("🔍 Show Paper Details"):
                    st.session_state.show_paper_details = True

            with tab2:
                st.markdown("#### Metadata Files")
                metadata_html = self.datatables.create_metadata_table(
                    output_data, "metadata_table"
                )
                st.components.v1.html(metadata_html, height=400, scrolling=True)

            with tab3:
                st.markdown("#### Corpus Summary")
                summary_html = self.datatables.create_summary_table(
                    output_data, "summary_table"
                )
                st.components.v1.html(summary_html, height=300, scrolling=True)

                # Show summary statistics
                summary = output_data["summary"]
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Papers", summary["total_papers"])
                with col2:
                    st.metric("Metadata Files", len(summary["metadata_files_found"]))
                with col3:
                    st.metric("XML Files", "✅" if summary["has_xml"] else "❌")
                with col4:
                    st.metric("PDF Files", "✅" if summary["has_pdf"] else "❌")

            with tab4:
                st.markdown("#### 🔍 Fulltext Search")

                # Search interface
                col1, col2 = st.columns([2, 1])

                with col1:
                    search_terms = st.text_area(
                        "Search Terms (one per line or comma-separated):",
                        placeholder=(
                            "Enter search terms...\nExample:\nmachine learning\n"
                            "artificial intelligence\nneural network"
                        ),
                        height=100,
                    )

                with col2:
                    st.markdown("**Search Options:**")
                    case_sensitive = st.checkbox("Case Sensitive", value=False)

                    search_fields = st.multiselect(
                        "Search in:",
                        ["xml", "pdf", "supplementary", "metadata"],
                        default=["xml", "metadata"],
                    )

                # Process search terms
                if search_terms.strip():
                    # Parse search terms
                    terms = []
                    for line in search_terms.split("\n"):
                        line_terms = [
                            term.strip() for term in line.split(",") if term.strip()
                        ]
                        terms.extend(line_terms)

                    if terms:
                        # Perform search
                        if st.button("🔍 Search Fulltext", type="primary"):
                            with st.spinner("Searching fulltext content..."):
                                search_results = self.datatables.search_fulltext(
                                    output_data, terms, search_fields, case_sensitive
                                )

                                # Store results in session state
                                st.session_state.search_results = search_results
                                st.session_state.current_corpus_data = output_data

                        # Show search results if available
                        if (
                            "search_results" in st.session_state
                            and st.session_state.search_results
                        ):
                            results = st.session_state.search_results

                            # Search summary
                            st.markdown("#### Search Results Summary")
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric(
                                    "Total Matches", results["summary"]["total_matches"]
                                )
                            with col2:
                                st.metric(
                                    "Papers with Matches",
                                    results["summary"]["papers_with_matches"],
                                )
                            with col3:
                                st.metric(
                                    "Match Rate",
                                    f"{results['summary']['match_rate']:.1%}",
                                )
                            with col4:
                                st.metric("Search Terms", len(results["search_terms"]))

                            # Search results table
                            st.markdown("#### Search Results")
                            results_html = self.datatables.create_search_results_table(
                                results, "search_results_table"
                            )
                            st.components.v1.html(
                                results_html, height=600, scrolling=True
                            )

                            # Filter papers by search results
                            st.markdown("#### Filter Papers by Search Results")
                            if st.button("📋 Show Only Papers with Matches"):
                                filtered_data = self.datatables.filter_papers_by_search(
                                    st.session_state.current_corpus_data, results
                                )

                                st.success(
                                    f"✅ Filtered to "
                                    f"{filtered_data['summary']['total_papers']} papers with matches"
                                )

                                # Show filtered papers table
                                filtered_html = self.datatables.create_papers_table(
                                    filtered_data, "filtered_papers_table"
                                )
                                st.components.v1.html(
                                    filtered_html, height=600, scrolling=True
                                )

                            # Export search results
                            if st.button("📄 Export Search Results"):
                                # Create CSV with search results
                                search_csv_data = []
                                for match in results["matches"]:
                                    search_csv_data.append(
                                        {
                                            "Paper_ID": match["paper_id"],
                                            "Search_Term": match["term"],
                                            "File": match["file"],
                                            "Line_Number": match["line_number"],
                                            "Context": match["context"],
                                            "Content_Type": match["content_type"],
                                        }
                                    )

                                search_df = pd.DataFrame(search_csv_data)
                                search_csv_filename = (
                                    f"{corpus_name}_search_results.csv"
                                )
                                search_df.to_csv(search_csv_filename, index=False)

                                st.success(
                                    f"✅ Search results exported to "
                                    f"{search_csv_filename}"
                                )

                                # Provide download link
                                with open(search_csv_filename, "r") as f:
                                    csv_data = f.read()
                                st.download_button(
                                    label="📥 Download Search Results",
                                    data=csv_data,
                                    file_name=search_csv_filename,
                                    mime="text/csv",
                                )
                else:
                    st.info(
                        "Enter search terms to search within the fulltext content of papers."  # noqa: E501
                    )

            with tab5:
                st.markdown("#### Export Options")

                # Export to CSV
                if st.button("📄 Export Papers to CSV"):
                    csv_filename = f"{corpus_name}_papers.csv"
                    if self.datatables.export_table_to_csv(output_data, csv_filename):
                        st.success(f"✅ Exported to {csv_filename}")

                        # Provide download link
                        with open(csv_filename, "r") as f:
                            csv_data = f.read()
                        st.download_button(
                            label="📥 Download CSV",
                            data=csv_data,
                            file_name=csv_filename,
                            mime="text/csv",
                        )
                    else:
                        st.error("❌ Export failed")

                # Show file structure
                st.markdown("#### File Structure")
                if output_data["paper_directories"]:
                    file_tree = self._generate_file_tree(output_data)
                    st.code(file_tree)

            # Show paper details if requested
            if st.session_state.get("show_paper_details", False):
                self._render_paper_details(output_data)

        except FileNotFoundError:
            st.error(f"❌ Corpus directory not found: {corpus_name}")
        except Exception as e:
            st.error(f"❌ Error loading corpus: {str(e)}")

    def _generate_file_tree(self, output_data: dict) -> str:
        """Generate a file tree representation of the corpus"""
        tree = []
        tree.append(output_data["output_dir"])

        for paper in output_data["paper_directories"][:10]:  # Show first 10 papers
            tree.append(f"├── {paper['directory']}")
            for file_path in paper["files"][:5]:  # Show first 5 files per paper
                tree.append(f"│   ├── {file_path}")
            if len(paper["files"]) > 5:
                tree.append(f"│   └── ... ({len(paper['files']) - 5} more files)")

        if len(output_data["paper_directories"]) > 10:
            tree.append(
                f"└── ... ({len(output_data['paper_directories']) - 10} more papers)"
            )

        return "\n".join(tree)

    def _render_paper_details(self, output_data: dict):
        """Render detailed view of papers"""
        st.markdown("### 📖 Paper Details")

        # Create a selectbox for paper selection
        paper_ids = [paper["directory"] for paper in output_data["paper_directories"]]
        selected_paper_id = st.selectbox("Select a paper:", paper_ids)

        if selected_paper_id:
            paper_details = self.datatables.get_paper_details(
                output_data, selected_paper_id
            )
            if paper_details:
                metadata = paper_details.get("metadata", {})

                col1, col2 = st.columns([2, 1])

                with col1:
                    st.markdown(f"**Title:** {metadata.get('title', 'N/A')}")
                    st.markdown(f"**Authors:** {metadata.get('authorString', 'N/A')}")
                    st.markdown(f"**Journal:** {metadata.get('journalTitle', 'N/A')}")
                    st.markdown(f"**DOI:** {metadata.get('doi', 'N/A')}")
                    st.markdown(f"**PMID:** {metadata.get('pmid', 'N/A')}")
                    st.markdown(f"**PMCID:** {metadata.get('pmcid', 'N/A')}")
                    st.markdown(
                        f"**Publication Date:** "
                        f"{metadata.get('firstPublicationDate', 'N/A')}"
                    )

                    # Abstract
                    abstract = metadata.get("abstractText", "")
                    if abstract:
                        st.markdown("**Abstract:**")
                        st.text(abstract)

                with col2:
                    st.markdown("**Files:**")
                    for file_path in paper_details["files"]:
                        st.markdown(f"- {file_path}")

                    st.markdown(f"**Total Files:** {len(paper_details['files'])}")

    def render_data_tables(self):
        """Render the data tables page"""
        st.markdown(
            '<h2 class="section-header">📊 Data Tables</h2>', unsafe_allow_html=True
        )

        st.markdown(
            """
        <div class="info-box">
            <strong>Interactive Data Tables:</strong> View and explore your downloaded papers using  # noqa: E501
            interactive HTML tables with sorting, searching, and pagination capabilities.
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Corpus selection
        if "corpora" not in st.session_state or not st.session_state.corpora:
            st.warning("No corpora found. Download some papers first!")
            return

        st.markdown("### Select Corpus to View")

        corpus_names = [corpus["name"] for corpus in st.session_state.corpora]
        selected_corpus = st.selectbox(
            "Select Corpus:",
            corpus_names,
            format_func=lambda x: f"{x} ({next(c['downloaded_papers'] for c in st.session_state.corpora if c['name'] == x)} papers)",
        )

        if selected_corpus:
            # Check if corpus directory exists
            if not os.path.exists(selected_corpus):
                st.error(f"❌ Corpus directory not found: {selected_corpus}")
                st.info(
                    "The corpus may have been moved or deleted. Please re-download the papers."
                )
                return

            # Create tabs for different views
            tab1, tab2, tab3 = st.tabs(
                ["📊 Papers Table", "🖼️ Figures", "📁 File Structure"]
            )

            with tab1:
                # Render the datatables for the selected corpus
                self._render_corpus_datatables(selected_corpus)

            with tab2:
                # Extract and display figures
                with st.spinner("Extracting figures and captions..."):
                    try:
                        # Load corpus data
                        corpus_data = self.datatables.read_pygetpapers_output(
                            selected_corpus
                        )

                        # Extract figures
                        figures_data = self.datatables.extract_figures(corpus_data)

                        if figures_data["papers"]:
                            summary = figures_data["summary"]
                            st.success(
                                f"✅ Found {summary['total_figures']} figures across {summary['papers_with_figures']} papers"
                            )

                            # Quick figures table
                            figures_html = self.datatables.create_figures_table(
                                figures_data, "corpus_figures_table"
                            )
                            st.components.v1.html(
                                figures_html, height=600, scrolling=True
                            )

                            # Link to full figures gallery
                            st.markdown("---")
                            st.markdown(
                                "**For more detailed figure analysis, visit the [Figures Gallery](#figures-gallery) page.**"
                            )
                        else:
                            st.info("No figures found in this corpus.")

                    except Exception as e:
                        st.error(f"❌ Error extracting figures: {str(e)}")

            with tab3:
                # Show file structure
                try:
                    corpus_data = self.datatables.read_pygetpapers_output(
                        selected_corpus
                    )
                    file_tree = self._generate_file_tree(corpus_data)
                    st.markdown("### File Structure")
                    st.code(file_tree, language="text")
                except Exception as e:
                    st.error(f"❌ Error loading file structure: {str(e)}")

            # Add a button to close the view
            if st.button("❌ Close Table View"):
                st.session_state.show_datatable = False
                st.session_state.selected_corpus = None
                st.rerun()

    def render_figures_gallery(self):
        """Render the figures gallery page"""
        st.markdown(
            '<h2 class="section-header">🖼️ Figures Gallery</h2>', unsafe_allow_html=True
        )

        st.markdown(
            """
        <div class="info-box">
            <strong>Extract and View Figures:</strong> Automatically extract figures, captions, and thumbnails
            from your downloaded papers. Browse visual content with interactive tables and image previews.
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Corpus selection
        if "corpora" not in st.session_state or not st.session_state.corpora:
            st.warning("No corpora found. Download some papers first!")
            return

        st.markdown("### Select Corpus to Extract Figures")

        corpus_names = [corpus["name"] for corpus in st.session_state.corpora]
        selected_corpus = st.selectbox(
            "Choose a corpus:",
            corpus_names,
            format_func=lambda x: f"{x} ({next(c['downloaded_papers'] for c in st.session_state.corpora if c['name'] == x)} papers)",
        )

        if selected_corpus:
            # Check if corpus directory exists
            if not os.path.exists(selected_corpus):
                st.error(f"❌ Corpus directory not found: {selected_corpus}")
                st.info(
                    "The corpus may have been moved or deleted. Please re-download the papers."
                )
                return

            # Extract figures
            with st.spinner("Extracting figures and captions..."):
                try:
                    # Load corpus data
                    corpus_data = self.datatables.read_pygetpapers_output(
                        selected_corpus
                    )

                    # Extract figures
                    figures_data = self.datatables.extract_figures(corpus_data)

                    # Store in session state
                    st.session_state.figures_data = figures_data
                    st.session_state.selected_figures_corpus = selected_corpus

                except Exception as e:
                    st.error(f"❌ Error extracting figures: {str(e)}")
                    return

            # Display figures summary
            if figures_data["papers"]:
                summary = figures_data["summary"]

                st.success(
                    f"✅ Found {summary['total_figures']} figures across {summary['papers_with_figures']} papers"
                )

                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Figures", summary["total_figures"])
                with col2:
                    st.metric("Papers with Figures", summary["papers_with_figures"])
                with col3:
                    st.metric(
                        "Average per Paper",
                        (
                            f"{summary['total_figures'] / summary['papers_with_figures']:.1f}"
                            if summary["papers_with_figures"] > 0
                            else "0"
                        ),
                    )
                with col4:
                    st.metric("Total Papers", len(corpus_data["paper_directories"]))

                # Display options
                st.markdown("### View Options")

                tab1, tab2 = st.tabs(["📊 Figures Summary", "🖼️ All Figures"])

                with tab1:
                    st.markdown("#### Figures by Paper")
                    summary_html = self.datatables.create_figures_summary_table(
                        figures_data, "figures_summary_table"
                    )
                    st.components.v1.html(summary_html, height=400, scrolling=True)

                with tab2:
                    st.markdown("#### All Figures with Thumbnails")

                    # Filter options
                    col1, col2 = st.columns(2)
                    with col1:
                        figure_types = list(
                            set(
                                fig["figure_type"]
                                for paper_figs in figures_data["papers"].values()
                                for fig in paper_figs["figures"]
                            )
                        )
                        selected_types = st.multiselect(
                            "Filter by Figure Type:", figure_types, default=figure_types
                        )

                    with col2:
                        search_caption = st.text_input(
                            "Search in Captions:", placeholder="Enter keywords..."
                        )

                    # Apply filters
                    filtered_figures = {}
                    for paper_id, paper_figures in figures_data["papers"].items():
                        filtered_figs = []
                        for figure in paper_figures["figures"]:
                            # Type filter
                            if figure["figure_type"] not in selected_types:
                                continue

                            # Caption search
                            if (
                                search_caption
                                and search_caption.lower()
                                not in figure["caption"].lower()
                            ):
                                continue

                            filtered_figs.append(figure)

                        if filtered_figs:
                            filtered_figures[paper_id] = {
                                **paper_figures,
                                "figures": filtered_figs,
                                "total_figures": len(filtered_figs),
                            }

                    # Display filtered figures
                    if filtered_figures:
                        filtered_data = {
                            "papers": filtered_figures,
                            "summary": {
                                "total_figures": sum(
                                    len(paper_figs["figures"])
                                    for paper_figs in filtered_figures.values()
                                ),
                                "papers_with_figures": len(filtered_figures),
                            },
                        }

                        figures_html = self.datatables.create_figures_table(
                            filtered_data, "figures_table"
                        )
                        st.components.v1.html(figures_html, height=800, scrolling=True)

                        # Export options
                        st.markdown("#### Export Figures Data")
                        col1, col2 = st.columns(2)

                        with col1:
                            if st.button("📊 Export Summary CSV"):
                                # Create summary CSV
                                summary_data = []
                                for paper_id, paper_figures in filtered_figures.items():
                                    type_counts = {}
                                    for figure in paper_figures["figures"]:
                                        fig_type = figure["figure_type"]
                                        type_counts[fig_type] = (
                                            type_counts.get(fig_type, 0) + 1
                                        )

                                    summary_data.append(
                                        {
                                            "Paper_ID": paper_id,
                                            "Paper_Title": paper_figures["paper_title"],
                                            "Total_Figures": paper_figures[
                                                "total_figures"
                                            ],
                                            "XML_Figures": type_counts.get(
                                                "xml_extracted", 0
                                            ),
                                            "Image_Files": type_counts.get(
                                                "image_file", 0
                                            ),
                                            "Captions_Only": type_counts.get(
                                                "caption_only", 0
                                            ),
                                        }
                                    )

                                df_summary = pd.DataFrame(summary_data)
                                csv_data = df_summary.to_csv(index=False)
                                st.download_button(
                                    label="📥 Download Summary CSV",
                                    data=csv_data,
                                    file_name=f"figures_summary_{selected_corpus}.csv",
                                    mime="text/csv",
                                )

                        with col2:
                            if st.button("📋 Export All Figures CSV"):
                                # Create detailed CSV
                                detailed_data = []
                                for paper_id, paper_figures in filtered_figures.items():
                                    for figure in paper_figures["figures"]:
                                        detailed_data.append(
                                            {
                                                "Paper_ID": paper_id,
                                                "Paper_Title": paper_figures[
                                                    "paper_title"
                                                ],
                                                "Figure_ID": figure["figure_id"],
                                                "Caption": figure["caption"],
                                                "Label": figure["label"],
                                                "Title": figure["title"],
                                                "Figure_Type": figure["figure_type"],
                                                "Image_Source": figure["image_src"],
                                                "Source_File": figure["source_file"],
                                            }
                                        )

                                df_detailed = pd.DataFrame(detailed_data)
                                csv_data = df_detailed.to_csv(index=False)
                                st.download_button(
                                    label="📥 Download Detailed CSV",
                                    data=csv_data,
                                    file_name=f"figures_detailed_{selected_corpus}.csv",
                                    mime="text/csv",
                                )
                    else:
                        st.info("No figures match the selected filters.")
            else:
                st.info("No figures found in the selected corpus.")

                # Show troubleshooting tips
                with st.expander("🔧 Troubleshooting - No Figures Found"):
                    st.markdown(
                        """
                    **Possible reasons why no figures were found:**

                    1. **Papers don't contain figures**: Some papers may not have visual content
                    2. **XML parsing issues**: Figures might be in unsupported XML formats
                    3. **Missing image files**: Images may not have been downloaded
                    4. **File permissions**: Check if the corpus directory is accessible

                    **Try these solutions:**
                    - Download papers with XML content (`--xml` flag)
                    - Download supplementary files (`--supp` flag)
                    - Check if the repository provides figure data
                    - Try a different corpus with more visual content
                    """
                    )

    def render_corpus_comparison(self):
        """Render the corpus comparison and merging page"""
        st.markdown(
            '<h2 class="section-header">🔍 Corpus Comparison & Merging</h2>',
            unsafe_allow_html=True,
        )

        st.markdown(
            """
        <div class="info-box">
            <strong>Compare and Merge Corpora:</strong> Analyze multiple corpora, find overlaps,
            and merge them into unified datasets for comprehensive analysis.
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Check if we have multiple corpora
        if "corpora" not in st.session_state or len(st.session_state.corpora) < 2:
            st.warning(
                "You need at least 2 corpora to perform comparison. Download more papers first!"
            )
            return

        # Corpus selection for comparison
        st.markdown("### Select Corpora for Comparison")

        available_corpora = [corpus["name"] for corpus in st.session_state.corpora]
        selected_corpora = st.multiselect(
            "Choose corpora to compare:",
            available_corpora,
            default=(
                available_corpora[:2]
                if len(available_corpora) >= 2
                else available_corpora
            ),
        )

        if len(selected_corpora) < 2:
            st.info("Please select at least 2 corpora for comparison.")
            return

        # Load corpus data
        corpora_data = []
        valid_corpora = []

        for corpus_name in selected_corpora:
            try:
                if os.path.exists(corpus_name):
                    corpus_data = self.datatables.read_pygetpapers_output(corpus_name)
                    corpora_data.append(corpus_data)
                    valid_corpora.append(corpus_name)
                else:
                    st.warning(f"Corpus directory not found: {corpus_name}")
            except Exception as e:
                st.error(f"Error loading corpus {corpus_name}: {str(e)}")

        if len(corpora_data) < 2:
            st.error("Need at least 2 valid corpora for comparison.")
            return

        # Perform comparison
        comparison_data = self.datatables.compare_corpora(corpora_data)

        # Display comparison results
        st.markdown("### Comparison Results")

        # Summary metrics
        summary = comparison_data["summary_stats"]
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Corpora", summary["total_corpora"])
        with col2:
            st.metric("Total Papers", summary["total_papers"])
        with col3:
            st.metric(
                "Average per Corpus", f"{summary['average_papers_per_corpus']:.1f}"
            )
        with col4:
            st.metric(
                "Common Papers",
                comparison_data["overlap_analysis"].get("common_papers", 0),
            )

        # Comparison table
        st.markdown("#### Corpus Comparison Table")
        comparison_html = self.datatables.create_comparison_table(
            comparison_data, "corpus_comparison_table"
        )
        st.components.v1.html(comparison_html, height=400, scrolling=True)

        # Overlap analysis
        if comparison_data.get("overlap_analysis"):
            st.markdown("#### Overlap Analysis")
            overlap_html = self.datatables.create_overlap_table(
                comparison_data, "overlap_table"
            )
            st.components.v1.html(overlap_html, height=300, scrolling=True)

            # Show common papers
            common_papers = comparison_data["overlap_analysis"].get(
                "common_paper_ids", []
            )
            if common_papers:
                st.markdown(f"**Common Papers ({len(common_papers)}):**")
                st.code(
                    ", ".join(common_papers[:10])
                    + ("..." if len(common_papers) > 10 else "")
                )

        # Merging functionality
        st.markdown("### Merge Corpora")

        col1, col2 = st.columns([2, 1])
        with col1:
            merged_name = st.text_input(
                "Merged Corpus Name:",
                value=f"merged_corpus_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            )

        with col2:
            if st.button("🔗 Merge Selected Corpora", type="primary"):
                try:
                    merged_data = self.datatables.merge_corpora(
                        corpora_data, merged_name
                    )

                    # Add merged corpus to session state
                    if "corpora" not in st.session_state:
                        st.session_state.corpora = []

                    st.session_state.corpora.append(
                        {
                            "name": merged_name,
                            "api": "merged",
                            "query": f"Merged from: {', '.join(valid_corpora)}",
                            "date_created": datetime.now().isoformat(),
                            "downloaded_papers": merged_data["summary"]["total_papers"],
                        }
                    )

                    st.success(
                        f"✅ Successfully merged {len(corpora_data)} corpora into '{merged_name}'"
                    )
                    st.info(
                        f"📊 Merged corpus contains {merged_data['summary']['total_papers']} unique papers"
                    )

                    # Show merged corpus table
                    st.markdown("#### Merged Corpus Overview")
                    merged_html = self.datatables.create_papers_table(
                        merged_data, "merged_papers_table"
                    )
                    st.components.v1.html(merged_html, height=600, scrolling=True)

                except Exception as e:
                    st.error(f"❌ Error merging corpora: {str(e)}")

        # Rerun search functionality
        st.markdown("### Rerun Searches")

        st.markdown(
            """
        **Rerun with Different Parameters:**
        - Modify existing queries with new parameters
        - Update corpora with additional papers
        - Change date ranges or result limits
        """
        )

        # Show existing corpora for rerun
        for i, corpus in enumerate(st.session_state.corpora):
            if corpus["name"] in selected_corpora:
                with st.expander(f"🔄 Rerun: {corpus['name']}"):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown(f"**Current Query:** {corpus['query']}")
                        st.markdown(
                            f"**Repository:** {self.supported_apis.get(corpus['api'], corpus['api'])}"
                        )
                        st.markdown(
                            f"**Current Papers:** {corpus['downloaded_papers']}"
                        )

                    with col2:
                        new_limit = st.number_input(
                            f"New Limit for {corpus['name']}:",
                            min_value=1,
                            max_value=10000,
                            value=corpus["downloaded_papers"],
                            key=f"rerun_limit_{i}",
                        )

                        if st.button(f"🔄 Rerun {corpus['name']}", key=f"rerun_{i}"):
                            st.info(
                                f"Rerun functionality will be implemented to update {corpus['name']} with {new_limit} papers"
                            )

    def render_fulltext_search(self):
        """Render the standalone fulltext search page"""
        st.markdown(
            '<h2 class="section-header">🔍 Fulltext Search</h2>', unsafe_allow_html=True
        )

        st.markdown(
            """
        <div class="info-box">
            <strong>Search Within Downloaded Papers:</strong> Search the fulltext content of your downloaded papers
            to find specific terms, phrases, or concepts within the actual paper content.
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Check if we have any corpora
        if "corpora" not in st.session_state or not st.session_state.corpora:
            st.warning("No corpora found. Download some papers first!")
            return

        # Corpus selection
        st.markdown("### Select Corpus to Search")

        available_corpora = [corpus["name"] for corpus in st.session_state.corpora]
        selected_corpus = st.selectbox(
            "Choose a corpus:",
            available_corpora,
            format_func=lambda x: f"{x} ({next(c['downloaded_papers'] for c in st.session_state.corpora if c['name'] == x)} papers)",
        )

        if not selected_corpus:
            st.info("Please select a corpus to search.")
            return

        # Check if corpus directory exists
        if not os.path.exists(selected_corpus):
            st.error(f"❌ Corpus directory not found: {selected_corpus}")
            st.info(
                "The corpus may have been moved or deleted. Please re-download the papers."
            )
            return

        # Load corpus data
        try:
            output_data = self.datatables.read_pygetpapers_output(selected_corpus)
        except Exception as e:
            st.error(f"❌ Error loading corpus: {str(e)}")
            return

        # Search interface
        st.markdown("### Search Configuration")

        col1, col2 = st.columns([2, 1])

        with col1:
            search_terms = st.text_area(
                "Search Terms:",
                placeholder="Enter search terms (one per line or comma-separated)...\n\nExamples:\nmachine learning\nartificial intelligence\nneural network\ndeep learning, reinforcement learning",
                height=150,
            )

            # Advanced search options
            with st.expander("🔧 Advanced Search Options"):
                col_a, col_b = st.columns(2)
                with col_a:
                    case_sensitive = st.checkbox("Case Sensitive", value=False)
                with col_b:
                    st.slider("Context Length", 50, 200, 100)
                    st.number_input("Max Results", 100, 10000, 1000)

        with col2:
            st.markdown("**Search in:**")
            search_fields = st.multiselect(
                "Content Types:",
                ["xml", "pdf", "supplementary", "metadata"],
                default=["xml", "metadata"],
            )

            st.markdown("**Search Options:**")
            st.markdown("- **XML**: Fulltext XML content")
            st.markdown("- **PDF**: PDF text content")
            st.markdown("- **Supplementary**: Supplementary files")
            st.markdown("- **Metadata**: Paper metadata")

        # Process search
        if search_terms.strip():
            # Parse search terms
            terms = []
            for line in search_terms.split("\n"):
                line_terms = [term.strip() for term in line.split(",") if term.strip()]
                terms.extend(line_terms)

            if terms:
                # Search button
                if st.button(
                    "🔍 Search Fulltext", type="primary", use_container_width=True
                ):
                    with st.spinner(
                        f"Searching {len(output_data['paper_directories'])} papers..."
                    ):
                        search_results = self.datatables.search_fulltext(
                            output_data, terms, search_fields, case_sensitive
                        )

                        # Store results in session state
                        st.session_state.fulltext_search_results = search_results
                        st.session_state.fulltext_corpus_data = output_data

                # Display results
                if (
                    "fulltext_search_results" in st.session_state
                    and st.session_state.fulltext_search_results
                ):
                    results = st.session_state.fulltext_search_results

                    # Results summary
                    st.markdown("### Search Results Summary")

                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Matches", results["summary"]["total_matches"])
                    with col2:
                        st.metric(
                            "Papers with Matches",
                            results["summary"]["papers_with_matches"],
                        )
                    with col3:
                        st.metric(
                            "Match Rate", f"{results['summary']['match_rate']:.1%}"
                        )
                    with col4:
                        st.metric("Search Terms", len(results["search_terms"]))

                    # Search terms used
                    st.markdown(
                        f"**Search Terms:** {', '.join(results['search_terms'])}"
                    )
                    st.markdown(
                        f"**Searched in:** {', '.join(results['search_fields'])}"
                    )

                    # Results table
                    st.markdown("### Search Results")

                    if results["matches"]:
                        results_html = self.datatables.create_search_results_table(
                            results, "fulltext_search_results_table"
                        )
                        st.components.v1.html(results_html, height=800, scrolling=True)

                        # Actions
                        st.markdown("### Actions")

                        col1, col2, col3 = st.columns(3)

                        with col1:
                            if st.button("📋 Filter Papers by Matches"):
                                filtered_data = self.datatables.filter_papers_by_search(
                                    st.session_state.fulltext_corpus_data, results
                                )

                                st.session_state.filtered_corpus_data = filtered_data
                                st.success(
                                    f"✅ Filtered to {filtered_data['summary']['total_papers']} papers with matches"
                                )

                        with col2:
                            if st.button("📄 Export Search Results"):
                                # Create CSV with search results
                                search_csv_data = []
                                for match in results["matches"]:
                                    search_csv_data.append(
                                        {
                                            "Paper_ID": match["paper_id"],
                                            "Search_Term": match["term"],
                                            "File": match["file"],
                                            "Line_Number": match["line_number"],
                                            "Context": match["context"],
                                            "Content_Type": match["content_type"],
                                        }
                                    )

                                search_df = pd.DataFrame(search_csv_data)
                                search_csv_filename = (
                                    f"{selected_corpus}_fulltext_search_results.csv"
                                )
                                search_df.to_csv(search_csv_filename, index=False)

                                st.success(
                                    f"✅ Search results exported to {search_csv_filename}"
                                )

                                # Provide download link
                                with open(search_csv_filename, "r") as f:
                                    csv_data = f.read()
                                st.download_button(
                                    label="📥 Download Search Results",
                                    data=csv_data,
                                    file_name=search_csv_filename,
                                    mime="text/csv",
                                )

                        with col3:
                            if st.button("📊 Show Match Distribution"):
                                # Create match distribution chart
                                match_counts = {}
                                for match in results["matches"]:
                                    paper_id = match["paper_id"]
                                    match_counts[paper_id] = (
                                        match_counts.get(paper_id, 0) + 1
                                    )

                                if match_counts:
                                    df_matches = pd.DataFrame(
                                        [
                                            {"Paper_ID": paper_id, "Matches": count}
                                            for paper_id, count in match_counts.items()
                                        ]
                                    )

                                    fig = px.histogram(
                                        df_matches,
                                        x="Matches",
                                        title="Distribution of Matches per Paper",
                                        nbins=20,
                                    )
                                    st.plotly_chart(fig, use_container_width=True)

                        # Show filtered papers if available
                        if "filtered_corpus_data" in st.session_state:
                            st.markdown("### Papers with Matches")
                            filtered_html = self.datatables.create_papers_table(
                                st.session_state.filtered_corpus_data,
                                "filtered_papers_table",
                            )
                            st.components.v1.html(
                                filtered_html, height=600, scrolling=True
                            )
                    else:
                        st.info("No matches found for the given search terms.")
        else:
            st.info(
                "Enter search terms to search within the fulltext content of papers."
            )

    def render_xml_to_html(self):
        """Render the XML to HTML conversion page"""
        st.markdown(
            '<h2 class="section-header">🔄 XML to HTML Conversion</h2>',
            unsafe_allow_html=True,
        )

        st.markdown(
            """
        <div class="info-box">
            <strong>JATS4R Integration & Fallback:</strong> Convert JATS XML files to HTML using JATS4R XSLT stylesheets or a built-in fallback converter. This tool automatically uses the best available method.
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Corpus selection
        st.markdown("### 📁 Select Corpus")

        if "corpora" not in st.session_state or not st.session_state.corpora:
            st.warning("No corpora found. Please download some papers first!")
            return

        corpus_options = {corpus["name"]: corpus for corpus in st.session_state.corpora}
        selected_corpus_name = st.selectbox(
            "Choose a corpus to convert:",
            options=list(corpus_options.keys()),
            format_func=lambda x: f"{x} ({corpus_options[x]['downloaded_papers']} papers)",
        )

        if selected_corpus_name:
            selected_corpus = corpus_options[selected_corpus_name]
            corpus_path = selected_corpus.get("path", selected_corpus_name)
            corpus_dir = Path(corpus_path)

            # Count XML and HTML files
            xml_files = list(corpus_dir.rglob("*.xml"))
            # Look for HTML files with .xml.html naming convention
            html_files = [
                f for f in corpus_dir.rglob("*.xml.html") if f.name != "index.html"
            ]
            xml_count = len(xml_files)
            html_count = len(html_files)

            st.markdown("### 📊 HTML Conversion Status")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("XML Files", xml_count)
            with col2:
                st.metric("HTML Files", html_count)

            if html_count < xml_count:
                st.warning(
                    f"Only {html_count} of {xml_count} XML files have HTML. You can convert the rest."
                )
                if st.button("🔄 Convert All XML to HTML", type="primary"):
                    with st.spinner(
                        "Converting XML files to HTML (using best available method)..."
                    ):
                        # Use CLI backend for robust conversion (uses fallback if needed)
                        result = self.run_pygetpapers_command(
                            ["--convert_html", str(corpus_path)]
                        )
                        if result["success"]:
                            st.success("✅ Conversion complete!")
                        else:
                            st.error("❌ Conversion failed!")
                        st.info(f"STDOUT:\n{result['stdout']}")
                        if result["stderr"]:
                            st.info(f"STDERR:\n{result['stderr']}")
                    st.experimental_rerun()
            else:
                st.success("All XML files have corresponding HTML files.")

            # Show converted files
            if html_count > 0:
                st.markdown("### 📄 Converted HTML Files")
                if html_files:
                    st.markdown("**Recent conversions:**")
                    for html_file in sorted(html_files)[:5]:
                        relative_path = html_file.relative_to(corpus_dir)
                        st.markdown(f"- 📄 [{html_file.stem}]({relative_path})")
                    if len(html_files) > 5:
                        st.markdown(f"... and {len(html_files) - 5} more files")
                    # Open index button
                    index_file = corpus_dir / "index.html"
                    if index_file.exists():
                        st.markdown(f"📄 [Open HTML Index]({index_file})")
                else:
                    st.info("No HTML files found in this corpus.")

    def render_settings(self):
        """Render the settings page"""
        st.markdown(
            '<h2 class="section-header">⚙️ Settings</h2>', unsafe_allow_html=True
        )

        # Default settings
        st.markdown("### Default Settings")

        col1, col2 = st.columns(2)

        with col1:
            st.selectbox(
                "Default Repository:",
                options=list(self.supported_apis.keys()),
                index=0,
                format_func=lambda x: self.supported_apis[x],
            )

            st.number_input(
                "Default Result Limit:", min_value=10, max_value=1000, value=10
            )

        with col2:
            st.text_input(
                "Default Output Directory Pattern:",
                value="pygetpapers_output_{timestamp}",
            )

            st.checkbox("Auto-save queries", value=True)

        # Advanced settings
        st.markdown("### Advanced Settings")

        st.number_input(
            "Command Timeout (seconds):", min_value=60, max_value=1800, value=300
        )

        # Save settings
        if st.button("💾 Save Settings"):
            st.success("Settings saved!")

    def render_help(self):
        """Render the help page"""
        st.markdown(
            '<h2 class="section-header">❓ Help & Documentation</h2>',
            unsafe_allow_html=True,
        )

        # Quick start guide
        with st.expander("🚀 Quick Start Guide", expanded=True):
            st.markdown(
                """
            1. **Choose a Repository**: Select from the available scholarly repositories
            2. **Enter Your Query**: Use simple keywords or build complex Boolean queries
            3. **Configure Download Options**: Choose what files to download
            4. **Click Search**: Start the download process
            5. **Manage Your Corpus**: View and organize downloaded papers
            """
            )

        # Repository information
        with st.expander("📚 Repository Information"):
            repo_info = pd.DataFrame(
                [
                    ["Europe PMC", "Biomedical literature", "Full-featured", "✅"],
                    ["arXiv", "Physics, math, CS", "PDF/XML", "✅"],
                    ["Crossref", "Academic metadata", "Metadata only", "✅"],
                    ["OpenAlex", "Academic papers", "PDF available", "✅"],
                    ["bioRxiv", "Biology preprints", "Date-based", "❌"],
                    ["medRxiv", "Medical preprints", "Date-based", "❌"],
                    ["Rxivist", "Preprint search", "Basic search", "❌"],
                ],
                columns=["Repository", "Content", "Features", "Query Support"],
            )

            st.dataframe(repo_info, use_container_width=True)

        # Query syntax
        with st.expander("🔍 Query Syntax Guide"):
            st.markdown(
                """
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
            """
            )

        # Troubleshooting
        with st.expander("🔧 Troubleshooting"):
            st.markdown(
                """
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
            """
            )

    def run(self):
        """Main application runner"""
        # Initialize session state for datatables
        if "total_papers" not in st.session_state:
            st.session_state.total_papers = 0
        if "total_corpora" not in st.session_state:
            st.session_state.total_corpora = 0
        if "corpora" not in st.session_state:
            st.session_state.corpora = []
        if "show_datatable" not in st.session_state:
            st.session_state.show_datatable = False
        if "selected_corpus" not in st.session_state:
            st.session_state.selected_corpus = None
        if "show_paper_details" not in st.session_state:
            st.session_state.show_paper_details = False

        # Scan for existing corpora on first load
        if "corpora_scanned" not in st.session_state:
            self._scan_for_existing_corpora()
            st.session_state.corporas_scanned = True

        self.render_header()
        page = self.render_sidebar()

        if page == "Search Papers":
            self.render_search_page()
        elif page == "Query Builder":
            self.render_query_builder()
        elif page == "Corpus Manager":
            self.render_corpus_manager()
        elif page == "Data Tables":
            self.render_data_tables()
        elif page == "Figures Gallery":
            self.render_figures_gallery()
        elif page == "Corpus Comparison":
            self.render_corpus_comparison()
        elif page == "Fulltext Search":
            self.render_fulltext_search()
        elif page == "XML to HTML":
            self.render_xml_to_html()
        elif page == "Settings":
            self.render_settings()
        elif page == "Help":
            self.render_help()

    def _scan_for_existing_corpora(self):
        """Scan the current directory for existing pygetpapers output directories and add them to session state"""
        import json
        import os
        from datetime import datetime
        from pathlib import Path

        # Get current directory
        current_dir = Path.cwd()

        # Look for directories that look like pygetpapers output
        # Common patterns: directory names with timestamps or descriptive names
        corpus_dirs = []

        for item in current_dir.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                # Check if this looks like a pygetpapers output directory
                if self._is_pygetpapers_output(item):
                    corpus_dirs.append(item)

        # Add any new corpora to session state
        # Handle case where session state is not initialized
        try:
            existing_corpus_names = {
                corpus["name"] for corpus in st.session_state.corpora
            }
        except (AttributeError, KeyError):
            # Session state not initialized, start with empty set
            existing_corpus_names = set()
            # Initialize session state if possible
            try:
                if "corpora" not in st.session_state:
                    st.session_state.corpora = []
            except:
                pass  # Not in Streamlit context

        for corpus_dir in corpus_dirs:
            if corpus_dir.name not in existing_corpus_names:
                # Try to extract metadata about this corpus
                corpus_info = self._extract_corpus_info(corpus_dir)
                if corpus_info:
                    try:
                        st.session_state.corpora.append(corpus_info)
                        # Update stats for auto-detected corpora
                        if "total_papers" not in st.session_state:
                            st.session_state.total_papers = 0
                        if "total_corpora" not in st.session_state:
                            st.session_state.total_corpora = 0

                        st.session_state.total_papers += corpus_info.get(
                            "downloaded_papers", 0
                        )
                        st.session_state.total_corpora += 1
                    except:
                        # Not in Streamlit context, just continue
                        pass

    def _is_pygetpapers_output(self, directory: Path) -> bool:
        """Check if a directory looks like pygetpapers output"""
        # Look for characteristic files
        characteristic_files = [
            "eupmc_results.json",
            "europe_pmc.csv",
            "crossref_results.json",
            "arxiv_results.json",
            "openalex_results.json",
        ]

        # Check if any characteristic files exist
        for file_name in characteristic_files:
            if (directory / file_name).exists():
                return True

        # Also check if it contains subdirectories that look like paper IDs
        # (e.g., PMC12345678, arXiv:1234.5678, etc.)
        paper_dirs = [d for d in directory.iterdir() if d.is_dir()]
        if len(paper_dirs) > 0:
            # Check if at least some look like paper IDs
            paper_id_patterns = ["PMC", "arXiv:", "doi_"]
            pattern_matches = 0
            for paper_dir in paper_dirs[:5]:  # Check first 5
                if any(pattern in paper_dir.name for pattern in paper_id_patterns):
                    pattern_matches += 1

            if pattern_matches >= 2:  # At least 2 out of 5 look like paper IDs
                return True

        return False

    def _extract_corpus_info(self, corpus_dir: Path) -> dict:
        """Extract information about a corpus directory"""
        try:
            # Count actually downloaded papers (subdirectories that look like paper IDs)
            paper_dirs = [d for d in corpus_dir.iterdir() if d.is_dir()]
            downloaded_papers_count = len(paper_dirs)

            # Try to determine the API/repository
            api = "Unknown"
            if (corpus_dir / "eupmc_results.json").exists():
                api = "eupmc"
            elif (corpus_dir / "crossref_results.json").exists():
                api = "crossref"
            elif (corpus_dir / "arxiv_results.json").exists():
                api = "arxiv"
            elif (corpus_dir / "openalex_results.json").exists():
                api = "openalex"

            # Try to get creation date from directory name or metadata
            date_created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Look for timestamp in directory name
            import re

            timestamp_match = re.search(r"(\d{8}_\d{6})", corpus_dir.name)
            if timestamp_match:
                try:
                    timestamp = timestamp_match.group(1)
                    date_obj = datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
                    date_created = date_obj.strftime("%Y-%m-%d %H:%M:%S")
                except ValueError:
                    pass

            # Try to extract query, requested limit, and total hits from metadata files
            query = "Unknown"
            requested_limit = 0
            total_hits = 0

            try:
                if (corpus_dir / "eupmc_results.json").exists():
                    with open(corpus_dir / "eupmc_results.json", "r") as f:
                        data = json.load(f)
                        if "request" in data and "query" in data["request"]:
                            query = data["request"]["query"]
                        # Extract requested limit from request parameters
                        if "request" in data and "pageSize" in data["request"]:
                            requested_limit = data["request"]["pageSize"]
                        elif "request" in data and "limit" in data["request"]:
                            requested_limit = data["request"]["limit"]
                        # Extract total hits
                        if "resultList" in data and "hitCount" in data["resultList"]:
                            total_hits = data["resultList"]["hitCount"]
                elif (corpus_dir / "europe_pmc.csv").exists():
                    # Try to get count from CSV
                    df = pd.read_csv(corpus_dir / "europe_pmc.csv")
                    total_hits = len(df)
                    # For CSV, assume requested limit is the number of rows (since we don't have request info)
                    requested_limit = len(df)
            except Exception:
                pass

            # Use directory name as repository name
            repository_name = corpus_dir.name

            return {
                "name": repository_name,
                "path": str(corpus_dir),
                "api": api,
                "query": query,
                "downloaded_papers": downloaded_papers_count,
                "requested_limit": requested_limit,
                "total_hits": total_hits,
                "date_created": date_created,
                "auto_detected": True,
            }

        except Exception as e:
            st.warning(f"Error extracting info from {corpus_dir.name}: {e}")
            return None


# Run the application
if __name__ == "__main__":
    app = PygetpapersUI()
    app.run()
