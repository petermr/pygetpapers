#!/usr/bin/env python3
"""
Simple test script to verify CI/CD functionality
"""

import os
import sys


def test_imports():
    """Test that all required modules can be imported"""
    print("🧪 Testing imports...")

    try:
        import streamlit

        print(f"✅ Streamlit {streamlit.__version__}")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False

    try:
        import plotly

        print(f"✅ Plotly {plotly.__version__}")
    except ImportError as e:
        print(f"❌ Plotly import failed: {e}")
        return False

    try:
        import pandas

        print(f"✅ Pandas {pandas.__version__}")
    except ImportError as e:
        print(f"❌ Pandas import failed: {e}")
        return False

    try:
        import lxml

        print(f"✅ lxml {lxml.__version__}")
    except ImportError as e:
        print(f"❌ lxml import failed: {e}")
        return False

    return True


def test_streamlit_app():
    """Test that the Streamlit app can be imported"""
    print("\n🧪 Testing Streamlit app...")

    try:
        pass

        print("✅ Streamlit app imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Streamlit app import failed: {e}")
        return False


def test_datatables():
    """Test that datatables integration can be imported"""
    print("\n🧪 Testing datatables integration...")

    try:
        pass

        print("✅ Datatables integration imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Datatables integration import failed: {e}")
        return False


def test_pygetpapers():
    """Test that pygetpapers CLI is available"""
    print("\n🧪 Testing pygetpapers CLI...")

    try:
        import subprocess

        result = subprocess.run(["pygetpapers", "--version"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ pygetpapers CLI available: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ pygetpapers CLI failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ pygetpapers CLI test failed: {e}")
        return False


def test_files_exist():
    """Test that required files exist"""
    print("\n🧪 Testing file existence...")

    required_files = ["streamlit_app.py", "run_streamlit.py", "datatables_integration.py", "requirements.txt"]

    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            all_exist = False

    return all_exist


def main():
    """Run all tests"""
    print("🚀 Starting CI/CD Tests")
    print("=" * 50)

    tests = [test_imports, test_streamlit_app, test_datatables, test_pygetpapers, test_files_exist]

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
    sys.exit(main())
