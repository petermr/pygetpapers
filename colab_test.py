#!/usr/bin/env python3
"""
Pygetpapers Colab Test Script

This script demonstrates how to use pygetpapers from Python code
using the new run_pygetpapers function.
"""

import os
import sys


def test_installation():
    """Test if pygetpapers is properly installed."""
    print("🔍 Testing pygetpapers installation...")

    try:
        import pygetpapers

        print(
            f"✅ pygetpapers imported successfully (version: {pygetpapers.__version__})"
        )
        return True
    except ImportError as e:
        print(f"❌ Failed to import pygetpapers: {e}")
        return False


def test_run_pygetpapers():
    """Test the new run_pygetpapers function."""
    print("\n🧪 Testing run_pygetpapers function...")

    try:
        from pygetpapers import run_pygetpapers

        print("✅ run_pygetpapers function imported successfully")

        # Test 1: Simple query with noexecute
        print("\n📝 Test 1: Simple query with noexecute")
        cmd = "pygetpapers -q wombat -n"
        print(f"Running: {cmd}")
        result = run_pygetpapers(cmd)

        if result["success"]:
            print("✅ Command executed successfully")
            print(f"Output directory: {result.get('output_directory', 'N/A')}")
            if result.get("stdout"):
                print("STDOUT:")
                print(
                    result["stdout"][:500] + "..."
                    if len(result["stdout"]) > 500
                    else result["stdout"]
                )
        else:
            print(f"❌ Command failed: {result.get('error', 'Unknown error')}")
            if result.get("stderr"):
                print("STDERR:")
                print(result["stderr"])

        # Test 2: Query with XML download and limit
        print("\n📝 Test 2: Query with XML download and limit")
        cmd = "pygetpapers -q 'climate change' -x -k 5"
        print(f"Running: {cmd}")
        result = run_pygetpapers(cmd)

        if result["success"]:
            print("✅ Command executed successfully")
            print(f"Output directory: {result.get('output_directory', 'N/A')}")
            if result.get("stdout"):
                print("STDOUT:")
                print(
                    result["stdout"][:500] + "..."
                    if len(result["stdout"]) > 500
                    else result["stdout"]
                )
        else:
            print(f"❌ Command failed: {result.get('error', 'Unknown error')}")
            if result.get("stderr"):
                print("STDERR:")
                print(result["stderr"])

        return True

    except Exception as e:
        print(f"❌ Failed to test run_pygetpapers: {e}")
        return False


def demonstrate_usage():
    """Demonstrate various usage examples."""
    print("\n📚 Usage Examples:")
    print("=" * 50)

    examples = [
        {
            "description": "Simple query with noexecute (just count results)",
            "command": "pygetpapers -q 'artificial intelligence' -n",
            "explanation": "Searches for 'artificial intelligence' and reports how many papers match, but doesn't download anything",
        },
        {
            "description": "Download XML fulltext with limit",
            "command": "pygetpapers -q 'machine learning' -x -k 10",
            "explanation": "Downloads XML fulltext for up to 10 papers about 'machine learning'",
        },
        {
            "description": "Download PDFs from Europe PMC",
            "command": "pygetpapers -q 'bioinformatics' -p -k 5 --api europe_pmc",
            "explanation": "Downloads PDFs for up to 5 papers about 'bioinformatics' from Europe PMC",
        },
        {
            "description": "Search bioRxiv with date range",
            "command": "pygetpapers -q '2024-01-01/2024-12-31' --api biorxiv -x -k 20",
            "explanation": "Downloads XML for up to 20 papers from bioRxiv published in 2024",
        },
        {
            "description": "Create datatables output",
            "command": "pygetpapers -q 'genomics' -x -k 15 --datatables",
            "explanation": "Downloads XML and creates interactive datatables HTML files",
        },
    ]

    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['description']}")
        print(f"   Command: {example['command']}")
        print(f"   Explanation: {example['explanation']}")

    print("\n💡 To run any of these examples:")
    print("   from pygetpapers import run_pygetpapers")
    print("   result = run_pygetpapers('your_command_here')")
    print("   print(result)")


def main():
    """Main test function."""
    print("🚀 Pygetpapers Python Interface Test")
    print("=" * 50)

    # Test installation
    if not test_installation():
        print("\n❌ Installation test failed. Please install pygetpapers first.")
        return False

    # Test run_pygetpapers function
    if not test_run_pygetpapers():
        print("\n❌ run_pygetpapers test failed.")
        return False

    # Demonstrate usage
    demonstrate_usage()

    print("\n🎉 All tests completed!")
    print("\n📖 For more information:")
    print("   - Read GETTING_STARTED.md")
    print("   - Check QUICK_REFERENCE.md")
    print("   - Run: pygetpapers --help")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
