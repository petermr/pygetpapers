#!/usr/bin/env python3
"""
Test script to check for XML links in Redalyc articles.
"""

import logging
import re
import sys
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from test_utils import skip_if_redalyc_down, test_redalyc_connectivity

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@skip_if_redalyc_down()
def test_redalyc_links():
    """Test what links we can find in Redalyc articles."""

    # Test with a known Redalyc article
    test_urls = [
        "https://www.redalyc.org/articulo.oa?id=14075366011",
        "https://www.redalyc.org/articulo.oa?id=41375362006",
        "https://www.redalyc.org/articulo.oa?id=123075329002",
    ]

    headers = {
        "User-Agent": "pygetpapers/2.0 (https://github.com/pygetpapers/pygetpapers)"
    }

    for url in test_urls:
        print(f"\n{'='*60}")
        print(f"Testing URL: {url}")
        print(f"{'='*60}")

        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Find all links
            all_links = soup.find_all("a", href=True)

            print(f"Total links found: {len(all_links)}")

            # Categorize links
            pdf_links = []
            xml_links = []
            download_links = []
            other_links = []

            for link in all_links:
                href = link.get("href", "").lower()
                link_text = link.get_text(strip=True).lower()
                full_href = link.get("href", "")

                # Check for PDF links
                if "pdf" in href or "pdf" in link_text:
                    pdf_links.append(
                        {
                            "href": full_href,
                            "text": link.get_text(strip=True),
                            "title": link.get("title", ""),
                        }
                    )

                # Check for XML links
                elif "xml" in href or "xml" in link_text:
                    xml_links.append(
                        {
                            "href": full_href,
                            "text": link.get_text(strip=True),
                            "title": link.get("title", ""),
                        }
                    )

                # Check for download links
                elif any(
                    keyword in href
                    for keyword in ["download", "descargar", "articulo.oa"]
                ):
                    download_links.append(
                        {
                            "href": full_href,
                            "text": link.get_text(strip=True),
                            "title": link.get("title", ""),
                        }
                    )

                # Other interesting links
                elif any(
                    keyword in href for keyword in ["epub", "mobi", "txt", "doc", "rtf"]
                ):
                    other_links.append(
                        {
                            "href": full_href,
                            "text": link.get_text(strip=True),
                            "title": link.get("title", ""),
                        }
                    )

            # Print results
            print(f"\nPDF Links ({len(pdf_links)}):")
            for link in pdf_links:
                print(f"  - {link['href']} (text: '{link['text']}')")

            print(f"\nXML Links ({len(xml_links)}):")
            for link in xml_links:
                print(f"  - {link['href']} (text: '{link['text']}')")

            print(f"\nDownload Links ({len(download_links)}):")
            for link in download_links:
                print(f"  - {link['href']} (text: '{link['text']}')")

            print(f"\nOther Format Links ({len(other_links)}):")
            for link in other_links:
                print(f"  - {link['href']} (text: '{link['text']}')")

            # Check for any XML-related content in the page
            print(f"\nChecking for XML-related content in page source...")
            page_text = response.text.lower()

            xml_indicators = [
                "xml",
                "jats",
                "nlm",
                "article-xml",
                "fulltext-xml",
                "download xml",
                "descargar xml",
                "xml format",
            ]

            found_indicators = []
            for indicator in xml_indicators:
                if indicator in page_text:
                    found_indicators.append(indicator)

            if found_indicators:
                print(f"Found XML indicators: {found_indicators}")
            else:
                print("No XML indicators found in page source")

            # Check for any API endpoints or data URLs
            print(f"\nChecking for potential API/data URLs...")
            api_patterns = [
                r'https?://[^"\s]+\.xml',
                r'https?://[^"\s]+/xml[^"\s]*',
                r'https?://[^"\s]+/api[^"\s]*',
                r'https?://[^"\s]+/data[^"\s]*',
            ]

            for pattern in api_patterns:
                matches = re.findall(pattern, response.text)
                if matches:
                    print(f"Found potential API/data URLs with pattern '{pattern}':")
                    for match in matches:
                        print(f"  - {match}")

        except Exception as e:
            assert False, f"Error testing {url}: {e}"


@skip_if_redalyc_down()
@skip_if_redalyc_down()
def test_redalyc_api_endpoints():
    """Test if Redalyc has any API endpoints that might provide XML."""

    print(f"\n{'='*60}")
    print("Testing potential Redalyc API endpoints")
    print(f"{'='*60}")

    # Common API endpoint patterns
    api_endpoints = [
        "https://www.redalyc.org/api/",
        "https://api.redalyc.org/",
        "https://www.redalyc.org/ws/",
        "https://www.redalyc.org/rest/",
        "https://www.redalyc.org/data/",
    ]

    headers = {
        "User-Agent": "pygetpapers/2.0 (https://github.com/pygetpapers/pygetpapers)"
    }

    successful_endpoints = []
    failed_endpoints = []

    for endpoint in api_endpoints:
        try:
            response = requests.get(endpoint, headers=headers, timeout=10)
            print(f"{endpoint}: {response.status_code}")
            if response.status_code == 200:
                print(
                    f"  Content-Type: {response.headers.get('content-type', 'unknown')}"
                )
                print(f"  Content preview: {response.text[:200]}...")
                successful_endpoints.append(endpoint)
            else:
                failed_endpoints.append((endpoint, f"Status {response.status_code}"))
        except requests.exceptions.RequestException as e:
            # Network errors are acceptable - just log them
            print(f"{endpoint}: Network error - {type(e).__name__}")
            failed_endpoints.append((endpoint, str(e)))
        except Exception as e:
            # Other errors should still fail the test
            assert False, f"{endpoint}: Unexpected error - {e}"

    # Test passes if we can check endpoints (even if they all fail)
    # The important part is that we tried and didn't crash
    print(f"\n✅ Checked {len(api_endpoints)} endpoints")
    print(f"   Successful: {len(successful_endpoints)}")
    print(f"   Failed: {len(failed_endpoints)}")


def main():
    """Run the XML links tests."""
    print("🧪 Testing Redalyc XML Links")
    print("=" * 50)

    # Test connectivity first
    print("🔍 Testing Redalyc connectivity...")
    is_connected, error_msg = test_redalyc_connectivity()

    if not is_connected:
        import pytest
        pytest.skip(f"Redalyc appears to be down: {error_msg}")

    print("✅ Redalyc is accessible, running XML links tests...")

    try:
        test_redalyc_links()
        test_redalyc_api_endpoints()
        print("🎉 XML links tests completed!")
    except Exception as e:
        assert False, f"Test failed: {e}"


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
