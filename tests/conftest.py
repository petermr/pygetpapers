#!/usr/bin/env python3
"""
Pytest configuration for pygetpapers tests.

This file provides pytest fixtures and configuration for running tests
with connectivity checking for external services like Redalyc.
"""

import configparser
from pathlib import Path

import pytest

from test_utils import test_redalyc_connectivity

# Path to repository skip configuration file
REPO_CONFIG_FILE = Path(__file__).parent / "test_repos_config.ini"


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "redalyc: marks tests that require Redalyc connectivity"
    )
    config.addinivalue_line(
        "markers", "scielo: marks tests that require SciELO connectivity"
    )
    config.addinivalue_line(
        "markers", "biorxiv: marks tests that require BioRxiv connectivity"
    )
    config.addinivalue_line(
        "markers", "upspace: marks tests that require Upspace connectivity"
    )
    config.addinivalue_line(
        "markers", "skip_if_redalyc_down: marks tests to skip if Redalyc is down"
    )


def _load_repo_skip_config():
    """
    Load repository skip configuration from config file.
    
    Returns:
        dict: Dictionary mapping repository names to skip status
    """
    config = {
        "redalyc": False,
        "scielo": False,
        "biorxiv": False,
        "upspace": False,
    }
    
    if REPO_CONFIG_FILE.exists():
        parser = configparser.ConfigParser()
        parser.read(REPO_CONFIG_FILE)
        
        if parser.has_section("test_repositories"):
            for repo in config.keys():
                value = parser.get("test_repositories", f"skip_{repo}", fallback="false")
                config[repo] = value.lower() in ("1", "true", "yes")
    
    return config


def pytest_collection_modifyitems(config, items):
    """
    Modify test collection to handle repository connectivity and skipping.
    
    Supports:
    1. Config file: tests/test_repos_config.ini (primary method)
    2. Pytest markers: -m "not redalyc" (command-line override)
    3. Auto-marking tests by file name
    4. Connectivity checking for Redalyc
    """
    # Load config file settings
    config_file_settings = _load_repo_skip_config()
    
    # Determine which repositories to skip from config file
    skip_repos = set()
    
    if config_file_settings["redalyc"]:
        skip_repos.add("redalyc")
        print("⚠️  Skipping Redalyc tests (config file)")
    
    if config_file_settings["scielo"]:
        skip_repos.add("scielo")
        print("⚠️  Skipping SciELO tests (config file)")
    
    if config_file_settings["biorxiv"]:
        skip_repos.add("biorxiv")
        print("⚠️  Skipping BioRxiv tests (config file)")
    
    if config_file_settings["upspace"]:
        skip_repos.add("upspace")
        print("⚠️  Skipping Upspace tests (config file)")
    
    # Note: Marker expressions are handled by pytest's built-in -m flag
    # Use -m "not redalyc" for command-line filtering (works alongside config)
    
    # Test Redalyc connectivity (only if not already skipped)
    is_redalyc_connected = True
    error_msg = ""
    if "redalyc" not in skip_repos:
        print("\n🔍 Testing Redalyc connectivity for test collection...")
        is_redalyc_connected, error_msg = test_redalyc_connectivity(timeout=5)
        
        if not is_redalyc_connected:
            print(f"⚠️  Redalyc appears to be down: {error_msg}")
            print("   Tests marked with @pytest.mark.skip_if_redalyc_down will be skipped")
    
    # Process each test item
    skipped_count = 0
    for item in items:
        nodeid_lower = item.nodeid.lower()
        item_repos = []
        
        # Auto-detect repository from nodeid (file/function name)
        if "redalyc" in nodeid_lower:
            item_repos.append("redalyc")
            # Auto-mark if not already marked
            if not any(m.name == "redalyc" for m in getattr(item, 'pytestmark', [])):
                item.add_marker(pytest.mark.redalyc)
        
        if "scielo" in nodeid_lower:
            item_repos.append("scielo")
            if not any(m.name == "scielo" for m in getattr(item, 'pytestmark', [])):
                item.add_marker(pytest.mark.scielo)
        
        if "biorxiv" in nodeid_lower:
            item_repos.append("biorxiv")
            if not any(m.name == "biorxiv" for m in getattr(item, 'pytestmark', [])):
                item.add_marker(pytest.mark.biorxiv)
        
        if "upspace" in nodeid_lower:
            item_repos.append("upspace")
            if not any(m.name == "upspace" for m in getattr(item, 'pytestmark', [])):
                item.add_marker(pytest.mark.upspace)
        
        # Check existing markers
        if hasattr(item, 'pytestmark'):
            for mark in item.pytestmark:
                if mark.name in ("redalyc", "scielo", "biorxiv", "upspace"):
                    if mark.name not in item_repos:
                        item_repos.append(mark.name)
        
        # Skip tests for disabled repositories
        for repo in item_repos:
            if repo in skip_repos:
                item.add_marker(
                    pytest.mark.skip(reason=f"Skipping {repo} tests (disabled via config)")
                )
                skipped_count += 1
                break
        
        # Handle Redalyc connectivity (existing behavior)
        if "redalyc" in item_repos and "redalyc" not in skip_repos:
            if not is_redalyc_connected:
                # Only skip if test uses skip_if_redalyc_down decorator
                # (Don't auto-skip all redalyc tests, let decorators handle it)
                pass
    
    if skip_repos:
        print(f"\n📊 Skipped {skipped_count} tests for repositories: {', '.join(sorted(skip_repos))}")


@pytest.fixture(scope="session")
def redalyc_connectivity():
    """Fixture to check Redalyc connectivity."""
    is_connected, error_msg = test_redalyc_connectivity()
    return {"connected": is_connected, "error": error_msg}


@pytest.fixture(scope="session")
def skip_if_redalyc_down(redalyc_connectivity):
    """Fixture to skip tests if Redalyc is down."""
    if not redalyc_connectivity["connected"]:
        pytest.skip(f"Redalyc is down: {redalyc_connectivity['error']}")
    return True
