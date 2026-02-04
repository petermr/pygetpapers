# Usage Examples: Skipping Repository Tests

## Quick Reference

### Command-Line Usage (Pytest Markers)

```bash
# Skip all Redalyc tests
pytest -m "not redalyc"

# Skip SciELO tests
pytest -m "not scielo"

# Skip BioRxiv tests
pytest -m "not biorxiv"

# Skip multiple repositories
pytest -m "not redalyc and not scielo"
pytest -m "not redalyc and not scielo and not biorxiv"

# Run only core tests (no repository tests)
pytest -m "not redalyc and not scielo and not biorxiv"

# Run only Redalyc tests
pytest -m "redalyc"

# Run Redalyc and SciELO, skip BioRxiv
pytest -m "redalyc or scielo"
```

### Environment Variable Usage (CI/CD)

```bash
# Skip Redalyc tests
SKIP_REDALYC=1 pytest

# Skip multiple repositories
SKIP_REDALYC=1 SKIP_SCIELO=1 pytest

# Skip all repository tests
SKIP_REDALYC=1 SKIP_SCIELO=1 SKIP_BIORXIV=1 pytest

# Combine with other pytest options
SKIP_REDALYC=1 pytest -v --durations=10
```

### Combined Usage

```bash
# Use both markers and env vars (env vars take precedence)
SKIP_REDALYC=1 pytest -m "not scielo"  # Skips both Redalyc and SciELO
```

---

## CI/CD Integration Examples

### GitHub Actions

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run core tests only
        env:
          SKIP_REDALYC: 1
          SKIP_SCIELO: 1
          SKIP_BIORXIV: 1
        run: pytest
      
      - name: Run repository tests (separate job)
        env:
          SKIP_REDALYC: 0
        run: pytest -m "redalyc or scielo or biorxiv"
```

### GitLab CI

```yaml
test:core:
  script:
    - SKIP_REDALYC=1 SKIP_SCIELO=1 SKIP_BIORXIV=1 pytest

test:repositories:
  script:
    - pytest -m "redalyc or scielo or biorxiv"
  only:
    - schedules  # Run repository tests on schedule
```

### Jenkins

```groovy
pipeline {
    agent any
    stages {
        stage('Core Tests') {
            steps {
                sh 'SKIP_REDALYC=1 SKIP_SCIELO=1 SKIP_BIORXIV=1 pytest'
            }
        }
        stage('Repository Tests') {
            when {
                expression { env.BRANCH_NAME == 'main' }
            }
            steps {
                sh 'pytest -m "redalyc or scielo or biorxiv"'
            }
        }
    }
}
```

---

## Common Workflows

### Local Development

```bash
# Quick test run (skip slow external repos)
pytest -m "not redalyc and not scielo and not biorxiv" -v

# Test specific repository
pytest -m "redalyc" -v

# Test everything except one repository
pytest -m "not redalyc" --durations=10
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Run fast tests only
SKIP_REDALYC=1 SKIP_SCIELO=1 SKIP_BIORXIV=1 pytest -m "not slow"
```

### Makefile Integration

```makefile
.PHONY: test test-core test-repos test-redalyc

test:
	pytest

test-core:
	SKIP_REDALYC=1 SKIP_SCIELO=1 SKIP_BIORXIV=1 pytest

test-repos:
	pytest -m "redalyc or scielo or biorxiv"

test-redalyc:
	pytest -m "redalyc"

test-scielo:
	pytest -m "scielo"

test-biorxiv:
	pytest -m "biorxiv"
```

---

## Advanced: Conditional Skipping

You can also create custom skip conditions:

```python
# In conftest.py or test file
import os
import pytest

def pytest_collection_modifyitems(config, items):
    # Skip repository tests if running in CI without network
    if os.getenv("CI") and not os.getenv("ALLOW_EXTERNAL_TESTS"):
        for item in items:
            if any(repo in item.nodeid.lower() for repo in ["redalyc", "scielo", "biorxiv"]):
                item.add_marker(
                    pytest.mark.skip(reason="External repository tests disabled in CI")
                )
```

---

## Troubleshooting

### Check which tests are being skipped

```bash
# Show skipped tests
pytest -v -rs

# Show only skipped tests
pytest -v -rs -k "skip"
```

### Verify markers are working

```bash
# List all markers
pytest --markers

# Show which tests have which markers
pytest -m redalyc --collect-only
```

### Debug marker expressions

```bash
# Test marker expression
pytest -m "not redalyc" --collect-only -q
```
