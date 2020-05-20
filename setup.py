"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""
# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path
import re

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='rocketCrawler',
    version='1.0',
    packages=['rocketCrawler'],
    url='https://github.com/EmCeBeh/rocketCrawler',  # Optional
    install_requires=['numpy', 'datetime', 'requests'],  # Optional
    license='',
    author='Martin Borchert',
    author_email='martin.b@robothek.de',
    description='Python module to download the rocket.Chat history from a particular group on the server. Uploaded files are stored as URLs.',  # Required
    long_description=long_description,  # Optional
    long_description_content_type='text/markdown',  # Optional (see note above)
)