#!/bin/bash
# Convert all Mermaid diagrams to SVG/PNG images
# Date: February 6, 2026 (system date)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
MERMAID_DIR="$PROJECT_ROOT/docs/mermaid_diagrams"
OUTPUT_DIR="$PROJECT_ROOT/docs/images"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Check if mermaid-cli is available
if command -v mmdc &> /dev/null; then
    MMDC_CMD="mmdc"
elif command -v npx &> /dev/null; then
    MMDC_CMD="npx @mermaid-js/mermaid-cli"
else
    echo "Error: mermaid-cli not found. Install with: npm install -g @mermaid-js/mermaid-cli"
    exit 1
fi

echo "📊 Converting Mermaid diagrams to images..."
echo "   Source: $MERMAID_DIR"
echo "   Output: $OUTPUT_DIR"
echo ""

# Convert each .mmd file to SVG
for mmd_file in "$MERMAID_DIR"/*.mmd; do
    if [ -f "$mmd_file" ]; then
        filename=$(basename "$mmd_file" .mmd)
        svg_file="$OUTPUT_DIR/${filename}.svg"
        
        echo "Converting: $filename.mmd → $filename.svg"
        $MMDC_CMD -i "$mmd_file" -o "$svg_file" -b white
        
        if [ -f "$svg_file" ]; then
            echo "  ✅ Generated: $svg_file"
        else
            echo "  ❌ Failed to generate: $svg_file"
        fi
    fi
done

echo ""
echo "📊 Summary:"
echo "   Generated SVG files in: $OUTPUT_DIR"
ls -lh "$OUTPUT_DIR"/*.svg 2>/dev/null || echo "   No SVG files generated"
