# Strategies for Skipping Repository-Specific Tests

This document outlines different strategies for skipping tests for specific repositories (Redalyc, SciELO, BioRxiv) that can be evaluated and implemented.

## Strategy 1: Pytest Markers with Command-Line Filtering (Recommended)

**Approach**: Use pytest markers to tag tests by repository, then filter with `-m` flag.

**Pros**:
- Built into pytest, no custom code needed
- Flexible - can combine markers (e.g., `-m "redalyc and slow"`)
- Easy to use: `pytest -m "not redalyc"`
- Works with existing pytest infrastructure

**Cons**:
- Requires marking all repository-specific tests
- Need to remember marker names

**Implementation**:

1. Update `pytest.ini`:
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

2. Mark tests in test files:
```python
@pytest.mark.redalyc
def test_redalyc_search():
    ...

@pytest.mark.scielo
def test_scielo_basic():
    ...

@pytest.mark.biorxiv
def test_biorxiv_search():
    ...
```

3. Usage:
```bash
# Skip all Redalyc tests
pytest -m "not redalyc"

# Skip multiple repositories
pytest -m "not redalyc and not scielo"

# Run only core tests (no repository tests)
pytest -m "not redalyc and not scielo and not biorxiv"

# Skip Redalyc and SciELO but run BioRxiv
pytest -m "not redalyc and not scielo"
```

---

## Strategy 2: Environment Variables

**Approach**: Use environment variables to control which repository tests run.

**Pros**:
- Simple to set: `SKIP_REDALYC=1 pytest`
- Can be set in CI/CD easily
- No need to remember command-line flags

**Cons**:
- Less discoverable than command-line flags
- Need to check environment in conftest.py

**Implementation**:

1. Update `conftest.py`:
```python
import os
import pytest

def pytest_collection_modifyitems(config, items):
    """Skip tests based on environment variables."""
    skip_repos = []
    
    if os.getenv("SKIP_REDALYC", "").lower() in ("1", "true", "yes"):
        skip_repos.append("redalyc")
    if os.getenv("SKIP_SCIELO", "").lower() in ("1", "true", "yes"):
        skip_repos.append("scielo")
    if os.getenv("SKIP_BIORXIV", "").lower() in ("1", "true", "yes"):
        skip_repos.append("biorxiv")
    
    for item in items:
        for repo in skip_repos:
            if repo in item.nodeid.lower():
                item.add_marker(
                    pytest.mark.skip(reason=f"Skipping {repo} tests (SKIP_{repo.upper()}=1)")
                )
```

2. Usage:
```bash
# Skip Redalyc tests
SKIP_REDALYC=1 pytest

# Skip multiple repositories
SKIP_REDALYC=1 SKIP_SCIELO=1 pytest

# Skip all repository tests
SKIP_REDALYC=1 SKIP_SCIELO=1 SKIP_BIORXIV=1 pytest
```

---

## Strategy 3: Pytest Configuration Options (Custom)

**Approach**: Add custom pytest command-line options.

**Pros**:
- Explicit and clear: `pytest --skip-redalyc`
- Self-documenting with `--help`
- Can combine with other pytest options

**Cons**:
- Requires custom pytest plugin code
- More complex to implement

**Implementation**:

1. Create `pytest_skip_repos.py`:
```python
"""Pytest plugin for skipping repository-specific tests."""
import pytest

def pytest_addoption(parser):
    """Add command-line options."""
    parser.addoption(
        "--skip-redalyc",
        action="store_true",
        default=False,
        help="Skip all Redalyc-related tests",
    )
    parser.addoption(
        "--skip-scielo",
        action="store_true",
        default=False,
        help="Skip all SciELO-related tests",
    )
    parser.addoption(
        "--skip-biorxiv",
        action="store_true",
        default=False,
        help="Skip all BioRxiv-related tests",
    )
    parser.addoption(
        "--skip-repos",
        action="store",
        default="",
        help="Comma-separated list of repositories to skip (e.g., 'redalyc,scielo')",
    )


def pytest_collection_modifyitems(config, items):
    """Skip tests based on command-line options."""
    skip_repos = []
    
    if config.getoption("--skip-redalyc"):
        skip_repos.append("redalyc")
    if config.getoption("--skip-scielo"):
        skip_repos.append("scielo")
    if config.getoption("--skip-biorxiv"):
        skip_repos.append("biorxiv")
    
    # Handle --skip-repos option
    skip_repos_option = config.getoption("--skip-repos")
    if skip_repos_option:
        skip_repos.extend([r.strip() for r in skip_repos_option.split(",")])
    
    for item in items:
        for repo in skip_repos:
            if repo.lower() in item.nodeid.lower():
                item.add_marker(
                    pytest.mark.skip(reason=f"Skipping {repo} tests (--skip-{repo})")
                )
```

2. Update `pytest.ini`:
```ini
[pytest]
plugins = pytest_skip_repos
```

3. Usage:
```bash
# Skip Redalyc tests
pytest --skip-redalyc

# Skip multiple repositories
pytest --skip-redalyc --skip-scielo

# Using comma-separated list
pytest --skip-repos redalyc,scielo,biorxiv
```

---

## Strategy 4: Enhanced Skip Decorators

**Approach**: Extend existing skip decorators to check configuration.

**Pros**:
- Works with existing decorator pattern
- Can check both connectivity AND configuration
- Flexible per-test control

**Cons**:
- Need to apply decorators to all tests
- More verbose than markers

**Implementation**:

1. Update `tests/test_utils.py`:
```python
import os
import pytest

def skip_if_repo_disabled(repo_name):
    """
    Decorator to skip tests if repository is disabled via config.
    
    Usage:
        @skip_if_repo_disabled("redalyc")
        def test_redalyc_functionality():
            ...
    """
    def decorator(test_func):
        def wrapper(*args, **kwargs):
            # Check environment variable
            env_var = f"SKIP_{repo_name.upper()}"
            if os.getenv(env_var, "").lower() in ("1", "true", "yes"):
                pytest.skip(f"Skipping {repo_name} tests ({env_var}=1)")
            
            # Check pytest config (if using Strategy 3)
            # This would require accessing pytest config, which is complex in decorators
            
            return test_func(*args, **kwargs)
        return wrapper
    return decorator

# Convenience decorators
skip_if_redalyc_disabled = lambda func: skip_if_repo_disabled("redalyc")(func)
skip_if_scielo_disabled = lambda func: skip_if_repo_disabled("scielo")(func)
skip_if_biorxiv_disabled = lambda func: skip_if_repo_disabled("biorxiv")(func)
```

2. Usage in tests:
```python
@skip_if_redalyc_down()
@skip_if_redalyc_disabled
def test_redalyc_search():
    ...
```

---

## Strategy 5: Test File Organization with Path Filtering

**Approach**: Organize tests by repository in subdirectories, use path filtering.

**Pros**:
- Clear organization
- Easy to skip entire directories
- No code changes needed in test files

**Cons**:
- Requires reorganizing test files
- Less granular control

**Implementation**:

1. Reorganize test structure:
```
tests/
  test_core.py
  test_declarative_framework.py
  repositories/
    redalyc/
      test_redalyc_*.py
    scielo/
      test_scielo_*.py
    biorxiv/
      test_biorxiv_*.py
```

2. Usage:
```bash
# Skip Redalyc tests
pytest --ignore=tests/repositories/redalyc

# Skip multiple repositories
pytest --ignore=tests/repositories/redalyc --ignore=tests/repositories/scielo

# Run only core tests
pytest tests/ --ignore=tests/repositories
```

---

## Strategy 6: Hybrid Approach (Recommended for Production)

**Approach**: Combine Strategy 1 (markers) with Strategy 2 (environment variables) for maximum flexibility.

**Pros**:
- Best of both worlds
- Works in CI/CD (env vars) and local development (markers)
- Backward compatible

**Cons**:
- Slightly more complex implementation

**Implementation**:

1. Update `conftest.py`:
```python
import os
import pytest

def pytest_collection_modifyitems(config, items):
    """Skip tests based on markers and environment variables."""
    skip_repos = []
    
    # Check environment variables
    if os.getenv("SKIP_REDALYC", "").lower() in ("1", "true", "yes"):
        skip_repos.append("redalyc")
    if os.getenv("SKIP_SCIELO", "").lower() in ("1", "true", "yes"):
        skip_repos.append("scielo")
    if os.getenv("SKIP_BIORXIV", "").lower() in ("1", "true", "yes"):
        skip_repos.append("biorxiv")
    
    # Check command-line marker expressions
    marker_expr = config.getoption("-m", default="")
    if marker_expr and "not redalyc" in marker_expr:
        skip_repos.append("redalyc")
    if marker_expr and "not scielo" in marker_expr:
        skip_repos.append("scielo")
    if marker_expr and "not biorxiv" in marker_expr:
        skip_repos.append("biorxiv")
    
    # Skip tests
    for item in items:
        for repo in skip_repos:
            # Check by marker
            if hasattr(item, 'pytestmark'):
                for mark in item.pytestmark:
                    if mark.name == repo:
                        item.add_marker(
                            pytest.mark.skip(reason=f"Skipping {repo} tests")
                        )
            # Check by nodeid
            if repo in item.nodeid.lower():
                item.add_marker(
                    pytest.mark.skip(reason=f"Skipping {repo} tests")
                )
```

---

## Comparison Matrix

| Strategy | Ease of Use | CI/CD Friendly | Flexibility | Implementation Effort |
|----------|-------------|----------------|-------------|----------------------|
| 1. Markers | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Low |
| 2. Env Vars | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Low |
| 3. Custom Options | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | Medium |
| 4. Decorators | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Medium |
| 5. File Organization | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | High (reorg) |
| 6. Hybrid | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Medium |

---

## Recommendation

**Start with Strategy 1 (Markers)** - it's the simplest and most pytest-idiomatic approach. If you need CI/CD integration, add Strategy 2 (Environment Variables) for a hybrid solution.

**Quick Start with Strategy 1**:
1. Add markers to `pytest.ini`
2. Mark repository-specific tests
3. Use `pytest -m "not redalyc"` to skip

**For CI/CD, add Strategy 2**:
1. Add environment variable checks to `conftest.py`
2. Set `SKIP_REDALYC=1` in CI/CD config
3. Tests automatically skip
