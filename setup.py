#!/usr/bin/env python

from setuptools import setup, find_packages

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
      version='0.0.3',
      author='Remi Sebastian Kits',
      author_email='kaitumisuuringute.keskus@gmail.com',
      packages=find_packages(exclude=['tests']),
      include_package_data=True,
      install_requires=INSTALL_REQUIRES)

