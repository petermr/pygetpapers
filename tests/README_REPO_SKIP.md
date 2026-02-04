# Repository Test Skipping Configuration

## Quick Start

Repository tests are controlled via `tests/test_repos_config.ini`.

**By default, all repository tests are SKIPPED** (redalyc, scielo, biorxiv).

## Configuration File

**File**: `tests/test_repos_config.ini`

```ini
[test_repositories]
skip_redalyc = true   # Skip Redalyc tests
skip_scielo = true    # Skip SciELO tests
skip_biorxiv = true   # Skip BioRxiv tests
```

## Usage

### Enable a Repository Test

Edit `test_repos_config.ini`:
```ini
skip_redalyc = false  # Enable Redalyc tests
```

### Run Tests

```bash
# Run with config file settings (default: skips all repos)
pytest

# Override config with pytest markers
pytest -m "not redalyc"  # Skip Redalyc (overrides config)
pytest -m redalyc         # Run only Redalyc tests (overrides config)
```

## Priority Order

1. **Config file** (`test_repos_config.ini`) - default/base settings
2. **Pytest markers** (`-m "not redalyc"`) - command-line filtering

## Examples

```bash
# Default: All repository tests skipped
pytest

# Enable Redalyc via config file
# Edit test_repos_config.ini: skip_redalyc = false
pytest

# Run Redalyc tests via marker (overrides config)
pytest -m redalyc

# Skip Redalyc via marker (overrides config)
pytest -m "not redalyc"
```

## Current Default Settings

All repository tests are **skipped by default**:
- ✅ Redalyc tests: **SKIPPED**
- ✅ SciELO tests: **SKIPPED**
- ✅ BioRxiv tests: **SKIPPED**

This ensures fast test runs without external dependencies.
