#!/usr/bin/env python

from pathlib import Path

from setuptools import setup, find_packages

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

versions = dict()

precisions = dict()

libs = ['numpy',
        'scipy',
        'pandas',
        'decorator',
        'watchdog',
        'requests']


def version_libs(libs, precisions, versions):
    return [lib + precisions[lib] + versions[lib]
            if lib in versions.keys() else lib
            for lib in libs]


INSTALL_REQUIRES = version_libs(libs, precisions, versions)

setup(name='weightipy',
      version='0.4.0',
      author='Remi Sebastian Kits',
      author_email='kaitumisuuringute.keskus@gmail.com',
      packages=find_packages(exclude=['tests']),
      include_package_data=True,
      install_requires=INSTALL_REQUIRES,
      long_description=long_description,
      long_description_content_type='text/markdown'
)

