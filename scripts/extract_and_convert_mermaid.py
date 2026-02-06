#!/usr/bin/env python3
"""
Extract Mermaid diagrams from markdown files and prepare for conversion.

Date: February 6, 2026 (system date)
"""

import re
from pathlib import Path

def extract_mermaid_diagrams(markdown_file: Path, output_dir: Path):
    """Extract all Mermaid diagrams from a markdown file."""
    content = markdown_file.read_text()
    
    # Find all Mermaid code blocks
    pattern = r'```mermaid\n(.*?)\n```'
    matches = re.findall(pattern, content, re.DOTALL)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    extracted_files = []
    for i, diagram_code in enumerate(matches, 1):
        output_file = output_dir / f"{markdown_file.stem}_diagram_{i}.mmd"
        output_file.write_text(diagram_code.strip())
        extracted_files.append(output_file)
        print(f"✅ Extracted: {output_file}")
    
    return extracted_files

def main():
    """Extract Mermaid diagrams from documentation files."""
    project_root = Path(__file__).parent.parent
    docs_dir = project_root / "docs"
    output_dir = project_root / "docs" / "mermaid_diagrams"
    
    # Files containing Mermaid diagrams
    markdown_files = [
        docs_dir / "architecture.md",
        docs_dir / "declarative-operations-framework.md",
    ]
    
    all_extracted = []
    for md_file in markdown_files:
        if md_file.exists():
            print(f"\n📄 Processing: {md_file.name}")
            extracted = extract_mermaid_diagrams(md_file, output_dir)
            all_extracted.extend(extracted)
        else:
            print(f"⚠️  File not found: {md_file}")
    
    print(f"\n📊 Summary:")
    print(f"   Extracted {len(all_extracted)} diagram(s)")
    print(f"   Output directory: {output_dir}")
    
    if all_extracted:
        print(f"\n📝 Next steps:")
        print(f"   1. Install mermaid-cli: npm install -g @mermaid-js/mermaid-cli")
        print(f"   2. Convert diagrams:")
        for mmd_file in all_extracted:
            svg_file = mmd_file.with_suffix('.svg')
            print(f"      mmdc -i {mmd_file} -o {svg_file}")

if __name__ == "__main__":
    main()
