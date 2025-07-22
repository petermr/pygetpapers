#!/usr/bin/env python3
"""
Pygetpapers Installation Script

This script helps users install pygetpapers on different operating systems.
It detects the OS and provides appropriate installation instructions.
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path


def print_header():
    """Print installation header."""
    print("=" * 60)
    print("           Pygetpapers Installation Script")
    print("=" * 60)
    print()


def detect_os():
    """Detect the operating system."""
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    elif system == "darwin":
        return "macos"
    elif system == "linux":
        return "linux"
    else:
        return "unknown"


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Error: Python 3.8 or higher is required.")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True


def check_pip():
    """Check if pip is available."""
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "--version"], capture_output=True, check=True
        )
        print("✅ pip is available")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ pip is not available")
        return False


def check_git():
    """Check if git is available."""
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
        print("✅ git is available")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ git is not available")
        return False


def install_dependencies_windows():
    """Install dependencies on Windows."""
    print("\n📦 Installing dependencies on Windows...")

    # Check if we're in the pygetpapers directory
    if not os.path.exists("pygetpapers.py"):
        print("❌ Please run this script from the pygetpapers directory")
        return False

    try:
        # Create virtual environment
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)

        # Activate virtual environment
        venv_python = os.path.join("venv", "Scripts", "python.exe")
        venv_pip = os.path.join("venv", "Scripts", "pip.exe")

        # Install requirements
        print("Installing requirements...")
        subprocess.run([venv_pip, "install", "-r", "requirements.txt"], check=True)

        # Install pygetpapers
        print("Installing pygetpapers...")
        subprocess.run([venv_pip, "install", "-e", "."], check=True)

        print("✅ Installation completed successfully!")
        print("\nTo activate the virtual environment:")
        print("   venv\\Scripts\\activate")
        print("\nTo run pygetpapers:")
        print("   pygetpapers --help")

        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        return False


def install_dependencies_macos():
    """Install dependencies on macOS."""
    print("\n📦 Installing dependencies on macOS...")

    # Check if we're in the pygetpapers directory
    if not os.path.exists("pygetpapers.py"):
        print("❌ Please run this script from the pygetpapers directory")
        return False

    try:
        # Create virtual environment
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)

        # Activate virtual environment
        venv_python = os.path.join("venv", "bin", "python")
        venv_pip = os.path.join("venv", "bin", "pip")

        # Install requirements
        print("Installing requirements...")
        subprocess.run([venv_pip, "install", "-r", "requirements.txt"], check=True)

        # Install pygetpapers
        print("Installing pygetpapers...")
        subprocess.run([venv_pip, "install", "-e", "."], check=True)

        print("✅ Installation completed successfully!")
        print("\nTo activate the virtual environment:")
        print("   source venv/bin/activate")
        print("\nTo run pygetpapers:")
        print("   pygetpapers --help")

        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        return False


def install_dependencies_linux():
    """Install dependencies on Linux."""
    print("\n📦 Installing dependencies on Linux...")

    # Check if we're in the pygetpapers directory
    if not os.path.exists("pygetpapers.py"):
        print("❌ Please run this script from the pygetpapers directory")
        return False

    try:
        # Create virtual environment
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)

        # Activate virtual environment
        venv_python = os.path.join("venv", "bin", "python")
        venv_pip = os.path.join("venv", "bin", "pip")

        # Install requirements
        print("Installing requirements...")
        subprocess.run([venv_pip, "install", "-r", "requirements.txt"], check=True)

        # Install pygetpapers
        print("Installing pygetpapers...")
        subprocess.run([venv_pip, "install", "-e", "."], check=True)

        print("✅ Installation completed successfully!")
        print("\nTo activate the virtual environment:")
        print("   source venv/bin/activate")
        print("\nTo run pygetpapers:")
        print("   pygetpapers --help")

        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        return False


def install_optional_dependencies():
    """Install optional dependencies."""
    print("\n🔧 Installing optional dependencies...")

    optional_packages = [
        "datatables-module",
        "selenium",
        "webdriver-manager",
        "beautifulsoup4",
        "lxml",
    ]

    venv_pip = None
    if os.path.exists(os.path.join("venv", "Scripts", "pip.exe")):
        venv_pip = os.path.join("venv", "Scripts", "pip.exe")
    elif os.path.exists(os.path.join("venv", "bin", "pip")):
        venv_pip = os.path.join("venv", "bin", "pip")

    if not venv_pip:
        print(
            "❌ Virtual environment not found. Please run the main installation first."
        )
        return False

    try:
        for package in optional_packages:
            print(f"Installing {package}...")
            subprocess.run([venv_pip, "install", package], check=True)

        print("✅ Optional dependencies installed successfully!")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install optional dependencies: {e}")
        return False


def create_output_directory():
    """Create the default output directory."""
    home_dir = os.path.expanduser("~")
    pygetpapers_dir = os.path.join(home_dir, "pygetpapers")

    try:
        os.makedirs(pygetpapers_dir, exist_ok=True)
        print(f"✅ Created output directory: {pygetpapers_dir}")
        return True
    except Exception as e:
        print(f"❌ Failed to create output directory: {e}")
        return False


def run_test():
    """Run a simple test to verify installation."""
    print("\n🧪 Running installation test...")

    venv_python = None
    if os.path.exists(os.path.join("venv", "Scripts", "python.exe")):
        venv_python = os.path.join("venv", "Scripts", "python.exe")
    elif os.path.exists(os.path.join("venv", "bin", "python")):
        venv_python = os.path.join("venv", "bin", "python")

    if not venv_python:
        print("❌ Virtual environment not found.")
        return False

    try:
        # Test pygetpapers import
        result = subprocess.run(
            [
                venv_python,
                "-c",
                "import pygetpapers; print('✅ pygetpapers imported successfully')",
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print(result.stdout.strip())
        else:
            print("❌ Failed to import pygetpapers")
            print(result.stderr)
            return False

        # Test pygetpapers command
        result = subprocess.run(
            [venv_python, "-m", "pygetpapers", "--version"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print(f"✅ pygetpapers command works: {result.stdout.strip()}")
        else:
            print("❌ pygetpapers command failed")
            print(result.stderr)
            return False

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def main():
    """Main installation function."""
    print_header()

    # Detect OS
    os_type = detect_os()
    print(f"🖥️  Detected OS: {os_type}")

    # Check prerequisites
    print("\n🔍 Checking prerequisites...")
    if not check_python_version():
        return False

    if not check_pip():
        print("\n📋 To install pip:")
        if os_type == "windows":
            print("   Download get-pip.py from https://bootstrap.pypa.io/get-pip.py")
            print("   Run: python get-pip.py")
        elif os_type == "macos":
            print("   Run: brew install python (includes pip)")
        elif os_type == "linux":
            print("   Run: sudo apt install python3-pip (Ubuntu/Debian)")
            print("   Or: sudo yum install python3-pip (CentOS/RHEL)")
        return False

    if not check_git():
        print("\n📋 To install git:")
        if os_type == "windows":
            print("   Download from https://git-scm.com/download/win")
        elif os_type == "macos":
            print("   Run: brew install git")
        elif os_type == "linux":
            print("   Run: sudo apt install git (Ubuntu/Debian)")
            print("   Or: sudo yum install git (CentOS/RHEL)")
        return False

    # Install dependencies based on OS
    success = False
    if os_type == "windows":
        success = install_dependencies_windows()
    elif os_type == "macos":
        success = install_dependencies_macos()
    elif os_type == "linux":
        success = install_dependencies_linux()
    else:
        print("❌ Unsupported operating system")
        return False

    if not success:
        return False

    # Create output directory
    create_output_directory()

    # Ask about optional dependencies
    print("\n" + "=" * 60)
    response = input("Install optional dependencies? (y/n): ").lower().strip()
    if response in ["y", "yes"]:
        install_optional_dependencies()

    # Run test
    if run_test():
        print("\n🎉 Installation completed successfully!")
        print("\n📚 Next steps:")
        print("1. Activate the virtual environment:")
        if os_type == "windows":
            print("   venv\\Scripts\\activate")
        else:
            print("   source venv/bin/activate")
        print("2. Try a simple search:")
        print("   pygetpapers --query 'artificial intelligence' --limit 5")
        print("3. Read the documentation:")
        print("   GETTING_STARTED.md")
        print("   QUICK_REFERENCE.md")
    else:
        print("\n❌ Installation test failed. Please check the error messages above.")
        return False

    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Installation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
