"""Setup for OAI Harvester."""

from __future__ import with_statement

import sys

from setuptools import setup, find_packages

import oaiharvest

# Check Python version
py_version = getattr(sys, 'version_info', (0, 0, 0))

# Basic information
_name = "oaiharvest"
_version = oaiharvest.__version__
_description = ("A harvester to collect records from an OAI-PMH enabled "
                "provider.")
_author = 'John Harrison'
_author_email = 'john.harrison@liv.ac.uk'

# Find longer description from README
with open('README.rst', 'r') as fh:
    _long_description = fh.read()

# Requirements
with open('requirements.txt', 'r') as fh:
    _install_requires = fh.readlines()

if py_version < (2, 7):
    _install_requires.append('argparse')


# Setup
setup(
    name=_name,
    version=_version,
    description=_description,
    long_description=_long_description,
    packages=[_name],
    author=_author,
    author_email=_author_email,
    maintainer=_author,
    maintainer_email=_author_email,
    include_package_data=True,
    exclude_package_data={'': ['README.*', 'LICENSE.*',
                               'requirements.txt', '.gitignore']},
    requires=['lxml(>=2.1)', 'pyoai(>=2.4)'],
    install_requires=_install_requires,
    setup_requires=['setuptools-git'],
    entry_points={
        'console_scripts': [
            "oai-harvest = oaiharvest.harvest:main",
            "oai-reg = oaiharvest.registry:main"
        ]
    },
    url='http://github.com/bloomonkey/oai-harvest',
    license="BSD",
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7", 
        "Topic :: Text Processing :: Markup",
    ]
)
