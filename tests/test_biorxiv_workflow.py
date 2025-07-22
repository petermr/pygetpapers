#!/usr/bin/env python3
"""
Test script demonstrating the complete bioRxiv workflow.

This script implements the full workflow described:
1. Send a query and retrieve hit list with cursor/pagination
2. For each hit: download metadata, download HTML, provide PDF link
3. Handle pagination and cursor management
4. Reset cursor/pointer if required
"""

import json
import logging
from pathlib import Path

from pygetpapers.repositories.biorxiv.biorxiv_advanced_scraper import BioRxivAdvancedScraper

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def demonstrate_full_workflow():
    """Demonstrate the complete bioRxiv workflow."""
    print("🔬 BioRxiv Full Workflow Demonstration")
    print("=" * 60)

    # Initialize scraper
    scraper = BioRxivAdvancedScraper(output_dir="biorxiv_workflow_output", delay=1.0)

    # Step 1: Send a query and retrieve hit list
    print("\n📋 STEP 1: Sending query and retrieving hit list")
    print("-" * 40)

    query = "urban heat island"
    max_papers = 3  # Small number for demonstration

    print(f"Query: '{query}'")
    print(f"Max papers to retrieve: {max_papers}")

    # Get search results with pagination
    papers_found = []
    for paper_data in scraper.search_with_pagination(
        query, max_papers, results_per_page=10
    ):
        paper = paper_data["paper"]
        pagination = paper_data["pagination"]

        papers_found.append(paper)

        print(f"\n📄 Paper {len(papers_found)}:")
        print(f"   Title: {paper['title'][:80]}...")
        print(f"   DOI: {paper['doi']}")
        print(
            f"   Authors: {', '.join(paper['authors'][:3])}{'...' if len(paper['authors']) > 3 else ''}"
        )
        print(
            f"   Page: {pagination['current_page']}, Paper #{pagination['papers_found']}"
        )

    print(f"\n✅ Retrieved {len(papers_found)} papers from search results")

    # Step 2: Process each hit
    print("\n📥 STEP 2: Processing each hit (metadata, HTML, PDF)")
    print("-" * 40)

    processed_papers = []

    for i, paper in enumerate(papers_found, 1):
        doi = paper["doi"]

        print(f"\n🔄 Processing paper {i}/{len(papers_found)}: {doi}")

        # Download full content (metadata, HTML, PDF link)
        download_result = scraper.download_paper_full_content(doi)

        if "error" not in download_result:
            processed_papers.append(download_result)

            print(f"   ✅ Metadata: {download_result['metadata_file']}")
            print(f"   ✅ HTML: {download_result['html_file']}")
            print(f"   ✅ PDF: {download_result['pdf_url']}")
            print(f"   ✅ Size: {download_result['file_size_bytes']:,} bytes")

            # Show some metadata
            metadata = download_result["metadata"]
            if "title" in metadata:
                print(f"   📝 Title: {metadata['title'][:60]}...")
            if "biorxiv_id" in metadata:
                print(f"   🆔 bioRxiv ID: {metadata['biorxiv_id']}")
        else:
            print(f"   ❌ Error: {download_result['error']}")

    print(f"\n✅ Successfully processed {len(processed_papers)} papers")

    # Step 3: Demonstrate pagination/cursor management
    print("\n🔄 STEP 3: Pagination and cursor management")
    print("-" * 40)

    # Show how to get next page
    print("Demonstrating pagination capabilities:")

    # Get first page
    first_page_papers = []
    for paper_data in scraper.search_with_pagination(
        query, max_papers=2, results_per_page=10, start_page=0
    ):
        first_page_papers.append(paper_data["paper"])

    print(f"   First page: {len(first_page_papers)} papers")

    # Get second page
    second_page_papers = []
    for paper_data in scraper.search_with_pagination(
        query, max_papers=2, results_per_page=10, start_page=1
    ):
        second_page_papers.append(paper_data["paper"])

    print(f"   Second page: {len(second_page_papers)} papers")

    # Verify different papers
    first_dois = {p["doi"] for p in first_page_papers}
    second_dois = {p["doi"] for p in second_page_papers}

    if first_dois != second_dois:
        print("   ✅ Pagination working: different papers on different pages")
    else:
        print("   ⚠️  Pagination issue: same papers on different pages")

    # Step 4: Create summary report
    print("\n📊 STEP 4: Summary report")
    print("-" * 40)

    summary = {
        "query": query,
        "total_papers_found": len(papers_found),
        "total_papers_processed": len(processed_papers),
        "success_rate": (
            len(processed_papers) / len(papers_found) if papers_found else 0
        ),
        "total_download_size": sum(p["file_size_bytes"] for p in processed_papers),
        "papers": [],
    }

    for paper in processed_papers:
        summary["papers"].append(
            {
                "doi": paper["doi"],
                "title": paper["metadata"].get("title", "Unknown"),
                "html_file": paper["html_file"],
                "pdf_url": paper["pdf_url"],
                "file_size": paper["file_size_bytes"],
            }
        )

    # Save summary
    summary_file = Path("biorxiv_workflow_output", "workflow_summary.json")
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"✅ Summary saved to: {summary_file}")
    print(f"   Papers found: {summary['total_papers_found']}")
    print(f"   Papers processed: {summary['total_papers_processed']}")
    print(f"   Success rate: {summary['success_rate']:.1%}")
    print(f"   Total download size: {summary['total_download_size']:,} bytes")

    # Step 5: Demonstrate batch processing
    print("\n⚡ STEP 5: Batch processing demonstration")
    print("-" * 40)

    print("Running batch download for demonstration...")
    batch_results = scraper.batch_download_papers(
        "climate change", max_papers=2, results_per_page=10
    )

    print(
        f"   Batch completed: {batch_results['summary']['total_papers_downloaded']} papers"
    )
    print(f"   Errors: {batch_results['summary']['total_errors']}")
    print(f"   Success rate: {batch_results['summary']['success_rate']:.1%}")

    return summary


def demonstrate_cursor_reset():
    """Demonstrate cursor reset functionality."""
    print("\n🔄 Cursor Reset Demonstration")
    print("-" * 40)

    scraper = BioRxivAdvancedScraper(output_dir="biorxiv_cursor_test", delay=0.5)

    query = "climate change"

    # First search
    print(f"First search for '{query}':")
    first_papers = []
    for paper_data in scraper.search_with_pagination(query, max_papers=3, start_page=0):
        first_papers.append(paper_data["paper"]["doi"])
        print(f"   {paper_data['paper']['doi']}")

    # Reset cursor (start from beginning)
    print("\nResetting cursor and searching again:")
    second_papers = []
    for paper_data in scraper.search_with_pagination(query, max_papers=3, start_page=0):
        second_papers.append(paper_data["paper"]["doi"])
        print(f"   {paper_data['paper']['doi']}")

    # Verify consistency
    if first_papers == second_papers:
        print("✅ Cursor reset working: same results on repeated searches")
    else:
        print("⚠️  Cursor reset issue: different results on repeated searches")

    return first_papers == second_papers


def main():
    """Run the complete workflow demonstration."""
    print("🧪 BioRxiv Complete Workflow Test")
    print("=" * 60)

    try:
        # Run main workflow
        summary = demonstrate_full_workflow()

        # Test cursor reset
        cursor_working = demonstrate_cursor_reset()

        print("\n" + "=" * 60)
        print("🎉 WORKFLOW DEMONSTRATION COMPLETED!")
        print("=" * 60)

        print("✅ Main workflow: SUCCESS")
        print(f"✅ Cursor reset: {'SUCCESS' if cursor_working else 'ISSUE'}")

        print("\n📁 Output directories created:")
        print("   - biorxiv_workflow_output/ (main workflow)")
        print("   - biorxiv_cursor_test/ (cursor test)")

        print("\n📊 Final summary:")
        print(f"   - Papers processed: {summary['total_papers_processed']}")
        print(f"   - Success rate: {summary['success_rate']:.1%}")
        print(f"   - Total size: {summary['total_download_size']:,} bytes")

    except Exception as e:
        print(f"❌ Workflow demonstration failed: {e}")
        logger.exception("Workflow error")


if __name__ == "__main__":
    main()
