#!/usr/bin/env python3
"""
Create DataTables for Lantana research results.
"""

import json
import glob
import html
from pathlib import Path

def create_lantana_datatables():
    """Create DataTables HTML for Lantana research."""
    
    # Load all metadata files
    articles = []
    for metadata_file in glob.glob('*/metadata.json'):
        with open(metadata_file, 'r', encoding='utf-8') as f:
            articles.append(json.load(f))
    
    print(f"Loaded {len(articles)} articles")
    
    # Create table rows
    table_rows = []
    for article in articles:
        # Extract data
        title = html.escape(article.get('title', 'No title'))
        authors = ', '.join(article.get('authors', ['Unknown']))
        authors = html.escape(authors)
        year = html.escape(str(article.get('year', 'Unknown')))
        abstract = html.escape(article.get('abstract') or 'No abstract')
        
        # SDG badges
        sdgs = article.get('sdg_classifications', [])
        sdg_html = ''
        for sdg in sdgs:
            if 'SDG-' in sdg:
                sdg_num = sdg.split('-')[1].split(':')[0]
                sdg_html += f'<span class="sdg-badge sdg-{sdg_num}">{sdg_num}</span> '
        
        # Keywords
        keywords = ', '.join(article.get('keywords', []))
        keywords = html.escape(keywords)
        
        # Links
        handle_url = article.get('handle_url', '')
        doi = article.get('doi', '')
        
        links_html = ''
        if handle_url:
            links_html += f'<a href="{handle_url}" target="_blank">Handle</a> '
        if doi:
            links_html += f'<a href="https://doi.org/{doi}" target="_blank">DOI</a>'
        
        # Local files
        article_id = article.get('id', 'unknown')
        local_files = f'<a href="{article_id}/metadata.json" target="_blank">JSON</a>'
        
        # Check if PDF exists
        pdf_path = Path(article_id) / "fulltext.pdf"
        if pdf_path.exists():
            local_files += f' <a href="{article_id}/fulltext.pdf" target="_blank">PDF</a>'
        
        # Create row
        row = f"""
        <tr>
            <td>{article_id}</td>
            <td>{title}</td>
            <td>{authors}</td>
            <td>{year}</td>
            <td>{abstract[:200]}...</td>
            <td>{sdg_html}</td>
            <td>{keywords}</td>
            <td>{links_html}</td>
            <td>{local_files}</td>
        </tr>
        """
        table_rows.append(row)
    
    # Create HTML template
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lantana Research Results - UPSpace</title>
    
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdn.datatables.net/1.11.5/js/jquery.dataTables.min.js"></script>
    <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.11.5/css/jquery.dataTables.min.css">
    
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; text-align: center; margin-bottom: 30px; }}
        .sdg-badge {{ display: inline-block; padding: 2px 6px; margin: 1px; border-radius: 3px; font-size: 11px; font-weight: bold; color: white; }}
        .sdg-06 {{ background-color: #26bde2; }}
        .sdg-15 {{ background-color: #56c02b; }}
        .sdg-02 {{ background-color: #dda63a; }}
        .sdg-13 {{ background-color: #3f7e44; }}
        .sdg-05 {{ background-color: #ff3a21; }}
        .sdg-03 {{ background-color: #4c9feb; }}
        .abstract-cell {{ max-width: 400px; }}
        .authors-cell {{ max-width: 300px; }}
        .sdg-cell {{ max-width: 200px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🌿 Lantana Research Results from UPSpace</h1>
        <p><strong>Query:</strong> Lantana | <strong>Results:</strong> {len(articles)} articles</p>
        
        <table id="lantana-table" class="display">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Title</th>
                    <th>Authors</th>
                    <th>Year</th>
                    <th>Abstract</th>
                    <th>SDGs</th>
                    <th>Keywords</th>
                    <th>Links</th>
                    <th>Files</th>
                </tr>
            </thead>
            <tbody>
                {''.join(table_rows)}
            </tbody>
        </table>
    </div>
    
    <script>
        $(document).ready(function() {{
            $('#lantana-table').DataTable({{
                pageLength: 10,
                order: [[3, 'desc']],
                responsive: true
            }});
        }});
    </script>
</body>
</html>
    """
    
    # Save HTML file
    with open('lantana_datatables.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ DataTables HTML created: lantana_datatables.html")

if __name__ == "__main__":
    create_lantana_datatables() 