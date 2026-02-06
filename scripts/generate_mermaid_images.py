#!/usr/bin/env python3
"""
Generate SVG/PNG images from Mermaid diagrams using Mermaid Live API.

Date: February 6, 2026 (system date)
"""

import json
import base64
from pathlib import Path
from typing import Optional

try:
    import requests
except ImportError:
    print("Error: requests library not installed. Install with: pip install requests")
    exit(1)


def generate_svg_from_mermaid(mermaid_code: str) -> Optional[str]:
    """
    Generate SVG from Mermaid code using Mermaid Live API.
    
    Args:
        mermaid_code: Mermaid diagram code
        
    Returns:
        SVG content as string, or None if failed
    """
    api_url = "https://api.mermaid.ink/svg"
    
    # Encode mermaid code to base64
    mermaid_b64 = base64.urlsafe_b64encode(mermaid_code.encode()).decode()
    
    try:
        response = requests.get(f"{api_url}/{mermaid_b64}", timeout=30)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error calling Mermaid API: {e}")
        return None


def generate_png_from_mermaid(mermaid_code: str) -> Optional[bytes]:
    """
    Generate PNG from Mermaid code using Mermaid Live API.
    
    Args:
        mermaid_code: Mermaid diagram code
        
    Returns:
        PNG content as bytes, or None if failed
    """
    api_url = "https://api.mermaid.ink/png"
    
    # Encode mermaid code to base64
    mermaid_b64 = base64.urlsafe_b64encode(mermaid_code.encode()).decode()
    
    try:
        response = requests.get(f"{api_url}/{mermaid_b64}", timeout=30)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Error calling Mermaid API: {e}")
        return None


def convert_mermaid_file(input_file: Path, output_dir: Path, format: str = "svg"):
    """
    Convert a Mermaid file to SVG or PNG.
    
    Args:
        input_file: Path to .mmd file
        output_dir: Output directory for images
        format: "svg" or "png"
    """
    mermaid_code = input_file.read_text()
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if format == "svg":
        svg_content = generate_svg_from_mermaid(mermaid_code)
        if svg_content:
            output_file = output_dir / f"{input_file.stem}.svg"
            output_file.write_text(svg_content)
            print(f"✅ Generated: {output_file}")
            return output_file
    elif format == "png":
        png_content = generate_png_from_mermaid(mermaid_code)
        if png_content:
            output_file = output_dir / f"{input_file.stem}.png"
            output_file.write_bytes(png_content)
            print(f"✅ Generated: {output_file}")
            return output_file
    
    return None


def main():
    """Generate images from all extracted Mermaid diagrams."""
    project_root = Path(__file__).parent.parent
    mermaid_dir = project_root / "docs" / "mermaid_diagrams"
    output_dir = project_root / "docs" / "images"
    
    if not mermaid_dir.exists():
        print(f"Error: Mermaid diagrams directory not found: {mermaid_dir}")
        print("Run extract_and_convert_mermaid.py first to extract diagrams.")
        return
    
    mermaid_files = list(mermaid_dir.glob("*.mmd"))
    
    if not mermaid_files:
        print(f"No Mermaid files found in {mermaid_dir}")
        return
    
    print(f"📊 Found {len(mermaid_files)} Mermaid diagram(s)")
    print(f"📁 Output directory: {output_dir}\n")
    
    # Generate SVG images
    print("Generating SVG images...")
    svg_files = []
    for mmd_file in sorted(mermaid_files):
        svg_file = convert_mermaid_file(mmd_file, output_dir, format="svg")
        if svg_file:
            svg_files.append(svg_file)
    
    # Generate PNG images
    print("\nGenerating PNG images...")
    png_files = []
    for mmd_file in sorted(mermaid_files):
        png_file = convert_mermaid_file(mmd_file, output_dir, format="png")
        if png_file:
            png_files.append(png_file)
    
    print(f"\n📊 Summary:")
    print(f"   Generated {len(svg_files)} SVG file(s)")
    print(f"   Generated {len(png_files)} PNG file(s)")
    print(f"   Output directory: {output_dir}")


if __name__ == "__main__":
    main()
