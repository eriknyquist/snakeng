import unittest
import os
from setuptools import setup
from distutils.core import Command

from snakeng import __version__

HERE = os.path.abspath(os.path.dirname(__file__))
README = os.path.join(HERE, "README.rst")
REQS = os.path.join(HERE, "requirements.txt")

with open(README, 'r') as f:
    long_description = f.read()

with open(REQS, 'r') as fh:
    requirements = [r.strip() for r in fh.readlines()]

setup(
    name='snakeng',
    version=__version__,
    description=('Easy-to-use snake game engine. Quickly implement snake for anything!'),
    long_description=long_description,
    url='http://github.com/eriknyquist/snakeng',
    author='Erik Nyquist',
    author_email='eknyquist@gmail.com',
    license='Apache 2.0',
    packages=['snakeng'],
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.7",
    install_requires=requirements,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    project_urls={
        "Documentation": "https://eriknyquist.github.io/snakeng",
        "Issues": "https://github.com/eriknyquist/snakeng/issues",
        "Contributions": "https://eriknyquist.github.io/snakeng/#contributions"
    }
)
