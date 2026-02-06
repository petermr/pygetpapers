# Workflow Diagram Images

**Date:** February 6, 2026 (system date)

## Overview

This directory contains generated SVG/PNG images from Mermaid diagrams in the documentation.

## Generated Images

The following diagrams have been extracted and are ready for conversion:

1. **architecture_diagram_1.mmd** - Current Architecture (v1.x)
2. **architecture_diagram_2.mmd** - Proposed Architecture (v2.0)
3. **declarative-operations-framework_diagram_1.mmd** - Declarative Operations Framework

## How to Generate Images

### Option 1: Using mermaid-cli (Recommended)

**Prerequisites:** Node.js and npm installed

```bash
# Install mermaid-cli globally (requires sudo/admin)
npm install -g @mermaid-js/mermaid-cli

# Or install locally in project (already done)
# npm install @mermaid-js/mermaid-cli --save-dev

# Convert diagrams to SVG
cd /Users/pm286/workspace/pygetpapers
npx @mermaid-js/mermaid-cli -i docs/mermaid_diagrams/architecture_diagram_1.mmd -o docs/images/architecture-v1.svg -b white
npx @mermaid-js/mermaid-cli -i docs/mermaid_diagrams/architecture_diagram_2.mmd -o docs/images/architecture-v2.svg -b white
npx @mermaid-js/mermaid-cli -i docs/mermaid_diagrams/declarative-operations-framework_diagram_1.mmd -o docs/images/declarative-operations-framework.svg -b white

# Convert to PNG instead
npx @mermaid-js/mermaid-cli -i docs/mermaid_diagrams/architecture_diagram_1.mmd -o docs/images/architecture-v1.png -b white
```

### Option 2: Using Python Script (When Network Available)

```bash
# Run the Python script (requires network access)
python scripts/generate_mermaid_images.py
```

### Option 3: Using VS Code Extension

1. Install "Markdown Preview Mermaid Support" extension
2. Open `docs/architecture.md` or `docs/declarative-operations-framework.md`
3. Press `Cmd+Shift+V` (Mac) or `Ctrl+Shift+V` (Windows/Linux)
4. Right-click on rendered diagram → "Save Image"

### Option 4: Using Online Tool

1. Go to https://mermaid.live/
2. Copy Mermaid code from `.mmd` files in `docs/mermaid_diagrams/`
3. Paste into editor
4. Click "Actions" → "Download PNG" or "Download SVG"

## Files Structure

```
docs/
├── mermaid_diagrams/          # Extracted Mermaid code (.mmd files)
│   ├── architecture_diagram_1.mmd
│   ├── architecture_diagram_2.mmd
│   └── declarative-operations-framework_diagram_1.mmd
└── images/                    # Generated images (SVG/PNG)
    ├── architecture-v1.svg
    ├── architecture-v2.svg
    └── declarative-operations-framework.svg
```

## Troubleshooting

### Issue: `mmdc: command not found`
**Solution:** Install mermaid-cli: `npm install -g @mermaid-js/mermaid-cli`

### Issue: Browser launch error
**Solution:** mermaid-cli requires Puppeteer. Ensure you have Chrome/Chromium installed or use the online tool.

### Issue: Network errors with Python script
**Solution:** Ensure you have internet access and the Mermaid API is reachable.

## Next Steps

Once images are generated, you can:
1. Reference them in markdown: `![Architecture v1](images/architecture-v1.svg)`
2. Use in presentations
3. Include in documentation
4. Share with team members

---

**Note:** The Mermaid source files (`.mmd`) are the source of truth. Regenerate images whenever diagrams are updated.
