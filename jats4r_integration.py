"""
JATS2HTML Integration for Pygetpapers

This module provides functionality to convert JATS XML files to HTML
using JATS2HTML XSLT stylesheets (alternative to defunct JATS4R).
"""

import logging
import os
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests

logger = logging.getLogger(__name__)


class JATS4RConverter:
    """
    JATS2HTML XSLT converter for JATS XML to HTML conversion.
    """

    def __init__(self, jats4r_path: Optional[str] = None):
        """
        Initialize JATS2HTML converter.

        Args:
            jats4r_path: Path to JATS2HTML installation. If None, will download automatically.
        """
        self.jats4r_path = jats4r_path or self._get_jats4r_path()
        self.xslt_path = None
        self.css_path = None
        self._setup_jats4r()

    def _get_jats4r_path(self) -> str:
        """Get or create JATS2HTML installation path."""
        # Use a local directory for JATS2HTML
        jats4r_dir = Path.cwd() / "jats4r"
        if not jats4r_dir.exists():
            jats4r_dir.mkdir(exist_ok=True)
        return str(jats4r_dir)

    def _setup_jats4r(self):
        """Download and setup JATS2HTML if not already present."""
        jats4r_dir = Path(self.jats4r_path)

        # Check if JATS2HTML is already set up
        xslt_file = jats4r_dir / "xslt" / "jats2html.xsl"
        if xslt_file.exists():
            self.xslt_path = str(xslt_file)
            self.css_path = str(jats4r_dir / "css" / "jats4r.css")
            logger.info(f"JATS2HTML found at {self.jats4r_path}")
            return

        # Download JATS2HTML from GitHub
        logger.info("Downloading JATS2HTML...")
        self._download_jats4r()

    def _download_jats4r(self):
        """Download JATS2HTML from GitHub (alternative to defunct JATS4R)."""
        try:
            # Download from transpect/jats2html (working alternative)
            url = "https://github.com/transpect/jats2html/archive/refs/heads/master.zip"
            response = requests.get(url, stream=True)
            response.raise_for_status()

            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp_file:
                for chunk in response.iter_content(chunk_size=8192):
                    tmp_file.write(chunk)
                tmp_file_path = tmp_file.name

            # Extract to JATS4R directory
            with zipfile.ZipFile(tmp_file_path, "r") as zip_ref:
                zip_ref.extractall(self.jats4r_path)

            # Move contents from extracted directory
            extracted_dir = Path(self.jats4r_path) / "jats2html-master"
            if extracted_dir.exists():
                # Move all contents to parent directory, handling conflicts
                for item in extracted_dir.iterdir():
                    dest_path = Path(self.jats4r_path) / item.name
                    if dest_path.exists():
                        if dest_path.is_dir():
                            # Merge directories
                            for subitem in item.iterdir():
                                subdest = dest_path / subitem.name
                                if subdest.exists():
                                    if subdest.is_file():
                                        subdest.unlink()  # Remove existing file
                                shutil.move(str(subitem), str(subdest))
                        else:
                            # Remove existing file and move new one
                            dest_path.unlink()
                            shutil.move(str(item), str(dest_path))
                    else:
                        shutil.move(str(item), str(dest_path))
                # Remove empty extracted directory
                shutil.rmtree(extracted_dir)

            # Clean up temporary file
            os.unlink(tmp_file_path)

            # Set paths - adapt to jats2html structure
            # Look for XSLT files in common locations
            possible_xslt_paths = [
                Path(self.jats4r_path) / "xslt" / "jats2html.xsl",
                Path(self.jats4r_path) / "jats2html.xsl",
                Path(self.jats4r_path) / "xsl" / "jats2html.xsl",
                Path(self.jats4r_path) / "transform" / "jats2html.xsl",
            ]

            self.xslt_path = None
            for xslt_path in possible_xslt_paths:
                if xslt_path.exists():
                    self.xslt_path = str(xslt_path)
                    break

            if not self.xslt_path:
                # Search for any .xsl file
                xsl_files = list(Path(self.jats4r_path).rglob("*.xsl"))
                if xsl_files:
                    self.xslt_path = str(xsl_files[0])
                    logger.info(f"Using XSLT file: {self.xslt_path}")
                else:
                    raise Exception("No XSLT files found in downloaded repository")

            # Look for CSS files
            possible_css_paths = [
                Path(self.jats4r_path) / "css" / "jats4r.css",
                Path(self.jats4r_path) / "css" / "jats2html.css",
                Path(self.jats4r_path) / "jats4r.css",
                Path(self.jats4r_path) / "jats2html.css",
            ]

            self.css_path = None
            for css_path in possible_css_paths:
                if css_path.exists():
                    self.css_path = str(css_path)
                    break

            logger.info("JATS2HTML downloaded and set up successfully")

        except Exception as e:
            logger.error(f"Failed to download JATS2HTML: {e}")
            raise

    def convert_xml_to_html(
        self, xml_file: str, output_file: str = None, include_css: bool = True
    ) -> Tuple[bool, str]:
        """
        Convert JATS XML file to HTML.

        Args:
            xml_file: Path to input XML file
            output_file: Path to output HTML file (optional)
            include_css: Whether to include CSS styling

        Returns:
            Tuple of (success, output_file_path or error_message)
        """
        try:
            xml_path = Path(xml_file)
            if not xml_path.exists():
                return False, f"XML file not found: {xml_file}"

            # Generate output filename if not provided
            if output_file is None:
                output_file = str(xml_path.with_suffix(".html"))

            # Check if xsltproc is available
            if not self._check_xsltproc():
                return False, "xsltproc not found. Please install libxslt."

            # Build xsltproc command
            cmd = ["xsltproc", "--output", output_file, self.xslt_path, str(xml_path)]

            # Run conversion
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode == 0:
                # Add CSS if requested
                if include_css and self.css_path and Path(self.css_path).exists():
                    self._add_css_to_html(output_file)

                return True, output_file
            else:
                # Check if it's an XSLT version compatibility issue
                if (
                    "compilation error" in result.stderr
                    or "XPath error" in result.stderr
                ):
                    return (
                        False,
                        "JATS2HTML XSLT requires XSLT 2.0, but xsltproc only supports XSLT 1.0. Please use Simple HTML Converter instead.",
                    )
                else:
                    return False, f"XSLT conversion failed: {result.stderr}"

        except subprocess.TimeoutExpired:
            return False, "XSLT conversion timed out"
        except Exception as e:
            return False, f"Conversion error: {str(e)}"

    def _check_xsltproc(self) -> bool:
        """Check if xsltproc is available."""
        try:
            result = subprocess.run(
                ["xsltproc", "--version"], capture_output=True, text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def _add_css_to_html(self, html_file: str):
        """Add CSS styling to HTML file."""
        try:
            with open(html_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Read CSS file
            with open(self.css_path, "r", encoding="utf-8") as f:
                css_content = f.read()

            # Insert CSS in head section
            if "<head>" in content:
                css_tag = f'<style type="text/css">\n{css_content}\n</style>'
                content = content.replace("<head>", f"<head>\n{css_tag}")
            else:
                # Add head section if it doesn't exist
                css_tag = (
                    f'<head>\n<style type="text/css">\n{css_content}\n</style>\n</head>'
                )
                content = content.replace("<html>", f"<html>\n{css_tag}")

            # Write back to file
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(content)

        except Exception as e:
            logger.warning(f"Failed to add CSS to HTML: {e}")

    def convert_corpus_xml_files(
        self, corpus_dir: str, output_dir: str = None
    ) -> Dict[str, List[str]]:
        """
        Convert all XML files in a corpus directory to HTML.
        HTML files will be placed as siblings to their corresponding XML files.

        Args:
            corpus_dir: Path to corpus directory
            output_dir: Output directory for HTML files (optional, not used for sibling placement)

        Returns:
            Dictionary with conversion results
        """
        results = {"successful": [], "failed": [], "skipped": []}

        try:
            corpus_path = Path(corpus_dir)
            if not corpus_path.exists():
                results["failed"].append(f"Corpus directory not found: {corpus_dir}")
                return results

            # Find all XML files
            xml_files = list(corpus_path.rglob("*.xml"))

            if not xml_files:
                results["skipped"].append("No XML files found in corpus")
                return results

            logger.info(f"Found {len(xml_files)} XML files to convert")

            for xml_file in xml_files:
                try:
                    # Create HTML file as sibling to XML file
                    html_file = xml_file.with_suffix(".html")

                    # Convert file
                    success, result = self.convert_xml_to_html(
                        str(xml_file), str(html_file)
                    )

                    if success:
                        results["successful"].append(str(html_file))
                        logger.info(f"Converted: {xml_file.name} -> {html_file.name}")
                    else:
                        results["failed"].append(f"{xml_file.name}: {result}")

                except Exception as e:
                    results["failed"].append(f"{xml_file.name}: {str(e)}")

            logger.info(
                f"Conversion complete: {len(results['successful'])} successful, "
                f"{len(results['failed'])} failed, {len(results['skipped'])} skipped"
            )

        except Exception as e:
            results["failed"].append(f"Corpus conversion error: {str(e)}")

        return results

    def get_conversion_status(self, corpus_dir: str) -> Dict[str, int]:
        """
        Get conversion status for a corpus.

        Args:
            corpus_dir: Path to corpus directory

        Returns:
            Dictionary with counts of XML and HTML files
        """
        try:
            corpus_path = Path(corpus_dir)
            if not corpus_path.exists():
                return {"xml_files": 0, "html_files": 0, "converted": 0}

            xml_files = list(corpus_path.rglob("*.xml"))
            html_files = list(corpus_path.rglob("*.html"))

            # Count converted files (HTML files that are siblings to XML files)
            converted = 0
            for xml_file in xml_files:
                html_file = xml_file.with_suffix(".html")
                if html_file.exists():
                    converted += 1

            return {
                "xml_files": len(xml_files),
                "html_files": len(html_files),
                "converted": converted,
            }

        except Exception as e:
            logger.error(f"Error getting conversion status: {e}")
            return {"xml_files": 0, "html_files": 0, "converted": 0}

    def create_html_index(self, corpus_dir: str, output_file: str = None) -> bool:
        """
        Create an HTML index file for all converted HTML files in a corpus.

        Args:
            corpus_dir: Path to corpus directory
            output_file: Output HTML index file (optional)

        Returns:
            True if successful, False otherwise
        """
        try:
            corpus_path = Path(corpus_dir)
            if not corpus_path.exists():
                return False

            if output_file is None:
                output_file = str(corpus_path / "index.html")

            # Find all HTML files (siblings to XML files)
            html_files = []
            xml_files = list(corpus_path.rglob("*.xml"))
            for xml_file in xml_files:
                html_file = xml_file.with_suffix(".html")
                if html_file.exists():
                    html_files.append(html_file)

            # Filter out index.html if it exists
            html_files = [f for f in html_files if f.name != "index.html"]

            if not html_files:
                return False

            # Create index HTML
            index_html = self._generate_index_html(html_files, corpus_path)

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(index_html)

            return True

        except Exception as e:
            logger.error(f"Error creating HTML index: {e}")
            return False

    def _generate_index_html(self, html_files: List[Path], corpus_path: Path) -> str:
        """Generate HTML index content."""
        html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JATS Corpus - HTML Index</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #333; }
        .file-list { list-style: none; padding: 0; }
        .file-list li { margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        .file-list a { text-decoration: none; color: #0066cc; font-weight: bold; }
        .file-list a:hover { text-decoration: underline; }
        .stats { background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0; }
    </style>
</head>
<body>
    <h1>📚 JATS Corpus - HTML Index</h1>
    <div class="stats">
        <strong>Corpus:</strong> {corpus_name}<br>
        <strong>Total HTML Files:</strong> {file_count}<br>
        <strong>Generated:</strong> {timestamp}
    </div>
    <h2>📄 Converted Papers</h2>
    <ul class="file-list">
""".format(
            corpus_name=corpus_path.name,
            file_count=len(html_files),
            timestamp=Path().cwd().stat().st_mtime,
        )

        for html_file in sorted(html_files):
            relative_path = html_file.relative_to(corpus_path)
            html_content += f'        <li><a href="{relative_path}" target="_blank">{html_file.stem}</a></li>\n'

        html_content += """    </ul>
    <p><em>Generated by Pygetpapers JATS4R Integration</em></p>
</body>
</html>"""

        return html_content
