# Pygetpapers Style Guide

This document records coding and naming conventions for the pygetpapers project.

## Query Examples

### STYLE: Use climate change examples for demonstrations and testing

- ✅ **Good**: `"climate change AND adaptation"`, `"global warming AND mitigation"`, `"carbon sequestration"`
- ❌ **Bad**: `"cancer AND immunotherapy"`, `"artificial intelligence"`, `"machine learning"`

**Rationale**: Climate change is a universally relevant topic that demonstrates the tool's capabilities while being accessible to all users. It avoids medical or technical jargon that might not be familiar to all audiences.

### STYLE: Include full download flags in examples

- ✅ **Good**: `pygetpapers --query "climate change AND adaptation" --api europe_pmc --limit 5 -x -p --fulltext_html --datatables`
- ❌ **Bad**: `pygetpapers --query "climate change AND adaptation" --limit 5`

**Rationale**: Examples should demonstrate the full capabilities by downloading XML (-x), PDF (-p), and generating HTML (--fulltext_html) to show local file links in datatables.

### STYLE: Never write any files to root directory of pygetpapers project without asking

- ✅ **Good**: Write files to appropriate subdirectories (examples/, temp/, docs/, etc.)
- ❌ **Bad**: Creating files directly in the project root without explicit permission

**Rationale**: The root directory should remain clean and organized. All output files, examples, and temporary files should go to designated directories. This prevents clutter and maintains project structure integrity.

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

## Development Protocol

### STYLE: Follow strict development protocol for all code changes

**Before Any Code Changes:**
1. **Full schema design** - Define exact output structure, file naming, directory layout
2. **Validation tool** - Create tool to verify output conforms to schema and prevent regression
3. **File change plan** - List exactly what files will be edited/created/deleted
4. **User approval** - Wait for explicit agreement before proceeding
5. **Small steps** - Make minimal changes, show diffs on demand

**For Any Code Project:**
1. **Propose changes** - "I will edit X, create Y, delete Z"
2. **Get agreement** - Wait for "proceed" or "modify plan"
3. **Show diffs** - On demand, show exactly what will change
4. **Test thoroughly** - Ensure existing functionality remains intact

**Rationale**: This protocol prevents breaking working systems, ensures user control over changes, and maintains code quality through systematic validation and testing.

### STYLE: Never write code without explicit user approval

- ✅ **Good**: Propose changes, wait for approval, then implement
- ❌ **Bad**: Writing code immediately without user agreement

**Rationale**: Users have invested significant time in building working systems. All changes must be approved to prevent regression and maintain trust.

### STYLE: Create validation tools for all output schemas

- ✅ **Good**: Build tools to verify output conforms to defined schemas
- ❌ **Bad**: Assuming output is correct without validation

**Rationale**: Validation tools prevent regression and ensure consistent output quality across all repositories and updates.

---

*This style guide will be updated as new conventions are established.* 