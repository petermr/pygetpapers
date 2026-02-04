"""
Tests for the Streamlit UI functionality.
These tests validate that the Streamlit app can be imported and run.
"""

import subprocess
import sys
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent


def test_streamlit_app_import():
    """Test that the streamlit app module can be imported"""
    import pytest
    
    # Test importing the main streamlit app from pygetpapers directory
    result = subprocess.run(
        [sys.executable, "-c", "import pygetpapers.streamlit_app"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=".",  # Run from current directory (root)
    )
    
    # If import fails due to missing dependencies, skip the test
    if result.returncode != 0:
        if "ImportError" in result.stderr or "ModuleNotFoundError" in result.stderr:
            pytest.skip(f"Streamlit dependencies not available: {result.stderr}")
        # For other errors (like segfaults), still fail but with better message
        assert False, f"Failed to import pygetpapers.streamlit_app: {result.stderr}"


def test_run_streamlit_import():
    """Test that the run_streamlit module can be imported"""
    import pytest
    
    # Test importing the run_streamlit module from pygetpapers directory
    result = subprocess.run(
        [sys.executable, "-c", "import pygetpapers.run_streamlit"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=".",  # Run from current directory (root)
    )
    
    # If import fails due to missing dependencies, skip the test
    if result.returncode != 0:
        if "ImportError" in result.stderr or "ModuleNotFoundError" in result.stderr:
            pytest.skip(f"Streamlit dependencies not available: {result.stderr}")
        # For other errors (like segfaults), still fail but with better message
        assert False, f"Failed to import pygetpapers.run_streamlit: {result.stderr}"


def test_streamlit_app_exists():
    """Test that the streamlit app file exists"""
    app_path = PROJECT_ROOT / "pygetpapers" / "streamlit_app.py"
    assert app_path.exists(), f"pygetpapers/streamlit_app.py should exist at {app_path}"


def test_run_streamlit_exists():
    """Test that the run_streamlit file exists"""
    run_path = PROJECT_ROOT / "pygetpapers" / "run_streamlit.py"
    assert run_path.exists(), f"pygetpapers/run_streamlit.py should exist at {run_path}"


def test_streamlit_app_syntax():
    """Test that the streamlit app has valid Python syntax"""
    app_path = PROJECT_ROOT / "pygetpapers" / "streamlit_app.py"
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(app_path)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert (
        result.returncode == 0
    ), f"pygetpapers/streamlit_app.py has syntax errors: {result.stderr}"


def test_run_streamlit_syntax():
    """Test that the run_streamlit file has valid Python syntax"""
    run_path = PROJECT_ROOT / "pygetpapers" / "run_streamlit.py"
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(run_path)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert (
        result.returncode == 0
    ), f"pygetpapers/run_streamlit.py has syntax errors: {result.stderr}"


if __name__ == "__main__":
    # Run all tests
    test_streamlit_app_import()
    test_run_streamlit_import()
    test_streamlit_app_exists()
    test_run_streamlit_exists()
    test_streamlit_app_syntax()
    test_run_streamlit_syntax()
    print("✅ All Streamlit UI tests passed!")
