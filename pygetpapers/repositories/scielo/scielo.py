"""
SciELO repository implementation for web scraping.

SciELO is a multilingual scientific repository focused on Latin America,
Spain, Portugal, and South Africa. This implementation uses web scraping
since SciELO doesn't provide a public REST API.
"""

import logging
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from pygetpapers.core.download_tools import DownloadTools
from pygetpapers.core.file_utils import FileUtils
from pygetpapers.core.repositoryinterface import RepositoryInterface


class SciELO(RepositoryInterface):
    """SciELO repository implementation using web scraping."""

    def __init__(self):
        """Initialize SciELO repository."""
        super().__init__()
        self.download_tools = DownloadTools("scielo")
        self.base_url = "https://scielo.org"
        self.search_url = "https://search.scielo.org"
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                ),
                "Accept": (
                    "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
                ),
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }
        )

        # Rate limiting
        self.request_delay = 2.0  # seconds between requests
        self.last_request_time = 0

    def _rate_limit(self):
        """Implement rate limiting to be respectful to SciELO's servers."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.request_delay:
            time.sleep(self.request_delay - time_since_last)
        self.last_request_time = time.time()

    def _make_request(
        self, url: str, params: Optional[Dict] = None
    ) -> Optional[requests.Response]:
        """Make a rate-limited request to SciELO with proper encoding detection."""
        self._rate_limit()
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            # Detect encoding properly
            if response.encoding is None or response.encoding.lower() == 'iso-8859-1':
                # Try to detect encoding from content
                import chardet
                detected = chardet.detect(response.content)
                if detected and detected['confidence'] > 0.7:
                    detected_encoding = detected['encoding']
                    logging.info(f"Detected encoding: {detected_encoding} (confidence: {detected['confidence']:.2f})")
                    response.encoding = detected_encoding
                else:
                    logging.warning(f"Could not reliably detect encoding for {url}. Detected: {detected}")
                    # Don't guess - alert user
                    print(f"⚠️  ENCODING WARNING: Could not detect encoding for {url}")
                    print(f"   Detected: {detected}")
                    print(f"   Response headers: {dict(response.headers)}")
                    print(f"   Please check if this is acceptable or specify encoding manually.")
                    # For now, use UTF-8 but log the issue
                    response.encoding = 'utf-8'
            
            # Validate that text extraction works
            try:
                test_text = response.text[:100]  # Test first 100 characters
                if not test_text or test_text.strip() == '':
                    logging.warning(f"Response text appears empty for {url}")
            except UnicodeDecodeError as e:
                logging.error(f"Unicode decode error for {url}: {e}")
                print(f"❌ ENCODING ERROR: Failed to decode response from {url}")
                print(f"   Error: {e}")
                print(f"   Please specify correct encoding manually.")
                return None
                
            return response
        except requests.RequestException as e:
            logging.error(f"Request failed for {url}: {e}")
            return None

    def _extract_article_links(self, html_content: str) -> List[str]:
        """Extract article links from search results page."""
        soup = BeautifulSoup(html_content, "html.parser")
        article_links = []

        # Look for article links - SciELO specific patterns
        link_selectors = [
            'a[href*="/scielo.php?script=sci_arttext"]',
            'a[href*="script=sci_arttext"]',
            'a[target="_blank"]',
        ]

        for selector in link_selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get("href")
                if href:
                    # Clean up the URL
                    if href.startswith("//"):
                        href = "https:" + href
                    elif href.startswith("/"):
                        href = urljoin(self.search_url, href)
                    elif not href.startswith("http"):
                        href = urljoin(self.search_url, href)
                    
                    # Only include article links (not PDF or other links)
                    if "script=sci_arttext" in href and href not in article_links:
                        article_links.append(href)

        return article_links

    def _extract_article_metadata(
        self, html_content: str, article_url: str
    ) -> Dict[str, Any]:
        """Extract metadata from an article page."""
        soup = BeautifulSoup(html_content, "html.parser")
        
        metadata = {
            "url": article_url,
            "title": None,
            "authors": [],
            "abstract": None,
            "journal": None,
            "year": None,
            "doi": None,
            "language": None,
            "keywords": [],
            "volume": None,
            "issue": None,
            "pages": None,
            "pdf_urls": [],
            "collection": None
        }

        # Extract title
        title_selectors = [
            'h1.title',
            '.title',
            'h1',
            '.article-title',
            'title',
            '.documentTitle',
            '[class*="title"]'
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title_text = title_elem.get_text(strip=True)
                if title_text and len(title_text) > 5:
                    metadata["title"] = title_text
                    break

        # Extract authors
        author_selectors = [
            '.authors',
            '.author',
            '.byline',
            '[class*="author"]',
            '.contribGroup',
            '.contrib'
        ]
        
        for selector in author_selectors:
            author_elems = soup.select(selector)
            for elem in author_elems:
                author_text = elem.get_text(strip=True)
                if author_text and len(author_text) > 2 and author_text not in metadata["authors"]:
                    # Clean up author text (remove ORCID links, etc.)
                    clean_author = re.sub(r'http://orcid\.org/\d{4}-\d{4}-\d{4}-\d{3}[0-9X]', '', author_text)
                    clean_author = re.sub(r'\d+', '', clean_author)  # Remove numbers
                    clean_author = clean_author.strip()
                    if clean_author and len(clean_author) > 2:
                        metadata["authors"].append(clean_author)

        # Extract abstract
        abstract_selectors = [
            '.abstract',
            '.resumo',
            '.summary',
            '[class*="abstract"]',
            '.abstractIn',
            '.abstractContent'
        ]
        
        for selector in abstract_selectors:
            abstract_elem = soup.select_one(selector)
            if abstract_elem:
                metadata["abstract"] = abstract_elem.get_text(strip=True)
                break

        # Extract journal
        journal_selectors = [
            '.journal',
            '.periodical',
            '.publication',
            '[class*="journal"]',
            '.journalTitle',
            '.source'
        ]
        
        for selector in journal_selectors:
            journal_elem = soup.select_one(selector)
            if journal_elem:
                metadata["journal"] = journal_elem.get_text(strip=True)
                break

        # Extract DOI
        doi_selectors = [
            '[class*="doi"]',
            '.doi',
            'a[href*="doi.org"]',
            '[id*="doi"]'
        ]
        
        for selector in doi_selectors:
            doi_elem = soup.select_one(selector)
            if doi_elem:
                doi_text = doi_elem.get_text(strip=True)
                if 'doi' in doi_text.lower():
                    metadata["doi"] = doi_text
                    break

        # Extract keywords
        keyword_selectors = [
            '.keywords',
            '.keyWords',
            '[class*="keyword"]',
            '.subject',
            '.descriptors'
        ]
        
        for selector in keyword_selectors:
            keyword_elems = soup.select(selector)
            for elem in keyword_elems:
                keyword_text = elem.get_text(strip=True)
                if keyword_text and len(keyword_text) > 2:
                    metadata["keywords"].append(keyword_text)

        # Extract PDF URLs
        pdf_selectors = [
            'a[href*=".pdf"]',
            'a[href*="/pdf/"]',
            'a[href*="script=sci_pdf"]',
            '.pdf-link a',
            'a[title*="PDF"]',
            'a[href*="format=pdf"]'
        ]
        
        for selector in pdf_selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get("href")
                if href:
                    if not href.startswith("http"):
                        parsed_url = urlparse(article_url)
                        href = f"{parsed_url.scheme}://{parsed_url.netloc}{href}"
                    if href not in metadata["pdf_urls"]:
                        metadata["pdf_urls"].append(href)

        # Extract collection from URL
        parsed_url = urlparse(article_url)
        if parsed_url.netloc:
            metadata["collection"] = parsed_url.netloc

        return metadata

    def search_articles(
        self, query: str, max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for articles on SciELO.

        Args:
            query: Search query string
            max_results: Maximum number of results to return

        Returns:
            List of article metadata dictionaries
        """
        logging.info(f"Searching SciELO for: {query}")

        # Build search parameters
        search_params = {
            "q": query,
            "lang": "en",  # Prefer English
            "count": min(max_results, 20),  # SciELO limit
            "from": 0,
            "output": "site",
            "sort": "",
            "format": "summary"
        }

        response = self._make_request(self.search_url, search_params)
        if not response:
            logging.error("Failed to get search results from SciELO")
            return []

        # Extract article links from search results
        article_links = self._extract_article_links(response.text)
        logging.info(f"Found {len(article_links)} article links from search")

        # Limit results
        article_links = article_links[:max_results]

        # Extract metadata for each article
        articles = []
        for link in article_links:
            article_response = self._make_request(link)
            if article_response:
                metadata = self._extract_article_metadata(article_response.text, link)
                articles.append(metadata)
                logging.info(
                    f"Extracted metadata for: {metadata.get('title', 'Unknown title')}"
                )

        return articles

    def download_article(self, article_url: str, output_dir: str) -> bool:
        """
        Download a single article and its associated files.

        Args:
            article_url: URL of the article to download
            output_dir: Directory to save the downloaded files

        Returns:
            True if download was successful, False otherwise
        """
        logging.info(f"Downloading article: {article_url}")

        # Get article page
        response = self._make_request(article_url)
        if not response:
            return False

        # Extract metadata
        metadata = self._extract_article_metadata(response.text, article_url)

        # Use custom SciELO article ID generation following style guide
        article_id = self._generate_scielo_article_id(metadata, article_url)
        article_dir = Path(output_dir) / article_id
        article_dir.mkdir(parents=True, exist_ok=True)

        # Save HTML content
        html_file = article_dir / f"{article_id}.html"
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(response.text)

        # Save metadata
        metadata_file = article_dir / f"{article_id}_metadata.json"
        with open(metadata_file, "w", encoding="utf-8") as f:
            import json
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        # Download PDFs if available
        for i, pdf_url in enumerate(metadata.get("pdf_urls", [])):
            try:
                pdf_response = self._make_request(pdf_url)
                if pdf_response and pdf_response.headers.get("content-type", "").startswith("application/pdf"):
                    pdf_file = article_dir / f"{article_id}_pdf_{i+1}.pdf"
                    with open(pdf_file, "wb") as f:
                        f.write(pdf_response.content)
                    logging.info(f"Downloaded PDF: {pdf_file}")
            except Exception as e:
                logging.warning(f"Failed to download PDF {pdf_url}: {e}")

        logging.info(f"Article downloaded to: {article_dir}")
        return True

    def scielo(
        self,
        query: str,
        cutoff_size: int,
        filter_dict: Optional[Dict] = None,
        update: Optional[Dict] = None,
        makecsv: bool = False,
        makexml: bool = False,
        makehtml: bool = False,
        makedatatables: bool = True,  # Default to True for DataTables
    ) -> Dict[str, Any]:
        """
        Main SciELO search and download method.

        Args:
            query: Search query
            cutoff_size: Maximum number of results
            filter_dict: Optional filters
            update: Optional update parameters
            makecsv: Generate CSV output
            makexml: Generate XML output
            makehtml: Generate HTML output
            makedatatables: Generate DataTables HTML output

        Returns:
            Dictionary with search results and metadata
        """
        logging.info(f"Starting SciELO search for: {query}")

        # Search for articles
        articles = self.search_articles(query, cutoff_size)

        # Prepare results
        results = {
            "query": query,
            "total_results": len(articles),
            "articles": articles,
            "search_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "repository": "scielo"
        }

        # Create output directory in temp/ as per style guide
        output_dir = Path("temp") / "scielo_results"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Download articles for file links to work
        print(f"📥 Downloading {len(articles)} articles...")
        for i, article in enumerate(articles, 1):
            article_url = article.get("url")
            if article_url:
                print(f"   [{i}/{len(articles)}] Downloading: {article.get('title', 'Unknown')[:50]}...")
                self.download_article(article_url, output_dir)
            else:
                print(f"   [{i}/{len(articles)}] Skipping: No URL available")

        # Generate outputs if requested
        if makecsv:
            self._generate_csv_output(results, output_dir / "scielo_results")
        
        if makexml:
            self._generate_xml_output(results, output_dir / "scielo_results")
        
        if makehtml:
            self._generate_html_output(results, output_dir / "scielo_results")
        
        if makedatatables:
            self._generate_datatables_output(results, "results")

        logging.info(f"SciELO search completed. Found {len(articles)} articles.")
        print(f"✅ SciELO search completed successfully!")
        print(f"   📊 Found {len(articles)} articles")
        print(f"   📁 Output directory: {output_dir}")
        if makedatatables:
            print(f"   🎯 DataTables: {output_dir}/scielo_results/datatables.html")
        
        return results

    def _generate_csv_output(self, results: Dict[str, Any], base_filename: Path) -> None:
        """Generate CSV output from search results."""
        import csv
        
        csv_file = base_filename.with_suffix('.csv')
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            if results["articles"]:
                fieldnames = results["articles"][0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for article in results["articles"]:
                    writer.writerow(article)
        
        logging.info(f"CSV output saved to: {csv_file}")

    def _generate_xml_output(self, results: Dict[str, Any], base_filename: Path) -> None:
        """Generate XML output from search results."""
        import xml.etree.ElementTree as ET
        
        root = ET.Element("scielo_results")
        root.set("query", results["query"])
        root.set("total_results", str(results["total_results"]))
        root.set("search_date", results["search_date"])
        
        for article in results["articles"]:
            article_elem = ET.SubElement(root, "article")
            for key, value in article.items():
                if isinstance(value, list):
                    for item in value:
                        item_elem = ET.SubElement(article_elem, key)
                        item_elem.text = str(item)
                else:
                    elem = ET.SubElement(article_elem, key)
                    elem.text = str(value) if value else ""
        
        tree = ET.ElementTree(root)
        xml_file = base_filename.with_suffix('.xml')
        tree.write(xml_file, encoding="utf-8", xml_declaration=True)
        
        logging.info(f"XML output saved to: {xml_file}")

    def _generate_html_output(self, results: Dict[str, Any], base_filename: Path) -> None:
        """Generate HTML output from search results."""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>SciELO Search Results: {results['query']}</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .article {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; }}
        .title {{ font-size: 18px; font-weight: bold; color: #333; }}
        .authors {{ color: #666; margin: 5px 0; }}
        .abstract {{ margin: 10px 0; }}
        .metadata {{ font-size: 12px; color: #888; }}
    </style>
</head>
<body>
    <h1>SciELO Search Results</h1>
    <p><strong>Query:</strong> {results['query']}</p>
    <p><strong>Total Results:</strong> {results['total_results']}</p>
    <p><strong>Search Date:</strong> {results['search_date']}</p>
    
    <div class="articles">
"""
        
        for article in results["articles"]:
            html_content += f"""
        <div class="article">
            <div class="title">{article.get('title', 'No title')}</div>
            <div class="authors">{', '.join(article.get('authors', []))}</div>
            <div class="abstract">{article.get('abstract', 'No abstract')}</div>
            <div class="metadata">
                <strong>Journal:</strong> {article.get('journal', 'Unknown')} | 
                <strong>DOI:</strong> {article.get('doi', 'None')} | 
                <strong>URL:</strong> <a href="{article.get('url', '#')}">{article.get('url', 'No URL')}</a>
            </div>
        </div>
"""
        
        html_content += """
    </div>
</body>
</html>
"""
        
        html_file = base_filename.with_suffix('.html')
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        logging.info(f"HTML output saved to: {html_file}")

    def _generate_datatables_output(self, results: Dict[str, Any], base_filename: str) -> None:
        """Generate DataTables HTML output from search results with proper file links."""
        # Create output directory in temp/ as per style guide
        output_dir = Path("temp") / f"scielo_{base_filename}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate DataTables HTML with proper file links
        datatables_html = self._create_scielo_datatables_html(results)
        
        # Save DataTables HTML
        datatables_file = output_dir / "datatables.html"
        with open(datatables_file, "w", encoding="utf-8") as f:
            f.write(datatables_html)
        
        # Create index file
        index_html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>SciELO Search Results - {results['query']}</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f5f5f5; padding: 20px; border-radius: 5px; }}
        .summary {{ margin: 20px 0; }}
        .datatables-link {{ 
            display: inline-block; 
            background-color: #007bff; 
            color: white; 
            padding: 10px 20px; 
            text-decoration: none; 
            border-radius: 5px; 
            margin: 10px 0;
        }}
        .datatables-link:hover {{ background-color: #0056b3; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>SciELO Search Results</h1>
        <div class="summary">
            <p><strong>Query:</strong> {results['query']}</p>
            <p><strong>Total Results:</strong> {results['total_results']}</p>
            <p><strong>Search Date:</strong> {results['search_date']}</p>
            <p><strong>Repository:</strong> SciELO</p>
        </div>
        <a href="datatables.html" class="datatables-link">View Interactive DataTable</a>
    </div>
    
    <h2>Search Summary</h2>
    <p>This search returned {results['total_results']} articles from SciELO.</p>
    <p>Click the link above to view the interactive DataTable with search, sort, and pagination features.</p>
    
    <h2>Files Generated</h2>
    <ul>
        <li><strong>datatables.html</strong> - Interactive DataTable with all results and file links</li>
        <li><strong>index.html</strong> - This summary page</li>
    </ul>
</body>
</html>
"""
        
        index_file = output_dir / "index.html"
        with open(index_file, "w", encoding="utf-8") as f:
            f.write(index_html)
        
        logging.info(f"DataTables output saved to: {output_dir}")
        print(f"✅ DataTables created successfully in: {output_dir}")

    def _create_scielo_datatables_html(self, results: Dict[str, Any]) -> str:
        """Create SciELO-specific DataTables HTML with proper file links."""
        
        # Prepare table rows with file links
        table_rows = []
        for article in results["articles"]:
            # Generate article ID for file paths
            article_id = self._generate_scielo_article_id(article, article.get("url", ""))
            
            # Create file links
            html_link = f'<a href="{article_id}/{article_id}.html" target="_blank" title="View HTML">📄 HTML</a>'
            metadata_link = f'<a href="{article_id}/{article_id}_metadata.json" target="_blank" title="View Metadata">📋 JSON</a>'
            
            # Create PDF links if available
            pdf_links = []
            for i, pdf_url in enumerate(article.get("pdf_urls", [])):
                pdf_filename = f"{article_id}_pdf_{i+1}.pdf"
                pdf_links.append(f'<a href="{article_id}/{pdf_filename}" target="_blank" title="Download PDF">📄 PDF{i+1}</a>')
            
            pdf_links_html = " | ".join(pdf_links) if pdf_links else "No PDF"
            
            # Create title link
            title_link = f'<a href="{article.get("url", "#")}" target="_blank">{article.get("title", "No title")}</a>'
            
            # Create table row
            row = f"""
        <tr>
            <td>{title_link}</td>
            <td>{", ".join(article.get("authors", []))}</td>
            <td>{article.get("abstract", "No abstract")[:100]}...</td>
            <td>{article.get("journal", "Unknown")}</td>
            <td>{article.get("doi", "No DOI")}</td>
            <td>{article.get("year", "")}</td>
            <td>{article.get("language", "")}</td>
            <td>{html_link} | {metadata_link}</td>
            <td>{pdf_links_html}</td>
        </tr>"""
            table_rows.append(row)
        
        # Create the full HTML
        datatables_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>SciELO Search Results - {results['query']}</title>
    <meta charset="utf-8">
    <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.13.7/css/jquery.dataTables.css">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1400px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .header h1 {{ color: #2c3e50; margin-bottom: 10px; }}
        .summary {{ background-color: #ecf0f1; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .summary p {{ margin: 5px 0; }}
        table {{ width: 100%; }}
        .dataTables_wrapper {{ margin-top: 20px; }}
        .footer {{ margin-top: 30px; text-align: center; color: #7f8c8d; font-size: 14px; }}
        /* Fixed column widths to prevent overlap */
        #scieloTable th:nth-child(1) {{ width: 20%; }} /* Title */
        #scieloTable th:nth-child(2) {{ width: 12%; }} /* Authors */
        #scieloTable th:nth-child(3) {{ width: 20%; }} /* Abstract */
        #scieloTable th:nth-child(4) {{ width: 10%; }} /* Journal */
        #scieloTable th:nth-child(5) {{ width: 8%; }}  /* DOI */
        #scieloTable th:nth-child(6) {{ width: 5%; }}  /* Year */
        #scieloTable th:nth-child(7) {{ width: 5%; }}  /* Language */
        #scieloTable th:nth-child(8) {{ width: 10%; }} /* HTML/JSON */
        #scieloTable th:nth-child(9) {{ width: 10%; }} /* PDFs */
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>SciELO Search Results</h1>
            <h2>{results['query']}</h2>
        </div>
        
        <div class="summary">
            <p><strong>Query:</strong> {results['query']}</p>
            <p><strong>Total Results:</strong> {results['total_results']} articles</p>
            <p><strong>Search Date:</strong> {results['search_date']}</p>
            <p><strong>Repository:</strong> SciELO (Multiple Regional Sites)</p>
            <p><strong>Note:</strong> All columns visible - file links point to downloaded content</p>
        </div>
        
        <table id="scieloTable" class="display" style="width:100%">
            <thead>
                <tr>
                    <th>Title</th>
                    <th>Authors</th>
                    <th>Abstract</th>
                    <th>Journal</th>
                    <th>DOI</th>
                    <th>Year</th>
                    <th>Language</th>
                    <th>Files</th>
                    <th>PDFs</th>
                </tr>
            </thead>
            <tbody>
                {''.join(table_rows)}
            </tbody>
        </table>
        
        <div class="footer">
            <p>Generated by pygetpapers SciELO Repository | Interactive DataTable with file links</p>
        </div>
    </div>
    
    <script type="text/javascript" src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
    <script type="text/javascript" src="https://cdn.datatables.net/1.13.7/js/jquery.dataTables.min.js"></script>
    <script>
        $(document).ready(function() {{
            $('#scieloTable').DataTable({{
                responsive: false,  // Disabled responsive to show all columns
                pageLength: 10,
                order: [[0, 'asc']],
                scrollX: true,      // Enable horizontal scrolling if needed
                language: {{
                    search: "Search articles:",
                    lengthMenu: "Show _MENU_ articles per page",
                    info: "Showing _START_ to _END_ of _TOTAL_ articles",
                    paginate: {{
                        first: "First",
                        last: "Last",
                        next: "Next",
                        previous: "Previous"
                    }}
                }}
            }});
        }});
    </script>
</body>
</html>"""
        
        return datatables_html

    def update(self, query_namespace: Dict[str, Any]) -> None:
        """Update from previous results."""
        logging.info("Update functionality not implemented for SciELO")

    def noexecute(self, query_namespace: Dict[str, Any]) -> None:
        """Search without downloading."""
        query = query_namespace.get("query", "")
        cutoff_size = query_namespace.get("limit", 10)
        
        articles = self.search_articles(query, cutoff_size)
        logging.info(f"Found {len(articles)} articles for query: {query}")

    def apipaperdownload(self, query_namespace: Dict[str, Any]) -> None:
        """Download papers from search results."""
        query = query_namespace.get("query", "")
        cutoff_size = query_namespace.get("limit", 10)
        output_dir = query_namespace.get("output", "scielo_downloads")
        
        # Search for articles
        articles = self.search_articles(query, cutoff_size)
        
        # Download each article
        for article in articles:
            article_url = article.get("url")
            if article_url:
                self.download_article(article_url, output_dir) 
    def _generate_scielo_article_id(self, metadata: Dict[str, Any], article_url: str) -> str:
        """
        Generate SciELO-specific article ID following style guide.
        
        Style guide: DOIs should not start with https___doi_org_.
        Use repository-specific URL or clean DOI.
        """
        # Try to extract SciELO article ID from URL first
        if article_url:
            # Extract SciELO article ID from URL
            # Example: https://www.scielo.br/scielo.php?script=sci_arttext&pid=S0100-12342024000100001
            scielo_match = re.search(r'pid=([A-Z0-9]+)', article_url)
            if scielo_match:
                return f"SCIELO_{scielo_match.group(1)}"
            
            # Extract ID from other SciELO URL patterns
            id_match = re.search(r'/([A-Z0-9]+)(?:[/?]|$)', article_url)
            if id_match:
                return f"SCIELO_{id_match.group(1)}"
        
        # Try to use DOI (clean version without https://doi.org/)
        if metadata.get('doi'):
            doi = metadata['doi']
            # Remove https://doi.org/ prefix if present
            if doi.startswith('https://doi.org/'):
                doi = doi.replace('https://doi.org/', '')
            elif doi.startswith('http://doi.org/'):
                doi = doi.replace('http://doi.org/', '')
            
            # Clean DOI for filename (replace non-alphanumeric with underscores)
            doi_clean = re.sub(r'[^\w\-]', '_', doi)
            return f"DOI_{doi_clean}"
        
        # Try to use title (first few words)
        if metadata.get('title'):
            title_clean = re.sub(r'[^\w\s]', '', metadata['title'])
            title_words = title_clean.split()[:3]
            if title_words:
                return f"TITLE_{'_'.join(title_words)}"
        
        # Fallback to hash of URL
        import hashlib
        url_hash = hashlib.md5(article_url.encode()).hexdigest()[:8]
        return f"SCIELO_hash_{url_hash}" 
