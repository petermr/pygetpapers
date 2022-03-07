#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import configparser
import os
with open(os.path.join(os.path.dirname(__file__), "pygetpapers", "config.ini")) as f:
    config_file = f.read()
config = configparser.RawConfigParser(allow_no_value=True)
config.read_string(config_file)
version = config.get("pygetpapers", "version")

with open('README.md', encoding='utf-8') as readme_file:
    readme = readme_file.read()
requirements = ['requests', 'pandas',
                'lxml', 'xmltodict', 'configargparse', 'habanero', 'arxiv', 'dict2xml', 'tqdm', 'coloredlogs']

setup(
    name='pygetpapers',
    version=f"{version}",
    description='Automated Download of Research Papers from various scientific repositories',
    long_description_content_type='text/markdown',
    long_description=readme,
    author='Ayush Garg',
    author_email='ayush@science.org.in',
    url='https://github.com/petermr/pygetpapers',
    packages=[
        'pygetpapers','pygetpapers.repository'
    ],
    package_dir={'pygetpapers':
                 'pygetpapers',
                 },
    include_package_data=True,
    install_requires=requirements,
    license='Apache License',
    zip_safe=False,
    keywords='research automation',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',

    ],
    entry_points={
        'console_scripts': [
            'pygetpapers=pygetpapers.pygetpapers:main',
        ],
    },
)
