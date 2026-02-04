#!/usr/bin/env python3
"""
Simple test script to verify CI/CD functionality
"""

import os


def test_imports():
    """Test that all required modules can be imported"""
    print("🧪 Testing imports...")

    import streamlit
    assert streamlit is not None, "Streamlit should be importable"
    assert hasattr(streamlit, "__version__"), "Streamlit should have __version__"
    print(f"✅ Streamlit {streamlit.__version__}")

    import plotly
    assert plotly is not None, "Plotly should be importable"
    assert hasattr(plotly, "__version__"), "Plotly should have __version__"
    print(f"✅ Plotly {plotly.__version__}")

    import pandas
    assert pandas is not None, "Pandas should be importable"
    assert hasattr(pandas, "__version__"), "Pandas should have __version__"
    print(f"✅ Pandas {pandas.__version__}")

    import lxml
    assert lxml is not None, "lxml should be importable"
    assert hasattr(lxml, "__version__"), "lxml should have __version__"
    print(f"✅ lxml {lxml.__version__}")


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

    import subprocess

    try:
        result = subprocess.run(
            ["pygetpapers", "--version"], capture_output=True, text=True, timeout=30
        )
        assert result.returncode == 0, f"pygetpapers CLI failed: {result.stderr}"
        assert result.stdout is not None, "pygetpapers CLI should produce output"
        print(f"✅ pygetpapers CLI available: {result.stdout.strip()}")
    except subprocess.TimeoutExpired:
        assert False, "pygetpapers CLI command timed out after 30 seconds"
    except FileNotFoundError:
        assert False, "pygetpapers CLI not found in PATH. Is it installed?"
    except Exception as e:
        assert False, f"pygetpapers CLI test failed: {e}"


def test_files_exist():
    """Test that required files exist"""
    print("\n🧪 Testing file existence...")

    # Get project root (parent of tests directory)
    import sys
    from pathlib import Path
    project_root = Path(__file__).parent.parent

    required_files = [
        project_root / "pygetpapers" / "streamlit_app.py",
        project_root / "pygetpapers" / "run_streamlit.py",
        project_root / "pygetpapers" / "tools" / "datatables_integration.py",
        project_root / "requirements.txt",
    ]

    for file_path in required_files:
        assert file_path.exists(), f"Required file missing: {file_path}"
        print(f"✅ {file_path.relative_to(project_root)} exists")


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
