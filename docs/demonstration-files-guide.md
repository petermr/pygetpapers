# Demonstration Files Guide

## Overview

Demonstration files are valuable for documentation, examples, and testing. This guide outlines best practices for including demonstration files in the repository while maintaining good performance and avoiding push issues.

## Guidelines

### ✅ Encouraged: Small Demonstration Files

**Size Limits:**
- **Individual files**: < 1MB each
- **Total demo directory**: < 10MB
- **PDFs**: < 5MB each

**Examples of Good Demo Files:**
- Small sample data files (< 100KB)
- Example configuration files
- Sample output files
- Small test documents
- Screenshots and diagrams

### ⚠️ Use Caution: Medium Files

**Size Limits:**
- **Individual files**: 1MB - 5MB
- **Should be documented** if included

**Examples:**
- Larger sample PDFs (if essential for documentation)
- Sample datasets (if small enough)
- Example outputs with more content

### ❌ Avoid: Large Files

**Size Limits:**
- **Individual files**: > 10MB (blocked by pre-commit hook)
- **PDFs**: > 5MB (warning from pre-commit hook)

**Examples to Avoid:**
- Full research papers
- Large datasets
- High-resolution images
- Video files
- Archive files

## Tools and Automation

### Pre-commit Hook

Automatically runs on every commit to:
- Block files > 10MB
- Warn about PDFs > 5MB
- Report demonstration directory sizes

### Demonstration File Checker

Run manually to audit demonstration files:
```bash
./scripts/check_demo_files.sh
```

### Manual Checks

Before committing demonstration files:
```bash
# Check file sizes
find . -name "*.pdf" -size +5M
find . -type f -size +10M

# Check directory sizes
du -sh *_research_output/ *_demo_output/ demo_*/
```

## Best Practices

### 1. Keep Files Small
- Use compressed formats when possible
- Include only essential content
- Consider using external links for large files

### 2. Document Large Files
If you must include larger files:
- Add a README explaining why they're needed
- Document the file size and purpose
- Consider using git-lfs for very large files

### 3. Use Appropriate Directories
- `examples/` - for small example files
- `tests/data/` - for test data files
- `docs/` - for documentation examples

### 4. Regular Cleanup
- Remove outdated demonstration files
- Archive old examples if needed
- Keep only current, relevant examples

## Examples

### Good Demonstration Structure
```
examples/
├── small_sample.pdf          # 50KB - good
├── sample_config.json        # 2KB - good
├── output_example.html       # 15KB - good
└── README.md                 # Documents the examples
```

### Avoid This Structure
```
examples/
├── large_research_paper.pdf  # 25MB - too large
├── full_dataset.zip          # 100MB - too large
└── high_res_screenshot.png   # 8MB - too large
```

## Troubleshooting

### Pre-commit Hook Failing
If the pre-commit hook blocks your commit:
1. Check which files are too large
2. Consider if they're really needed
3. Use external storage if necessary
4. Document why large files are essential

### Push Issues
If you encounter push problems:
1. Check repository size: `du -sh .git`
2. Look for large files: `find . -size +10M`
3. Use the demonstration file checker
4. Consider using git-lfs for large files

## External Resources

For large files that can't be included:
- **GitHub Releases**: For downloadable assets
- **External Storage**: Google Drive, Dropbox, etc.
- **Data Repositories**: Zenodo, Figshare, etc.
- **Documentation**: Link to external sources

## Summary

Demonstration files are valuable when they're:
- ✅ Small (< 1MB each)
- ✅ Well-documented
- ✅ Essential for understanding
- ✅ Regularly maintained

Avoid including files that are:
- ❌ Large (> 10MB)
- ❌ Unnecessary
- ❌ Outdated
- ❌ Duplicated elsewhere 