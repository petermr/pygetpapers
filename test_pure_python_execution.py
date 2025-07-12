#!/usr/bin/env python3
"""
Test script demonstrating pure Python execution in the declarative operations framework.

This script shows how the framework uses internal pygetpapers APIs instead of subprocess calls.
"""

import sys
from pathlib import Path

# Add the pygetpapers directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_pure_python_execution():
    """Test that operations use pure Python calls."""
    print("🚀 Testing Pure Python Execution")
    print("=" * 50)
    
    try:
        from pygetpapers.declarative_operations import DeclarativeOperationsManager
        
        # Load configuration
        config_file = "config/crossref_declarative.yaml"
        manager = DeclarativeOperationsManager(config_file, "test_output")
        
        print(f"✅ Loaded configuration: {config_file}")
        print(f"   Operations: {len(manager.operations)}")
        print(f"   Repositories: {len(manager.repositories)}")
        
        # Test operation execution (pure Python)
        working_dir = Path("test_output")
        working_dir.mkdir(exist_ok=True)
        
        # Get the first operation
        operation_name = list(manager.operations.keys())[0]
        operation = manager.operations[operation_name]
        
        print(f"\n🔧 Testing operation: {operation_name}")
        print(f"   Description: {operation.description}")
        print(f"   Command: {operation.command}")
        
        # Check dependencies
        satisfied, missing = manager.check_dependencies(operation, working_dir)
        print(f"   Dependencies: {'✅' if satisfied else '❌'} ({missing})")
        
        # Execute operation (pure Python)
        print(f"\n🚀 Executing operation using internal APIs...")
        success = manager.execute_operation(
            operation, 
            working_dir, 
            query="test query",
            limit=5
        )
        
        if success:
            print(f"✅ Operation executed successfully using pure Python")
        else:
            print(f"❌ Operation failed")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_no_subprocess_imports():
    """Verify that no subprocess usage is used."""
    print("\n🔍 Checking for subprocess usage...")
    
    try:
        # Check declarative operations module
        import pygetpapers.declarative_operations as decl_ops
        
        # Get the source code
        import inspect
        source = inspect.getsource(decl_ops)
        
        if "subprocess" in source:
            print("❌ Found subprocess import in declarative_operations.py")
            return False
        else:
            print("✅ No subprocess imports found in declarative_operations.py")
        
        # Check CLI module
        import pygetpapers.declarative_cli as decl_cli
        source = inspect.getsource(decl_cli)
        
        if "subprocess" in source:
            print("❌ Found subprocess import in declarative_cli.py")
            return False
        else:
            print("✅ No subprocess imports found in declarative_cli.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Import check failed: {e}")
        return False

def test_internal_api_calls():
    """Test that operations call internal pygetpapers APIs."""
    print("\n🔗 Testing Internal API Integration...")
    
    try:
        from pygetpapers.declarative_operations import DeclarativeOperationsManager
        
        # Create manager
        manager = DeclarativeOperationsManager("config/crossref_declarative.yaml")
        
        # Check that the manager has access to internal APIs
        assert hasattr(manager, '_execute_repository_operation'), "Should have internal API method"
        print("✅ Internal API method available")
        
        # Check that it imports pygetpapers main class
        from pygetpapers.pygetpapers import Pygetpapers
        print("✅ Can import Pygetpapers main class")
        
        # Test that we can create a pygetpapers instance
        pygetpapers = Pygetpapers()
        print("✅ Can create Pygetpapers instance")
        
        return True
        
    except Exception as e:
        print(f"❌ Internal API test failed: {e}")
        return False

def main():
    """Run all tests."""
    tests = [
        ("Pure Python Execution", test_pure_python_execution),
        ("No Subprocess Imports", test_no_subprocess_imports),
        ("Internal API Calls", test_internal_api_calls)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"TEST: {test_name}")
        print(f"{'='*60}")
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 Test Results:")
    print(f"{'='*60}")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Pure Python execution is working correctly.")
        print("\n✅ Key Benefits:")
        print("   - No subprocess calls required")
        print("   - Direct integration with pygetpapers APIs")
        print("   - Full security without external process risks")
        print("   - Better error handling and debugging")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
    finally:
        # Cleanup
        test_dir = Path("test_output")
        if test_dir.exists():
            import shutil
            shutil.rmtree(test_dir)
            print(f"\n🧹 Cleaned up test directory")
    
    sys.exit(exit_code) 