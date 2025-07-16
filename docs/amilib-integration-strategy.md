# Amilib Integration Strategy

## Overview
This document outlines the strategy for integrating amilib (a sibling library with PDF, HTML, and Wikimedia parsing capabilities) with pygetpapers v2.0.

## Background

### Amilib Capabilities
Amilib provides advanced processing capabilities for:
- PDF parsing and text extraction
- HTML processing and cleaning
- Wikimedia content extraction
- Structured data extraction
- Content analysis and transformation

### Integration Challenge
The challenge was to integrate amilib's capabilities without:
- Creating tight coupling between libraries
- Complicating pygetpapers' core functionality
- Requiring all users to install amilib
- Compromising pygetpapers' simplicity

## Architectural Decision: Optional Post-Processing Enhancement

### Core Decision
**Treat amilib as an optional post-processing enhancement rather than a core dependency**

### Rationale

#### 1. Maintain Core Simplicity
- Pygetpapers remains focused on paper discovery and download
- Core functionality doesn't require amilib
- Users can start with basic functionality and add processing later

#### 2. Independent Development Cycles
- Both libraries can evolve independently
- Changes in amilib don't break pygetpapers
- Each library can optimize for its specific use case

#### 3. User Choice
- Users can choose their processing depth
- Lightweight users aren't forced to install heavy dependencies
- Advanced users can leverage full amilib capabilities

#### 4. File System as Integration Boundary
- Simple, reliable integration mechanism
- No complex API coupling
- Easy to debug and troubleshoot
- Supports batch processing workflows

## Implementation Strategy

### 1. File System Integration
```
pygetpapers_output/
├── repository/
│   ├── query/
│   │   ├── paper_id/
│   │   │   ├── metadata.json
│   │   │   ├── fulltext.pdf
│   │   │   ├── fulltext.html
│   │   │   └── processed/
│   │   │       ├── extracted_text.txt
│   │   │       ├── structured_data.json
│   │   │       └── analysis_results.json
```

### 2. Integration Endpoints
Define clear integration points between the libraries:

#### Input Interface
- Pygetpapers provides standardized file structure
- Consistent metadata format (JSON)
- Predictable file naming conventions
- Clear content type indicators

#### Output Interface
- Amilib processes files in place
- Creates `processed/` subdirectories
- Maintains original files
- Provides processing metadata

### 3. Configuration-Driven Integration
```yaml
# Example integration configuration
amilib_integration:
  enabled: true
  processing_pipeline:
    - pdf_text_extraction
    - html_cleaning
    - metadata_enhancement
  output_formats:
    - txt
    - json
    - html
  batch_size: 100
```

## Integration Workflows

### 1. Basic Workflow (Pygetpapers Only)
```bash
pygetpapers --query "climate change" --repository biorxiv --limit 10
```
- Downloads papers to file system
- Creates metadata.json files
- Provides basic content access

### 2. Enhanced Workflow (With Amilib)
```bash
# Step 1: Download papers
pygetpapers --query "climate change" --repository biorxiv --limit 10

# Step 2: Process with amilib
amilib_process --input-dir pygetpapers_output --pipeline full
```
- Downloads papers (same as basic workflow)
- Processes PDFs for text extraction
- Enhances metadata with extracted information
- Creates structured data outputs

### 3. Integrated Workflow (Future)
```bash
pygetpapers --query "climate change" --repository biorxiv --limit 10 --post-process amilib
```
- Single command execution
- Automatic amilib processing
- Unified output structure

## Technical Implementation

### 1. Schema Definition
Define clear schemas for integration:

#### Pygetpapers Output Schema
```json
{
  "paper_id": "string",
  "repository": "string",
  "query": "string",
  "download_timestamp": "ISO8601",
  "files": {
    "metadata": "metadata.json",
    "pdf": "fulltext.pdf",
    "html": "fulltext.html"
  },
  "processing_status": {
    "amilib_processed": false,
    "processing_timestamp": null
  }
}
```

#### Amilib Processing Schema
```json
{
  "processing_metadata": {
    "amilib_version": "string",
    "processing_timestamp": "ISO8601",
    "pipeline_steps": ["step1", "step2"],
    "processing_status": "success|failed|partial"
  },
  "extracted_content": {
    "text": "extracted_text.txt",
    "structured_data": "structured_data.json",
    "analysis": "analysis_results.json"
  }
}
```

### 2. Error Handling
- Graceful degradation when amilib unavailable
- Clear error messages for missing dependencies
- Fallback to basic pygetpapers functionality
- Processing status tracking

### 3. Performance Considerations
- Batch processing capabilities
- Incremental processing (skip already processed files)
- Parallel processing where appropriate
- Resource usage monitoring

## Future Evolution

### Phase 1: File System Integration (Current)
- Basic file system integration
- Manual workflow coordination
- Clear separation of concerns

### Phase 2: Enhanced Integration (Future)
- Optional CLI integration
- Configuration-driven processing
- Unified output formats

### Phase 3: Deep Integration (Future)
- Shared configuration management
- Integrated processing pipelines
- Unified user interface

## Benefits of This Approach

### 1. Modularity
- Each library maintains its core purpose
- Easy to understand and maintain
- Clear boundaries and responsibilities

### 2. Flexibility
- Users can choose their processing depth
- Supports various use cases
- Enables experimentation and customization

### 3. Reliability
- Simple integration mechanism
- Easy to debug and troubleshoot
- Robust error handling

### 4. Scalability
- Supports large-scale processing
- Enables batch operations
- Efficient resource utilization

## Migration Path

### For Existing Users
- No breaking changes to pygetpapers
- Gradual adoption of amilib features
- Backward compatibility maintained

### For New Users
- Start with basic pygetpapers functionality
- Add amilib processing as needed
- Clear upgrade path available

## Conclusion

The file system-based integration strategy provides a robust, flexible, and maintainable approach to combining pygetpapers and amilib capabilities. This approach:

- Maintains the simplicity of pygetpapers
- Provides powerful processing capabilities through amilib
- Enables independent development and evolution
- Supports various user needs and use cases

The clear separation of concerns and file system integration boundary ensures that both libraries can evolve independently while providing users with powerful, integrated workflows when needed. 