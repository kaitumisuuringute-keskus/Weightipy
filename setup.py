"""
weightipy setup.py - Backward compatibility shim

Modern configuration is now in pyproject.toml (PEP 517/518/621).
This file exists only for backward compatibility with older tools.

For package metadata and dependencies, see pyproject.toml
"""

from setuptools import setup

# All configuration is now in pyproject.toml
# This minimal setup() call allows legacy tools to work
setup()
