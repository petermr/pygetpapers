#!/usr/bin/env python3
"""
Example: Adding a New Repository

This example demonstrates how to add a new repository using the
configuration-driven system. No code required - just configuration!
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def add_new_repository_example():
    """Example of adding a new repository via configuration."""
    
    print("=== Adding a New Repository Example ===")
    print()
    
    # Step 1: Define the repository configuration
    new_repository_config = {
        "name": "Example Repository",
        "description": "An example repository for demonstration",
        "base_url": "https://api.example.com/",
        
        # API Configuration
        "api_client": {
            "type": "requests",
            "base_url": "https://api.example.com/v1/",
            "headers": {
                "User-Agent": "pygetpapers/1.0",
                "Accept": "application/json"
            },
            "rate_limit": 20,
            "timeout": 30
        },
        
        # Response Structure
        "response_structure": {
            "items_path": "data.papers",
            "total_path": "data.total",
            "cursor_path": "data.next_page",
            "paper_key": "id"
        },
        
        # Content Types Supported
        "content_types": ["metadata", "fulltext"],
        
        # Paper Identification
        "paper_key": "id",
        "paper_id_format": "custom_id",
        
        # Query Configuration
        "query_format": "string",
        "supports_filters": True,
        "supports_date_range": True,
        "supports_cursor_pagination": True,
        
        # File Naming
        "file_name": "example_result",
        
        # XML2HTML Support
        "xml2html_supported": False,
        "xml2html_converters": [],
        
        # Rate Limiting
        "rate_limits": {
            "requests_per_minute": 20,
            "delay_between_requests": 3.0
        },
        
        # Security
        "security": {
            "allowed_domains": ["example.com", "api.example.com"],
            "max_file_size": 52428800,  # 50MB
            "timeout": 30
        }
    }
    
    print("Step 1: Repository Configuration")
    print("The configuration above defines a new repository with:")
    print(f"- Name: {new_repository_config['name']}")
    print(f"- API Type: {new_repository_config['api_client']['type']}")
    print(f"- Content Types: {new_repository_config['content_types']}")
    print(f"- Paper Key: {new_repository_config['paper_key']}")
    print()
    
    # Step 2: Add to schema (this would be done by editing the YAML file)
    print("Step 2: Add to Schema")
    print("Add this configuration to config/repository_schema.yaml:")
    print("```yaml")
    print("repositories:")
    print("  example_repo:")
    print("    name: \"Example Repository\"")
    print("    # ... rest of configuration")
    print("```")
    print()
    
    # Step 3: Use the repository
    print("Step 3: Use the Repository")
    print("Once added to the schema, you can use it like this:")
    print("```python")
    print("from pygetpapers.repository_config import create_repository")
    print("")
    print("# Create the repository")
    print("repo = create_repository('example_repo')")
    print("")
    print("# Search for papers")
    print("query_namespace = {")
    print("    'query': 'machine learning',")
    print("    'limit': 10,")
    print("    'filter': None")
    print("}")
    print("repo.noexecute(query_namespace)")
    print("```")
    print()
    
    # Step 4: Show the minimal implementation
    print("Step 4: Minimal Implementation (Optional)")
    print("If you want a custom wrapper class, it's just a few lines:")
    print("```python")
    print("from pygetpapers.repository_config import create_repository")
    print("")
    print("class ExampleRepository:")
    print("    def __init__(self):")
    print("        self.repository = create_repository('example_repo')")
    print("    ")
    print("    def search(self, query, limit=10):")
    print("        query_namespace = {'query': query, 'limit': limit}")
    print("        return self.repository.search_papers(query, limit)")
    print("```")
    print()
    
    print("=== Benefits ===")
    print("✅ No code duplication")
    print("✅ Consistent interface")
    print("✅ Built-in security and rate limiting")
    print("✅ Automatic dependency resolution")
    print("✅ Easy to maintain and extend")
    print("✅ Configuration validation")
    print()

def compare_with_old_approach():
    """Compare the new approach with the old hard-coded approach."""
    
    print("=== Comparison: Old vs New Approach ===")
    print()
    
    print("OLD APPROACH (Hard-coded):")
    print("- Create a new Python file with 200+ lines")
    print("- Implement all API calls manually")
    print("- Handle rate limiting yourself")
    print("- Implement security checks")
    print("- Duplicate common functionality")
    print("- Hard to maintain and extend")
    print()
    
    print("NEW APPROACH (Configuration-driven):")
    print("- Add configuration to YAML file (~50 lines)")
    print("- All API calls handled automatically")
    print("- Built-in rate limiting and security")
    print("- Reuse common functionality")
    print("- Easy to maintain and extend")
    print("- Consistent interface across repositories")
    print()
    
    print("CODE REDUCTION: ~75% less code for new repositories!")
    print()

def show_existing_repositories():
    """Show how to list and use existing repositories."""
    
    print("=== Using Existing Repositories ===")
    print()
    
    try:
        from pygetpapers.repository_config import get_repository_config
        
        config = get_repository_config()
        repositories = config.list_repositories()
        
        print("Available repositories:")
        for repo in repositories:
            repo_config = config.get_repository_config(repo)
            print(f"- {repo}: {repo_config['name']} ({repo_config['description']})")
        
        print()
        print("To use any repository:")
        print("```python")
        print("from pygetpapers.repository_config import create_repository")
        print("")
        print("# Choose any repository")
        print("repo = create_repository('crossref')  # or 'europe_pmc', 'biorxiv', etc.")
        print("")
        print("# Use the same interface for all repositories")
        print("repo.noexecute({'query': 'test', 'limit': 5})")
        print("```")
        print()
        
    except Exception as e:
        print(f"Error loading repositories: {e}")

def main():
    """Run the example."""
    add_new_repository_example()
    compare_with_old_approach()
    show_existing_repositories()
    
    print("=== Summary ===")
    print("The new configuration-driven approach makes adding repositories")
    print("much easier and more maintainable. Instead of writing hundreds")
    print("of lines of code, you just configure the repository in YAML!")
    print()
    print("Ready to add your next repository? 🚀")

if __name__ == "__main__":
    main() 