"""
Setup script for corpus_module.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="corpus-module",
    version="0.1.0",
    author="AmiLib Team",
    author_email="contact@amilib.org",
    description="Standalone corpus management module for document analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/amilib/corpus-module",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires=">=3.8",
    install_requires=[
        "lxml>=4.6.0",
        "datatables-module>=0.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "search": [
            "beautifulsoup4>=4.9.0",
            "requests>=2.25.0",
        ],
    },
    keywords="corpus, text-analysis, document-management, search, linguistics",
    project_urls={
        "Bug Reports": "https://github.com/amilib/corpus-module/issues",
        "Source": "https://github.com/amilib/corpus-module",
        "Documentation": "https://github.com/amilib/corpus-module/blob/main/README.md",
    },
) 