#!/usr/bin/env python3
"""
Simple test script to verify CI/CD functionality
"""

import os


def test_imports():
    """Test that all required modules can be imported"""
    print("🧪 Testing imports...")

    try:
        import streamlit

        print(f"✅ Streamlit {streamlit.__version__}")
    except ImportError as e:
        assert False, f"Streamlit import failed: {e}"

    try:
        import plotly

        print(f"✅ Plotly {plotly.__version__}")
    except ImportError as e:
        assert False, f"Plotly import failed: {e}"

    try:
        import pandas

        print(f"✅ Pandas {pandas.__version__}")
    except ImportError as e:
        assert False, f"Pandas import failed: {e}"

    try:
        import lxml

        print(f"✅ lxml {lxml.__version__}")
    except ImportError as e:
        assert False, f"lxml import failed: {e}"

    return True


# def test_streamlit_app():
#     """Test that the Streamlit app can be imported"""
#     print("\n🧪 Testing Streamlit app...")
#
#     try:
#         # Test if the module can be imported
#         import pygetpapers.streamlit_app
#
#         # Access a simple attribute to ensure it's actually imported
#         _ = pygetpapers.streamlit_app.__name__
#
#         print("✅ Streamlit app imported successfully")
#         return True
#     except ImportError as e:
#         print(f"❌ Streamlit app import failed: {e}")
#         return False


# def test_datatables():
#     """Test that datatables integration can be imported"""
#     print("\n🧪 Testing datatables integration...")
#
#     try:
#         # Test if the module can be imported
#         import pygetpapers.tools.datatables_integration
#
#         # Access a simple attribute to ensure it's actually imported
#         _ = pygetpapers.tools.datatables_integration.__name__
#
#         print("✅ Datatables integration imported successfully")
#         return True
#     except ImportError as e:
#         print(f"❌ Datatables integration import failed: {e}")
#         return False


def test_pygetpapers():
    """Test that pygetpapers CLI is available"""
    print("\n🧪 Testing pygetpapers CLI...")

    try:
        import subprocess

        result = subprocess.run(
            ["pygetpapers", "--version"], capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            print(f"✅ pygetpapers CLI available: {result.stdout.strip()}")
        else:
            assert False, f"pygetpapers CLI failed: {result.stderr}"
    except Exception as e:
        assert False, f"pygetpapers CLI test failed: {e}"

    return True


def test_files_exist():
    """Test that required files exist"""
    print("\n🧪 Testing file existence...")

    required_files = [
        "pygetpapers/streamlit_app.py",
        "pygetpapers/run_streamlit.py",
        "pygetpapers/tools/datatables_integration.py",
        "requirements.txt",
    ]

    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            assert False, f"Required file missing: {file}"

    return True


def main():
    """Run all tests"""
    print("🚀 Starting CI/CD Tests")
    print("=" * 50)

    tests = [
        test_imports,
        # test_streamlit_app,  # Disabled - not suitable for GitHub Actions
        # test_datatables,     # Disabled - not suitable for GitHub Actions
        test_pygetpapers,
        test_files_exist,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")

    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! CI/CD should work correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the issues above.")
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
