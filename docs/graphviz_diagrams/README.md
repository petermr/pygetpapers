# Graphviz Diagrams

**Date:** February 6, 2026 (system date)

## Overview

This directory contains Graphviz DOT format (`.gv`) files converted from Mermaid diagrams. These files can be used to generate high-quality SVG, PNG, PDF, or other image formats using Graphviz.

## Generated Files

1. **architecture_diagram_1.gv** - Current Architecture (v1.x)
2. **architecture_diagram_2.gv** - Proposed Architecture (v2.0)
3. **declarative-operations-framework_diagram_1.gv** - Declarative Operations Framework

## Converting to Images

### Prerequisites

Install Graphviz:
```bash
# macOS
brew install graphviz

# Ubuntu/Debian
sudo apt-get install graphviz

# Or download from: https://graphviz.org/download/
```

### Generate SVG Images

```bash
cd /Users/pm286/workspace/pygetpapers

# Convert single file
dot -Tsvg docs/graphviz_diagrams/architecture_diagram_1.gv -o docs/images/architecture-v1.svg

# Convert all files
for gv_file in docs/graphviz_diagrams/*.gv; do
    dot -Tsvg "$gv_file" -o "docs/images/$(basename "$gv_file" .gv).svg"
done
```

### Generate PNG Images

```bash
# Convert single file
dot -Tpng docs/graphviz_diagrams/architecture_diagram_1.gv -o docs/images/architecture-v1.png

# Convert all files
for gv_file in docs/graphviz_diagrams/*.gv; do
    dot -Tpng "$gv_file" -o "docs/images/$(basename "$gv_file" .gv).png"
done
```

### Generate PDF Images

```bash
dot -Tpdf docs/graphviz_diagrams/architecture_diagram_1.gv -o docs/images/architecture-v1.pdf
```

## Output Formats

Graphviz supports many output formats:
- **SVG** (`-Tsvg`) - Scalable vector graphics (recommended)
- **PNG** (`-Tpng`) - Raster image
- **PDF** (`-Tpdf`) - PDF document
- **EPS** (`-Teps`) - Encapsulated PostScript
- **PNG** (`-Tpng`) - High-resolution raster

## Customization

You can edit the `.gv` files to customize:
- Node colors: `node [fillcolor=lightblue, style="rounded,filled"]`
- Edge styles: `edge [style=dashed, color=gray]`
- Layout: Change `rankdir=TB` to `rankdir=LR` for left-right layout
- Font sizes: `node [fontsize=12]`

## Conversion Script

The conversion script is located at:
```
scripts/mermaid_to_graphviz.py
```

To regenerate Graphviz files from Mermaid:
```bash
python scripts/mermaid_to_graphviz.py
```

## Advantages of Graphviz

- ✅ **High-quality output** - Professional-looking diagrams
- ✅ **Multiple formats** - SVG, PNG, PDF, EPS, etc.
- ✅ **Customizable** - Full control over styling
- ✅ **Command-line friendly** - Easy to automate
- ✅ **No browser required** - Unlike mermaid-cli

## Files Structure

```
docs/
├── mermaid_diagrams/          # Source Mermaid files (.mmd)
├── graphviz_diagrams/         # Graphviz DOT files (.gv)
└── images/                    # Generated images (SVG/PNG)
```

---

**Note:** The Graphviz `.gv` files are the converted format. The original Mermaid `.mmd` files remain the source of truth.
