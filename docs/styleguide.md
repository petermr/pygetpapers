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

### STYLE: No use of `sys.path` or `PYTHONPATH`

- ✅ **Good**: Use proper package installation with `pip install -e .`
- ❌ **Bad**: `sys.path.append()`, `PYTHONPATH` environment variables

**Rationale**: Manipulating Python's import path is fragile and can cause import conflicts. Use proper package installation instead.

## Interface Design

### STYLE: Remove unused UI elements

- ✅ **Good**: Clean interface without unused counters or duplicate sections
- ❌ **Bad**: "File Downloads:" counters that are never updated

**Rationale**: Unused UI elements clutter the interface and confuse users.

## Version Management

### STYLE: Every edit should increase the version

- ✅ **Good**: Increment version number for every code change during development
- ❌ **Bad**: Making multiple changes without version bumps

**Rationale**: During development this will be `\d.\d.\da\d+`, e.g. `1.2.5a21`. This prevents confusion with cached installations and makes it clear when changes were made.

## Output Directory Structure

### STYLE: Use user's home directory for output

- ✅ **Good**: `~/pygetpapers/{repo}_{timestamp}`
- ❌ **Bad**: Output in current working directory

**Rationale**: Using the home directory provides a consistent, user-accessible location for downloaded files.

### STYLE: Output should never be sent to the root dir of pygetpapers. Use dir temp/ to which all non-permanent output should be sent. Deleting temp should not delete anything important

- ✅ **Good**: `temp/output_files/`, `temp/test_results/`, `temp/downloads/`
- ❌ **Bad**: Output files in the root pygetpapers directory

**Rationale**: Keeping temporary output in a dedicated `temp/` directory prevents cluttering the project root and makes it clear which files are temporary and can be safely deleted.

---

*This style guide will be updated as new conventions are established.* 