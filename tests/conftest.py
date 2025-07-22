#!/usr/bin/env python3
"""
Pytest configuration for pygetpapers tests.

This file provides pytest fixtures and configuration for running tests
with connectivity checking for external services like Redalyc.
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from test_utils import test_redalyc_connectivity


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "redalyc: marks tests that require Redalyc connectivity"
    )
    config.addinivalue_line(
        "markers", "skip_if_redalyc_down: marks tests to skip if Redalyc is down"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to handle Redalyc connectivity."""
    # Test Redalyc connectivity once at collection time
    print("\n🔍 Testing Redalyc connectivity for test collection...")
    is_redalyc_connected, error_msg = test_redalyc_connectivity(timeout=5)

    if not is_redalyc_connected:
        print(f"⚠️  Redalyc appears to be down: {error_msg}")
        print("   Tests marked with @pytest.mark.skip_if_redalyc_down will be skipped")

    # Mark tests that should be skipped if Redalyc is down
    for item in items:
        if "redalyc" in item.nodeid.lower():
            if not is_redalyc_connected:
                item.add_marker(
                    pytest.mark.skip(reason=f"Redalyc is down: {error_msg}")
                )
            else:
                item.add_marker(pytest.mark.redalyc)


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
