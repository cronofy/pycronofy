#!/usr/bin/env python
from distutils.core import setup
import os
import re
import codecs

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name='PyCronofy',
    version=find_version("pycronofy", "__init__.py"),
    description='Python library for Cronofy',
    author='VenueBook',
    author_email='dev@venuebook.com',
    url='https://github.com/cronofy/pycronofy',
    packages=['pycronofy'],
    install_requires=["future"]
)
