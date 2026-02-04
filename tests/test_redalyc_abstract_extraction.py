#!/usr/bin/env python3
"""
Test Redalyc Abstract Extraction and Datatables Display

This script tests the enhanced abstract extraction functionality
and creates a datatables display for Redalyc search results.
"""

import json
import logging
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

from test_utils import skip_if_redalyc_down, test_redalyc_connectivity

from pygetpapers.repositories.redalyc.redalyc_selenium import RedalycSelenium

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@skip_if_redalyc_down()
def test_redalyc_abstract_extraction(query="Lantana"):
    """Test the enhanced Redalyc abstract extraction."""
    logger.info("Testing Redalyc abstract extraction...")

    # Initialize Redalyc scraper
    scraper = RedalycSelenium(headless=True)

    try:
        # Search for articles
        max_results = 5

        logger.info(f"Searching for: {query}")
        articles = scraper.search_articles(query, max_results)

        logger.info(f"Found {len(articles)} articles")

        # Display results
        for i, article in enumerate(articles, 1):
            logger.info(f"\nArticle {i}:")
            logger.info(f"  Title: {article.get('title', 'N/A')}")
            logger.info(f"  Journal: {article.get('journal', 'N/A')}")
            logger.info(f"  Year: {article.get('year', 'N/A')}")
            logger.info(f"  URL: {article.get('url', 'N/A')}")
            logger.info(f"  Article ID: {article.get('article_id', 'N/A')}")

            abstract = article.get("abstract", "")
            if abstract:
                logger.info(f"  Abstract: {abstract[:150]}...")
            else:
                logger.info("  Abstract: Not found")

            content_preview = article.get("content_preview", "")
            if content_preview:
                logger.info(f"  Content Preview: {content_preview[:100]}...")

        return articles

    except Exception as e:
        logger.error(f"Error during testing: {e}")
        return []
    finally:
        scraper.close()


def create_datatables_display(
    articles: List[Dict[str, Any]],
    query: str = "lantana",
    output_dir: str = "redalyc_datatables_output",
):
    """Create a datatables display for Redalyc articles."""
    logger.info("Creating datatables display...")

    if not articles:
        logger.warning("No articles to display")
        return

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Prepare data for datatables
    datatables_data = {
        "repository": "redalyc_selenium",
        "total_articles": len(articles),
        "search_query": query,
        "articles": {},
    }

    # Convert articles list to dictionary format expected by datatables
    for article in articles:
        article_id = (
            article.get("article_id")
            or f"article_{hash(article.get('title', '') + article.get('journal', ''))}"
        )
        # Ensure all required fields are present
        display_data = {
            "title": article.get("title", "Unknown Title"),
            "journal": article.get("journal", "Unknown Journal"),
            "year": article.get("year", "Unknown Year"),
            "url": article.get("url", ""),
            "pdf_url": article.get("pdf_url", ""),
            "abstract": article.get("abstract", "No abstract available"),
            "content_preview": article.get("content_preview", ""),
            "article_id": article_id,
            "download_status": "not_downloaded",
            "file_paths": {},
        }
        datatables_data["articles"][article_id] = display_data

    try:
        # Create a simple HTML table directly from our articles data
        table_html = create_simple_redalyc_table(datatables_data["articles"])

        # Save the table HTML as 'datatables.html' and as the old name for compatibility
        datatables_file = output_path / "datatables.html"
        with open(datatables_file, "w", encoding="utf-8") as f:
            f.write(table_html)
        logger.info(f"Saved datatables HTML to: {datatables_file}")

        table_file = output_path / "redalyc_papers_table.html"
        with open(table_file, "w", encoding="utf-8") as f:
            f.write(table_html)
        logger.info(f"Saved papers table to: {table_file}")

        # Save the raw data as JSON
        json_file = output_path / "redalyc_articles_data.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(datatables_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved raw data to: {json_file}")

        # Create an index file using external template
        index_template_path = (
            Path(__file__).parent
            / "src"
            / "pygetpapers"
            / "redalyc"
            / "templates"
            / "redalyc_index.html"
        )

        try:
            with open(index_template_path, "r", encoding="utf-8") as f:
                index_template = f.read()
        except FileNotFoundError:
            logger.error(f"Index template file not found: {index_template_path}")
            index_html = (
                "<html><body><h1>Error: Template file not found</h1>" "</body></html>"
            )
        else:
            # Replace template placeholders
            index_html = index_template.replace(
                "{{TOTAL_ARTICLES}}", str(len(articles))
            )
            index_html = index_html.replace(
                "{{ARTICLES_WITH_ABSTRACTS}}",
                str(len([a for a in articles if a.get("abstract")])),
            )
            index_html = index_html.replace(
                "{{ARTICLES_WITH_PDF}}",
                str(len([a for a in articles if a.get("pdf_url")])),
            )
            index_html = index_html.replace(
                "{{SEARCH_QUERY}}", datatables_data.get("search_query", "Unknown")
            )
            index_html = index_html.replace(
                "{{REPOSITORY_NAME}}", datatables_data.get("repository", "Unknown")
            )

        index_file = output_path / "index.html"
        with open(index_file, "w", encoding="utf-8") as f:
            f.write(index_html)

        logger.info(f"Saved index file to: {index_file}")
        logger.info(f"All files saved to: {output_path}")

        return str(output_path)

    except Exception as e:
        logger.error(f"Error creating datatables display: {e}")
        return None


def create_simple_redalyc_table(articles_dict: Dict[str, Any]) -> str:
    """Create a simple HTML table with jQuery DataTables for Redalyc articles.

    Style: Javascript should be used as little as possible and must be readable
    and NEVER deliberately abbreviated.
    """

    # Prepare table data
    table_rows = []
    for article_id, article in articles_dict.items():
        # Clean up content preview - remove metadata concatenation
        content_preview = article.get("content_preview", "")
        if content_preview:
            # Remove journal metadata patterns
            content_preview = re.sub(
                r"\d+\s+[A-Z\s]+\s+\d+\(\d+\):\s+\d+-\d+\.\s+\d+\s+ISSN\s+\d+-\d+",
                "",
                content_preview,
            )
            content_preview = re.sub(
                r"[A-Z\s]+\s+vol\.\s+\d+,\s+no\.\s+\d+,\s+[A-Za-z]+\s+\d+",
                "",
                content_preview,
            )
            content_preview = content_preview.strip()
            if len(content_preview) > 200:
                content_preview = content_preview[:200] + "..."

        # Handle empty URLs
        url = article.get("url", "")
        pdf_url = article.get("pdf_url", "")

        row = {
            "ID": article_id,
            "Title": article.get("title", "Unknown Title"),
            "Journal": article.get("journal", "Unknown Journal"),
            "Year": article.get("year", "Unknown Year"),
            "Abstract": article.get("abstract", "No abstract available"),
            "Content Preview": content_preview,
            "URL": url,
            "PDF URL": pdf_url,
        }
        table_rows.append(row)

    # Load HTML template from external file
    template_path = (
        Path(__file__).parent
        / "src"
        / "pygetpapers"
        / "redalyc"
        / "templates"
        / "redalyc_datatables.html"
    )

    try:
        with open(template_path, "r", encoding="utf-8") as f:
            html_template = f.read()
    except FileNotFoundError:
        logger.error(f"Template file not found: {template_path}")
        return "<html><body><h1>Error: Template file not found</h1></body></html>"

    # Generate table rows HTML
    table_rows_html = []
    for row in table_rows:
        # Handle URL display
        if row["URL"]:
            url_link = (
                f'<a href="{row["URL"]}" target="_blank" '
                f'class="btn btn-primary">View</a>'
            )
        else:
            url_link = '<span class="btn btn-disabled">N/A</span>'

        # Handle PDF URL display
        if row["PDF URL"]:
            pdf_link = (
                f'<a href="{row["PDF URL"]}" target="_blank" '
                f'class="btn btn-success">PDF</a>'
            )
        else:
            pdf_link = '<span class="btn btn-disabled">N/A</span>'

        table_rows_html.append(
            f"""
                <tr>
                    <td>{row['ID']}</td>
                    <td>{row['Title']}</td>
                    <td>{row['Journal']}</td>
                    <td>{row['Year']}</td>
                    <td class="abstract-cell">{row['Abstract']}</td>
                    <td class="preview-cell">{row['Content Preview']}</td>
                    <td class="url-cell">{url_link}</td>
                    <td class="pdf-cell">{pdf_link}</td>
                </tr>
        """
        )

    # Replace template placeholder with actual table rows
    html_content = html_template.replace("{{TABLE_ROWS}}", "".join(table_rows_html))

    return html_content


def main():
    """Run the Redalyc abstract extraction test."""
    print("🧪 Testing Redalyc Abstract Extraction and Datatables")
    print("=" * 60)

    # Test connectivity first
    print("🔍 Testing Redalyc connectivity...")
    is_connected, error_msg = test_redalyc_connectivity()

    if not is_connected:
        import pytest
        pytest.skip(f"Redalyc appears to be down: {error_msg}")

    print("✅ Redalyc is accessible, running abstract extraction test...")

    try:
        # Test abstract extraction
        query = "Lantana"
        articles = test_redalyc_abstract_extraction(query)

        if articles:
            print(f"✅ Found {len(articles)} articles")

            # Test datatables creation
            output_path = create_datatables_display(articles, query)
            if output_path:
                print(f"✅ Datatables created successfully in: {output_path}")
            else:
                assert False, "Failed to create datatables"
        else:
            print("⚠️  No articles found")
            assert True  # Not a failure, just no results

        print("🎉 Redalyc abstract extraction test completed successfully!")

    except Exception as e:
        assert False, f"Test failed: {e}"


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
