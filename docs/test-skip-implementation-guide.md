# Implementation Guide: Skipping Repository Tests

## Quick Start (Strategy 1: Pytest Markers)

### Step 1: Update pytest.ini

Add repository markers to your `pytest.ini`:

```ini
markers =
    redalyc: marks tests that require Redalyc connectivity
    scielo: marks tests that require SciELO connectivity
    biorxiv: marks tests that require BioRxiv connectivity
    skip_if_redalyc_down: marks tests to skip if Redalyc is down
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

### Step 2: Mark Your Tests

Add markers to repository-specific test files:

**tests/test_redalyc_*.py:**
```python
import pytest

@pytest.mark.redalyc
def test_redalyc_search():
    ...

@pytest.mark.redalyc
def test_redalyc_download():
    ...
```

**docs/scielo/test_scielo_*.py:**
```python
import pytest

@pytest.mark.scielo
def test_scielo_basic():
    ...

@pytest.mark.scielo
def test_scielo_metadata_extraction():
    ...
```

**tests/test_biorxiv_*.py:**
```python
import pytest

@pytest.mark.biorxiv
def test_biorxiv_search():
    ...

@pytest.mark.biorxiv
def test_biorxiv_download():
    ...
```

### Step 3: Use Command-Line Filtering

```bash
# Skip all Redalyc tests
pytest -m "not redalyc"

# Skip multiple repositories
pytest -m "not redalyc and not scielo"

# Skip all repository tests, run only core tests
pytest -m "not redalyc and not scielo and not biorxiv"

# Run only Redalyc tests
pytest -m "redalyc"

# Run only core tests (no repository tests)
pytest -m "not redalyc and not scielo and not biorxiv"
```

---

## Advanced: Hybrid Approach (Strategy 6)

### Step 1: Update conftest.py

Add environment variable support to your existing `conftest.py`:

```python
import os
import pytest
from test_utils import test_redalyc_connectivity

def pytest_collection_modifyitems(config, items):
    """Skip tests based on environment variables and markers."""
    skip_repos = set()
    
    # Check environment variables (for CI/CD)
    if os.getenv("SKIP_REDALYC", "").lower() in ("1", "true", "yes"):
        skip_repos.add("redalyc")
    if os.getenv("SKIP_SCIELO", "").lower() in ("1", "true", "yes"):
        skip_repos.add("scielo")
    if os.getenv("SKIP_BIORXIV", "").lower() in ("1", "true", "yes"):
        skip_repos.add("biorxiv")
    
    # Check marker expressions (for command-line)
    marker_expr = config.getoption("-m", default="")
    if marker_expr:
        if "not redalyc" in marker_expr:
            skip_repos.add("redalyc")
        if "not scielo" in marker_expr:
            skip_repos.add("scielo")
        if "not biorxiv" in marker_expr:
            skip_repos.add("biorxiv")
    
    # Skip tests
    for item in items:
        # Check by marker
        if hasattr(item, 'pytestmark'):
            for mark in item.pytestmark:
                if mark.name in skip_repos:
                    item.add_marker(
                        pytest.mark.skip(reason=f"Skipping {mark.name} tests")
                    )
        
        # Check by nodeid
        nodeid_lower = item.nodeid.lower()
        for repo in skip_repos:
            if repo in nodeid_lower:
                item.add_marker(
                    pytest.mark.skip(reason=f"Skipping {repo} tests")
                )
```

### Step 2: Usage Examples

**Command-line (local development):**
```bash
pytest -m "not redalyc"
pytest -m "not redalyc and not scielo"
```

**Environment variables (CI/CD):**
```bash
SKIP_REDALYC=1 pytest
SKIP_REDALYC=1 SKIP_SCIELO=1 SKIP_BIORXIV=1 pytest
```

**GitHub Actions example:**
```yaml
- name: Run tests (skip external repos)
  env:
    SKIP_REDALYC: 1
    SKIP_SCIELO: 1
    SKIP_BIORXIV: 1
  run: pytest
```

---

## Auto-Marking Tests by File Name

You can automatically mark tests based on file names in `conftest.py`:

```python
def pytest_collection_modifyitems(config, items):
    """Auto-mark tests based on file names."""
    for item in items:
        nodeid_lower = item.nodeid.lower()
        
        # Auto-mark by file name
        if "redalyc" in nodeid_lower and not any(m.name == "redalyc" for m in item.pytestmark):
            item.add_marker(pytest.mark.redalyc)
        if "scielo" in nodeid_lower and not any(m.name == "scielo" for m in item.pytestmark):
            item.add_marker(pytest.mark.scielo)
        if "biorxiv" in nodeid_lower and not any(m.name == "biorxiv" for m in item.pytestmark):
            item.add_marker(pytest.mark.biorxiv)
```

This way, tests in `test_redalyc_*.py` files are automatically marked.

---

## Recommended Implementation Order

1. **Phase 1**: Add markers to `pytest.ini` (5 minutes)
2. **Phase 2**: Auto-mark tests by file name in `conftest.py` (10 minutes)
3. **Phase 3**: Add environment variable support (15 minutes)
4. **Phase 4**: Manually mark any tests not auto-detected (as needed)

This gives you immediate functionality with minimal effort, then you can refine as needed.
