"""
Pygetpapers Streamlit Web Interface (No Dependencies Version)

A lightweight web interface for pygetpapers without external dependencies.
"""

import base64
import json
import logging
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import streamlit as st

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from datatables_integration import PygetpapersDatatables
except ImportError:
    # Fallback if datatables module is not available
    PygetpapersDatatables = None
    logger.warning("Datatables module not available. Some features will be limited.")

# Page configuration
st.set_page_config(
    page_title="Pygetpapers UI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown(
    """
    <style>
    .section-header {
        color: #1f77b4;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 5px;
        border-left: 4px solid #1f77b4;
        margin: 10px 0;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        margin: 10px 0;
    }
    .metric-value {
        font-size: 2em;
        font-weight: bold;
        color: #1f77b4;
    }
    .metric-label {
        color: #666;
        font-size: 0.9em;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


class PygetpapersUINoDeps:
    """
    Pygetpapers UI without external dependencies.
    """

    def __init__(self):
        self.supported_apis = {
            "eupmc": "Europe PMC",
            "arxiv": "arXiv",
            "crossref": "Crossref",
            "openalex": "OpenAlex",
            "biorxiv": "bioRxiv",
            "medrxiv": "medRxiv",
            "rxivist": "Rxivist",
        }

        self.api_features = {
            "eupmc": {
                "xml": True,
                "pdf": True,
                "supplementary": True,
                "references": True,
                "citations": True,
                "date_range": True,
            },
            "arxiv": {
                "xml": True,
                "pdf": True,
                "supplementary": False,
                "references": False,
                "citations": False,
                "date_range": False,
            },
            "crossref": {
                "xml": False,
                "pdf": False,
                "supplementary": False,
                "references": False,
                "citations": False,
                "date_range": True,
            },
            "openalex": {
                "xml": False,
                "pdf": True,
                "supplementary": False,
                "references": False,
                "citations": False,
                "date_range": True,
            },
            "biorxiv": {
                "xml": False,
                "pdf": True,
                "supplementary": False,
                "references": False,
                "citations": False,
                "date_range": False,
            },
            "medrxiv": {
                "xml": False,
                "pdf": True,
                "supplementary": False,
                "references": False,
                "citations": False,
                "date_range": False,
            },
            "rxivist": {
                "xml": False,
                "pdf": False,
                "supplementary": False,
                "references": False,
                "citations": False,
                "date_range": False,
            },
        }

        # Initialize datatables
        self.datatables = PygetpapersDatatables()

    def run_pygetpapers_command(
        self, args: List[str], progress_placeholder=None
    ) -> Dict[str, any]:
        """
        Run pygetpapers command and return results with real-time progress tracking.
        """
        try:
            # Add pygetpapers command
            full_args = ["pygetpapers"] + args

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
                full_args,
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

            return {
                "success": returncode == 0,
                "stdout": "\n".join(stdout_lines),
                "stderr": "\n".join(stderr_lines),
                "returncode": returncode,
                "progress_data": progress_data,
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Command timed out after 5 minutes",
                "returncode": -1,
                "progress_data": progress_data if "progress_data" in locals() else {},
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1,
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

    def build_query_string(self, query_parts: List[Dict[str, str]]) -> str:
        """
        Build query string from query parts.
        """
        if not query_parts:
            return ""

        query_string = ""
        for i, part in enumerate(query_parts):
            if not part["query"].strip():
                continue

            if i > 0:
                query_string += f" {part['operator']} "

            # Add field-specific search if not "all"
            if part["field"] != "all":
                query_string += f'{part["field"].upper()}:"{part["query"]}"'
            else:
                query_string += part["query"]

        return query_string

    def render_header(self):
        """Render the application header"""
        st.markdown(
            """
            <div style="text-align: center; padding: 20px;">
                <h1>📚 Pygetpapers UI</h1>
                <p><em>Download and manage scholarly papers with ease</em></p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    def render_sidebar(self):
        """Render the sidebar navigation"""
        st.sidebar.markdown("## Navigation")

        page = st.sidebar.selectbox(
            "Choose a page:",
            [
                "Search Papers",
                "Query Builder",
                "Corpus Manager",
                "Data Tables",
                "XML to HTML",
                "Settings",
                "Help",
            ],
        )

        # Show statistics in sidebar
        st.sidebar.markdown("---")
        st.sidebar.markdown("## Statistics")

        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.metric("Total Papers", st.session_state.get("total_papers", 0))
        with col2:
            st.metric("Total Corpora", st.session_state.get("total_corpora", 0))

        return page

    def render_search_page(self):
        """Render the main search page"""
        st.markdown(
            '<h2 class="section-header">🔍 Search Papers</h2>',
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="info-box">
                <strong>Quick Start:</strong> Choose a repository, enter your search query, 
                configure download options, and click "Search and Download".
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Repository selection
        st.markdown("### 📚 Repository Selection")
        selected_api = st.selectbox(
            "Choose Repository:",
            options=list(self.supported_apis.keys()),
            format_func=lambda x: self.supported_apis[x],
        )

        features = self.api_features[selected_api]

        # Show repository info
        st.info(
            f"**{self.supported_apis[selected_api]}** supports: "
            + ", ".join([k for k, v in features.items() if v])
        )

        # Search query
        st.markdown("### 🔍 Search Query")

        # Check if we have a generated query from query builder
        if "generated_query" in st.session_state:
            default_query = st.session_state.generated_query
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

                # Store output directory for corpus management
                if "corpora" not in st.session_state:
                    st.session_state.corpora = []
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
                <strong>Build Complex Queries:</strong> Use this tool to create sophisticated
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

        # Generate query
        if st.button("🔧 Generate Query"):
            query_string = self.build_query_string(st.session_state.query_parts)
            if query_string:
                st.markdown("### Generated Query")
                st.code(query_string)

                # Copy to search page
                if st.button("📋 Use This Query"):
                    st.session_state.generated_query = query_string
                    st.success("Query copied! Go to Search Papers to use it.")
            else:
                st.warning("Please enter at least one query part.")

        # Show current query parts
        if st.session_state.query_parts:
            st.markdown("### Current Query Parts")
            for i, part in enumerate(st.session_state.query_parts):
                if part["query"].strip():
                    operator = f" {part['operator']} " if i > 0 else ""
                    field = (
                        f"{part['field'].upper()}:" if part["field"] != "all" else ""
                    )
                    st.markdown(
                        f"**Part {i + 1}:** {operator}{field}\"{part['query']}\""
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
            st.info("No corpora found. Download some papers first!")
            return

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

    def render_data_tables(self):
        """Render the data tables page"""
        st.markdown(
            '<h2 class="section-header">📊 Data Tables</h2>',
            unsafe_allow_html=True,
        )

        if not st.session_state.get("corpora"):
            st.info("No corpora found. Download some papers first!")
            return

        # Corpus selection
        corpus_names = [corpus["name"] for corpus in st.session_state.corpora]
        selected_corpus = st.selectbox("Select Corpus:", options=corpus_names)

        if selected_corpus:
            try:
                output_data = self.datatables.read_pygetpapers_output(selected_corpus)

                # Show different table types
                tab1, tab2, tab3 = st.tabs(["Papers", "Metadata", "Summary"])

                with tab1:
                    st.markdown("### Papers Table")
                    papers_html = self.datatables.create_papers_table(output_data)
                    st.components.v1.html(papers_html, height=600, scrolling=True)

                with tab2:
                    if output_data["metadata_files"]:
                        st.markdown("### Metadata Files")
                        metadata_html = self.datatables.create_metadata_table(
                            output_data
                        )
                        st.components.v1.html(metadata_html, height=400, scrolling=True)
                    else:
                        st.info("No metadata files found.")

                with tab3:
                    st.markdown("### Summary Statistics")
                    summary_html = self.datatables.create_summary_table(output_data)
                    st.components.v1.html(summary_html, height=300, scrolling=True)

            except Exception as e:
                st.error(f"Error reading corpus: {e}")

    def render_xml_to_html(self):
        """Render the XML to HTML conversion page"""
        st.markdown(
            '<h2 class="section-header">🔄 XML to HTML Conversion</h2>',
            unsafe_allow_html=True,
        )

        st.markdown(
            """
        <div class="info-box">
            <strong>JATS4R Integration:</strong> Convert JATS XML files to beautiful HTML using JATS4R XSLT stylesheets.
            This feature requires the full version with JATS4R support.
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.info(
            "📝 **Note:** XML to HTML conversion is available in the full version of the Streamlit app."
        )
        st.info("Please use `streamlit run streamlit_app.py` for JATS4R integration.")

    def render_settings(self):
        """Render the settings page"""
        st.markdown(
            '<h2 class="section-header">⚙️ Settings</h2>',
            unsafe_allow_html=True,
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

    def run(self):
        """Main application runner"""
        # Initialize session state
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
        elif page == "XML to HTML":
            self.render_xml_to_html()
        elif page == "Settings":
            self.render_settings()
        elif page == "Help":
            self.render_help()


# Run the application
if __name__ == "__main__":
    app = PygetpapersUINoDeps()
    app.run()
