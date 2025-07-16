# Installation and Deployment

## Overview
This document outlines the installation and deployment strategies for pygetpapers v2.0, including the comprehensive installation script, cross-platform compatibility, and deployment considerations.

## Background

### Installation Challenges
- Cross-platform compatibility requirements
- Complex dependency management
- User experience considerations
- Development vs production environments
- Virtual environment management

### Deployment Goals
- Simplify installation process
- Ensure consistent environments
- Provide clear error handling
- Support different user skill levels
- Enable automated deployment

## Design Decisions

### 1. Comprehensive Installation Script
**Decision**: Create a comprehensive, cross-platform installation script
**Rationale**:
- Reduces installation complexity
- Provides consistent experience across platforms
- Handles dependency management automatically
- Offers clear error messages and recovery options

### 2. Virtual Environment Strategy
**Decision**: Use virtual environments for isolation
**Rationale**:
- Prevents dependency conflicts
- Enables clean uninstallation
- Supports multiple Python versions
- Facilitates development and testing

### 3. Cross-Platform Compatibility
**Decision**: Support Windows, macOS, and Linux
**Rationale**:
- Broadens user base
- Supports different research environments
- Enables collaboration across platforms
- Reduces platform-specific issues

## Installation Script Implementation

### 1. Core Installation Script

#### Script Structure
```python
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
```

#### OS-Specific Installation
```python
def install_dependencies_windows():
    """Install dependencies on Windows."""
    print("\n📦 Installing dependencies on Windows...")
    
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
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        return False

def install_dependencies_macos():
    """Install dependencies on macOS."""
    print("\n📦 Installing dependencies on macOS...")
    
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
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        return False
```

### 2. Prerequisites Checking

#### System Requirements Check
```python
def check_prerequisites():
    """Check system prerequisites."""
    print("\n🔍 Checking prerequisites...")
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Check pip availability
    if not check_pip():
        print("\n📋 To install pip:")
        print_platform_specific_pip_instructions()
        return False
    
    # Check git availability
    if not check_git():
        print("\n📋 To install git:")
        print_platform_specific_git_instructions()
        return False
    
    return True

def check_pip():
    """Check if pip is available."""
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      capture_output=True, check=True)
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
```

### 3. Optional Dependencies

#### Optional Package Installation
```python
def install_optional_dependencies():
    """Install optional dependencies."""
    print("\n🔧 Installing optional dependencies...")
    
    optional_packages = [
        "datatables-module",
        "selenium",
        "webdriver-manager",
        "beautifulsoup4",
        "lxml"
    ]
    
    venv_pip = get_venv_pip_path()
    
    if not venv_pip:
        print("❌ Virtual environment not found. Please run the main installation first.")
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
```

### 4. Installation Verification

#### Test Installation
```python
def run_test():
    """Run a simple test to verify installation."""
    print("\n🧪 Running installation test...")
    
    venv_python = get_venv_python_path()
    
    if not venv_python:
        print("❌ Virtual environment not found.")
        return False
    
    try:
        # Test pygetpapers import
        result = subprocess.run([venv_python, "-c", "import pygetpapers; print('✅ pygetpapers imported successfully')"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout.strip())
        else:
            print("❌ Failed to import pygetpapers")
            print(result.stderr)
            return False
        
        # Test pygetpapers command
        result = subprocess.run([venv_python, "-m", "pygetpapers", "--version"], 
                              capture_output=True, text=True)
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
```

## Cross-Platform Considerations

### 1. Windows Support

#### Windows-Specific Features
- PowerShell and Command Prompt compatibility
- Path handling with backslashes
- Virtual environment activation scripts
- Windows-specific dependency management

#### Windows Installation Process
```bash
# Windows installation steps
1. Download and install Python 3.8+
2. Ensure pip is available
3. Install git if not present
4. Run install.py script
5. Activate virtual environment: venv\Scripts\activate
6. Test installation: pygetpapers --help
```

### 2. macOS Support

#### macOS-Specific Features
- Homebrew integration
- Unix-like path handling
- macOS-specific dependency resolution
- Terminal compatibility

#### macOS Installation Process
```bash
# macOS installation steps
1. Install Python via Homebrew or official installer
2. Ensure pip is available
3. Install git if not present
4. Run install.py script
5. Activate virtual environment: source venv/bin/activate
6. Test installation: pygetpapers --help
```

### 3. Linux Support

#### Linux-Specific Features
- Package manager integration
- System-wide vs user installation
- Linux-specific dependency management
- Shell script compatibility

#### Linux Installation Process
```bash
# Linux installation steps
1. Install Python 3.8+ via package manager
2. Install pip if not present
3. Install git if not present
4. Run install.py script
5. Activate virtual environment: source venv/bin/activate
6. Test installation: pygetpapers --help
```

## Deployment Strategies

### 1. Development Environment

#### Local Development Setup
```bash
# Clone repository
git clone https://github.com/petermr/pygetpapers.git
cd pygetpapers

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows: venv\Scripts\activate
# Unix/macOS: source venv/bin/activate

# Install in development mode
pip install -e .

# Install development dependencies
pip install -r requirements-dev.txt
```

#### Development Tools
- Pre-commit hooks for code quality
- Automated testing with pytest
- Code coverage reporting
- Linting and formatting tools

### 2. Production Environment

#### Production Installation
```bash
# Install from PyPI (when available)
pip install pygetpapers

# Or install from source
git clone https://github.com/petermr/pygetpapers.git
cd pygetpapers
pip install -r requirements.txt
pip install -e .
```

#### Production Considerations
- System-wide installation options
- Service account setup
- Logging configuration
- Performance optimization

### 3. Container Deployment

#### Docker Support
```dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy pygetpapers source
COPY . .

# Install pygetpapers
RUN pip install -e .

# Set default command
CMD ["pygetpapers", "--help"]
```

#### Docker Compose
```yaml
version: '3.8'
services:
  pygetpapers:
    build: .
    volumes:
      - ./data:/app/data
      - ./config:/app/config
    environment:
      - PYTHONPATH=/app
    command: ["pygetpapers", "--query", "test", "--repository", "biorxiv"]
```

## Error Handling and Recovery

### 1. Installation Errors

#### Common Issues
- Python version incompatibility
- Missing system dependencies
- Network connectivity issues
- Permission problems
- Virtual environment conflicts

#### Recovery Strategies
```python
def handle_installation_error(error_type, error_message):
    """Handle installation errors with recovery suggestions."""
    
    if error_type == "python_version":
        print("❌ Python version error:")
        print("   Please install Python 3.8 or higher")
        print("   Download from: https://python.org/downloads/")
        
    elif error_type == "pip_missing":
        print("❌ pip not found:")
        print("   Please install pip:")
        print_platform_specific_pip_instructions()
        
    elif error_type == "git_missing":
        print("❌ git not found:")
        print("   Please install git:")
        print_platform_specific_git_instructions()
        
    elif error_type == "network_error":
        print("❌ Network error:")
        print("   Please check your internet connection")
        print("   Try using a different network or VPN")
        
    elif error_type == "permission_error":
        print("❌ Permission error:")
        print("   Try running with administrator privileges")
        print("   Or install in a user directory")
```

### 2. Runtime Errors

#### Common Runtime Issues
- Missing optional dependencies
- Repository connectivity problems
- File system permission issues
- Memory constraints

#### Error Recovery
```python
def handle_runtime_error(error_type, error_message):
    """Handle runtime errors with recovery suggestions."""
    
    if error_type == "missing_dependency":
        print("❌ Missing dependency:")
        print("   Run: pip install <package_name>")
        print("   Or re-run installation with optional dependencies")
        
    elif error_type == "repository_unavailable":
        print("❌ Repository unavailable:")
        print("   Check your internet connection")
        print("   Try a different repository")
        print("   Check if the repository is down")
        
    elif error_type == "file_permission":
        print("❌ File permission error:")
        print("   Check file permissions")
        print("   Try running with appropriate privileges")
```

## Performance Optimization

### 1. Installation Performance

#### Optimization Strategies
- Parallel dependency installation
- Caching of downloaded packages
- Minimal dependency sets
- Efficient virtual environment creation

#### Performance Monitoring
```python
def monitor_installation_performance():
    """Monitor installation performance metrics."""
    start_time = time.time()
    
    # Track installation steps
    steps = {
        'python_check': 0,
        'dependencies': 0,
        'pygetpapers': 0,
        'optional': 0,
        'test': 0
    }
    
    # Record timing for each step
    for step in steps:
        step_start = time.time()
        # Execute step
        steps[step] = time.time() - step_start
    
    total_time = time.time() - start_time
    
    print(f"\n📊 Installation Performance:")
    print(f"   Total time: {total_time:.2f} seconds")
    for step, duration in steps.items():
        print(f"   {step}: {duration:.2f} seconds")
```

### 2. Runtime Performance

#### Optimization Features
- Lazy loading of repositories
- Caching of API responses
- Parallel download processing
- Memory-efficient file handling

## Security Considerations

### 1. Installation Security

#### Security Measures
- Verify package integrity
- Use secure package sources
- Validate downloaded files
- Secure virtual environment setup

#### Security Best Practices
```python
def verify_package_integrity(package_path):
    """Verify package integrity before installation."""
    # Check file checksums
    # Validate package signatures
    # Verify package source
    pass

def secure_installation():
    """Perform secure installation."""
    # Use HTTPS for downloads
    # Verify package integrity
    # Set secure permissions
    # Validate dependencies
    pass
```

### 2. Runtime Security

#### Security Features
- Input validation and sanitization
- Secure file handling
- API key protection
- Error message security

## Future Enhancements

### 1. Automated Installation

#### CI/CD Integration
- Automated testing on multiple platforms
- Continuous deployment pipelines
- Automated dependency updates
- Release automation

### 2. Advanced Deployment

#### Cloud Deployment
- AWS Lambda support
- Google Cloud Functions
- Azure Functions
- Container orchestration

### 3. User Experience

#### Installation Improvements
- Graphical installation wizard
- Progress indicators
- Interactive configuration
- Automated troubleshooting

## Conclusion

The comprehensive installation and deployment strategy ensures that pygetpapers v2.0 can be easily installed and deployed across different platforms and environments. The installation script provides a user-friendly experience while handling the complexity of dependency management and environment setup.

The cross-platform compatibility ensures that researchers can use pygetpapers regardless of their operating system, while the deployment strategies support both development and production use cases.

The error handling and recovery mechanisms provide clear guidance when issues arise, and the performance optimizations ensure efficient operation across different environments.

This installation strategy supports the goal of making pygetpapers accessible to a wide range of users while maintaining the reliability and functionality that researchers depend on. 