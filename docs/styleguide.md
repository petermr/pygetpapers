# Pygetpapers Style Guide

This document records coding and naming conventions for the pygetpapers project.

## File Naming Conventions

### STYLE: All filenames should only have alphanumeric and underscores

- ✅ **Good**: `biorxiv_integration.py`, `test_scraper.py`, `metadata_2024.json`
- ❌ **Bad**: `biorxiv-integration.py`, `test.scraper.py`, `metadata-2024.json`

**Rationale**: Using only alphanumeric characters and underscores ensures maximum compatibility across different operating systems and avoids issues with special characters in file paths.

## Path Construction

### STYLE: Use clean Path construction with comma-separated arguments

- ✅ **Good**: `Path(Path.home(), "pygetpapers")`
- ❌ **Bad**: `Path.home() / "pygetpapers"`

**Rationale**: The comma-separated format is more explicit and readable than the `/` operator approach.

## Code Organization

### STYLE: Use absolute imports

- ✅ **Good**: `from pathlib import Path`, `import streamlit as st`
- ❌ **Bad**: `from .pathlib import Path`, `from ..streamlit import st`

**Rationale**: Absolute imports are more explicit and avoid confusion about module hierarchy.

### STYLE: Avoid local imports that shadow global imports

- ✅ **Good**: Use global imports at the top of the file
- ❌ **Bad**: Local `from pathlib import Path` inside functions

**Rationale**: Local imports can cause `UnboundLocalError` when they shadow global imports.

## Interface Design

### STYLE: Remove unused UI elements

- ✅ **Good**: Clean interface without unused counters or duplicate sections
- ❌ **Bad**: "File Downloads:" counters that are never updated

**Rationale**: Unused UI elements clutter the interface and confuse users.

## Output Directory Structure

### STYLE: Use user's home directory for output

- ✅ **Good**: `~/pygetpapers/{repo}_{timestamp}`
- ❌ **Bad**: Output in current working directory

**Rationale**: Using the home directory provides a consistent, user-accessible location for downloaded files.

---

*This style guide will be updated as new conventions are established.* 