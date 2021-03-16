#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()
requirements = ['requests', 'pandas_read_xml', 'pandas',
                'lxml', 'chromedriver_autoinstaller', 'xmltodict', 'selenium']

setup(
    name='pygetpapers',
    version='0.0.1',
    description='Automated Download of Research Papers from EuropePMC repository',
    long_description=readme,
    author='Ayush Garg',
    author_email='ayush@science.org.in',
    url='https://github.com/petermr/pygetpapers',
    packages=[
        'pygetpapers',
    ],
    package_dir={'pygetpapers':
                 'pygetpapers'},
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
