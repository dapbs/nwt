#!/usr/bin/python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os


README = open(os.path.join(os.path.dirname(__file__), "README.md")).read()
REQUIREMENTS = [
    line.strip()
    for line in open(
        os.path.join(os.path.dirname(__file__), "requirements.txt")
    ).readlines()
]

setup(
    name="nwt",
    version="1.0.0",
    description="Unoffical Percolate API",
    long_description=README,
    author="dapbs",
    author_email="dapbs@github.com",
    url="https://github.com/dapbs/nwt",
    keywords=["Percolate", "API"],
    install_requires=REQUIREMENTS,
    packages=find_packages(),
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)

