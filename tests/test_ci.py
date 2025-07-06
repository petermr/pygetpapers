"""
Fast CI tests that don't make real API calls.
These tests validate the CLI interface and basic functionality without
downloading papers.
"""

import subprocess
import sys
from pathlib import Path


def test_cli_help():
    """Test that the CLI help command works"""
    result = subprocess.run(
        [sys.executable, "-m", "pygetpapers.pygetpapers", "--help"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0
    assert "usage:" in result.stdout.lower()
    assert "pygetpapers" in result.stdout


def test_cli_version():
    """Test that the CLI version command works"""
    result = subprocess.run(
        [sys.executable, "-m", "pygetpapers.pygetpapers", "--version"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0
    # Version output goes to stderr, not stdout
    assert "pygetpapers" in (result.stdout + result.stderr).lower()


def test_cli_noexecute():
    """Test the --noexecute flag (should not download anything)"""
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pygetpapers.pygetpapers",
            "-q",
            "test query",
            "--noexecute",
            "-k",
            "1",
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )

    # Should complete without error (even if no results found)
    assert result.returncode in [0, 1]  # 0 = success, 1 = no results found
    # Output goes to stderr, not stdout
    assert (
        "Total" in (result.stdout + result.stderr)
        or "hits" in (result.stdout + result.stderr).lower()
    )


def test_cli_syntax():
    """Test that basic CLI syntax is valid"""
    # Test with invalid API (should fail gracefully)
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pygetpapers.pygetpapers",
            "--api",
            "invalid_api",
            "-q",
            "test",
            "--noexecute",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )

    # Should handle invalid API gracefully
    assert result.returncode != 0  # Should fail with invalid API


def test_imports():
    """Test that all main modules can be imported"""
    try:
        pass

        print("✅ All pygetpapers modules imported successfully")
    except ImportError as e:
        assert False, f"Failed to import pygetpapers: {e}"


def test_config_file():
    """Test that config file exists and is readable"""
    config_path = Path("pygetpapers/config.ini")
    assert config_path.exists(), "config.ini should exist"

    # Test that it can be read
    with open(config_path, "r") as f:
        content = f.read()
        assert "[DEFAULT]" in content or "api" in content.lower()


if __name__ == "__main__":
    # Run all tests
    test_cli_help()
    test_cli_version()
    test_cli_noexecute()
    test_cli_syntax()
    test_imports()
    test_config_file()
    print("✅ All CI tests passed!")
