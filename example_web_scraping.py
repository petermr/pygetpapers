#!/usr/bin/env python3
"""
Example script demonstrating the Generic Web Scraping Framework

This script shows how to use the web scraping framework to search for papers
from bioRxiv and other repositories using configuration-based scraping.
"""

import logging
import sys
from pathlib import Path

# Add the pygetpapers directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from pygetpapers.web_scraping import (
    GenericWebScraper,
    ScrapingConfigParser,
    WebScrapingRepositoryManager,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def main():
    """Main function demonstrating web scraping capabilities."""

    print("=" * 60)
    print("Pygetpapers Generic Web Scraping Framework Demo")
    print("=" * 60)

    # Initialize the repository manager
    print("\n1. Initializing repository manager...")
    manager = WebScrapingRepositoryManager()

    # List available repositories
    print("\n2. Available repositories:")
    repositories = manager.list_repositories()
    for repo_name in repositories:
        info = manager.get_repository_info(repo_name)
        if info:
            status = "✅ Enabled" if info["enabled"] else "❌ Disabled"
            print(f"   - {repo_name}: {info['name']} ({status})")

    if not repositories:
        print("   No repositories found. Please check your configuration file.")
        return

    # Example search
    query = "urban heat island"
    print(f"\n3. Searching for: '{query}'")

    try:
        # Search all repositories
        results = manager.search_all_repositories(
            query=query,
            max_results=10,  # Limit to 10 results per repository
            output_dir="./web_scraping_output",
        )

        print(f"\n4. Search completed!")
        print(f"   - Repositories searched: {len(results['repositories_searched'])}")
        print(f"   - Total papers found: {results['total_papers']}")
        print(f"   - Errors encountered: {len(results['errors'])}")

        # Show results by repository
        print(f"\n5. Results by repository:")
        for repo_name, repo_results in results["papers_by_repository"].items():
            papers = repo_results["papers"]
            print(f"   - {repo_name}: {len(papers)} papers")

            # Show first few papers
            for i, paper in enumerate(papers[:3]):
                title = paper.get("title", "No title")[:60]
                authors = paper.get("authors", "No authors")[:40]
                print(f"     {i+1}. {title}...")
                print(f"        Authors: {authors}...")

        # Show any errors
        if results["errors"]:
            print(f"\n6. Errors encountered:")
            for error in results["errors"]:
                print(f"   - {error}")

        print(f"\n7. Output saved to: ./web_scraping_output/")

    except Exception as e:
        logger.error(f"Error during search: {e}")
        print(f"Error: {e}")


def demo_single_repository():
    """Demonstrate searching a single repository."""

    print("\n" + "=" * 60)
    print("Single Repository Demo")
    print("=" * 60)

    # Initialize scraper
    scraper = GenericWebScraper()

    # List available repositories
    repos = scraper.list_available_repositories()
    print(f"\nAvailable repositories: {repos}")

    if "biorxiv_web" in repos:
        print(f"\nSearching bioRxiv for 'climate change'...")

        try:
            results = scraper.search_papers(
                repo_name="biorxiv_web", query="climate change", max_results=5
            )

            print(f"Found {len(results['papers'])} papers")

            for i, paper in enumerate(results["papers"]):
                title = paper.get("title", "No title")
                authors = paper.get("authors", "No authors")
                doi = paper.get("doi", "No DOI")

                print(f"\n{i+1}. {title}")
                print(f"   Authors: {authors}")
                print(f"   DOI: {doi}")

        except Exception as e:
            print(f"Error: {e}")


def demo_configuration():
    """Demonstrate configuration management."""

    print("\n" + "=" * 60)
    print("Configuration Demo")
    print("=" * 60)

    config_parser = ScrapingConfigParser()

    # Show available repositories
    repos = config_parser.get_available_repositories()
    print(f"\nAvailable repositories: {repos}")

    # Validate configurations
    print(f"\nValidating configurations...")
    for repo_name in repos:
        errors = config_parser.validate_config(
            config_parser.load_repository_config(repo_name) or {}
        )
        if errors:
            print(f"❌ {repo_name}: {len(errors)} errors")
            for error in errors[:2]:  # Show first 2 errors
                print(f"   - {error}")
        else:
            print(f"✅ {repo_name}: Valid configuration")


if __name__ == "__main__":
    try:
        # Run main demo
        main()

        # Run additional demos
        demo_single_repository()
        demo_configuration()

        print("\n" + "=" * 60)
        print("Demo completed successfully!")
        print("=" * 60)

    except KeyboardInterrupt:
        print("\nDemo interrupted by user.")
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"Demo failed: {e}")
        sys.exit(1)
