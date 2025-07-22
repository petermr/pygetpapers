#!/usr/bin/env python3
"""
Streamlit Runner for Pygetpapers

This script helps manage Streamlit instances and prevents port conflicts.
"""

import os
import subprocess
import sys
import time


def find_available_port(start_port=8501, max_attempts=10):
    """Find an available port starting from start_port"""
    import socket

    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("localhost", port))
                return port
        except OSError:
            continue
    return None


def kill_existing_streamlit():
    """Kill existing Streamlit processes"""
    try:
        # Find and kill existing Streamlit processes
        result = subprocess.run(["pkill", "-f", "streamlit"], capture_output=True)
        if result.returncode == 0:
            print("✅ Killed existing Streamlit processes")
        else:
            print("ℹ️  No existing Streamlit processes found")
    except Exception as e:
        print(f"⚠️  Could not kill existing processes: {e}")


def run_streamlit(app_file="pygetpapers/streamlit_app.py", port=None, headless=True):
    """Run Streamlit with the specified configuration"""

    # Find available port if not specified
    if port is None:
        port = find_available_port()
        if port is None:
            print("❌ No available ports found")
            return False

    # Build command
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        app_file,
        "--server.port",
        str(port),
    ]

    if headless:
        cmd.extend(["--server.headless", "true"])

    print(f"🚀 Starting Streamlit on port {port}")
    print(f"📱 Local URL: http://localhost:{port}")
    print(f"🌐 Network URL: http://192.168.0.82:{port}")
    print(f"🔗 External URL: http://81.101.149.173:{port}")
    print()
    print("Press Ctrl+C to stop the server")
    print()

    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n👋 Streamlit server stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running Streamlit: {e}")
        return False

    return True


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="Run Pygetpapers Streamlit app")
    parser.add_argument(
        "--app",
        default="pygetpapers/streamlit_app.py",
        help="Streamlit app file to run",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Port to run on (auto-find if not specified)",
    )
    parser.add_argument(
        "--kill-existing",
        action="store_true",
        help="Kill existing Streamlit processes before starting",
    )
    parser.add_argument(
        "--no-headless", action="store_true", help="Don't run in headless mode"
    )

    args = parser.parse_args()

    # Check if app file exists
    if not os.path.exists(args.app):
        print(f"❌ App file not found: {args.app}")
        return False

    # Kill existing processes if requested
    if args.kill_existing:
        kill_existing_streamlit()
        time.sleep(1)  # Give time for processes to terminate

    # Run Streamlit
    return run_streamlit(
        app_file=args.app, port=args.port, headless=not args.no_headless
    )


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
