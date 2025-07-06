"""
Tests for the Streamlit UI functionality.
These tests validate that the Streamlit app can be imported and run.
"""

import subprocess
import sys
from pathlib import Path


def test_streamlit_app_import():
    """Test that the streamlit app module can be imported"""
    try:
        # Test importing the main streamlit app from root directory
        result = subprocess.run(
            [sys.executable, "-c", "import streamlit_app"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=".",  # Run from current directory (root)
        )
        assert (
            result.returncode == 0
        ), f"Failed to import streamlit_app: {result.stderr}"
    except Exception as e:
        assert False, f"Failed to import streamlit_app: {e}"


def test_run_streamlit_import():
    """Test that the run_streamlit module can be imported"""
    try:
        # Test importing the run_streamlit module from root directory
        result = subprocess.run(
            [sys.executable, "-c", "import run_streamlit"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=".",  # Run from current directory (root)
        )
        assert (
            result.returncode == 0
        ), f"Failed to import run_streamlit: {result.stderr}"
    except Exception as e:
        assert False, f"Failed to import run_streamlit: {e}"


def test_streamlit_app_exists():
    """Test that the streamlit app file exists"""
    app_path = Path("streamlit_app.py")
    assert app_path.exists(), "streamlit_app.py should exist"


def test_run_streamlit_exists():
    """Test that the run_streamlit file exists"""
    run_path = Path("run_streamlit.py")
    assert run_path.exists(), "run_streamlit.py should exist"


def test_streamlit_app_syntax():
    """Test that the streamlit app has valid Python syntax"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", "streamlit_app.py"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert (
            result.returncode == 0
        ), f"streamlit_app.py has syntax errors: {result.stderr}"
    except Exception as e:
        assert False, f"Failed to compile streamlit_app.py: {e}"


def test_run_streamlit_syntax():
    """Test that the run_streamlit file has valid Python syntax"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", "run_streamlit.py"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert (
            result.returncode == 0
        ), f"run_streamlit.py has syntax errors: {result.stderr}"
    except Exception as e:
        assert False, f"Failed to compile run_streamlit.py: {e}"


if __name__ == "__main__":
    # Run all tests
    test_streamlit_app_import()
    test_run_streamlit_import()
    test_streamlit_app_exists()
    test_run_streamlit_exists()
    test_streamlit_app_syntax()
    test_run_streamlit_syntax()
    print("✅ All Streamlit UI tests passed!")
