#!/usr/bin/env python3
"""
Script to run the Pygetpapers Streamlit UI on port 8502
This avoids conflicts with other Streamlit applications running on port 8501
"""

import subprocess
import sys
import os


def main():
    """Run the Streamlit application on port 8502"""

    # Check if streamlit is available
    try:
        import streamlit

        print(f"Streamlit version: {streamlit.__version__}")
    except ImportError:
        print("Error: Streamlit is not installed. Please install it with:")
        print("pip install streamlit")
        sys.exit(1)

    # Check if pygetpapers is available
    try:
        # Try local development version first
        if os.path.exists("pygetpapers") and os.path.exists("pygetpapers/pygetpapers.py"):
            result = subprocess.run(
                [sys.executable, "-m", "pygetpapers.pygetpapers", "--version"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                print("✅ Pygetpapers development version is available")
            else:
                print("Warning: Pygetpapers development version may not be properly installed")
        else:
            # Try installed version
            result = subprocess.run(["pygetpapers", "--version"], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("✅ Pygetpapers installed version is available")
            else:
                print("Warning: Pygetpapers may not be properly installed")
    except FileNotFoundError:
        print("Warning: Pygetpapers command not found. Please install it with:")
        print("pip install pygetpapers")

    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(script_dir, "streamlit_app.py")

    if not os.path.exists(app_path):
        print(f"Error: streamlit_app.py not found at {app_path}")
        sys.exit(1)

    print("\n🚀 Starting Pygetpapers Streamlit UI...")
    print("📍 URL: http://localhost:8502")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)

    # Run streamlit with specific port
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        app_path,
        "--server.port",
        "8502",
        "--server.address",
        "localhost",
        "--browser.gatherUsageStats",
        "false",
    ]

    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n👋 Streamlit server stopped by user")
    except Exception as e:
        print(f"Error running Streamlit: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
