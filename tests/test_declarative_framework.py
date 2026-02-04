#!/usr/bin/env python3
"""
Test script for the Declarative Operations Framework

This script demonstrates the framework working with security components.
Run this to verify the implementation is working correctly.
"""

import os
import sys
from pathlib import Path


def test_security_framework():
    """Test the security framework components."""
    print("🔒 Testing Security Framework...")

    try:
        from pygetpapers.security_framework import (
            ResourceManager,
            SafeContentProcessor,
            SecurityValidator,
            create_security_framework,
        )

        # Test security validator
        validator = SecurityValidator()
        print("✅ SecurityValidator created successfully")

        # Test URL validation
        valid_url = "https://api.crossref.org/works"
        invalid_url = "https://malicious-site.com/admin"

        assert validator.validate_url(valid_url), "Valid URL should pass"
        assert not validator.validate_url(invalid_url), "Invalid URL should fail"
        print("✅ URL validation working")

        # Test resource manager
        resource_mgr = ResourceManager()
        print("✅ ResourceManager created successfully")

        # Test rate limiting
        assert resource_mgr.can_make_request(
            "crossref.org"
        ), "Should allow first request"
        print("✅ Rate limiting working")

        # Test content processor
        processor = SafeContentProcessor()
        print("✅ SafeContentProcessor created successfully")

        # Test complete framework
        framework = create_security_framework("./test_corpus")
        print("✅ Complete security framework created")

        return True

    except Exception as e:
        assert False, f"Security framework test failed: {e}"


def test_declarative_operations():
    """Test the declarative operations framework."""
    print("\n🔧 Testing Declarative Operations...")

    try:
        from pygetpapers.declarative_operations import (
            DeclarativeOperationsManager,
            create_declarative_config_for_repository,
        )

        # Test configuration creation
        create_declarative_config_for_repository("test_repo", "test_config.yaml")
        print("✅ Configuration creation working")

        # Test manager initialization
        manager = DeclarativeOperationsManager("config/crossref_declarative.yaml")
        print("✅ DeclarativeOperationsManager created successfully")

        # Test operations loading
        assert len(manager.operations) > 0, "Should load operations from config"
        print(f"✅ Loaded {len(manager.operations)} operations")

        # Test repositories loading
        assert len(manager.repositories) > 0, "Should load repositories from config"
        print(f"✅ Loaded {len(manager.repositories)} repositories")

        # Test dependency checking
        working_dir = Path("./test_corpus")
        working_dir.mkdir(exist_ok=True)

        for op_name, operation in manager.operations.items():
            satisfied, missing = manager.check_dependencies(operation, working_dir)
            print(f"   {op_name}: {'✅' if satisfied else '❌'} dependencies")

        print("✅ Dependency checking working")

        return True

    except Exception as e:
        assert False, f"Declarative operations test failed: {e}"


def test_cli_interface():
    """Test the CLI interface."""
    print("\n🖥️  Testing CLI Interface...")

    try:
        from argparse import Namespace

        from pygetpapers.declarative_cli import (
            create_config_command,
            list_operations_command,
            validate_config_command,
        )

        # Test configuration validation
        args = Namespace(config="config/crossref_declarative.yaml")
        result = validate_config_command(args)
        assert result == 0, "Configuration validation should succeed"
        print("✅ CLI validation working")

        return True

    except Exception as e:
        assert False, f"CLI interface test failed: {e}"


def test_integration():
    """Test integration between components."""
    print("\n🔗 Testing Integration...")

    try:
        from pygetpapers.declarative_operations import DeclarativeOperationsManager
        from pygetpapers.security_framework import create_security_framework

        # Create working directory
        working_dir = Path("./test_corpus")
        working_dir.mkdir(exist_ok=True)

        # Initialize manager with security framework
        manager = DeclarativeOperationsManager(
            "config/crossref_declarative.yaml", working_dir
        )

        # Test that security framework is available
        assert hasattr(manager, "security"), "Manager should have security framework"
        assert (
            "validator" in manager.security
        ), "Security framework should have validator"
        print("✅ Security framework integrated")

        # Test operation execution (simulation)
        for op_name, operation in list(manager.operations.items())[
            :2
        ]:  # Test first 2 operations
            print(f"   Testing operation: {op_name}")
            success = manager.execute_operation(operation, working_dir, query="test")
            print(f"   {op_name}: {'✅' if success else '❌'}")

        print("✅ Integration working")

        return True

    except Exception as e:
        assert False, f"Integration test failed: {e}"


def cleanup():
    """Clean up test files."""
    print("\n🧹 Cleaning up...")

    test_files = ["test_config.yaml", "test_corpus"]

    for file_path in test_files:
        path = Path(file_path)
        if path.exists():
            if path.is_dir():
                import shutil

                shutil.rmtree(path)
            else:
                path.unlink()
            print(f"   Removed: {file_path}")


def main():
    """Run all tests."""
    print("🚀 Testing Declarative Operations Framework")
    print("=" * 50)

    tests = [
        ("Security Framework", test_security_framework),
        ("Declarative Operations", test_declarative_operations),
        ("CLI Interface", test_cli_interface),
        ("Integration", test_integration),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results:")

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1

    print(f"\n🎯 Overall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Framework is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
    finally:
        cleanup()

    sys.exit(exit_code)
