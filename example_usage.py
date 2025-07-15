#!/usr/bin/env python3
"""
Example usage of pygetpapers Python interface

This script demonstrates how to use the new run_pygetpapers function
to execute pygetpapers commands directly from Python code.
"""

from pygetpapers import run_pygetpapers

def main():
    """Demonstrate the new Python interface."""
    print("🚀 Pygetpapers Python Interface Example")
    print("=" * 50)
    
    # Example 1: Simple query with noexecute
    print("\n📝 Example 1: Simple query with noexecute")
    cmd = "pygetpapers -q wombat -n"
    print(f"Command: {cmd}")
    
    result = run_pygetpapers(cmd)
    print(f"Success: {result['success']}")
    if result['success']:
        print(f"Output directory: {result.get('output_directory', 'N/A')}")
        if result.get('stdout'):
            print("Output:")
            print(result['stdout'][:300] + "..." if len(result['stdout']) > 300 else result['stdout'])
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
    
    # Example 2: Query with XML download and limit
    print("\n📝 Example 2: Query with XML download and limit")
    cmd = "pygetpapers -q wombat -x -k 10"
    print(f"Command: {cmd}")
    
    result = run_pygetpapers(cmd)
    print(f"Success: {result['success']}")
    if result['success']:
        print(f"Output directory: {result.get('output_directory', 'N/A')}")
        if result.get('stdout'):
            print("Output:")
            print(result['stdout'][:300] + "..." if len(result['stdout']) > 300 else result['stdout'])
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
    
    # Example 3: Search bioRxiv with date range
    print("\n📝 Example 3: Search bioRxiv with date range")
    cmd = "pygetpapers -q '2024-01-01/2024-12-31' --api biorxiv -x -k 5"
    print(f"Command: {cmd}")
    
    result = run_pygetpapers(cmd)
    print(f"Success: {result['success']}")
    if result['success']:
        print(f"Output directory: {result.get('output_directory', 'N/A')}")
        if result.get('stdout'):
            print("Output:")
            print(result['stdout'][:300] + "..." if len(result['stdout']) > 300 else result['stdout'])
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
    
    # Example 4: Create datatables output
    print("\n📝 Example 4: Create datatables output")
    cmd = "pygetpapers -q 'machine learning' -x -k 5 --datatables"
    print(f"Command: {cmd}")
    
    result = run_pygetpapers(cmd)
    print(f"Success: {result['success']}")
    if result['success']:
        print(f"Output directory: {result.get('output_directory', 'N/A')}")
        if result.get('stdout'):
            print("Output:")
            print(result['stdout'][:300] + "..." if len(result['stdout']) > 300 else result['stdout'])
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
    
    print("\n🎉 Examples completed!")
    print("\n💡 Key benefits of this interface:")
    print("   - Run pygetpapers commands directly from Python")
    print("   - Capture output and errors programmatically")
    print("   - Integrate with other Python workflows")
    print("   - No need for subprocess calls")

if __name__ == "__main__":
    main() 