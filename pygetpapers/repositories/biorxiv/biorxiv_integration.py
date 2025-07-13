#!/usr/bin/env python3
"""
BioRxiv Integration with pygetpapers Framework

This module demonstrates how the bioRxiv web scraper can be integrated
with the existing pygetpapers framework to provide text-based search
capabilities alongside the existing API-based date-only search.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from pygetpapers.repositories.biorxiv.biorxiv_advanced_scraper import BioRxivAdvancedScraper

logger = logging.getLogger(__name__)


class BioRxivIntegration:
    """
    Integration class for bioRxiv scraper with pygetpapers framework.

    This class provides a unified interface for bioRxiv data collection
    that can be used alongside other pygetpapers data sources.
    """

    def __init__(self, output_dir: str = "biorxiv_integration_output"):
        """
        Initialize the bioRxiv integration.

        Args:
            output_dir: Output directory for bioRxiv data
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize the scraper
        self.scraper = BioRxivAdvancedScraper(
            output_dir=str(self.output_dir), delay=1.0
        )

        # Create metadata file
        self.metadata_file = self.output_dir / "biorxiv_metadata.json"
        self.papers_metadata = []

    def search_and_collect(
        self,
        query: str,
        max_papers: int = 50,
        results_per_page: int = 25,
        save_metadata: bool = True,
    ) -> Dict[str, Any]:
        """
        Search and collect bioRxiv papers with metadata tracking.

        Args:
            query: Search query
            max_papers: Maximum number of papers to collect
            results_per_page: Results per page
            save_metadata: Whether to save metadata to file

        Returns:
            Collection summary
        """
        logger.info(f"Starting bioRxiv collection for query: {query}")

        collection_summary = {
            "query": query,
            "max_papers": max_papers,
            "start_time": None,
            "end_time": None,
            "papers_collected": 0,
            "papers_downloaded": 0,
            "errors": [],
            "papers": [],
        }

        try:
            collection_summary["start_time"] = self.scraper.session.get(
                "https://www.biorxiv.org", timeout=5
            ).elapsed.total_seconds()

            # Collect papers
            papers_found = []
            for paper_data in self.scraper.search_with_pagination(
                query, max_papers, results_per_page
            ):
                paper = paper_data["paper"]
                papers_found.append(paper)
                collection_summary["papers_collected"] += 1

                # Download full content
                doi = paper["doi"]
                download_result = self.scraper.download_paper_full_content(doi)

                if "error" not in download_result:
                    collection_summary["papers_downloaded"] += 1

                    # Add to metadata
                    paper_metadata = {
                        "doi": doi,
                        "title": paper["title"],
                        "authors": paper["authors"],
                        "biorxiv_id": paper.get("biorxiv_id"),
                        "landing_file": download_result["landing_file"],
                        "fulltext_file": download_result["fulltext_file"],
                        "pdf_url": download_result["pdf_url"],
                        "fulltext_url": download_result["fulltext_url"],
                        "landing_size": download_result["landing_size_bytes"],
                        "fulltext_size": download_result["fulltext_size_bytes"],
                        "download_timestamp": download_result["download_timestamp"],
                        "search_query": query,
                    }

                    collection_summary["papers"].append(paper_metadata)
                    self.papers_metadata.append(paper_metadata)
                else:
                    collection_summary["errors"].append(
                        {"doi": doi, "error": download_result["error"]}
                    )

            collection_summary["end_time"] = self.scraper.session.get(
                "https://www.biorxiv.org", timeout=5
            ).elapsed.total_seconds()

            # Save metadata if requested
            if save_metadata:
                self.save_metadata()

            logger.info(
                f"Collection completed: {collection_summary['papers_downloaded']} papers downloaded"
            )

        except Exception as e:
            logger.error(f"Collection error: {e}")
            collection_summary["errors"].append(
                {"type": "collection_error", "error": str(e)}
            )

        return collection_summary

    def save_metadata(self) -> str:
        """
        Save collected metadata to file.

        Returns:
            Path to saved metadata file
        """
        metadata = {
            "total_papers": len(self.papers_metadata),
            "collection_timestamp": self.scraper.session.get(
                "https://www.biorxiv.org", timeout=5
            ).elapsed.total_seconds(),
            "papers": self.papers_metadata,
        }

        with open(self.metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        logger.info(f"Metadata saved to: {self.metadata_file}")
        return str(self.metadata_file)

    def get_paper_info(self, doi: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific paper.

        Args:
            doi: DOI of the paper

        Returns:
            Paper information or None if not found
        """
        for paper in self.papers_metadata:
            if paper["doi"] == doi:
                return paper
        return None

    def list_papers(self) -> List[Dict[str, Any]]:
        """
        List all collected papers.

        Returns:
            List of paper metadata
        """
        return self.papers_metadata.copy()

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get collection statistics.

        Returns:
            Statistics dictionary
        """
        if not self.papers_metadata:
            return {"total_papers": 0, "total_size": 0, "unique_queries": 0}

        total_landing_size = sum(p.get("landing_size", 0) for p in self.papers_metadata)
        total_fulltext_size = sum(
            p.get("fulltext_size", 0) for p in self.papers_metadata
        )
        total_size = total_landing_size + total_fulltext_size
        unique_queries = len(set(p["search_query"] for p in self.papers_metadata))

        return {
            "total_papers": len(self.papers_metadata),
            "total_size": total_size,
            "total_landing_size": total_landing_size,
            "total_fulltext_size": total_fulltext_size,
            "unique_queries": unique_queries,
            "average_size": (
                total_size / len(self.papers_metadata) if self.papers_metadata else 0
            ),
        }

    def export_to_csv(self, output_file: Optional[str] = None) -> str:
        """
        Export paper metadata to CSV format.

        Args:
            output_file: Output CSV file path

        Returns:
            Path to exported CSV file
        """
        if not output_file:
            output_file = self.output_dir / "biorxiv_papers.csv"

        import csv

        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
            if not self.papers_metadata:
                return str(output_file)

            fieldnames = self.papers_metadata[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for paper in self.papers_metadata:
                writer.writerow(paper)

        logger.info(f"CSV exported to: {output_file}")
        return str(output_file)


def demonstrate_integration():
    """Demonstrate the bioRxiv integration capabilities."""
    print("🔗 BioRxiv Integration Demonstration")
    print("=" * 50)

    # Initialize integration
    integration = BioRxivIntegration()

    # Example queries
    queries = ["urban heat island", "climate change adaptation"]

    total_summary = {"queries": [], "total_papers": 0, "total_errors": 0}

    for query in queries:
        print(f"\n📋 Processing query: '{query}'")

        # Collect papers
        summary = integration.search_and_collect(
            query, max_papers=3, results_per_page=10
        )

        total_summary["queries"].append(summary)
        total_summary["total_papers"] += summary["papers_downloaded"]
        total_summary["total_errors"] += len(summary["errors"])

        print(f"   Papers collected: {summary['papers_collected']}")
        print(f"   Papers downloaded: {summary['papers_downloaded']}")
        print(f"   Errors: {len(summary['errors'])}")

    # Show statistics
    print("\n📊 Integration Statistics:")
    stats = integration.get_statistics()
    print(f"   Total papers: {stats['total_papers']}")
    print(f"   Total size: {stats['total_size']:,} bytes")
    print(f"   Landing pages: {stats['total_landing_size']:,} bytes")
    print(f"   Full text: {stats['total_fulltext_size']:,} bytes")
    print(f"   Unique queries: {stats['unique_queries']}")
    print(f"   Average paper size: {stats['average_size']:,.0f} bytes")

    # List papers
    print("\n📄 Collected Papers:")
    papers = integration.list_papers()
    for i, paper in enumerate(papers, 1):
        print(f"   {i}. {paper['title'][:60]}...")
        print(f"      DOI: {paper['doi']}")
        print(f"      Landing: {paper.get('landing_size', 0):,} bytes")
        print(f"      Fulltext: {paper.get('fulltext_size', 0):,} bytes")
        if paper.get("fulltext_file"):
            print(f"      ✅ Full text available")
        else:
            print(f"      ❌ Full text not available")

    # Export to CSV
    csv_file = integration.export_to_csv()
    print(f"\n📤 CSV exported to: {csv_file}")

    # Save metadata
    metadata_file = integration.save_metadata()
    print(f"📋 Metadata saved to: {metadata_file}")

    return total_summary


def compare_with_api_search():
    """
    Demonstrate how bioRxiv web scraper complements API-based search.

    The bioRxiv API only supports date-based searches, while the web scraper
    supports text-based searches, making them complementary.
    """
    print("\n🔄 Comparison: Web Scraper vs API Search")
    print("=" * 50)

    print("BioRxiv API Limitations:")
    print("   ❌ Only supports date-based searches")
    print("   ❌ No text query support")
    print("   ❌ Limited metadata")

    print("\nBioRxiv Web Scraper Advantages:")
    print("   ✅ Full text search support")
    print("   ✅ Rich metadata extraction")
    print("   ✅ HTML content download")
    print("   ✅ PDF link extraction")
    print("   ✅ Pagination support")

    print("\nIntegration Benefits:")
    print("   🔗 Can be used alongside existing pygetpapers API calls")
    print("   🔗 Provides text-based search for bioRxiv")
    print("   🔗 Maintains consistent data format")
    print("   🔗 Supports batch processing")


def main():
    """Run the integration demonstration."""
    print("🧪 BioRxiv Integration with pygetpapers")
    print("=" * 60)

    try:
        # Run integration demonstration
        summary = demonstrate_integration()

        # Show comparison
        compare_with_api_search()

        print("\n" + "=" * 60)
        print("🎉 INTEGRATION DEMONSTRATION COMPLETED!")
        print("=" * 60)

        print(f"✅ Total papers collected: {summary['total_papers']}")
        print(f"✅ Total errors: {summary['total_errors']}")
        print(f"✅ Queries processed: {len(summary['queries'])}")

        print("\n📁 Output directory: biorxiv_integration_output/")
        print("📄 Files created:")
        print("   - biorxiv_metadata.json (metadata)")
        print("   - biorxiv_papers.csv (CSV export)")
        print("   - Individual paper directories")

    except Exception as e:
        print(f"❌ Integration demonstration failed: {e}")
        logger.exception("Integration error")


if __name__ == "__main__":
    main()
