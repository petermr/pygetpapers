# Repository Test Skipping Configuration Guide

## Overview

Repository-specific tests can be skipped using a configuration file (`tests/test_repos_config.ini`). This allows you to control which repository tests run without modifying code or command-line arguments.

## Configuration File

**Location**: `tests/test_repos_config.ini`

**Format**:
```ini
[test_repositories]
# Set to 'true' or '1' to skip tests for that repository
# Set to 'false' or '0' to run tests for that repository

skip_redalyc = true
skip_scielo = true
skip_biorxiv = true
```

## Priority Order

Settings are applied in this order (later settings override earlier ones):

1. **Config file** (`test_repos_config.ini`) - Default/base settings
2. **Pytest markers** (`-m "not redalyc"`) - Command-line filtering

## Usage Examples

### Using Config File Only

Edit `tests/test_repos_config.ini`:
```ini
[test_repositories]
skip_redalyc = true
skip_scielo = true
skip_biorxiv = false  # Run BioRxiv tests
```

Then run:
```bash
pytest  # Automatically skips Redalyc and SciELO, runs BioRxiv
```

### Override with Pytest Markers

```bash
# Config file settings + marker filtering
pytest -m "not redalyc"  # Skips Redalyc (even if config says run)
```

## Common Scenarios

### Scenario 1: Skip All Repository Tests (Default)

```ini
[test_repositories]
skip_redalyc = true
skip_scielo = true
skip_biorxiv = true
```

```bash
pytest  # Only runs core tests
```

### Scenario 2: Run Only One Repository

```ini
[test_repositories]
skip_redalyc = true
skip_scielo = true
skip_biorxiv = false  # Only run BioRxiv tests
```

```bash
pytest  # Runs BioRxiv tests only
```

### Scenario 3: Run Specific Repository Tests

Use pytest markers to run only specific repository tests:

```bash
# Run only Redalyc tests (ignores config file)
pytest -m redalyc

# Run only SciELO tests
pytest -m scielo

# Run all repository tests
pytest -m "redalyc or scielo or biorxiv"
```

## Editing the Config File

The config file uses standard INI format:

```ini
[test_repositories]
# Boolean values: true, false, 1, 0, yes, no
skip_redalyc = true
skip_scielo = false
skip_biorxiv = 1  # Also accepts 1/0
```

**Valid values for `true`**: `true`, `1`, `yes`  
**Valid values for `false`**: `false`, `0`, `no`

## Default Configuration

By default, all repository tests are **skipped**:
- `skip_redalyc = true`
- `skip_scielo = true`
- `skip_biorxiv = true`

This ensures fast test runs without external dependencies.

## Enabling Repository Tests

To enable repository tests, edit `tests/test_repos_config.ini`:

```ini
[test_repositories]
skip_redalyc = false  # Enable Redalyc tests
skip_scielo = false   # Enable SciELO tests
skip_biorxiv = false  # Enable BioRxiv tests
```

Or use pytest markers to override config file settings:
```bash
# Run Redalyc tests even if config says skip
pytest -m redalyc

# Run all repository tests
pytest -m "redalyc or scielo or biorxiv"
```

## Verification

Check which tests will be skipped:
```bash
# Show what will be skipped
pytest --collect-only | grep -i "skip"

# Test with config
pytest --collect-only -q | head -20
```

## File Location

The config file is located at:
- **Path**: `tests/test_repos_config.ini`
- **Relative to project root**: `tests/test_repos_config.ini`

If the file doesn't exist, defaults are used (all repositories enabled for testing).
