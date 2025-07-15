#!/usr/bin/env python3
"""
Test utilities for pygetpapers tests.

This module provides common testing utilities including connectivity testing.
"""

import requests
import socket
import time
from typing import Optional, Tuple
from urllib.parse import urlparse


def test_redalyc_connectivity(timeout: int = 10) -> Tuple[bool, str]:
    """
    Test connectivity to Redalyc website.
    
    Args:
        timeout: Timeout in seconds for the connection test
        
    Returns:
        Tuple of (is_connected, error_message)
    """
    redalyc_urls = [
        "https://www.redalyc.org",
        "https://redalyc.org",
        "http://www.redalyc.org"
    ]
    
    for url in redalyc_urls:
        try:
            print(f"Testing connectivity to {url}...")
            response = requests.get(url, timeout=timeout)
            if response.status_code == 200:
                print(f"✅ Successfully connected to {url}")
                return True, ""
            else:
                print(f"⚠️  {url} returned status code {response.status_code}")
        except requests.exceptions.Timeout:
            print(f"⏰ Timeout connecting to {url}")
        except requests.exceptions.ConnectionError as e:
            print(f"🔌 Connection error for {url}: {e}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Request error for {url}: {e}")
        except Exception as e:
            print(f"❌ Unexpected error for {url}: {e}")
    
    error_msg = f"Failed to connect to any Redalyc URL after {timeout}s timeout"
    print(f"❌ {error_msg}")
    return False, error_msg


def test_redalyc_api_connectivity(timeout: int = 10) -> Tuple[bool, str]:
    """
    Test connectivity to Redalyc API endpoints.
    
    Args:
        timeout: Timeout in seconds for the connection test
        
    Returns:
        Tuple of (is_connected, error_message)
    """
    api_urls = [
        "https://www.redalyc.org/api/",
        "https://api.redalyc.org/",
        "https://www.redalyc.org/ws/",
        "https://www.redalyc.org/rest/"
    ]
    
    for url in api_urls:
        try:
            print(f"Testing API connectivity to {url}...")
            response = requests.get(url, timeout=timeout)
            if response.status_code in [200, 404, 403]:  # 404/403 means endpoint exists
                print(f"✅ API endpoint {url} is reachable (status: {response.status_code})")
                return True, ""
            else:
                print(f"⚠️  {url} returned status code {response.status_code}")
        except requests.exceptions.Timeout:
            print(f"⏰ Timeout connecting to API {url}")
        except requests.exceptions.ConnectionError as e:
            print(f"🔌 Connection error for API {url}: {e}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Request error for API {url}: {e}")
        except Exception as e:
            print(f"❌ Unexpected error for API {url}: {e}")
    
    error_msg = f"Failed to connect to any Redalyc API endpoint after {timeout}s timeout"
    print(f"❌ {error_msg}")
    return False, error_msg


def skip_if_redalyc_down():
    """
    Decorator to skip tests if Redalyc is down.
    
    Usage:
        @skip_if_redalyc_down()
        def test_redalyc_functionality():
            # test code here
    """
    def decorator(test_func):
        def wrapper(*args, **kwargs):
            is_connected, error_msg = test_redalyc_connectivity()
            if not is_connected:
                print(f"⏭️  Skipping {test_func.__name__}: Redalyc is down")
                print(f"   Reason: {error_msg}")
                return True  # Return True to indicate "skipped" rather than "failed"
            return test_func(*args, **kwargs)
        return wrapper
    return decorator


def require_redalyc_connectivity():
    """
    Decorator to require Redalyc connectivity for tests.
    
    Usage:
        @require_redalyc_connectivity()
        def test_redalyc_functionality():
            # test code here
    """
    def decorator(test_func):
        def wrapper(*args, **kwargs):
            is_connected, error_msg = test_redalyc_connectivity()
            if not is_connected:
                print(f"❌ {test_func.__name__} requires Redalyc connectivity")
                print(f"   Reason: {error_msg}")
                return False
            return test_func(*args, **kwargs)
        return wrapper
    return decorator


def test_network_connectivity(host: str = "8.8.8.8", port: int = 53, timeout: int = 3) -> bool:
    """
    Test basic network connectivity.
    
    Args:
        host: Host to test connectivity to (default: Google DNS)
        port: Port to test (default: 53 for DNS)
        timeout: Timeout in seconds
        
    Returns:
        True if network is available, False otherwise
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False


def wait_for_redalyc(max_wait: int = 60, check_interval: int = 5) -> bool:
    """
    Wait for Redalyc to become available.
    
    Args:
        max_wait: Maximum time to wait in seconds
        check_interval: Interval between checks in seconds
        
    Returns:
        True if Redalyc becomes available, False if timeout
    """
    print(f"⏳ Waiting for Redalyc to become available (max {max_wait}s)...")
    
    start_time = time.time()
    while time.time() - start_time < max_wait:
        is_connected, _ = test_redalyc_connectivity(timeout=5)
        if is_connected:
            print("✅ Redalyc is now available!")
            return True
        
        print(f"⏳ Still waiting... ({int(time.time() - start_time)}s elapsed)")
        time.sleep(check_interval)
    
    print(f"⏰ Timeout waiting for Redalyc after {max_wait}s")
    return False 