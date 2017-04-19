"""Setup for OAI Harvester."""
from __future__ import with_statement

from setuptools import setup

# Basic information
_name = "oaiharvest"
_description = ("A harvester to collect records from an OAI-PMH enabled "
                "provider.")
_author = 'John Harrison'
_author_email = 'john@bloomonkey.co.uk'

# Find longer description from README
with open('README.rst', 'r') as fh:
    _long_description = fh.read()

# Requirements
with open('requirements.txt', 'r') as fh:
    _install_requires = fh.readlines()


# Setup
setup(
    name=_name,
    use_scm_version=True,
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
    setup_requires=['setuptools-git', 'setuptools_scm', 'wheel'],
    extras_require={
        ':python_version=="2.6"': ['argparse'],
        ':python_version=="2.7"': ['argparse'],
    },
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
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Text Processing :: Markup",
    ]
)
