"""Setup for the pydoa package."""

import setuptools
from setuptools import Extension

with open('README.md') as f:
    README = f.read()

setuptools.setup(
    author="Pankaj Chejara",
    author_email="pankajchejara23@gmail.com",
    name='pydoa',
    license="MIT",
    description='Python package for processing and visualizing direction of arrival data.',
    version='v1.3',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/pankajchejara23/pydoa',
    packages=setuptools.find_packages(),
    python_requires=">=3.5",
    install_requires=['requests','pandas','networkx','scipy','dash','numpy','matplotlib','dash-bootstrap-components','dash-cytoscape'],
    classifiers=[
        # Trove classifiers
        # (https://pypi.python.org/pypi?%3Aaction=list_classifiers)
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
    ],
)
