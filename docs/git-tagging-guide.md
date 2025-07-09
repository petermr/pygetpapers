# Git Tagging Guide for Pygetpapers

## Overview

This guide outlines the git tagging strategy for the pygetpapers project, ensuring consistent versioning and feature tracking.

## Tagging Scheme

### 1. Semantic Versioning (Release Tags)
```
v<major>.<minor>.<patch>
```

**Examples:**
- `v1.2.4` - Current stable release
- `v1.3.0` - New minor version with features
- `v2.0.0` - Major version with breaking changes

**When to use:**
- **Patch (v1.2.4 → v1.2.5)**: Bug fixes, minor improvements
- **Minor (v1.2.4 → v1.3.0)**: New features, backward compatible
- **Major (v1.2.4 → v2.0.0)**: Breaking changes, major rewrites

### 2. Feature Tags
```
feature/<feature-name>
```

**Examples:**
- `feature/html-text-search`
- `feature/dot-file-toggle`
- `feature/xml2html-interface`

**When to use:**
- Mark completion of major features
- Reference specific feature implementations
- Track feature development history

### 3. Milestone Tags
```
milestone/<milestone-name>
```

**Examples:**
- `milestone/file-browser-complete`
- `milestone/v1.0-release`
- `milestone/api-complete`

**When to use:**
- Mark major project milestones
- Significant architectural achievements
- Completion of major subsystems

### 4. Pre-release Tags
```
v<version>-alpha.<number>
v<version>-beta.<number>
v<version>-rc.<number>
```

**Examples:**
- `v1.3.0-alpha.1`
- `v1.3.0-beta.2`
- `v1.3.0-rc.1`

**When to use:**
- Alpha: Early development, incomplete features
- Beta: Feature complete, testing phase
- RC: Release candidate, final testing

## Creating Tags

### Annotated Tags (Recommended)
```bash
# Release tag with detailed message
git tag -a v1.3.0 -m "Release v1.3.0: Enhanced File Browser

Major Features:
- HTML Text Search
- Dot File Toggle
- XML2HTML Interface

Breaking Changes: None
Compatibility: Fully backward compatible"

# Feature tag
git tag -a feature/html-text-search -m "Feature: HTML Text Search in File Browser

- Search through HTML files with snippet display
- Highlighted search results
- File navigation from search results

Implementation:
- _search_html_files() method
- HTML tag stripping
- Context snippet generation"

# Milestone tag
git tag -a milestone/file-browser-complete -m "Milestone: Complete File Browser Implementation

This milestone represents the completion of a comprehensive file browser system:

Core Features:
- Universal Browser
- Corpus Browser
- HTML Text Search
- Dot File Toggle
- File Viewer

Technical Achievements:
- Dual-mode browser architecture
- Real-time search and filtering
- Comprehensive error handling"
```

### Lightweight Tags (Quick reference)
```bash
git tag v1.3.0
```

## Tag Management

### Listing Tags
```bash
# List all tags
git tag -l

# List tags matching pattern
git tag -l "v1.*"
git tag -l "feature/*"

# List tags with messages
git tag -n
```

### Viewing Tag Details
```bash
# Show tag details
git show v1.3.0

# Show tag message only
git tag -l -n9 v1.3.0
```

### Pushing Tags
```bash
# Push specific tag
git push origin v1.3.0

# Push all tags
git push origin --tags
```

### Deleting Tags
```bash
# Delete local tag
git tag -d v1.3.0

# Delete remote tag
git push origin --delete v1.3.0
```

## Tagging Workflow

### 1. Feature Development
1. Develop feature in feature branch
2. Test thoroughly
3. Create feature tag when complete
4. Merge to main branch

### 2. Release Preparation
1. Ensure all features are complete
2. Update version numbers
3. Update documentation
4. Create release tag
5. Push tags to remote

### 3. Hotfix Process
1. Create hotfix branch from latest release tag
2. Fix the issue
3. Create patch version tag
4. Merge to main and release branches

## Current Tags

### Release Tags
- `v1.2.4` - Previous stable release
- `v1.3.0` - Enhanced File Browser release

### Feature Tags
- `feature/html-text-search` - HTML text search functionality
- `feature/dot-file-toggle` - Dot file visibility toggle
- `feature/xml2html-interface` - XML to HTML conversion interface

### Milestone Tags
- `milestone/file-browser-complete` - Complete file browser implementation

## Best Practices

1. **Always use annotated tags** for releases and features
2. **Write descriptive messages** explaining what the tag represents
3. **Include breaking changes** in release tag messages
4. **Tag features when complete**, not during development
5. **Use consistent naming** conventions
6. **Push tags promptly** after creation
7. **Document major changes** in tag messages
8. **Review tags before release** to ensure accuracy

## Automation

Consider automating tag creation with:
- GitHub Actions for automated releases
- Pre-commit hooks for version checking
- CI/CD pipelines for tag validation

## Future Considerations

- Consider using conventional commits for automated versioning
- Implement automated changelog generation from tags
- Use semantic-release for automated version management
- Consider using GitHub releases for better tag management 