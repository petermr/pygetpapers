# Mermaid Diagram Rendering Guide

**Date:** February 6, 2026 (system date)  
**Purpose:** Guide for converting Mermaid diagrams to images/SVG

## Overview

Mermaid diagrams in markdown files can be rendered as images/SVG using several methods. This guide covers the most practical options for the pygetpapers project.

## Option 1: VS Code Extension (Recommended for Development)

### Install Mermaid Preview Extension

**Extension:** "Markdown Preview Mermaid Support" or "Mermaid Preview"

1. Open VS Code
2. Go to Extensions (Cmd+Shift+X on Mac, Ctrl+Shift+X on Windows/Linux)
3. Search for "Mermaid Preview" or "Markdown Preview Mermaid Support"
4. Install the extension

**Usage:**
- Open any `.md` file containing Mermaid diagrams
- Press `Cmd+Shift+V` (Mac) or `Ctrl+Shift+V` (Windows/Linux) to preview
- Diagrams will render automatically in the preview pane
- Right-click on rendered diagram → "Save Image" to export as PNG/SVG

**Pros:**
- ✅ No installation required (just VS Code extension)
- ✅ Live preview while editing
- ✅ Easy export to PNG/SVG
- ✅ Works offline

**Cons:**
- ⚠️ Only works in VS Code
- ⚠️ Manual export process

## Option 2: Mermaid CLI (Command Line Tool)

### Installation

**Prerequisites:** Node.js and npm must be installed

```bash
# Check if Node.js is installed
node --version
npm --version

# Install mermaid-cli globally
npm install -g @mermaid-js/mermaid-cli

# Verify installation
mmdc --version
```

### Usage

**Convert single diagram:**
```bash
# Extract Mermaid code from markdown and convert to SVG
mmdc -i docs/architecture.md -o docs/images/architecture.svg

# Convert to PNG instead
mmdc -i docs/architecture.md -o docs/images/architecture.png

# Specify background color (for PNG)
mmdc -i docs/architecture.md -o docs/images/architecture.png -b white
```

**Extract and convert specific diagram:**
```bash
# Create a temporary .mmd file with just the diagram
cat > temp_diagram.mmd << 'EOF'
graph TB
    A[Start] --> B[Process]
    B --> C[End]
EOF

# Convert to SVG
mmdc -i temp_diagram.mmd -o diagram.svg

# Clean up
rm temp_diagram.mmd
```

**Batch conversion script:**
```bash
#!/bin/bash
# convert_mermaid_diagrams.sh

# Create output directory
mkdir -p docs/images

# Convert architecture diagrams
mmdc -i docs/architecture.md -o docs/images/architecture-v1.svg
mmdc -i docs/architecture.md -o docs/images/architecture-v2.svg

# Convert declarative operations diagram
mmdc -i docs/declarative-operations-framework.md -o docs/images/declarative-framework.svg

echo "Diagrams converted successfully!"
```

**Pros:**
- ✅ Command-line automation
- ✅ Batch processing support
- ✅ High-quality output
- ✅ Can be integrated into build scripts

**Cons:**
- ⚠️ Requires Node.js/npm installation
- ⚠️ Need to extract Mermaid code from markdown first

## Option 3: Online Mermaid Live Editor

**URL:** https://mermaid.live/

**Usage:**
1. Copy Mermaid code from your markdown file
2. Paste into https://mermaid.live/
3. Diagram renders automatically
4. Click "Actions" → "Download PNG" or "Download SVG"

**Pros:**
- ✅ No installation required
- ✅ Works in any browser
- ✅ Easy to use
- ✅ Can share diagrams via URL

**Cons:**
- ⚠️ Requires internet connection
- ⚠️ Manual copy-paste process
- ⚠️ Not suitable for automation

## Option 4: Python Library (Programmatic)

### Installation

```bash
pip install mermaid
```

### Usage

```python
from mermaid import Mermaid

# Mermaid code from your diagram
mermaid_code = """
graph TB
    A[Start] --> B[Process]
    B --> C[End]
"""

# Create Mermaid instance
mermaid = Mermaid(mermaid_code)

# Render to SVG
svg_output = mermaid.to_svg()
with open('diagram.svg', 'w') as f:
    f.write(svg_output)

# Render to PNG (requires additional dependencies)
# png_output = mermaid.to_png()
```

**Note:** The Python `mermaid` library may have limited features. Consider using `mermaid-cli` via subprocess instead.

## Option 5: GitHub/GitLab Native Rendering

**GitHub and GitLab automatically render Mermaid diagrams** in markdown files!

**Usage:**
- Push your `.md` files to GitHub/GitLab
- View the files in the web interface
- Diagrams render automatically
- Right-click → "Save image" to download

**Pros:**
- ✅ No installation required
- ✅ Automatic rendering
- ✅ Works for all team members
- ✅ Version controlled with code

**Cons:**
- ⚠️ Requires Git repository
- ⚠️ Need to push to remote
- ⚠️ Export requires manual save

## Option 6: Pandoc (Document Conversion)

**Installation:**
```bash
# macOS
brew install pandoc

# Ubuntu/Debian
sudo apt-get install pandoc

# Or download from https://pandoc.org/installing.html
```

**Usage:**
```bash
# Convert markdown with Mermaid to HTML (diagrams render)
pandoc docs/architecture.md -o docs/architecture.html --standalone

# Convert to PDF (requires additional setup for Mermaid)
pandoc docs/architecture.md -o docs/architecture.pdf
```

**Note:** Pandoc requires additional configuration for Mermaid rendering.

## Recommended Setup for pygetpapers Project

### For Development (VS Code Users)

1. **Install VS Code Mermaid extension**
   - "Markdown Preview Mermaid Support" or "Mermaid Preview"
   - Preview diagrams while editing
   - Export as needed

### For Automation (CI/CD or Scripts)

1. **Install mermaid-cli**
   ```bash
   npm install -g @mermaid-js/mermaid-cli
   ```

2. **Create conversion script**
   ```bash
   # scripts/convert_diagrams.sh
   #!/bin/bash
   mkdir -p docs/images
   
   # Extract and convert diagrams
   # (You'll need to extract Mermaid code blocks first)
   ```

### For Documentation (GitHub)

- **No action needed!** GitHub automatically renders Mermaid diagrams
- Just ensure your `.md` files are in the repository
- View diagrams directly in GitHub web interface

## Extracting Mermaid Code from Markdown

To convert diagrams using CLI tools, you need to extract the Mermaid code blocks:

**Manual extraction:**
1. Copy the code between ` ```mermaid` and ` ``` `
2. Save to `.mmd` file
3. Convert using `mmdc`

**Automated extraction script:**
```python
#!/usr/bin/env python3
"""Extract Mermaid diagrams from markdown files."""

import re
from pathlib import Path

def extract_mermaid_diagrams(markdown_file: Path, output_dir: Path):
    """Extract all Mermaid diagrams from a markdown file."""
    content = markdown_file.read_text()
    
    # Find all Mermaid code blocks
    pattern = r'```mermaid\n(.*?)\n```'
    matches = re.findall(pattern, content, re.DOTALL)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for i, diagram_code in enumerate(matches, 1):
        output_file = output_dir / f"{markdown_file.stem}_diagram_{i}.mmd"
        output_file.write_text(diagram_code.strip())
        print(f"Extracted: {output_file}")
    
    return len(matches)

# Usage
if __name__ == "__main__":
    extract_mermaid_diagrams(
        Path("docs/architecture.md"),
        Path("docs/mermaid_diagrams")
    )
```

## Quick Start: Convert All Diagrams

**One-time setup:**
```bash
# Install mermaid-cli
npm install -g @mermaid-js/mermaid-cli

# Create output directory
mkdir -p docs/images
```

**Convert diagrams:**
```bash
# Extract Mermaid code and convert
# (You'll need to extract code blocks first, or use the Python script above)

# Example: Convert extracted diagram
mmdc -i docs/mermaid_diagrams/architecture_diagram_1.mmd \
     -o docs/images/architecture-v1.svg \
     -b white
```

## Troubleshooting

### Issue: `mmdc: command not found`
**Solution:** Install mermaid-cli: `npm install -g @mermaid-js/mermaid-cli`

### Issue: Diagrams not rendering in VS Code
**Solution:** Install "Markdown Preview Mermaid Support" extension

### Issue: Diagrams not showing on GitHub
**Solution:** Ensure code blocks use ` ```mermaid` (not ` ```mermaid` with extra spaces)

### Issue: SVG output is blank
**Solution:** Check Mermaid syntax, ensure diagram code is valid

## Best Practices

1. **Keep diagrams in markdown** - Source of truth
2. **Generate images for presentations** - Use CLI to create PNG/SVG
3. **Version control both** - Commit both `.md` and generated images
4. **Document diagram locations** - Keep track of where diagrams are used
5. **Automate conversion** - Add to build scripts if needed

## References

- **Mermaid Documentation:** https://mermaid.js.org/
- **Mermaid CLI:** https://github.com/mermaid-js/mermaid-cli
- **Mermaid Live Editor:** https://mermaid.live/
- **VS Code Extension:** Search "Mermaid Preview" in VS Code marketplace

---

**Date:** February 6, 2026 (system date)
