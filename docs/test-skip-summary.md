# Test Skipping Strategies - Summary

## ✅ Implementation Status

I've implemented **Strategy 6 (Hybrid Approach)** which combines:
- ✅ Pytest markers for command-line filtering
- ✅ Environment variables for CI/CD
- ✅ Auto-detection of repository tests by file name

## Quick Start

### Option 1: Command-Line (Pytest Markers)

```bash
# Skip Redalyc tests
pytest -m "not redalyc"

# Skip multiple repositories  
pytest -m "not redalyc and not scielo"

# Skip all repository tests
pytest -m "not redalyc and not scielo and not biorxiv"
```

### Option 2: Environment Variables (CI/CD)

```bash
# Skip Redalyc tests
SKIP_REDALYC=1 pytest

# Skip multiple repositories
SKIP_REDALYC=1 SKIP_SCIELO=1 SKIP_BIORXIV=1 pytest
```

### Option 3: Combined

```bash
# Environment variables + markers
SKIP_REDALYC=1 pytest -m "not scielo"  # Skips both Redalyc and SciELO
```

## What Was Changed

1. **pytest.ini**: Added `scielo` and `biorxiv` markers
2. **tests/conftest.py**: 
   - Added environment variable support (SKIP_REDALYC, SKIP_SCIELO, SKIP_BIORXIV)
   - Auto-detects and marks tests by file name
   - Skips tests based on configuration

## How It Works

### Auto-Detection

Tests are automatically marked based on their file/function names:
- Files containing `redalyc` → `@pytest.mark.redalyc`
- Files containing `scielo` → `@pytest.mark.scielo`  
- Files containing `biorxiv` → `@pytest.mark.biorxiv`

### Manual Marking (Optional)

You can also manually mark tests:

```python
import pytest

@pytest.mark.redalyc
def test_custom_redalyc_test():
    ...
```

### Skipping Logic

1. **Environment variables** are checked first (for CI/CD)
2. **Pytest markers** (`-m "not redalyc"`) are handled by pytest's built-in filtering
3. Tests matching skipped repositories are automatically skipped

## Examples

### Local Development

```bash
# Fast test run (skip external repos)
pytest -m "not redalyc and not scielo and not biorxiv"

# Test only one repository
pytest -m "redalyc"
```

### CI/CD Pipeline

```yaml
# GitHub Actions example
- name: Run core tests
  env:
    SKIP_REDALYC: 1
    SKIP_SCIELO: 1
    SKIP_BIORXIV: 1
  run: pytest
```

### Makefile

```makefile
test-core:
	SKIP_REDALYC=1 SKIP_SCIELO=1 SKIP_BIORXIV=1 pytest

test-repos:
	pytest -m "redalyc or scielo or biorxiv"
```

## Testing the Implementation

```bash
# Verify markers are registered
pytest --markers | grep -E "(redalyc|scielo|biorxiv)"

# Test skipping Redalyc tests
SKIP_REDALYC=1 pytest --collect-only | grep -i redalyc

# Test marker filtering
pytest -m "not redalyc" --collect-only -q
```

## Files Modified

- `pytest.ini` - Added repository markers
- `tests/conftest.py` - Added skipping logic
- `docs/test-skip-strategies.md` - Strategy documentation
- `docs/test-skip-implementation-guide.md` - Implementation guide
- `docs/test-skip-usage-examples.md` - Usage examples

## Next Steps (Optional)

1. **Mark specific tests manually** if auto-detection misses any
2. **Add to CI/CD** using environment variables
3. **Create Makefile targets** for common test scenarios
4. **Document in README** for team members

## Support

For more details, see:
- `docs/test-skip-strategies.md` - All available strategies
- `docs/test-skip-implementation-guide.md` - Step-by-step guide
- `docs/test-skip-usage-examples.md` - Usage examples
